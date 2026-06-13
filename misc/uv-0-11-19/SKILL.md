---
name: uv-0-11-19
description: Fast Python package and project manager written in Rust. Replaces pip, pip-tools, pipx, poetry, pyenv, virtualenv, twine, and more. Use when managing Python dependencies, creating virtual environments, running tools with uvx (pipx alternative), installing Python versions, building/publishing packages, or any Python project setup task.
---

# uv 0.11.19

Extremely fast Python package and project manager (10–100× faster than pip). Single tool replacing `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `virtualenv`, and `twine`.

## Overview

uv manages Python projects, scripts, tools, and environments. It provides:

- **Projects** — dependency management with lockfiles (`uv.lock`)
- **Scripts** — inline metadata (PEP 723) for standalone `.py` files
- **Tools** — `uvx` for ephemeral tool execution (pipx replacement)
- **Python versions** — install and switch between Python implementations
- **pip interface** — drop-in `uv pip` replacement with familiar CLI

## Usage

### Project workflow

```bash
uv init my-project          # create new project
cd my-project
uv add requests             # add dependency (auto-creates .venv)
uv add 'flask>=2.0'         # with version constraint
uv add --dev pytest          # dev dependency
uv remove requests           # remove dependency
uv lock                      # resolve and write uv.lock
uv sync                      # install from lockfile
uv run python main.py        # run in project environment
uv run flask run             # run CLI tool from dependencies
```

### uvx — run tools without installing (pipx alternative)

```bash
uvx ruff check .            # ephemeral: resolves, installs, runs, discards
uvx pycowsay hello          # one-off tool execution
uvx ruff@0.8.0 check        # pin exact version
uvx --from httpie http      # package name ≠ command name
uvx --with mkdocs-material mkdocs  # include extra dependency
```

### Python version management

```bash
uv python install 3.12      # install specific version
uv python install pypy@3.10 # alternative implementation
uv python list              # list available/installed versions
uv python pin 3.12          # write .python-version file
uv venv --python 3.11       # create venv with specific Python
```

### Scripts with inline metadata (PEP 723)

```bash
uv init --script task.py    # scaffold script with metadata block
uv add --script task.py requests rich  # add deps to script header
uv run task.py              # auto-resolves deps from inline metadata
```

Inline metadata block in `.py` files:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "rich"]
# ///
```

### Build and publish

```bash
uv build                    # wheel + sdist into dist/
uv version --bump minor     # semantic version bump
uv publish                  # upload to PyPI (set UV_PUBLISH_TOKEN)
```

### pip interface (drop-in replacement)

```bash
uv venv                     # create virtualenv
uv pip install flask        # install package
uv pip install -r reqs.txt  # install from file
uv pip compile reqs.in -o reqs.txt  # lock dependencies (pip-compile replacement)
uv pip sync reqs.txt        # exact environment match
uv pip freeze               # list installed packages
```

### Cache management

```bash
uv cache clean              # clear all cache
uv cache clean ruff         # clear specific package
uv cache prune --ci         # CI: keep built wheels, drop pre-built
```

## Gotchas

- **`uvx` vs `uv run`** — `uvx` runs in an isolated environment with no access to project dependencies. Use `uv run` when the tool needs your project installed (e.g., `pytest`, `mypy`).
- **`--no-project` flag** — inside a project directory, `uv run script.py` installs the project first. Use `uv run --no-project script.py` to skip that.
- **Inline scripts ignore project deps** — when a `.py` file has PEP 723 metadata, `uv run` uses only those dependencies, not the surrounding project's.
- **Package vs command name mismatch** — if `uvx ruff` fails because the command isn't in the package, use `uvx --from <package> <command>`.
- **`--system` required for system Python** — uv refuses to modify system Python by default. Add `--system` flag explicitly (appropriate for CI/containers).
- **Automatic Python downloads** — uv downloads missing Python versions by default. Disable with `UV_PYTHON_DOWNLOADS=never` if you need strict control.
- **Workspaces share one lockfile** — all workspace members resolve together. Conflicting `requires-python` across members takes the intersection.
- **`uv pip compile` outputs to stdout** — use `-o requirements.txt` to write a file; without it the output is just displayed.

## References

- [01-projects.md](references/01-projects.md) — project structure, pyproject.toml, lockfile, dependency sources
- [02-tools.md](references/02-tools.md) — uvx details, tool install/upgrade, package vs command names
- [03-scripts.md](references/03-scripts.md) — PEP 723 inline metadata, shebang scripts, locking scripts
- [04-python.md](references/04-python.md) — Python installation, version requests, managed vs system Python
- [05-pip-interface.md](references/05-pip-interface.md) — uv pip commands, compile/sync, constraints and overrides
- [06-workspaces.md](references/06-workspaces.md) — multi-package workspaces, shared lockfile, workspace sources
