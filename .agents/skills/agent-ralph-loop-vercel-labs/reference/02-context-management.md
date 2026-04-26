# Context Management

Long-running agent loops accumulate conversation history that can exceed model context windows. `RalphContextManager` handles this automatically when enabled through the `contextManagement` setting.

## Enabling Context Management

```typescript
const agent = new RalphLoopAgent({
  model: 'anthropic/claude-opus-4.5',
  contextManagement: {
    maxContextTokens: 180_000,      // Leave room for output within model's window
    enableSummarization: true,       // Auto-summarize older iterations
    recentIterationsToKeep: 2,       // Keep last 2 iterations in full detail
    maxFileChars: 30_000,            // Truncate files larger than this
    changeLogBudget: 8_000,          // Token budget for change log
    fileContextBudget: 60_000,       // Token budget for tracked files
  },
});
```

## Configuration Options

**`maxContextTokens`** (default: 150,000) — Maximum tokens to use for context. Set this to your model's context window minus a buffer for output.

**`enableSummarization`** (default: true) — Whether to auto-summarize older messages when approaching token limits.

**`recentIterationsToKeep`** (default: 2) — Number of recent iterations to keep in full detail before summarizing.

**`maxFileChars`** (default: 30,000) — Maximum characters for a single file read before truncation. Larger files are chunked with line numbers.

**`changeLogBudget`** (default: 5,000) — Token budget reserved for the change log of decisions and actions.

**`fileContextBudget`** (default: 50,000) — Token budget reserved for tracked file contents.

**`summarizationModel`** (optional) — Separate model to use for summarization. Uses the main model if not provided.

## What Context Manager Tracks

### File Context

When tools read or write files, the context manager tracks them:

- **File reads** are cached with estimated token counts. Large files are auto-truncated with line numbers and a message instructing how to read specific sections.
- **File writes** remove the old cached content (since it's stale) and log the modification.
- **File edits** update the cached content in-place.
- Least-recently-used files are evicted when the file context budget is exceeded.

### Change Log

A running log of decisions, actions, errors, and observations. Each entry has a type, summary, optional details, iteration number, and timestamp. Oldest entries are trimmed when the budget is exceeded.

### Iteration Summaries

When summarization triggers (messages exceed 70% of `maxContextTokens`), the context manager uses the LLM to generate a 2-3 sentence summary of each older iteration. Summaries capture what was accomplished, key decisions, and blockers.

## Token Budget Management

The context manager maintains three budgets:

- **File budget** — For cached file contents
- **Change log budget** — For decision/action tracking
- **Summaries budget** — For compressed iteration history

Call `contextManager.getTokenBudget()` to inspect current usage:

```typescript
const budget = agent.getContextManager()?.getTokenBudget();
// { total: 180000, used: { files: 12000, changeLog: 3000, summaries: 5000 }, available: 160000 }
```

## Context-Aware Tool Wrappers

The `createContextAwareTools` helper wraps existing tools to automatically track file operations through the context manager:

```typescript
import { createContextAwareTools, RalphContextManager } from 'ralph-loop-agent';

const contextManager = new RalphContextManager({
  maxContextTokens: 150_000,
});

const tools = createContextAwareTools(
  { readFile, writeFile, editFile, otherTool },
  contextManager
);
```

Supported tool names for tracking: `readFile`, `writeFile`, `editFile`. Other tools pass through unchanged.

## Manual Context Operations

Access the context manager directly via `agent.getContextManager()`:

**Track a file read:**

```typescript
const ctx = agent.getContextManager();
const result = ctx.trackFileRead('src/index.ts', content, {
  lineRange: { start: 50, end: 100 },
});
// Returns { content, truncated, totalLines?, lineRange? }
```

**Track a file write:**

```typescript
ctx.trackFileWrite('src/index.ts', newContent);
```

**Add a change log entry:**

```typescript
ctx.addChangeLogEntry({
  type: 'decision',
  summary: 'Chose Vitest over Jest for migration',
  details: 'Vitest has better Vite integration and faster startup',
});
```

**Build context injection string:**

```typescript
const injection = ctx.buildContextInjection();
// Returns formatted markdown with summaries and change log
```

**Clear all tracked state:**

```typescript
ctx.clear();
```

## Token Estimation Utilities

**`estimateTokens(text)`** — Rough estimate using 3.5 chars ≈ 1 token (intentionally conservative).

**`estimateMessageTokens(message)`** — Estimate tokens for a `ModelMessage`, handling string content, array content with text/tool result parts, and defaults to 100 for unknown parts.

## Summarization Flow

When the context manager detects that messages are approaching the token budget:

1. It identifies messages from the previous iteration
2. Calls `summarizeIteration()` which extracts tool usage and file modifications
3. Sends a summarization prompt to the LLM (or `summarizationModel`)
4. Stores the summary as an `IterationSummary` with tools used, files modified, and estimated token cost
5. Keeps only recent messages (based on `recentIterationsToKeep`)
6. Returns compressed message set for the next iteration

The `onContextSummarized` callback fires when this happens:

```typescript
onContextSummarized: ({ iteration, summarizedIterations, tokensSaved }) => {
  console.log(`Context summarized at iteration ${iteration}: ${summarizedIterations} iterations compressed, ${tokensSaved} tokens available`);
},
```

## Large File Handling

When a file exceeds `maxFileChars`:

- If `lineRange` is provided, extract that specific range with line numbers
- If no range, auto-truncate to the first portion and append: `... [TRUNCATED: File has N lines, showing 1-M. Use lineRange to read specific sections] ...`
- Line numbers are left-padded to 6 digits for alignment

This prevents single large files from consuming the entire context budget.
