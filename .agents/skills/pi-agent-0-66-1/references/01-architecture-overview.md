# Architecture Overview

## System Architecture

Pi Agent 0.66.1 implements a layered architecture that builds on Pi AI to provide stateful conversation management, tool execution, and event streaming.

### Layer 1: Agent Class (Public API)

```typescript
class Agent {
  // State management
  state: AgentState
  
  // Event system
  subscribe(listener): () => void
  
  // Conversation methods
  prompt(message): Promise<void>
  continue(): Promise<void>
  steer(message): void
  followUp(message): void
}
```

**Design Decision:** Minimal public API with comprehensive event system.

### Layer 2: Agent Loop (Core Logic)

```typescript
async function runLoop(context, messages, config, signal, emit) {
  // Main conversation loop with tool execution
  // Handles steering and follow-up queues
  // Emits lifecycle events
}
```

**Design Decision:** Pure function with explicit dependencies for testability.

### Layer 3: Pi AI Integration

Uses `streamSimple()` from Pi AI for LLM interactions.

**Design Decision:** Leverages existing, well-tested LLM abstraction.

## Core Components

### Agent State

```typescript
interface AgentState {
  systemPrompt: string;
  model: Model<any>;
  thinkingLevel: ThinkingLevel;
  tools: AgentTool<any>[];
  messages: AgentMessage[];
  
  // Runtime state (read-only)
  readonly isStreaming: boolean;
  readonly streamingMessage?: AgentMessage;
  readonly pendingToolCalls: ReadonlySet<string>;
  readonly errorMessage?: string;
}
```

**Key Insight:** State separates configuration (mutable) from runtime status (immutable).

### Message Types

**AgentMessage (App-level):**
```typescript
type AgentMessage = 
  | UserMessage
  | AssistantMessage  
  | ToolResultMessage
  | CustomMessage;  // App-specific types
```

**Message (LLM-level):**
```typescript
type Message = 
  | UserMessage
  | AssistantMessage
  | ToolResultMessage;
  // No custom types - LLMs don't understand them
```

### Event System

```typescript
type AgentEvent = 
  | { type: "agent_start" }
  | { type: "agent_end"; messages: AgentMessage[] }
  | { type: "turn_start" }
  | { type: "turn_end"; message: AssistantMessage; toolResults: ToolResultMessage[] }
  | { type: "message_start"; message: AgentMessage }
  | { type: "message_update"; message: AssistantMessage; assistantMessageEvent: AssistantMessageEvent }
  | { type: "message_end"; message: AgentMessage }
  | { type: "tool_execution_start"; toolCall: ToolCall }
  | { type: "tool_execution_update"; partialResult: unknown }
  | { type: "tool_execution_end"; toolCall: ToolCall; result: ToolResult };
```

## Component Interactions

### Prompt Flow

```
1. User calls agent.prompt("Hello")
   ↓
2. Agent creates UserMessage, adds to steering queue
   ↓
3. Agent loop starts (emits agent_start)
   ↓
4. Loop processes steering message (emits message_start/end)
   ↓
5. transformContext() called (AgentMessage[] → AgentMessage[])
   ↓
6. convertToLlm() called (AgentMessage[] → Message[])
   ↓
7. streamSimple() called with LLM context
   ↓
8. LLM streams events (text_delta, toolcall_end, etc.)
   ↓
9. Agent emits message_update events to subscribers
   ↓
10. Tool calls detected → executeToolCalls()
    ↓
11. beforeToolCall hook (can block execution)
    ↓
12. Tool executes
    ↓
13. afterToolCall hook (can modify result)
    ↓
14. ToolResultMessage added to context
    ↓
15. Loop continues if more tool calls or steering messages
    ↓
16. Loop exits when no more work (emits agent_end)
```

### State Updates During Streaming

```typescript
// Before streaming
agent.state.isStreaming = false;
agent.state.streamingMessage = undefined;

// During streaming (message_start)
agent.state.isStreaming = true;
agent.state.streamingMessage = partialAssistantMessage;

// During streaming (message_update)
agent.state.streamingMessage = updatedPartialMessage;

// After streaming (message_end)
agent.state.streamingMessage = undefined;
// isStreaming stays true until agent_end listeners complete
```

## Extensibility Points

### Custom Message Types

```typescript
// 1. Declare custom message type
declare module "@mariozechner/pi-agent-core" {
  interface AgentMessage {
    role: "user" | "assistant" | "toolResult" | "systemStatus";
    content: string;
  }
}

// 2. Implement convertToLlm to filter them out
convertToLlm: (messages) => {
  return messages.filter(m => 
    m.role === "user" || m.role === "assistant" || m.role === "toolResult"
  );
}
```

### Custom Stream Function

```typescript
// For proxy backends or custom LLM providers
const agent = new Agent({
  streamFn: async (model, context, options) => {
    return streamProxy(model, context, {
      ...options,
      proxyUrl: "https://proxy.example.com"
    });
  }
});
```

### Dynamic API Keys

```typescript
// For OAuth tokens that expire
const agent = new Agent({
  getApiKey: async (provider) => {
    if (provider === "github-copilot") {
      return await refreshGitHubToken();
    }
    return undefined; // Use default
  }
});
```

## Performance Considerations

### Memory Efficiency

- **Message Arrays**: Copied only when transformed (not on every read)
- **Event Stream**: Events emitted as they arrive, no buffering
- **State Snapshots**: Getters return copies to prevent external mutation

### CPU Efficiency

- **Tool Preflight**: Sequential validation before parallel execution
- **Context Transform**: Called once per turn, not per message
- **Event Emission**: Async listeners don't block loop

### Network Efficiency

- **Streaming**: Native HTTP streaming via Pi AI
- **Abort Support**: Instant cancellation with AbortSignal
- **Retry Logic**: Automatic retry on transient errors

## Security Considerations

### Tool Authorization

```typescript
beforeToolCall: async ({ toolCall, args, context }) => {
  // Check user permissions
  if (toolCall.name === "delete_file" && !user.canDelete) {
    return { block: true, reason: "Permission denied" };
  }
  
  // Validate arguments
  if (toolCall.name === "bash" && args.command.includes("rm -rf")) {
    return { block: true, reason: "Dangerous command blocked" };
  }
}
```

### Input Validation

- All tool arguments validated against TypeBox schemas before execution
- Malicious inputs rejected in `beforeToolCall` hook
- Sanitization of user-provided content

### Error Isolation

- Tool execution errors don't crash agent loop
- Errors captured in `errorMessage` state field
- Graceful degradation on provider failures
