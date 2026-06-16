#!/usr/bin/env bash
# uv — Manage Python projects, scripts, tools, environments, and packages with uv — the fast Python package manager. Use when working with pyproject.toml, virtual environments, pip alternatives, venv creation, dependency locking (uv.lock), running Python scripts with inline metadata, installing/running CLI tools via uvx, managing Python versions, building wheels/sdists, publishing to PyPI, workspace management, or migrating from pip/pip-tools/virtualenv. Covers uv run, uv add, uv sync, uv lock, uv build, uv publish, uv venv, uv pip, uv tool, uv python, and all related workflows.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$SCRIPT_DIR/_uv.py" "$@"
