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
required_environment_variables: []

external_references:
  - https://docs.astral.sh/ty/
  - https://github.com/astral-sh/ty
---

# ty 0.0.29


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for using ty 0.0.29, an extremely fast Python type checker and language server written in Rust that is 10x-100x faster than mypy and Pyright with comprehensive diagnostics, configurable rule levels, and advanced typing features including intersection types, redeclarations, and gradual type support. Use when type checking Python code, setting up editor integrations for real-time type checking, configuring type checking rules, suppressing specific violations, or needing fast incremental analysis in IDEs.

An extremely fast Python type checker and language server, written in Rust. ty is 10x-100x faster than mypy and Pyright with comprehensive diagnostics, configurable rule levels, support for redeclarations and partially typed code, and advanced typing features like intersection types and sophisticated reachability analysis.

## When to Use

- Type checking Python projects with fast incremental analysis
- Setting up real-time type checking in editors (VS Code, Neovim, PyCharm, Zed, Emacs)
- Replacing mypy or Pyright for faster feedback loops
- Configuring granular type checking rules and severity levels
- Suppression of specific type errors while maintaining overall type safety
- Projects with mixed typed/untyped code (gradual typing support)
- Codebases requiring intersection types and advanced type narrowing

## Quick Start

### Run Without Installation

Use uvx to quickly get started:

```bash
uvx ty check
```

ty will check all Python files in the working directory or project by default.

### Installation

**Add as project dependency (recommended):**
```bash
uv add --dev ty
uv run ty check
```

**Install globally with uv:**
```bash
uv tool install ty@latest
ty check
```

**Standalone installer:**
```bash
# macOS and Linux
curl -LsSf https://astral.sh/ty/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/ty/install.ps1 | iex"
```

**Other methods:** pipx, pip, mise, Docker, GitHub Releases

See [Installation](references/01-installation.md) for all installation options.

## Core Features

### Type Checking

```bash
# Check current directory
ty check

# Check specific files
ty check example.py src/

# Watch mode (incremental rechecking)
ty check --watch

# Show rule violations as warnings instead of errors
ty check --warn possibly-unresolved-reference

# Ignore specific rules
ty check --ignore redundant-cast
```

See [Type Checking](references/02-type-checking.md) for detailed usage.

### Rule Configuration

ty's diagnostics are associated with configurable rules:

```bash
# Set rule severity levels
ty check \
  --error possibly-missing-attribute \
  --warn unused-ignore-comment \
  --ignore redundant-cast

# Error on all rules
ty check --error all
```

Or configure in `pyproject.toml`:

```toml
[tool.ty.rules]
possibly-missing-attribute = "error"
unused-ignore-comment = "warn"
redundant-cast = "ignore"
```

See [Rules](references/03-rules.md) for the complete rules reference.

### Suppression Comments

Suppress specific violations inline:

```python
# Suppress specific rule
a = 10 + "test"  # ty: ignore[unsupported-operator]

# Multiple rules on one line
sum_three_numbers("one", 5)  # ty: ignore[missing-argument, invalid-argument-type]

# Standard type: ignore format (PEP 484)
result = unknown_function()  # type: ignore

# Combined suppressions
value = calculate()  # ty: ignore[invalid-type]  # fmt: skip

# Suppress entire file
# ty: ignore[invalid-argument-type]

def main():
    ...
```

See [Suppression](references/04-suppression.md) for detailed suppression patterns.

### Editor Integration

ty provides a language server with code navigation, completions, code actions, auto-import, inlay hints, and on-hover help.

**VS Code:** Install the official [ty extension](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty)

**Neovim:** Use nvim-lspconfig:
```lua
vim.lsp.enable('ty')
```

**PyCharm:** Enable in Settings → Python → Tools → ty (version 2025.3+)

**Zed:** Add to `settings.json`:
```json
{
  "languages": {
    "Python": {
      "language_servers": ["ty", "ruff"]
    }
  }
}
```

See [Editor Integration](references/05-editors.md) for complete setup instructions.

## Advanced Features

### Intersection Types

ty has first-class support for intersection types (`A & B` means "both A and B"):

```python
def output_as_json(obj: Serializable) -> str:
    if isinstance(obj, Versioned):
        reveal_type(obj)  # reveals: Serializable & Versioned
        return str({
            "data": obj.serialize_json(),
            "version": obj.version
        })
```

### Redeclarations

Reuse symbols with different types within the same scope:

```python
def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")
    return [Path(p) for p in paths]
```

### Gradual Guarantee

ty avoids false positives in untyped code:

```python
class RetryPolicy:
    max_retries = None

policy = RetryPolicy()
policy.max_retries = 1  # No error (type is Unknown | None)
```

See [Type System](references/06-type-system.md) for advanced type system features.

## Configuration

### Environment Configuration

Configure Python environment and platform:

```toml
[tool.ty.environment]
python = "./.venv"              # Path to Python environment
python-version = "3.12"         # Target Python version
python-platform = "linux"       # Target platform (win32, darwin, linux, all)
extra-paths = ["./shared"]      # Additional module search paths
root = ["./src", "./lib"]       # Project root directories
```

### Analysis Configuration

Control import resolution and type ignore behavior:

```toml
[tool.ty.analysis]
allowed-unresolved-imports = ["test.**", "!test.foo"]  # Suppress unresolved imports
replace-imports-with-any = ["pandas.**", "numpy.**"]   # Replace with Any
respect-type-ignore-comments = true                    # Respect PEP 484 ignores
```

### File Overrides

Apply different rules to specific files:

```toml
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]
[rules]
possibly-unresolved-reference = "ignore"
```

See [Configuration](references/07-configuration.md) for complete settings reference.

## Reference Files

- [`references/01-installation.md`](references/01-installation.md) - Installation methods and setup
- [`references/02-type-checking.md`](references/02-type-checking.md) - Running the type checker, file selection, watch mode
- [`references/03-rules.md`](references/03-rules.md) - Rule levels, configuration, and rule reference
- [`references/04-suppression.md`](references/04-suppression.md) - Inline suppression comments and directives
- [`references/05-editors.md`](references/05-editors.md) - Editor integrations (VS Code, Neovim, PyCharm, Zed, Emacs)
- [`references/06-type-system.md`](references/06-type-system.md) - Intersection types, redeclarations, gradual guarantee, reachability analysis
- [`references/07-configuration.md`](references/07-configuration.md) - Complete configuration reference (rules, environment, analysis, overrides)

## Common Workflows

### Quick Type Check

```bash
# Run type checker on current project
ty check

# Check with watch mode for development
ty check --watch

# Check specific files
ty check src/my_module.py
```

### Migrate from mypy

```bash
# Install ty
uv add --dev ty

# Replace mypy in CI/CD
# Before: mypy src/
# After:  ty check src/

# Convert mypy ignore comments (optional)
# # type: ignore[arg-type] → # ty: ignore[invalid-argument-type]
```

### Migrate from Pyright

```bash
# Install ty
uv add --dev ty

# Update editor settings to use ty language server
# VS Code: Install ty extension (auto-disables Python extension LSP)

# ty uses same PEP standards, minimal config changes needed
```

### Configure for Project

```toml title="pyproject.toml"
[tool.ty]
[tool.ty.environment]
python-version = "3.12"

[tool.ty.rules]
all = "error"
possibly-unresolved-reference = "warn"

[tool.ty.analysis]
allowed-unresolved-imports = ["tests.**"]
```

## Troubleshooting

### Import Errors

If ty can't find your dependencies:

```bash
# Ensure virtual environment is activated or use uv run
uv run ty check

# Or specify Python environment explicitly
ty check --python ./.venv

# Configure in pyproject.toml
# [tool.ty.environment]
# python = "./.venv"
```

### Platform-Specific Issues

```toml
# Specify target platform for cross-platform projects
[tool.ty.environment]
python-platform = "all"  # Assume code runs on any platform
```

### Too Many False Positives

```toml
# Relax specific rules
[tool.ty.rules]
possibly-unresolved-reference = "warn"  # Instead of error
unused-ignore-comment = "ignore"        # Disable unused ignore warnings

# Allow unresolved imports for testing
[tool.ty.analysis]
allowed-unresolved-imports = ["tests.**", "fixtures.**"]
```

### Suppression Not Working

```python
# Ensure correct syntax
result = func()  # ty: ignore[specific-rule-name]

# For multi-line violations, place comment on first or last line
sum_three_numbers(  # ty: ignore[missing-argument]
    1,
    2
)

# Check rule name is correct (see rules reference)
```

## Performance Tips

1. **Use watch mode** during development for incremental checking
2. **Configure allowed-unresolved-imports** to skip third-party modules without stubs
3. **Enable language server** in editor for real-time feedback without manual runs
4. **Set python-version** to match your target deployment for accurate analysis
5. **Use overrides** to relax rules in test files or legacy code

## Online Playground

Try ty without installation at [play.ty.dev](https://play.ty.dev) - great for sharing bug reports and testing type system features.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
