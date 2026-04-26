# Stop Conditions

Stop conditions determine when the outer Ralph loop should halt. Multiple conditions can be combined as an array — the loop stops when **any** condition is met (OR logic).

## Built-in Stop Conditions

### `iterationCountIs(n)`

Stop after `n` iterations. This is the default (`10`) if no stop condition is provided.

```typescript
import { iterationCountIs } from 'ralph-loop-agent';

stopWhen: iterationCountIs(50)
```

### `tokenCountIs(n)`

Stop when total token usage (input + output combined) exceeds `n`.

```typescript
import { tokenCountIs } from 'ralph-loop-agent';

stopWhen: tokenCountIs(100_000)
```

### `inputTokenCountIs(n)`

Stop when input token count alone exceeds `n`.

```typescript
import { inputTokenCountIs } from 'ralph-loop-agent';

stopWhen: inputTokenCountIs(50_000)
```

### `outputTokenCountIs(n)`

Stop when output token count alone exceeds `n`.

```typescript
import { outputTokenCountIs } from 'ralph-loop-agent';

stopWhen: outputTokenCountIs(50_000)
```

### `costIs(maxCost, ratesOrModel?)`

Stop when estimated cost exceeds `maxCost` (in USD). Uses built-in pricing for common models or accepts custom rates.

```typescript
import { costIs } from 'ralph-loop-agent';

// Infer pricing from agent's model
stopWhen: costIs(5.00)

// Explicit model string
stopWhen: costIs(5.00, 'anthropic/claude-sonnet-4')

// Custom rates (cost per million tokens)
stopWhen: costIs(5.00, {
  inputCostPerMillionTokens: 3.00,
  outputCostPerMillionTokens: 15.00,
})
```

## Combining Stop Conditions

Pass an array to stop when **any** condition is met:

```typescript
stopWhen: [
  iterationCountIs(50),
  tokenCountIs(100_000),
  costIs(5.00),
]
```

## Built-in Model Pricing

The `costIs` function includes pricing for these models (cost per million tokens in USD):

**Anthropic:**

- `claude-haiku-4.5`: $1.00 input / $5.00 output
- `claude-3.5-haiku`: $0.80 input / $4.00 output
- `claude-3-haiku`: $0.25 input / $1.25 output
- `claude-sonnet-4.5` / `claude-3.7-sonnet` / `claude-sonnet-4` / `claude-3.5-sonnet`: $3.00 input / $15.00 output
- `claude-opus-4.5`: $5.00 input / $25.00 output
- `claude-opus-4.1` / `claude-opus-4` / `claude-3-opus`: $15.00 input / $75.00 output

**OpenAI:**

- `gpt-4o`: $2.50 input / $10.00 output
- `gpt-4o-mini`: $0.15 input / $0.60 output
- `gpt-4-turbo`: $10.00 input / $30.00 output
- `o1`: $15.00 input / $60.00 output
- `o1-mini` / `o3-mini`: $1.10 input / $4.40 output

**Google:**

- `gemini-2.5-pro`: $1.25 input / $10.00 output
- `gemini-2.5-flash`: $0.15 input / $0.60 output
- `gemini-2.0-flash`: $0.10 input / $0.40 output

**Other:**

- `xai/grok-3`: $3.00 input / $15.00 output
- `xai/grok-3-mini`: $0.30 input / $0.50 output
- `deepseek/deepseek-chat`: $0.14 input / $0.28 output
- `deepseek/deepseek-reasoner`: $0.55 input / $2.19 output

## Cost Calculation Details

The `calculateCost` function accounts for prompt caching when cache token details are available:

- Uncached input tokens use standard input rate
- Cache read tokens use `cacheReadCostPerMillionTokens` (if defined)
- Cache write tokens use `cacheWriteCostPerMillionTokens` (if defined)
- Output tokens always use standard output rate

When no cache details are present, the standard input rate applies to all input tokens.

## Custom Stop Conditions

Implement `RalphStopCondition<TOOLS>` — a function receiving `RalphStopConditionContext` and returning `boolean | Promise<boolean>`:

```typescript
import type { RalphStopCondition } from 'ralph-loop-agent';

const elapsedMinutesIs = (minutes: number): RalphStopCondition<any> => {
  const startTime = Date.now();
  return () => (Date.now() - startTime) / 60_000 >= minutes;
};

stopWhen: elapsedMinutesIs(30)
```

The context provides:

- `iteration` — Current iteration number (1-indexed)
- `allResults` — All `GenerateTextResult` from completed iterations
- `totalUsage` — Aggregated `LanguageModelUsage` across all iterations
- `model` — Model identifier string (e.g., `'anthropic/claude-opus-4.5'`)

## Token Usage Aggregation

The package provides utilities for accurate token counting:

**`aggregateStepUsage(result)`** — Sums usage from all steps within a `generateText` result. This is more accurate than `result.usage` alone, which may not include all tool call tokens. Takes the maximum between step-aggregated and result-level counts.

**`addLanguageModelUsage(usage1, usage2)`** — Adds two `LanguageModelUsage` objects together, handling undefined fields correctly.

**`getModelPricing(model)`** — Looks up built-in pricing for a model string. Returns `undefined` if unknown.
