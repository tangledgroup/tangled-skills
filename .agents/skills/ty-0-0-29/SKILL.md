---
name: ty-0-0-29
description: A skill for using ty 0.0.29, an extremely fast Python type checker and language server written in Rust that is 10x-100x faster than mypy and Pyright with comprehensive diagnostics, configurable rule levels, and advanced typing features including intersection types, redeclarations, and gradual type support. Use when type checking Python code, setting up editor integrations for real-time type checking, configuring type checking rules, suppressing specific violations, or needing fast incremental analysis in IDEs.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - python
  - type-checking
  - static-analysis
  - language-server
  - mypy-alternative
  - pyright-alternative
  - rust
  - performance
category: tooling
external_references:
  - https://docs.astral.sh/ty/
  - https://github.com/astral-sh/ty
---

# ty 0.0.29

## Overview

ty is an extremely fast Python type checker written in Rust by Astral (the same team behind Ruff and uv). It is 10x-100x faster than mypy and Pyright while providing comprehensive diagnostics, configurable rule levels, and advanced type system features including intersection types, redeclarations, and gradual type support.

ty supports all typing features described in the [Python typing specification](https://typing.python.org/en/latest/spec/index.html). Beyond standard type checking, ty provides a full-featured language server for IDE integration with diagnostics, code completions, go-to-definition, hover information, inlay hints, rename refactoring, and more.

Key capabilities:
- **Blazing fast**: Written in Rust with parallel analysis and fine-grained incrementality
- **Type system**: Intersection types (`A & B`), redeclarations, gradual guarantee, fixpoint iteration
- **Configuration**: `pyproject.toml` (`[tool.ty]`) or standalone `ty.toml`, with per-file overrides
- **Language server**: Full LSP support for VS Code, Neovim, Zed, PyCharm (2025.3+), Emacs, and any LSP-compatible editor
- **Watch mode**: Incremental rechecking on file changes with fine-grained dependency tracking
- **Python versions**: Supports targeting Python 3.7 through 3.15

## When to Use

- Type checking Python codebases with fast feedback (CI/CD, pre-commit, or interactive)
- Setting up real-time type checking in editors via the language server
- Migrating from mypy or Pyright to a faster type checker
- Configuring rule levels and suppression comments for type violations
- Working with advanced type system features like intersection types and redeclarations
- Needing fast incremental analysis in IDEs on large projects

## Installation / Setup

### Quick start without installation

```bash
uvx ty check
```

### Add to your project (recommended)

```bash
uv add --dev ty
uv run ty check
```

To update:

```bash
uv lock --upgrade-package ty
```

### Install globally with uv

```bash
uv tool install ty@latest
ty check
```

### Standalone installer

macOS/Linux:

```bash
curl -LsSf https://astral.sh/ty/install.sh | sh
```

Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/ty/install.ps1 | iex"
```

Other methods: pipx (`pipx install ty`), pip, mise, GitHub Releases, Docker, Bazel.

## Core Concepts

### Running the type checker

```bash
ty check              # Check all Python files in current directory
ty check example.py   # Check specific file
ty check --watch      # Watch mode with incremental rechecking
```

### Configuration files

ty searches for `pyproject.toml` (reading `[tool.ty]`) or `ty.toml` in the current and parent directories. `ty.toml` takes precedence over `pyproject.toml`. User-level config: `~/.config/ty/ty.toml` (macOS/Linux) or `%APPDATA%\ty\ty.toml` (Windows).

```toml
# pyproject.toml
[tool.ty.rules]
index-out-of-bounds = "ignore"

# ty.toml (equivalent, takes precedence if both exist)
[rules]
index-out-of-bounds = "ignore"
```

### Rule levels

Each rule can be set to `error` (exit code 1), `warn` (warning only), or `ignore` (disabled). Configure via CLI flags (`--error`, `--warn`, `--ignore`) or in config files. Use `all` to set a default for all rules.

```bash
ty check --error all
ty check --ignore redundant-cast --warn unused-ignore-comment
```

### Environment discovery

ty discovers installed packages from the active virtual environment (`VIRTUAL_ENV`), `.venv` in project root, or `python3`/`python` on PATH. Use `--python` to specify explicitly.

### Python version targeting

By default, ty uses the lower bound of `project.requires-python` from `pyproject.toml`, then falls back to virtual environment metadata, then defaults to 3.14. Set explicitly with `--python-version` or `environment.python-version`.

## Advanced Topics

**Type System**: Intersection types, redeclarations, gradual guarantee, fixpoint iteration → See [Type System](reference/01-type-system.md)

**Configuration**: Rules, overrides, environment settings, exclusions → See [Configuration](reference/02-configuration.md)

**CLI Reference**: Commands, options, exit codes, environment variables → See [CLI Reference](reference/03-cli-reference.md)

**Editor Integration**: VS Code, Neovim, Zed, PyCharm, Emacs, LSP features → See [Editor Integration](reference/04-editor-integration.md)

**Suppression and FAQ**: Suppression comments, typing questions, common issues → See [Suppression and FAQ](reference/05-suppression-and-faq.md)
