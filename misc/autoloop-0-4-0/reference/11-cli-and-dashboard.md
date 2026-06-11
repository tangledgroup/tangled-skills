# CLI and Dashboard

## Main Commands

```
autoloop run <preset-name|preset-dir> [prompt...] [flags]
autoloop list
autoloop loops [--all]
autoloop loops show <run-id>
autoloop loops artifacts <run-id>
autoloop loops watch <run-id>
autoloop inspect <artifact> [selector] [--format <md|terminal|text|json|csv|graph>]
autoloop dashboard [--port <port>]
autoloop worktree <list|show|merge|clean> [args]
autoloop chain <list|run> [args]
autoloop emit <topic> [summary]
autoloop memory <list|status|find|add|remove> [args]
autoloop task <add|complete|update|remove|list> [args]
autoloop runs clean [--max-age <days>]
```

## `run` — Start a Loop

```bash
autoloop run autocode "Fix the login bug"
autoloop run . "Fix the login bug" -b pi
autoloop run --preset autocode "Fix the login bug"
autoloop run autocode --worktree --automerge "Implement the approved fix"
autoloop run . --chain autocode,autoqa "Implement and validate"
```

Flags:
- `-b <backend>` — override backend (`pi`, `kiro`, `claude`, or any shell command)
- `-p <preset>` / `--preset` — resolve a named or custom preset
- `--chain <steps>` — run an inline chain of comma-separated presets
- `--worktree` / `--no-worktree` — force worktree isolation or shared checkout
- `--automerge` — auto-merge worktree on success
- `--profile <spec>` — activate a profile (`repo:<name>` or `user:<name>`)
- `--no-default-profiles` — suppress config-defined default profiles
- `-v` / `--verbose` — debug-level logging
- `-- <args>` — pass extra arguments to the backend

## `loops` — Operator Surface

```bash
autoloop loops                              # active runs
autoloop loops --all                        # all runs
autoloop loops show <run-id>                # detailed run info
autoloop loops artifacts <run-id>           # artifact file paths
autoloop loops watch <run-id>               # live watch (polls every 2s)
autoloop loops health                       # exception-focused health summary
autoloop loops health --verbose             # include completions
```

Health system classifies runs using preset-aware thresholds:
- **Active** — running and recently updated
- **Watching** — quiet longer than the preset's warning threshold
- **Stuck** — quiet longer than the preset's stuck threshold
- **Failed** — failed or timed out within 24 hours
- **Completed** — completed within 24 hours (shown with `--verbose`)

## `inspect` — Read Projected Artifacts

```bash
autoloop inspect journal --format json      # raw JSONL
autoloop inspect scratchpad --format md     # iteration summaries
autoloop inspect prompt 3 --format md       # iteration 3 prompt
autoloop inspect output 3 --format text     # iteration 3 output
autoloop inspect memory --format md         # materialized memory
autoloop inspect coordination --format md   # issues, slices, commits
autoloop inspect metrics --format csv       # per-iteration metrics
autoloop inspect chain --format md          # chain execution state
autoloop inspect topology --format graph    # ASCII directed graph
```

## `emit` — Publish Coordination Events

```bash
autoloop emit doc.written "Wrote docs/cli.md"
autoloop emit task.complete "All work done"
```

Validated against the current iteration's allowed-event set. Coordination topics bypass validation.

## `dashboard` — Browser-Based Operator UI

```bash
autoloop dashboard                           # http://127.0.0.1:4800
autoloop dashboard -p 3000                   # custom port
autoloop dashboard --host 0.0.0.0 -p 8080   # bind to all interfaces
```

Alpine.js SPA served from a local Hono HTTP server. Four zones: header, chat box (preset dropdown + prompt textarea), run list grouped by health status, and detail pane with events timeline. Polls API routes on a 3-second interval.

### API Routes

- `GET /api/runs` — all runs categorized by health status
- `GET /api/runs/:id` — single run by ID or prefix match
- `GET /api/runs/:id/events` — parsed journal events for a run
- `GET /api/presets` — available presets with descriptions
- `POST /api/runs` — start a new loop (spawns detached child process)
- `GET /healthz` — readiness check

## Environment Variables

- `AUTOLOOP_PROJECT_DIR` — override the project directory
- `AUTOLOOP_STATE_DIR` — state directory for stream logs
- `AUTOLOOP_ITERATION` — current iteration number
- `AUTOLOOP_PROMPT` — override the prompt sent to the backend
- `AUTOLOOP_BIN` — path to the autoloops binary
- `AUTOLOOP_LOG_LEVEL` — current log level
- `AUTOLOOP_REVIEW_MODE` — set to `metareview` during review turns
- `AUTOLOOP_MEMORY_FILE` — exported so agents can locate the memory file

## Mock Backend for Testing

A deterministic mock backend removes the need for a live LLM:

```bash
export MOCK_FIXTURE_PATH=test/fixtures/backend/complete-success.json
autoloop run . -b "node dist/testing/mock-backend.js"
```

Fixture schema:
```json
{
  "output": "text printed to stdout",
  "exit_code": 0,
  "delay_ms": 0,
  "emit_event": "task.complete",
  "emit_payload": "done"
}
```
