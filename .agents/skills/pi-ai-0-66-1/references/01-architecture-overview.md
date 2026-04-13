# Architecture Overview

## System Architecture

Pi AI 0.66.1 implements a layered architecture that abstracts away provider-specific details while maintaining type safety and extensibility.

### Layer 1: Public API

```typescript
// Core entry points
export function stream(model, context, options): AssistantMessageEventStream
export function complete(model, context, options): Promise<AssistantMessage>
export function streamSimple(model, context, options): AssistantMessageEventStream
export function getModel(provider, modelId): Model<Api>
```

**Design Decision:** Minimal surface area - only 4 core functions plus utilities.

### Layer 2: API Registry

```typescript
// api-registry.ts
const apiProviderRegistry = new Map<string, RegisteredApiProvider>();

export function registerApiProvider(provider: ApiProvider): void
export function getApiProvider(api: Api): ApiProviderInternal | undefined
```

**Design Decision:** Central registry enables dynamic provider loading without code changes.

### Layer 3: Provider Implementations

Each provider implements the `ApiProvider` interface:

```typescript
interface ApiProvider {
  api: string;
  stream: (model, context, options) => AssistantMessageEventStream;
  streamSimple: (model, context, options) => AssistantMessageEventStream;
}
```

**Design Decision:** Uniform interface across all providers enables interchangeability.

### Layer 4: SDK Integration

Providers use official SDKs (OpenAI, Anthropic, etc.) for HTTP/client logic.

**Design Decision:** Leverage maintained SDKs instead of rolling our own HTTP clients.

## Key Architectural Patterns

### 1. Registry Pattern

**Problem:** How to support 25+ providers without massive switch statements?

**Solution:** Central registry with dynamic registration:

```typescript
// Registration happens in register-builtins.ts
registerApiProvider(openaiCompletionsProvider);
registerApiProvider(anthropicMessagesProvider);
registerApiProvider(googleGenerativeAiProvider);

// Later, lookup by API type
const provider = getApiProvider('openai-completions');
```

**Benefits:**
- No code changes to add providers
- Multiple providers can register same API (competition)
- Easy to unregister/replace providers

### 2. Event Stream Pattern

**Problem:** How to provide rich streaming updates without blocking?

**Solution:** Async iterable event stream:

```typescript
class AssistantMessageEventStream implements AsyncIterable<Event> {
  async *[Symbol.asyncIterator]() {
    while (true) {
      // Yield events as they arrive
      yield await this.nextEvent();
    }
  }
}
```

**Benefits:**
- Natural async/await syntax
- Backpressure handling built-in
- Can be piped to other streams
- Easy to test with mock events

### 3. TypeBox Schema Pattern

**Problem:** How to provide type-safe tool definitions that work at runtime?

**Solution:** TypeBox schemas with AJV validation:

```typescript
const schema = Type.Object({
  email: Type.String({ format: 'email' })
});

// Compile-time type
type EmailData = Static<typeof schema>; // { email: string }

// Runtime validation
const valid = Validate(schema, { email: 'test@example.com' });
```

**Benefits:**
- Single source of truth (schema)
- Types inferred automatically
- Validation errors are descriptive
- Schemas are JSON-serializable

### 4. Context Serialization Pattern

**Problem:** How to transfer conversations between models/providers?

**Solution:** Plain JSON message format:

```typescript
interface Message {
  role: 'user' | 'assistant' | 'toolResult';
  content: Array<TextContent | ImageContent | ToolCall>;
}

// Serialize
const json = JSON.stringify(context);

// Deserialize and continue with different model
const restored = JSON.parse(json) as Context;
```

**Benefits:**
- No provider-specific serialization logic
- Works across all models automatically
- Easy to store in databases
- Enables A/B testing and fallbacks

## Component Interactions

### Request Flow

```
1. Application calls stream(model, context, options)
   ↓
2. stream() looks up provider via getApiProvider(model.api)
   ↓
3. Provider.stream() transforms context to provider-specific format
   ↓
4. Provider makes SDK call with streaming enabled
   ↓
5. SDK returns raw chunks (provider-specific format)
   ↓
6. Provider transforms chunks to unified events
   ↓
7. Events pushed to AssistantMessageEventStream
   ↓
8. Application consumes events via for-await loop
```

### Tool Call Flow

```
1. User message includes available tools
   ↓
2. Model responds with toolCall content block
   ↓
3. Stream emits toolcall_start, toolcall_delta, toolcall_end events
   ↓
4. Application executes tool with parsed arguments
   ↓
5. Application adds toolResult message to context
   ↓
6. Application calls complete() again with updated context
   ↓
7. Model receives tool result and continues conversation
```

## Extensibility Points

### Adding a New Provider

1. Create provider file (e.g., `new-provider.ts`)
2. Implement `stream()` and `streamSimple()` functions
3. Register via `registerApiProvider()`
4. Add models to `models.generated.ts`

**No changes to core code required.**

### Adding a New Event Type

1. Add to `AssistantMessageEvent` union type
2. Emit from provider stream implementation
3. Update consumers to handle new event

**Backward compatible - existing consumers ignore unknown events.**

### Custom Model Registration

```typescript
// Add custom model at runtime
modelRegistry.get('openai')?.set('custom-model', {
  id: 'custom-model',
  provider: 'openai',
  api: 'openai-completions',
  cost: { input: 100, output: 200, cacheRead: 50, cacheWrite: 100 },
  contextWindow: 128000,
  supports: { tools: true, images: true, reasoning: false }
});

// Use it immediately
const model = getModel('openai', 'custom-model');
```

## Performance Considerations

### Memory Efficiency

- **Streaming**: Events emitted as they arrive, no buffering
- **Lazy Evaluation**: Models loaded on-demand from registry
- **Minimal State**: Event stream maintains only current message being built

### CPU Efficiency

- **TypeBox Validation**: AJV uses compiled JavaScript for fast validation
- **Progressive JSON Parsing**: Parse incrementally during streaming
- **Message Transformation**: Single-pass conversion from provider format

### Network Efficiency

- **Native Streaming**: All providers use native HTTP streaming
- **Abort Support**: Cancel requests instantly with AbortSignal
- **Retry Logic**: Automatic retry on transient errors

## Security Considerations

### API Key Management

```typescript
// Never hardcode keys - use environment variables
const apiKey = getEnvApiKey('openai') || options?.apiKey;

// Supports multiple sources:
// 1. options.apiKey (explicit)
// 2. process.env.OPENAI_API_KEY (environment)
// 3. OAuth tokens (for providers like GitHub Copilot)
```

### Input Validation

- All tool arguments validated against TypeBox schemas
- Malicious inputs rejected before reaching model
- Sanitization of Unicode surrogates for cross-platform safety

### Error Handling

- Provider errors wrapped in unified error events
- No sensitive data leaked in error messages
- Graceful degradation on provider failures
