# Configuration

## Settings Files

JSON settings with project overriding global:

- Global: `~/.pi/agent/settings.json`
- Project: `.pi/settings.json` (overrides global, nested objects merge)

Edit directly or use `/settings` in interactive mode.

### Key Settings

**Model & Thinking:**
- `defaultProvider` — Default provider name
- `defaultModel` — Default model ID
- `defaultThinkingLevel` — `"off"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`
- `hideThinkingBlock` — Hide thinking blocks in output
- `thinkingBudgets` — Custom token budgets per level

**UI & Display:**
- `theme` — Theme name (`"dark"`, `"light"`, or custom)
- `quietStartup` — Hide startup header
- `collapseChangelog` — Show condensed changelog after updates
- `enableInstallTelemetry` — Anonymous install/update ping (default: true)
- `doubleEscapeAction` — `"tree"`, `"fork"`, or `"none"`
- `treeFilterMode` — Default `/tree` filter: `"default"`, `"no-tools"`, `"user-only"`, `"labeled-only"`, `"all"`
- `editorPaddingX` — Horizontal editor padding 0-3 (default: 0)
- `autocompleteMaxVisible` — Max autocomplete dropdown items 3-20 (default: 5)
- `showHardwareCursor` — Show terminal cursor

**Terminal & Images:**
- `terminal.showImages` — Show images in terminal (default: true)
- `terminal.imageWidthCells` — Inline image width in cells (default: 60)
- `terminal.clearOnShrink` — Clear empty rows on shrink (default: false)
- `images.autoResize` — Resize images to 2000x2000 max (default: true)
- `images.blockImages` — Block all images from LLM (default: false)

**Compaction:**
```json
{
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  }
}
```

**Retry:**
```json
{
  "retry": {
    "enabled": true,
    "maxRetries": 3,
    "baseDelayMs": 2000,
    "provider": { "timeoutMs": 3600000, "maxRetries": 0, "maxRetryDelayMs": 60000 }
  }
}
```

**Message Delivery:**
- `steeringMode` — `"one-at-a-time"` (default) or `"all"`
- `followUpMode` — `"one-at-a-time"` (default) or `"all"`
- `transport` — `"sse"`, `"websocket"`, or `"auto"`

**Shell:**
- `shellPath` — Custom shell path
- `shellCommandPrefix` — Prefix for every bash command
- `npmCommand` — Command argv for npm operations (e.g., `["mise", "exec", "node@20", "--", "npm"]`)

**Resources:**
- `packages` — npm/git packages to load
- `extensions` — Local extension paths
- `skills` — Local skill paths
- `prompts` — Local prompt template paths
- `themes` — Local theme paths
- `enableSkillCommands` — Register skills as `/skill:name` (default: true)

**Sessions:**
- `sessionDir` — Custom session storage directory
- Environment: `PI_CODING_AGENT_SESSION_DIR` (new in 0.71.0, same as `--session-dir`)
- Precedence: `--session-dir` > `PI_CODING_AGENT_SESSION_DIR` > `sessionDir` in settings.json

**Model Cycling:**
- `enabledModels` — Model patterns for Ctrl+P cycling (e.g., `["claude-*", "gpt-4o"]`)

## Keybindings

Customize via `~/.pi/agent/keybindings.json`. Uses namespaced keybinding ids:

```json
{
  "tui.editor.cursorUp": ["up", "ctrl+p"],
  "tui.editor.cursorDown": ["down", "ctrl+n"],
  "app.model.select": ["ctrl+l"],
  "app.tools.expand": ["ctrl+o"]
}
```

Key format: `modifier+key` where modifiers are `ctrl`, `shift`, `alt`. Run `/reload` after editing.

### Namespaced Keybinding IDs

- TUI editor: `tui.editor.*` — cursor movement, deletion, kill ring
- TUI input: `tui.input.*` — newLine, submit, tab, copy
- TUI select: `tui.select.*` — up, down, confirm, cancel
- Application: `app.*` — interrupt, clear, exit, suspend, editor.external
- Sessions: `app.session.*` — new, tree, fork, resume, rename, delete
- Models: `app.model.*` — select, cycleForward, cycleBackward
- Thinking: `app.thinking.*` — cycle, toggle
- Tools: `app.tools.expand`
- Messages: `app.message.followUp`, `app.message.dequeue`
- Tree: `app.tree.*` — fold/unfold, filter modes, label editing

Use these ids in extensions with `keyHint("app.tools.expand", "to expand")`.

## Context Files

Pi loads `AGENTS.md` (or `CLAUDE.md`) from:
- `~/.pi/agent/AGENTS.md` (global)
- Parent directories walking up from cwd
- Current directory

All matching files are concatenated. Disable with `--no-context-files` (`-nc`).

Replace default system prompt with `.pi/SYSTEM.md` (project) or `~/.pi/agent/SYSTEM.md` (global). Append without replacing via `APPEND_SYSTEM.md`.

## Prompt Templates

Markdown snippets that expand into full prompts. Type `/name` to invoke.

Locations:
- Global: `~/.pi/agent/prompts/*.md`
- Project: `.pi/prompts/*.md`
- Packages: `prompts/` directories
- CLI: `--prompt-template <path>` (repeatable)

```markdown
<!-- ~/.pi/agent/prompts/review.md -->
---
description: Review staged git changes
argument-hint: "<focus>"
---
Review the staged changes (`git diff --cached`). Focus on: $@
```

Usage: `/review bugs security`

Arguments: `$1`, `$2` (positional), `$@` or `$ARGUMENTS` (all args), `${@:N}` (from Nth), `${@:N:L}` (L args from N).

## Skills

On-demand capability packages following the Agent Skills standard.

Locations:
- Global: `~/.pi/agent/skills/`, `~/.agents/skills/`
- Project: `.pi/skills/`, `.agents/skills/` (cwd and ancestors up to git root)
- Packages: `skills/` directories
- CLI: `--skill <path>` (repeatable)

Invoke via `/skill:name`. Discovery: in `~/.pi/agent/skills/` and `.pi/skills/`, direct root `.md` files are individual skills; all locations discover `SKILL.md` directories recursively.

## Themes

JSON files defining 51 color tokens. Hot-reload: edit active theme file and pi immediately applies changes.

Locations:
- Built-in: `dark`, `light`
- Global: `~/.pi/agent/themes/*.json`
- Project: `.pi/themes/*.json`
- Packages: `themes/` directories
- CLI: `--theme <path>` (repeatable)

```json
{
  "$schema": "https://raw.githubusercontent.com/badlogic/pi-mono/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json",
  "name": "my-theme",
  "vars": { "primary": "#00aaff", "secondary": 242 },
  "colors": {
    "accent": "primary",
    "border": "primary",
    "borderAccent": "#00ffff",
    "success": "#00ff00",
    "error": "#ff0000",
    "text": "",
    // ... all 51 tokens required
  }
}
```

Color values: hex (`"#ff0000"`), 256-color index (`39`), variable reference (`"primary"`), or default (`""`).

## Pi Packages

Bundle and share extensions, skills, prompts, and themes via npm or git. Add `pi-package` keyword for discoverability.

### Install/Manage

```bash
pi install npm:@foo/bar@1.0.0
pi install git:github.com/user/repo@v1
pi install https://github.com/user/repo
pi install /absolute/path/to/package

pi remove npm:@foo/bar
pi list
pi update                    # Update pi and packages (skips pinned)
pi update --extensions      # Packages only
pi update --self            # Pi only
pi config                   # Enable/disable resources
```

Use `-l` for project-local installs (`.pi/settings.json`).

### Package Structure

```json
{
  "name": "my-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

Without `pi` manifest, pi auto-discovers from conventional directories (`extensions/`, `skills/`, `prompts/`, `themes/`).

### Dependencies

Runtime dependencies in `dependencies` of `package.json`. Pi bundles core packages — list them as `peerDependencies` with `"*"` range: `@mariozechner/pi-ai`, `@mariozechner/pi-agent-core`, `@mariozechner/pi-coding-agent`, `@mariozechner/pi-tui`, `typebox`.

### Package Filtering

```json
{
  "packages": [
    "npm:simple-pkg",
    {
      "source": "npm:my-package",
      "extensions": ["extensions/*.ts", "!extensions/legacy.ts"],
      "skills": [],
      "prompts": ["prompts/review.md"]
    }
  ]
}
```

## CLI Reference

```bash
pi [options] [@files...] [messages...]

# Modes
pi -p "prompt"                    # Print mode (non-interactive)
pi --mode json "prompt"           # JSON event stream
pi --mode rpc                     # RPC mode

# Model options
pi --provider openai --model gpt-4o "help"
pi --model openai/gpt-4o "help"   # Provider prefix
pi --model sonnet:high "solve"    # Thinking shorthand

# Session
pi -c                             # Continue recent
pi -r                             # Resume picker
pi --session <path|id>            # Specific session
pi --fork <path|id>               # Fork session

# Resources
pi -e ./ext.ts                    # Load extension
pi --no-extensions                # Disable extensions
pi --skill path/to/SKILL.md       # Load skill
pi --no-skills                    # Disable skills

# Tools
pi --tools read,grep,find,ls -p "review"   # Read-only mode
pi --no-builtin-tools -e ./my-ext.ts       # Extension tools only
pi --no-tools                          # No tools

# File arguments
pi @prompt.md "Answer this"
pi -p @screenshot.png "What's in this image?"
```

### Environment Variables

- `PI_CODING_AGENT_DIR` — Override config directory (default: `~/.pi/agent`)
- `PI_SKIP_VERSION_CHECK` — Skip version check at startup
- `PI_TELEMETRY` — `0` to disable install telemetry
- `PI_CACHE_RETENTION` — Set to `long` for extended prompt cache
- `VISUAL`, `EDITOR` — External editor for Ctrl+G
