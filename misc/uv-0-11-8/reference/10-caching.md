# Caching

## Dependency Caching

uv uses aggressive caching to avoid re-downloading and re-building dependencies:

- **Registry dependencies** — Respects HTTP caching headers
- **Direct URL dependencies** — HTTP headers + URL-based caching
- **Git dependencies** — Cached by fully-resolved commit hash
- **Local dependencies** — Cached by last-modified time of source archive or `pyproject.toml`/`setup.py`/`setup.cfg`

## Cache Escape Hatches

```bash
# Clear entire cache
uv cache clean

# Clear specific package
uv cache clean ruff

# Force revalidation for all dependencies
uv sync --refresh
uv pip install --refresh ...

# Force revalidation for specific dependency
uv sync --refresh-package ruff
uv pip install --refresh-package ruff ...

# Force reinstall (ignore installed versions)
uv sync --reinstall
uv pip install --reinstall ...
```

## Dynamic Metadata

By default, uv rebuilds local directory dependencies only if `pyproject.toml`, `setup.py`, or `setup.cfg` changes. Customize cache keys:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true } }]
```

Include Git tags:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true, tags = true } }]
```

Include additional files:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { file = "requirements.txt" }]
```

Globs are supported:

```toml
[tool.uv]
cache-keys = [{ file = "**/*.toml" }]
```

Environment variables:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { env = "MY_ENV_VAR" }]
```

Directory presence:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { dir = "src" }]
```

Always rebuild (escape hatch):

```toml
[tool.uv]
reinstall-package = ["my-package"]
```

## Cache Safety

uv's cache is thread-safe and append-only. Multiple concurrent uv commands are safe. A file-based lock prevents concurrent modifications to the target virtual environment.

Never modify the cache directly (e.g., removing files manually).

## Clearing the Cache

```bash
# Remove all entries
uv cache clean

# Remove specific package
uv cache clean ruff

# Remove unused entries (safe for periodic cleanup)
uv cache prune
```

Cache-modifying commands have a 5-minute timeout waiting for other uv processes. Change with `UV_LOCK_TIMEOUT`. Use `--force` to ignore the lock when no other processes are active.

## Caching in CI

uv caches both built wheels and pre-built downloads. The cache directory is at `$XDG_CACHE_HOME/uv` or `$HOME/.cache/uv` on macOS/Linux, `%LOCALAPPDATA%\uv\cache` on Windows.

For Docker layer caching, use partial installations:

```dockerfile
# Layer 1: Install dependencies (cached unless pyproject.toml changes)
COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-install-project

# Layer 2: Copy project and install
COPY . .
RUN uv sync --frozen
```
