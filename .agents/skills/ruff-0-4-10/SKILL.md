---
name: ruff-0-4-10
description: A skill for using Ruff 0.4.10, an extremely fast Python linter and code formatter written in Rust that replaces Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, autoflake, and more with 10x-100x faster performance. Use when linting Python code for style and correctness issues, formatting code consistently, configuring rule selection across 800+ lint rules, suppressing violations with noqa comments, or needing fast incremental analysis in CI/CD pipelines and editors.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - python
  - linter
  - formatter
  - code-quality
  - flake8
  - black
  - isort
  - pyupgrade
category: tooling
external_references:
  - https://docs.astral.sh/ruff
  - https://github.com/astral-sh/ruff
---

# Ruff 0.4.10

## Overview

Ruff is an extremely fast Python linter and code formatter, written in Rust. It aims to be orders of magnitude faster than alternative tools while integrating more functionality behind a single, common interface.

Ruff can replace Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, autoflake, and more — all while executing tens or hundreds of times faster than any individual tool.

Key features:

- 10-100x faster than existing linters (like Flake8) and formatters (like Black)
- Installable via `pip`, `uv`, `pipx`, Homebrew, Conda, or standalone installers
- `pyproject.toml`, `ruff.toml`, or `.ruff.toml` configuration support
- Drop-in parity with Flake8, isort, and Black
- Built-in caching to avoid re-analyzing unchanged files
- Automatic fix support for error correction (e.g., remove unused imports)
- Over 800 built-in rules, with native re-implementations of popular Flake8 plugins like flake8-bugbear
- First-party editor integrations for VS Code and more
- Monorepo-friendly, with hierarchical and cascading configuration

## When to Use

Use Ruff when:

- Linting Python code for style and correctness issues
- Formatting Python code consistently (Black-compatible)
- Replacing multiple tools (Flake8 + plugins, Black, isort, pydocstyle, pyupgrade, autoflake) with a single fast tool
- Configuring rule selection across 800+ lint rules
- Suppressing violations with `noqa` comments
- Setting up fast CI/CD pipeline analysis
- Integrating with editors via the Ruff language server
- Working with Jupyter Notebooks (`.ipynb`) alongside regular Python files

## Core Concepts

### Two Subcommands

Ruff provides two primary subcommands:

- **`ruff check`** — The linter. Analyzes Python files for rule violations and optionally auto-fixes them.
- **`ruff format`** — The formatter. Reformats Python code to a consistent style (Black-compatible).

### Rule Codes

Ruff mirrors Flake8's rule code system: each rule has a one-to-three letter prefix followed by three digits (e.g., `F401`). The prefix indicates the rule source:

- `F` — Pyflakes (unused imports, undefined names, etc.)
- `E` — pycodestyle (indentation, whitespace, line length, etc.)
- `W` — pycodestyle warnings
- `UP` — pyupgrade (modernize Python syntax)
- `B` — flake8-bugbear (common bugs and design issues)
- `I` — isort (import sorting)
- `D` — pydocstyle (docstring conventions)
- `SIM` — flake8-simplify (code simplification)
- And many more (50+ rule categories)

### Default Rule Set

By default, Ruff enables Pyflakes (`F`) rules and a subset of pycodestyle (`E4`, `E7`, `E9`) codes, omitting stylistic rules that overlap with formatters.

## Installation / Setup

Install via `uv` (recommended), `pip`, `pipx`, Homebrew, Conda, or standalone installers:

```bash
# With uv (recommended).
uv tool install ruff@latest   # Install globally.
uv add --dev ruff             # Or add to your project.

# With pip.
pip install ruff

# With pipx.
pipx install ruff

# Standalone installer (macOS/Linux).
curl -LsSf https://astral.sh/ruff/install.sh | sh

# Homebrew.
brew install ruff

# Conda.
conda install -c conda-forge ruff
```

Invoke directly with `uvx`:

```bash
uvx ruff check    # Lint all files in the current directory.
uvx ruff format   # Format all files in the current directory.
```

## Usage Examples

### Basic Linting

```bash
ruff check                          # Lint files in the current directory.
ruff check --fix                    # Lint and auto-fix.
ruff check --watch                  # Lint and re-lint on file changes.
ruff check path/to/code/            # Lint a specific directory.
ruff check path/to/file.py          # Lint a single file.
```

### Basic Formatting

```bash
ruff format                         # Format all files in the current directory.
ruff format --check                 # Check without writing (CI-friendly).
ruff format --diff                  # Show diff of what would change.
ruff format path/to/code/           # Format a specific directory.
```

### Rule Selection

```bash
# Enable specific rules.
ruff check --select F401,F403 --quiet

# Extend default rules with additional categories.
ruff check --extend-select B

# Show all files Ruff will analyze.
ruff check --show-files

# Inspect effective settings for a file.
ruff check --show-settings path/to/file.py
```

### Configuration via `pyproject.toml`

```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "B", "UP", "I"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Configuration via `ruff.toml`

```toml
line-length = 88
target-version = "py310"

[lint]
select = ["E4", "E7", "E9", "F", "B", "UP", "I"]
ignore = ["E501"]

[lint.per-file-ignores]
"__init__.py" = ["E402"]

[format]
quote-style = "double"
indent-style = "space"
```

### Suppressing Violations

```python
# Inline noqa — ignore specific rule on this line.
x = 1  # noqa: F841

# Ignore multiple rules on one line.
i = 1  # noqa: E741, F841

# Ignore all violations on a line.
x = 1  # noqa

# File-level suppression (place near top of file).
# ruff: noqa: F841

# Block-level suppression.
# ruff: disable[E501]
long_string = "Lorem ipsum dolor sit amet ..."
# ruff: enable[E501]
```

### Pre-commit Integration

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.4.10
  hooks:
    - id: ruff-check
      args: [--fix]
    - id: ruff-format
```

### GitHub Actions

```yaml
name: Ruff
on: [push, pull_request]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v3
```

## Advanced Topics

**Linter Deep Dive**: Rule selection, fix safety, error suppression mechanisms → [The Ruff Linter](reference/01-the-ruff-linter.md)

**Formatter Deep Dive**: Black compatibility, configuration options, docstring formatting, f-string handling, format suppression → [The Ruff Formatter](reference/02-the-ruff-formatter.md)

**Configuration Reference**: File discovery, hierarchical config, CLI flags, per-file-ignores, plugin settings → [Configuring Ruff](reference/03-configuring-ruff.md)

**Rules and Settings**: Rule categories, key settings, preview mode, versioning policy → [Rules and Settings](reference/04-rules-and-settings.md)
