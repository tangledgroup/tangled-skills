# Provider Architecture - Deep Dive

This reference document explains how pi-ai implements its unified multi-provider LLM API.

## The Provider Problem

Different LLM providers have different APIs:
- OpenAI uses a completions or responses API
- Anthropic uses a messages API
- Google uses a generative AI API
- Each has different request/response formats, authentication methods, and capabilities

Writing code that works with all of them would require either:
1. Maintaining separate code paths for each provider (duplication, hard to maintain)
2. Forcing all providers into one rigid format (loses provider-specific features)

Pi's solution is a **unified event stream** with **lazy-loaded adapters**.

## Core Abstraction: The Event Stream

Instead of returning a simple string or object, pi's API returns an async iterable of events:

```
stream(model, context, options) -> AsyncIterable<AssistantMessageEvent>
```

Each event represents something happening during generation:
- Text starting, arriving in chunks, ending
- Thinking/reasoning content streaming
- Tool calls being constructed
- Completion with stop reason
- Errors if something goes wrong

This design has several benefits:

**Streaming**: UIs can display text as it arrives rather than waiting for the full response.

**Progressive parsing**: Tool call arguments are parsed incrementally as JSON arrives, allowing UIs to show partial information (e.g., "writing to file X" before the full content is known).

**Unified interface**: All providers emit the same event types, so consumer code doesn't need provider-specific logic.

**Error handling**: Errors become events in the stream, allowing graceful degradation and partial result recovery.

## Provider Registration System

Providers are registered in a central registry that maps API types to stream functions:

```
Registry: ApiType -> StreamFunction
```

When you call `stream(model, context, options)`:
1. Look up the model's API type (e.g., "anthropic-messages")
2. Get the registered stream function for that API
3. Call it with your model, context, and options
4. Return the event stream to the caller

The registry supports multiple implementations of the same API type, allowing custom providers or forks.

## Lazy Loading Pattern

Providers are loaded on-demand using dynamic imports:

```typescript
function loadAnthropicProvider(): Promise<ProviderModule> {
    if (!cachedPromise) {
        cachedPromise = import("./anthropic.js");
    }
    return cachedPromise;
}

function createLazyStream(loadFunction): StreamFunction {
    return (model, context, options) => {
        const stream = new EventStream();
        
        loadFunction()
            .then(module => {
                const innerStream = module.stream(model, context, options);
                forwardEvents(innerStream, stream);
            })
            .catch(error => {
                stream.push({ type: "error", error });
                stream.end();
            });
        
        return stream; // Return immediately, loading happens async
    };
}
```

**Why lazy load?**

1. **Tree-shaking**: Unused providers aren't included in the bundle
2. **Browser compatibility**: Node.js-only providers (like Bedrock) can be excluded in browser builds
3. **Startup time**: Providers load only when first used, not at application startup
4. **Error isolation**: If a provider fails to load, it doesn't crash the entire application

## Provider-Specific Options

Different providers support different features:
- Anthropic supports thinking with token budgets
- OpenAI supports reasoning effort levels
- Google supports thinking enabled/disabled with budget tokens

Pi uses TypeScript generics to enforce type safety:

```typescript
interface Model<TApi extends Api> {
    api: TApi;
    // ... other properties
}

type StreamFunction<TApi, TOptions> = (
    model: Model<TApi>,
    context: Context,
    options?: TOptions
) => AsyncIterable<AssistantMessageEvent>;
```

When you get a model, TypeScript knows its API type:
```typescript
const claude = getModel("anthropic", "claude-sonnet-4");
// Type: Model<"anthropic-messages">

await stream(claude, context, { thinkingEnabled: true }); // ✓ Valid
await stream(claude, context, { reasoningEffort: "high" }); // ✗ Type error
```

This prevents passing invalid options to providers that don't support them.

## Simple vs Provider-Specific Options

Pi offers two interfaces for calling models:

**Simple Interface**: Unified options that work across all providers
```typescript
await completeSimple(model, context, {
    reasoning: "medium" // Maps to provider-specific settings
});
```

The simple interface normalizes common features:
- `reasoning`: "off" | "minimal" | "low" | "medium" | "high" | "xhigh"
- Maps to each provider's equivalent setting

**Provider-Specific Interface**: Full control over provider features
```typescript
await complete(claude, context, {
    thinkingEnabled: true,
    thinkingBudgetTokens: 8192
});
```

Use simple when you want portability, provider-specific when you need fine-grained control.

## Message Transformation

When messages from one provider are sent to another (cross-provider handoff), pi transforms them for compatibility:

**Same provider**: Messages pass through unchanged.

**Different provider**: 
- Text content passes through unchanged
- Tool calls and results pass through unchanged  
- Thinking blocks become tagged text: `<thinking>...</thinking>`

This allows workflows like:
1. Start conversation with Claude (with thinking enabled)
2. Switch to GPT-5 for a complex question
3. GPT-5 sees Claude's thinking as regular text with tags
4. Continue with Gemini, which also sees the tagged thinking

The transformation happens automatically in the message conversion layer before sending to the provider.

## Model Metadata

Each model has metadata describing its capabilities:

**Basic properties**:
- ID and display name
- API type and provider name
- Base URL (for custom endpoints)

**Capabilities**:
- `reasoning`: Does it support thinking/reasoning?
- `input`: Supported input types ("text", "image")
- `contextWindow`: Maximum token context size
- `maxTokens`: Maximum output tokens

**Pricing**:
- Cost per 1M tokens for input, output, cache reads, cache writes
- Used to track conversation costs

**Compatibility flags**:
- For OpenAI-compatible providers, flags indicate which features are supported
- Some servers don't support certain fields or use different field names
- Flags allow pi to adapt requests for each server's capabilities

Models can be discovered automatically (from provider APIs) or defined manually (for local servers like Ollama).

## Error Handling

Provider errors are converted to standardized error events:

**Network errors**: Connection failures, timeouts become error events with the partial content received so far.

**API errors**: Rate limits, authentication failures, context overflow become error events with the provider's error message.

**Abort**: User-initiated cancellation becomes an error event with reason "aborted" and partial content.

The final message includes:
- `stopReason`: Why generation stopped ("stop", "length", "toolUse", "error", "aborted")
- `errorMessage`: Error details if applicable
- `content`: Any partial content received before the error
- `usage`: Token counts for what was actually consumed

This allows callers to:
- Display partial responses even when errors occur
- Track costs for failed requests
- Decide whether to retry based on error type
- Continue conversations after aborts by adding partial messages to context

## Cross-Provider Handoffs

Pi supports switching providers mid-conversation seamlessly:

**Context serialization**: The context object (messages, tools, system prompt) is plain JSON, easily serializable.

**Message transformation**: When sending to a different provider, messages are transformed for compatibility (thinking becomes tagged text).

**Tool continuity**: Tool calls and results work across all providers since they use a standardized format.

**State preservation**: Token usage, costs, and timestamps are preserved when switching providers.

This enables workflows like:
- Start with a fast/cheap model for initial responses
- Switch to a more capable model for complex reasoning
- Use specialized models for specific tasks (vision, code, etc.)
- Maintain conversation continuity across provider outages

## Testing with Faux Provider

Pi includes a faux (fake) provider for testing:

**Deterministic responses**: Queue up predefined responses that are returned in order.

**No API calls**: Tests run without hitting real APIs or consuming tokens.

**Full event streaming**: Emits the same event types as real providers, including progressive tool call parsing.

**Usage tracking**: Simulates token counting and costs for testing billing logic.

**Multi-model support**: Can register multiple faux models with different capabilities for testing model switching.

Tests use the faux provider to verify:
- Event sequences are correct
- Tool execution works properly
- Error handling behaves as expected
- Cross-provider handoffs transform messages correctly

## Custom Providers

To add a new provider:

1. **Implement stream function**: Call the provider's API and emit standardized events
2. **Convert messages**: Transform pi's message format to the provider's format and back
3. **Handle errors**: Convert provider errors to pi's error event format
4. **Register provider**: Add to the API registry with lazy loading
5. **Add models**: Define model metadata or fetch from provider's API
6. **Add authentication**: Implement API key lookup or OAuth flow
7. **Write tests**: Verify streaming, tool use, errors, and edge cases

The provider implementation is isolated - it doesn't affect other providers or the core system.

## Browser Compatibility

Some providers use Node.js-specific APIs (file system, environment variables, AWS SDK). Pi handles this through:

**Conditional loading**: Node.js-only providers are loaded via special import that fails gracefully in browsers.

**Explicit API keys**: In browsers, API keys must be passed explicitly (no environment variable lookup).

**OAuth exclusion**: OAuth login flows don't work in browsers; use server-side authentication instead.

**Feature detection**: Models from incompatible providers appear in lists but fail at runtime with clear error messages.

For production web apps, use a backend proxy that keeps API keys secure and handles provider communication.
