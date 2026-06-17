---
name: ruff-0-4-10
description: >
  Lint, format, and configure Python code with Ruff (v0.4+). Use when the user mentions
  ruff, python linting, python formatting, code quality, replacing flake8/black/isort/pyupgrade,
  pyproject.toml ruff config, ruff check, ruff format, or needs help setting up Python linting
  and formatting. Also triggers for import sorting (isort replacement), docstring checks,
  auto-fixing lint violations, pre-commit hooks with ruff, CI/CD linting pipelines, and
  migrating from flake8 + black + isort to a single tool.
---

# ruff 0.4.10

Ruff is an extremely fast Python linter and code formatter written in Rust. It replaces Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, autoflake, and more — all in one binary executing 10–100× faster.

## Overview

Ruff provides two main capabilities:

- **Linter** (`ruff check`) — Over 800 rules across 50+ rule categories (Pyflakes, pycodestyle, isort, pyupgrade, flake8-bugbear, etc.). Default rules: `E4`, `E7`, `E9`, `F`.
- **Formatter** (`ruff format`) — Black-compatible code formatter with near-identical output (>99.9% line parity on Black-formatted projects).

Both share the same configuration strategy via `pyproject.toml`, `ruff.toml`, or `.ruff.toml`.

## Usage

### Installation

```bash
pip install ruff          # PyPI (any platform, no Rust needed)
brew install ruff         # macOS/Linux Homebrew
conda install -c conda-forge ruff  # Conda
```

### Linting

```bash
ruff check                        # Current directory
ruff check path/to/code/          # Specific directory
ruff check --fix                  # Auto-fix safe violations
ruff check --fix --unsafe-fixes   # Include unsafe fixes
ruff check --select F401,B        # Enable specific rules only
ruff check --add-noqa .           # Add noqa to existing violations (migration)
ruff check --show-files            # See which files will be checked
ruff check --show-settings         # Debug resolved config for a file
```

### Formatting

```bash
ruff format                       # Current directory
ruff format path/to/code/         # Specific directory
ruff format --check               # Dry-run (exit 1 if changes needed)
ruff format --diff                # Show diff without writing
```

### Sorting Imports

Ruff's formatter does not sort imports. Use the linter for that:

```bash
ruff check --select I --fix   # Sort imports via isort rules
ruff format                   # Then format
```

### Common Workflows

**Quick lint and fix:**
```bash
ruff check --fix . && ruff format .
```

**CI check (fail on violations):**
```bash
ruff check . && ruff format --check .
```

**Migrate a codebase incrementally:**
```bash
ruff check --select UP --add-noqa .   # Suppress existing pyupgrade violations
# Then gradually remove noqa comments as you fix them
```

### Configuration Files

Ruff reads config from `pyproject.toml`, `ruff.toml`, or `.ruff.toml` (in that precedence order). Config is hierarchical — the closest file to a given source file wins. Ruff does not merge parent configs; use `extend` for inheritance:

```toml
# ruff.toml
extend = "../ruff.toml"    # Inherit from parent
line-length = 100           # Override specific setting
```

In `pyproject.toml`, prefix sections with `tool.ruff`:

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ruff.format]
quote-style = "single"
```

### Key Configuration Settings

| Setting | Default | Description |
|---|---|---|
| `line-length` | 88 | Max line length (same as Black) |
| `target-version` | py38 | Minimum Python version (`py37`–`py313`) |
| `src` | `["."]` | Directories for first-party import detection |
| `exclude` | `.git`, `.venv`, etc. | Paths to skip discovery |
| `lint.select` | `["E4","E7","E9","F"]` | Rule codes to enable |
| `lint.ignore` | `[]` | Rule codes to disable |
| `lint.per-file-ignores` | `{}` | File-pattern → rule ignores map |
| `preview` | false | Enable unstable rules/features |

### CLI Config Overrides

Some settings have dedicated flags; others use `--config "key = value"`:

```bash
ruff check --select F401 --line-length=100 .
ruff check --config "lint.dummy-variable-rgx = '__.*'" .
ruff format --line-length=120 .
```

### Error Suppression

```python
# Inline: ignore specific rules on a line
x = 1  # noqa: F841

# Inline: ignore all rules on a line
x = 1  # noqa

# File-level: ignore specific rule everywhere in file
# ruff: noqa: F841

# File-level: ignore all rules
# ruff: noqa
```

### Format Suppression

```python
# fmt: off
not_formatted = 3
also_not_formatted = 4
# fmt: on

# Single-statement skip
a = [1, 2, 3, 4, 5]  # fmt: skip
```

## Gotchas

- **`select` replaces, `extend-select` adds** — Using `--select F` on CLI replaces the config's select entirely. Use `--extend-select F` to add on top of existing rules. Same applies in config files: prefer `select` for explicit rule sets, `extend-select` to add categories.

- **`ALL` enables everything including future rules** — Enabling `select = ["ALL"]` means new rules automatically trigger on upgrade. Pin your Ruff version or use explicit `select` lists instead.

- **Formatter-linter conflicts** — Running both linter and formatter can clash on rules like `E501` (line-too-long), `W191` (tab-indentation), `COM812`/`COM819` (trailing commas), `ISC001`/`ISC002` (implicit string concatenation). Ruff's defaults avoid these, but if you enable such rules, add them to `lint.ignore`.

- **Unsafe fixes can change semantics** — By default only safe fixes apply with `--fix`. Some fixes (e.g., `list(x)[0]` → `next(iter(x))`) change exception types. Use `--unsafe-fixes` explicitly when needed.

- **Config discovery is closest-wins, not merged** — Unlike ESLint, Ruff does not cascade settings from parent configs. The nearest config file is used entirely. Use `extend = "../ruff.toml"` for inheritance.

- **`.ruff.toml` > `ruff.toml` > `pyproject.toml`** — If multiple config files exist in the same directory, `.ruff.toml` takes highest precedence.

- **Import sorting requires the linter, not formatter** — `ruff format` does not sort imports. Run `ruff check --select I --fix` then `ruff format`.

- **Preview rules need `preview = true` AND explicit selection** — Even with preview enabled, a preview rule is only active if its code/category is in `select`/`extend-select`. Preview mode alone doesn't auto-enable all preview rules.

- **`src` matters for first-party imports** — If your code lives under `src/`, set `src = ["src"]` or isort will misclassify your imports as third-party.

- **Jupyter notebooks need explicit opt-in** — Add `extend-include = ["*.ipynb"]` to lint/format `.ipynb` files, or pass them directly on the CLI.

- **Exit codes**: `0` = success/no violations, `1` = violations found, `2` = abnormal termination (bad config/CLI). Use `--exit-zero` to always return 0, or `--exit-non-zero-on-fix` to signal when fixes were applied.

## References

Detailed reference material loaded on demand:

- [01-rule-categories.md](references/01-rule-categories.md) — Rule code prefixes (E, F, I, UP, B, etc.) with descriptions and popular rule examples
- [02-configuration.md](references/02-configuration.md) — Complete configuration reference: settings tables, hierarchical config, per-file ignores, isort options, pydocstyle conventions
- [03-linter-deep-dive.md](references/03-linter-deep-dive.md) — Rule selection resolution, fix safety model, noqa system, action comments, output formats, caching
- [04-formatter-deep-dive.md](references/04-formatter-deep-dive.md) — Black compatibility, known deviations, docstring formatting, format suppression pragmas, conflicting lint rules
- [05-integrations.md](references/05-integrations.md) — VS Code, pre-commit, LSP, Neovim, Emacs, GitHub Actions, Docker
