# Coding Agent — Interactive Mode, Commands, Sessions

## Contents
- Interface Layout
- Editor Features
- Slash Commands
- Keyboard Shortcuts
- Message Queue (Steering / Follow-up)
- Sessions and Branching
- Compaction
- Settings
- Context Files and System Prompt
- CLI Reference

## Interface Layout

Top to bottom:
- **Startup header** — Shortcuts (`/hotkeys`), loaded AGENTS.md files, prompt templates, skills, extensions
- **Messages** — User prompts, assistant responses, tool calls/results, notifications, errors
- **Editor** — Input area; border color indicates thinking level
- **Footer** — Working directory, session name, token/cache usage, cost, context usage, current model

Extensions can replace the editor, add widgets above/below it, custom status line, footer, or overlays.

## Editor Features

| Feature | How |
|---------|-----|
| File reference | Type `@` to fuzzy-search project files |
| Path completion | Tab to complete paths |
| Multi-line | Shift+Enter (Ctrl+Enter on Windows Terminal) |
| Images | Ctrl+V to paste (Alt+V on Windows), or drag onto terminal |
| Bash commands | `!command` runs and sends output to LLM, `!!command` runs without sending |

## Slash Commands

Type `/` in the editor to trigger commands. Extensions can register custom commands, skills are available as `/skill:name`, prompt templates expand via `/templatename`.

| Command | Description |
|---------|-------------|
| `/login`, `/logout` | OAuth authentication |
| `/model` | Switch models |
| `/scoped-models` | Enable/disable models for Ctrl+P cycling |
| `/settings` | Thinking level, theme, message delivery, transport |
| `/resume` | Pick from previous sessions |
| `/new` | Start a new session |
| `/name <text>` | Set session display name |
| `/session` | Show session info (file, ID, messages, tokens, cost) |
| `/tree` | Jump to any point in session and continue from there |
| `/fork` | Create new session from a previous user message |
| `/clone` | Duplicate current active branch into new session |
| `/compact [prompt]` | Manually compact context, optional custom instructions |
| `/copy` | Copy last assistant message to clipboard |
| `/export [file]` | Export session to HTML file |
| `/share` | Upload as private GitHub gist with shareable HTML link |
| `/reload` | Reload keybindings, extensions, skills, prompts, context files |
| `/hotkeys` | Show all keyboard shortcuts |
| `/changelog` | Display version history |
| `/quit` | Quit pi |

## Keyboard Shortcuts

Customize via `~/.pi/agent/keybindings.json`.

| Key | Action |
|-----|--------|
| Ctrl+C | Clear editor |
| Ctrl+C twice | Quit |
| Escape | Cancel/abort |
| Escape twice | Open `/tree` |
| Ctrl+L | Open model selector |
| Ctrl+P / Shift+Ctrl+P | Cycle scoped models forward/backward |
| Shift+Tab | Cycle thinking level |
| Ctrl+O | Collapse/expand tool output |
| Ctrl+T | Collapse/expand thinking blocks |

## Message Queue (Steering / Follow-up)

Submit messages while the agent is working:
- **Enter** — Queues a *steering* message, delivered after current assistant turn finishes executing tool calls
- **Alt+Enter** — Queues a *follow-up* message, delivered only after agent finishes all work
- **Escape** — Aborts and restores queued messages to editor
- **Alt+Up** — Retrieves queued messages back to editor

Configure delivery in settings: `steeringMode` and `followUpMode` can be `"one-at-a-time"` (default, waits for response) or `"all"` (delivers all queued at once). `transport` selects provider transport preference (`"sse"`, `"websocket"`, or `"auto"`).

## Sessions and Branching

Sessions are JSONL files with tree structure. Each entry has `id` and `parentId`, enabling in-place branching without creating new files. Auto-save to `~/.pi/agent/sessions/` organized by working directory.

### Session Management

```bash
pi -c                              # Continue most recent session
pi -r                              # Browse and select from past sessions
pi --no-session                    # Ephemeral mode (don't save)
pi --session <file-or-uuid>        # Use specific session file or partial UUID
pi --fork <file-or-uuid>           # Fork existing session into new session
```

### `/tree` — Navigate Session Tree

Navigate in-place. Select any previous point, continue from there, switch between branches. All history preserved in single file.
- Search by typing, fold/unfold and jump between branches with Ctrl+←/Ctrl+→ or Alt+←/Alt+→
- Filter modes (Ctrl+O): default → no-tools → user-only → labeled-only → all
- Press Shift+L to label entries as bookmarks, Shift+T to toggle label timestamps

### `/fork` — Create New Session from Previous Message

Opens selector, copies active path up to selected point, places prompt in editor for modification.

### `/clone` — Duplicate Current Branch

Duplicates current active branch into new session file at current position. Keeps full active-path history.

## Compaction

Long sessions can exhaust context windows. Compaction summarizes older messages while keeping recent ones.

- **Manual**: `/compact` or `/compact <custom instructions>`
- **Automatic**: Enabled by default. Triggers on context overflow (recovers and retries) or when approaching limit (proactive). Configure via `/settings` or `settings.json`.

Compaction is lossy. Full history remains in JSONL file; use `/tree` to revisit. Customize compaction behavior via extensions.

## Settings

Two locations, project overrides global:
- **Global**: `~/.pi/agent/settings.json`
- **Project**: `.pi/settings.json`

Use `/settings` in interactive mode for common options. See [Providers and Models](reference/02-providers-and-models.md) for provider-specific settings.

### Telemetry and Update Checks

- **Update check**: Fetches `https://pi.dev/api/latest-version`. Disable with `PI_SKIP_VERSION_CHECK=1`.
- **Install/update telemetry**: Sends anonymous version ping after first install or update. Opt out with `enableInstallTelemetry: false` in settings.json or `PI_TELEMETRY=0`.
- **Offline mode**: `--offline` or `PI_OFFLINE=1` disables all startup network operations.

## Context Files and System Prompt

Pi loads `AGENTS.md` (or `CLAUDE.md`) at startup from:
- `~/.pi/agent/AGENTS.md` (global)
- Parent directories walking up from cwd
- Current directory

All matching files are concatenated. Disable with `--no-context-files` (or `-nc`).

### System Prompt

Replace default system prompt with `.pi/SYSTEM.md` (project) or `~/.pi/agent/SYSTEM.md` (global). Append without replacing via `APPEND_SYSTEM.md`.

## CLI Reference

```bash
pi [options] [@files...] [messages...]
```

### Modes

| Flag | Description |
|------|-------------|
| (default) | Interactive mode |
| `-p`, `--print` | Print response and exit |
| `--mode json` | Output all events as JSON lines |
| `--mode rpc` | RPC mode for process integration |
| `--export <file> [out]` | Export session to HTML |

In print mode, pi reads piped stdin and merges into initial prompt:
```bash
cat README.md | pi -p "Summarize this text"
```

### Model Options

| Option | Description |
|--------|-------------|
| `--provider <name>` | Provider (anthropic, openai, google, etc.) |
| `--model <pattern>` | Model pattern or ID (supports `provider/id` and `:` shorthand) |
| `--api-key <key>` | API key (overrides env vars) |
| `--thinking <level>` | `off`, `minimal`, `low`, `medium`, `high`, `xhigh` |
| `--models <patterns>` | Comma-separated patterns for Ctrl+P cycling |
| `--list-models [search]` | List available models |

### Tool Options

| Option | Description |
|--------|-------------|
| `--tools <names>`, `-t <names>` | Allowlist specific tool names |
| `--no-builtin-tools`, `-nbt` | Disable built-in tools but keep extension/custom tools |
| `--no-tools`, `-nt` | Disable all tools |

Built-in tools: `read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`

### Resource Options

| Option | Description |
|--------|-------------|
| `-e`, `--extension <path>` | Load extension (repeatable) |
| `--no-extensions` | Disable extension discovery |
| `--skill <path>` | Load skill (repeatable) |
| `--no-skills` | Disable skill discovery |
| `--prompt-template <path>` | Load prompt template (repeatable) |
| `--no-prompt-templates` | Disable prompt template discovery |
| `--theme <path>` | Load theme (repeatable) |
| `--no-themes` | Disable theme discovery |
| `--no-context-files`, `-nc` | Disable AGENTS.md/CLAUDE.md discovery |

Combine `--no-*` with explicit flags to load exactly what you need, ignoring settings.json.

### File Arguments

Prefix files with `@` to include in the message:
```bash
pi @prompt.md "Answer this"
pi -p @screenshot.png "What's in this image?"
pi @code.ts @test.ts "Review these files"
```

### Package Commands

```bash
pi install <source> [-l]          # Install package, -l for project-local
pi remove <source> [-l]           # Remove package
pi update [source|self|pi]        # Update pi and packages
pi update --extensions            # Update packages only
pi update --self                  # Update pi only
pi list                           # List installed packages
pi config                         # Enable/disable package resources
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PI_CODING_AGENT_DIR` | Override config directory (default: `~/.pi/agent`) |
| `PI_CODING_AGENT_SESSION_DIR` | Override session storage directory |
| `PI_PACKAGE_DIR` | Override package directory |
| `PI_OFFLINE` | Disable startup network operations |
| `PI_SKIP_VERSION_CHECK` | Skip version update check |
| `PI_TELEMETRY` | Override install/update telemetry (`1`/`0`) |
| `PI_CACHE_RETENTION` | Set to `long` for extended prompt cache (Anthropic: 1h, OpenAI: 24h) |
| `VISUAL`, `EDITOR` | External editor for Ctrl+G |
