---
name: uv
description: Manage Python projects, scripts, tools, environments, and packages with uv — the fast Python package manager. Use when working with pyproject.toml, virtual environments, pip alternatives, venv creation, dependency locking (uv.lock), running Python scripts with inline metadata, installing/running CLI tools via uvx, managing Python versions, building wheels/sdists, publishing to PyPI, workspace management, or migrating from pip/pip-tools/virtualenv. Covers uv run, uv add, uv sync, uv lock, uv build, uv publish, uv venv, uv pip, uv tool, uv python, and all related workflows.
metadata:
  tags:
    - python
    - packaging
    - devops
---

# uv

uv is an extremely fast Python package manager and resolver, written in Rust. It replaces `pip`, `pip-tools`, `virtualenv`, `pipx`, and more with a single unified tool.

## Overview

uv provides five independent interfaces that can be used together or separately:

1. **Projects** — Full project management with `pyproject.toml`, lockfiles, and automatic environments
2. **Scripts** — Standalone Python scripts with inline dependency metadata (PEP 723)
3. **Tools** — One-off or installed CLI tools via `uvx` / `uv tool`
4. **Python versions** — Install, discover, and manage Python interpreters
5. **pip interface** — Drop-in replacement for `pip`, `pip-tools`, and `virtualenv`

### Core workflow (projects)

```bash
uv init my-project          # Create a new project
cd my-project
uv add requests             # Add dependency (auto-locks + syncs)
uv run python main.py       # Run in project environment
uv lock                     # Explicitly update lockfile
uv sync                     # Explicitly sync environment
uv build                    # Build sdist + wheel
uv publish                  # Publish to PyPI
```

### Quick reference by task

| Task | Command |
|------|---------|
| Create project | `uv init <name>` / `uv init --lib` / `uv init --package` |
| Add dependency | `uv add <package>` / `uv add --dev pytest` / `uv add --optional extra pkg` |
| Remove dependency | `uv remove <package>` |
| Run command | `uv run <command>` / `uv run --with httpx script.py` |
| Lock dependencies | `uv lock` / `uv lock --upgrade` / `uv lock --upgrade-package pkg` |
| Sync environment | `uv sync` / `uv sync --extra foo` / `uv sync --no-dev` |
| Run tool (ephemeral) | `uvx ruff` / `uvx ruff@0.6.0 check` |
| Install tool (persistent) | `uv tool install ruff` |
| Create venv | `uv venv` / `uv venv --python 3.12` |
| pip install | `uv pip install flask` (requires active venv) |
| pip compile | `uv pip compile requirements.in -o requirements.txt` |
| Install Python | `uv python install 3.12` |
| List Python versions | `uv python list` |
| Pin Python version | `uv python pin 3.12` |
| Build package | `uv build` / `uv build --wheel` / `uv build --sdist` |
| Publish package | `uv publish` |
| View dependency tree | `uv tree` |
| Export lockfile | `uv export --format requirements.txt` / `uv export --format pylock.toml` |
| Cache management | `uv cache clean` / `uv cache prune --ci` |

## Gotchas

- **`uv run` auto-locks and syncs** — by default, `uv run` ensures the lockfile and environment are up-to-date before running. Use `--locked` to error if outdated, `--frozen` to skip checking, or `--no-sync` to skip syncing.
- **Scripts with inline metadata are isolated from projects** — even inside a project directory, a script with `# /// script` metadata runs in its own environment, ignoring the project's dependencies. This is intentional and cannot be disabled per-script.
- **`uvx` vs `uv run --with`** — `uvx tool` runs isolated from any project. If the tool needs your project installed (e.g., `pytest`, `mypy`), use `uv run pytest` instead of `uvx pytest`.
- **`uv sync` removes extraneous packages by default** — unlike `uv run`, `uv sync` performs "exact" syncing. Use `--inexact` to retain extra packages. Conversely, `uv run` uses inexact syncing by default; use `--exact` for exact syncing.
- **`tool.uv.sources` is uv-only** — sources defined in `[tool.uv.sources]` are ignored by other tools (pip, build, etc.). Use `uv lock --no-sources` or `uv build --no-sources` to test compatibility.
- **Build system determines install behavior** — without a `[build-system]` table, uv won't build/install the project itself (only its dependencies). Add a build system or set `tool.uv.package = true` to force installation.
- **Workspaces share one lockfile** — all workspace members must be compatible. Use `conflicts` declarations for incompatible extras/groups across members.
- **`--system` flag required for non-virtualenv targets** — uv refuses to modify system Python by default. Use `--system` explicitly (appropriate in CI/containers).
- **Cache directory matters for performance** — keep the cache on the same filesystem as the target environment to enable hard-linking instead of slow copies.
- **Free-threaded Python requires explicit request** — use `3.13t` or `3.13+freethreaded` to select free-threaded CPython 3.13+. For 3.14+, it's available but GIL-enabled is still preferred by default.

## References

- [01-projects.md](./references/01-projects.md) — Project creation, structure, dependencies, lockfiles, syncing, running commands
- [02-scripts.md](./references/02-scripts.md) — Standalone scripts with inline metadata (PEP 723), shebangs, locking scripts
- [03-tools.md](./references/03-tools.md) — Running and installing tools with `uvx` / `uv tool`, version pinning, extras, plugins
- [04-python-versions.md](./references/04-python-versions.md) — Installing, discovering, and managing Python interpreters
- [05-pip-interface.md](./references/05-pip-interface.md) — pip-compatible commands: venv, install, compile, sync, constraints, overrides
- [06-dependencies.md](./references/06-dependencies.md) — Dependency sources (Git, URL, path, workspace), workspaces, build isolation, editable installs
- [07-resolution.md](./references/07-resolution.md) — Resolution strategies, package indexes, authentication, constraints, overrides, reproducibility
- [08-advanced.md](./references/08-advanced.md) — Caching, configuration files, building/publishing, export formats, workspace conflicts
