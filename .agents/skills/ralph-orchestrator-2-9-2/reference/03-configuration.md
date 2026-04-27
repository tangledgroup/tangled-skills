# Configuration Reference

## Configuration File Layers

Ralph composes configuration from up to three layers (deep merge, project overrides user):

1. `~/.ralph/config.yml` — User-level defaults (loaded automatically if present)
2. `ralph.yml` in workspace root (or `$RALPH_CONFIG` / `-c <file>`) — Project overrides
3. `-c core.field=value` — CLI overrides applied last

```bash
ralph run                                    # Uses ralph.yml + ~/.ralph/config.yml
ralph run -c custom-config.yml              # Override project config path
ralph run -c ralph.yml -c core.scratchpad=.runs/task-1/scratchpad.md
```

## Full YAML Schema

```yaml
# Event loop settings
event_loop:
  completion_promise: "LOOP_COMPLETE"   # Output text that ends the loop
  max_iterations: 100                    # Maximum orchestration loops
  max_runtime_seconds: 14400             # 4 hours max runtime
  idle_timeout_secs: 1800                # 30 min idle timeout
  starting_event: "task.start"           # First event published (hat mode)
  checkpoint_interval: 5                 # Git checkpoint frequency
  prompt_file: "PROMPT.md"               # Default prompt file

# CLI backend settings
cli:
  backend: "claude"                      # Backend name
  prompt_mode: "arg"                     # arg or stdin

# Core behaviors
core:
  scratchpad:                            # Scratchpad configuration
    enabled: true                        # Enable scratchpad (default: true)
    path: .ralph/agent/scratchpad.md     # Scratchpad file path
  specs_dir: "./specs/"                  # Specifications directory
  guardrails:                            # Rules injected into every prompt
    - "Fresh context each iteration"
    - "Never modify production database"

# Memories — persistent learning
memories:
  enabled: true                          # Enable memory system
  inject: auto                           # auto, manual, none
  budget: 2000                           # Max tokens to inject
  filter:
    types: []                            # Filter by memory type
    tags: []                             # Filter by tags
    recent: 0                            # Days limit (0 = no limit)

# Tasks — runtime work tracking
tasks:
  enabled: true                          # Enable task system

# Optional features
features:
  parallel: true                         # Allow worktree loops
  auto_merge: false                      # Auto-merge worktree loops
  preflight:
    enabled: false                       # Run preflight on ralph run
    strict: false                        # Treat warnings as failures
    skip: []                             # Skip checks by name

# Lifecycle hooks (v1)
hooks:
  enabled: false
  defaults:
    timeout_seconds: 30
    max_output_bytes: 8192
    suspend_mode: wait_for_resume
  events:
    pre.loop.start:
      - name: env-guard
        command: ["./scripts/hooks/env-guard.sh"]
        on_error: block

# Hats — specialized personas
hats:
  my_hat:
    name: "My Hat"                       # Display name (required)
    description: "Purpose"               # Optional
    triggers: ["event.*"]                # Subscription patterns (required)
    publishes: ["event.done"]            # Allowed event types (required)
    default_publishes: "event.done"      # Default when no explicit emit
    max_activations: 10                  # Activation limit
    backend: "claude"                    # Backend override
    scratchpad: .ralph/agent/my-hat.md   # Per-hat scratchpad
    instructions: |                      # Hat-specific prompt (required)
      Instructions here...
```

## Section Details

### event_loop

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `completion_promise` | string | `"LOOP_COMPLETE"` | Output text that ends the loop |
| `max_iterations` | integer | `100` | Maximum iterations before stopping |
| `max_runtime_seconds` | integer | `14400` | Maximum runtime (4 hours) |
| `idle_timeout_secs` | integer | `1800` | Idle timeout (30 minutes) |
| `starting_event` | string | `null` | First event (enables hat mode) |
| `checkpoint_interval` | integer | `5` | Git checkpoint frequency |
| `prompt_file` | string | `"PROMPT.md"` | Default prompt file |

### cli

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backend` | string | auto-detect | Backend name |
| `prompt_mode` | string | `"arg"` | How prompt is passed |

Backend values: `claude`, `kiro`, `gemini`, `codex`, `amp`, `copilot`, `opencode`, `pi`, `custom`.

Prompt mode values: `arg` (pass as CLI argument), `stdin` (pass via stdin pipe).

### core

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `scratchpad` | string or object | `{ enabled: true, path: ".ralph/agent/scratchpad.md" }` | Scratchpad config |
| `specs_dir` | string | `"./specs/"` | Specifications directory |
| `guardrails` | list | `[]` | Rules injected into every prompt |

Scratchpad accepts a plain string (shorthand for path with enabled=true) or structured object with `enabled` and `path`.

### memories

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable memory system |
| `inject` | string | `"auto"` | Injection mode (auto, manual, none) |
| `budget` | integer | `2000` | Max tokens to inject |
| `filter.types` | list | `[]` | Filter by memory type |
| `filter.tags` | list | `[]` | Filter by tags |
| `filter.recent` | integer | `0` | Days limit (0 = no limit) |

### tasks

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable task system |

### features

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `parallel` | boolean | `true` | Spawn worktree loops when primary lock held |
| `auto_merge` | boolean | `false` | Auto-merge completed worktree loops |
| `preflight.enabled` | boolean | `false` | Run preflight on `ralph run` |
| `preflight.strict` | boolean | `false` | Treat warnings as failures |
| `preflight.skip` | list | `[]` | Skip checks by name |

### hooks (Lifecycle Hooks v1)

Hooks execute external commands at orchestrator phase-events. Supported phase-event keys:

- `pre.loop.start`, `post.loop.start`
- `pre.iteration.start`, `post.iteration.start`
- `pre.plan.created`, `post.plan.created`
- `pre.human.interact`, `post.human.interact`
- `pre.loop.complete`, `post.loop.complete`
- `pre.loop.error`, `post.loop.error`

Hook spec fields:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Stable identifier for telemetry |
| `command` | Yes | Command argv array |
| `cwd` | No | Working directory override |
| `env` | No | Environment variable overrides |
| `timeout_seconds` | No | Per-hook timeout override |
| `max_output_bytes` | No | Output cap per stream |
| `on_error` | Yes | `warn`, `block`, or `suspend` |
| `suspend_mode` | No | Suspend strategy (`wait_for_resume`, `retry_backoff`, `wait_then_retry`) |
| `mutate.enabled` | No | Opt-in stdout mutation parsing |

Validate hooks config: `ralph hooks validate -c ralph.yml`

## CLI Config Sources

### `-c` (Core Config)

```bash
ralph run -c ralph.yml                        # File path
ralph run -c https://example.com/ralph.yml    # Remote URL
ralph run -c core.scratchpad=.runs/task.md    # Field override
```

### `-H` (Hat Collection)

```bash
ralph run -c ralph.yml -H builtin:code-assist  # Built-in collection
ralph run -c ralph.yml -H hats/my-hats.yml     # Local file
ralph run -c ralph.yml -H https://example.com/hats.yml  # Remote
```

When both `-c` and `-H` are used, `-H` wins for workflow sections (`hats`, `events`, `event_loop` overrides). CLI field overrides (`-c core.*=...`) still apply last.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `RALPH_CONFIG` | Default config file path |
| `RALPH_DIAGNOSTICS` | Set to `1` to enable diagnostics |
| `NO_COLOR` | Disable color output |
| `RALPH_WAVE_WORKER` | Set to `1` inside wave workers |
| `RALPH_WAVE_ID` | Wave correlation ID |
| `RALPH_WAVE_INDEX` | 0-based worker index |
| `RALPH_EVENTS_FILE` | Per-worker events file path |

## Example Configurations

### Traditional Mode (Minimal)

```yaml
cli:
  backend: "claude"
event_loop:
  completion_promise: "LOOP_COMPLETE"
  max_iterations: 100
```

### Hat-Based Mode

```yaml
cli:
  backend: "claude"
event_loop:
  completion_promise: "LOOP_COMPLETE"
  max_iterations: 100
  starting_event: "task.start"

hats:
  planner:
    name: "Planner"
    triggers: ["task.start"]
    publishes: ["plan.ready"]
    instructions: "Create an implementation plan."

  builder:
    name: "Builder"
    triggers: ["plan.ready"]
    publishes: ["build.done"]
    instructions: |
      Implement the plan.
      Evidence required: tests pass, lint pass.
```

### With Memories and Tasks Disabled (Legacy)

```yaml
cli:
  backend: "claude"
event_loop:
  completion_promise: "LOOP_COMPLETE"

memories:
  enabled: false
tasks:
  enabled: false
```
