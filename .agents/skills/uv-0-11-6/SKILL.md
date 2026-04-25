---
name: uv-0-11-6
description: A skill for using uv 0.11.6, an extremely fast Python package and project manager written in Rust that replaces pip, pip-tools, pipx, poetry, pyenv, twine, virtualenv, and more with 10-100x faster performance. Use when managing Python projects, installing packages, running scripts with dependencies, managing Python versions, working with tools published as Python packages, or needing high-performance dependency resolution and universal lockfiles.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - python
  - package-management
  - dependency-resolution
  - virtual-environments
  - pip-replacement
  - poetry-alternative
  - rust
  - performance
category: tooling
external_references:
  - https://docs.astral.sh/uv/
  - https://github.com/astral-sh/uv
---
## Overview
A skill for using uv 0.11.6, an extremely fast Python package and project manager written in Rust that replaces pip, pip-tools, pipx, poetry, pyenv, twine, virtualenv, and more with 10-100x faster performance. Use when managing Python projects, installing packages, running scripts with dependencies, managing Python versions, working with tools published as Python packages, or needing high-performance dependency resolution and universal lockfiles.

An extremely fast Python package and project manager, written in Rust. uv provides a unified interface to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv`, and more with 10-100x faster performance than pip.

## When to Use
- Installing and managing Python versions across projects
- Creating and managing Python projects with `pyproject.toml`
- Running Python scripts with inline dependency metadata
- Installing and running tools published as Python packages (e.g., ruff, black)
- Replacing pip/pip-tools workflows with faster alternatives
- Managing project dependencies with universal lockfiles
- Working with monorepos using workspace support
- Building and publishing Python packages

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### Installation

Install uv with the standalone installer:

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative methods:**
- **pip**: `pip install uv` or `pipx install uv`
- **Homebrew**: `brew install uv`
- **Cargo**: `cargo install --locked uv`
- **Docker**: `ghcr.io/astral-sh/uv`

### Enable Shell Completion

```bash
# Bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc

# fish
echo 'uv generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish
```

## Core Features
### Python Versions

Install and manage Python versions directly:

```bash
# Install latest Python
uv python install

# Install specific version
uv python install 3.12

# Install multiple versions
uv python install 3.11 3.12

# Install PyPy
uv python install pypy@3.10

# List installed versions
uv python list

# Pin project to specific Python version
uv python pin 3.12

# Uninstall Python version
uv python uninstall 3.11
```

See [Python Versions](reference/01-python-versions.md) for detailed information on discovery, automatic downloads, and managed installations.

### Scripts

Run Python scripts with automatic dependency management:

```bash
# Run script without dependencies
uv run example.py

# Run script with ad-hoc dependencies
uv run --with rich --with requests example.py

# Run script from stdin
echo 'print("hello")' | uv run -

# Create executable script with shebang
#!/usr/bin/env -S uv run --script
```

Scripts can declare inline dependencies using PEP 723 metadata:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint
```

See [Scripts Guide](reference/02-scripts.md) for comprehensive examples and metadata formats.

### Projects

Create and manage Python projects with `pyproject.toml`:

```bash
# Initialize new project
uv init my-project
cd my-project

# Add dependencies
uv add requests flask

# Add version-constrained dependency
uv add 'requests>=2.28,<3'

# Add git dependency
uv add git+https://github.com/psf/requests

# Remove dependency
uv remove requests

# Lock dependencies (create uv.lock)
uv lock

# Sync environment with lockfile
uv sync

# Run command in project environment
uv run -- flask run

# View dependency tree
uv tree

# Build distribution packages
uv build

# Publish to PyPI
uv publish
```

See [Projects Guide](reference/03-projects.md) for detailed workflows including workspaces, dependency management, and publishing.

### Tools

Run and install tools published as Python packages:

```bash
# Run tool without installation (alias: uv tool run)
uvx ruff check
uvx black --check .

# Run specific version
uvx ruff@0.3.0 check
uvx ruff@latest check

# Install tool for persistent use
uv tool install ruff
uv tool install 'black>=24.0'

# List installed tools
uv tool list

# Uninstall tool
uv tool uninstall ruff

# Upgrade tools
uv tool upgrade ruff
```

See [Tools Guide](reference/04-tools.md) for advanced usage including extras, git sources, and plugin management.

### pip Interface

For legacy workflows or fine-grained control:

```bash
# Create virtual environment
uv venv
uv venv --python 3.11

# Install packages (replaces pip install)
uv pip install requests flask
uv pip install -r requirements.txt

# Compile requirements (replaces pip-compile)
uv pip compile requirements.in -o requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# Sync environment (replaces pip-sync)
uv pip sync requirements.txt

# List installed packages
uv pip list
uv pip freeze
uv pip show requests

# Uninstall packages
uv pip uninstall requests

# View dependency tree
uv pip tree
```

See [pip Interface](reference/05-pip-interface.md) for compatibility details and advanced options.

## Advanced Topics
## Advanced Topics

- [Python Versions](reference/01-python-versions.md)
- [Scripts](reference/02-scripts.md)
- [Projects](reference/03-projects.md)
- [Tools](reference/04-tools.md)
- [Pip Interface](reference/05-pip-interface.md)
- [Configuration](reference/06-configuration.md)

## Common Workflows
### Migrate from pip

```bash
# Instead of: pip install package
uv pip install package

# Instead of: pip-compile requirements.in
uv pip compile requirements.in -o requirements.txt

# Instead of: pip-sync requirements.txt
uv pip sync requirements.txt
```

### Migrate from poetry

```bash
# Instead of: poetry new project
uv init project

# Instead of: poetry add package
uv add package

# Instead of: poetry lock
uv lock

# Instead of: poetry install
uv sync

# Instead of: poetry run command
uv run -- command

# Instead of: poetry publish
uv publish
```

### Migrate from pipx

```bash
# Instead of: pipx install tool
uv tool install tool

# Instead of: pipx run tool
uvx tool

# Instead of: pipx uninstall tool
uv tool uninstall tool
```

## Troubleshooting
### Cache Issues

```bash
# Clear entire cache
uv cache clean

# Clear cache for specific package
uv cache clean requests

# Force refresh all dependencies
uv sync --refresh

# Force refresh specific package
uv sync --refresh-package requests

# Reinstall packages
uv sync --reinstall
```

### Python Version Not Found

```bash
# Check available Python versions
uv python list

# Install missing Python version
uv python install 3.12

# Disable managed Python (use system Python only)
uv sync --no-managed-python
```

### Dependency Resolution Failures

```bash
# View detailed resolution log
uv lock --verbose

# Force upgrade specific package
uv lock --upgrade-package requests

# Add constraints file
uv pip compile requirements.in --constraint constraints.txt

# Add overrides for conflicting dependencies
uv pip compile requirements.in --override overrides.txt
```

See [Configuration](reference/06-configuration.md) for advanced settings and environment variable control.

