# Feedback and Backpressure

## The Feedback Loop Problem

Ralph runs autonomously — potentially while you sleep. Without feedback mechanisms, broken code compounds across iterations. Each iteration builds on the previous one's output. If iteration 3 introduces a bug, iterations 4 through 10 may build on that broken foundation, creating cascading failures.

Feedback loops are Ralph's immune system — they detect and reject bad code before it propagates.

## Quality Gates

Every Ralph iteration must pass quality checks before committing. These are the gates that prevent broken code from entering the repository.

### Standard Quality Checks

The prompt instructs Ralph to run:

1. **Typecheck** — `npm run typecheck` or equivalent
2. **Lint** — `npm run lint` or equivalent
3. **Tests** — `npm test` or equivalent

These checks are project-specific and should be customized in the prompt template. The key requirement: **all commits must pass quality checks**.

### Why Typechecking Is Mandatory

Type checking is the most important quality gate because it catches errors that syntax checking misses:

- Incorrect function signatures
- Missing imports
- Type mismatches in data flow
- Broken interfaces between modules

Every story's acceptance criteria must include "Typecheck passes" as a verifiable condition. This is not optional.

### The Backpressure Concept

Geoffrey Huntley describes this as **backpressure** — the mechanism that rejects invalid code generation. Just as a pipe system uses backpressure to prevent overflow, Ralph uses quality checks to prevent bad code from propagating.

```
Generate code → Run tests/typecheck → Pass? → Commit
                                    → Fail? → Fix and retry
```

The speed of this cycle matters. Fast feedback (seconds) is better than slow feedback (minutes). The faster the wheel turns, the more iterations Ralph can complete in a given time.

## Testing Strategies

### Unit Tests Per Story

After implementing functionality, Ralph runs tests for that specific unit of code:

```markdown
After implementing functionality or resolving problems, run the tests for that unit of code that was improved.
```

This targeted approach is more efficient than running the full test suite for every change. It provides fast feedback on the specific area being modified.

### Test Documentation

Ralph is instructed to document **why** tests exist, not just what they test:

```markdown
Important: When authoring documentation (e.g., rust doc or stdlib documentation), capture the why — explain what tests are trying to verify and why the backing implementation is important.
```

Example from a real Ralph-generated test:

```python
@doc """
Tests that the QueryOptimizer initializes the required ETS tables.

This test ensures that the init function properly creates the ETS tables
needed for caching and statistics tracking. This is fundamental to the
module's operation.
"""
test "creates required ETS tables" do
  # Clean up any existing tables first
  try do :ets.delete(:anole_query_cache) catch _:_ -> :ok end
  try do :ets.delete(:anole_query_stats) catch _:_ -> :ok end

  # Call init
  assert :ok = QueryOptimizer.init()

  # Verify tables exist
  assert :ets.info(:unole_query_cache) != :undefined
  assert :ets.info(:anole_query_stats) != :undefined
end
```

This documentation helps future Ralph iterations understand whether a test is still relevant or if it should be modified/deleted.

### Related Test Failures

When tests unrelated to the current work fail, Ralph must resolve them:

```markdown
If tests unrelated to your work fail then it's your job to resolve these tests as part of the increment of change.
```

This prevents test debt from accumulating across iterations. Every commit leaves the test suite in a passing state.

## Browser Verification for UI Stories

Frontend stories require visual verification. Code can be correct syntactically but still produce wrong visual output.

### The dev-browser Skill

Ralph uses the [dev-browser skill](https://github.com/anthropics/claude-code-dev-browser) to verify UI changes:

```bash
# Start the browser server
~/.config/amp/skills/dev-browser/server.sh &

# Write and execute a verification script
cd ~/.config/amp/skills/dev-browser && npx tsx <<'EOF'
import { connect, waitForPageLoad } from "@/client.js";

const client = await connect();
const page = await client.page("test");
await page.setViewportSize({ width: 1280, height: 900 });
const port = process.env.PORT || "3000";
await page.goto(`http://localhost:${port}/your-page`);
await waitForPageLoad(page);
await page.screenshot({ path: "tmp/screenshot.png" });
await client.disconnect();
EOF
```

### Browser Verification Criteria

UI stories must include this acceptance criterion:

```
Verify in browser using dev-browser skill
```

A frontend story is NOT complete until browser verification passes. The screenshot provides evidence that the UI renders correctly.

## Preventing Placeholder Implementations

Claude (and other models) have an inherent bias toward minimal and placeholder implementations. They optimize for "compiling code" rather than "correct, complete code."

### The Anti-Placeholder Directive

```markdown
DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS. WE WANT FULL IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU
```

This extreme language signals maximum importance to the model. It addresses the reward function bias where models prefer stub implementations that compile over complete implementations that may not.

### Detection Strategies

If Ralph produces placeholder code despite the directive:

1. Run additional Ralph loops focused on identifying placeholders
2. Search for TODO comments, stub functions, and minimal implementations
3. Transform findings into a new task list for future iterations

```markdown
Consider searching for TODO, minimal implementations and placeholders.
```

## Language-Specific Backpressure

Different programming languages provide different levels of built-in backpressure through their type systems.

### Strongly Typed Languages (Rust, TypeScript)

- **Advantage**: Type system catches many errors at compile time
- **Tradeoff**: Slower compilation means slower feedback cycles
- Rust's strong types provide extreme correctness but slow iteration speed
- TypeScript's type checking is fast and catches most interface errors

### Dynamically Typed Languages (Python, JavaScript)

For dynamically typed languages, wire in external static analysis:

- **Python**: [pyrefly.org](https://pyrefly.org/) for type checking
- **Erlang**: Dialyzer for static analysis
- **JavaScript**: ESLint + TypeScript type checking

Without static analysis on dynamically typed languages, Ralph will produce a "bonfire of outcomes" — compounding errors that are hard to trace.

## Speed of the Feedback Cycle

The speed of quality checks directly impacts Ralph's effectiveness:

- **Fast feedback** (seconds): Typecheck, unit tests, linting
- **Medium feedback** (minutes): Integration tests, full test suite
- **Slow feedback** (hours): End-to-end tests, deployment pipelines

Ralph works best with fast feedback. The faster the wheel turns, the more iterations complete in a given time, and the more opportunities Ralph has to self-correct.

### Optimizing Feedback Speed

- Run only relevant tests for the changed code
- Use incremental type checking where available
- Cache build artifacts between iterations (git preserves them)
- Avoid full rebuilds when partial checks suffice

## The Compounding Effect of Quality Gates

Quality gates create a compounding positive effect:

1. **Iteration 1**: Ralph implements a feature, passes typecheck and tests
2. **Iteration 2**: Ralph builds on iteration 1's verified code — no inherited bugs
3. **Iteration 3**: Ralph continues building on verified foundation
4. **Iteration N**: The codebase remains healthy because every increment was verified

Without quality gates:

1. **Iteration 1**: Ralph implements a feature with a subtle bug
2. **Iteration 2**: Ralph builds on the buggy code, introducing new bugs
3. **Iteration 3**: The bug cascade grows — Ralph is now fixing bugs from iterations 1 and 2
4. **Iteration N**: The codebase is broken, Ralph is spinning its wheels

This is why the prompt emphasizes: "Keep CI green. Broken code compounds across iterations."

## Customizing Quality Checks

After copying the prompt template to your project, customize quality check commands:

```markdown
## Quality Requirements

Run these checks before committing:
1. `npm run typecheck` — TypeScript type checking
2. `npm run lint` — ESLint code style
3. `npm test -- --testPathPattern=changed-files` — Relevant tests only
4. `npx prisma validate` — Database schema validation
```

Include any project-specific checks that catch errors early:

- Database migration validation
- API contract testing
- Security scanning
- Performance benchmarks
- Accessibility checks

## When Feedback Is Not Enough

Some issues cannot be caught by automated feedback:

- Architectural decisions
- Security vulnerabilities in logic (not syntax)
- Business logic correctness
- User experience quality

For these, human review is essential. Ralph is designed to get you to 90% — the remaining 10% requires human judgment.

## Summary of Feedback Principles

1. **Every commit passes quality checks** — No exceptions
2. **Typecheck is mandatory** — Include in every story's acceptance criteria
3. **Tests are documented** — Explain why tests exist, not just what they test
4. **Browser verification for UI** — Visual confirmation is required
5. **Anti-placeholder directives** — Prevent minimal implementations
6. **Fast feedback cycles** — Optimize for speed of iteration
7. **Static analysis for dynamic languages** — Wire in type checkers
8. **Resolve all test failures** — Don't leave test debt behind
