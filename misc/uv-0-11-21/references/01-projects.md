# Projects Reference

## Project Creation

### Basic application (default: packaged/src layout)
Since 0.11.21, `uv init` defaults to a **packaged application** with `src/` layout:
```bash
uv init my-project          # src/ layout with build system (DEFAULT)
cd my-project
```
Creates: `src/my_project/__init__.py`, `[build-system]` with `uv_build`, `[project.scripts]` entry point, `.python-version`, `README.md`, `.git/`, `.gitignore`

### Flat layout (no package)
```bash
uv init --no-package my-project   # Flat layout, no build system
```
Creates: `pyproject.toml`, `main.py`, `.python-version`, `README.md`, `.git/`, `.gitignore`

### Library
```bash
uv init --lib my-lib         # Implies --package, adds py.typed marker
```

### Library
```bash
uv init --lib my-lib         # Implies --package, adds py.typed marker
```



### With specific build backend
```bash
uv init --build-backend hatchling my-project
uv init --build-backend setuptools my-project
uv init --build-backend maturin my-ext    # Rust extension modules
uv init --build-backend scikit-build-core my-ext  # C/C++/Fortran extensions
```

### Minimal project
```bash
uv init --bare my-project    # Only pyproject.toml, no README, no .python-version, no git
```

## Project Structure

A complete uv project:
```
my-project/
├── .git/
├── .venv/                   # Auto-created by uv, exclude from VCS
├── .python-version          # e.g., "3.12" or "cpython@3.12"
├── .gitignore
├── pyproject.toml           # Project metadata + dependencies
├── uv.lock                  # Universal lockfile (check into VCS)
└── main.py
```

### Key files

- **`pyproject.toml`** — PEP 621 project metadata, `[tool.uv]` configuration
- **`.python-version`** — Default Python version for the project
- **`.venv/`** — Project virtual environment (auto-managed by uv)
- **`uv.lock`** — Cross-platform lockfile with exact resolved versions

## Managing Dependencies

### Adding dependencies
```bash
uv add requests                          # Latest compatible version
uv add 'requests>=2.28,<3'               # Explicit constraint
uv add 'requests==2.31.0'                # Exact version
uv add --dev pytest                      # Development dependency (dependency-groups.dev)
uv add --group lint ruff                 # Custom group
uv add --optional network httpx          # Optional extra
uv add git+https://github.com/psf/requests  # Git source
uv add -r requirements.txt               # Import from requirements file
uv add "jax; sys_platform == 'linux'"    # Platform-specific
```

### Removing dependencies
```bash
uv remove requests
uv remove --dev pytest
uv remove --group lint ruff
uv remove --optional network httpx
```

### Changing dependency constraints
```bash
uv add 'httpx>0.1.0'                      # Update constraint (locked version unchanged if still valid)
uv add 'httpx>0.1.0' --upgrade-package httpx  # Force upgrade to latest
```

## Dependency Groups

uv uses PEP 735 `[dependency-groups]` table for development dependencies:

```toml
[dependency-groups]
dev = ["pytest"]
lint = ["ruff"]
test = ["pytest", "coverage"]

# Nesting groups
dev = [
  {include-group = "lint"},
  {include-group = "test"}
]
```

Commands:
```bash
uv sync --all-groups                     # Include all groups
uv sync --no-dev                         # Exclude dev group
uv sync --only-dev                       # Only dev group (no project deps)
uv sync --group lint                     # Specific group
uv sync --no-default-groups              # Disable all default groups
```

Default groups can be configured:
```toml
[tool.uv]
default-groups = ["dev", "lint"]
# or
default-groups = "all"
```

## Optional Dependencies (Extras)

```toml
[project.optional-dependencies]
plot = ["matplotlib>=3.6"]
excel = ["openpyxl>=3.1", "xlsxwriter>=3.0"]
```

Usage:
```bash
uv sync --extra plot                     # Enable specific extra
uv sync --all-extras                     # Enable all extras
uv add numpy --optional plot             # Add to an extra
```

## Locking and Syncing

### Automatic behavior
`uv run`, `uv add`, and `uv tree` automatically lock and sync before executing. This is the default workflow.

### Explicit control
```bash
uv lock                                  # Update lockfile only
uv lock --upgrade                        # Upgrade all packages
uv lock --upgrade-package requests       # Upgrade specific package
uv lock --upgrade-package requests==2.31 # Upgrade to exact version
uv lock --check                          # Check if lockfile is current (CI)
```

### Upgrading dependencies (preview)
`uv upgrade` updates dependency constraints in `pyproject.toml`:
```bash
uv upgrade requests                    # Upgrade to latest
uv upgrade requests --upgrade-package  # Update a single constraint
```
Git revisions are rejected in `uv upgrade`.
uv sync                                  # Sync environment from lockfile
uv sync --extra foo                      # Sync with extra
```

### Lock/sync flags for `uv run`
```bash
uv run --locked command     # Error if lockfile outdated
uv run --frozen command     # Skip lockfile check entirely
uv run --no-sync command    # Skip environment sync
```

## Running Commands

```bash
uv run python main.py              # Run script in project env
uv run flask run -p 3000           # Run CLI from project deps
uv run bash scripts/deploy.sh      # Run shell script with project available
uv run --with httpx==0.26.0 python -c "import httpx"  # Temp override
```

### Dotenv support
```bash
uv run --env-file .env python app.py
uv run --env-file .env --env-file .env.local python app.py   # Later overrides earlier
```

## Exporting Lockfiles

```bash
uv export --format requirements.txt     # pip-compatible
uv export --format pylock.toml          # PEP 751 standard
uv export --format cyclonedx1.5         # SBOM (preview)
uv export --format requirements.txt --output-file requirements.txt
uv export --emit-index-url              # Include index URL in output
uv export --emit-find-links             # Include --find-links in output
```

## Version Management

```bash
uv version                              # Show current package version
uv version --short                      # Version only
uv version 1.0.0                        # Set exact version
uv version --bump minor                 # Semantic bump
uv version --bump patch --bump beta     # Pre-release
uv version --bump stable                # Clear pre-release
uv version 2.0.0 --dry-run              # Preview change
```

## pyproject.toml Structure

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["requests>=2.28"]

[project.optional-dependencies]
dev = ["pytest", "ruff"]

[dependency-groups]
lint = ["ruff"]
test = ["pytest"]

[project.scripts]
my-cli = "my_project:main"

[build-system]
requires = ["uv_build>=0.11.21,<0.12"]
build-backend = "uv_build"

[tool.uv]
default-groups = ["dev", "lint"]
exclude-newer = "2025-01-01"
```
