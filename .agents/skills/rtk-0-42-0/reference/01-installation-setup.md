# Installation & Setup

## Contents
- Name Collision Warning
- Pre-Installation Check
- Homebrew (recommended)
- Quick Install (Linux/macOS)
- Cargo
- Pre-built Binaries
- Verify Installation
- Project Initialization (`rtk init`)
- Uninstall

## Name Collision Warning

Two different projects are named "rtk":
1. **Rust Token Killer** (this project) — `rtk-ai/rtk` on GitHub, has `rtk gain` command
2. **Rust Type Kit** (`reachingforthejack/rtk`) — DIFFERENT PROJECT, a Rust codebase query tool

**Always verify with `rtk gain`** after any install. If it says "command not found" or "not a rtk command", you have the wrong package.

## Pre-Installation Check

```bash
# Check if RTK is already installed
rtk --version

# Verify it's the Token Killer (not Type Kit)
rtk gain
# Should show token savings stats, NOT "command not found"

# Check installation path
which rtk
```

If `rtk gain` works, skip to Project Initialization. If wrong RTK is installed:
```bash
cargo uninstall rtk
```

## Homebrew (recommended)

```bash
brew install rtk
```

## Quick Install (Linux/macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh
```

Installs to `~/.local/bin`. Add to PATH if needed:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
```

## Cargo

```bash
cargo install --git https://github.com/rtk-ai/rtk
```

⚠️ **Do NOT run `cargo install rtk`** — that pulls the wrong package (Rust Type Kit) from crates.io. Always use `--git`.

## Pre-built Binaries

Download from [releases](https://github.com/rtk-ai/rtk/releases):

| Platform | File |
|----------|------|
| macOS x86_64 | `rtk-x86_64-apple-darwin.tar.gz` |
| macOS arm64 | `rtk-aarch64-apple-darwin.tar.gz` |
| Linux x86_64 musl | `rtk-x86_64-unknown-linux-musl.tar.gz` |
| Linux x86_64 gnu | `rtk-aarch64-unknown-linux-gnu.tar.gz` |
| Windows | `rtk-x86_64-pc-windows-msvc.zip` |

**Windows users:** Extract and place `rtk.exe` in PATH. Run from Command Prompt, PowerShell, or Windows Terminal — do not double-click the `.exe`. For full hook support, use WSL.

## Verify Installation

```bash
rtk --version   # Should show "rtk 0.x.y"
rtk gain        # Should show token savings stats (or empty if no history)
```

## Project Initialization

`rtk init` installs hooks, rules files, or plugin configurations depending on your AI assistant.

### Global vs. Project-Local

```bash
rtk init --global       # All projects (recommended)
rtk init                # Current project only (local CLAUDE.md)
```

### Dry-Run Preview

```bash
rtk init --global --dry-run -v    # See what would change before writing
```

### By AI Assistant

| Assistant | Command | Method |
|-----------|---------|--------|
| Claude Code | `rtk init --global` | PreToolUse shell hook + settings.json patch |
| GitHub Copilot (VS Code) | `rtk init --global --copilot` | PreToolUse hook |
| GitHub Copilot CLI | `rtk init --global --copilot` | PreToolUse deny-with-suggestion |
| Cursor | `rtk init --global --cursor` | preToolUse hook |
| Gemini CLI | `rtk init --global --gemini` | BeforeTool hook |
| Pi | `rtk init --agent pi [--global]` | TypeScript extension (`.pi/extensions/rtk.ts`) |
| OpenCode | `rtk init --global --opencode` | TypeScript plugin (`tool.execute.before`) |
| OpenClaw | `openclaw plugins install ./openclaw` | TypeScript plugin (`before_tool_call`) |
| Hermes | `rtk init --agent hermes` | Python plugin adapter (terminal command mutation) |
| Cline / Roo Code | `rtk init --cline` | `.clinerules` (project-scoped rules) |
| Windsurf | `rtk init --windsurf` | `.windsurfrules` (project-scoped rules) |
| Codex CLI | `rtk init --codex` | Patches `AGENTS.md` |
| Kilo Code | `rtk init --agent kilocode` | `.kilocode/rules/rtk-rules.md` |
| Google Antigravity | `rtk init --agent antigravity` | `.agents/rules/antigravity-rtk-rules.md` |

### Verify Installation

```bash
rtk init --show    # Shows hook status and installed files
```

## Uninstall

```bash
# Remove hook/extension/rules
rtk init --uninstall              # default (Claude Code)
rtk init --uninstall --agent pi   # Pi extension

# Remove binary
cargo uninstall rtk               # if installed via cargo
brew uninstall rtk                # if installed via Homebrew
```
