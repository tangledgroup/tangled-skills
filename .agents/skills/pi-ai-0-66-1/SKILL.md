---
name: pi-ai-0-66-1
description: A skill for understanding and implementing the Pi AI 0.66.1 unified LLM API architecture, covering its provider abstraction patterns, streaming event system, type-safe tool definitions with TypeBox, cross-provider context serialization, and multi-model handoff capabilities for building agentic workflows. Use when designing or implementing unified AI client libraries, analyzing provider abstraction patterns, building streaming LLM interfaces, or understanding how to create extensible multi-provider AI systems with automatic model discovery and cost tracking.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - ai-infrastructure
  - llm-abstraction
  - provider-patterns
  - streaming-api
  - typebox
  - agentic-workflows
  - event-streams
category: architecture
required_environment_variables: []
---

# Pi AI 0.66.1 Architecture and Implementation

Pi AI is a unified LLM API library that provides automatic model discovery, provider configuration, token/cost tracking, and context persistence with mid-session handoff capabilities. It supports 25+ providers (OpenAI, Anthropic, Google, Mistral, Groq, etc.) through a pluggable architecture with type-safe tool definitions using TypeBox schemas.

**Key architectural innovations:**
- **Provider abstraction layer**: Unified API across heterogeneous LLM providers
- **Event-driven streaming**: Rich event stream protocol for real-time updates
- **Type-safe tools**: TypeBox schemas for compile-time validation
- **Context serialization**: Portable conversation state for cross-model handoffs
- **Extensible registry**: Dynamic provider registration without code changes

## When to Use

- Designing unified AI client libraries for multiple providers
- Implementing streaming LLM interfaces with rich event types
- Building agentic workflows requiring tool calling and validation
- Creating extensible plugin architectures for AI providers
- Understanding event-driven stream patterns for LLM responses
- Analyzing type-safe API design for AI/ML systems
- Implementing cross-provider context transfer and model handoffs

## Core Architecture Overview

### Design Philosophy

Pi AI follows several key architectural principles:

1. **Provider Agnosticism**: Abstract away provider-specific quirks into a unified interface
2. **Type Safety First**: Use TypeBox for runtime and compile-time validation
3. **Event-Driven Streaming**: Rich event protocol instead of simple text streams
4. **Zero Code Generation**: Models defined in TypeScript, no CLI generation needed
5. **Composable Context**: Messages as plain JSON for serialization and transfer

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  stream(model, context, options) → EventStream          │
│  complete(model, context, options) → Promise<Message>   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 API Registry Layer                       │
│  registerApiProvider(api, { stream, streamSimple })     │
│  getApiProvider(api) → ProviderImplementation           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Provider Implementation Layer               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ OpenAI   │ │Anthropic │ │  Google  │ │ Mistral  │  │
│  │ Provider │ │ Provider │ │ Provider │ │ Provider │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                SDK/HTTP Client Layer                     │
│  OpenAI SDK, Anthropic SDK, Google Generative AI SDK    │
└─────────────────────────────────────────────────────────┘
```

See [Architecture Deep Dive](references/01-architecture-overview.md) for detailed component analysis.

## Quick Start

### Basic Usage

```typescript
import { Type, getModel, stream, Context, Tool } from '@mariozechner/pi-ai';

// Get a typed model (auto-complete for providers and models)
const model = getModel('openai', 'gpt-4o-mini');

// Define tools with TypeBox schemas
const tools: Tool[] = [{
  name: 'get_weather',
  description: 'Get current weather',
  parameters: Type.Object({
    location: Type.String({ description: 'City name' }),
    units: Type.Union([Type.Literal('celsius'), Type.Literal('fahrenheit')])
  })
}];

// Create conversation context
const context: Context = {
  systemPrompt: 'You are a helpful assistant.',
  messages: [{ role: 'user', content: 'What is the weather in London?' }],
  tools
};

// Stream with rich events
const s = stream(model, context);

for await (const event of s) {
  switch (event.type) {
    case 'text_delta':
      process.stdout.write(event.delta);
      break;
    case 'toolcall_end':
      console.log(`Tool: ${event.toolCall.name}`);
      break;
    case 'done':
      console.log(`Finished: ${event.reason}`);
      break;
  }
}

// Get final message and add to context
const finalMessage = await s.result();
context.messages.push(finalMessage);

console.log(`Tokens: ${finalMessage.usage.input} in, ${finalMessage.usage.output} out`);
console.log(`Cost: $${finalMessage.usage.cost.total.toFixed(4)}`);
```

### Simple API (Auto-Reasoning)

```typescript
import { streamSimple } from '@mariozechner/pi-ai';

// Automatically handles reasoning/thinking based on model capabilities
const s = streamSimple(model, context, {
  reasoning: 'high'  // minimal | low | medium | high | xhigh
});
```

See [Usage Patterns](references/02-usage-patterns.md) for comprehensive examples.

## Key Implementation Patterns

### 1. Provider Abstraction Pattern

Each provider implements a standard interface:

```typescript
interface ApiProvider<TApi extends Api = Api> {
  api: TApi;
  stream: StreamFunction<TApi>;
  streamSimple: StreamFunction<TApi, SimpleStreamOptions>;
}

// Example: OpenAI provider registration
registerApiProvider({
  api: 'openai-completions',
  stream: streamOpenAICompletions,
  streamSimple: (model, context, options) => {
    const reasoning = clampReasoning(options?.reasoning, model);
    return streamOpenAICompletions(model, context, { ...options, reasoningEffort: reasoning });
  }
});
```

**Why this works:**
- Decouples API protocol from provider business logic
- Enables multiple providers per API (e.g., OpenAI + Azure)
- Allows custom providers without modifying core code

### 2. Event Stream Pattern

Rich event types instead of simple text streams:

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
  | { type: 'toolcall_delta'; contentIndex: number; partial: AssistantMessage }
  | { type: 'toolcall_end'; contentIndex: number; toolCall: ToolCall; partial: AssistantMessage }
  | { type: 'done'; reason: StopReason; partial: AssistantMessage }
  | { type: 'error'; error: Error };
```

**Benefits:**
- Real-time UI updates for each content type
- Progressive JSON parsing for tool arguments
- Separate handling of reasoning/thinking content
- Full context at every event via `partial` message

### 3. TypeBox Schema Pattern

Tools defined with TypeBox for validation:

```typescript
const tool: Tool = {
  name: 'create_user',
  description: 'Create a new user',
  parameters: Type.Object({
    email: Type.String({ format: 'email' }),
    role: StringEnum(['admin', 'user', 'guest']),
    metadata: Type.Optional(Type.Record(Type.String()))
  })
};
```

**Why TypeBox:**
- Compile-time type inference via `Static<T>`
- Runtime validation with AJV
- Serializable to plain JSON (unlike Zod)
- Compatible with all TypeScript tooling

### 4. Context Serialization Pattern

Messages are plain JSON, enabling:
- Cross-model handoffs mid-conversation
- Persistence to databases
- Transfer between services
- Replay and debugging

```typescript
// Serialize context
const json = JSON.stringify(context);

// Later, restore and continue with different model
const restoredContext = JSON.parse(json) as Context;
const newModel = getModel('anthropic', 'claude-3-5-sonnet');
const continuation = await complete(newModel, restoredContext);
```

See [Provider Implementation](references/03-provider-patterns.md) for detailed patterns.

## Model Registry System

### Automatic Model Discovery

Models defined in generated TypeScript file:

```typescript
// models.generated.ts (auto-generated from provider specs)
export const MODELS = {
  openai: {
    'gpt-4o-mini': {
      id: 'gpt-4o-mini',
      provider: 'openai',
      api: 'openai-completions',
      cost: { input: 150, output: 600, cacheRead: 75, cacheWrite: 300 },
      contextWindow: 128000,
      supports: { tools: true, images: true, reasoning: true }
    }
  },
  anthropic: { /* ... */ }
};
```

### Type-Safe Model Access

```typescript
// Fully typed - TypeScript knows the API type
const model = getModel('openai', 'gpt-4o-mini');
// Model<"openai-completions"> with auto-complete

// List all providers
const providers = getProviders(); // KnownProvider[]

// List models for a provider
const models = getModels('anthropic'); // Model<AnthropicApi>[]
```

See [Model Management](references/04-model-registry.md) for registry implementation.

## Streaming Implementation Details

### Event Stream Protocol

```typescript
class AssistantMessageEventStream implements AsyncIterable<AssistantMessageEvent> {
  private queue: AssistantMessageEvent[] = [];
  private resolvers: Array<(event: AssistantMessageEvent) => void> = [];
  
  async *[Symbol.asyncIterator]() {
    while (true) {
      if (this.queue.length > 0) {
        yield this.queue.shift();
      } else {
        // Wait for next event
        await new Promise(r => this.resolvers.push(r));
      }
    }
  }
  
  push(event: AssistantMessageEvent) {
    if (this.resolvers.length > 0) {
      const resolve = this.resolvers.shift();
      resolve!(event);
    } else {
      this.queue.push(event);
    }
  }
  
  async result(): Promise<AssistantMessage> {
    // Wait for 'done' event and return final message
  }
}
```

### Progressive JSON Parsing

Tool arguments parsed incrementally during streaming:

```typescript
// During toolcall_delta events
const partialArgs = '{"location": "London", "units": "ce';
const parsed = parseStreamingJson(partialArgs); 
// → { location: 'London', units: undefined } (partial but valid)

// Allows UI to show partial data immediately
if (parsed.location) {
  showLocationInput(parsed.location);
}
```

See [Streaming Architecture](references/05-streaming-system.md) for complete implementation.

## Cross-Provider Handoffs

### Context Transfer Example

```typescript
// Start with OpenAI
let context: Context = {
  messages: [{ role: 'user', content: 'Analyze this code...' }],
  tools: [readFileTool, writeFileTool]
};

const model1 = getModel('openai', 'gpt-4o');
const response1 = await complete(model1, context);
context.messages.push(response1);

// Switch to Anthropic for complex reasoning
const model2 = getModel('anthropic', 'claude-3-5-sonnet');
const response2 = await complete(model2, context, { reasoning: 'high' });
context.messages.push(response2);

// Final summary with cheaper model
const model3 = getModel('openai', 'gpt-4o-mini');
const summary = await complete(model3, context);
```

**Why this matters:**
- Cost optimization (expensive models only when needed)
- Leverage different model strengths
- Fallback on provider outages
- A/B testing model performance

## Cost Tracking and Optimization

### Automatic Cost Calculation

```typescript
// Costs defined per model (per 1M tokens)
const model = {
  cost: { 
    input: 150,      // $0.15 per 1M input tokens
    output: 600,     // $0.60 per 1M output tokens
    cacheRead: 75,   // $0.075 per 1M cached reads
    cacheWrite: 300  // $0.30 per 1M cached writes
  }
};

// Automatically calculated from usage
const usage = {
  input: 1000,
  output: 500,
  cacheRead: 0,
  cacheWrite: 0
};

const cost = calculateCost(model, usage);
// → { input: 0.00015, output: 0.0003, total: 0.00045 }
```

See [Cost Optimization](references/06-cost-tracking.md) for strategies.

## Reference Files

- [`references/01-architecture-overview.md`](references/01-architecture-overview.md) - High-level architecture, design philosophy, component interactions
- [`references/02-usage-patterns.md`](references/02-usage-patterns.md) - Common usage patterns, tool definitions, context management
- [`references/03-provider-patterns.md`](references/03-provider-patterns.md) - Provider implementation patterns, message transformation, error handling
- [`references/04-model-registry.md`](references/04-model-registry.md) - Model registry system, type-safe model access, cost calculation
- [`references/05-streaming-system.md`](references/05-streaming-system.md) - Event stream protocol, progressive parsing, abort handling
- [`references/06-cost-tracking.md`](references/06-cost-tracking.md) - Cost tracking implementation, optimization strategies, cache retention

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/pi-ai-0-66-1/`). All paths are relative to this directory.

## Key Design Decisions

### Why TypeBox Over Zod?

1. **JSON Serializable**: TypeBox schemas are plain JSON; Zod schemas are functions
2. **No Runtime Dependency**: TypeBox types inferred at compile time
3. **AJV Integration**: Direct compatibility with industry-standard validator
4. **Smaller Bundle**: ~5KB vs ~40KB for Zod

### Why Event Streams Over Simple Iterables?

1. **Rich Semantics**: Each event type carries specific meaning
2. **Progressive Updates**: UI can update incrementally (e.g., show tool args as they parse)
3. **Debugging**: Event log provides complete audit trail
4. **Extensibility**: New event types don't break existing consumers

### Why No Code Generation?

1. **Type Safety**: TypeScript generics provide full type inference
2. **Developer Experience**: No build step, instant feedback
3. **Flexibility**: Custom models added at runtime
4. **Simplicity**: Single source of truth (models.generated.ts)

### Why Separate stream() and streamSimple()?

1. **Progressive Enhancement**: Simple API for common cases, full API for advanced needs
2. **Model Capabilities**: Automatically adapt reasoning based on model support
3. **Backward Compatibility**: Existing code works without changes
4. **Clarity**: Explicit vs implicit reasoning configuration

## Troubleshooting

### Common Issues

**Provider not found:**
```typescript
// Check registered providers
const providers = getProviders();
console.log(providers.includes('openai')); // true

// Verify model exists
const model = getModel('openai', 'gpt-4o-mini');
console.log(model?.id); // 'gpt-4o-mini'
```

**Tool validation errors:**
```typescript
// Ensure TypeBox schemas are valid
const schema = Type.Object({
  required: Type.String()  // ✓ Correct
});

// Not this:
const invalid = Type.Object({
  required: String  // ✗ Wrong - must use Type.String()
});
```

**Streaming not working:**
```typescript
// Ensure you're awaiting the stream
const s = stream(model, context);
for await (const event of s) {
  // Handle events
}

// Not this:
const s = stream(model, context);
s.forEach(event => {})  // ✗ Wrong - it's an async iterator
```

## Additional Resources

- **GitHub Repository:** https://github.com/badlogic/pi-mono/tree/v0.66.1/packages/ai
- **TypeBox Documentation:** https://github.com/sinclairzx81/typebox
- **AJV Validator:** https://ajv.js.org/
- **Changelog:** See `CHANGELOG.md` in package for version history

## Implementation Insights

The Pi AI library demonstrates several advanced patterns for building unified AI client libraries:

1. **Registry Pattern**: Dynamic provider registration enables hot-swapping and custom providers
2. **Event Sourcing**: Event stream provides audit trail and replay capability
3. **Adapter Pattern**: Each provider adapts its SDK to common interface
4. **Strategy Pattern**: Different streaming strategies (simple vs full) for different use cases
5. **Factory Pattern**: `getModel()` factory provides type-safe model instantiation

These patterns make the codebase highly extensible while maintaining type safety and developer experience.
