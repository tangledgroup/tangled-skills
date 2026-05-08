# Error Handling

## Contents
- Fail-Fast Semantics
- Error Recovery Patterns
- Debugging Multi-Stage Pipes
- Partial Output Handling

## Fail-Fast Semantics

### Default Behavior

Pipes use **fail-fast** by default. If any stage fails, the pipe stops immediately and reports the failure. Subsequent stages are not executed.

A stage is considered failed when:

- A tool returns a non-zero exit code (bash)
- A skill produces an explicit error or empty result where data was expected
- A file cannot be read (read tool reports file not found)
- A search returns zero results and the next stage depends on those results
- The agent determines it cannot meaningfully execute the stage with available context

### Failure Report Format

When a pipe fails, report:

```
**Pipe failed at Stage N** (`<stage-instruction>`): <error-reason>
Stage N-1 produced: <brief-description-of-previous-output>
Suggested fix: <actionable-suggestion>
```

**Example**:

```
**Pipe failed at Stage 2** (`scrapling get first result URL`): No URLs found in search results.
Stage 1 produced: 0 results for query "nonexistent-topic-xyz-12345".
Suggested fix: Try a broader search query or check the spelling of the search term.
```

### When to Override Fail-Fast

Override fail-fast only when explicitly instructed. Signals to continue despite errors:

- "continue even if stage fails"
- "skip errors"
- "best effort"
- "try your best even if some stages don't work"

When overriding, mark skipped stages clearly in the output:

```
Stage 2: SKIPPED (no results from Stage 1, continuing with empty context)
```

## Error Recovery Patterns

### Retry

If a stage fails due to a transient error (network timeout, temporary file access issue), retry once before reporting failure.

```
Stage 1: duckduckgo search for "topic" — FAILED (timeout)
Stage 1: RETRY — SUCCESS (3 results)
Stage 2: scrapling get first result URL — executing...
```

Do not retry more than once. If the second attempt fails, report failure.

### Skip

If a stage is optional and its failure doesn't block meaningful progress, skip it and continue with whatever context is available.

```
Stage 1: read optional-config.yaml — FAILED (file not found)
Stage 1: SKIPPED (optional file, using defaults)
Stage 2: analyze the codebase — executing with default config
```

Only skip if the stage was clearly optional or the user instructed continuation.

### Substitute

If a stage fails because a specific skill/tool is unavailable, try a reasonable substitute.

```
Stage 2: scrapling get https://example.com — FAILED (scrapling not available)
Stage 2: SUBSTITUTE with bash curl — SUCCESS
```

Substitution examples:
- `scrapling` → `bash curl` + `pandoc` for HTML-to-Markdown
- `duckduckgo` → direct `bash curl` to alternative search
- `read` of remote URL → `bash curl` to fetch content

Report substitutions clearly so the user knows what changed.

## Debugging Multi-Stage Pipes

### Identifying the Failed Stage

Each stage should be numbered in error reports. When debugging, focus on:

1. **Which stage failed** — the error report identifies this
2. **What the previous stage produced** — was its output valid for the next stage?
3. **Whether the stage instruction is clear** — ambiguous instructions cause silent failures

### Common Debugging Steps

1. **Run stages individually**: Execute each stage separately to isolate the failure point
2. **Inspect intermediate output**: Check what Stage N-1 actually produced vs what Stage N expected
3. **Check stage resolution**: Verify the agent resolved the stage to the correct skill/tool (not a raw instruction when a skill was intended)
4. **Verify pipe buffer**: Ensure the previous stage's output wasn't truncated or empty

### Example Debug Session

```
Pipe: | read data.csv | extract email column | validate all emails

Failure: Stage 3 reports "no data to validate"

Debug:
- Stage 1 (read data.csv): Produces full CSV content ✓
- Stage 2 (extract email column): Produces empty output ✗
- Root cause: Stage 2 instruction was ambiguous — agent didn't know which column is "email"
- Fix: | read data.csv | extract the "contact_email" column by header name | validate all emails
```

## Partial Output Handling

### Truncated Input

If a stage receives truncated pipe buffer input (because the previous stage exceeded size limits):

- Proceed with available data
- Note in output: `[working with truncated input: N of M lines]`
- If truncation clearly affects correctness, report as a warning (not a failure)

### Partial Stage Success

If a stage partially succeeds (e.g., processed 8 of 10 items, 2 failed):

- Report the partial results
- List which items failed and why
- Continue the pipe with whatever output was produced
- Mark the stage as PARTIAL in the output

```
Stage 2: scrapling get 5 URLs — PARTIAL (3 succeeded, 2 failed)
  - https://a.com: OK
  - https://b.com: OK
  - https://c.com: OK
  - https://d.com: FAILED (404)
  - https://e.com: FAILED (timeout)
Stage 3: summarize — executing with 3 of 5 pages
```

### Empty Intermediate Results

If a stage produces valid but empty output (e.g., "grep found 0 matches"):

- This is NOT a failure if the operation completed successfully
- The next stage receives an empty pipe buffer
- If the next stage cannot meaningfully operate on empty input, it fails gracefully with a clear message

```
Stage 2: bash grep -r "TODO" src/ — SUCCESS (0 matches found)
Stage 3: count the TODOs — Result: 0 TODO comments found in src/
```

Here Stage 3 can still produce meaningful output (the count is 0), so the pipe succeeds.

### Distinguishing Empty from Failed

| Scenario | Status | Action |
|----------|--------|--------|
| Tool completed, zero results | SUCCESS | Continue with empty buffer |
| Tool crashed or returned error code | FAILED | Fail-fast, report error |
| Skill produced no output | Check context — if expected (e.g., filter found nothing), SUCCESS; if unexpected, FAILED |
| Agent cannot execute instruction | FAILED | Report ambiguity and stop |
