# Streaming System Architecture

This document covers the event-driven streaming architecture in Pi AI, including the event protocol, progressive parsing, and abort handling.

## Event Stream Protocol Overview

Pi AI uses a rich event protocol instead of simple text streams:

```typescript
type AssistantMessageEvent = 
  | { type: 'start'; partial: AssistantMessage }
  | { type: 'text_start'; contentIndex: number; partial: AssistantMessage }
  | { type: 'text_delta'; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: 'text_end'; contentIndex: number; content: string; partial: AssistantMessage }
  | { type: 'thinking_start'; contentIndex: number; partial: AssistantMessage }
  | { type: 'thinking_delta'; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: 'thinking_end'; contentIndex: number; content: string; partial: AssistantMessage }
  | { type: 'toolcall_start'; contentIndex: number; partial: AssistantMessage }
  | { type: 'toolcall_delta'; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: 'toolcall_end'; contentIndex: number; toolCall: ToolCall; partial: AssistantMessage }
  | { type: 'done'; reason: StopReason; message: AssistantMessage }
  | { type: 'error'; reason: 'aborted' | 'error'; error: AssistantMessage };
```

### Event Categories

**Lifecycle Events:**
- `start`: Stream initialization
- `done`: Successful completion
- `error`: Error or abort

**Content Events (per content block):**
- `*_start`: Beginning of a content block
- `*_delta`: Incremental updates
- `*_end`: Finalized content block

## Event Stream Implementation

### Core EventStream Class

```typescript
// In utils/event-stream.ts
export class EventStream<T, R = T> implements AsyncIterable<T> {
  private queue: T[] = [];
  private waiting: ((value: IteratorResult<T>) => void)[] = [];
  private done = false;
  private finalResultPromise: Promise<R>;
  private resolveFinalResult!: (result: R) => void;

  constructor(
    private isComplete: (event: T) => boolean,
    private extractResult: (event: T) => R,
  ) {
    this.finalResultPromise = new Promise((resolve) => {
      this.resolveFinalResult = resolve;
    });
  }

  push(event: T): void {
    if (this.done) return;

    if (this.isComplete(event)) {
      this.done = true;
      this.resolveFinalResult(this.extractResult(event));
    }

    // Deliver to waiting consumer or queue it
    const waiter = this.waiting.shift();
    if (waiter) {
      waiter({ value: event, done: false });
    } else {
      this.queue.push(event);
    }
  }

  end(result?: R): void {
    this.done = true;
    if (result !== undefined) {
      this.resolveFinalResult(result);
    }
    while (this.waiting.length > 0) {
      const waiter = this.waiting.shift()!;
      waiter({ value: undefined as any, done: true });
    }
  }

  async *[Symbol.asyncIterator](): AsyncIterator<T> {
    while (true) {
      if (this.queue.length > 0) {
        yield this.queue.shift()!;
      } else if (this.done) {
        return;
      } else {
        const result = await new Promise<IteratorResult<T>>((resolve) => 
          this.waiting.push(resolve)
        );
        if (result.done) return;
        yield result.value;
      }
    }
  }

  result(): Promise<R> {
    return this.finalResultPromise;
  }
}
```

### AssistantMessageEventStream

Specialized stream for assistant messages:

```typescript
export class AssistantMessageEventStream extends EventStream<AssistantMessageEvent, AssistantMessage> {
  constructor() {
    super(
      // Check if event completes the stream
      (event) => event.type === 'done' || event.type === 'error',
      
      // Extract final result from completion event
      (event) => {
        if (event.type === 'done') {
          return event.message;
        } else if (event.type === 'error') {
          return event.error;
        }
        throw new Error('Unexpected event type for final result');
      }
    );
  }
}

// Factory function for extensions
export function createAssistantMessageEventStream(): AssistantMessageEventStream {
  return new AssistantMessageEventStream();
}
```

## Event Emission Pattern

### Text Content Streaming

```typescript
// In provider implementation
const stream = new AssistantMessageEventStream();
const output: AssistantMessage = { ... };

stream.push({ type: 'start', partial: output });

// Initialize text block
let currentBlock: TextContent = { type: 'text', text: '' };
output.content.push(currentBlock);

stream.push({
  type: 'text_start',
  contentIndex: 0,
  partial: output
});

// Stream text deltas
for await (const chunk of upstreamStream) {
  if (chunk.delta?.content) {
    currentBlock.text += chunk.delta.content;
    
    stream.push({
      type: 'text_delta',
      contentIndex: 0,
      delta: chunk.delta.content,
      partial: output
    });
  }
}

// Finalize text block
stream.push({
  type: 'text_end',
  contentIndex: 0,
  content: currentBlock.text,
  partial: output
});

stream.push({
  type: 'done',
  reason: 'stop',
  message: output
});

stream.end();
```

### Thinking Content Streaming

```typescript
// For models with reasoning/thinking support
if (chunk.delta?.reasoning_content) {
  if (!currentBlock || currentBlock.type !== 'thinking') {
    // Finish previous block
    finishCurrentBlock(currentBlock);
    
    // Start thinking block
    currentBlock = { type: 'thinking', thinking: '' };
    output.content.push(currentBlock);
    
    stream.push({
      type: 'thinking_start',
      contentIndex: blocks.length - 1,
      partial: output
    });
  }
  
  // Stream thinking delta
  currentBlock.thinking += chunk.delta.reasoning_content;
  
  stream.push({
    type: 'thinking_delta',
    contentIndex: blocks.length - 1,
    delta: chunk.delta.reasoning_content,
    partial: output
  });
}

// End thinking block
if (finishReason === 'stop' && currentBlock?.type === 'thinking') {
  stream.push({
    type: 'thinking_end',
    contentIndex: blocks.length - 1,
    content: currentBlock.thinking,
    partial: output
  });
}
```

### Tool Call Streaming

```typescript
// Stream tool call with progressive JSON parsing
if (chunk.delta?.tool_calls) {
  const toolCallDelta = chunk.delta.tool_calls[0];
  
  if (!currentBlock || currentBlock.type !== 'toolCall') {
    finishCurrentBlock(currentBlock);
    
    // Start tool call block
    currentBlock = {
      type: 'toolCall',
      id: toolCallDelta.id || '',
      name: toolCallDelta.function?.name || '',
      arguments: {},
      partialArgs: ''
    } as ToolCall & { partialArgs: string };
    
    output.content.push(currentBlock);
    
    stream.push({
      type: 'toolcall_start',
      contentIndex: blocks.length - 1,
      partial: output
    });
  }
  
  // Accumulate partial JSON arguments
  if (toolCallDelta.function?.arguments) {
    currentBlock.partialArgs += toolCallDelta.function.arguments;
    
    stream.push({
      type: 'toolcall_delta',
      contentIndex: blocks.length - 1,
      delta: toolCallDelta.function.arguments,
      partial: output
    });
  }
}

// Finalize tool call with parsed arguments
if (finishReason === 'tool_calls' && currentBlock?.type === 'toolCall') {
  const toolCall = currentBlock as ToolCall & { partialArgs?: string };
  
  // Parse final JSON
  toolCall.arguments = parseStreamingJson(toolCall.partialArgs);
  delete toolCall.partialArgs;
  
  stream.push({
    type: 'toolcall_end',
    contentIndex: blocks.length - 1,
    toolCall: toolCall,
    partial: output
  });
}
```

## Progressive JSON Parsing

### Partial JSON Parser

```typescript
// In utils/json-parse.ts
import { parse as partialParse } from 'partial-json';

export function parseStreamingJson<T = any>(partialJson: string | undefined): T {
  if (!partialJson || partialJson.trim() === '') {
    return {} as T;
  }
  
  // Try standard parsing first (fastest for complete JSON)
  try {
    return JSON.parse(partialJson) as T;
  } catch {
    // Try partial-json for incomplete JSON
    try {
      const result = partialParse(partialJson);
      return (result ?? {}) as T;
    } catch {
      // If all parsing fails, return empty object
      return {} as T;
    }
  }
}

// Usage example:
const partialArgs = '{"location": "London", "units": "ce';
const parsed = parseStreamingJson<{ location?: string; units?: string }>(partialArgs);
// → { location: 'London', units: undefined }

// Allows UI to show partial data immediately:
if (parsed.location) {
  showLocationInput(parsed.location);
}
```

### Progressive Parsing Benefits

1. **Real-time UI Updates**: Show tool arguments as they're generated
2. **Early Validation**: Validate partial data before completion
3. **Better UX**: Users see progress instead of waiting for full response
4. **Debugging**: Inspect intermediate states during streaming

## Abort Handling

### Signal-Based Abortion

```typescript
// In provider implementation
const stream = new AssistantMessageEventStream();

(async () => {
  try {
    const controller = new AbortController();
    const signal = options?.signal || controller.signal;
    
    const upstreamStream = await apiCall({ signal });
    
    for await (const chunk of upstreamStream) {
      if (signal.aborted) {
        // Emit abort event
        stream.push({
          type: 'error',
          reason: 'aborted',
          error: {
            ...output,
            stopReason: 'aborted',
            errorMessage: 'Request aborted by user'
          }
        });
        stream.end();
        return;
      }
      
      // Process chunk...
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      stream.push({
        type: 'error',
        reason: 'aborted',
        error: output
      });
    } else {
      stream.push({
        type: 'error',
        reason: 'error',
        error: { ...output, stopReason: 'error', errorMessage: error.message }
      });
    }
    stream.end();
  }
})();

return stream;
```

### User-Initiated Abort

```typescript
// In application code
const controller = new AbortController();

const stream = stream(model, context, { signal: controller.signal });

const eventTask = (async () => {
  for await (const event of stream) {
    console.log(event.type);
  }
})();

// Abort after 5 seconds
setTimeout(() => {
  controller.abort();
  console.log('Aborted!');
}, 5000);

await eventTask;
```

## Multi-Content Streaming

### Interleaved Content Types

Models can emit multiple content types in a single response:

```typescript
// Example: thinking → text → tool call
const output: AssistantMessage = {
  role: 'assistant',
  content: [],
  api: model.api,
  provider: model.provider,
  model: model.id,
  usage: { ... },
  stopReason: 'stop',
  timestamp: Date.now()
};

// 1. Thinking block
output.content.push({ type: 'thinking', thinking: '' });
stream.push({ type: 'thinking_start', contentIndex: 0, partial: output });
stream.push({ type: 'thinking_delta', contentIndex: 0, delta: 'Let me think...', partial: output });
stream.push({ type: 'thinking_end', contentIndex: 0, content: 'Let me think about this', partial: output });

// 2. Text block
output.content.push({ type: 'text', text: '' });
stream.push({ type: 'text_start', contentIndex: 1, partial: output });
stream.push({ type: 'text_delta', contentIndex: 1, delta: 'The answer is ', partial: output });
stream.push({ type: 'text_end', contentIndex: 1, content: 'The answer is 42', partial: output });

// 3. Tool call block
output.content.push({ type: 'toolCall', id: '123', name: 'save_result', arguments: {} });
stream.push({ type: 'toolcall_start', contentIndex: 2, partial: output });
stream.push({ type: 'toolcall_delta', contentIndex: 2, delta: '{"value":', partial: output });
stream.push({ type: 'toolcall_delta', contentIndex: 2, delta: ' 42}', partial: output });
stream.push({ type: 'toolcall_end', contentIndex: 2, toolCall: { ... }, partial: output });

// Complete
stream.push({ type: 'done', reason: 'toolUse', message: output });
stream.end();
```

### Consumer Pattern for Multi-Content

```typescript
for await (const event of stream) {
  switch (event.type) {
    case 'thinking_delta':
      // Show thinking in collapsed section
      updateThinkingDisplay(event.delta);
      break;
      
    case 'text_delta':
      // Stream text to main output
      appendText(event.delta);
      break;
      
    case 'toolcall_delta':
      // Show tool call being constructed
      const partialArgs = parseStreamingJson(accumulateToolArgs(event.delta));
      updateToolCallUI(partialArgs);
      break;
      
    case 'toolcall_end':
      // Execute tool call
      const result = await executeTool(event.toolCall);
      
      // Add tool result to context
      context.messages.push({
        role: 'toolResult',
        toolCallId: event.toolCall.id,
        toolName: event.toolCall.name,
        content: [{ type: 'text', text: JSON.stringify(result) }],
        isError: false,
        timestamp: Date.now()
      });
      
      // Continue streaming with new context
      break;
      
    case 'done':
      console.log(`Completed: ${event.reason}`);
      break;
  }
}
```

## Event Stream Forwarding

### Proxy Pattern for Lazy Loading

```typescript
// In register-builtins.ts
function forwardStream(
  target: AssistantMessageEventStream,
  source: AsyncIterable<AssistantMessageEvent>
): void {
  (async () => {
    for await (const event of source) {
      target.push(event);
    }
    target.end();
  })();
}

// Usage in lazy provider loading
function createLazyStream(loadModule: () => Promise<Module>): StreamFunction {
  return (model, context, options) => {
    const outer = new AssistantMessageEventStream();
    
    loadModule()
      .then(module => {
        const inner = module.stream(model, context, options);
        forwardStream(outer, inner);
      })
      .catch(error => {
        outer.push({
          type: 'error',
          reason: 'error',
          error: createErrorMessage(model, error)
        });
        outer.end();
      });
      
    return outer;
  };
}
```

## Performance Optimizations

### Backpressure Handling

The event stream handles consumers slower than producers:

```typescript
// Events are queued if consumer is slow
push(event: T): void {
  const waiter = this.waiting.shift();
  if (waiter) {
    waiter({ value: event, done: false }); // Fast path: direct delivery
  } else {
    this.queue.push(event); // Slow path: queue for later
  }
}

// Queue grows as needed (memory trade-off)
// Consider implementing max queue size for production use
```

### Memory Efficiency

Events reference shared `partial` message object:

```typescript
// All events share the same partial message instance
const output: AssistantMessage = { ... };

stream.push({ type: 'text_start', contentIndex: 0, partial: output });
stream.push({ type: 'text_delta', contentIndex: 0, delta: 'Hello ', partial: output });
stream.push({ type: 'text_delta', contentIndex: 0, delta: 'World', partial: output });

// Memory efficient: only one AssistantMessage object
// Each event is small (~50 bytes) + reference to shared object
```

## Debugging and Testing

### Event Logging

```typescript
const events: AssistantMessageEvent[] = [];

for await (const event of stream) {
  events.push(event);
  console.log(`${event.type}:`, 
    event.type === 'text_delta' ? event.delta :
    event.type === 'done' ? event.reason :
    '...'
  );
}

// Replay events for debugging
for (const event of events) {
  console.dir(event, { depth: null });
}
```

### Test Helpers

```typescript
// In providers/faux.ts
export function createFauxStream(responses: FauxResponseStep[]): AssistantMessageEventStream {
  const stream = new AssistantMessageEventStream();
  
  (async () => {
    for (const response of responses) {
      const message = typeof response === 'function' 
        ? await response(context, options, state)
        : response;
      
      // Simulate streaming
      for (const block of message.content) {
        if (block.type === 'text') {
          stream.push({ type: 'text_start', contentIndex: 0, partial: message });
          
          // Stream character by character
          for (let i = 0; i < block.text.length; i++) {
            await sleep(10); // Simulate network latency
            stream.push({
              type: 'text_delta',
              contentIndex: 0,
              delta: block.text[i],
              partial: message
            });
          }
          
          stream.push({ type: 'text_end', contentIndex: 0, content: block.text, partial: message });
        }
      }
      
      stream.push({ type: 'done', reason: message.stopReason, message });
    }
    
    stream.end();
  })();
  
  return stream;
}
```

## Best Practices

1. **Always Emit Start/End**: Each content block should have `*_start` and `*_end` events
2. **Include Partial Message**: Every event includes current state via `partial`
3. **Handle Abort Gracefully**: Check `signal.aborted` in streaming loops
4. **Queue Events**: Don't assume consumer keeps up with producer
5. **Parse Progressively**: Use `parseStreamingJson()` for tool arguments
6. **Test Event Order**: Verify events emit in correct sequence

## Common Patterns

### Text-Only Streaming

```typescript
const stream = streamSimple(model, context);

for await (const event of stream) {
  if (event.type === 'text_delta') {
    process.stdout.write(event.delta);
  }
}

const message = await stream.result();
console.log(`\nTotal tokens: ${message.usage.output}`);
```

### Tool-Using Streaming

```typescript
const stream = stream(model, context, { tools });

for await (const event of stream) {
  if (event.type === 'toolcall_end') {
    const result = await executeTool(event.toolCall);
    
    // Add result to context for next turn
    context.messages.push({
      role: 'toolResult',
      toolCallId: event.toolCall.id,
      toolName: event.toolCall.name,
      content: [{ type: 'text', text: JSON.stringify(result) }],
      isError: false,
      timestamp: Date.now()
    });
  }
}
```

### Thinking-Aware Streaming

```typescript
let isThinking = false;

for await (const event of stream) {
  if (event.type === 'thinking_start') {
    isThinking = true;
    showThinkingIndicator();
  }
  
  if (event.type === 'thinking_delta' && isThinking) {
    updateThinkingDisplay(event.delta);
  }
  
  if (event.type === 'thinking_end') {
    isThinking = false;
    hideThinkingIndicator();
  }
  
  if (event.type === 'text_delta' && !isThinking) {
    appendText(event.delta);
  }
}
```
