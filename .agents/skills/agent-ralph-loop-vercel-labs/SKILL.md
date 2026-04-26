---
name: agent-ralph-loop-vercel-labs
description: Continuous autonomy framework for the Vercel AI SDK implementing the Ralph Wiggum technique — an iterative outer loop that keeps feeding an AI agent a task until verifyCompletion confirms success. Use when building autonomous coding agents, long-running code migrations, refactoring tasks, or any workflow requiring iterative verification and feedback loops beyond single-shot LLM tool calls.
license: Apache-2.0
author: Tangled <noreply@tangledgroup.com>
version: "0.0.3"
tags:
  - autonomous-agent
  - ai-sdk
  - iterative-loop
  - coding-agent
  - continuous-autonomy
  - vercel
category: agent-framework
external_references:
  - https://github.com/vercel-labs/ralph-loop-agent
---

# Ralph Loop Agent (Vercel Labs) 0.0.3

## Overview

Ralph Loop Agent is an experimental npm package from Vercel Labs that implements the "Ralph Wiggum technique" for continuous AI agent autonomy. It wraps the Vercel AI SDK's `generateText` in an outer iteration loop that keeps running until a `verifyCompletion` function confirms the task is actually done — or a safety limit is hit.

Named after the persistently repeating Ralph Wiggum from *The Simpsons*, this approach embraces iterative improvement over single-shot perfection. Where standard AI SDK tool loops stop when the model finishes its tool calls, Ralph keeps going: verifying completion, providing feedback, and running another iteration until the task actually succeeds.

Think of it as `while (true)` for AI autonomy: the agent works, an evaluator checks the result, and if it's not done, the agent tries again with context from previous attempts.

### Architecture: Two Nested Loops

```
Outer Ralph Loop (ralph-loop-agent)
├── Iteration 1
│   └── Inner AI SDK Tool Loop (generateText)
│       └── LLM ↔ tools ↔ LLM ↔ tools ... until toolStopWhen
├── verifyCompletion: "Is the task actually complete?"
├── If not done → inject feedback → Iteration 2
│   └── Inner AI SDK Tool Loop (with accumulated context)
├── ...
└── If done → return RalphLoopAgentResult
```

## When to Use

- Building autonomous coding agents that run until a task is verified complete
- Long-running code migrations (Jest → Vitest, CJS → ESM, etc.)
- Dependency upgrades across large codebases
- Multi-file refactoring tasks requiring verification between iterations
- Feature implementation from specifications with automated review
- Any workflow where single-shot LLM tool calls are insufficient and iterative verification is needed

## Installation

```bash
npm install ralph-loop-agent ai zod
```

The package depends on the Vercel AI SDK (`ai` ≥ 6.0.0) and `@ai-sdk/provider-utils`. Zod 4.x is a peer dependency.

## Core Concepts

### The Ralph Loop Pattern

Standard AI SDK `generateText` runs an inner tool loop: LLM calls tools, gets results, calls more tools, until `stopWhen` (typically `stepCountIs(20)`). Then it returns. Ralph wraps this in an outer loop:

1. Run `generateText` (inner tool loop)
2. Check stop conditions (iterations, tokens, cost)
3. Call `verifyCompletion` to check if the task is actually done
4. If not complete, inject feedback into conversation and go to step 1
5. If complete or stop condition hit, return final result

### Key Components

**RalphLoopAgent** — The main class. Accepts a model, instructions, tools, stop conditions, and a verification function. Provides `loop()` for full execution and `stream()` for streaming the final iteration.

**Stop Conditions** — Functions that determine when to halt the outer loop: `iterationCountIs(n)`, `tokenCountIs(n)`, `costIs(maxDollars)`. Multiple conditions can be combined as an array (OR'd together).

**verifyCompletion** — An async function called after each iteration. Returns `{ complete: boolean, reason?: string }`. When `complete` is false, the `reason` string is injected as feedback for the next iteration.

**RalphContextManager** — Built-in context management for long-running loops. Tracks file reads/writes, maintains a change log, auto-summarizes older iterations when approaching token limits, and handles large files with line-range chunking.

## Usage Examples

### Basic Agent Loop

```typescript
import { RalphLoopAgent, iterationCountIs } from 'ralph-loop-agent';

const agent = new RalphLoopAgent({
  model: 'anthropic/claude-opus-4.5',
  instructions: 'You are a helpful coding assistant.',
  stopWhen: iterationCountIs(10),
  verifyCompletion: async ({ result }) => ({
    complete: result.text.includes('DONE'),
    reason: 'Task completed successfully',
  }),
});

const { text, iterations, completionReason } = await agent.loop({
  prompt: 'Create a function that calculates fibonacci numbers',
});

console.log(text);
console.log(`Completed in ${iterations} iterations`);
console.log(`Reason: ${completionReason}`);
```

### Migration Task with Real Verification

```typescript
import { RalphLoopAgent, iterationCountIs } from 'ralph-loop-agent';

const migrationAgent = new RalphLoopAgent({
  model: 'anthropic/claude-opus-4.5',
  instructions: `You are migrating a codebase from Jest to Vitest.

    Completion criteria:
    - All test files use vitest imports
    - vitest.config.ts exists
    - All tests pass when running 'pnpm test'`,

  tools: { readFile, writeFile, execute },

  stopWhen: iterationCountIs(50),

  verifyCompletion: async () => {
    const checks = await Promise.all([
      fileExists('vitest.config.ts'),
      !await fileExists('jest.config.js'),
      noFilesMatch('**/*.test.ts', /from ['"]@jest/),
      fileContains('package.json', '"vitest"'),
    ]);

    return {
      complete: checks.every(Boolean),
      reason: checks.every(Boolean) ? 'Migration complete' : 'Structural checks failed',
    };
  },

  onIterationStart: ({ iteration }) => console.log(`Starting iteration ${iteration}`),
  onIterationEnd: ({ iteration, duration }) => console.log(`Iteration ${iteration} completed in ${duration}ms`),
});

const result = await migrationAgent.loop({
  prompt: 'Migrate all Jest tests to Vitest.',
});

console.log(result.text);
console.log(result.iterations);
console.log(result.completionReason);
```

### Streaming the Final Iteration

```typescript
const stream = await agent.stream({
  prompt: 'Build a calculator',
});

for await (const chunk of stream.textStream) {
  process.stdout.write(chunk);
}
```

Note: Streaming runs non-streaming iterations until verification passes or the final iteration is reached, then streams that last iteration.

## Advanced Topics

**Stop Conditions & Cost Control**: Built-in pricing for Anthropic, OpenAI, Google, xAI, and DeepSeek models → [Stop Conditions](reference/01-stop-conditions.md)

**Context Management for Long Loops**: File tracking, change logs, auto-summarization, token budgets → [Context Management](reference/02-context-management.md)

**API Reference**: Complete type definitions for RalphLoopAgent, settings, results, and verification → [API Reference](reference/03-api-reference.md)

**CLI Example Architecture**: Coding agent + Vercel Sandbox + Judge Agent pattern from the reference implementation → [CLI Example](reference/04-cli-example.md)
