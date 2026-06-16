---
name: ty
description: >
  Use ty, the extremely fast Python type checker and language server by Astral (creators of uv and Ruff).
  Use this skill whenever the user mentions ty, Python type checking, mypy migration, pyright migration,
  type diagnostics, or needs to configure a Python type checker. Also triggers for questions about
  Python typing features like intersection types, gradual typing, or redeclarations.
  ty is 10x–100x faster than mypy/Pyright and supports full LSP (completions, hover, navigate, etc.).
---

# ty

ty is an extremely fast Python type checker and language server written in Rust, by Astral (creators of uv and Ruff). It offers 10x–100x speedups over mypy and Pyright while providing comprehensive diagnostics, rich editor integration, and advanced type system features like intersection types and reachability-based analysis.

## Overview

ty provides two main capabilities:

- **Type checking** (`ty check`) — Fast static type analysis of Python code with configurable rules, per-file overrides, and suppression comments
- **Language server** (`ty server`) — Full LSP implementation with completions, hover, go-to-definition, rename, inlay hints, signature help, and more

Key design principles:

- Supports partially typed code (gradual guarantee) — no errors for missing annotations by default
- Allows redeclarations of symbols within the same scope
- First-class intersection types for precise narrowing
- Reachability analysis based on type inference (not just pattern matching)
- Fine-grained incremental analysis for sub-millisecond IDE feedback

ty is currently in beta with `0.0.x` versioning. Breaking changes can occur between any two versions.

## Usage

### Quick start

```bash
# Run without installation via uvx
uvx ty check

# Or inside a project with uv
uv run ty check
```

### Type checking

```bash
# Check all Python files in current directory/project
ty check

# Check specific files or directories
ty check src/ tests/test_main.py

# Watch mode — recheck on file changes (uses fine-grained incrementality)
ty check --watch

# Set Python version explicitly
ty check --python-version 3.12

# Point to a custom virtual environment
ty check --python .venv

# Adjust rule severity on the command line
ty check --error all --ignore redundant-cast --warn unused-ignore-comment

# CI-friendly output formats
ty check --output-format github    # GitHub Actions annotations
ty check --output-format gitlab    # GitLab Code Quality JSON
ty check --output-format junit     # JUnit XML report
ty check --output-format concise   # One diagnostic per line
```

### Language server

```bash
# Start the LSP server (used by editors)
ty server
```

Editors connect to `ty server` automatically. See reference files for editor-specific setup.

### Explain rules

```bash
# Get documentation for a specific rule
ty explain rule invalid-argument-type

# List all rules
ty explain rule
```

### Version info

```bash
ty version
ty version --output-format json
```

## Gotchas

- **ty does not warn about missing type annotations.** Unlike mypy's `disallow_untyped_defs`, ty treats unannotated symbols as `Unknown` and only reports errors when the unknown type causes a concrete problem. Use Ruff's `flake8-annotations` (ANN) rules if you need to enforce annotation coverage.

- **`float` annotations accept `int` too.** Per the Python typing spec, `float` means `int | float`. If you need strictly `float`, use `ty_extensions.JustFloat` behind a `TYPE_CHECKING` guard. Same for `complex` → `JustComplex`.

- **Generic containers are invariant.** `list[Subtype]` is not assignable to `list[Supertype]` because lists are mutable. Use `Sequence[T]` (covariant) when mutation isn't needed, or explicitly widen the annotation.

- **`Top[list[Unknown]]` in narrowing results.** When checking `isinstance(x, list)` on a union type like `Item | list[Item]`, ty accounts for possible subclasses of both `Item` and `list`. Use `@final` on `Item` or check `isinstance(x, Item)` first to get cleaner narrowing.

- **ty does not support mypy plugins.** There is no plugin system. Support for popular libraries (pydantic, SQLAlchemy, attrs, django) may be added directly into ty over time.

- **Configuration file precedence:** `ty.toml` overrides `[tool.ty]` in `pyproject.toml` when both exist in the same directory. CLI flags override all files. Project-level config overrides user-level (`~/.config/ty/ty.toml`).

- **Virtual environment discovery:** ty checks `VIRTUAL_ENV`, then looks for `.venv` in project root, then falls back to `python3`/`python` on PATH. When using `uv run`, the venv is detected automatically via `VIRTUAL_ENV`.

- **Suppression comments use `ty: ignore`, not `type: ignore`.** ty supports both formats, but `type: ignore` suppresses all violations on a line. Use `ty: ignore[rule]` for targeted suppression. The `type: ignore[ty:rule]` format works too and is useful when mixing multiple type checkers.

- **Exit code 2 means configuration/CLI errors.** Exit code 0 = no errors, 1 = type errors found, 2 = bad config or CLI options, 101 = internal error. Use `--exit-zero` to always return 0; use `--error-on-warning` to treat warnings as failures.

## References

Detailed reference material loaded on demand:

- [Installation methods](references/01-installation.md) — uvx, pip, standalone installer, Docker, Bazel, shell completion
- [Configuration](references/02-configuration.md) — pyproject.toml / ty.toml settings, overrides, environment options
- [Type system features](references/03-type-system.md) — redeclarations, intersection types, gradual typing, reachability analysis
- [Language server and editors](references/04-language-server.md) — LSP features, VS Code, Neovim, Zed, PyCharm, Emacs settings
- [Rules and suppression](references/05-rules-and-suppression.md) — rule levels, suppression comments, migration from mypy/pyright
- [Environment variables](references/06-environment.md) — TY_CONFIG_FILE, TY_LOG, PYTHONPATH, VIRTUAL_ENV, and more
