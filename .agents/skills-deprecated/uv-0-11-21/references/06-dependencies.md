# Dependencies Reference

## Dependency Sources (`tool.uv.sources`)

Sources define alternative origins for dependencies during development. They are uv-specific and ignored by other tools.

### Git Sources
```bash
uv add git+https://github.com/encode/httpx
uv add git+ssh://git@github.com/encode/httpx
uv add git+https://github.com/encode/httpx --tag 0.27.0
uv add git+https://github.com/encode/httpx --branch main
uv add git+https://github.com/encode/httpx --rev 326b943
uv add git+https://github.com/langchain-ai/langchain#subdirectory=libs/langchain
uv add --lfs git+https://github.com/repo/lfs-tool    # Git LFS support
```

Resulting `pyproject.toml`:
```toml
[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.0" }
```

### URL Sources
```bash
uv add "https://files.pythonhosted.org/packages/.../httpx-0.27.0.tar.gz"
```

```toml
[tool.uv.sources]
httpx = { url = "https://files.pythonhosted.org/.../httpx-0.27.0.tar.gz" }
```

### Path Sources
```bash
uv add ./foo-0.1.0-py3-none-any.whl         # Local wheel
uv add ~/projects/bar/                       # Local directory (builds as package)
uv add --editable ../projects/bar/           # Editable install
```

```toml
[tool.uv.sources]
bar = { path = "../projects/bar", editable = true }
```

### Index Sources
```bash
uv add torch --index pytorch=https://download.pytorch.org/whl/cpu
```

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

### Platform-Specific Sources
```toml
[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.2",
          marker = "sys_platform == 'darwin'" }
```

### Multiple Sources per Dependency
```toml
[tool.uv.sources]
torch = [
  { index = "torch-cpu", marker = "platform_system == 'Darwin'" },
  { index = "torch-gpu", marker = "platform_system == 'Linux'" },
]

[[tool.uv.index]]
name = "torch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[[tool.uv.index]]
name = "torch-gpu"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
```

### Disabling Sources
```bash
uv lock --no-sources     # Ignore tool.uv.sources (test published compatibility)
uv build --no-sources    # Build without sources
```

## Editable Installs

Editable installs link source files directly into the environment via `.pth` files, so changes are reflected immediately.

```bash
uv add --editable ./path/foo
uv add --no-editable ./path/foo   # Opt-out of editable (deployment)
```

Workspace members are editable by default. Use `--no-editable` to install as regular packages.

## Virtual Dependencies

A virtual dependency installs its transitive dependencies but not the package itself:

```toml
[tool.uv.sources]
bar = { path = "../projects/bar", package = false }
```

Useful for directories that define dependencies but aren't importable packages.

## Workspaces

Workspaces group multiple packages under a single lockfile, inspired by Cargo/Rust workspaces.

### Creating a workspace
```toml
# pyproject.toml (workspace root)
[project]
name = "albatross"
version = "0.1.0"
dependencies = ["bird-feeder", "tqdm>=4,<5"]

[tool.uv.sources]
bird-feeder = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/seeds"]
```

### Workspace behavior
- Single `uv.lock` for all members
- `uv lock` resolves the entire workspace at once
- `uv run` and `uv sync` operate on workspace root by default
- `uv run --package bird-feeder <cmd>` targets a specific member
- Dependencies between members are editable by default
- Root `tool.uv.sources` apply to all members unless overridden

### Workspace layout
```
albatross/
├── pyproject.toml          # Workspace root
├── uv.lock                 # Shared lockfile
├── src/albatross/main.py
├── packages/
│   ├── bird-feeder/
│   │   ├── pyproject.toml
│   │   └── src/bird_feeder/
│   └── seeds/              # Excluded from workspace
│       └── pyproject.toml
```

### When not to use workspaces
- Members have conflicting requirements (use path dependencies instead)
- Each member needs separate virtual environments
- Members need different `requires-python` ranges

## Build Isolation

By default, uv builds packages in isolated environments with their declared build dependencies.

### Disabling build isolation for specific packages
```toml
[project]
dependencies = ["cchardet", "cython", "setuptools"]

[tool.uv]
no-build-isolation-package = ["cchardet"]
```

uv performs two-phase install: first packages with build isolation, then those without.

### Augmenting build dependencies
```toml
[tool.uv.extra-build-dependencies]
cchardet = ["cython"]
flash-attn = [{ requirement = "torch", match-runtime = true }]
```

`match-runtime = true` ensures the build dependency matches the runtime version. Only works with packages declaring static metadata.

### Providing metadata upfront
For packages without static metadata:
```toml
[[tool.uv.dependency-metadata]]
name = "flash-attn"
version = "2.6.3"
requires-dist = ["torch", "einops"]
```

## Dependency Specifiers

Standard PEP 508 syntax:
```
package[extras] >=1.2.3,<2,!=1.4.0 ; python_version < '3.10'
```

Version operators: `>`, `<`, `>=`, `<=`, `==`, `!=`, `~=`

Examples:
```
tqdm >=4.66.2,<5
torch ==2.2.2
transformers[torch] >=4.39.3,<5
importlib_metadata >=7.1.0; python_version < '3.10'
jax; sys_platform == 'linux'
```

`~=` (compatible release): `foo ~=1.2` equals `>=1.2,<2`; `foo ~=1.2.3` equals `>=1.2.3,<1.3`

## Lower Bounds

`uv add` automatically adds lower bounds (e.g., `>=0.27.2`). Lower bounds prevent the resolver from backtracking to ancient versions during conflict resolution.

Validate bounds with:
```bash
uv lock --resolution lowest       # Test with lowest compatible versions
uv lock --resolution lowest-direct # Lowest direct, latest transitive
```
