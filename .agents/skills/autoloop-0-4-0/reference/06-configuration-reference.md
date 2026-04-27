# Configuration Reference

## File Format

All runtime configuration lives in `autoloops.toml` at the root of a loop's project directory. Keys use flat dot-notation (`section.key = value`). Configuration is **hot-reloaded** every iteration — change any value mid-run and it takes effect on the next iteration without restarting.

```toml
event_loop.max_iterations = 100
backend.command = "pi"
event_loop.required_events = ["review.passed"]
```

Arrays can use TOML syntax or bare CSV:
```toml
event_loop.required_events = ["review.passed", "tests.ok"]
# equivalent to:
event_loop.required_events = review.passed,tests.ok
```

## Precedence

`autoloops.toml` > `autoloops.conf` (legacy) > built-in defaults. The CLI `-b`/`--backend` flag overrides backend settings at runtime. Extra arguments after `--` are appended to the backend's argument list.

## Event Loop Keys

- `event_loop.max_iterations` — maximum iterations before halt (default: `3`)
- `event_loop.completion_event` — event signaling completion (default: `"task.complete"`, overridden by `topology.toml` `completion` field)
- `event_loop.completion_promise` — text fallback string for completion when model cannot emit structured events (default: `"LOOP_COMPLETE"`)
- `event_loop.required_events` — events that must appear in journal before completion is accepted (default: empty)
- `event_loop.prompt` — inline prompt text (takes precedence over `prompt_file`)
- `event_loop.prompt_file` — path to file containing the loop objective

Prompt resolution order: CLI override > `event_loop.prompt` > `event_loop.prompt_file`.

## Backend Keys

- `backend.kind` — backend type: `"pi"` for Pi adapter, `"kiro"` for Kiro ACP backend (persistent session), `"command"` for mock/test (default: auto-detected from command)
- `backend.command` — executable to invoke (default: `"pi"`)
- `backend.timeout_ms` — timeout per invocation in milliseconds (default: `300000`, i.e., 5 minutes)
- `backend.args` — extra flags appended after built-in arguments (default: empty)
- `backend.prompt_mode` — how the prompt is passed: `"arg"` (command-line argument) or `"stdin"` (default: `"arg"`)
- `backend.trust_all_tools` — auto-approve tool permissions (Kiro only, default: `true`)
- `backend.agent` — agent name for ACP session (Kiro only)
- `backend.model` — model ID for ACP session (Kiro only)

## Review Keys

- `review.enabled` — enable metareview (default: `true`)
- `review.every_iterations` — run review every N iterations; `0` = auto-derive from topology role count
- `review.command` / `review.kind` / `review.args` / `review.prompt_mode` — fallback to corresponding backend values
- `review.timeout_ms` — timeout for review invocations (default: `300000`)
- `review.prompt` — inline review prompt text
- `review.prompt_file` — path to review prompt file (default: `"metareview.md"`)

## Parallel Keys

- `parallel.enabled` — enable structured parallel trigger validation (default: `false`)
- `parallel.max_branches` — maximum branch objectives from one `.parallel` trigger (default: `3`)
- `parallel.branch_timeout_ms` — timeout budget per branch wave in milliseconds (default: `180000`)

## Worktree / Isolation Keys

- `worktree.enabled` — enable worktree isolation by default (default: `false`)
- `isolation.enabled` — alias for `worktree.enabled`
- `worktree.branch_prefix` — prefix for worktree branch names (default: `"autoloop"`)
- `worktree.merge_strategy` — merge strategy: `"squash"`, `"merge"`, or `"rebase"` (default: `"squash"`)
- `worktree.cleanup` — when to remove worktree: `"on_success"` or `"always"` (default: `"on_success"`)

## Memory Keys

- `memory.prompt_budget_chars` — maximum characters of memory injected into prompt (default: `8000`)

## Profile Keys

- `profiles.default` — profile specs activated on every run unless `--no-default-profiles` is passed (default: empty)

## Harness Keys

- `harness.instructions_file` — path to harness instructions file (default: `"harness.md"`)

## Core Keys

- `core.state_dir` — directory for runtime state (default: `".autoloop"`)
- `core.journal_file` — path to journal file (default: `".autoloop/journal.jsonl"`)
- `core.memory_file` — path to memory file (default: `".autoloop/memory.jsonl"`)
- `core.tasks_file` — path to tasks file (default: `".autoloop/tasks.jsonl"`)
- `core.log_level` — log verbosity: `debug`, `info`, `warn`, `error`, `none` (default: `"info"`)
- `core.run_id_format` — run ID format: `"human"` (`<word>-<word>`), `"compact"` (timestamp-based), `"counter"` (`run-1`, `run-2`)

## Full Example

```toml
event_loop.max_iterations = 100
event_loop.completion_event = "task.complete"
event_loop.completion_promise = "LOOP_COMPLETE"
event_loop.required_events = ["review.passed"]

backend.kind = "pi"
backend.command = "pi"
backend.timeout_ms = 300000

review.enabled = true
review.timeout_ms = 300000
review.every_iterations = 0

parallel.enabled = false
parallel.max_branches = 3
parallel.branch_timeout_ms = 180000

memory.prompt_budget_chars = 8000
harness.instructions_file = "harness.md"

core.state_dir = ".autoloop"
core.journal_file = ".autoloop/journal.jsonl"
core.memory_file = ".autoloop/memory.jsonl"
core.tasks_file = ".autoloop/tasks.jsonl"

worktree.enabled = false
worktree.branch_prefix = "autoloop"
worktree.merge_strategy = "squash"
worktree.cleanup = "on_success"
```
