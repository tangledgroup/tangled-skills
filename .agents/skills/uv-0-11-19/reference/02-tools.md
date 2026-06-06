# Tools

## Contents
- Running tools (uvx)
- Installing tools
- Tool versions
- Upgrading tools
- Additional dependencies
- Python versions for tools
- Tool executables and PATH

## Running tools (uvx)

`uvx` is an alias for `uv tool run`. It executes tools in ephemeral, cached virtual environments isolated from any project.

```bash
# Run a tool (auto-installs into cache)
uvx ruff check .

# Run with specific version
uvx ruff@0.6.0 check .

# Force latest version (bypass cache)
uvx ruff@latest check .

# Run isolated (ignore installed version and cache)
uvx --isolated ruff check .
```

Prefer `uvx` over `uv tool install` for most cases. Install only when the tool must be available on PATH for other programs (e.g., in Docker images or for uncontrolled scripts).

## Installing tools

`uv tool install` creates a persistent environment and symlinks executables into the tool executable directory (on PATH).

```bash
# Install latest version
uv tool install ruff

# Install specific version
uv tool install ruff==0.6.0
uv tool install ruff@0.6.0

# Install latest
uv tool install ruff@latest

# With version constraints
uv tool install 'black>=23,<24'

# Force overwrite existing executable
uv tool install --force ruff
```

List installed tools:
```bash
uv tool list
uv tool list --paths  # Show locations
```

Uninstall:
```bash
uv tool uninstall ruff
```

## Tool versions

- `uv tool install` installs latest unless version specified
- `uvx` uses latest on first invocation, then cached version
- `uvx <tool>@latest` forces latest, bypassing cache
- If a tool is installed, `uvx <tool>` uses the installed version
- `uvx --isolated <tool>` ignores installed version

## Upgrading tools

```bash
# Upgrade all packages in a tool environment
uv tool upgrade black

# Upgrade a specific package within the tool
uv tool upgrade black --upgrade-package click

# Reinstall during upgrade
uv tool upgrade black --reinstall
uv tool upgrade black --reinstall-package click
```

Upgrades respect original version constraints. To change constraints, reinstall: `uv tool install black>=24`.

## Additional dependencies

Include extra packages alongside a tool:

```bash
# Run with extra dependency
uvx --with httpx my-tool

# Short form
uvx -w httpx my-tool

# Specific version
uvx --with 'httpx==0.26.0' my-tool

# Install tool with extra dependencies
uv tool install --with httpx my-tool
```

### Executables from additional packages

`--with-executables-from` installs executables from extra packages too:

```bash
uv tool install --with-executables-from ansible-core,ansible-lint ansible
```

Difference from `--with`:
- `--with` adds dependency but not its executables
- `--with-executables-from` adds both dependency and executables

## Python versions for tools

Each tool environment uses a specific Python version. Tool environments ignore `.python-version` files and project `requires-python`.

```bash
# Install tool with specific Python
uv tool install ruff --python 3.12

# Run tool with specific Python
uvx --python 3.11 ruff check .
```

If the Python version used by a tool is uninstalled, the tool environment breaks.

## Tool executables and PATH

Tool executables are symlinked (Unix) or copied (Windows) into the tool executable directory. This directory must be on PATH.

```bash
# Add tool directory to shell PATH
uv tool update-shell
```

If PATH is not configured, uv displays a warning. Installation fails if an executable already exists (not from uv) — use `--force` to override.

### Relationship to uv run

`uvx <tool>` is nearly equivalent to:
```bash
uv run --no-project --with <tool> -- <tool>
```

Differences:
- No `--with` needed — package inferred from command name
- Cached in dedicated tool environment directory
- Always isolated from project (no `--no-project` needed)
- Uses installed version if tool is already installed

Use `uv run` instead of `uvx` when the tool should access the project (e.g., `pytest`, `mypy`).
