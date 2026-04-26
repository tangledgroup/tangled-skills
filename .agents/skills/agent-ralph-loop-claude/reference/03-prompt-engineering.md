# Prompt Engineering

## Writing Effective Ralph Prompts

Ralph Loop prompts need to be self-contained and include clear completion criteria. Since the same prompt is fed back on every iteration, it must contain all necessary context — Claude relies on files and git history for progress tracking, not on accumulated conversation.

### Clear Completion Criteria

Specify exactly what "done" means with verifiable conditions:

```markdown
Build a REST API for todos.

When complete:
- All CRUD endpoints working
- Input validation in place
- Tests passing (coverage > 80%)
- README with API docs
- Output: <promise>COMPLETE</promise>
```

Avoid vague language like "make it good" or "build something for X."

### Incremental Goals

Break complex tasks into ordered phases:

```markdown
Phase 1: User authentication (JWT, tests)
Phase 2: Product catalog (list/search, tests)
Phase 3: Shopping cart (add/remove, tests)

Output <promise>COMPLETE</promise> when all phases done.
```

This gives Claude a natural progression — each iteration can focus on the next unfinished phase.

### Self-Correction Instructions

Explicitly tell Claude to verify and fix its own work:

```markdown
Implement feature X following TDD:
1. Write failing tests
2. Implement feature
3. Run tests
4. If any fail, debug and fix
5. Refactor if needed
6. Repeat until all green
7. Output: <promise>COMPLETE</promise>
```

### Escape Hatches

Always use `--max-iterations` as a safety net to prevent infinite loops on impossible tasks:

```bash
/ralph-loop "Try to implement feature X" --max-iterations 20
```

Include instructions for what to do if stuck:

```markdown
After 15 iterations, if not complete:
- Document what's blocking progress
- List what was attempted
- Suggest alternative approaches
```

## Anti-Patterns

### Vague Promises

The `--completion-promise` uses exact string matching. You cannot use it for multiple completion conditions:

```bash
# This won't work as expected — only "DONE" will match
/ralph-loop "..." --completion-promise "DONE"
# Claude outputting <promise>SUCCESS</promise> will NOT stop the loop
```

Always rely on `--max-iterations` as your primary safety mechanism.

### Overly Broad Tasks

```markdown
# Too broad — no clear stopping point
Create a complete e-commerce platform.
```

Break into specific, verifiable subtasks instead.

### Missing Verification Steps

```markdown
# No way for Claude to know if it succeeded
Write code for feature X.
```

Include test commands, lint checks, or other verification steps:

```markdown
# Better — includes self-verification
Implement feature X:
1. Write the implementation
2. Run: pytest tests/test_feature_x.py
3. Fix any failures
4. Output <promise>COMPLETE</promise> when all tests pass
```

## Real-World Results

From published testing:

- Successfully generated 6 repositories overnight in Y Combinator hackathon testing
- One $50k contract completed for $297 in API costs
- Created an entire programming language ("cursed") over 3 months using this approach

These results demonstrate that with well-crafted prompts, Ralph Loop can drive substantial autonomous development work.

## Philosophy

Ralph embodies several key principles:

- **Iteration > Perfection** — Don't aim for perfect on first try. Let the loop refine the work.
- **Failures Are Data** — "Deterministically bad in an undeterministic world" means failures are predictable and informative. Use them to tune prompts.
- **Operator Skill Matters** — Success depends on writing good prompts, not just having a good model.
- **Persistence Wins** — Keep trying until success. The loop handles retry logic automatically.
