# Agent Loop Implementation Deep Dive

This document provides a detailed analysis of the agent loop implementation, including turn management, message transformation, and tool execution flow.

## Overview

The agent loop is the core engine that drives conversation state through multiple turns, handling LLM calls, tool executions, steering messages, and follow-ups. It's implemented in two main functions:

- `runAgentLoop()`: Starts a new conversation with prompt messages
- `runAgentLoopContinue()`: Continues from existing context (no new prompt)

Both share the core logic via `runLoop()`.

## Loop Architecture

### Main Loop Structure

```typescript
async function runLoop(
  currentContext: AgentContext,
  newMessages: AgentMessage[],
  config: AgentLoopConfig,
  signal: AbortSignal | undefined,
  emit: AgentEventSink,
  streamFn?: StreamFn
): Promise<void> {
  let firstTurn = true;
  let pendingMessages = await getSteeringMessages();
  
  // OUTER LOOP: Handles follow-up messages
  while (true) {
    let hasMoreToolCalls = true;
    
    // INNER LOOP: Processes tool calls and steering
    while (hasMoreToolCalls || pendingMessages.length > 0) {
      if (!firstTurn) {
        await emit({ type: "turn_start" });
      } else {
        firstTurn = false;
      }
      
      // Phase 1: Inject pending messages
      if (pendingMessages.length > 0) {
        for (const message of pendingMessages) {
          await emit({ type: "message_start", message });
          await emit({ type: "message_end", message });
          currentContext.messages.push(message);
          newMessages.push(message);
        }
        pendingMessages = [];
      }
      
      // Phase 2: Stream assistant response
      const message = await streamAssistantResponse(
        currentContext, config, signal, emit, streamFn
      );
      newMessages.push(message);
      
      // Phase 3: Check for errors
      if (message.stopReason === "error" || 
          message.stopReason === "aborted") {
        await emit({ type: "turn_end", message, toolResults: [] });
        await emit({ type: "agent_end", messages: newMessages });
        return;  // Exit both loops on error
      }
      
      // Phase 4: Execute tool calls
      const toolCalls = message.content.filter(c => c.type === "toolCall");
      hasMoreToolCalls = toolCalls.length > 0;
      
      const toolResults: ToolResultMessage[] = [];
      if (hasMoreToolCalls) {
        toolResults.push(...await executeToolCalls(
          currentContext, message, config, signal, emit
        ));
        
        for (const result of toolResults) {
          currentContext.messages.push(result);
          newMessages.push(result);
        }
      }
      
      // Phase 5: End turn
      await emit({ type: "turn_end", message, toolResults });
      
      // Check for more steering messages
      pendingMessages = await getSteeringMessages() || [];
    }
    
    // Agent would stop here - check for follow-ups
    const followUpMessages = await getFollowUpMessages() || [];
    if (followUpMessages.length > 0) {
      pendingMessages = followUpMessages;
      continue;  // Continue OUTER loop with follow-ups
    }
    
    // No more messages, exit both loops
    break;
  }
  
  await emit({ type: "agent_end", messages: newMessages });
}
```

### Loop Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    runLoop() Entry                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
      ┌──────────────────────────────┐
      │  Get initial steering msgs   │
      └──────────────┬───────────────┘
                     │
                     ▼
      ┌──────────────────────────────────────────┐
      │  OUTER LOOP (follow-up handling)         │
      │  while (true) {                          │
      └──────────────┬───────────────────────────┘
                     │
                     ▼
      ┌──────────────────────────────────────────┐
      │  INNER LOOP (tool calls + steering)      │
      │  while (hasMoreToolCalls || pending) {   │
      └──────────────┬───────────────────────────┘
                     │
         ┌───────────┼───────────┬────────────────┐
         │           │           │                │
         ▼           ▼           ▼                ▼
    ┌────────┐  ┌────────┐  ┌────────┐      ┌─────────┐
    │ Inject │  │ Stream │  │ Execute│      │ Check   │
    │ Pending│  │ LLM    │  │ Tools  │      │ Follow- │
    │ Msgs   │  │ Response│ │        │      │ ups     │
    └────┬───┘  └────┬───┘  └────┬───┘      └────┬────┘
         │           │           │                │
         └───────────┴─────┬─────┴────────────────┘
                           │
                    ┌──────▼───────┐
                    │ Turn Complete│
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         Has Follow-ups?           No Follow-ups?
              │                         │
              ▼                         ▼
        Continue Outer Loop       Break (Exit)
              │                         │
              └───────────┬─────────────┘
                          │
                          ▼
              Emit agent_end Event
                          │
                          ▼
                   Return newMessages
```

## Message Transformation Pipeline

### Two-Phase Transformation

The loop transforms messages in two distinct phases before each LLM call:

```typescript
async function streamAssistantResponse(
  context: AgentContext,
  config: AgentLoopConfig,
  signal: AbortSignal | undefined,
  emit: AgentEventSink,
  streamFn?: StreamFn
): Promise<AssistantMessage> {
  
  // PHASE 1: transformContext (optional)
  // Operates on AgentMessage[] level
  let messages = context.messages;
  if (config.transformContext) {
    messages = await config.transformContext(messages, signal);
  }
  
  // PHASE 2: convertToLlm (required)
  // Converts AgentMessage[] to Message[] for LLM
  const llmMessages = await config.convertToLlm(messages);
  
  // Build LLM context
  const llmContext: Context = {
    systemPrompt: context.systemPrompt,
    messages: llmMessages,
    tools: context.tools
  };
  
  // Resolve API key (important for OAuth tokens)
  const resolvedApiKey = config.getApiKey
    ? await config.getApiKey(config.model.provider)
    : undefined;
  
  // Call LLM via streamSimple
  const response = await streamFn(
    config.model, 
    llmContext, 
    { ...config, apiKey: resolvedApiKey, signal }
  );
  
  // Stream events to emitter
  let partialMessage: AssistantMessage | null = null;
  let addedPartial = false;
  
  for await (const event of response) {
    switch (event.type) {
      case "start":
        partialMessage = event.partial;
        context.messages.push(partialMessage);
        addedPartial = true;
        await emit({ type: "message_start", message: { ...partialMessage } });
        break;
        
      case "text_delta":
      case "thinking_delta":
      case "toolcall_delta":
        if (partialMessage) {
          partialMessage = event.partial;
          context.messages[context.messages.length - 1] = partialMessage;
          await emit({
            type: "message_update",
            assistantMessageEvent: event,
            message: { ...partialMessage }
          });
        }
        break;
        
      case "done":
      case "error":
        const finalMessage = await response.result();
        if (addedPartial) {
          context.messages[context.messages.length - 1] = finalMessage;
        } else {
          context.messages.push(finalMessage);
          await emit({ type: "message_start", message: { ...finalMessage } });
        }
        await emit({ type: "message_end", message: finalMessage });
        return finalMessage;
    }
  }
  
  // Fallback for incomplete streams
  const finalMessage = await response.result();
  if (addedPartial) {
    context.messages[context.messages.length - 1] = finalMessage;
  } else {
    context.messages.push(finalMessage);
    await emit({ type: "message_start", message: { ...finalMessage } });
  }
  await emit({ type: "message_end", message: finalMessage });
  return finalMessage;
}
```

### Transformation Examples

#### Filtering UI-Only Messages

```typescript
// Custom message types for UI
interface NotificationMessage {
  role: "notification";
  content: string;
  timestamp: number;
}

declare module "@mariozechner/pi-agent-core" {
  interface CustomAgentMessages {
    notification: NotificationMessage;
  }
}

// Conversion filters out UI-only messages
const agent = new Agent({
  convertToLlm: (messages) => {
    return messages.filter((msg): msg is Message => {
      return msg.role === "user" || 
             msg.role === "assistant" || 
             msg.role === "toolResult";
    });
  }
});

// UI notification won't be sent to LLM
agent.state.messages.push({
  role: "notification",
  content: "Processing large file...",
  timestamp: Date.now()
});
```

#### Context Pruning

```typescript
const agent = new Agent({
  transformContext: async (messages) => {
    // Keep system prompt + last N messages
    const MAX_MESSAGES = 20;
    
    if (messages.length <= MAX_MESSAGES) {
      return messages;
    }
    
    const [systemPrompt] = messages;
    const recentMessages = messages.slice(-MAX_MESSAGES);
    
    return [systemPrompt, ...recentMessages];
  }
});
```

#### Dynamic Context Injection

```typescript
const agent = new Agent({
  transformContext: async (messages) => {
    // Inject time-sensitive context
    const currentTime = new Date().toISOString();
    const userLocation = await getUserLocation();
    
    return [
      {
        role: "user",
        content: `Current time: ${currentTime}, Location: ${userLocation}`,
        timestamp: Date.now()
      },
      ...messages
    ];
  }
});
```

## Turn Management

### Turn Lifecycle Events

Each turn emits a specific sequence of events:

```typescript
// Turn starts
await emit({ type: "turn_start" });

// Pending messages injected
for (const msg of pendingMessages) {
  await emit({ type: "message_start", message: msg });
  await emit({ type: "message_end", message: msg });
}

// Assistant response streamed
await emit({ type: "message_start", message: partialAssistantMsg });
await emit({ type: "message_update", message: partial, assistantMessageEvent });
await emit({ type: "message_end", message: finalAssistantMsg });

// Tool executions (if any)
for (const toolCall of toolCalls) {
  await emit({ type: "tool_execution_start", toolCallId, toolName, args });
  await emit({ type: "tool_execution_update", partialResult });
  await emit({ type: "tool_execution_end", result, isError });
  
  // Tool result as message
  await emit({ type: "message_start", message: toolResultMsg });
  await emit({ type: "message_end", message: toolResultMsg });
}

// Turn ends
await emit({ type: "turn_end", message: assistantMsg, toolResults });
```

### Turn Counting and Tracking

```typescript
let turnCount = 0;
const turnHistory: Array<{
  turn: number;
  assistantMessage: AssistantMessage;
  toolResults: ToolResultMessage[];
  duration: number;
}> = [];

agent.subscribe((event) => {
  if (event.type === "turn_start") {
    turnCount++;
    const startTime = Date.now();
    
    currentTurn = {
      turn: turnCount,
      assistantMessage: null!,
      toolResults: [],
      startTime
    };
  }
  
  if (event.type === "turn_end") {
    currentTurn.assistantMessage = event.message;
    currentTurn.toolResults = event.toolResults;
    currentTurn.duration = Date.now() - currentTurn.startTime;
    
    turnHistory.push(currentTurn);
    
    console.log(
      `Turn ${turnCount} completed in ${currentTurn.duration}ms, ` +
      `${event.toolResults.length} tool calls`
    );
  }
});
```

## Steering and Follow-up Integration

### Steering Message Injection

Steering messages are checked after each turn completes:

```typescript
// After tool execution, check for steering
pendingMessages = await config.getSteeringMessages?.() || [];

if (pendingMessages.length > 0) {
  // Inner loop continues with pending messages
  // They're injected before next LLM call
} else {
  // No steering, inner loop exits if no more tool calls
}
```

### Follow-up Message Handling

Follow-ups are checked when the agent would otherwise stop:

```typescript
// After inner loop exits (no tool calls, no steering)
const followUpMessages = await config.getFollowUpMessages?.() || [];

if (followUpMessages.length > 0) {
  // Set as pending and continue outer loop
  pendingMessages = followUpMessages;
  continue;  // Back to inner loop with follow-ups
}

// No follow-ups either, exit both loops
break;
```

### Queue Mode Behavior

The `PendingMessageQueue` controls how messages are drained:

```typescript
class PendingMessageQueue {
  private messages: AgentMessage[] = [];
  
  constructor(public mode: "all" | "one-at-a-time") {}
  
  drain(): AgentMessage[] {
    if (this.mode === "all") {
      // Return all queued messages at once
      const drained = this.messages.slice();
      this.messages = [];
      return drained;
    }
    
    // Return only first message
    const first = this.messages[0];
    if (!first) return [];
    this.messages = this.messages.slice(1);
    return [first];
  }
}
```

**Mode Comparison:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| `one-at-a-time` | Process one message per turn | Safer, maintains conversation flow |
| `all` | Process all messages in one turn | Faster batch processing |

## Error Handling in Loop

### LLM Errors

```typescript
const message = await streamAssistantResponse(...);

if (message.stopReason === "error" || message.stopReason === "aborted") {
  // Emit turn end with empty tool results
  await emit({ type: "turn_end", message, toolResults: [] });
  
  // Exit loop immediately
  await emit({ type: "agent_end", messages: newMessages });
  return;
}
```

### Tool Execution Errors

Tool errors don't stop the loop - they're added as tool results:

```typescript
async function executePreparedToolCall(...) {
  try {
    const result = await prepared.tool.execute(...);
    return { result, isError: false };
  } catch (error) {
    // Convert to error result, don't throw
    return {
      result: createErrorToolResult(error.message),
      isError: true
    };
  }
}
```

### Abort Signal Handling

The loop respects abort signals throughout:

```typescript
// Passed to transformContext
if (config.transformContext) {
  messages = await config.transformContext(messages, signal);
}

// Passed to streamSimple
const response = await streamFn(config.model, llmContext, {
  ...config,
  signal
});

// Passed to tool execution
const result = await prepared.tool.execute(
  prepared.toolCall.id,
  prepared.args,
  signal  // Tool should check signal.aborted
);
```

## Message Array Management

### Context vs New Messages

The loop maintains two message arrays:

```typescript
// currentContext.messages: Full conversation history
// Used for LLM calls, includes all past messages

// newMessages: Messages added during this run
// Returned to caller, used for state updates

// Initial setup in runAgentLoop:
const newMessages: AgentMessage[] = [...prompts];
const currentContext: AgentContext = {
  ...context,
  messages: [...context.messages, ...prompts]
};

// During loop:
currentContext.messages.push(message);  // Add to context
newMessages.push(message);              // Track for return
```

### Why Two Arrays?

1. **Efficiency**: `newMessages` tracks only what changed
2. **Rollback**: Can discard `newMessages` on error without modifying context
3. **Testing**: Easy to assert what was added during a run

## Performance Considerations

### Transformation Overhead

```typescript
// transformContext called once per turn (good)
transformContext?: (messages: AgentMessage[]) => Promise<AgentMessage[]>;

// convertToLlm called once per turn (good)
convertToLlm?: (messages: AgentMessage[]) => Message[] | Promise<Message[]>;

// Both should be O(n) where n = message count
// Avoid expensive operations like re-parsing all messages
```

### Event Emission Cost

```typescript
// Events are emitted synchronously but can be async
await emit({ type: "message_start", message });

// If emit is slow, it blocks the loop
// Use lightweight emitters for best performance

// Bad: Heavy processing in emitter
agent.subscribe(async (event) => {
  if (event.type === "message_update") {
    await heavyProcessing(event.message);  // Blocks loop!
  }
});

// Good: Fire-and-forget for non-critical updates
agent.subscribe((event) => {
  if (event.type === "message_update") {
    void analytics.track(event);  // Doesn't block
  }
});
```

### Memory Management

```typescript
// Messages grow unbounded without pruning
// Implement transformContext to limit size

const agent = new Agent({
  transformContext: (messages) => {
    if (messages.length > 50) {
      // Summarize old messages or drop them
      return pruneOldMessages(messages);
    }
    return messages;
  }
});
```

## Debugging the Loop

### Event Logging

```typescript
const eventLog: AgentEvent[] = [];

agent.subscribe((event) => {
  eventLog.push({
    ...event,
    timestamp: Date.now(),
    turnCount: currentTurn
  });
  
  console.log(
    `[${event.type}] ${formatMessage(event)}`
  );
});

// After run, analyze event sequence
function analyzeEventSequence(log: AgentEvent[]) {
  const turns = log.filter(e => e.type === "turn_start").length;
  const toolCalls = log.filter(e => e.type === "tool_execution_start").length;
  const errors = log.filter(e => e.type === "turn_end" && 
    (e as any).message?.errorMessage).length;
  
  return { turns, toolCalls, errors };
}
```

### State Snapshots

```typescript
agent.subscribe((event) => {
  if (event.type === "turn_start") {
    console.log("Turn state:", {
      messageCount: agent.state.messages.length,
      pendingTools: agent.state.pendingToolCalls.size,
      isStreaming: agent.state.isStreaming
    });
  }
});
```

## Best Practices

1. **Keep transformations simple** - O(n) operations only
2. **Use async emitters sparingly** - They block loop progress
3. **Implement context pruning** - Prevent unbounded growth
4. **Log events for debugging** - Event sequence reveals issues
5. **Handle abort signals** - Tools should check `signal.aborted`
6. **Test with mock stream** - Validate loop logic without LLM calls
7. **Monitor turn counts** - Detect infinite loops early
