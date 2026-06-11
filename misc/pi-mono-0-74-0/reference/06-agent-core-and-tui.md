# Agent Core and TUI

## Contents
- Agent Core Overview
- AgentMessage vs LLM Message
- Event Flow
- Agent Options
- Agent State
- Methods (Prompting, State, Control)
- Steering and Follow-up
- Custom Message Types
- Tools (AgentTool)
- Proxy Usage
- Low-Level API (agentLoop)
- TUI Framework Overview
- Built-in Components
- Overlays
- Focusable Interface (IME Support)
- Differential Rendering
- Terminal Interface
- Utilities

## Agent Core Overview

`@earendil-works/pi-agent-core` is a stateful agent with tool execution and event streaming, built on `@earendil-works/pi-ai`.

```bash
npm install @earendil-works/pi-agent-core
```

### Quick Start

```typescript
import { Agent } from "@earendil-works/pi-agent-core";
import { getModel } from "@earendil-works/pi-ai";

const agent = new Agent({
  initialState: {
    systemPrompt: "You are a helpful assistant.",
    model: getModel("anthropic", "claude-sonnet-4-20250514"),
  },
});

agent.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await agent.prompt("Hello!");
```

## AgentMessage vs LLM Message

Agent works with `AgentMessage`, a flexible type that can include:
- Standard LLM messages (`user`, `assistant`, `toolResult`)
- Custom app-specific message types via declaration merging

LLMs only understand `user`, `assistant`, and `toolResult`. The `convertToLlm` function bridges the gap by filtering and transforming messages before each LLM call.

### Message Flow

```
AgentMessage[] → transformContext() → AgentMessage[] → convertToLlm() → Message[] → LLM
(optional)           (required)
```

1. **transformContext**: Prune old messages, inject external context
2. **convertToLlm**: Filter out UI-only messages, convert custom types to LLM format

## Event Flow

### prompt() Event Sequence

```
prompt("Hello")
├─ agent_start
├─ turn_start
├─ message_start { userMessage }
├─ message_end { userMessage }
├─ message_start { assistantMessage }
├─ message_update { partial... }  // Streaming chunks
├─ message_update { partial... }
├─ message_end { assistantMessage }
├─ turn_end { message, toolResults: [] }
└─ agent_end { messages: [...] }
```

### With Tool Calls

```
prompt("Read config.json")
├─ agent_start
├─ turn_start
├─ message_start/end { userMessage }
├─ message_start { assistantMessage with toolCall }
├─ message_update...
├─ message_end { assistantMessage }
├─ tool_execution_start { toolCallId, toolName, args }
├─ tool_execution_update { partialResult }  // If tool streams
├─ tool_execution_end { toolCallId, result }
├─ message_start/end { toolResultMessage }
├─ turn_end { message, toolResults: [toolResult] }
│
├─ turn_start  // Next turn
├─ message_start { assistantMessage }  // LLM responds to tool result
├─ message_update...
├─ message_end
├─ turn_end
└─ agent_end
```

### Event Types

| Event | Description |
|-------|-------------|
| `agent_start` | Agent begins processing |
| `agent_end` | Final event. Awaited subscribers for this still count toward settlement |
| `turn_start` | New turn begins (one LLM call + tool executions) |
| `turn_end` | Turn completes with assistant message and tool results |
| `message_start` | Any message begins (user, assistant, toolResult) |
| `message_update` | **Assistant only.** Includes `assistantMessageEvent` with delta |
| `message_end` | Message completes |
| `tool_execution_start` | Tool begins |
| `tool_execution_update` | Tool streams progress |
| `tool_execution_end` | Tool completes |

`Agent.subscribe()` listeners are awaited in registration order. `agent_end` means no more loop events, but `await agent.waitForIdle()` and `await agent.prompt(...)` only settle after awaited `agent_end` listeners finish.

### continue()

Resumes from existing context without adding a new message. Use for retries after errors. Last message must be `user` or `toolResult` (not `assistant`).

## Agent Options

```typescript
const agent = new Agent({
  initialState: {
    systemPrompt: string,
    model: Model,
    thinkingLevel: "off" | "minimal" | "low" | "medium" | "high" | "xhigh",
    tools: AgentTool[],
    messages: AgentMessage[],
  },
  convertToLlm: (messages) => messages.filter(...),
  transformContext: async (messages, signal) => pruneOldMessages(messages),
  steeringMode: "one-at-a-time",   // or "all"
  followUpMode: "one-at-a-time",   // or "all"
  streamFn: streamProxy,           // Custom stream function for proxy backends
  sessionId: "session-123",        // Provider caching
  getApiKey: async (provider) => refreshToken(),  // Dynamic API key resolution
  toolExecution: "parallel",       // or "sequential"
  beforeToolCall: async ({ toolCall, args, context }) => { ... },
  afterToolCall: async ({ toolCall, result, isError, context }) => { ... },
  thinkingBudgets: { minimal: 128, low: 512, medium: 1024, high: 2048 },
});
```

### Tool Execution Mode

- **`parallel`** (default): Preflight tool calls sequentially, execute allowed tools concurrently, emit `tool_execution_end` as each tool finalizes, then emit toolResult messages in assistant source order
- **`sequential`**: Execute tool calls one by one

Per-tool `executionMode` overrides global. If any tool call targets a tool with `executionMode: "sequential"`, the entire batch executes sequentially.

### beforeToolCall / afterToolCall

- `beforeToolCall`: Runs after `tool_execution_start` and validated argument parsing. Can block execution by returning `{ block: true, reason: "..." }`.
- `afterToolCall`: Runs after tool execution finishes and before `tool_execution_end`. Return `{ terminate: true }` to hint that automatic follow-up LLM call should be skipped (only takes effect when every finalized tool result in batch sets `terminate: true`).

### shouldStopAfterTurn

Low-level loop callers can set `shouldStopAfterTurn` to stop gracefully after current turn completes:
```typescript
const stream = agentLoop(prompts, context, {
  model,
  shouldStopAfterTurn: async ({ message, toolResults, context }) => {
    return shouldCompactBeforeNextTurn(context.messages);
  },
});
```

## Agent State

```typescript
interface AgentState {
  systemPrompt: string;
  model: Model;
  thinkingLevel: ThinkingLevel;
  tools: AgentTool[];
  messages: AgentMessage[];
  readonly isStreaming: boolean;
  readonly streamingMessage?: AgentMessage;
  readonly pendingToolCalls: ReadonlySet;
  readonly errorMessage?: string;
}
```

Access via `agent.state`. Assigning `agent.state.tools = [...]` or `agent.state.messages = [...]` copies the top-level array before storing. Mutating the returned array mutates current agent state.

## Methods

### Prompting

```typescript
await agent.prompt("Hello");
await agent.prompt("What's in this image?", [
  { type: "image", data: base64Data, mimeType: "image/jpeg" },
]);
await agent.prompt({ role: "user", content: "Hello", timestamp: Date.now() });
await agent.continue();  // Resume from current context
```

### State Management

```typescript
agent.state.systemPrompt = "New prompt";
agent.state.model = getModel("openai", "gpt-4o");
agent.state.thinkingLevel = "medium";
agent.state.tools = [myTool];
agent.toolExecution = "sequential";
agent.beforeToolCall = async ({ toolCall }) => undefined;
agent.afterToolCall = async ({ toolCall, result }) => undefined;
agent.state.messages = newMessages;  // copies top-level array
agent.state.messages.push(message);
agent.reset();
```

### Session and Thinking Budgets

```typescript
agent.sessionId = "session-123";
agent.thinkingBudgets = { minimal: 128, low: 512, medium: 1024, high: 2048 };
```

### Control

```typescript
agent.abort();                              // Cancel current operation
await agent.waitForIdle();                  // Wait for completion
const unsubscribe = agent.subscribe(async (event, signal) => { ... });
unsubscribe();
```

## Steering and Follow-up

```typescript
agent.steeringMode = "one-at-a-time";
agent.followUpMode = "one-at-a-time";

// While agent is running tools
agent.steer({ role: "user", content: "Stop! Do this instead.", timestamp: Date.now() });

// After the agent finishes its current work
agent.followUp({ role: "user", content: "Also summarize the result.", timestamp: Date.now() });

agent.clearSteeringQueue();
agent.clearFollowUpQueue();
agent.clearAllQueues();
```

Steering messages are detected after a turn completes: all tool calls from current assistant message have finished, steering messages injected, LLM responds on next turn. Follow-up messages checked only when no more tool calls and no steering messages.

## Custom Message Types

Extend `AgentMessage` via declaration merging:
```typescript
declare module "@earendil-works/pi-agent-core" {
  interface CustomAgentMessages {
    notification: { role: "notification"; text: string; timestamp: number };
  }
}

const msg: AgentMessage = { role: "notification", text: "Info", timestamp: Date.now() };
```

Handle custom types in `convertToLlm`:
```typescript
const agent = new Agent({
  convertToLlm: (messages) => messages.flatMap(m => {
    if (m.role === "notification") return []; // Filter out
    return [m];
  }),
});
```

## Tools (AgentTool)

```typescript
import { Type } from "typebox";

const readFileTool: AgentTool = {
  name: "read_file",
  label: "Read File",
  description: "Read a file's contents",
  parameters: Type.Object({
    path: Type.String({ description: "File path" }),
  }),
  executionMode: "sequential",  // Optional per-tool override
  execute: async (toolCallId, params, signal, onUpdate) => {
    const content = await fs.readFile(params.path, "utf-8");
    onUpdate?.({ content: [{ type: "text", text: "Reading..." }], details: {} });
    return {
      content: [{ type: "text", text: content }],
      details: { path: params.path, size: content.length },
    };
  },
};
```

### Error Handling

**Throw an error** when a tool fails. Do not return error messages as content:
```typescript
execute: async (toolCallId, params, signal, onUpdate) => {
  if (!fs.existsSync(params.path)) {
    throw new Error(`File not found: ${params.path}`);
  }
  return { content: [{ type: "text", text: "..." }] };
}
```

Thrown errors are caught by the agent and reported to LLM as tool errors with `isError: true`. Return `terminate: true` from `execute()` or `afterToolCall` to hint that agent should stop after current tool batch.

## Proxy Usage

For browser apps that proxy through a backend:
```typescript
import { Agent, streamProxy } from "@earendil-works/pi-agent-core";

const agent = new Agent({
  streamFn: (model, context, options) =>
    streamProxy(model, context, { ...options, authToken: "...", proxyUrl: "https://your-server.com" }),
});
```

## Low-Level API

For direct control without the Agent class:
```typescript
import { agentLoop, agentLoopContinue } from "@earendil-works/pi-agent-core";

const context: AgentContext = { systemPrompt: "You are helpful.", messages: [], tools: [] };
const config: AgentLoopConfig = {
  model: getModel("openai", "gpt-4o"),
  convertToLlm: (msgs) => msgs.filter(m => ["user", "assistant", "toolResult"].includes(m.role)),
  toolExecution: "parallel",
  beforeToolCall: async ({ toolCall, args, context }) => undefined,
  afterToolCall: async ({ toolCall, result, isError, context }) => undefined,
};

for await (const event of agentLoop([userMessage], context, config)) {
  console.log(event.type);
}

// Continue from existing context
for await (const event of agentLoopContinue(context, config)) {
  console.log(event.type);
}
```

These low-level streams are observational — they do not wait for async event handling to settle. Use `Agent` class if message processing must act as a barrier before tool preflight.

## TUI Framework Overview

`@earendil-works/pi-tui` is a minimal terminal UI framework with differential rendering and synchronized output for flicker-free interactive CLI applications.

### Features
- **Differential Rendering**: Three-strategy system that only updates what changed
- **Synchronized Output**: Uses CSI 2026 for atomic screen updates (no flicker)
- **Bracketed Paste Mode**: Handles large pastes correctly
- **Component-based**: Simple Component interface with `render()` method
- **Theme Support**: Components accept theme interfaces
- **Inline Images**: Kitty or iTerm2 graphics protocols

### Quick Start

```typescript
import { TUI, Text, Editor, ProcessTerminal, matchesKey } from "@earendil-works/pi-tui";

const terminal = new ProcessTerminal();
const tui = new TUI(terminal);
tui.addChild(new Text("Welcome!"));

const editor = new Editor(tui, theme);
editor.onSubmit = (text) => {
  console.log("Submitted:", text);
  tui.addChild(new Text(`You said: ${text}`));
};
tui.addChild(editor);
tui.setFocus(editor);

tui.addInputListener((data) => {
  if (matchesKey(data, 'ctrl+c')) { tui.stop(); process.exit(0); }
});
tui.start();
```

## Built-in Components

### TUI (Main Container)

```typescript
const tui = new TUI(terminal);
tui.addChild(component);
tui.removeChild(component);
tui.start();
tui.stop();
tui.requestRender();  // Request re-render
tui.onDebug = () => console.log("Debug triggered");
```

### Container / Box

Groups child components. Box applies padding and background color:
```typescript
const box = new Box(1, 1, (text) => chalk.bgGray(text));
box.addChild(new Text("Content"));
box.setBgFn((text) => chalk.bgBlue(text));
```

### Text / TruncatedText

Displays multi-line text with word wrapping. TruncatedText truncates to fit viewport width.

### Input

Single-line text input with horizontal scrolling:
```typescript
const input = new Input();
input.onSubmit = (value) => console.log(value);
input.setValue("initial");
input.getValue();
```

Key bindings: Enter (submit), Ctrl+A/E (line start/end), Ctrl+W/Alt+Backspace (delete word), Ctrl+U/K (delete to start/end), Ctrl+Left/Right (word navigation).

### Editor

Multi-line text editor with autocomplete, file completion, paste handling, vertical scrolling:
```typescript
const editor = new Editor(tui, theme, options?);
editor.onSubmit = (text) => console.log(text);
editor.onChange = (text) => console.log("Changed:", text);
editor.disableSubmit = true;
editor.setAutocompleteProvider(provider);
editor.borderColor = (s) => chalk.blue(s);
```

Features: Multi-line editing with word wrap, slash command autocomplete (`/`), file path autocomplete (Tab), large paste handling (>10 lines creates marker).

### Markdown

Renders markdown with syntax highlighting and theming:
```typescript
const md = new Markdown("# Hello\n\nSome **bold** text", 1,{