# Anti-Patterns and Key Insights

Summary of common LLM coding anti-patterns, the timing problem that makes "good" patterns harmful, and core insights from Karpathy's observations.

---

## Anti-Patterns Summary

**Silently Assumes**: The LLM picks file formats, field names, data structures, and scope without asking. Fix: list assumptions explicitly, ask for clarification before implementing.

**Over-Abstracts Early**: Strategy patterns, factory classes, and dependency injection for single-use code. Fix: one function until complexity is actually needed by a concrete requirement.

**Drive-by Refactoring**: Reformats quotes, adds type hints, changes naming conventions while fixing an unrelated bug. Fix: only change lines that fix the reported issue.

**Vague Success Criteria**: "I'll review and improve the code" instead of "write test for bug X, make it pass, verify no regressions." Fix: transform every task into a verifiable goal with specific check conditions.

---

## The Timing Problem

The overcomplicated examples in the code examples reference are not obviously wrong — they follow established design patterns and best practices. The problem is timing: complexity is added before it is needed, which makes code harder to understand, introduces more bugs, takes longer to implement, and is harder to test.

The simple versions are easier to understand, faster to implement, easier to test, and can be refactored later when complexity is actually needed.

Good code is code that solves today's problem simply, not tomorrow's problem prematurely.

---

## Karpathy's Key Observations

From Andrej Karpathy's original analysis:

> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

> "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."

> "They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task."

> "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go."

---

## Applying to Different Tools

These guidelines work across AI coding tools. The core principles translate directly:

**Claude Code**: Use as CLAUDE.md content or install via the plugin marketplace from the original repository.

**Cursor**: Place as a `.cursor/rules/` file with `alwaysApply: true`.

**Pi / OpenCode / Codex**: Use as an agent skill in `.agents/skills/`.

**General**: Merge into any project-specific instruction file. The guidelines are designed to compose with existing rules — add them alongside project conventions, coding standards, and architectural guidelines.

---

## Customization

Add project-specific sections alongside these guidelines:

```markdown
## Project-Specific Guidelines

- Use TypeScript strict mode
- All API endpoints must have tests
- Follow the existing error handling patterns in `src/utils/errors.ts`
```

The four principles provide behavioral guardrails. Project-specific rules provide technical constraints. Together they produce clean, correctly-scoped changes.
