# Subagent Patterns

## The Primary Context Window As Scheduler

Ralph requires a mindset of not allocating expensive results to the primary context window. Instead, spawn subagents to perform allocation-heavy work. The primary context window operates as a scheduler, delegating tasks and receiving summarized results.

Every tool execution in an agentic loop adds its evaluation result to the context window. When subagents run builds, tests, or codebase searches, their full output would fill the primary context rapidly. By keeping subagent results summarized, the primary agent maintains a lean context focused on decision-making.

## Parallel Subagents for File Operations

Ralph can use many parallel subagents for searching the filesystem and writing files:

```
You may use up to 500 parallel subagents for all operations but only 1
subagent for build/tests of rust.
```

This pattern allows massive parallelism for read/write/search operations while constraining validation to a single serial channel. The reasoning is practical: if hundreds of subagents simultaneously run builds and tests, the resulting backpressure overwhelms the system.

## Serial Subagents for Validation

Only one subagent should handle build and test validation:

```
You may use up to parallel subagents for all operations but only 1
subagent for build/tests of rust.
```

This prevents "bad form back pressure" — the chaos that results from hundreds of concurrent build processes competing for resources and flooding the context window with interleaved output.

## Controlling Parallelism

You can control the amount of parallelism for subagents through explicit instructions in your prompt. Different operations benefit from different levels of concurrency:

- **Codebase search**: High parallelism (many files searched simultaneously)
- **File writing**: Moderate parallelism (avoid conflicts on same files)
- **Build/test validation**: Single serial channel (one at a time)
- **Standard library authoring**: High parallelism when modules are independent

## Subagent Delegation Patterns

### Search Before Assume

Use subagents to verify assumptions about the codebase before making changes:

```
Before making changes search codebase (don't assume not implemented)
using subagents. Think hard.
```

Code-based search via ripgrep is non-deterministic. A common failure scenario is the LLM running a search and incorrectly concluding that code has not been implemented. Subagents provide more thorough verification than the primary agent's limited search capacity.

### Plan Maintenance

Use subagents to keep the plan file updated without consuming the primary context:

```
ALWAYS KEEP @fix_plan.md up to date with your learnings using a subagent.
```

This ensures the plan stays current while the primary agent focuses on implementation decisions.

### Self-Documentation

Use subagents to update operational knowledge:

```
When you learn something new about how to run the compiler or examples
make sure you update @AGENT.md using a subagent but keep it brief.
```

This creates a feedback loop where operational knowledge accumulates without polluting the primary context window with command output and debugging traces.

### Bug Resolution

Use subagents to handle discovered bugs independently:

```
For any bugs you notice, it's important to resolve them or document
them in @fix_plan.md to be resolved using a subagent even if it is
unrelated to the current piece of work.
```

This allows the primary agent to stay focused on its current task while subagents handle discovered issues asynchronously.

### Plan Cleanup

Use subagents to maintain plan file hygiene:

```
When @fix_plan.md becomes large periodically clean out the items that
are completed from the file using a subagent.
```

Large plan files consume valuable context window space. Regular cleanup keeps the allocation lean.

## Context Window Economics

Understanding context window usage is essential for effective subagent patterns:

- The practical context window limit is approximately 170k tokens
- Every tool execution adds its result to the context
- Subagent results should be summarized, not dumped in full
- The primary agent's context should contain decisions and summaries, not raw output
- Specifications are re-allocated every loop (intentional waste for consistency)

## Subagent Anti-Patterns

### Fanning Out Validation

Never fan out build/test validation across many subagents. The resulting backpressure overwhelms the system with interleaved output and resource contention.

### Unbounded Context Allocation

Do not let subagents dump full execution results into the primary context. Instruct subagents to summarize findings rather than return raw output.

### Ignoring Subagent Findings

When subagents report issues (bugs, missing implementations, inconsistencies), the primary agent must act on them — either by resolving immediately or documenting in the plan file.

## Speculative Decoding With Subagents

When building complex systems like compilers, use subagents for speculative exploration:

```
Your task is to implement missing stdlib and compiler functionality and
produce a compiled application via LLVM for that functionality using
parallel subagents. Follow the fix_plan.md and choose the most important
thing. Before making changes search codebase (don't assume not implemented)
using subagents.
```

This pattern lets multiple subagents explore different implementation paths simultaneously, with the primary agent selecting the best result based on backpressure feedback.
