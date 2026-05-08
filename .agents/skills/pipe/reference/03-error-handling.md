# Error Handling

## Contents
- Stage Failure Modes
- Error Propagation Strategies
- Recovery Patterns
- Partial Pipe Results

## Stage Failure Modes

A stage can fail in several ways:

1. **Resolution failure** — The agent cannot determine which capability to use for the stage
2. **Execution failure** — The resolved capability runs but produces an error (e.g., file not found, tool error)
3. **Context failure** — The stage depends on output from a previous stage that was empty or malformed
4. **Timeout** — The stage takes too long to complete (platform-dependent)

### Detection

The agent should detect failures by:
- Checking for explicit error messages in tool/script output
- Checking for empty or null outputs when content is expected
- Checking for resolution ambiguity with no clear winner
- Observing platform-level timeout signals

## Error Propagation Strategies

By default, pipes use **fail-fast** semantics — the pipe stops at the first stage failure.

### Fail-Fast (Default)

When a stage fails, stop execution immediately and report:
- Which stage failed
- The error message or reason
- Any partial results from stages that completed before the failure

```
/pipe read nonexistent.txt | analyze content
       ↓
    File not found → pipe stops, "analyze content" never runs
```

### Continue-With-Warning

For non-critical failures, the agent may continue with remaining stages if:
- The failure is recoverable (e.g., optional file missing)
- Subsequent stages don't depend on the failed stage's output
- The user explicitly requested lenient execution

The agent should flag warnings inline but proceed.

```
/pipe read optional-config.yaml | fall back to defaults | generate report
       ↓
    File not found → warning logged, "fall back to defaults" runs, pipe continues
```

## Recovery Patterns

When a stage fails, the agent can apply these recovery strategies:

### Retry

If the failure is transient (e.g., network timeout, temporary file lock), retry the stage once before reporting failure. Do not retry indefinitely — one retry is sufficient to distinguish transient from persistent failures.

### Skip and Continue

If the stage is optional and subsequent stages don't depend on its output, skip the failed stage and continue with the next one. Mark the skipped stage in the output report.

### Fallback Stage

If a stage has an obvious alternative approach, try the alternative before reporting failure:

```
/pipe read config.json | (if fails) read config.yaml | parse settings
```

The agent interprets parenthetical fallbacks as conditional alternatives. If `config.json` doesn't exist, try `config.yaml`.

## Partial Pipe Results

When a pipe fails partway through, the agent should report:

1. **Completed stages** — List each completed stage with its output (or summary of output)
2. **Failed stage** — The stage that caused failure, with error details
3. **Skipped stages** — Stages that never ran due to the failure

This allows the user to understand what succeeded and what didn't, and to decide whether to retry, modify, or abort the pipe.

### Example Error Report

```
Pipe execution: 2/4 stages completed

✓ Stage 1: "read src/main.py" — 150 lines read
✓ Stage 2: "find function definitions" — found 7 functions
✗ Stage 3: "generate type signatures" — failed: no type information available
  ⏭ Stage 4: "format as markdown" — skipped (depends on stage 3)
```
