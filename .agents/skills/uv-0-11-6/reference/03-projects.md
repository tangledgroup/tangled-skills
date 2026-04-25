# Working on Projects

uv provides comprehensive project management with `pyproject.toml`, lockfiles, workspaces, and publishing support.

## Creating Projects

### Initialize New Project

```bash
# Create new project in directory
uv init my-project
cd my-project

# Initialize in current directory
mkdir my-project && cd my-project
uv init

# Create library instead of application
uv init --lib my-library

# Specify Python version
uv init my-project --python 3.12
```

### Project Structure

After initialization, uv creates:

```text
my-project/
├── .gitignore          # Git ignore file
├── .python-version     # Pinned Python version
├── README.md           # Project documentation
├── main.py             # Entry point (or src/my_project/)
└── pyproject.toml      # Project configuration
```

After first `uv sync` or `uv run`:

```text
my-project/
├── .venv/              # Virtual environment
├── uv.lock             # Dependency lockfile
├── ...
```

## Managing Dependencies

### Adding Dependencies

```bash
# Add runtime dependency
uv add requests

# Add with version constraint
uv add 'requests>=2.28,<3'

# Add multiple dependencies
uv add flask cors

# Add git dependency
uv add git+https://github.com/psf/requests

# Add from local path
uv add ./local-package

# Add optional dependency (extra)
uv add --dev pytest
uv add --extra docs sphinx

# Add from requirements.txt
uv add -r requirements.txt
```

### Removing Dependencies

```bash
# Remove runtime dependency
uv remove requests

# Remove dev dependency
uv remove --dev pytest
```

### Dependency Groups

```bash
# Add to development group
uv add --group dev pytest pytest-cov

# Add to custom group
uv add --group lint ruff mypy

# Install specific group
uv pip install --group lint

# Compile requirements for group
uv pip compile --group lint
```

### pyproject.toml Structure

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A sample project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.28",
    "httpx>=0.25",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov",
]
docs = [
    "sphinx",
    "sphinx-rtd-theme",
]

[tool.uv]
dev-dependencies = [
    "ruff>=0.3",
    "mypy",
]

[build-system]
requires = ["uv_build>=0.11.6,<0.12"]
build-backend = "uv_build"
```

## Locking and Syncing

### Creating Lockfile

```bash
# Lock dependencies
uv lock

# Lock with upgrade
uv lock --upgrade

# Upgrade specific package
uv lock --upgrade-package requests

# Check lockfile is up-to-date
uv lock --frozen
```

### Syncing Environment

```bash
# Sync all dependencies
uv sync

# Sync without extras
uv sync --no-extras

# Sync specific extra
uv sync --extra dev

# Sync all extras
uv sync --all-extras

# Clean sync (remove extraneous packages)
uv sync --clean

# Reinstall all packages
uv sync --reinstall

# Force refresh cache
uv sync --refresh
```

### Lockfile Format

`uv.lock` is a human-readable TOML file:

```toml
version = 1
requires-python = ">=3.12"

[package]
name = "requests"
version = "2.31.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "urllib3" },
    { name = "certifi" },
]

[metadata]
lock-version = "1.0"
content-hash = "abc123..."
```

## Running Commands

### Execute in Project Environment

```bash
# Run Python script
uv run main.py

# Run module
uv run -m pytest

# Run command with arguments
uv run -- flask run --port 3000

# Run installed tool
uv run -- ruff check .

# Skip project installation
uv run --no-project script.py
```

### Development Workflow

```bash
# Add dependency and test immediately
uv add requests
uv run python -c "import requests; print(requests.__version__)"

# Run tests
uv run -- pytest

# Run linter
uv run -- ruff check .

# Format code
uv run -- ruff format .
```

## Building and Publishing

### Build Distribution

```bash
# Build wheel and source distribution
uv build

# Build only wheel
uv build --wheel

# Build only source distribution
uv build --sdist

# Build specific project in workspace
uv build --package my-package
```

Output:
```text
dist/
├── my_project-0.1.0-py3-none-any.whl
└── my_project-0.1.0.tar.gz
```

### Publish to PyPI

```bash
# Publish to PyPI
uv publish

# Publish to TestPyPI
uv publish --index testpypi

# Publish with token
uv publish --token $PYPI_API_TOKEN

# Check what would be published
uv publish --dry-run
```

### Updating Version

```bash
# View current version
uv version
uv version --short  # Output: 0.1.0

# Update version in pyproject.toml (manual edit required)
# Then commit changes and publish
```

## Workspaces

Workspaces allow managing multiple related packages together.

### Creating Workspace

```bash
# Initialize workspace root
uv init my-workspace
cd my-workspace

# Add workspace configuration to pyproject.toml
# [tool.uv.workspace]
# members = ["packages/*"]

# Create package in workspace
uv init packages/my-package
```

### Workspace Structure

```text
my-workspace/
├── packages/
│   ├── lib-core/
│   │   └── pyproject.toml
│   └── lib-utils/
│       └── pyproject.toml
├── pyproject.toml      # Workspace root
├── uv.lock             # Shared lockfile
└── src/
    └── my_workspace/
```

### Workspace Configuration

```toml
# Root pyproject.toml
[project]
name = "my-workspace"
version = "0.1.0"
dependencies = [
    "lib-core",
    "lib-utils",
]

[tool.uv.sources]
lib-core = { workspace = true }
lib-utils = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/legacy"]
```

### Workspace Commands

```bash
# Lock entire workspace
uv lock

# Sync workspace root
uv sync

# Sync specific package
uv sync --package lib-core

# Run command in specific package
uv run --package lib-core pytest

# Build all packages
uv build
```

## Environment Variables

Load environment variables from dotenv files:

```bash
# Auto-load .env file
uv run -- python app.py

# Load specific file
uv run --env-file .env.development -- python app.py

# Load multiple files (later overrides earlier)
uv run --env-file .env --env-file .env.local -- python app.py

# Disable dotenv loading
uv run --no-env-file -- python app.py
```

## Exporting Lockfiles

```bash
# Export to requirements.txt format
uv export

# Export with dev dependencies
uv export --dev

# Export specific extra
uv export --extra docs

# Exclude editable packages
uv export --no-editables

# Output to file
uv export -o requirements.txt
```

## Troubleshooting

### Lockfile Out of Sync

```bash
# Re-lock dependencies
uv lock

# Force sync
uv sync --reinstall
```

### Dependency Conflicts

```bash
# View resolution details
uv lock --verbose

# Upgrade conflicting package
uv lock --upgrade-package package-name

# Add override file
echo "conflicting-pkg>=2.0" > overrides.txt
uv lock --override overrides.txt
```

### Build Failures

```bash
# Rebuild with verbose output
uv build --verbose

# Clear cache and rebuild
uv cache clean package-name
uv build

# Install build dependencies manually
uv pip install setuptools wheel build
```

## Best Practices

1. **Commit `uv.lock`** to version control for reproducible builds
2. **Use dependency groups** for dev, test, and lint tools
3. **Pin Python version** in `.python-version` file
4. **Use workspaces** for monorepos with shared dependencies
5. **Export lockfiles** when integrating with CI/CD pipelines
6. **Run `uv lock --check`** in CI to ensure lockfile is up-to-date
