# Agent Runtime - Deep Dive

This reference document explains how pi-agent-core implements the stateful agent message loop with tool execution.

## The Agent Loop

At its core, an agent is a loop that:
1. Sends messages to an LLM
2. Receives a response
3. Executes any requested tools
4. Adds results to the conversation
5. Repeats until no more tools are needed

Pi's implementation adds sophistication: parallel tool execution, steering/follow-up queues, event streaming, and extensibility hooks.

## Message Flow

The agent works with two message types:

**AgentMessages**: The full message type including custom app-specific messages (notifications, UI-only messages, etc.)

**LLM Messages**: A subset that LLMs understand (user, assistant, toolResult)

Before each LLM call, the agent converts AgentMessages to LLM messages by filtering out custom types and transforming as needed. This separation allows the UI to have rich message types while keeping LLM interactions simple.

## The Turn Structure

A "turn" is one complete cycle of:
1. Send context to LLM
2. Stream assistant response
3. Execute any tool calls from the response
4. Add tool results to context

The agent can run multiple turns in sequence (when tools are called) before completing a user prompt.

**Event sequence for a simple prompt** (no tools):
- agent_start
- turn_start
- message_start (user message)
- message_end (user message)
- message_start (assistant response begins)
- message_update (streaming chunks)
- message_end (assistant response complete)
- turn_end (no tool results)
- agent_end

**Event sequence with tools**:
- agent_start
- turn_start
- message_start/end (user message)
- message_start/update/end (assistant with tool calls)
- tool_execution_start (for each tool)
- tool_execution_end (for each tool)
- message_start/end (tool result messages)
- turn_end (with tool results)
- turn_start (next turn, responding to tool results)
- message_start/update/end (final assistant response)
- turn_end
- agent_end

## Tool Execution Modes

Pi supports two tool execution modes:

### Parallel Mode (Default)

Tools are executed concurrently for maximum speed:

**Phase 1: Sequential Preflight**
- Each tool call is validated against its schema
- The `beforeToolCall` hook runs, which can block execution
- Decisions are made sequentially to maintain deterministic ordering

**Phase 2: Parallel Execution**
- All allowed tools execute concurrently via Promise.all
- Independent tools run simultaneously
- Errors are caught per-tool, not failing the entire batch

**Phase 3: Ordered Emission**
- Results are emitted in the original order from the assistant message
- This preserves the LLM's intended sequence
- Tool result messages are added in order

**Why this design?**
- Preflight is sequential to allow hooks to see previous decisions
- Execution is parallel for performance
- Emission is ordered to maintain conversation coherence

### Sequential Mode

Tools execute one at a time, in order:
- Each tool completes before the next starts
- Results are immediately available to subsequent tools
- Slower but simpler debugging
- Useful when tools depend on each other's results

## Steering and Follow-up Queues

Pi supports two types of interrupting/queuing work:

### Steering (Interrupt)

Steering messages have highest priority and interrupt current work:
- User can send a steering message while tools are running
- Current tools complete, but no new turns run until steering is processed
- Useful for "stop what you're doing and do this instead"
- Can be in "one-at-a-time" mode (process one steering message) or "all" mode (process all queued)

### Follow-up (Queue)

Follow-up messages queue for after current work completes:
- Added to a queue, processed when agent would otherwise stop
- Only run if no tools are pending and no steering messages exist
- Useful for "after you're done, also do this"
- Same "one-at-a-time" or "all" modes

**Priority order**:
1. Complete current tool executions
2. Process steering messages (if any)
3. Process follow-up messages (if any and no tools running)
4. End agent loop

This design allows users to interrupt long-running operations or queue additional work without losing context.

## Event Streaming

Every state change emits an event:

**Why events?**
- **Decoupling**: UI doesn't need to know agent internals, just reacts to events
- **Streaming**: Text can be displayed as it arrives, not after full response
- **Extensions**: Third-party code can hook into any point in the workflow
- **Testing**: Events can be recorded and replayed for deterministic tests

**Event categories**:
- Agent lifecycle: agent_start, agent_end
- Turn lifecycle: turn_start, turn_end  
- Message events: message_start, message_update, message_end
- Tool events: tool_execution_start, tool_execution_update, tool_execution_end

**Message updates are special**: For assistant messages, the update event includes the raw LLM event (text_delta, toolcall_delta, etc.), allowing UIs to show exactly what the model is generating in real-time.

## Custom Message Types

Pi supports extending message types via TypeScript declaration merging:

```typescript
declare module "@mariozechner/pi-agent-core" {
    interface CustomAgentMessages {
        notification: { role: "notification"; text: string; timestamp: number };
    }
}
```

Now `{ role: "notification", ... }` is a valid AgentMessage.

**How it works**:
- Custom messages are part of the agent's internal state
- When converting to LLM messages, they're filtered out (LLMs don't understand them)
- They can trigger UI updates via event listeners
- Useful for system notifications, progress indicators, or app-specific message types

**Use cases**:
- Show "Compacting session..." notifications without cluttering LLM context
- Track internal state changes that shouldn't be sent to the LLM
- Add app-specific message types for specialized workflows

## Tool Validation and Errors

Tools are defined with TypeBox schemas for parameter validation:

**Validation flow**:
1. LLM returns tool call with JSON arguments
2. Arguments are parsed (progressively during streaming)
3. At toolcall_end, full arguments are validated against schema
4. If invalid, error is returned to LLM as a tool result with isError=true
5. LLM can retry with corrected arguments

**Error handling**:
- Thrown errors become tool results with isError=true
- Error messages are sent to the LLM, allowing it to recover
- The agent doesn't crash on tool errors; they become part of the conversation

**Before/After hooks**:
- `beforeToolCall`: Runs after validation, can block execution
- `afterToolCall`: Runs after execution, can modify results before emitting events

These hooks enable:
- Security checks (block dangerous commands)
- Rate limiting (throttle expensive operations)
- Result post-processing (add metadata, transform output)
- Auditing (log all tool calls)

## State Management

The agent maintains state in an AgentState object:

**Immutable properties** (set at creation):
- Tools available to the agent
- Initial messages

**Mutable properties** (can change during runtime):
- System prompt (can be updated mid-conversation)
- Model (can switch models between turns)
- Thinking level (can adjust reasoning effort)
- Messages (grows as conversation progresses)

**Computed properties** (derived from state):
- isStreaming: true while agent is actively generating
- streamingMessage: the current partial assistant message
- pendingToolCalls: IDs of tools currently executing
- errorMessage: if the agent encountered an error

State is accessible via `agent.state` and can be inspected by event listeners and extensions.

## Session Integration

The agent doesn't handle persistence itself - that's the session layer's job. However, it integrates with sessions through:

**Session ID**: Passed to LLM calls for prompt cache retention (Anthropic, OpenAI)

**Message timestamps**: Each message includes a timestamp for ordering and compaction

**Context transformation**: Sessions can prune old messages or inject context before convertToLlm

The agent is stateless regarding persistence - it just processes messages. The session layer handles saving/loading.

## Abort and Recovery

Agents can be aborted mid-operation:

**During LLM call**:
- Abort signal is passed to the stream
- Provider cancels the request
- Error event emitted with reason "aborted"
- Partial content is preserved in the error message

**During tool execution**:
- Abort signal is passed to each tool
- Tools can check signal.aborted and cleanup
- In-progress tools complete or abort based on their implementation
- Results (or errors) are added to context

**Continuing after abort**:
- Aborted messages can be added to context
- User can send "continue" prompt
- Agent resumes from where it left off
- Partial work is preserved

This design allows graceful interruption and resumption without losing progress.

## Parallel vs Sequential Trade-offs

**Parallel execution benefits**:
- Faster overall completion when tools are independent
- Better utilization of async I/O
- Natural fit for LLMs that emit multiple tool calls at once

**Sequential execution benefits**:
- Simpler debugging (one thing happens at a time)
- Tools can depend on previous results within the same turn
- Easier to reason about ordering

Pi defaults to parallel because:
- Most tools are independent (read files, run commands, etc.)
- LLMs often emit multiple tool calls simultaneously
- Users typically prefer faster responses
- Sequential can be enabled when needed for specific workflows

## Extension Integration Points

Extensions can hook into the agent at multiple points:

**Lifecycle hooks**:
- onBeforeAgentStart: Before any processing begins
- onAgentStart: After agent starts
- onTurnStart/End: Each turn boundary
- onMessageStart/Update/End: Message lifecycle
- onToolExecutionStart/End: Tool execution lifecycle
- onAgentEnd: Final cleanup

**Tool hooks**:
- beforeToolCall: Can block tool execution
- afterToolCall: Can modify results

**Custom tools**:
- Extensions can register additional tools
- Tools are merged with built-in tools
- All tools go through the same validation/execution flow

This extensibility allows adding capabilities without modifying core agent code.
