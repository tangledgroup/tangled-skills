# Provider Implementation Patterns

This document covers the implementation patterns used across different provider implementations in Pi AI.

## Core Provider Interface

All providers implement the same interface:

```typescript
interface ApiProvider<TApi extends Api = Api, TOptions extends StreamOptions = StreamOptions> {
  api: TApi;
  stream: StreamFunction<TApi, TOptions>;
  streamSimple: StreamFunction<TApi, SimpleStreamOptions>;
}
```

### Registration Pattern

Providers register themselves with the API registry:

```typescript
// In register-builtins.ts
registerApiProvider({
  api: 'anthropic-messages',
  stream: streamAnthropic,
  streamSimple: streamSimpleAnthropic
});
```

**Lazy Loading**: Providers are loaded on-demand to reduce bundle size:

```typescript
function createLazyStream(loadModule: () => Promise<Module>): StreamFunction {
  return (model, context, options) => {
    const outer = new AssistantMessageEventStream();
    
    loadModule()
      .then(module => {
        const inner = module.stream(model, context, options);
        forwardStream(outer, inner);
      })
      .catch(error => {
        outer.push({ type: 'error', error: createErrorMessage(error) });
        outer.end();
      });
      
    return outer;
  };
}
```

## Message Transformation Pattern

Providers transform unified messages to their API format:

```typescript
// In transform-messages.ts
export function transformMessages<TApi extends Api>(
  messages: Message[],
  model: Model<TApi>,
  normalizeToolCallId?: (id: string, model: Model<TApi>) => string
): Message[] {
  const toolCallIdMap = new Map<string, string>();
  
  // First pass: transform assistant messages
  const transformed = messages.map(msg => {
    if (msg.role === 'assistant') {
      return {
        ...msg,
        content: msg.content.flatMap(block => {
          if (block.type === 'thinking') {
            // Convert thinking to text for models that don't support it
            if (!isSameModel && !block.redacted) {
              return { type: 'text', text: block.thinking };
            }
          }
          if (block.type === 'toolCall' && normalizeToolCallId) {
            // Normalize tool call IDs for cross-provider compatibility
            const normalizedId = normalizeToolCallId(block.id, model);
            return { ...block, id: normalizedId };
          }
          return block;
        })
      };
    }
    return msg;
  });
  
  return transformed;
}
```

### Tool Call ID Normalization

OpenAI Responses API generates IDs that are 450+ characters with special characters. Anthropic requires IDs matching `^[a-zA-Z0-9_-]+$` (max 64 chars):

```typescript
// In anthropic.ts
function normalizeToolCallId(id: string, model: Model<Api>): string {
  // Hash long IDs to short ones
  const hash = shortHash(id);
  return `tool_${hash}`; // Max 32 chars
}
```

## Content Block Conversion Pattern

Each provider converts unified content blocks to their format:

### Anthropic Example

```typescript
function convertContentBlocks(
  content: (TextContent | ImageContent)[]
): string | Array<{ type: 'text'; text: string } | { type: 'image'; source: ... }> {
  const hasImages = content.some(c => c.type === 'image');
  
  if (!hasImages) {
    // Anthropic accepts plain string for text-only messages
    return content.map(c => (c as TextContent).text).join('\n');
  }
  
  // Convert to content block array for images
  const blocks = content.map(block => {
    if (block.type === 'text') {
      return { type: 'text', text: block.text };
    }
    return {
      type: 'image',
      source: {
        type: 'base64',
        media_type: block.mimeType,
        data: block.data
      }
    };
  });
  
  // Anthropic requires at least one text block
  if (!blocks.some(b => b.type === 'text')) {
    blocks.unshift({ type: 'text', text: '(see attached image)' });
  }
  
  return blocks;
}
```

### OpenAI Example

```typescript
function convertContentBlocks(
  content: (TextContent | ImageContent)[]
): ChatCompletionContentPart[] {
  return content.map(block => {
    if (block.type === 'text') {
      return { type: 'text', text: block.text };
    }
    return {
      type: 'image_url',
      image_url: {
        url: `data:${block.mimeType};base64,${block.data}`
      }
    };
  });
}
```

## Streaming Event Emission Pattern

Providers emit events as they receive data from upstream APIs:

```typescript
// In openai-completions.ts
const stream = new AssistantMessageEventStream();

for await (const chunk of openaiStream) {
  const choice = chunk.choices[0];
  
  if (choice.delta?.content) {
    // Emit text_delta event for each chunk
    stream.push({
      type: 'text_delta',
      contentIndex: blocks.length - 1,
      delta: choice.delta.content,
      partial: output
    });
    
    // Update local state
    currentBlock.text += choice.delta.content;
  }
  
  if (choice.delta?.tool_calls) {
    // Emit toolcall_delta for streaming tool arguments
    stream.push({
      type: 'toolcall_delta',
      contentIndex: blocks.length - 1,
      delta: JSON.stringify(choice.delta.tool_calls[0].function.arguments),
      partial: output
    });
  }
  
  if (choice.finish_reason) {
    // Emit done event when complete
    stream.push({
      type: 'done',
      reason: mapStopReason(choice.finish_reason),
      message: output
    });
  }
}

stream.end();
```

## Progressive JSON Parsing Pattern

Tool arguments are parsed incrementally during streaming:

```typescript
// In utils/json-parse.ts
export function parseStreamingJson<T = any>(partialJson: string): T {
  if (!partialJson || partialJson.trim() === '') {
    return {} as T;
  }
  
  // Try standard parsing first
  try {
    return JSON.parse(partialJson) as T;
  } catch {
    // Try partial-json for incomplete JSON
    try {
      return partialParse(partialJson) as T;
    } catch {
      return {} as T;
    }
  }
}

// Usage in provider:
if (event.type === 'toolcall_delta') {
  const parsedArgs = parseStreamingJson(currentBlock.partialArgs);
  // Show partial data in UI immediately
  if (parsedArgs.location) {
    showLocationInput(parsedArgs.location);
  }
}
```

## Error Handling Pattern

Providers map upstream errors to unified format:

```typescript
// In openai-completions.ts
function mapStopReason(finishReason: string): { 
  stopReason: StopReason; 
  errorMessage?: string 
} {
  switch (finishReason) {
    case 'stop':
      return { stopReason: 'stop' };
    case 'length':
      return { stopReason: 'length' };
    case 'tool_calls':
      return { stopReason: 'toolUse' };
    case 'content_filter':
      return { 
        stopReason: 'error', 
        errorMessage: 'Content filtered by safety system' 
      };
    default:
      return { 
        stopReason: 'error', 
        errorMessage: `Unknown finish reason: ${finishReason}` 
      };
  }
}

// In stream function:
try {
  // API call
} catch (error) {
  const errorMessage = error instanceof Error ? error.message : String(error);
  
  output.stopReason = 'error';
  output.errorMessage = errorMessage;
  
  stream.push({
    type: 'error',
    reason: 'error',
    error: output
  });
  stream.end();
}
```

## Token Usage Tracking Pattern

Providers track token usage from API responses:

```typescript
// In openai-completions.ts
function parseChunkUsage(usage: any, model: Model<Api>): Usage {
  return {
    input: usage.prompt_tokens || 0,
    output: usage.completion_tokens || 0,
    cacheRead: usage.prompt_tokens_details?.cached_tokens || 0,
    cacheWrite: 0, // Not typically reported by OpenAI
    totalTokens: (usage.total_tokens || 0),
    cost: {
      input: 0,
      output: 0,
      cacheRead: 0,
      cacheWrite: 0,
      total: 0
    }
  };
}

// Calculate costs after receiving usage
output.usage = parseChunkUsage(chunk.usage, model);
calculateCost(model, output.usage);
```

## API Key Resolution Pattern

Providers resolve API keys from multiple sources:

```typescript
// In env-api-keys.ts
export function getEnvApiKey(provider: KnownProvider): string | undefined {
  // Special handling for OAuth providers
  if (provider === 'anthropic') {
    return process.env.ANTHROPIC_OAUTH_TOKEN || process.env.ANTHROPIC_API_KEY;
  }
  
  // AWS Bedrock supports multiple auth methods
  if (provider === 'amazon-bedrock') {
    if (process.env.AWS_PROFILE || 
        (process.env.AWS_ACCESS_KEY_ID && process.env.AWS_SECRET_ACCESS_KEY) ||
        process.env.AWS_BEARER_TOKEN_BEDROCK) {
      return '<authenticated>';
    }
  }
  
  // Standard API key providers
  const envMap: Record<string, string> = {
    openai: 'OPENAI_API_KEY',
    google: 'GEMINI_API_KEY',
    groq: 'GROQ_API_KEY',
    // ... more providers
  };
  
  return process.env[envMap[provider]];
}
```

## Provider-Specific Options Pattern

Providers expose custom options while maintaining compatibility:

```typescript
// In anthropic.ts
export interface AnthropicOptions extends StreamOptions {
  thinkingEnabled?: boolean;
  thinkingBudgetTokens?: number;
  effort?: 'low' | 'medium' | 'high' | 'max';
  interleavedThinking?: boolean;
  toolChoice?: 'auto' | 'any' | 'none' | { type: 'tool'; name: string };
}

// In openai-completions.ts
export interface OpenAICompletionsOptions extends StreamOptions {
  toolChoice?: 'auto' | 'none' | 'required' | { type: 'function'; function: { name: string } };
  reasoningEffort?: 'minimal' | 'low' | 'medium' | 'high' | 'xhigh';
}

// In google.ts
export interface GoogleOptions extends StreamOptions {
  thinkingBudget?: number;
  includeThoughts?: boolean;
  toolConfig?: { functionCallingConfig: { mode: 'AUTO' | 'ANY' | 'NONE' } };
}
```

## Compatibility Detection Pattern

Providers auto-detect compatibility based on URL:

```typescript
// In openai-completions.ts
function detectCompatibility(baseUrl: string): OpenAICompletionsCompat {
  const compat: OpenAICompletionsCompat = {};
  
  // Auto-detect store support
  if (baseUrl.includes('api.openai.com')) {
    compat.supportsStore = true;
    compat.supportsDeveloperRole = true;
  }
  
  // Auto-detect reasoning support
  if (baseUrl.includes('groq.com')) {
    compat.requiresThinkingAsText = true;
  }
  
  // OpenRouter-specific routing
  if (baseUrl.includes('openrouter.ai')) {
    compat.thinkingFormat = 'openrouter';
  }
  
  return compat;
}
```

## Error Recovery Pattern

Providers implement retry logic with exponential backoff:

```typescript
// In provider implementation
async function callWithRetry(
  apiCall: () => Promise<Response>,
  maxRetries = 3
): Promise<Response> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      const isRetryable = error.status === 429 || 
                          error.status >= 500 ||
                          error.code === 'ECONNRESET';
      
      if (!isRetryable || i === maxRetries - 1) {
        throw error;
      }
      
      // Exponential backoff with jitter
      const delay = Math.min(
        1000 * Math.pow(2, i) + Math.random() * 1000,
        options?.maxRetryDelayMs || 60000
      );
      
      await sleep(delay);
    }
  }
  throw new Error('Max retries exceeded');
}
```

## Key Takeaways

1. **Unified Interface**: All providers implement the same `stream()` and `streamSimple()` interface
2. **Message Transformation**: Convert between unified format and provider-specific formats
3. **Event Emission**: Rich event types for real-time updates
4. **Progressive Parsing**: Parse JSON incrementally during streaming
5. **Error Mapping**: Map provider-specific errors to unified format
6. **Lazy Loading**: Load providers on-demand to reduce bundle size
7. **Compatibility Detection**: Auto-detect provider capabilities from URL
8. **Retry Logic**: Implement exponential backoff for transient failures

These patterns enable Pi AI to support 25+ providers while maintaining a consistent, type-safe interface.
