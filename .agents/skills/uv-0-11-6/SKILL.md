---
name: uv-0-11-6
description: A skill for using uv 0.11.6, an extremely fast Python package and project manager written in Rust that replaces pip, pip-tools, pipx, poetry, pyenv, twine, virtualenv, and more with 10-100x faster performance. Use when managing Python projects, installing packages, running scripts with dependencies, managing Python versions, working with tools published as Python packages, or needing high-performance dependency resolution and universal lockfiles.
version: "0.3.0"
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

# uv 0.11.6

## Overview

uv is an extremely fast Python package and project manager, written in Rust. It replaces `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv`, and more — with 10-100x faster performance across all operations.

uv provides three primary interfaces:

- **Projects** — Full project management with lockfiles, dependency resolution, and automatic environment management (`uv init`, `uv add`, `uv sync`, `uv run`, `uv lock`)
- **Tools** — Install and run Python CLI tools without polluting your system (`uv tool install`, `uvx`)
- **Python versions** — Discover, install, and manage Python interpreters (`uv python install`)

It also includes a drop-in replacement for `pip` (`uv pip`), `venv` creation (`uv venv`), package building (`uv build`), and publishing to PyPI (`uv publish`).

## When to Use

- Creating new Python projects with `uv init`
- Managing project dependencies with lockfiles (`uv add`, `uv sync`, `uv lock`)
- Running commands in isolated project environments (`uv run`)
- Installing and running one-off Python CLI tools (`uvx`, `uv tool install`)
- Managing Python interpreter versions across projects (`uv python install`)
- Replacing pip workflows with faster equivalents (`uv pip install`, `uv pip compile`)
- Building and publishing Python packages (`uv build`, `uv publish`)
- Working with monorepos via workspaces
- Setting up CI/CD with reproducible lockfiles

## Core Concepts

### Three Interfaces

uv organizes its functionality into three interfaces:

1. **Project interface** — The primary, high-level workflow for managing Python projects with automatic environment and lockfile management
2. **Tool interface** — For installing and running standalone Python CLI tools
3. **pip interface** — A drop-in replacement for pip, pip-tools, and virtualenv commands

### Universal Lockfiles

uv generates a `uv.lock` file that is universal (cross-platform). It captures the packages that would be installed across all possible Python markers — operating system, architecture, and Python version. Unlike `requirements.txt`, this lockfile is checked into version control for reproducible installations.

### Automatic Lock and Sync

Locking and syncing are automatic in uv. When you run `uv run`, the project is locked and synced before invoking the command. This ensures the environment is always up-to-date without manual steps.

### Managed Python Versions

uv can install Python versions itself (managed Python) or discover existing system installations. By default, it automatically downloads Python versions as needed. Use `uv python install` to explicitly install versions, and `.python-version` files to pin versions per-project.

## Installation / Setup

### Standalone Installer (Recommended)

macOS and Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Request a specific version:
```bash
curl -LsSf https://astral.sh/uv/0.11.6/install.sh | sh
```

### Alternative Methods

```bash
# pip
pip install uv

# pipx (recommended for pip installs)
pipx install uv

# Homebrew
brew install uv

# Cargo (builds from source, requires Rust toolchain)
cargo install --locked uv
```

### Upgrading

```bash
# Self-update (standalone installer only)
uv self update

# Via pip
pip install --upgrade uv
```

### Shell Autocompletion

```bash
# Bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
echo 'uv generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish
```

## Usage Examples

### Quick Start — Create and Run a Project

```bash
# Create a new project
uv init my-app
cd my-app

# Add a dependency
uv add httpx

# Run the project
uv run python main.py

# Or run a specific command with extra dependencies
uv run --with ruff ruff check .
```

### One-Off Tool Execution

```bash
# Run ruff without installing it (uvx is an alias for uv tool run)
uvx ruff check .

# Run a specific version
uvx ruff@0.6.0 check .

# Run with additional dependencies
uvx --with httpx==0.27.0 mytool
```

### Managing Python Versions

```bash
# Install a specific Python version
uv python install 3.12

# Pin a version for the current project
uv python pin 3.12

# List installed versions
uv python list
```

### Creating a Virtual Environment

```bash
uv venv --python 3.12
source .venv/bin/activate
```

## Advanced Topics

**Project Structure and Files**: pyproject.toml, lockfiles, virtual environments → [Projects](reference/01-projects.md)

**Managing Dependencies**: Adding, removing, platform-specific deps, extras, dependency groups → [Dependencies](reference/02-dependencies.md)

**Locking and Syncing**: Lockfile management, upgrades, export formats, partial installations → [Locking and Syncing](reference/03-locking-syncing.md)

**Running Commands**: uv run, additional dependencies per invocation, scripts, signal handling → [Running Commands](reference/04-running-commands.md)

**Workspaces**: Multi-package monorepos, shared lockfiles, workspace sources → [Workspaces](reference/05-workspaces.md)

**Tools Interface**: uvx, tool install/upgrade, tool environments, per-invocation deps → [Tools](reference/06-tools.md)

**Python Version Management**: Managed vs system Python, .python-version files, installation → [Python Versions](reference/07-python-versions.md)

**Configuration Files**: pyproject.toml, uv.toml, environment variables, dotenv support → [Configuration](reference/08-configuration.md)

**Package Indexes**: Private indexes, authentication, index strategies, pinning → [Package Indexes](reference/09-indexes.md)

**Caching**: Cache semantics, clearing, CI caching, dynamic metadata → [Caching](reference/10-caching.md)

**The pip Interface**: uv pip install/compile/sync, environments, compatibility → [pip Interface](reference/11-pip-interface.md)

**Building and Publishing**: uv build, uv publish, distribution formats → [Build and Publish](reference/12-build-publish.md)

**CLI Reference**: Command summary, common options, flags → [CLI Reference](reference/13-cli-reference.md)
