# Dependencies

## Dependency Fields

Dependencies are defined in several fields:

- `project.dependencies` — Published dependencies
- `project.optional-dependencies` — Published optional dependencies (extras)
- `dependency-groups` — Local development dependencies (PEP 735)
- `tool.uv.sources` — Alternative sources for dependencies during development

uv supports modifying dependencies with `uv add` and `uv remove`, but metadata can also be edited directly in `pyproject.toml`.

## Adding Dependencies

```bash
# Add a dependency (auto-constrains to latest compatible version)
uv add httpx

# Add with explicit constraint
uv add "httpx>=0.20"

# Add as dev dependency
uv add --dev ruff

# Add to a specific group
uv add --group lint ruff

# Add as optional dependency (extra)
uv add --optional docs sphinx

# Import from requirements.txt
uv add -r requirements.txt
```

The dependency includes a constraint for the most recent compatible version. Adjust bounds with `--bounds` or provide the constraint directly.

When adding from non-registry sources, uv adds an entry in `tool.uv.sources`:

```bash
uv add "httpx @ git+https://github.com/encode/httpx"
```

Resulting in:

```toml
[project]
dependencies = ["httpx"]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx" }
```

## Removing Dependencies

```bash
uv remove httpx
uv remove --dev ruff
uv remove --group lint ruff
uv remove --optional docs sphinx
```

If a source is defined for the removed dependency and no other references exist, it is also removed.

## Changing Dependencies

To change an existing dependency constraint:

```bash
uv add "httpx>0.1.0"
```

To force updating to the latest within constraints:

```bash
uv add "httpx>0.1.0" --upgrade-package httpx
```

## Platform-Specific Dependencies

Use environment markers for platform or Python version targeting:

```bash
# Linux only
uv add "jax; sys_platform == 'linux'"

# Python 3.11+
uv add "numpy; python_version >= '3.11'"
```

Resulting in:

```toml
[project]
dependencies = [
    "jax; sys_platform == 'linux'",
    "numpy; python_version >= '3.11'",
]
```

## Project Dependencies (Published)

The `project.dependencies` table defines packages required for the project using dependency specifier syntax (PEP 621):

```toml
[project]
name = "albatross"
version = "0.1.0"
dependencies = [
    "tqdm >=4.66.2,<5",
    "torch ==2.2.2",
    "transformers[torch] >=4.39.3,<5",
    "importlib_metadata >=7.1.0,<8; python_version < '3.10'",
]
```

## Optional Dependencies (Extras)

Defined in `project.optional-dependencies`:

```toml
[project.optional-dependencies]
docs = ["sphinx>=7.0.0"]
test = ["pytest>=7.0.0"]
all = ["sphinx>=7.0.0", "pytest>=7.0.0"]
```

Sync extras with `uv sync --extra docs` or `uv sync --all-extras`.

## Development Dependencies

Defined in `[dependency-groups]` (PEP 735):

```toml
[dependency-groups]
dev = ["pytest>=7.0.0", "ruff"]
lint = ["ruff", "mypy"]
docs = ["sphinx>=7.0.0"]
```

The `dev` group is synced by default. Control with:

- `--no-dev` — exclude dev group
- `--only-dev` — install only dev deps (not project)
- `--all-groups` — include all groups
- `--group <name>` — include specific group
- `--no-group <name>` — exclude specific group

## Dependency Sources

The `tool.uv.sources` table extends standard dependency tables with alternative sources:

### Path Dependencies

```toml
[tool.uv.sources]
foo = { path = "../foo", editable = true }
```

### Git Dependencies

```toml
[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx" }
httpx = { git = "https://github.com/encode/httpx", rev = "main" }
httpx = { git = "https://github.com/encode/httpx", tag = "v0.27.0" }
httpx = { git = "https://github.com/encode/httpx", branch = "dev" }
```

### URL Dependencies

```toml
[tool.uv.sources]
mypackage = { url = "https://example.com/mypackage-1.0.0-py3-none-any.whl" }
```

### Platform-Specific Sources

```toml
[tool.uv.sources]
torch = [
    { index = "pytorch-cu118", marker = "sys_platform == 'darwin'" },
    { index = "pytorch-cu124", marker = "sys_platform != 'darwin'" },
]
```

## Importing from Requirements Files

```bash
uv add -r requirements.txt
```

See the pip-to-project migration guide for details.
