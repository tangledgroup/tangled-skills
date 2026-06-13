# The Four Principles

Detailed guidance for each of the four behavioral principles. Each principle includes specific rules and a quick test to verify compliance.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

LLMs often pick an interpretation silently and run with it. This principle forces explicit reasoning before implementation begins.

### Rules

- **State assumptions explicitly** — If uncertain, ask rather than guess. Name the assumption and why you made it.
- **Present multiple interpretations** — Don't pick silently when ambiguity exists. List the options with tradeoffs.
- **Push back when warranted** — If a simpler approach exists, say so. If the request conflicts with project conventions, flag it.
- **Stop when confused** — Name what's unclear and ask for clarification. Do not proceed past confusion.

### Common Failure Modes

LLMs tend to:

- Assume file formats, field names, and data structures without checking
- Pick one interpretation of ambiguous requests and commit to it
- Implement features the user didn't ask for based on "what makes sense"
- Hide uncertainty behind confident-sounding but wrong implementations

### The Test

Before writing any code, could you articulate:

1. What you are building and why
2. What assumptions you are making
3. At least one alternative interpretation (if applicable)

If you cannot answer these clearly, stop and clarify first.

---

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

Combat the tendency toward overengineering. The default should always be the simplest thing that could possibly work.

### Rules

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If you write 200 lines and it could be 50, rewrite it

### When to Add Complexity

Only add complexity when a concrete requirement demands it. If the need for multiple strategies, caching layers, or configuration systems emerges later — refactor then. Do not preemptively build scaffolding for hypothetical future needs.

### The Test

Would a senior engineer say this is overcomplicated? If yes, simplify.

Specifically: could the same behavior be achieved with fewer classes, fewer functions, fewer conditional branches? If so, reduce until it cannot.

---

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code, the scope of changes should match the scope of the request precisely.

### When Editing Existing Code

- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it — don't delete it

### When Your Changes Create Orphans

- Remove imports, variables, and functions that YOUR changes made unused
- Don't remove pre-existing dead code unless explicitly asked

### Style Matching

When adding code to an existing file, match:

- Quote style (single vs. double)
- Spacing conventions
- Whether type hints are used
- Docstring conventions
- Variable naming patterns

Do not "upgrade" the existing code's style as a side effect of your change.

### The Test

Every changed line should trace directly to the user's request. If you cannot explain why a specific line changed in terms of the original request, it should not be there.

---

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform imperative tasks into verifiable goals. Strong success criteria let the agent loop independently. Weak criteria ("make it work") require constant clarification.

### Transform Tasks Into Verification Loops

Instead of vague instructions, convert to test-driven steps:

- "Add validation" becomes "Write tests for invalid inputs, then make them pass"
- "Fix the bug" becomes "Write a test that reproduces it, then make it pass"
- "Refactor X" becomes "Ensure tests pass before and after"

### Multi-Step Plans

For multi-step tasks, state a brief plan with verification at each step:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Each step should be independently verifiable and, where possible, independently deployable.

### Test-First Approach

When fixing bugs:

1. Write a test that reproduces the issue
2. Verify the test fails (confirms the bug exists)
3. Implement the fix
4. Verify the test passes
5. Check for regressions in existing tests

### The Test

Can you state, before writing code, exactly what conditions must be true when you are done? If the answer is "it works" or "it doesn't crash", the criteria are too weak.

---

## Tradeoff Note

These guidelines bias toward caution over speed. For trivial tasks — simple typo fixes, obvious one-liners, straightforward renames — use judgment. Not every change needs the full rigor.

The goal is reducing costly mistakes on non-trivial work, not slowing down simple tasks.
