# Configuration

## Configuration Files

uv searches for configuration in this order:

1. **Project-level** — `pyproject.toml` (under `[tool.uv]`) or `uv.toml` in current/parent directories
2. **User-level** — `~/.config/uv/uv.toml` (macOS/Linux) or `%APPDATA%\uv\uv.toml` (Windows)
3. **System-level** — `/etc/uv/uv.toml` (macOS/Linux) or `%PROGRAMDATA%\uv\uv.toml` (Windows)

`uv.toml` takes precedence over `pyproject.toml` in the same directory. Settings merge with project-level taking highest priority. Environment variables take precedence over files; command-line flags take precedence over everything.

For `uv tool` commands, only user- and system-level configuration are read (no local files).

In workspaces, uv begins search at workspace root — member-level configuration is ignored.

### pyproject.toml Configuration

```toml
[tool.uv]
index-url = "https://test.pypi.org/simple"
```

### uv.toml Configuration

Same structure without `[tool.uv]` prefix:

```toml
index-url = "https://test.pypi.org/simple"
```

User- and system-level configuration must use `uv.toml` format (not `pyproject.toml`).

### Disabling Configuration Discovery

```bash
uv sync --no-config          # Disable all config discovery
UV_NO_CONFIG=1 uv sync       # Via environment variable

# Use specific config file
uv sync --config-file /path/to/uv.toml
```

## Environment Variable Files

`uv run` loads dotenv files (`.env`, `.env.local`, `.env.development`):

```bash
echo "MY_VAR='Hello, world!'" > .env
uv run --env-file .env -- python -c 'import os; print(os.getenv("MY_VAR"))'
```

Disable with `UV_NO_ENV_FILE=1` or `--no-env-file`.

## pip-Specific Configuration

The `[tool.uv.pip]` section configures only `uv pip` subcommands:

```toml
[tool.uv.pip]
index-url = "https://test.pypi.org/simple"
```

This affects `uv pip install` but not `uv sync`, `uv lock`, or `uv run`.

## Key Settings

Common `[tool.uv]` settings:

- `managed = false` — Disable automatic project environment management
- `package = true/false` — Override whether project is built and installed
- `override-dependencies` — Override dependency versions workspace-wide
- `constraint-dependencies` — Apply version constraints without adding deps
- `environments` — Allow/deny specific Python environments
- `required-version` — Require minimum uv version
- `sources` — Alternative dependency sources
- `workspace.members` / `workspace.exclude` — Workspace member globs
- `cache-keys` — Custom cache invalidation keys for dynamic metadata
- `extra-build-dependencies` — Additional build dependencies
- `no-build-isolation-package` — Packages to build without isolation
- `reinstall-package` — Always rebuild and reinstall specific packages

See the settings reference at https://docs.astral.sh/uv/reference/settings/ for complete enumeration.
