# Stop Hook Deep Dive

## Overview

The Stop hook (`hooks/stop-hook.sh`) is the core mechanism that creates the Ralph Loop. It intercepts Claude Code's session exit, checks whether a loop is active and complete, and either allows exit or feeds the prompt back for another iteration.

## Execution Flow

```
Claude tries to exit
  │
  ▼
Stop hook fires (receives JSON on stdin)
  │
  ├── No state file? → exit 0 (allow exit)
  │
  ├── Wrong session_id? → exit 0 (allow exit, another session owns the loop)
  │
  ├── Corrupted state? → cleanup + exit 0
  │
  ├── Max iterations reached? → cleanup + exit 0
  │
  ├── No transcript? → cleanup + exit 0
  │
  └── Parse last assistant message
      │
      ├── Completion promise matched? → cleanup + exit 0 (success)
      │
      └── Not complete → update iteration + output JSON to block exit
```

## Hook Input

The Stop hook receives JSON on stdin from Claude Code:

```json
{
  "session_id": "<unique-session-id>",
  "transcript_path": "/path/to/transcript.jsonl"
}
```

## State File Parsing

The hook reads `.claude/ralph-loop.local.md` and extracts YAML frontmatter fields using `sed` and `grep`:

- `iteration` — current iteration number (must be numeric)
- `max_iterations` — maximum allowed iterations (0 = unlimited)
- `completion_promise` — expected promise text (null if not set)
- `session_id` — owning session for isolation

## Session Isolation

The hook compares the state file's `session_id` against the hook input's `session_id`. If they differ, the hook exits cleanly — this prevents one Claude Code session from blocking another that happened to start a Ralph loop.

Legacy state files without `session_id` fall through to allow backward compatibility.

## Transcript Parsing

The hook reads the transcript (JSONL format) to extract Claude's last assistant text message:

1. Grep for lines containing `"role":"assistant"`
2. Take the last 100 such lines (bounded input for performance)
3. Use `jq` to extract text blocks only (filtering out tool_use and thinking blocks)
4. Take the last text block

This approach handles Claude Code's JSONL format where each content block is its own line, all with `role: assistant`.

## Completion Promise Detection

When a completion promise is configured, the hook extracts text from `<promise>` tags using Perl:

```bash
PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe 's/.*?<promise>(.*?)<\/promise>.*/$1/s; s/^\s+|\s+$//g; s/\s+/ /g')
```

The Perl flags:
- `-0777` — slurp entire input (enables multiline matching)
- `s` flag in regex — makes `.` match newlines
- `.*?` — non-greedy (takes first `<promise>` tag)
- Whitespace normalization — strips leading/trailing whitespace, collapses internal whitespace

Comparison uses `=` for literal string matching (not glob pattern matching), avoiding issues with special characters like `*`, `?`, `[`.

## Loop Continuation Output

When the loop should continue, the hook outputs JSON to block exit:

```json
{
  "decision": "block",
  "reason": "<original prompt text>",
  "systemMessage": "🔄 Ralph iteration N | To stop: output <promise>TEXT</promise>"
}
```

The `reason` field contains the original prompt extracted from the state file (everything after the closing `---`). The `systemMessage` provides Claude with iteration context and completion instructions.

## Error Handling

The hook handles several failure modes gracefully:

- **Corrupted iteration field** — non-numeric value triggers cleanup with diagnostic message
- **Corrupted max_iterations field** — same as above
- **Missing transcript file** — cleanup with warning
- **No assistant messages in transcript** — cleanup with warning
- **jq parse failure** — cleanup with error details
- **Empty prompt in state file** — cleanup with diagnostic explaining possible causes

In all error cases, the hook removes the state file and allows exit to prevent infinite error loops.

## Iteration Update

The hook updates the iteration count atomically:

```bash
TEMP_FILE="${RALPH_STATE_FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$RALPH_STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$RALPH_STATE_FILE"
```

Using a temp file with process ID suffix and atomic `mv` prevents corruption from concurrent access or interrupted writes.
