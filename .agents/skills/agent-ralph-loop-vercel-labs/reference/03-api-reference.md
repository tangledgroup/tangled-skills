# API Reference

## RalphLoopAgent

### Constructor

```typescript
new RalphLoopAgent<TOOLS extends ToolSet>(settings: RalphLoopAgentSettings<TOOLS>)
```

### Properties

- `version` — String identifier (`'ralph-agent-v1'`)
- `id` — Optional agent ID from settings
- `tools` — The tools available to the agent

### Methods

**`loop(options)`** — Runs the agent loop until completion or stop condition.

```typescript
async loop({
  prompt: string,                              // Task description
  abortSignal?: AbortSignal,                   // For cancellation
  preserveContext?: boolean,                   // Preserve context from previous loop() calls (default: false)
  startIteration?: number,                     // Starting iteration for resuming (default: 0)
}): Promise<RalphLoopAgentResult<TOOLS>>
```

**`stream(options)`** — Streams the final iteration. Runs non-streaming iterations until verification passes or stop condition is near, then streams the last one.

```typescript
async stream({
  prompt: string,
  abortSignal?: AbortSignal,
}): Promise<StreamTextResult<TOOLS>>
```

**`getContextManager()`** — Returns the `RalphContextManager` instance if context management is enabled, or `null`.

## RalphLoopAgentSettings

Full settings type (extends AI SDK's `CallSettings`):

- `id?: string` — Agent identifier
- `instructions?: string | SystemModelMessage | SystemModelMessage[]` — System prompt(s)
- `model: LanguageModel | string` — AI model (AI Gateway string format supported, e.g., `'anthropic/claude-opus-4.5'`)
- `tools?: TOOLS` — Tool set for the agent
- `toolChoice?: ToolChoice` — Tool selection strategy (default: `'auto'`)
- `stopWhen?: RalphStopCondition | RalphStopCondition[]` — Outer loop stop condition(s) (default: `iterationCountIs(10)`)
- `toolStopWhen?: StopCondition | StopCondition[]` — Inner tool loop stop condition (default: `stepCountIs(20)`)
- `verifyCompletion?: VerifyCompletionFunction<TOOLS>` — Task completion verification
- `contextManagement?: RalphContextConfig` — Context management configuration
- `onIterationStart?: OnIterationStartCallback` — Called at start of each iteration
- `onIterationEnd?: OnIterationEndCallback<TOOLS>` — Called at end of each iteration
- `onContextSummarized?: function` — Called when context is summarized due to token limits
- `providerOptions?: ProviderOptions` — Provider-specific options
- `experimental_context?: unknown` — Context passed into tool calls
- All standard AI SDK `CallSettings`: `maxOutputTokens`, `temperature`, `topP`, `topK`, `presencePenalty`, `frequencyPenalty`, `stopSequences`, `seed`, `prepareStep`, `activeTools`, `experimental_telemetry`, `experimental_repairToolCall`

## RalphLoopAgentResult

```typescript
interface RalphLoopAgentResult<TOOLS extends ToolSet = {}> {
  text: string;                              // Final output text
  iterations: number;                        // Number of iterations executed
  completionReason: 'verified' | 'max-iterations' | 'aborted';
  reason?: string;                           // Reason from verifyCompletion
  result: GenerateTextResult<TOOLS, never>;  // Full result from last iteration
  allResults: GenerateTextResult<TOOLS, never>[];  // All iteration results
  totalUsage: LanguageModelUsage;            // Aggregated token usage
}
```

## VerifyCompletion

```typescript
type VerifyCompletionFunction<TOOLS extends ToolSet = {}> = (
  context: VerifyCompletionContext<TOOLS>,
) => VerifyCompletionResult | Promise<VerifyCompletionResult>;

interface VerifyCompletionContext<TOOLS extends ToolSet = {}> {
  result: GenerateTextResult<TOOLS, never>;     // Current iteration result
  iteration: number;                             // Current iteration (1-indexed)
  allResults: GenerateTextResult<TOOLS, never>[];  // All results so far
  originalPrompt: string;                        // Original task prompt
}

interface VerifyCompletionResult {
  complete: boolean;    // true to stop the loop, false to continue
  reason?: string;      // If complete=true: explanation. If complete=false: feedback for next iteration
}
```

## Callbacks

### OnIterationStartCallback

```typescript
type OnIterationStartCallback = (event: {
  iteration: number;  // 1-indexed
}) => void | Promise<void>;
```

### OnIterationEndCallback

```typescript
type OnIterationEndCallback<TOOLS extends ToolSet = {}> = (event: {
  iteration: number;                                 // 1-indexed
  duration: number;                                  // Milliseconds
  result: GenerateTextResult<TOOLS, never>;          // Iteration result
}) => void | Promise<void>;
```

### OnContextSummarizedCallback

```typescript
(event: {
  iteration: number;              // Current iteration when summarization occurred
  summarizedIterations: number;   // How many iterations were compressed
  tokensSaved: number;            // Tokens available after summarization
}) => void | Promise<void>;
```

## Stop Condition Types

```typescript
type RalphStopCondition<TOOLS extends ToolSet = {}> = (
  context: RalphStopConditionContext<TOOLS>,
) => boolean | Promise<boolean>;

interface RalphStopConditionContext<TOOLS extends ToolSet = {}> {
  iteration: number;
  allResults: GenerateTextResult<TOOLS, never>[];
  totalUsage: LanguageModelUsage;
  model: string;
}

type CostRates = {
  inputCostPerMillionTokens: number;
  outputCostPerMillionTokens: number;
  cacheReadCostPerMillionTokens?: number;
  cacheWriteCostPerMillionTokens?: number;
};
```

## Exported Functions

| Function | Purpose |
|----------|---------|
| `iterationCountIs(n)` | Stop after n iterations |
| `tokenCountIs(n)` | Stop when total tokens exceed n |
| `inputTokenCountIs(n)` | Stop when input tokens exceed n |
| `outputTokenCountIs(n)` | Stop when output tokens exceed n |
| `costIs(maxCost, rates?)` | Stop when cost exceeds maxCost |
| `getModelPricing(model)` | Look up built-in pricing for a model |
| `calculateCost(usage, rates)` | Calculate cost from usage and rates |
| `addLanguageModelUsage(a, b)` | Add two usage objects |
| `aggregateStepUsage(result)` | Aggregate token usage from all steps |
| `estimateTokens(text)` | Rough token estimate (3.5 chars ≈ 1 token) |
| `estimateMessageTokens(msg)` | Token estimate for a ModelMessage |
| `createContextAwareTools(tools, ctx)` | Wrap tools to track file operations |

## RalphContextManager

```typescript
class RalphContextManager {
  constructor(config?: RalphContextConfig);

  getTokenBudget(): { total: number; used: { files: number; changeLog: number; summaries: number }; available: number };
  setIteration(iteration: number): void;
  trackFileRead(path: string, content: string, options?): { content: string; truncated: boolean; totalLines?: number; lineRange? };
  trackFileWrite(path: string, content: string): void;
  trackFileEdit(path: string, oldString: string, newString: string): void;
  addChangeLogEntry(entry): void;
  getChangeLogContext(): string;
  getFileContext(): string;
  getIterationSummariesContext(): string;
  buildContextInjection(): string;
  prepareMessagesForIteration(messages, iteration, model, previousResult?): Promise<{ messages: ModelMessage[]; summarized: boolean }>;
  summarizeIteration(iteration, messages, model): Promise<IterationSummary>;
  clear(): void;
}
```

## RalphContextConfig

- `maxContextTokens?: number` (default: 150,000)
- `changeLogBudget?: number` (default: 5,000)
- `fileContextBudget?: number` (default: 50,000)
- `maxFileChars?: number` (default: 30,000)
- `enableSummarization?: boolean` (default: true)
- `recentIterationsToKeep?: number` (default: 2)
- `summarizationModel?: LanguageModel`

## Model Support

The agent accepts any AI SDK-compatible model. String format uses AI Gateway convention: `'provider/model-id'`. Anthropic models receive automatic prompt caching via `cacheControl: { type: 'ephemeral' }` on the last message.
