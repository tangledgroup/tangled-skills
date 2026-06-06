# Caching and Configuration

## Contents
- Cache management
- Cache directory
- Refresh and reinstall flags
- CI caching
- Configuration files
- Environment variables

## Cache management

uv uses a global cache for dependency deduplication. Wheels, source distributions, and Git repositories are cached to avoid re-downloading.

```bash
# Clear entire cache
uv cache clean

# Clear cache for specific package
uv cache clean ruff

# Prune unused entries (safe to run periodically)
uv cache prune

# CI mode — remove pre-built wheels, keep source-built wheels
uv cache prune --ci
```

Cache is thread-safe and append-only. Multiple uv commands can run concurrently. Never modify the cache directory manually.

## Cache directory

Determined by (in order):

1. `--no-cache` — temporary directory for single invocation
2. `--cache-dir`, `UV_CACHE_DIR`, or `[tool.uv] cache-dir`
3. System default: `$XDG_CACHE_HOME/uv` / `~/.cache/uv` (Unix), `%LOCALAPPDATA%\uv\cache` (Windows)

uv always requires a cache directory. `--no-cache` still uses a temp cache internally. Prefer `--refresh` over `--no-cache` — it updates the cache for subsequent operations.

Place the cache on the same filesystem as the target environment for performance (linking instead of copying).

## Refresh and reinstall flags

| Flag | Effect |
|------|--------|
| `--refresh` | Revalidate all cached dependencies |
| `--refresh-package <pkg>` | Revalidate a specific package's cache |
| `--reinstall` | Ignore installed versions, reinstall everything |
| `--reinstall-package <pkg>` | Reinstall a specific package |

These apply to any command: `uv sync --refresh`, `uv pip install --refresh-package ruff`, etc.

## CI caching

In CI environments, persisting pre-built wheels is often slower than re-downloading. Caching source-built wheels is worthwhile since building is expensive.

Recommended pattern:
```bash
# At end of CI job
uv cache prune --ci
```

This removes pre-built wheels and unzipped source distributions, retaining only wheels built from source.

## Configuration files

uv reads configuration from (nearest to farthest):

1. `.uv.toml` in current directory or parent directories
2. User config directory: `$XDG_CONFIG_HOME/uv/uv.toml` or `~/.config/uv/uv.toml`

Disable with `--no-config`.

Example `.uv.toml`:
```toml
[python]
download = false

[pip]
index-url = "https://custom.index/simple"
```

### Project-level configuration

`pyproject.toml` `[tool.uv]` section for project-specific settings:

```toml
[tool.uv]
managed = false                  # Disable auto-lock/sync
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true } }]
reinstall-package = ["my-package"]  # Always rebuild
override-dependencies = ["requests>=2.31"]
constraint-dependencies = ["numpy<2"]
```

### Dynamic metadata cache keys

For projects with dynamic metadata (e.g., `setuptools-scm`), extend cache keys:

```toml
[tool.uv]
cache-keys = [
  { file = "pyproject.toml" },
  { git = { commit = true, tags = true } },
  { env = "MY_ENV_VAR" },
  { dir = "src" },
]
```

Globs supported: `{ file = "**/*.toml" }` (may be expensive on large directories).

## Environment variables

Key environment variables:

| Variable | Description |
|----------|-------------|
| `UV_CACHE_DIR` | Override cache directory |
| `UV_NO_CACHE` | Disable cache (use temp) |
| `UV_PYTHON_DOWNLOADS` | `automatic` (default), `never` |
| `UV_NO_MODIFY_PATH` | Skip PATH modification on self-update |
| `UV_LOCK_TIMEOUT` | Cache lock timeout (default 5min) |
| `UV_INDEX_URL` | Default package index URL |
| `UV_EXTRA_INDEX_URL` | Additional index URLs |
| `UV_PROJECT_ENVIRONMENT` | Override `.venv` path |

Full list: run `uv help` or see uv's environment documentation.

## Indexes

uv supports multiple package indexes:

```bash
# Custom primary index
uv pip install --index-url https://custom.index/simple flask

# Additional index
uv pip install --extra-index-url https://wheels.internal/simple flask
```

In configuration:
```toml
[pip]
index-url = "https://custom.index/simple"
extra-index-url = ["https://wheels.internal/simple"]
```

Per-project in `pyproject.toml`:
```toml
[tool.uv.index]
url = "https://custom.index/simple"
```
