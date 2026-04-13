# Configuration

uv supports configuration through files, environment variables, and command-line arguments with a clear precedence order.

## Configuration Files

### File Types and Locations

uv searches for configuration in this order:

1. **Project-level**: `pyproject.toml` (in `[tool.uv]` section) or `uv.toml`
2. **User-level**: `~/.config/uv/uv.toml` (macOS/Linux) or `%APPDATA%\uv\uv.toml` (Windows)
3. **System-level**: `/etc/uv/uv.toml` (macOS/Linux) or `%PROGRAMDATA%\uv\uv.toml` (Windows)

### pyproject.toml Configuration

```toml
[tool.uv]
# Cache directory
cache-dir = "./.uv-cache"

# Python version preference
python-preference = "managed"

# Index configuration
[[tool.uv.index]]
url = "https://test.pypi.org/simple"
default = true

# Dependency configuration
exclude-newer = "2024-01-01T00:00:00Z"

# Build options
no-build = []
no-binary = []

# Resolution strategy
resolution = "highest"
```

### uv.toml Configuration

`uv.toml` uses the same structure but without `[tool.uv]` prefix:

```toml
# uv.toml (equivalent to [tool.uv] in pyproject.toml)
cache-dir = "./.uv-cache"
python-preference = "managed"

[[index]]
url = "https://test.pypi.org/simple"
default = true
```

### File Precedence

- `uv.toml` takes precedence over `pyproject.toml` in same directory
- Project-level overrides user-level, which overrides system-level
- Command-line arguments override all configuration files

### Disabling Configuration Files

```bash
# Disable all config file discovery
uv sync --no-config

# Use specific config file
uv sync --config-file ./custom-uv.toml
```

## Environment Variables

### Python Management

| Variable | Description | Example |
|----------|-------------|---------|
| `UV_PYTHON` | Path to Python interpreter | `/usr/bin/python3.12` |
| `UV_MANAGED_PYTHON` | Enable/disable managed Python | `1`, `0` |
| `UV_PYTHON_DOWNLOADS` | Auto-download behavior | `auto`, `manual`, `never` |
| `UV_NO_MANAGED_PYTHON` | Disable managed Python | `1` |

### Cache Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `UV_CACHE_DIR` | Custom cache directory | `~/.cache/uv` |
| `UV_NO_CACHE` | Disable caching | `1` |
| `UV_PRUNE` | Auto-prune cache | `1` |

### Index and Package Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `UV_INDEX_URL` | Default PyPI index URL | `https://test.pypi.org/simple` |
| `UV_EXTRA_INDEX_URL` | Additional index URLs | `url1 url2` |
| `UV_NO_INDEX` | Disable index lookup | `1` |
| `UV_FIND_LINKS` | Additional package sources | `./packages` |

### Build and Resolution

| Variable | Description | Example |
|----------|-------------|---------|
| `UV_NO_BUILD` | Packages to exclude from building | `pkg1 pkg2` |
| `UV_NO_BINARY` | Packages that must be built from source | `pkg1 pkg2` |
| `UV_RESOLUTION` | Resolution strategy | `highest`, `lowest`, `lowest-direct` |
| `UV_EXCLUDE_NEWER` | Exclude packages updated after date | `2024-01-01T00:00:00Z` |

### Environment Files (dotenv)

| Variable | Description | Example |
|----------|-------------|---------|
| `UV_ENV_FILE` | Path to .env file | `.env.local` |
| `UV_NO_ENV_FILE` | Disable dotenv loading | `1` |

### Behavior and Performance

| Variable | Description | Example |
|----------|-------------|---------|
| `UV_NATIVE_TLS` | Use native TLS instead of rustls | `1` |
| `UV_COMPILE_BYTECODE` | Compile to bytecode after install | `1` |
| `UV_LINK_MODE` | Link mode for installations | `clone`, `copy`, `hardlink` |
| `UV_LOCK_TIMEOUT` | Cache lock timeout (seconds) | `300` |
| `UV_NO_MODIFY_PATH` | Don't modify shell PATH on update | `1` |

### Using Environment Variables

```bash
# Set for single command
UV_INDEX_URL=https://test.pypi.org/simple uv pip install requests

# Set in shell session
export UV_PYTHON_DOWNLOADS=never
uv sync

# Multiple variables
UV_NO_CACHE=1 UV_RESOLUTION=highest uv lock
```

## Command-Line Configuration

### Precedence Order

Configuration is applied in this order (lowest to highest priority):

1. System-level configuration file (`/etc/uv/uv.toml`)
2. User-level configuration file (`~/.config/uv/uv.toml`)
3. Project-level configuration file (`pyproject.toml` or `uv.toml`)
4. Environment variables
5. Command-line arguments

### Common Command-Line Flags

```bash
# Cache control
uv sync --refresh           # Refresh all cached data
uv sync --refresh-package pkg  # Refresh specific package
uv sync --no-cache          # Disable cache entirely

# Python selection
uv sync --python 3.12       # Use specific Python version
uv sync --no-managed-python  # Don't use managed Python

# Index configuration
uv pip install --index-url https://test.pypi.org/simple requests
uv pip install --extra-index-url https://private.pypi.org/simple requests

# Build control
uv pip install --no-build package-name
uv pip install --no-binary :none:  # Force build from source

# Resolution strategy
uv lock --upgrade            # Upgrade all packages
uv lock --upgrade-package pkg  # Upgrade specific package
```

## Cache Configuration

### Cache Directory

```bash
# Show cache directory
uv cache dir

# Set custom cache directory
export UV_CACHE_DIR=./.uv-cache

# Or in config file
# [tool.uv]
# cache-dir = "./.uv-cache"
```

### Cache Management Commands

```bash
# Clean entire cache
uv cache clean

# Clean specific package
uv cache clean requests

# Prune unused entries
uv cache prune

# CI-optimized prune (keep built wheels)
uv cache prune --ci

# Force cleanup (ignore locks)
uv cache clean --force
```

### Cache Behavior

- **Registry dependencies**: Cached based on HTTP headers
- **Git dependencies**: Cached by commit hash
- **Local dependencies**: Cached by file modification time
- **Direct URLs**: Cached by URL and HTTP headers

## Index Configuration

### Default Index

```toml
# pyproject.toml
[tool.uv]
[[index]]
url = "https://test.pypi.org/simple"
default = true
verify = true
```

### Multiple Indices

```toml
[[tool.uv.index]]
url = "https://pypi.org/simple"

[[tool.uv.index]]
url = "https://test.pypi.org/simple"
default = true

[[tool.uv.index]]
url = "https://private.pypi.org/simple"
verify = false  # Disable SSL verification
```

### Index Priority

1. Explicit `--index-url` flag
2. Default index (`default = true`)
3. Extra indices in order defined
4. Built-in PyPI

## Project-Specific Configuration

### Dependency Sources

```toml
[tool.uv.sources]
# Use workspace package
my-library = { workspace = true }

# Use git repository
requests = { git = "https://github.com/psf/requests", rev = "v2.31.0" }

# Use local path
local-package = { path = "./local-package" }

# Use URL
custom-package = { url = "https://example.com/package.whl" }

# Platform-specific sources
windows-pkg = { path = "./windows", markers = "sys_platform == 'win32'" }
linux-pkg = { path = "./linux", markers = "sys_platform == 'linux'" }
```

### Dev Dependencies

```toml
[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.3",
]
```

### Cache Keys for Dynamic Metadata

```toml
[tool.uv]
cache-keys = [
    { file = "pyproject.toml" },
    { file = "requirements.txt" },
    { git = { commit = true, tags = true } },
    { env = "MY_ENV_VAR" },
]
```

### Reinstall Configuration

```toml
[tool.uv]
# Always reinstall these packages
reinstall-package = ["dynamic-package"]

# Packages to exclude from builds
no-build = ["package-with-build-issues"]

# Packages that must be built from source
no-binary = ["package-requiring-custom-build"]
```

## Troubleshooting Configuration

### Debug Configuration Loading

```bash
# Show which config files are loaded
uv sync --verbose

# Show effective configuration
uv pip compile requirements.in --verbose
```

### Configuration Conflicts

When configuration is conflicting:

```bash
# Use --no-config to bypass all config files
uv sync --no-config

# Use specific config file
uv sync --config-file ./debug-uv.toml

# Set environment variable explicitly
UV_INDEX_URL=https://pypi.org/simple uv pip install requests
```

### Common Issues

**Cache corruption:**
```bash
uv cache clean
uv sync --refresh
```

**Python version conflicts:**
```bash
export UV_PYTHON_DOWNLOADS=auto
uv python install 3.12
uv python pin 3.12
```

**Index resolution failures:**
```bash
# Check index configuration
cat pyproject.toml | grep -A5 "\[\[tool.uv.index\]\]"

# Try with explicit index
uv pip install --index-url https://pypi.org/simple package-name
```

## Best Practices

1. **Use `pyproject.toml` for project-specific settings** - Keeps configuration with code
2. **Use `~/.config/uv/uv.toml` for user preferences** - Global defaults
3. **Use environment variables for CI/CD** - Easy to inject and version
4. **Document non-obvious configuration** - Add comments in config files
5. **Test configuration changes locally** - Before committing to repository
