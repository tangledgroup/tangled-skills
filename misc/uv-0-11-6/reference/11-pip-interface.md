# pip Interface

## Overview

uv provides a drop-in replacement for common `pip`, `pip-tools`, and `virtualenv` commands. These work directly with virtual environments, in contrast to the project interface where the environment is managed automatically.

uv does not rely on or invoke pip — it implements the interface natively for speed.

## Creating Environments

```bash
# Create a virtual environment
uv venv

# With specific Python version
uv venv --python 3.12

# In a specific directory
uv venv /path/to/venv

# Activate
source .venv/bin/activate
```

## Managing Packages

```bash
# Install packages
uv pip install requests
uv pip install -r requirements.txt
uv pip install ".[dev]"

# Uninstall packages
uv pip uninstall requests

# Upgrade packages
uv pip install --upgrade requests
uv pip install --upgrade -r requirements.txt

# Freeze installed packages
uv pip freeze
```

## Inspecting Environments

```bash
# List installed packages
uv pip list

# Show package details
uv pip show requests

# Check for broken packages
uv pip check
```

## Declaring Dependencies

```bash
# Compile requirements (pip-compile equivalent)
uv pip compile requirements.in -o requirements.txt

# With constraints
uv pip compile requirements.in --constraint constraints.txt -o requirements.txt

# Export to pylock.toml (PEP 751)
uv pip compile requirements.in -o pylock.toml
```

## Locking and Syncing Environments

```bash
# Sync environment from requirements file
uv pip sync requirements.txt

# Install from pylock.toml
uv pip install -r pylock.toml
uv pip sync pylock.toml
```

## Configuration

pip-specific settings go under `[tool.uv.pip]`:

```toml
[tool.uv.pip]
index-url = "https://test.pypi.org/simple"
```

These settings apply only to `uv pip` subcommands, not to `uv sync`, `uv lock`, or `uv run`.

## Compatibility

The pip interface closely matches pip's behavior but does not exactly implement all interfaces. Consult the pip-compatibility guide at https://docs.astral.sh/uv/pip/compatibility/ for differences.
