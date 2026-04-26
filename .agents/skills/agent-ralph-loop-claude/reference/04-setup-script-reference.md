# Setup Script Reference

## Overview

`scripts/setup-ralph-loop.sh` is called by the `/ralph-loop` command. It parses user arguments, validates inputs, creates the state file, and outputs setup confirmation messages.

## Argument Parsing

The script accepts positional arguments (the prompt) and two named options:

```bash
/ralph-loop [PROMPT...] [--max-iterations <n>] [--completion-promise '<text>']
```

### Positional Arguments

All non-option arguments are collected as prompt parts and joined with spaces. This allows prompts without quoting:

```bash
/ralph-loop Build a REST API for todos
```

### --max-iterations

Sets the maximum number of loop iterations before auto-stop.

- Must be a positive integer or 0 (unlimited)
- Default: 0 (unlimited)
- Validation rejects decimals, negative numbers, and non-numeric text

Examples:
```bash
--max-iterations 10    # Stop after 10 iterations
--max-iterations 50    # Stop after 50 iterations
--max-iterations 0     # Unlimited (runs forever)
```

### --completion-promise

Sets the exact phrase that signals task completion.

- Multi-word promises must be quoted
- Default: null (no promise check, relies on max-iterations only)
- The value is YAML-quoted in the state file to preserve spaces and special characters

Examples:
```bash
--completion-promise 'DONE'
--completion-promise 'TASK COMPLETE'
--completion-promise 'All tests passing'
```

## State File Creation

The script creates `.claude/ralph-loop.local.md` with YAML frontmatter:

```yaml
---
active: true
iteration: 1
session_id: <CLAUDE_CODE_SESSION_ID>
max_iterations: <n>
completion_promise: "<text>"
started_at: "2025-01-15T10:30:00Z"
---

<User's prompt text>
```

Fields:
- `active` — always true when loop is running
- `iteration` — starts at 1, incremented by Stop hook each cycle
- `session_id` — from `${CLAUDE_CODE_SESSION_ID}` environment variable
- `max_iterations` — 0 means unlimited
- `completion_promise` — quoted string or null
- `started_at` — UTC timestamp in ISO 8601 format

After the closing `---`, the full user prompt is stored as markdown body text. The Stop hook extracts this using awk to get everything after the second `---`.

## Validation

The script validates inputs before creating any files:

1. **Empty prompt** — exits with error if no positional arguments provided
2. **Missing option values** — exits with error if `--max-iterations` or `--completion-promise` lacks an argument
3. **Invalid max-iterations** — exits with error if value is not a non-negative integer

Each validation error includes specific examples of correct usage.

## Output Messages

On successful setup, the script outputs:

1. Activation confirmation with iteration count, max iterations, and completion promise
2. Instructions for monitoring (`head -10 .claude/ralph-loop.local.md`)
3. Warning that the loop cannot be stopped manually without `--max-iterations` or `--completion-promise`
4. The initial prompt text
5. If a completion promise is set, a detailed banner explaining the `<promise>` tag requirements and strict rules against outputting false promises

## Help Text

Running with `-h` or `--help` displays full usage documentation including description, arguments, options, examples, stopping methods, and monitoring commands.
