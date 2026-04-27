# The Ralph Loop Methodology

## Origins

The Ralph loop (also called "Ralph Wiggum loop" or "Ralph Wiggum technique") is an autonomous coding methodology pioneered by Geoffrey Huntley. It breaks feature development into structured phases — each run as an independent agent loop with checkpoints. Wiggum CLI implements this technique as a production-grade tool.

The core insight: **AI agents are bad at planning but good at executing**. Give an agent a vague instruction like "add user authentication" and it starts writing code immediately — often in the wrong place, with wrong patterns, missing edge cases, and no tests. The Ralph loop forces structure before execution.

## Why Structure Matters

METR's 2025 research on AI agent capabilities shows that success rates drop sharply as task complexity increases — from near-100% on tasks a human finishes in under 4 minutes, to less than 10% on tasks requiring over 4 hours of human effort. Without structure, agents default to the most obvious implementation path, which is rarely the best one.

GitClear's 2025 analysis of 211 million lines of code changes found that AI-assisted development correlates with copy-pasted code rising from 8.3% to 12.3% of all changes, while refactoring dropped from 25% to under 10%. Explicit verification catches these quality issues before they reach production.

## The Five Phases

The Ralph loop separates execution into five distinct phases, each with clear inputs and outputs:

### Phase 1: Plan

The agent reads the spec and creates a step-by-step implementation plan. This plan accounts for the project's specific file structure, patterns, and conventions — because `wiggum init` captured all that context upfront. The plan is visible in the TUI so you can review it before execution continues.

**Input**: Feature spec (`.ralph/specs/<name>.md`) + project context
**Output**: Structured implementation plan with file-level tasks

### Phase 2: Implement

Code gets written according to the plan. The agent creates or modifies files, adds imports, updates configurations. Because it's working from a structured plan (not a vague description), changes are focused and consistent.

**Input**: Implementation plan + project codebase
**Output**: Working code changes

### Phase 3: Test

The agent writes tests for the new functionality and runs the existing test suite. If tests fail, it iterates — fixing either the implementation or the tests until everything passes. This is where backpressure works: tests reject invalid work, forcing the agent to fix issues before proceeding.

**Input**: Implemented code + test framework configuration
**Output**: Passing test suite

### Phase 4: Verify

The agent re-reads the original spec and checks each requirement against the actual implementation. Did it add the API endpoint? Does error handling match the spec? Are edge cases covered? This isn't a rubber stamp — it's an explicit confirmation step that catches subtle cases where code "works" but doesn't do what was asked.

**Input**: Original spec + implemented code
**Output**: Verification report confirming spec compliance

### Phase 5: PR

The agent creates a pull request with a structured description: what was changed, why, and how to test it. The PR is ready for human review.

**Input**: All verified changes
**Output**: Pull request with structured summary

## Phase Isolation vs. Bash Scripts

This is the critical distinction between Wiggum and simpler Ralph loop implementations:

**Bash-script loops** run agents in a single undifferentiated retry loop. The agent does everything in one pass, and if something goes wrong, you restart from scratch. When implementation hits a wall, the agent thrashes — rewriting the same code over and over.

**The Ralph loop** separates concerns: planning happens before implementation, testing happens after implementation, verification happens after testing. Each phase can succeed or fail independently. If implementation fails, you know exactly where it failed and can intervene at that specific phase. Phase-level retry means you don't waste tokens re-doing successful phases.

| Aspect | Bash Scripts | Ralph Loop (Wiggum) |
|--------|-------------|---------------------|
| Execution model | Single retry loop | 5 isolated phases |
| Spec quality | Manual prompt | AI-generated from codebase context |
| Error recovery | Restart from scratch | Phase-level retry |
| Monitoring | Terminal output | TUI with phase tracking |
| Agent support | Hardcoded | Any CLI agent |

## Checkpoints and Recovery

Each phase has a checkpoint. The TUI shows real-time progress with phase indicators. If a loop is interrupted, `--resume` continues from the last successful checkpoint rather than starting over. This matters for long-running features that might take hours.

The action inbox feature allows loops to pause mid-execution and request user input without blocking. You approve or redirect, then the loop continues.

## When to Use the Ralph Loop

**Good candidates:**
- CRUD features — well-defined inputs and outputs
- API endpoints — clear request/response contracts
- UI components — detailed design specs
- Refactoring tasks — mechanical changes with clear before/after
- Test coverage — writing tests for existing code

**Less ideal candidates:**
- Exploratory work — when you're not sure what you want yet
- Deeply creative tasks — novel algorithms, architecture design
- Cross-cutting concerns — changes that touch every file in the project

## The Spec-First Principle

The Ralph loop works best for well-specified features. The better your spec, the better the output. This is why Wiggum pairs the Ralph loop with a spec generation step — the AI interview ensures your spec is detailed enough for autonomous execution.

When autonomous loops produce bad code, the real culprit is usually a vague or incomplete specification, not the agent. Wiggum's `wiggum new` command runs an AI-powered interview grounded in your actual codebase context to generate implementation-ready specs with test plans and architectural decisions.
