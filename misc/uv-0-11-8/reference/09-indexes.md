# Package Indexes

## Overview

By default, uv uses PyPI. Configure additional indexes via `[[tool.uv.index]]` in `pyproject.toml` or `--index` on the command line.

## Defining an Index

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

Indexes are prioritized in definition order. Command-line indexes take precedence over config file indexes. PyPI is the default (lowest priority) index.

Exclude PyPI by setting `default = true` on another index:

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
default = true
```

On the command line:

```bash
uv lock --index pytorch=https://download.pytorch.org/whl/cpu
UV_INDEX=pytorch=https://download.pytorch.org/whl/cpu uv lock
```

## Pinning a Package to an Index

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

Platform-specific index pinning:

```toml
[tool.uv.sources]
torch = [
    { index = "pytorch-cu118", marker = "sys_platform == 'darwin'" },
    { index = "pytorch-cu124", marker = "sys_platform != 'darwin'" },
]

[[tool.uv.index]]
name = "pytorch-cu118"
url = "https://download.pytorch.org/whl/cu118"

[[tool.uv.index]]
name = "pytorch-cu124"
url = "https://download.pytorch.org/whl/cu124"
```

## Explicit Indexes

Mark an index as `explicit = true` to prevent packages from being installed from it unless explicitly pinned:

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

This ensures `torch` comes from the pytorch index while all other packages come from PyPI.

## Index Strategies

```bash
# Default: first-index (stop at first index with the package)
uv lock --index-strategy first-index

# Prefer first index even if newer versions exist elsewhere
uv lock --index-strategy unsafe-first-match

# Best version across all indexes (risk of dependency confusion)
uv lock --index-strategy unsafe-best-match
```

Default `first-index` prevents dependency confusion attacks. `unsafe-best-match` is closest to pip's behavior but exposes users to such risks.

## Authentication

### Environment Variables

For an index named `internal-proxy`, set:

```bash
export UV_INDEX_INTERNAL_PROXY_USERNAME=public
export UV_INDEX_INTERNAL_PROXY_PASSWORD=koala
```

The environment variable name uses the uppercase index name with non-alphanumeric characters replaced by underscores.

### Direct URL Credentials

```toml
[[tool.uv.index]]
url = "https://public:koala@example.com/simple"
```

Not recommended for shared projects — use environment variables instead.

### uv auth CLI

```bash
# Login to a service (stores in system keyring)
uv auth login pypi.org --username user --password pass

# Logout
uv auth logout pypi.org

# Show stored token
uv auth token pypi.org

# Show credentials directory
uv auth dir
```

Supported keyring providers: `native` (system keyring), `subprocess` (keyring command).
