# Configuration

## Config Keys

Manage `gh` settings with `gh config`:

```bash
# List all configuration
gh config list

# Get a specific setting
gh config set editor vim
gh config get editor

# Set git protocol (ssh or https)
gh config set git_protocol ssh

# Set default browser
gh config set browser /usr/bin/firefox

# Enable color labels
gh config set color_labels enabled

# Enable accessible color palette
gh config set accessible_colors enabled

# Disable spinner
gh config set spinner disabled

# Clear cached data
gh config clear-cache
```

### Available Config Keys

**editor** — Default editor for interactive prompts (falls back to `GIT_EDITOR`, `VISUAL`, `EDITOR`)

**git_protocol** — Protocol for git operations: `https` (default) or `ssh`

**prompt** — Interactive prompt mode: `enabled` (default), `disabled`, or `prefer_editor_prompt`

**pager** — Pager for long output (falls back to `PAGER`, default `less`)

**browser** — Default browser for `--web` flag (falls back to `BROWSER`)

**color_labels** — Color-coded labels: `enabled` or `disabled` (default)

**accessible_colors** — Accessible color palette: `enabled` or `disabled` (default)

**spinner** — Activity spinner: `enabled` (default) or `disabled`

**telemetry** — Telemetry collection: `enabled` (default), `disabled`, or `log`

## Environment Variables

### Authentication

- **GH_TOKEN** / **GITHUB_TOKEN** — Personal access token for github.com
- **GH_ENTERPRISE_TOKEN** / **GITHUB_ENTERPRISE_TOKEN** — Token for GitHub Enterprise Server
- **GH_HOST** — Default GitHub hostname (overrides github.com)
- **GH_REPO** — Default repository in `[HOST/]OWNER/REPO` format

### Behavior

- **GH_EDITOR** — Override editor (`GIT_EDITOR`, `VISUAL`, `EDITOR` fallback chain)
- **GH_BROWSER** — Override browser (`BROWSER` fallback)
- **GH_PAGER** — Override pager (`PAGER` fallback, default `less`)
- **GLAMOUR_STYLE** — Style for markdown rendering
- **GH_PROMPT_DISABLED** — Disable interactive prompts
- **GH_PATH** — Override PATH for extension execution
- **GH_MDWIDTH** — Fixed width for markdown rendering (e.g., `pr view`)

### Debugging

- **GH_DEBUG** — Enable debug logging. Set to `api` for API request/response logging, or `1`/`true`/`yes` for general debug
- **DEBUG** — Alternative debug variable

### Display

- **NO_COLOR** — Disable all colors (set to any value)
- **CLICOLOR** — Force color output (`0` disables)
- **CLICOLOR_FORCE** — Force color even without TTY
- **GH_COLOR_LABELS** — Enable/disable colored labels
- **GH_ACCESSIBLE_COLORS** — Enable accessible color palette
- **GH_FORCE_TTY** — Force TTY output format
- **GH_SPINNER_DISABLED** — Disable activity spinner

### Updates and Extensions

- **GH_NO_UPDATE_NOTIFIER** — Suppress update notifications
- **GH_NO_EXTENSION_UPDATE_NOTIFIER** — Suppress extension update notifications

### Telemetry (v2.91)

- **GH_TELEMETRY** — Control telemetry: `log`, `false`, `0` to disable
- **DO_NOT_TRACK** — Standard opt-out: set to `true` or `1`

Telemetry is enabled by default in v2.91. It collects pseudonymous usage data to understand feature adoption. See `gh help telemetry` for details.

### Configuration Directory

- **GH_CONFIG_DIR** — Override config directory location
- Default locations:
  - Linux/macOS: `$XDG_CONFIG_HOME/gh` or `$HOME/.config/gh`
  - Windows: `$AppData/GitHub CLI`

### Accessibility

- **GH_ACCESSIBLE_PROMPTER** — Enable accessible prompter interface

## Shell Completion

Generate shell completion scripts:

```bash
# Bash
gh completion -s bash >> ~/.bashrc

# Zsh
gh completion -s zsh >> ~/.zshrc

# Fish
gh completion -s fish > ~/.config/fish/completions/gh.fish

# PowerShell
gh completion -s powershell > gh.ps1
```

## Help System

Access built-in documentation:

```bash
# General help
gh help

# Command-specific help
gh help pr
gh help pr create

# Reference topics
gh help environment    # Environment variables
gh help exit-codes     # Exit codes
gh help formatting     # Output formatting options
gh help reference      # Full command reference
gh help telemetry      # Telemetry details
```

## Preview Features

Enable experimental features:

```bash
gh preview
```

Check available preview features with `gh preview` commands.
