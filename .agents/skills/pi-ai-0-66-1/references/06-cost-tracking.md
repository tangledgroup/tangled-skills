# Cost Tracking and Optimization

This document covers cost tracking implementation, optimization strategies, and cache retention management in Pi AI.

## Cost Model Structure

### Per-Model Cost Definition

Each model defines costs per 1 million tokens:

```typescript
interface ModelCosts {
  input: number;    // $ per 1M input tokens
  output: number;   // $ per 1M output tokens
  cacheRead: number; // $ per 1M cached reads (typically 10-25% of input)
  cacheWrite: number; // $ per 1M cached writes (typically 100-200% of input)
}

// Example: GPT-4o Mini
const gpt4oMiniCosts: ModelCosts = {
  input: 150,      // $0.15 per 1M tokens
  output: 600,     // $0.60 per 1M tokens
  cacheRead: 75,   // $0.075 per 1M cached reads (50% discount)
  cacheWrite: 300  // $0.30 per 1M cached writes (2x input cost)
};

// Example: Claude 3.5 Sonnet
const claude35SonnetCosts: ModelCosts = {
  input: 3000,     // $3.00 per 1M tokens
  output: 15000,   // $15.00 per 1M tokens
  cacheRead: 300,  // $0.30 per 1M cached reads (10% of input)
  cacheWrite: 3750 // $3.75 per 1M cached writes (125% of input)
};
```

### Cost Calculation Implementation

```typescript
// In models.ts
export function calculateCost<TApi extends Api>(
  model: Model<TApi>,
  usage: Usage
): Usage['cost'] {
  // Convert per-1M-token rates to actual costs
  usage.cost.input = (model.cost.input / 1000000) * usage.input;
  usage.cost.output = (model.cost.output / 1000000) * usage.output;
  usage.cost.cacheRead = (model.cost.cacheRead / 1000000) * usage.cacheRead;
  usage.cost.cacheWrite = (model.cost.cacheWrite / 1000000) * usage.cacheWrite;
  
  // Total cost across all categories
  usage.cost.total = 
    usage.cost.input + 
    usage.cost.output + 
    usage.cost.cacheRead + 
    usage.cost.cacheWrite;
    
  return usage.cost;
}

// Usage example:
const model = getModel('openai', 'gpt-4o-mini');
const usage = {
  input: 10000,      // 10K input tokens
  output: 5000,      // 5K output tokens
  cacheRead: 0,
  cacheWrite: 0,
  totalTokens: 15000,
  cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 }
};

const cost = calculateCost(model, usage);
// {
//   input: 0.0015,      // $0.0015 for 10K input tokens
//   output: 0.003,      // $0.003 for 5K output tokens
//   cacheRead: 0,
//   cacheWrite: 0,
//   total: 0.0045       // Total: $0.0045
// }
```

## Cost Comparison Strategies

### Model Selection by Cost

```typescript
function findCheapestModel(
  models: Model<Api>[],
  estimatedInputTokens: number,
  estimatedOutputTokens: number
): { model: Model<Api>; estimatedCost: number } {
  let cheapest: { model: Model<Api>; cost: number } | null = null;
  
  for (const model of models) {
    const usage = {
      input: estimatedInputTokens,
      output: estimatedOutputTokens,
      cacheRead: 0,
      cacheWrite: 0,
      totalTokens: estimatedInputTokens + estimatedOutputTokens,
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 }
    };
    
    const cost = calculateCost(model, usage);
    
    if (!cheapest || cost.total < cheapest.cost) {
      cheapest = { model, cost: cost.total };
    }
  }
  
  if (!cheapest) {
    throw new Error('No models available');
  }
  
  return { model: cheapest.model, estimatedCost: cheapest.cost };
}

// Usage:
const allModels = getProviders()
  .flatMap(provider => getModels(provider))
  .map(m => m as Model<Api>);

const result = findCheapestModel(allModels, 10000, 5000);
console.log(`Cheapest: ${result.model.name} at $${result.estimatedCost.toFixed(4)}`);
```

### Cost-Benefit Analysis

```typescript
function compareModelValue(
  models: [Model<Api>, Model<Api>],
  usage: Usage
): {
  cheaper: Model<Api>;
  moreExpensive: Model<Api>;
  savings: number;
  percentageDifference: number;
} {
  const cost1 = calculateCost(models[0], { ...usage, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 } });
  const cost2 = calculateCost(models[1], { ...usage, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 } });
  
  const cheaper = cost1.total < cost2.total ? models[0] : models[1];
  const moreExpensive = cost1.total < cost2.total ? models[1] : models[0];
  const cheaperCost = cost1.total < cost2.total ? cost1.total : cost2.total;
  const expensiveCost = cost1.total < cost2.total ? cost2.total : cost1.total;
  
  return {
    cheaper,
    moreExpensive,
    savings: expensiveCost - cheaperCost,
    percentageDifference: ((expensiveCost - cheaperCost) / expensiveCost) * 100
  };
}

// Usage:
const comparison = compareModelValue(
  [getModel('openai', 'gpt-4o'), getModel('openai', 'gpt-4o-mini')],
  { input: 10000, output: 5000, cacheRead: 0, cacheWrite: 0, totalTokens: 15000, cost: {} as any }
);

console.log(`Switching to ${comparison.cheaper.name} saves $${comparison.savings.toFixed(4)} (${comparison.percentageDifference.toFixed(1)}%)`);
```

## Cache Retention Strategies

### Cache Retention Levels

Pi AI supports three cache retention preferences:

```typescript
type CacheRetention = 'none' | 'short' | 'long';

interface StreamOptions {
  cacheRetention?: CacheRetention; // Default: 'short'
}
```

**Retention Levels:**
- `none`: Disable caching (no cache write costs, no cache read benefits)
- `short`: Short-term caching (default, ~1 hour TTL on Anthropic)
- `long`: Long-term caching (extended TTL where supported)

### Provider-Specific Cache Mapping

```typescript
// In anthropic.ts
function getCacheControl(
  baseUrl: string,
  cacheRetention?: CacheRetention
): { retention: CacheRetention; cacheControl?: { type: 'ephemeral'; ttl?: '1h' } } {
  const retention = resolveCacheRetention(cacheRetention);
  
  if (retention === 'none') {
    return { retention };
  }
  
  // Anthropic supports 1-hour TTL for cache echoes
  const ttl = retention === 'long' && baseUrl.includes('api.anthropic.com') 
    ? '1h' 
    : undefined;
    
  return {
    retention,
    cacheControl: { type: 'ephemeral', ...(ttl && { ttl }) }
  };
}

// Usage in API call:
const { retention, cacheControl } = getCacheControl(model.baseUrl, options?.cacheRetention);

if (cacheControl) {
  // Add cache control to system message
  messages.unshift({
    role: 'user',
    content: [{
      type: 'cache_control',
      cache_type: cacheControl.type,
      ...(cacheControl.ttl && { ttl: cacheControl.ttl })
    }]
  });
}
```

### Cache Cost Optimization

```typescript
function estimateCacheSavings(
  model: Model<Api>,
  contextTokens: number,
  newTokens: number,
  cacheHitRate: number = 0.7 // Assume 70% cache hit rate
): {
  withoutCache: number;
  withCache: number;
  savings: number;
  breakevenRequests: number;
} {
  // Cost without caching
  const withoutCache = calculateCost(model, {
    input: contextTokens + newTokens,
    output: 0,
    cacheRead: 0,
    cacheWrite: 0,
    totalTokens: 0,
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 }
  }).total;
  
  // Cost with caching (first request)
  const writeCost = calculateCost(model, {
    input: contextTokens,
    output: 0,
    cacheRead: 0,
    cacheWrite: contextTokens,
    totalTokens: 0,
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 }
  }).total;
  
  // Cost with caching (subsequent requests with cache hits)
  const readCost = calculateCost(model, {
    input: newTokens,
    output: 0,
    cacheRead: contextTokens,
    cacheWrite: 0,
    totalTokens: 0,
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 }
  }).total;
  
  // Expected cost with cache hits
  const withCache = writeCost + (readCost * cacheHitRate);
  
  // Breakeven point
  const savingsPerRequest = withoutCache - readCost;
  const breakevenRequests = savingsPerRequest > 0 
    ? Math.ceil(writeCost / savingsPerRequest)
    : Infinity;
  
  return {
    withoutCache,
    withCache,
    savings: withoutCache - withCache,
    breakevenRequests
  };
}

// Usage:
const analysis = estimateCacheSavings(
  getModel('anthropic', 'claude-3-5-sonnet'),
  50000,  // 50K context tokens
  1000    // 1K new tokens per request
);

console.log(`Without cache: $${analysis.withoutCache.toFixed(4)}/request`);
console.log(`With cache: $${analysis.withCache.toFixed(4)}/request (avg)`);
console.log(`Breakeven: ${analysis.breakevenRequests} requests`);
```

## Budget Management

### Cost Tracking Accumulator

```typescript
class CostTracker {
  private totalCost = 0;
  private totalInputTokens = 0;
  private totalOutputTokens = 0;
  private requests = 0;
  private modelCosts = new Map<string, number>();
  
  recordUsage(message: AssistantMessage): void {
    this.totalCost += message.usage.cost.total;
    this.totalInputTokens += message.usage.input;
    this.totalOutputTokens += message.usage.output;
    this.requests++;
    
    // Track per-model costs
    const modelKey = `${message.provider}:${message.model}`;
    const current = this.modelCosts.get(modelKey) || 0;
    this.modelCosts.set(modelKey, current + message.usage.cost.total);
  }
  
  getSummary(): {
    totalCost: number;
    totalTokens: number;
    averageCostPerRequest: number;
    costPer1kTokens: number;
    modelBreakdown: Record<string, number>;
  } {
    const totalTokens = this.totalInputTokens + this.totalOutputTokens;
    
    return {
      totalCost: this.totalCost,
      totalTokens,
      averageCostPerRequest: this.totalCost / this.requests,
      costPer1kTokens: (this.totalCost / totalTokens) * 1000,
      modelBreakdown: Object.fromEntries(this.modelCosts)
    };
  }
  
  estimateRemainingBudget(budget: number): number {
    const remaining = budget - this.totalCost;
    const avgCost = this.totalCost / this.requests;
    return Math.floor(remaining / avgCost);
  }
}

// Usage:
const tracker = new CostTracker();

for await (const event of stream) {
  if (event.type === 'done') {
    tracker.recordUsage(event.message);
    
    const summary = tracker.getSummary();
    console.log(`Total spent: $${summary.totalCost.toFixed(4)}`);
    console.log(`Average per request: $${summary.averageCostPerRequest.toFixed(4)}`);
  }
}

const remainingRequests = tracker.estimateRemainingBudget(10.00);
console.log(`~${remainingRequests} requests remaining in $10 budget`);
```

### Budget-Limited Streaming

```typescript
async function streamWithBudget(
  model: Model<Api>,
  context: Context,
  maxBudget: number,
  currentSpent: number = 0
): Promise<AssistantMessage> {
  if (currentSpent >= maxBudget) {
    throw new Error(`Budget exceeded: $${currentSpent.toFixed(4)} >= $${maxBudget.toFixed(4)}`);
  }
  
  const stream = stream(model, context);
  
  for await (const event of stream) {
    if (event.type === 'done') {
      const newTotal = currentSpent + event.message.usage.cost.total;
      
      if (newTotal > maxBudget) {
        // Partial response - budget exceeded during generation
        console.warn(`Warning: Response truncated due to budget limit`);
      }
      
      return event.message;
    }
  }
  
  throw new Error('Stream completed without done event');
}

// Usage with conversation loop:
let totalSpent = 0;
const budget = 5.00; // $5 budget

for (let i = 0; i < maxTurns; i++) {
  try {
    const response = await streamWithBudget(model, context, budget, totalSpent);
    totalSpent += response.usage.cost.total;
    
    console.log(`Turn ${i + 1}: $${response.usage.cost.total.toFixed(4)} (total: $${totalSpent.toFixed(4)})`);
    
    if (totalSpent >= budget) {
      console.log('Budget exhausted');
      break;
    }
    
    context.messages.push(response);
  } catch (error) {
    console.error('Budget exceeded:', error.message);
    break;
  }
}
```

## Cost Optimization Techniques

### Tiered Model Strategy

Use different models for different tasks:

```typescript
function selectModelForTask(
  taskType: 'reasoning' | 'creative' | 'factual' | 'summary',
  contextLength: number
): Model<Api> {
  const models = getProviders()
    .flatMap(provider => getModels(provider))
    .map(m => m as Model<Api>);
  
  let filtered = models;
  
  // Filter by capability
  if (taskType === 'reasoning') {
    filtered = filtered.filter(m => m.reasoning);
  }
  
  // Filter by context window
  filtered = filtered.filter(m => m.contextWindow >= contextLength);
  
  // Select based on task type
  switch (taskType) {
    case 'reasoning':
      // Use capable model with reasoning
      return findCheapestModel(filtered, contextLength, 4000).model;
      
    case 'creative':
      // Use balanced model
      const creativeModels = filtered.filter(m => 
        m.cost.output < 5000 && m.contextWindow >= 100000
      );
      return findCheapestModel(creativeModels, contextLength, 2000).model;
      
    case 'factual':
      // Use cheap model for simple queries
      const factualModels = filtered.filter(m => 
        m.cost.input < 200 && m.cost.output < 800
      );
      return findCheapestModel(factualModels, contextLength, 500).model;
      
    case 'summary':
      // Use cheapest model for summaries
      return findCheapestModel(filtered, contextLength, 1000).model;
  }
  
  // Fallback: cheapest available
  return findCheapestModel(filtered, contextLength, 2000).model;
}

// Usage in conversation:
async function intelligentConversation(context: Context) {
  // Complex reasoning with expensive model
  const reasoningModel = selectModelForTask('reasoning', context.messages.length * 100);
  const analysis = await complete(reasoningModel, context);
  context.messages.push(analysis);
  
  // Summary with cheap model
  const summaryModel = selectModelForTask('summary', context.messages.length * 100);
  const summary = await complete(summaryModel, {
    ...context,
    systemPrompt: 'Summarize the conversation so far'
  });
  
  return summary;
}
```

### Context Compression

Reduce context size to save costs:

```typescript
function compressContext(
  messages: Message[],
  maxTokens: number,
  summaryModel: Model<Api>
): Message[] {
  const compressed: Message[] = [];
  let currentTokens = 0;
  
  // Add system prompt
  if (messages[0]?.role === 'user' && messages[0].content.includes('system')) {
    compressed.push(messages[0]);
    currentTokens += estimateTokens(messages[0].content);
  }
  
  // Add recent messages
  for (const message of messages.slice().reverse()) {
    const messageTokens = estimateTokens(message.content);
    
    if (currentTokens + messageTokens > maxTokens) {
      break;
    }
    
    compressed.unshift(message);
    currentTokens += messageTokens;
  }
  
  // If we dropped messages, summarize them
  if (compressed.length < messages.length) {
    const dropped = messages.slice(0, messages.length - compressed.length);
    
    const summary = await complete(summaryModel, {
      systemPrompt: 'Summarize this conversation segment concisely',
      messages: dropped,
      tools: []
    });
    
    // Insert summary at beginning
    compressed.unshift({
      role: 'user',
      content: `Previous conversation summary:\n${summary.content.map(b => b.text).join('\n')}`,
      timestamp: Date.now()
    });
  }
  
  return compressed;
}
```

### Batch Processing

Combine multiple requests to amortize context costs:

```typescript
async function batchProcess(
  model: Model<Api>,
  tasks: Array<{ prompt: string; id: string }>,
  maxBatchSize: number = 10
): Promise<Array<{ id: string; response: string; cost: number }>> {
  const results: Array<{ id: string; response: string; cost: number }> = [];
  
  for (let i = 0; i < tasks.length; i += maxBatchSize) {
    const batch = tasks.slice(i, i + maxBatchSize);
    
    const batchPrompt = batch.map((t, idx) => 
      `${idx + 1}. ${t.prompt}\nID: ${t.id}`
    ).join('\n\n');
    
    const context: Context = {
      systemPrompt: 'Process each task and include its ID in the response',
      messages: [{ role: 'user', content: batchPrompt, timestamp: Date.now() }],
      tools: []
    };
    
    const response = await complete(model, context);
    const responseText = response.content.map(b => b.text).join('\n');
    
    // Parse batch responses
    const responseParts = responseText.split(/\n\s*\d+\./).filter(Boolean);
    
    for (let j = 0; j < batch.length; j++) {
      results.push({
        id: batch[j].id,
        response: responseParts[j]?.trim() || '',
        cost: response.usage.cost.total / batch.length // Split cost across tasks
      });
    }
  }
  
  return results;
}

// Cost comparison:
const tasks = Array(10).fill(null).map((_, i) => ({ prompt: `Task ${i + 1}`, id: `task-${i}` }));

// Individual requests (expensive - repeats context each time)
const individualCost = await Promise.all(
  tasks.map(t => complete(model, { messages: [{ role: 'user', content: t.prompt }] }))
).then(responses => responses.reduce((sum, r) => sum + r.usage.cost.total, 0));

// Batch request (cheaper - shares context)
const batchResults = await batchProcess(model, tasks);
const batchCost = batchResults.reduce((sum, r) => sum + r.cost, 0);

console.log(`Individual: $${individualCost.toFixed(4)}`);
console.log(`Batch: $${batchCost.toFixed(4)}`);
console.log(`Savings: ${((individualCost - batchCost) / individualCost * 100).toFixed(1)}%`);
```

## Monitoring and Alerting

### Cost Threshold Alerts

```typescript
class CostMonitor {
  private threshold: number;
  private currentCost = 0;
  private callbacks: Array<(cost: number, threshold: number) => void> = [];
  
  constructor(threshold: number) {
    this.threshold = threshold;
  }
  
  onThreshold(callback: (cost: number, threshold: number) => void): void {
    this.callbacks.push(callback);
  }
  
  record(message: AssistantMessage): void {
    this.currentCost += message.usage.cost.total;
    
    // Check thresholds (50%, 75%, 90%, 100%)
    for (const percentage of [50, 75, 90, 100]) {
      const threshold = (this.threshold * percentage) / 100;
      
      if (this.currentCost >= threshold && this.currentCost - message.usage.cost.total < threshold) {
        // Just crossed this threshold
        this.callbacks.forEach(cb => cb(this.currentCost, threshold));
      }
    }
  }
  
  getUsage(): {
    current: number;
    threshold: number;
    remaining: number;
    percentage: number;
  } {
    return {
      current: this.currentCost,
      threshold: this.threshold,
      remaining: this.threshold - this.currentCost,
      percentage: (this.currentCost / this.threshold) * 100
    };
  }
}

// Usage:
const monitor = new CostMonitor(10.00); // $10 monthly budget

monitor.onThreshold((cost, threshold) => {
  console.warn(`⚠️ Budget alert: $${cost.toFixed(2)} spent ($${threshold.toFixed(2)} threshold)`);
  
  if (cost >= threshold) {
    console.error('🚨 Budget exhausted!');
  }
});

// Record each API call
const response = await complete(model, context);
monitor.record(response);

console.log(`Budget usage: ${monitor.getUsage().percentage.toFixed(1)}%`);
```

## Best Practices

1. **Track Costs Per-Request**: Always calculate and log costs for each API call
2. **Set Budget Limits**: Implement hard limits to prevent unexpected charges
3. **Use Cache Retention**: Enable caching for repeated context (saves 50-90%)
4. **Select Models Strategically**: Use expensive models only when needed
5. **Compress Context**: Summarize old messages to reduce token counts
6. **Batch Requests**: Combine multiple tasks to share context costs
7. **Monitor Usage**: Set up alerts at 50%, 75%, 90%, 100% of budget
8. **Test with Faux Provider**: Validate logic without incurring costs

## Cost Comparison Table

Example costs for 10K input + 5K output tokens:

| Model | Input Cost | Output Cost | Total | Cache Read | Cache Write |
|-------|-----------|-------------|-------|------------|-------------|
| GPT-4o Mini | $0.0015 | $0.0030 | $0.0045 | $0.00075 | $0.0030 |
| GPT-4o | $0.0050 | $0.0150 | $0.0200 | $0.0025 | $0.0100 |
| Claude 3.5 Haiku | $0.0025 | $0.0125 | $0.0150 | $0.0025 | $0.0075 |
| Claude 3.5 Sonnet | $0.0300 | $0.1500 | $0.1800 | $0.0030 | $0.0375 |
| Gemini 1.5 Pro | $0.0025 | $0.0075 | $0.0100 | $0.0000 | $0.0000 |

*Note: Cache costs vary by provider. Some (like Google) don't charge extra for caching.*
