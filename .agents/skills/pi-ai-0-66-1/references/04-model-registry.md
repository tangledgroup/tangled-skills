# Model Registry System

This document covers the model registry implementation in Pi AI, including type-safe model access, cost calculation, and automatic model discovery.

## Architecture Overview

The model registry provides a centralized, type-safe way to access LLM models across all providers:

```typescript
// Model definitions (auto-generated)
const MODELS = {
  openai: { 'gpt-4o-mini': ModelDef, ... },
  anthropic: { 'claude-3-5-sonnet': ModelDef, ... },
  // ... more providers
};

// Registry initialization
const modelRegistry: Map<string, Map<string, Model<Api>>> = new Map();

for (const [provider, models] of Object.entries(MODELS)) {
  const providerModels = new Map();
  for (const [id, model] of Object.entries(models)) {
    providerModels.set(id, model);
  }
  modelRegistry.set(provider, providerModels);
}
```

## Type-Safe Model Access

### Generic Model Retrieval

The `getModel()` function provides full type inference:

```typescript
export function getModel<TProvider extends KnownProvider, TModelId extends keyof (typeof MODELS)[TProvider]>(
  provider: TProvider,
  modelId: TModelId
): Model<ModelApi<TProvider, TModelId>> {
  const providerModels = modelRegistry.get(provider);
  return providerModels?.get(modelId) as Model<ModelApi<TProvider, TModelId>>;
}

// Usage with full type inference:
const model = getModel('openai', 'gpt-4o-mini');
// TypeScript knows this is: Model<"openai-completions">

const anthropicModel = getModel('anthropic', 'claude-3-5-sonnet');
// TypeScript knows this is: Model<"anthropic-messages">
```

### Type Extraction Helper

The `ModelApi` type extracts the API type from model definitions:

```typescript
type ModelApi<
  TProvider extends KnownProvider,
  TModelId extends keyof (typeof MODELS)[TProvider]
> = (typeof MODELS)[TProvider][TModelId] extends { api: infer TApi } 
  ? (TApi extends Api ? TApi : never) 
  : never;

// Example:
type GPT4oApi = ModelApi<'openai', 'gpt-4o-mini'>;
// Resolves to: "openai-completions"
```

## Model Definition Structure

Each model definition includes comprehensive metadata:

```typescript
interface Model<TApi extends Api> {
  id: string;                    // Model identifier (e.g., 'gpt-4o-mini')
  name: string;                  // Human-readable name (e.g., 'GPT-4o Mini')
  api: TApi;                     // API type (e.g., 'openai-completions')
  provider: Provider;            // Provider name (e.g., 'openai')
  baseUrl: string;               // API endpoint URL
  reasoning: boolean;            // Supports reasoning/thinking
  input: ('text' | 'image')[];   // Input modalities supported
  cost: {
    input: number;               // $ per 1M input tokens
    output: number;              // $ per 1M output tokens
    cacheRead: number;           // $ per 1M cached reads
    cacheWrite: number;          // $ per 1M cached writes
  };
  contextWindow: number;         // Maximum context size in tokens
  maxTokens: number;             // Maximum output tokens
  headers?: Record<string, string>;  // Custom headers for API requests
  compat?: OpenAICompletionsCompat;  // Compatibility overrides
}
```

### Example Model Definition

```typescript
const gpt4oMini: Model<'openai-completions'> = {
  id: 'gpt-4o-mini',
  name: 'GPT-4o Mini',
  api: 'openai-completions',
  provider: 'openai',
  baseUrl: 'https://api.openai.com/v1',
  reasoning: true,
  input: ['text', 'image'],
  cost: {
    input: 150,      // $0.15 per 1M tokens
    output: 600,     // $0.60 per 1M tokens
    cacheRead: 75,   // $0.075 per 1M cached reads
    cacheWrite: 300  // $0.30 per 1M cached writes
  },
  contextWindow: 128000,
  maxTokens: 16384
};
```

## Provider Discovery

### List All Providers

```typescript
export function getProviders(): KnownProvider[] {
  return Array.from(modelRegistry.keys()) as KnownProvider[];
}

// Usage:
const providers = getProviders();
// ['openai', 'anthropic', 'google', 'groq', 'mistral', ...]
```

### List Models for Provider

```typescript
export function getModels<TProvider extends KnownProvider>(
  provider: TProvider
): Model<ModelApi<TProvider, keyof (typeof MODELS)[TProvider]>>[] {
  const models = modelRegistry.get(provider);
  return models ? Array.from(models.values()) : [];
}

// Usage:
const openaiModels = getModels('openai');
// [gpt-4o, gpt-4o-mini, o3-mini, ...]

const anthropicModels = getModels('anthropic');
// [claude-3-5-sonnet, claude-3-5-haiku, claude-3-opus, ...]
```

## Cost Calculation

### Automatic Cost Tracking

Costs are automatically calculated from token usage:

```typescript
export function calculateCost<TApi extends Api>(
  model: Model<TApi>,
  usage: Usage
): Usage['cost'] {
  usage.cost.input = (model.cost.input / 1000000) * usage.input;
  usage.cost.output = (model.cost.output / 1000000) * usage.output;
  usage.cost.cacheRead = (model.cost.cacheRead / 1000000) * usage.cacheRead;
  usage.cost.cacheWrite = (model.cost.cacheWrite / 1000000) * usage.cacheWrite;
  usage.cost.total = 
    usage.cost.input + 
    usage.cost.output + 
    usage.cost.cacheRead + 
    usage.cost.cacheWrite;
    
  return usage.cost;
}

// Usage:
const model = getModel('openai', 'gpt-4o-mini');
const usage = {
  input: 1000,
  output: 500,
  cacheRead: 0,
  cacheWrite: 0,
  totalTokens: 1500,
  cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 }
};

const cost = calculateCost(model, usage);
// {
//   input: 0.00015,    // $0.00015 for 1000 input tokens
//   output: 0.0003,    // $0.0003 for 500 output tokens
//   cacheRead: 0,
//   cacheWrite: 0,
//   total: 0.00045     // Total: $0.00045
// }
```

### Cost Comparison Example

```typescript
function compareModelCosts(modelIds: Array<[string, string]>, usage: Usage) {
  const comparisons = modelIds.map(([provider, modelId]) => {
    const model = getModel(provider, modelId);
    const cost = calculateCost(model, { ...usage, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 } });
    
    return {
      provider,
      model: model.name,
      cost: cost.total,
      savings: null // Will be calculated below
    };
  });
  
  // Find cheapest option
  const cheapest = comparisons.reduce((min, c) => c.cost < min.cost ? c : min);
  
  // Calculate savings vs cheapest
  comparisons.forEach(c => {
    c.savings = c.cost - cheapest.cost;
  });
  
  return comparisons.sort((a, b) => a.cost - b.cost);
}

// Usage:
const usage = { input: 10000, output: 5000, cacheRead: 0, cacheWrite: 0, totalTokens: 15000, cost: {} as any };
const rankings = compareModelCosts([
  ['openai', 'gpt-4o'],
  ['openai', 'gpt-4o-mini'],
  ['anthropic', 'claude-3-5-sonnet'],
  ['anthropic', 'claude-3-5-haiku']
], usage);

console.table(rankings.map(r => ({
  Model: r.model,
  Cost: `$${r.cost.toFixed4}`,
  Extra: `$${r.savings.toFixed(4)}`
})));
```

## Model Capabilities

### Reasoning Support

Check if a model supports reasoning/thinking:

```typescript
const model = getModel('openai', 'o3-mini');
console.log(model.reasoning); // true

const nonReasoningModel = getModel('openai', 'gpt-4o-mini');
console.log(nonReasoningModel.reasoning); // false (but supports reasoning_effort)
```

### XHigh Thinking Support

Some models support extended thinking levels:

```typescript
export function supportsXhigh<TApi extends Api>(model: Model<TApi>): boolean {
  if (model.id.includes('gpt-5.2') || 
      model.id.includes('gpt-5.3') || 
      model.id.includes('gpt-5.4')) {
    return true;
  }
  
  if (model.id.includes('opus-4-6') || 
      model.id.includes('opus-4.6')) {
    return true;
  }
  
  return false;
}

// Usage:
const opus46 = getModel('anthropic', 'claude-opus-4-6');
if (supportsXhigh(opus46)) {
  streamSimple(opus46, context, { reasoning: 'xhigh' });
} else {
  streamSimple(opus46, context, { reasoning: 'high' }); // Fallback
}
```

### Input Modalities

Check what input types a model supports:

```typescript
const model = getModel('openai', 'gpt-4o');
console.log(model.input); // ['text', 'image']

const textOnlyModel = getModel('anthropic', 'claude-3-5-haiku');
console.log(textOnlyModel.input); // ['text']

// Validate before sending images:
if (!model.input.includes('image')) {
  throw new Error(`${model.name} does not support image input`);
}
```

## Model Comparison Utilities

### Check Model Equality

Compare models by ID and provider:

```typescript
export function modelsAreEqual<TApi extends Api>(
  a: Model<TApi> | null | undefined,
  b: Model<TApi> | null | undefined
): boolean {
  if (!a || !b) return false;
  return a.id === b.id && a.provider === b.provider;
}

// Usage:
const model1 = getModel('openai', 'gpt-4o');
const model2 = getModel('openai', 'gpt-4o');
const model3 = getModel('anthropic', 'claude-3-5-sonnet');

console.log(modelsAreEqual(model1, model2)); // true
console.log(modelsAreEqual(model1, model3)); // false
```

### Filter Models by Capability

```typescript
function getModelsByCapability(
  capability: 'reasoning' | 'images' | 'tools',
  minContextWindow?: number
): Model<Api>[] {
  const allModels = getProviders()
    .flatMap(provider => getModels(provider))
    .map(m => m as Model<Api>);
  
  return allModels.filter(model => {
    if (capability === 'reasoning' && !model.reasoning) {
      return false;
    }
    if (capability === 'images' && !model.input.includes('image')) {
      return false;
    }
    if (minContextWindow && model.contextWindow < minContextWindow) {
      return false;
    }
    return true;
  });
}

// Usage:
const imageModels = getModelsByCapability('images');
const reasoningModels = getModelsByCapability('reasoning', 100000);
```

## Custom Model Registration

### Add Custom Models

You can add custom models at runtime:

```typescript
import { getModel, getModels } from '@mariozechner/pi-ai';

// Create a custom model definition
const customModel: Model<'openai-completions'> = {
  id: 'custom-gpt-4',
  name: 'Custom GPT-4',
  api: 'openai-completions',
  provider: 'custom-provider',
  baseUrl: 'https://custom-api.example.com/v1',
  reasoning: true,
  input: ['text', 'image'],
  cost: {
    input: 200,
    output: 800,
    cacheRead: 0,
    cacheWrite: 0
  },
  contextWindow: 128000,
  maxTokens: 4096
};

// Note: Custom models need to be added via settings.json or custom registry
// The built-in getModel() only returns pre-registered models
```

### Model Registry Extensions

For advanced use cases, you can extend the registry:

```typescript
// Create a custom registry wrapper
class ExtendedModelRegistry {
  private customModels = new Map<string, Map<string, Model<Api>>>();
  
  addCustomModel(provider: string, model: Model<Api>) {
    if (!this.customModels.has(provider)) {
      this.customModels.set(provider, new Map());
    }
    this.customModels.get(provider)!.set(model.id, model);
  }
  
  getModel(provider: string, modelId: string): Model<Api> | undefined {
    // Check custom models first
    const customProvider = this.customModels.get(provider);
    if (customProvider?.has(modelId)) {
      return customProvider.get(modelId);
    }
    
    // Fall back to built-in registry
    try {
      return getModel(provider as KnownProvider, modelId as any);
    } catch {
      return undefined;
    }
  }
}
```

## Performance Considerations

### Registry Initialization

The model registry is initialized once at module load:

```typescript
// In models.ts (runs once on import)
const modelRegistry: Map<string, Map<string, Model<Api>>> = new Map();

for (const [provider, models] of Object.entries(MODELS)) {
  const providerModels = new Map<string, Model<Api>>();
  for (const [id, model] of Object.entries(models)) {
    providerModels.set(id, model as Model<Api>);
  }
  modelRegistry.set(provider, providerModels);
}

// O(1) lookup time for getModel()
```

### Memory Usage

Model definitions are lightweight (~50 bytes each):

```typescript
// ~25 providers × ~20 models each × ~50 bytes = ~25KB in memory
const modelSize = JSON.stringify(getModel('openai', 'gpt-4o')).length;
console.log(modelSize); // ~300 bytes per model
```

## Best Practices

1. **Use Type-Safe Access**: Always use `getModel()` for type inference
2. **Check Capabilities**: Verify model supports required features before use
3. **Track Costs**: Use `calculateCost()` for billing and optimization
4. **Handle Missing Models**: Check if model exists before using
5. **Cache Model References**: Reuse model objects instead of re-fetching

```typescript
// ✓ Good: Cache model reference
const model = getModel('openai', 'gpt-4o-mini');
const response1 = await complete(model, context1);
const response2 = await complete(model, context2);

// ✗ Bad: Re-fetch model each time
const response1 = await complete(getModel('openai', 'gpt-4o-mini'), context1);
const response2 = await complete(getModel('openai', 'gpt-4o-mini'), context2);
```

## Troubleshooting

### Model Not Found

```typescript
// Check if provider exists
const providers = getProviders();
console.log(providers.includes('openai')); // true

// Check if model exists for provider
const models = getModels('openai');
console.log(models.some(m => m.id === 'gpt-4o-mini')); // true

// Try getting the model
const model = getModel('openai', 'gpt-4o-mini');
if (!model) {
  console.error('Model not found!');
}
```

### Type Errors

If TypeScript complains about model types:

```typescript
// ✗ Wrong: Mixing providers
const model1 = getModel('openai', 'gpt-4o-mini');
const model2 = getModel('anthropic', 'claude-3-5-sonnet');
// model1 and model2 have different API types

// ✓ Correct: Use type assertions or generics
function processModel<TApi extends Api>(model: Model<TApi>) {
  // Handle any model type
}

processModel(model1);
processModel(model2);
```
