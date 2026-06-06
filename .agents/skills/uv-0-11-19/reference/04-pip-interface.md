# Pip Interface

## Contents
- Overview
- Creating environments
- Installing packages
- Compiling requirements
- Syncing environments
- Key differences from pip

## Overview

`uv pip` provides a drop-in replacement for `pip`, `pip-tools`, and `virtualenv`. It operates directly on virtual environments (unlike the project interface which manages `.venv` automatically). Use this interface when migrating existing pip workflows or working in projects not managed by uv.

uv does not invoke pip — the interface is named for familiarity only.

## Creating environments

```bash
# Create .venv with default Python
uv venv

# With specific Python
uv venv --python 3.12

# With specific Python version
uv venv --python 3.12.3

# In a custom directory
uv venv my-env

# Without Python discovery (use system only)
uv venv --no-python-downloads
```

Activate as usual: `source .venv/bin/activate` (Unix) or `.venv\Scripts\activate` (Windows).

## Installing packages

```bash
# Install a package
uv pip install flask

# With extras
uv pip install "flask[dotenv]"

# Multiple packages
uv pip install flask ruff

# Version constraint
uv pip install 'ruff>=0.2.0'
uv pip install 'ruff==0.3.0'

# From Git
uv pip install "git+https://github.com/astral-sh/ruff"
uv pip install "git+https://github.com/astral-sh/ruff@v0.2.0"

# Editable install
uv pip install -e .
uv pip install -e "./project/ruff"

# From requirements file
uv pip install -r requirements.txt

# From pyproject.toml
uv pip install -r pyproject.toml
uv pip install -r pyproject.toml --extra foo
uv pip install -r pyproject.toml --all-extras

# Dependency groups
uv pip install --group dev
uv pip install --project some/path/ --group foo --group bar

# Specific Python version
uv pip install --python 3.12 flask

# Force refresh cache
uv pip install --refresh flask
uv pip install --refresh-package ruff flask

# Reinstall (ignore installed versions)
uv pip install --reinstall flask
```

### Uninstalling

```bash
uv pip uninstall flask
uv pip uninstall flask ruff
```

## Compiling requirements

`uv pip compile` locks dependencies into `requirements.txt` format, like pip-tools:

```bash
# From requirements.in
uv pip compile requirements.in -o requirements.txt

# From pyproject.toml
uv pip compile pyproject.toml -o requirements.txt

# Multiple sources
uv pip compile pyproject.toml requirements-dev.in -o requirements-dev.txt

# From stdin
echo "ruff" | uv pip compile - -o requirements.txt

# With extras
uv pip compile pyproject.toml --extra foo -o requirements.txt
uv pip compile pyproject.toml --all-extras -o requirements.txt

# Dependency groups
uv pip compile --group dev -o dev-requirements.txt
uv pip compile --project some/path/ --group foo --group bar -o requirements.txt

# Universal (cross-platform) resolution
uv pip compile requirements.in --universal -o requirements.txt

# Upgrade all dependencies
uv pip compile requirements.in --upgrade -o requirements.txt

# Upgrade specific package
uv pip compile requirements.in --upgrade-package ruff -o requirements.txt
```

When an output file exists, uv preserves pinned versions. Use `--upgrade` or `--upgrade-package` to change them.

## Syncing environments

`uv pip sync` installs exact packages from a requirements file, removing extras:

```bash
# Sync from requirements.txt
uv pip sync requirements.txt

# Sync from pylock.toml (PEP 751)
uv pip sync pylock.toml

# Allow extras (don't remove unlisted packages)
uv pip sync requirements.txt --no-sync  # skip
```

## Key differences from pip

- uv does not invoke or depend on pip
- `uv pip install` does not remove unlisted packages (unlike `uv pip sync`)
- `uv pip compile` preserves existing pins in output files
- Many additional flags: `--universal`, `--refresh`, `--reinstall`, `--group`
- 10–100x faster resolution and installation
- Full compatibility documented in uv's pip-compatibility guide
