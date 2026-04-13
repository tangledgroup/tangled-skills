---
name: pi-agent-0-66-1
description: A skill for understanding and implementing the Pi Agent 0.66.1 stateful agent architecture, covering its event-driven message loop, tool execution patterns, queue management for steering/follow-ups, and integration with Pi AI for LLM interactions. Use when designing agentic systems, implementing multi-turn conversation loops, building tool-execution frameworks, or understanding how to create responsive UIs with streaming agent events.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - agentic-systems
  - message-loops
  - tool-execution
  - event-streams
  - conversation-state
  - ai-agents
  - streaming-ui
category: architecture
required_environment_variables: []
---

# Pi Agent 0.66.1 Architecture and Implementation

Pi Agent is a stateful agent framework built on top of Pi AI that provides multi-turn conversation management, tool execution, event streaming, and queue-based message handling. It implements a sophisticated agent loop with support for steering (user interruptions) and follow-up messages, enabling responsive interactive applications.

**Key architectural innovations:**
- **Stateful Agent Loop**: Maintains conversation context across multiple turns
- **Event-Driven Architecture**: Rich event stream for real-time UI updates
- **Tool Execution Pipeline**: Preflight validation, parallel/sequential execution, post-processing
- **Queue Management**: Steering and follow-up message queues with configurable modes
- **Message Transformation**: Separation of AgentMessage (app-level) from LLM Message (provider-level)

## When to Use

- Designing stateful conversational AI applications
- Implementing multi-turn agent loops with tool calling
- Building responsive UIs that stream agent events
- Creating interruptible agents with user steering
- Understanding event-driven architecture for AI systems
- Implementing tool execution with validation hooks
- Managing conversation state across multiple LLM calls

## Quick Start

### Basic Agent Setup

```typescript
import { Agent } from "@mariozechner/pi-agent-core";
import { getModel } from "@mariozechner/pi-ai";

const agent = new Agent({
  initialState: {
    systemPrompt: "You are a helpful coding assistant.",
    model: getModel("anthropic", "claude-3-5-sonnet"),
    tools: [readFileTool, writeFileTool, bashTool]
  }
});

// Subscribe to events for UI updates
agent.subscribe((event) => {
  if (event.type === "message_update" && 
      event.assistantMessageEvent?.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

// Start conversation
await agent.prompt("Help me refactor this code");
```

### Event-Driven UI Pattern

```typescript
const agent = new Agent({ initialState });

// Stream all events to UI
const unsubscribe = agent.subscribe(async (event) => {
  switch (event.type) {
    case "turn_start":
      ui.showLoading();
      break;
    case "message_update":
      if (event.assistantMessageEvent?.type === "text_delta") {
        ui.appendText(event.assistantMessageEvent.delta);
      }
      break;
    case "tool_execution_start":
      ui.showToolExecution(event.toolCall.name);
      break;
    case "tool_execution_end":
      ui.showToolResult(event.result);
      break;
    case "turn_end":
      ui.hideLoading();
      break;
  }
});

await agent.prompt("Analyze this file");
```

See [Usage Patterns](references/02-usage-patterns.md) for comprehensive examples.

## Core Architecture Overview

### Design Philosophy

Pi Agent follows several key architectural principles:

1. **Separation of Concerns**: AgentMessage (app-level) vs Message (LLM-level)
2. **Event-Driven Updates**: All state changes emit events for UI synchronization
3. **Composable Hooks**: beforeToolCall/afterToolCall for customization
4. **Queue-Based Steering**: Configurable modes for user interruptions
5. **State Ownership**: Agent owns transcript, exposes immutable snapshots

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  agent.prompt("Hello") → EventStream<AgentEvent>        │
│  agent.subscribe(event => handleEvent(event))           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Agent Class                            │
│  - State Management (messages, tools, model)            │
│  - Event Emission (listeners)                           │
│  - Queue Management (steering, follow-up)               │
│  - Tool Execution (before/after hooks)                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 Agent Loop Layer                         │
│  runAgentLoop() / runAgentLoopContinue()                │
│  - Message transformation (AgentMessage → Message)      │
│  - LLM streaming via streamSimple()                     │
│  - Tool call detection and execution                    │
│  - Turn management (start/end events)                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Pi AI Layer                             │
│  streamSimple(model, context, options)                  │
│  → EventStream<AssistantMessageEvent>                   │
└─────────────────────────────────────────────────────────┘
```

See [Architecture Deep Dive](references/01-architecture-overview.md) for detailed component analysis.

## Key Implementation Patterns

### 1. Message Transformation Pattern

**Problem**: Applications need custom message types (UI-only), but LLMs only understand user/assistant/toolResult.

**Solution**: Two-phase transformation:

```typescript
// Phase 1: transformContext (optional) - prune, inject context
transformContext?: (messages: AgentMessage[]) => Promise<AgentMessage[]>;

// Phase 2: convertToLlm (required) - filter to LLM-compatible messages
convertToLlm?: (messages: AgentMessage[]) => Message[];

// Default implementation
function defaultConvertToLlm(messages: AgentMessage[]): Message[] {
  return messages.filter(
    msg => msg.role === "user" || msg.role === "assistant" || msg.role === "toolResult"
  );
}
```

**Benefits:**
- App can have UI-only message types (e.g., `systemStatus`, `uiHint`)
- LLM only sees what it understands
- Transformation happens once per turn (efficient)

### 2. Event Stream Pattern

**Problem**: UI needs real-time updates during streaming without polling.

**Solution**: Async iterable event stream with rich event types:

```typescript
interface AgentEvent {
  type: 
    | "agent_start" | "agent_end"
    | "turn_start" | "turn_end"
    | "message_start" | "message_update" | "message_end"
    | "tool_execution_start" | "tool_execution_update" | "tool_execution_end";
  // ... event-specific fields
}

// Subscribe to events
agent.subscribe(async (event: AgentEvent) => {
  // Handle event
});
```

**Benefits:**
- Single source of truth for UI state
- No polling or state synchronization needed
- Events include partial data for progressive rendering

### 3. Tool Execution Pipeline Pattern

**Problem**: Tools need validation, authorization, and post-processing.

**Solution**: Three-phase pipeline with hooks:

```typescript
const agent = new Agent({
  // Phase 1: Preflight (after arg validation, before execution)
  beforeToolCall: async ({ toolCall, args, context }) => {
    if (toolCall.name === "bash" && !isTrustedUser()) {
      return { block: true, reason: "Bash requires authorization" };
    }
    return undefined; // Allow execution
  },
  
  // Phase 2: Execution (automatic)
  // Tool function called with validated args
  
  // Phase 3: Post-processing (after execution, before events)
  afterToolCall: async ({ toolCall, result, isError, context }) => {
    if (!isError && toolCall.name === "write_file") {
      return { 
        details: { 
          ...result.details, 
          audited: true,
          auditTimestamp: Date.now()
        } 
      };
    }
  }
});
```

**Benefits:**
- Centralized authorization logic
- Audit trail for all tool executions
- Result transformation without modifying tools

### 4. Queue Management Pattern

**Problem**: Users want to interrupt agent or add follow-ups while it's thinking.

**Solution**: Two queues with configurable modes:

```typescript
const agent = new Agent({
  steeringMode: "one-at-a-time",  // or "all"
  followUpMode: "one-at-a-time"   // or "all"
});

// User types while agent is responding
agent.steer("Actually, also check the database");

// Add follow-up for after current turn
agent.followUp("Then summarize the findings");
```

**Queue Modes:**
- `one-at-a-time`: Process one message per turn (default, safer)
- `all`: Process all queued messages in one turn (faster, riskier)

### 5. State Management Pattern

**Problem**: Agent state needs to be mutable but thread-safe during streaming.

**Solution**: Immutable snapshots with controlled mutation:

```typescript
// Read state (returns copy)
const currentState = agent.state;
console.log(currentState.messages.length);

// Mutate state (controlled via setters)
agent.state.systemPrompt = "New prompt";
agent.state.tools = [newTool];  // Copies array before storing

// State during streaming
if (agent.state.isStreaming) {
  const partialMessage = agent.state.streamingMessage;
  console.log("Currently generating:", partialMessage?.content);
}
```

**Benefits:**
- No race conditions during streaming
- State snapshots are safe to store
- Clear separation of read vs write operations

## Agent Loop Implementation

### Main Loop Structure

```typescript
async function runLoop(context, newMessages, config, signal, emit) {
  let firstTurn = true;
  let pendingMessages = await getSteeringMessages();
  
  // Outer loop: handles follow-up messages
  while (true) {
    let hasMoreToolCalls = true;
    
    // Inner loop: processes tool calls and steering
    while (hasMoreToolCalls || pendingMessages.length > 0) {
      if (!firstTurn) await emit({ type: "turn_start" });
      
      // 1. Inject pending messages (steering/follow-ups)
      for (const msg of pendingMessages) {
        await emit({ type: "message_start", message: msg });
        await emit({ type: "message_end", message: msg });
        context.messages.push(msg);
      }
      pendingMessages = [];
      
      // 2. Stream assistant response
      const assistantMessage = await streamAssistantResponse(context, config);
      newMessages.push(assistantMessage);
      
      // 3. Check for errors
      if (assistantMessage.stopReason === "error") {
        await emit({ type: "turn_end", message: assistantMessage });
        await emit({ type: "agent_end", messages: newMessages });
        return;
      }
      
      // 4. Execute tool calls
      const toolCalls = getToolCalls(assistantMessage);
      hasMoreToolCalls = toolCalls.length > 0;
      
      if (hasMoreToolCalls) {
        const results = await executeToolCalls(toolCalls, context);
        for (const result of results) {
          context.messages.push(result);
        }
      }
      
      await emit({ type: "turn_end", message: assistantMessage });
      pendingMessages = await getSteeringMessages();
    }
    
    // Check for follow-up messages
    const followUps = await getFollowUpMessages();
    if (followUps.length > 0) {
      pendingMessages = followUps;
      continue;  // Continue outer loop
    }
    
    break;  // No more messages, exit
  }
  
  await emit({ type: "agent_end", messages: newMessages });
}
```

See [Agent Loop Deep Dive](references/03-agent-loop.md) for complete implementation.

## Tool Execution Strategies

### Parallel Execution (Default)

```typescript
const agent = new Agent({
  toolExecution: "parallel"  // Default
});

// Flow:
// 1. Preflight all tool calls sequentially (beforeToolCall)
// 2. Execute allowed tools concurrently
// 3. Emit results in original assistant message order
```

**Benefits:** Faster execution for independent tools

### Sequential Execution

```typescript
const agent = new Agent({
  toolExecution: "sequential"
});

// Flow:
// 1. Preflight and execute first tool
// 2. Emit result
// 3. Preflight and execute second tool
// 4. Repeat...
```

**Benefits:** Better for dependent tool calls, matches historical behavior

## Context Transformation

### Message Pruning

```typescript
const agent = new Agent({
  transformContext: async (messages) => {
    // Keep only last 10 messages to save tokens
    if (messages.length > 10) {
      return [messages[0], ...messages.slice(-10)];
    }
    return messages;
  }
});
```

### Context Injection

```typescript
const agent = new Agent({
  transformContext: async (messages) => {
    // Inject user context before each turn
    const userContext = await fetchUserPreferences();
    return [
      { role: "system", content: `User prefs: ${userContext}` },
      ...messages
    ];
  }
});
```

## Reference Files

- [`references/01-architecture-overview.md`](references/01-architecture-overview.md) - High-level architecture, design philosophy, component interactions
- [`references/02-usage-patterns.md`](references/02-usage-patterns.md) - Common usage patterns, event handling, state management
- [`references/03-agent-loop.md`](references/03-agent-loop.md) - Agent loop implementation details, turn management, tool execution flow
- [`references/04-tool-execution.md`](references/04-tool-execution.md) - Tool execution pipeline, hooks, parallel vs sequential strategies
- [`references/05-event-system.md`](references/05-event-system.md) - Event types, streaming patterns, UI integration
- [`references/06-queue-management.md`](references/06-queue-management.md) - Steering and follow-up queues, mode configurations

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/pi-agent-0-66-1/`). All paths are relative to this directory.

## Key Design Decisions

### Why Separate AgentMessage from Message?

1. **Extensibility**: Apps can add custom message types without LLM confusion
2. **Abstraction**: UI logic separated from provider constraints
3. **Transformation Control**: Explicit conversion point for debugging

### Why Event-Driven Over Callbacks?

1. **Composability**: Multiple subscribers can listen independently
2. **Async Support**: Subscribers can be async and are awaited in order
3. **Debugging**: Event log provides complete audit trail

### Why Two Queues (Steering vs Follow-up)?

1. **Semantic Clarity**: Steering = interrupt current thought; Follow-up = add after completion
2. **Timing Control**: Different injection points in the loop
3. **User Intent**: Distinguish "wait, change direction" from "also do this next"

### Why Parallel Tool Execution Default?

1. **Performance**: Independent tools execute concurrently
2. **User Expectation**: Faster responses feel more responsive
3. **Safety**: Preflight still sequential for authorization

## Troubleshooting

### Common Issues

**Agent stuck in loop:**
```typescript
// Check for infinite tool call cycles
agent.subscribe((event) => {
  if (event.type === "turn_end") {
    console.log("Turn", turnCount++, "completed");
    if (turnCount > 10) {
      console.warn("Possible infinite loop detected");
    }
  }
});
```

**Tool not executing:**
```typescript
// Check beforeToolCall hook
beforeToolCall: async ({ toolCall, args }) => {
  console.log("Tool preflight:", toolCall.name, args);
  // Ensure you return undefined to allow, not null or void
  return undefined;  
}
```

**Events not firing:**
```typescript
// Verify subscription before prompting
const unsubscribe = agent.subscribe(handleEvent);
await agent.prompt("Hello");
// Don't call unsubscribe() until done
```

## Additional Resources

- **GitHub Repository:** https://github.com/badlogic/pi-mono/tree/v0.66.1/packages/agent
- **Pi AI Package:** https://github.com/badlogic/pi-mono/tree/v0.66.1/packages/ai
- **TypeBox Documentation:** https://github.com/sinclairzx81/typebox
- **Changelog:** See `CHANGELOG.md` in package for version history

## Implementation Insights

The Pi Agent library demonstrates advanced patterns for building production-ready agentic systems:

1. **State Machine Pattern**: Clear turn states with start/end events
2. **Strategy Pattern**: Configurable tool execution modes
3. **Observer Pattern**: Event subscribers for UI updates
4. **Pipeline Pattern**: Tool execution with pre/post hooks
5. **Queue Pattern**: Message buffering with configurable processing

These patterns make the codebase highly testable, extensible, and suitable for production use with proper error handling and state management.
