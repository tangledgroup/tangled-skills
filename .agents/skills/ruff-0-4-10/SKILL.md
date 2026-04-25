---
name: ruff-0-4-10
description: A skill for using Ruff 0.4.10, an extremely fast Python linter and formatter written in Rust that replaces Flake8, isort, pydocstyle, pyupgrade, autoflake, Black, and more with unified configuration and 10x-100x faster performance. Use when linting Python code for style and correctness issues, formatting code consistently, configuring rule selection across 800+ lint rules, suppressing violations with noqa comments, or needing fast incremental analysis in CI/CD pipelines and editors.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - python
  - linting
  - formatting
  - code-quality
  - flake8-alternative
  - black-alternative
  - isort-alternative
  - rust
  - performance
category: tooling
required_environment_variables: []
---

# Ruff 0.4.10


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for using Ruff 0.4.10, an extremely fast Python linter and formatter written in Rust that replaces Flake8, isort, pydocstyle, pyupgrade, autoflake, Black, and more with unified configuration and 10x-100x faster performance. Use when linting Python code for style and correctness issues, formatting code consistently, configuring rule selection across 800+ lint rules, suppressing violations with noqa comments, or needing fast incremental analysis in CI/CD pipelines and editors.

An extremely fast Python linter and formatter written in Rust. Ruff replaces Flake8 (plus dozens of plugins), isort, pydocstyle, pyupgrade, autoflake, Black, and more with unified configuration and 10x-100x faster performance. It supports 800+ lint rules across 50+ built-in plugins and provides a Black-compatible formatter.

## When to Use

- Linting Python code for style, correctness, and best practices
- Formatting code consistently with Black compatibility
- Replacing multiple tools (Flake8, isort, Black, pyupgrade) with one
- Configuring granular rule selection from 800+ available rules
- CI/CD pipelines requiring fast feedback loops
- Editor integrations for real-time linting and formatting
- Migrating from Flake8 or Black configurations

## Quick Start

### Installation

**pip (recommended):**
```bash
pip install ruff
```

**Other methods:**
- **Homebrew:** `brew install ruff`
- **Conda:** `conda install -c conda-forge ruff`
- **Docker:** `docker run -v .:/io --rm ghcr.io/astral-sh/ruff check`
- **Arch Linux:** `pacman -S ruff`

See [Installation](references/01-installation.md) for all installation options.

### Linting

```bash
# Check current directory
ruff check

# Check specific files or directories
ruff check src/
ruff check example.py

# Auto-fix fixable issues
ruff check --fix

# Show which issues can be fixed
ruff check --show-source

# Watch mode (re-lint on change)
ruff check --watch
```

### Formatting

```bash
# Format current directory
ruff format

# Check without writing
ruff format --check

# Format specific files
ruff format src/
```

See [Linter](references/02-linter.md) and [Formatter](references/03-formatter.md) for detailed usage.

## Core Features

### Rule Selection

Ruff supports 800+ lint rules across 50+ plugins:

**Default rules:** E4, E7, E9, F (pycodestyle + Pyflakes)

**Common configuration:**
```toml
[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "B",      # flake8-bugbear
    "I",      # isort
    "UP",     # pyupgrade
    "SIM",    # flake8-simplify
]
```

See [Rules](references/04-rules.md) for the complete rules reference.

### Fixes

Ruff can automatically fix many issues:

```bash
# Apply safe fixes
ruff check --fix

# Show unsafe fixes
ruff check --unsafe-fixes

# Apply all fixes (safe + unsafe)
ruff check --fix --unsafe-fixes
```

**Fix safety:**
- **Safe:** Meaning and intent preserved (e.g., removing unused imports)
- **Unsafe:** Could change behavior (e.g., exception type changes)

### Error Suppression

Suppress violations inline with `noqa` comments:

```python
# Ignore specific rule
x = 1  # noqa: F841

# Ignore multiple rules
i = 1  # noqa: E741, F841

# Ignore all violations on line
value = unknown()  # noqa

# Ignore for entire file (at top of file)
# noqa: F401
```

See [Suppression](references/05-suppression.md) for detailed patterns.

### Configuration

Configure Ruff in `pyproject.toml`, `ruff.toml`, or `.ruff.toml`:

```toml
[tool.ruff]
# Line length (same as Black)
line-length = 88

[tool.ruff.lint]
# Enable rules
select = ["E", "F", "B", "I"]

# Ignore specific rules
ignore = ["E501"]

# Per-file ignores
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["F401", "F811"]

[tool.ruff.format]
# Use single quotes
quote-style = "single"

# Format docstring code examples
docstring-code-format = true
```

See [Configuration](references/06-configuration.md) for complete settings.

## Editor Integration

Ruff integrates with most Python editors via LSP or native plugins:

- **VS Code:** Use the official Ruff extension
- **Neovim:** Use `nvim-lspconfig` or `ruff.nvim`
- **PyCharm:** Built-in support (2023.2+)
- **Vim:** Use `ALE` or `coc-pyright`
- **Emacs:** Use `eglot` or `lsp-mode`

See [Integrations](references/07-integrations.md) for setup instructions.

## Common Workflows

### Quick Lint and Fix

```bash
# Check and auto-fix
ruff check --fix

# Check with unsafe fixes
ruff check --fix --unsafe-fixes
```

### Format Code

```bash
# Format all files
ruff format

# Check formatting without writing
ruff format --check
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Lint with Ruff
  run: ruff check .

- name: Format check
  run: ruff format --check .
```

### Migration from Flake8

```bash
# Install Ruff
pip install ruff

# Replace flake8 commands
# Before: flake8 src/
# After:  ruff check src/

# Convert configuration (see migration guide)
```

See [Migration](references/08-migration.md) for detailed guides.

## Reference Files

- [`references/01-installation.md`](references/01-installation.md) - Installation methods and setup
- [`references/02-linter.md`](references/02-linter.md) - Linting commands, rule selection, fixes
- [`references/03-formatter.md`](references/03-formatter.md) - Formatting code, Black compatibility, docstring formatting
- [`references/04-rules.md`](references/04-rules.md) - Rule categories, selection strategies, popular rules
- [`references/05-suppression.md`](references/05-suppression.md) - noqa comments, per-file ignores, format suppression
- [`references/06-configuration.md`](references/06-configuration.md) - Complete configuration reference
- [`references/07-integrations.md`](references/07-integrations.md) - Editor integrations and CI/CD setup
- [`references/08-migration.md`](references/08-migration.md) - Migrating from Flake8, Black, isort

## Troubleshooting

### Rules Not Applying

```toml
# Check select/ignore precedence
[tool.ruff.lint]
select = ["E", "F"]  # Base rules
extend-select = ["B"]  # Add more rules
ignore = ["E501"]  # Ignore specific rule
```

### Auto-Fix Not Working

```bash
# Check if rule supports fixing
ruff rule F401  # Shows fix availability

# Enable unsafe fixes if needed
ruff check --fix --unsafe-fixes
```

### Performance Issues

```toml
# Exclude unnecessary directories
[tool.ruff]
exclude = ["venv", "node_modules", "build"]

# Use cache (enabled by default)
# Clear cache if needed: rm -rf .ruff_cache
```

## Best Practices

1. **Start with defaults** - Ruff's default rules catch common errors with zero configuration
2. **Add rules gradually** - Enable one category at a time (e.g., add "B" for bugbear)
3. **Use `--fix` in CI** - Auto-fix in PRs, require clean lint in main branch
4. **Configure per-file ignores** - Relax rules for tests, legacy code, or generated files
5. **Enable docstring formatting** - Format code examples in docstrings automatically
6. **Combine lint and format** - Use Ruff for both to avoid conflicts

## Performance

Ruff is 10x-100x faster than alternative tools:
- **vs Flake8:** 10-100x faster due to Rust implementation
- **vs Black:** 20-300x faster for formatting
- **Incremental analysis:** Fast re-checks with caching
- **Parallel execution:** Automatically uses multiple CPU cores

## Online Resources

- **Documentation:** https://docs.astral.sh/ruff/
- **Rules reference:** https://docs.astral.sh/ruff/rules/
- **GitHub:** https://github.com/astral-sh/ruff
- **Playground:** https://play.ruff.rs/

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
