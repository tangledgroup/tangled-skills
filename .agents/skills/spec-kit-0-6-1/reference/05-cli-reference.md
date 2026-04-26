# CLI Reference

## `specify` Command Overview

The `specify` CLI is the entry point for Spec Kit. It bootstraps projects, manages extensions and presets, and provides utility commands.

```bash
specify <command> [options]
```

## Core Commands

### `specify init`

Bootstrap a new Spec Kit project or initialize in an existing directory.

```bash
# New project directory
specify init <PROJECT_NAME>

# Current directory
specify init .

# With --here flag (same as .)
specify init --here

# Specify integration
specify init my-project --integration claude
specify init my-project --integration copilot
specify init my-project --integration gemini
specify init my-project --integration codex
specify init my-project --integration pi

# Skills mode (installs agent skills instead of slash commands)
specify init my-project --integration codex --integration-options="--skills"

# Force merge into non-empty directory
specify init . --force --integration copilot

# Skip git initialization
specify init my-project --no-git

# Specify script type
specify init my-project --script sh    # POSIX shell
specify init my-project --script ps    # PowerShell

# Ignore agent tools check
specify init my-project --ignore-agent-tools
```

**Flags:**

- `--integration <agent>` — Specify AI coding agent (claude, copilot, gemini, codex, pi, etc.)
- `--integration-options "<opts>"` — Pass options to the integration (e.g., `"--skills"`)
- `--force` — Skip confirmation for non-empty directories; overwrite shared infrastructure files
- `--no-git` — Skip git repository initialization
- `--script sh|ps` — Force script type (auto-detected by OS otherwise)
- `--ignore-agent-tools` — Skip checking for installed agent tools

### `specify version`

Show the installed Spec Kit version.

```bash
specify version
```

### `specify check`

Verify installed tools and confirm the CLI is working.

```bash
specify check
```

### `specify integration list`

List all available agent integrations.

```bash
specify integration list
```

## Extension Commands

```bash
# Search
specify extension search
specify extension search <keyword>
specify extension search --tag <tag>
specify extension search --author "<author>"
specify extension search --verified

# Info
specify extension info <extension-name>

# Install
specify extension add <name>
specify extension add <name> --from <url>
specify extension add --dev /path/to/extension

# Manage
specify extension list
specify extension update
specify extension update <name>
specify extension disable <name>
specify extension enable <name>
specify extension remove <name>
specify extension remove <name> --keep-config
specify extension remove <name> --force

# Catalogs
specify extension catalog list
specify extension catalog add --name "<name>" --priority <N> [--install-allowed] <url>
specify extension catalog remove <name>
```

## Preset Commands

```bash
# Search
specify preset search
specify preset search <keyword>

# Install
specify preset add <name>
specify preset add --dev /path/to/preset

# Manage
specify preset list
specify preset info <name>
specify preset resolve <template-name>
specify preset remove <name>
```

## Directory Structure

After `specify init`, your project contains:

```text
my-project/
├── .specify/
│   ├── templates/              # Core templates (specs, plans, tasks)
│   │   └── overrides/          # Project-local template overrides
│   ├── scripts/                # Automation scripts (.sh and .ps1 variants)
│   ├── memory/                 # Shared project memory
│   │   └── constitution.md     # Governing principles
│   ├── presets/                # Installed preset templates
│   │   └── templates/
│   ├── extensions/             # Installed extensions
│   │   └── <ext-name>/
│   ├── extensions.yml          # Project-wide extension settings
│   └── extension-catalogs.yml  # Catalog configuration
│
├── specs/                      # Feature specifications (never touched by upgrades)
│   └── <feature-number>-<name>/
│       ├── spec.md             # Feature specification
│       ├── plan.md             # Implementation plan
│       ├── tasks.md            # Task list
│       ├── research.md         # Technical research
│       ├── data-model.md       # Data models
│       ├── contracts/          # API contracts
│       └── quickstart.md       # Validation scenarios
│
├── .claude/                    # Claude Code integration (if applicable)
│   └── commands/               # Slash command files
├── .github/                    # GitHub/Copilot integration
├── .gemini/                    # Gemini CLI integration
└── ...                         # Other agent directories
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPECKIT_CATALOG_URL` | Override the full catalog stack with a single URL | Built-in default stack |
| `GH_TOKEN` / `GITHUB_TOKEN` | GitHub token for authenticated requests to private repos | None |
| `SPECIFY_FEATURE` | Active feature directory (required when using `--no-git`) | Detected from git branch |
| `SPECKIT_{EXT_ID}_*` | Extension-specific configuration overrides | Extension defaults |

## Upgrade Guide

### Upgrade CLI Tool

```bash
# uv tool install users
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@vX.Y.Z

# pipx users
pipx install --force git+https://github.com/github/spec-kit.git@vX.Y.Z
```

### Update Project Files

```bash
specify init --here --force --integration <your-agent>
```

This updates:
- Slash command files (`.claude/commands/`, `.github/prompts/`, etc.)
- Script files (`.specify/scripts/`) — only with `--force`
- Template files (`.specify/templates/`) — only with `--force`
- Shared memory files (`.specify/memory/`)

**What stays safe:** Your `specs/` directory is completely excluded from template packages and will never be modified during upgrades.

### Known Issue: Constitution Overwrite

`specify init --here --force` overwrites `.specify/memory/constitution.md` with the default template. Workaround:

```bash
# Back up before upgrade
cp .specify/memory/constitution.md /tmp/constitution-backup.md

# Run upgrade
specify init --here --force --integration copilot

# Restore
mv /tmp/constitution-backup.md .specify/memory/constitution.md
```

Or use git: `git restore .specify/memory/constitution.md`

## Enterprise / Air-Gapped Installation

For environments without internet access:

```bash
# Step 1: On a connected machine (same OS and Python version)
git clone https://github.com/github/spec-kit.git
cd spec-kit
pip install build
python -m build --wheel --outdir dist/
pip download -d dist/ dist/specify_cli-*.whl

# Step 2: Transfer dist/ to air-gapped machine

# Step 3: Install offline
pip install --no-index --find-links=./dist specify-cli

# Step 4: Initialize (no network needed)
specify init my-project --integration claude
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: typer` | Run `uv pip install -e .` |
| Scripts not executable (Linux) | Re-run init or `chmod +x scripts/*.sh` |
| Git step skipped | You passed `--no-git` or Git not installed |
| Wrong script type | Pass `--script sh` or `--script ps` explicitly |
| Slash commands not showing after upgrade | Restart your IDE/agent to reload command files |
| Duplicate slash commands in IDE | Manually delete old command files from agent folder |
| TLS errors on corporate network | Configure certificate store or proxy (`SSL_CERT_FILE`, `HTTPS_PROXY`) |

> **Note:** The `--skip-tls` flag is deprecated and has no effect.

## Local Development

For iterating on the `specify` CLI itself:

```bash
# Run directly from source
python -m src.specify_cli --help
python -m src.specify_cli init demo-project --integration claude --ignore-agent-tools

# Editable install
uv venv && source .venv/bin/activate
uv pip install -e .
specify --help

# uvx from local path
uvx --from . specify init demo-uvx --integration copilot --ignore-agent-tools
```
