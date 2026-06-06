---
name: uv-0-11-19
description: >-
  Manages Python projects, tools, scripts, and environments using uv 0.11.19 — Astral's extremely fast Python package manager written in Rust. Covers project management with lockfiles and workspaces, tool installation via uvx, Python version management, pip-compatible interface, inline script metadata, caching, and configuration. Use when creating or managing Python projects, installing CLI tools, running scripts with dependencies, managing Python versions, replacing pip/pipx/poetry workflows, or configuring uv behavior.
---

# uv 0.11.19

## Overview

uv is an extremely fast Python package and project manager written in Rust by Astral (creators of Ruff). It replaces `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `virtualenv`, and more with a single tool that is 10–100x faster than pip.

uv provides four main interfaces:

- **Projects** (`uv init`, `uv add`, `uv run`, `uv sync`, `uv lock`) — Full project management with universal lockfiles, workspaces, and automatic environment management.
- **Tools** (`uvx` / `uv tool run`, `uv tool install`) — Install and run CLI tools from Python packages, like pipx.
- **Python versions** (`uv python install`, `uv python pin`) — Install and manage Python interpreters directly.
- **Pip interface** (`uv pip compile`, `uv pip install`, `uv venv`) — Drop-in replacement for pip, pip-tools, and virtualenv commands.

Additionally, uv supports **scripts** with inline dependency metadata and a **global cache** for disk-space-efficient dependency deduplication.

## When to Use

- Creating a new Python project with `uv init`
- Adding dependencies to a project with `uv add <package>`
- Running commands or scripts in a project environment with `uv run`
- Installing CLI tools from PyPI with `uvx <tool>` or `uv tool install <tool>`
- Managing Python versions without pyenv: `uv python install 3.12`
- Replacing pip/pip-tools workflows: `uv pip compile`, `uv pip sync`
- Running single-file scripts with inline dependencies
- Setting up workspaces for multi-package repositories
- Configuring uv via environment variables or configuration files

## Core Concepts

### Project lifecycle

```bash
# Create a new project
uv init my-project

# Add a dependency (auto-creates .venv, updates pyproject.toml and uv.lock)
cd my-project && uv add requests

# Run a command in the project environment (auto-syncs first)
uv run python main.py

# Explicitly lock or sync
uv lock        # Resolve dependencies into uv.lock
uv sync        # Install lockfile into .venv
```

### Locking and syncing

Locking resolves dependencies into `uv.lock`. Syncing installs packages from the lockfile into `.venv`. Both are **automatic** during `uv run` — the environment is always up-to-date. Disable with `--locked` (error if stale) or `--frozen` (skip check entirely).

### Tools (uvx)

`uvx` is an alias for `uv tool run`. It executes tools in ephemeral, cached environments:

```bash
# Run without installing (cached)
uvx ruff check .

# Install persistently (adds to PATH)
uv tool install ruff

# Run with extra dependencies
uvx --with httpx ruff check .
```

### Python version requests

Most commands accept `--python` with flexible formats:

- `3.12`, `3.12.3` — specific versions
- `>=3.12,<3.13` — version specifiers
- `cpython@3.12`, `pypy` — by implementation
- `/opt/bin/python3` — by path

uv auto-downloads missing Python versions. Pin with `.python-version` file or `uv python pin 3.12`.

### Cache

uv uses a global cache at `$XDG_CACHE_HOME/uv` (or `~/.cache/uv`) for dependency deduplication. Clear with `uv cache clean`, prune unused entries with `uv cache prune`, or force revalidation with `--refresh`.

## Advanced Topics

**Projects**: Full project management — init, add, run, sync, lock, workspaces, layout, dependencies → [Projects](reference/01-projects.md)

**Tools**: Tool installation, execution, upgrades, additional dependencies, PATH integration → [Tools](reference/02-tools.md)

**Python versions**: Installing, upgrading, pinning, discovery logic, managed vs system Python → [Python Versions](reference/03-python-versions.md)

**Pip interface**: pip/pip-tools/virtualenv replacement — compile, install, sync, environments → [Pip Interface](reference/04-pip-interface.md)

**Scripts**: Inline metadata, `uv run` with scripts, dependency declaration → [Scripts](reference/05-scripts.md)

**Caching and configuration**: Cache management, environment variables, config files, indexes → [Caching and Configuration](reference/06-caching-and-config.md)
