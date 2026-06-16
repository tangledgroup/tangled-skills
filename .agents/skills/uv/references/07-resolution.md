# Resolution Reference

## Resolution Modes

### Universal resolution (default for projects)
uv's project interface uses universal resolution — the lockfile is portable across platforms, architectures, and Python versions. Different package versions can be selected for different environments via markers.

```bash
uv lock                                    # Universal resolution
```

### Platform-specific resolution (pip interface)
```bash
uv pip compile requirements.in -o requirements.txt          # Current platform
uv pip compile --python-platform linux --python-version 3.10 requirements.in
uv pip compile --universal requirements.in -o requirements.txt  # Universal via pip
```

## Resolution Strategy

### Latest versions (default)
```bash
uv lock                                    # Latest compatible versions
```

### Lowest versions (testing)
```bash
uv lock --resolution lowest                # All deps at lowest compatible
uv lock --resolution lowest-direct         # Direct deps lowest, transitive latest
```

Use `--resolution lowest` in CI to validate declared lower bounds.

## Pre-Release Handling

By default, pre-releases are accepted only when:
1. The package is a direct dependency with a pre-release specifier (e.g., `flask>=2.0.0rc1`)
2. All published versions of the package are pre-releases

```bash
uv lock --prerelease allow                 # Allow all pre-releases
uv add 'flask>=2.0.0rc1'                   # Opt-in for specific package
```

## Multi-Version Resolution (Fork Strategy)

Controls how uv balances minimizing version count vs selecting latest per platform:

```toml
[tool.uv]
fork-strategy = "requires-python"   # Default: latest per Python version, minimize across platforms
fork-strategy = "fewest"            # Minimize versions across all dimensions
```

Example with `requires-python` (default):
```
numpy==1.24.4 ; python_version == "3.8"
numpy==2.0.2  ; python_version == "3.9"
numpy==2.2.0  ; python_version >= "3.10"
```

Example with `fewest`:
```
numpy==1.24.4    # Same version for all Python versions
```

## Limited Resolution Environments

Constrain which platforms uv resolves for:
```toml
[tool.uv]
environments = [
    "sys_platform == 'darwin'",
    "sys_platform == 'linux'",
]
```

Entries must be disjoint (non-overlapping). Use to exclude platforms you don't support.

## Required Environments

Force resolution to include specific platforms (for wheel-only packages):
```toml
[tool.uv]
required-environments = [
    "sys_platform == 'darwin' and platform_machine == 'x86_64'"
]
```

Ensures wheel-only packages (like PyTorch) include wheels for the specified platform.

## Common Marker Values

| Marker | Linux | macOS | Windows |
|--------|-------|-------|---------|
| `sys_platform` | `'linux'` | `'darwin'` | `'win32'` |
| `platform_system` | `'Linux'` | `'Darwin'` | `'Windows'` |
| `platform_machine` (x86-64) | `'x86_64'` | `'x86_64'` | `'AMD64'` |
| `platform_machine` (ARM64) | `'aarch64'` | `'arm64'` | `'ARM64'` |
| `os_name` | `'posix'` | `'posix'` | `'nt'` |

Check current platform:
```bash
uvx python -c "import sysconfig; print(sysconfig.get_config_vars())"
```

## Package Indexes

### Defining indexes
```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

Indexes are consulted in definition order. PyPI is the default (lowest priority) unless replaced:
```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
default = true         # Replaces PyPI as default
```

### Explicit indexes
```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true        # Only packages pinned to this index use it
```

### Flat indexes (find-links)
```toml
[[tool.uv.index]]
name = "local-wheels"
url = "/path/to/wheels"
format = "flat"
```

### Index strategy
```bash
uv lock --index-strategy first-index      # Default: stop at first index with package
uv lock --index-strategy unsafe-first-match  # Prefer first index even if newer elsewhere
uv lock --index-strategy unsafe-best-match   # Best version across all indexes (risk of dep confusion)
```

### Command-line indexes
```bash
uv lock --index pytorch=https://download.pytorch.org/whl/cpu
UV_INDEX=pytorch=https://download.pytorch.org/whl/cpu uv lock
```

## Authentication

### Environment variables
```bash
export UV_INDEX_INTERNAL_PROXY_USERNAME=public
export UV_INDEX_INTERNAL_PROXY_PASSWORD=secret
```
(Index name is uppercased, non-alphanumeric chars replaced with underscores)

### Credentials in URL
```toml
[[tool.uv.index]]
name = "internal"
url = "https://user:pass@pypi-proxy.corp.dev/simple"
```

### Credential providers
uv supports netrc and keyring discovery. Configure per-index:
```toml
[[tool.uv.index]]
name = "example"
url = "https://example.com/simple"
authenticate = "always"    # Always search for credentials
# authenticate = "never"   # Never search (prevent credential leaks)
```

### Ignoring error codes
```toml
[[tool.uv.index]]
name = "private-index"
url = "https://private-index.com/simple"
authenticate = "always"
ignore-error-codes = [403]
```

### Cache control headers
```toml
[[tool.uv.index]]
name = "example"
url = "https://example.com/simple"
cache-control = { api = "max-age=600", files = "max-age=365000000, immutable" }
```

## Constraints and Overrides

### Constraints (narrow versions without forcing inclusion)
```toml
[tool.uv]
constraint-dependencies = ["pydantic<2.0"]
```
Or via file:
```bash
uv lock --constraint constraints.txt
```

### Overrides (replace declared requirements entirely)
```toml
[tool.uv]
override-dependencies = ["pydantic>=1.0,<3"]
```
Or via file:
```bash
uv pip compile requirements.in --override overrides.txt
```

## Reproducible Resolutions

### Exclude newer
```toml
[tool.uv]
exclude-newer = "2025-01-01T00:00:00Z"
```

Or duration-based (cooldown):
```toml
[tool.uv]
exclude-newer = "1 week"
```

Per-package:
```toml
[tool.uv]
exclude-newer = "2025-01-01"
exclude-newer-package = { setuptools = "30 days", flask = false }
```

Per-index:
```toml
[[tool.uv.index]]
name = "internal"
url = "https://internal.example.com/simple"
exclude-newer = "7 days"
# exclude-newer = false    # Disable for this index
```

## Conflicting Dependencies

Declare conflicts between extras, groups, or workspace members:
```toml
[tool.uv]
conflicts = [
    [{ extra = "extra1" }, { extra = "extra2" }],
    [{ group = "group1" }, { group = "group2" }],
    [{ package = "member1", extra = "extra1" }, { package = "member2", extra = "extra2" }],
]
```

Conflicting groups cannot be installed together. uv resolves them separately.

## Dependency Cooldowns

Delay resolution of new package versions for security:
```toml
[tool.uv]
exclude-newer = "24 hours"      # Ignore packages uploaded in last 24h
exclude-newer = "P7D"           # ISO 8601: 7-day cooldown
```

Duration formats: `24 hours`, `1 week`, `30 days`, `PT24H`, `P7D`, `P30D`
