# Streaming APIs and Event Contracts

How production agents implement real-time tool call streaming using SSE (Server-Sent Events) for responsive UIs.

## The Problem

For an agent, "streaming text" isn't enough. You need the model to tell you about tool calls **as they happen**, not after everything is done. This is what makes a coding agent feel responsive rather than frozen.

**Latency target**: ~100ms end-to-end for perceived immediacy (classic HCI guidance).

## The Solution: Event-Based Streaming

When you ask an agent to "read main.py and fix the bug," the model doesn't just generate text. Behind the scenes:

1. Model decides to call a tool (e.g., `read_file`)
2. Generates arguments for that tool (`{"path": "src/main.py"}`)
3. Harness executes it
4. Returns results to model

**All of this happens over a streaming connection using SSE** - a web standard that lets a server push data to a client over a single long-lived HTTP connection.

## Three-Phase Streaming Lifecycle

Both Anthropic and OpenAI expose similar three-phase streaming for tool calls:

### Phase 1: Tool Call Starting

The model has decided to call a tool. You get the tool name and unique call ID immediately, **before** arguments are fully generated. The UI can already show "Reading main.py..." while the model is still generating.

**Anthropic Messages API**:
```json
{
  "type": "content_block_start",
  "index": 1,
  "content_block": {
    "type": "tool_use",
    "id": "toolu_01T1xKzZvQPNmR7Y8vN2pQ3wXy",
    "name": "read_file",
    "input": {}
  }
}
```

**OpenAI Responses API**:
```json
{
  "type": "response.output_item.added",
  "item": {
    "id": "fc_001",
    "type": "function_call",
    "name": "read_file",
    "arguments": ""
  }
}
```

### Phase 2: Arguments Streaming

The model generates JSON arguments token by token. You see arguments building up incrementally in the UI, making the whole interaction feel more responsive.

**Anthropic**:
```json
{
  "type": "content_block_delta",
  "index": 1,
  "delta": {
    "type": "input_json_delta",
    "partial_json": "{\"path\": \"src/m"
  }
}
{
  "type": "content_block_delta",
  "index": 1,
  "delta": {
    "type": "input_json_delta",
    "partial_json": "ain.py\"}"
  }
}
```

**OpenAI**:
```json
{
  "type": "response.function_call_arguments.delta",
  "item_id": "fc_001",
  "delta": "{\"path\": \"src/m"
}
{
  "type": "response.function_call_arguments.delta",
  "item_id": "fc_001",
  "delta": "ain.py\"}"
}
```

### Phase 3: Tool Call Complete

The tool call is fully formed. Arguments are finalized, harness can now actually execute the tool.

**Anthropic**:
```json
{
  "type": "content_block_stop",
  "index": 1
}
```

**OpenAI**:
```json
{
  "type": "response.function_call_arguments.done",
  "item_id": "fc_001",
  "arguments": "{\"path\": \"src/main.py\"}",
  "name": "read_file"
}
```

## Implementation: SSE Client

```typescript
class StreamingAgentClient {
  private eventStream: EventSource;
  private toolCallBuffers: Map<string, PartialToolCall> = new Map();
  
  async streamRequest(prompt: string, onEvent: (event: AgentEvent) => void) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': process.env.ANTHROPIC_API_KEY,
        'Anthropic-Beta': 'tools-2024-05-11'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4096,
        stream: true,
        messages: [{ role: 'user', content: prompt }],
        tools: this.getToolDefinitions()
      })
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const events = this.parseSSEEvents(chunk);
      
      for (const event of events) {
        await this.handleEvent(event, onEvent);
      }
    }
  }
  
  private async handleEvent(event: any, onEvent: (event: AgentEvent) => void) {
    switch (event.type) {
      case 'content_block_start':
        if (event.content_block.type === 'tool_use') {
          // Phase 1: Tool call starting
          this.toolCallBuffers.set(event.content_block.id, {
            id: event.content_block.id,
            name: event.content_block.name,
            arguments: ''
          });
          
          onEvent({
            type: 'tool_call_start',
            tool: event.content_block.name,
            callId: event.content_block.id
          });
        }
        break;
      
      case 'content_block_delta':
        if (event.delta.type === 'input_json_delta') {
          // Phase 2: Arguments streaming
          const buffer = this.toolCallBuffers.get(event.index);
          if (buffer) {
            buffer.arguments += event.delta.partial_json;
            
            onEvent({
              type: 'tool_call_arguments_streaming',
              callId: buffer.id,
              argumentsSoFar: buffer.arguments
            });
          }
        }
        break;
      
      case 'content_block_stop':
        // Phase 3: Tool call complete
        const buffer = this.toolCallBuffers.get(event.index);
        if (buffer) {
          const toolResult = await this.executeTool(buffer.name, buffer.arguments);
          
          onEvent({
            type: 'tool_call_complete',
            callId: buffer.id,
            tool: buffer.name,
            result: toolResult
          });
          
          this.toolCallBuffers.delete(buffer.id);
        }
        break;
    }
  }
}
```

## Implementation: Event-Driven UI

```typescript
// OpenCode-style event-driven TUI
class TuiApp {
  constructor(private sdk: AgentSDK) {}
  
  initializeEventHandlers() {
    // Subscribe to tool call events
    this.sdk.event.on(ToolEvent.CallStart.type, (evt) => {
      this.statusBar.show(`Executing: ${evt.properties.tool}...`);
      this.toast.show({
        title: 'Tool Execution',
        message: `Starting ${evt.properties.tool}`,
        variant: 'info',
        duration: 2000
      });
    });
    
    this.sdk.event.on(ToolEvent.ArgumentsStreaming.type, (evt) => {
      // Update progress indicator with streaming arguments
      this.toolPanel.updateArguments(evt.properties.callId, evt.properties.argumentsSoFar);
    });
    
    this.sdk.event.on(ToolEvent.CallComplete.type, (evt) => {
      this.statusBar.clear();
      
      if (evt.properties.result.success) {
        this.toast.show({
          title: 'Success',
          message: `${evt.properties.tool} completed`,
          variant: 'success'
        });
      } else {
        this.toast.show({
          title: 'Error',
          message: evt.properties.result.error,
          variant: 'error'
        });
      }
      
      // Update conversation history
      this.conversationPanel.addToolCall(evt.properties);
    });
  }
}
```

## Why This Matters for Harnesses

Without these events, you'd have to wait for the entire model response to finish before you even know a tool call happened. With them:

1. **Real-time feedback**: UI shows what agent is doing immediately
2. **Early preparation**: Can start preparing execution environment (spinning up sandbox)
3. **Persistence**: Each event can be logged to timeline for replay and debugging
4. **User intervention**: User can approve/deny tool calls as they're being generated

**Codex is built around consuming Responses API SSE streams** and translating them into internal events for its own clients and surfaces.

## Open Responses Standard

Launched January 2026, Open Responses defines provider-agnostic API shape:

```typescript
interface OpenResponsesEvent {
  type: string;
  timestamp: number;
  data: any;
}

// Semantic streaming events
type SemanticEventType = 
  | 'item.added'          // New item (message, tool call) starting
  | 'item.delta'          // Item content streaming
  | 'item.done'           // Item complete
  | 'tool_call.start'     // Tool call beginning
  | 'tool_call.arguments' // Arguments streaming
  | 'tool_call.done'      // Tool call ready to execute
  | 'response.completed'; // Entire response done

// Provider-agnostic tool invocation
interface ToolInvocation {
  call_id: string;
  name: string;
  arguments: Record<string, any>;
  output?: any;
}
```

**Benefits**:
- Write harness code once, work with multiple providers
- Switch models without rewriting streaming logic
- Future-proof against API changes

## Multi-Turn Thread State

Agents aren't "one request." They're threads that grow until they hit context window, then require compaction or truncation strategies.

### Thread Management

```typescript
class ThreadManager {
  private threads: Map<string, ThreadState> = new Map();
  
  async getThread(threadId: string): Promise<ThreadState> {
    if (!this.threads.has(threadId)) {
      this.threads.set(threadId, {
        id: threadId,
        messages: [],
        toolCalls: [],
        createdAt: new Date()
      });
    }
    return this.threads.get(threadId)!;
  }
  
  async addMessage(threadId: string, message: Message) {
    const thread = await this.getThread(threadId);
    thread.messages.push(message);
    
    // Check if context window is getting full
    const tokenCount = this.countTokens(thread.messages);
    if (tokenCount > this.MAX_TOKENS * 0.8) {
      await this.compactThread(thread);
    }
  }
  
  private async compactThread(thread: ThreadState) {
    // Summarize early messages
    const earlyMessages = thread.messages.slice(0, thread.messages.length / 2);
    const summary = await this.summarizeMessages(earlyMessages);
    
    // Replace with summary
    thread.messages = [
      { role: 'assistant', content: `Summary of earlier conversation: ${summary}` },
      ...thread.messages.slice(thread.messages.length / 2)
    ];
  }
}
```

### Context Compaction Strategies

**1. Summarization**:
```typescript
async function summarizeThread(messages: Message[]): Promise<string> {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    body: JSON.stringify({
      model: 'claude-3-haiku', // Cheap model for summarization
      max_tokens: 500,
      messages: [
        { 
          role: 'user', 
          content: `Summarize this conversation for context. Extract key decisions, facts, and current state:\n\n${formatMessages(messages)}` 
        }
      ]
    })
  });
  
  const data = await response.json();
  return data.content[0].text;
}
```

**2. Selective Forgetting**:
```typescript
function selectRelevantMessages(
  allMessages: Message[],
  currentTask: string,
  maxTokens: number
): Message[] {
  // Score messages by relevance to current task
  const scored = allMessages.map(msg => ({
    message: msg,
    score: calculateRelevanceScore(msg, currentTask),
    tokens: countTokens(msg)
  }));
  
  // Sort by score and take top messages until token limit
  scored.sort((a, b) => b.score - a.score);
  
  const selected: Message[] = [];
  let totalTokens = 0;
  
  for (const item of scored) {
    if (totalTokens + item.tokens < maxTokens) {
      selected.push(item.message);
      totalTokens += item.tokens;
    }
  }
  
  // Restore chronological order
  return selected.sort((a, b) => a.timestamp - b.timestamp);
}
```

## Cost Considerations

OpenAI notes: "Generally, the cost of sampling the model dominates the cost of network traffic, making sampling the primary target of our efficiency efforts. This is why prompt caching is so important."

### Prompt Caching

```typescript
async function createMessageWithCachedContext(
  systemPrompt: string,
  documentation: string[], // Frequently accessed docs
  userMessage: string
) {
  return fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    body: JSON.stringify({
      model: 'claude-3-5-sonnet',
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'document',
              source: {
                type: 'text',
                media_type: 'text/markdown',
                data: documentation.join('\n\n')
              },
              cache_control: { type: 'ephemeral' } // Cache this
            },
            { type: 'text', text: userMessage }
          ]
        }
      ],
      system: systemPrompt
    })
  });
}
```

**Benefits**:
- Cached content doesn't count against context window
- Repeated access to cached content is cheaper
- Ideal for system prompts and frequently-accessed documentation

## Error Handling in Streaming

```typescript
async function streamWithErrorHandling(
  prompt: string,
  onEvent: (event: any) => void
) {
  let isComplete = false;
  
  try {
    while (!isComplete) {
      const event = await nextEvent();
      
      if (event.type === 'error') {
        throw new StreamingError(event.error);
      }
      
      onEvent(event);
      
      if (event.type === 'message_stop' || event.type === 'response.completed') {
        isComplete = true;
      }
    }
  } catch (error) {
    if (error instanceof StreamingError) {
      // Handle streaming-specific errors
      this.handleError(error);
    } else {
      // Network or other errors
      this.handleNetworkError(error);
    }
  }
}
```

## Best Practices

### 1. Show Progress During Tool Calls

```typescript
// Bad: No feedback during long tool calls
await executeTool(toolName, args);

// Good: Stream progress updates
const progressStream = executeToolWithProgress(toolName, args);
for await (const progress of progressStream) {
  ui.updateProgress(progress);
}
```

### 2. Buffer and Validate JSON Arguments

```typescript
class JsonArgumentBuffer {
  private buffer = '';
  
  append(chunk: string): string | null {
    this.buffer += chunk;
    
    try {
      const parsed = JSON.parse(this.buffer);
      this.buffer = '';
      return JSON.stringify(parsed); // Return validated JSON
    } catch {
      // Not complete yet, keep buffering
      return null;
    }
  }
  
  getIncomplete(): string {
    return this.buffer;
  }
}
```

### 3. Handle Partial Tool Execution

```typescript
async function executeToolWithTimeout(
  toolName: string,
  args: any,
  timeoutMs: number = 60000
) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const result = await Promise.race([
      executeTool(toolName, args),
      new Promise<never>((_, reject) => {
        controller.signal.addEventListener('abort', () => {
          reject(new TimeoutError(`Tool ${toolName} timed out`));
        });
      })
    ]);
    
    clearTimeout(timeoutId);
    return result;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}
```

### 4. Persist Events for Replay

```typescript
class EventLogger {
  private events: AgentEvent[] = [];
  
  log(event: AgentEvent): void {
    this.events.push({
      ...event,
      timestamp: Date.now(),
      sequenceNumber: this.events.length
    });
    
    // Also persist to disk/database
    this.persistEvent(event);
  }
  
  async replay(fromSequence: number): Promise<AgentEvent[]> {
    return this.events
      .filter(e => e.sequenceNumber >= fromSequence)
      .sort((a, b) => a.timestamp - b.timestamp);
  }
}
```

## References

- **Anthropic Streaming Docs**: https://docs.anthropic.com/en/api/messages-streaming
- **OpenAI Responses API**: https://platform.openai.com/docs/api-reference/responses-streaming
- **Open Responses Standard**: https://www.openresponses.org/
- **SSE Specification**: https://html.spec.whatwg.org/multipage/server-sent-events.html

## Key Takeaways

1. **Streaming as events, not just text** - Tool calls must stream as they happen for responsive UIs
2. **Three-phase lifecycle** - Start (tool name + ID), Delta (arguments streaming), Stop (execute)
3. **100ms latency target** - For perceived immediacy in user experience
4. **SSE is the standard** - Server-Sent Events for real-time updates
5. **Open Responses for portability** - Provider-agnostic API shape
6. **Context compaction matters** - Threads grow until they hit context window limits
7. **Prompt caching reduces cost** - Cache frequent context portions
8. **Event persistence enables replay** - Log all events for debugging and recovery
