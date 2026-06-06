# Projects

## Contents
- Creating projects
- Adding dependencies
- Running commands
- Locking and syncing
- Project layout
- Workspaces

## Creating projects

`uv init` creates a new project with `pyproject.toml`, `.python-version`, and sample files.

```bash
# Application (default) — no build system, files at root
uv init my-app
# Produces: pyproject.toml, main.py, README.md, .python-version

# Library — src layout with __init__.py
uv init --lib my-lib
# Produces: pyproject.toml, src/my_lib/__init__.py, README.md, .python-version

# Packaged application — has build system and entry point
uv init --package my-cli
```

Application `pyproject.toml` (no build system, not installed as a package):

```toml
[project]
name = "my-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []
```

Packaged application adds `[build-system]` and `[project.scripts]`:

```toml
[project.scripts]
my-cli = "my_cli:main"

[build-system]
requires = ["uv_build>=0.11.19,<0.12"]
build-backend = "uv_build"
```

## Adding dependencies

`uv add` updates `pyproject.toml`, creates/updates `.venv`, and refreshes `uv.lock`:

```bash
# Add a package
uv add requests

# Add with version constraint
uv add 'requests>=2.28'

# Add dev dependency (goes to [dependency-groups])
uv add --dev pytest

# Add optional dependency (extra)
uv add --optional docs sphinx

# Add from Git
uv add "ruff @ git+https://github.com/astral-sh/ruff"

# Add workspace member as dependency
uv add bird-feeder --workspace
```

Remove with `uv remove <package>`. Edit `pyproject.toml` directly and run `uv lock` to update.

## Running commands

`uv run` ensures the environment is up-to-date, then executes the command:

```bash
# Run a Python file
uv run main.py

# Run a module
uv run -m http.server

# Run an installed script
uv run my-cli --arg

# Run with extra one-off dependency
uv run --with httpx python test.py

# Run without syncing environment (faster, skip update check)
uv run --no-sync python main.py

# Run in exact mode (remove extraneous packages)
uv run --exact python main.py

# Run a specific workspace member
uv run --package bird-feeder python -c "import bird_feeder"
```

## Locking and syncing

Locking resolves dependencies into `uv.lock`. Syncing installs from lockfile into `.venv`.

```bash
# Explicit lock (auto-done by uv run/sync)
uv lock

# Check lockfile is up-to-date
uv lock --check

# Upgrade all packages to latest within constraints
uv lock --upgrade

# Upgrade a single package
uv lock --upgrade-package requests

# Sync environment from lockfile
uv sync

# Sync without dev dependencies
uv sync --no-dev

# Sync with optional extras
uv sync --extra docs --extra test

# Sync all extras
uv sync --all-extras

# Exact sync (default) removes extraneous packages
# Inexact sync retains them
uv sync --inexact
```

### Export formats

```bash
# Export to requirements.txt
uv export --format requirements.txt

# Export to pylock.toml (PEP 751)
uv export --format pylock.toml

# Export to CycloneDX SBOM
uv export --format cyclonedx1.5
```

## Project layout

A uv project has three key files:

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, build system |
| `.venv/` | Virtual environment (auto-created, gitignored) |
| `uv.lock` | Universal lockfile (check into VCS) |

The `.venv` is created next to `pyproject.toml`. Do not modify it manually — use `uv add` for project dependencies or `uv run --with` for one-off needs.

Disable automatic management:

```toml
[tool.uv]
managed = false
```

### Dependency groups (PEP 735)

```toml
[dependency-groups]
dev = ["pytest", "ruff"]
docs = ["sphinx"]
```

- `dev` group is synced by default
- `uv sync --no-dev` excludes it
- `uv sync --group docs` includes a specific group
- `uv sync --all-groups` includes all groups

### Optional dependencies (extras)

```toml
[project.optional-dependencies]
docs = ["sphinx>=7"]
test = ["pytest>=8"]
```

## Workspaces

Workspaces group multiple packages under a single lockfile, inspired by Cargo.

```toml
# Root pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/seeds"]

[tool.uv.sources]
bird-feeder = { workspace = true }
```

Key behaviors:

- Single `uv.lock` for all members
- `uv run` and `uv sync` operate on workspace root by default
- `uv run --package <name>` targets a specific member
- Dependencies between members use `workspace = true` in `[tool.uv.sources]`
- All inter-member dependencies are editable
- Root `[tool.uv.sources]` applies to all members unless overridden
- Single `requires-python` enforced across workspace (intersection of all members)

When not to use workspaces:
- Members have conflicting requirements
- Each member needs separate virtual environment
- Use path dependencies instead: `bird-feeder = { path = "packages/bird-feeder" }`
