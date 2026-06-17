# Configuration Reference

## Config File Formats

Ruff accepts three config file formats. All use the same schema:

| File | Section Prefix | Notes |
|---|---|---|
| `ruff.toml` | None (root level) | Cleanest format, dedicated to Ruff |
| `.ruff.toml` | None (root level) | Same as `ruff.toml`, higher precedence |
| `pyproject.toml` | `[tool.ruff]` | Co-located with other tool configs |

### Precedence in Same Directory

`.ruff.toml` > `ruff.toml` > `pyproject.toml`

### Hierarchical Discovery

Ruff walks up the directory tree from each analyzed file, finding the **closest** config file. The closest config is used entirely — settings are **not merged** with parent configs. Use `extend` for inheritance.

```
my_project/
├── ruff.toml              # Root config
├── src/
│   └── module/
│       └── ruff.toml      # Overrides root entirely (or extends it)
└── tests/
    └── ruff.toml          # Separate test config
```

### Config Inheritance via `extend`

```toml
# tests/ruff.toml
extend = "../ruff.toml"        # Inherit all settings from parent
line-length = 120               # Override specific setting

[lint]
extend-select = ["PT"]          # Add pytest rules on top
```

Note: `src` paths in the extended config are relative to the *extending* file's directory. If you extend from a subdirectory, adjust `src`:

```toml
extend = "../ruff.toml"
src = ["../src"]
```

## Top-Level Settings

| Setting | Type | Default | Description |
|---|---|---|---|
| `line-length` | int | 88 | Max line length for linter and formatter |
| `indent-width` | int | 4 | Number of spaces per indent level |
| `target-version` | str | `"py38"` | Minimum Python version: `py37`–`py313` |
| `src` | list[str] | `["."]` | Directories for first-party import detection |
| `exclude` | list[str] | `.git`, `.venv`, etc. | Paths to exclude from discovery |
| `extend-exclude` | list[str] | `[]` | Additional paths to exclude (additive) |
| `include` | list[str] | `["*.py", "*.ipy"]` | File patterns to include |
| `extend-include` | list[str] | `[]` | Additional file patterns (additive) |
| `respect-gitignore` | bool | true | Skip files listed in `.gitignore` |
| `force-exclude` | bool | false | Apply exclusions even for direct CLI paths |
| `builtins` | list[str] | `[]` | Additional builtin names to recognize |
| `cache-dir` | str | `.ruff_cache` | Cache directory path |
| `extend` | str | — | Path to another config file to inherit from |
| `per-file-target-version` | dict | `{}` | File-pattern → target version map |
| `show-fixes` | bool | false | Always show available fixes in output |
| `preview` | bool | false | Enable preview rules and features |

## Lint Settings (`[lint]`)

### Rule Selection

| Setting | Type | Description |
|---|---|---|
| `select` | list[str] | Rule codes/categories to enable (replaces defaults) |
| `extend-select` | list[str] | Additional rules on top of `select`/defaults |
| `ignore` | list[str] | Rule codes to disable |
| `fixable` | list[str] | Rules eligible for auto-fix (default: `["ALL"]`) |
| `unfixable` | list[str] | Rules excluded from auto-fix |
| `extend-fixable` | list[str] | Add rules to fixable set |
| `extend-unfixable` | list[str] | Add rules to unfixable set |
| `extend-safe-fixes` | list[str] | Promote unsafe fixes to safe for these rules |
| `extend-unsafe-fixes` | list[str] | Demote safe fixes to unsafe for these rules |

### Per-File Ignores

```toml
[lint.per-file-ignores]
"__init__.py" = ["F401", "E402"]
"**/{tests,docs}/*" = ["T201", "S101"]
"scripts/*.py" = ["E501"]
```

Use `lint.extend-per-file-ignores` to add on top of existing ignores.

### Dummy Variable Regex

```toml
[lint]
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"
```

Controls which underscore-prefixed variables are considered "intentionally unused" (suppressing `F841`).

## isort Settings (`[lint.isort]`)

Ruff's import sorting replaces isort with Black-compatible defaults:

| Setting | Type | Default | Description |
|---|---|---|---|
| `force-single-line` | bool | false | Each import on its own line |
| `force-wrap-aliases` | bool | false | Force `from ... import x as y` wrapping |
| `combine-as-imports` | bool | false | Combine `from x import a, b` statements |
| `required-imports` | list[str] | `[]` | Always add these imports (e.g., `__future__`) |
| `known-first-party` | list[str] | `[]` | Modules always treated as first-party |
| `known-third-party` | list[str] | `[]` | Modules always treated as third-party |
| `known-local-folder` | list[str] | `[]` | Names treated as local folder imports |
| `no-lines-before` | list[str] | `[]` | Module patterns that don't get blank line before them |
| `relative-imports-order` | str | `"closest-to-furthest"` | Sort order for relative imports |
| `split-on-trailing-comma` | bool | true | Respect trailing commas for line splitting |

### Import Action Comments

Ruff respects isort's inline directives:

```python
# isort: skip_file     # Skip sorting for entire file
# ruff: isort: skip_file  # Ruff-prefixed variant

import os
import sys  # isort: skip   # Skip this import
```

## pydocstyle Settings (`[lint.pydocstyle]`)

| Setting | Type | Default | Description |
|---|---|---|---|
| `convention` | str | — | Docstring convention: `"google"`, `"numpy"`, or `"pep257"` |
| `ignore-deprecated` | bool | false | Skip rules for deprecated functions |

Setting a convention automatically disables rules conflicting with that style. Augment by adding specific rules to `select` and relaxing via `ignore`:

```toml
[lint]
select = ["D", "D401"]      # Convention + require imperative mood
ignore = ["D417"]            # Relax: don't require param docs

[lint.pydocstyle]
convention = "google"
```

## Format Settings (`[format]`)

| Setting | Type | Default | Description |
|---|---|---|---|
| `quote-style` | str | `"double"` | `"double"` or `"single"` |
| `indent-style` | str | `"space"` | `"space"` or `"tab"` |
| `skip-magic-trailing-comma` | bool | false | Respect trailing commas for line breaks |
| `line-ending` | str | `"auto"` | `"auto"`, `"lf"`, `"cr"`, `"crlf"` |
| `docstring-code-format` | bool | false | Format code examples inside docstrings |
| `docstring-code-line-length` | str/int | `"dynamic"` | Line length for docstring code; `"dynamic"` uses surrounding code's limit |
| `preview` | bool | false | Enable preview formatting style |

## Preview Settings

Preview can be enabled separately for linting and formatting:

```toml
[lint]
preview = true              # Preview lint rules

[format]
preview = true              # Preview formatting style
```

With `lint.preview = true` and `lint.explicit-preview-rules = true`, preview rules must be selected by their exact code (not category prefix).

## Environment Variables

| Variable | Description |
|---|---|
| `RUFF_OUTPUT_FORMAT` | Default output format for `ruff check` |
| `RUFF_OUTPUT_FILE` | Default output file path |
| `RUFF_NO_CACHE` | Disable cache (equivalent to `--no-cache`) |
| `RUFF_CACHE_DIR` | Override cache directory |
| `NO_COLOR` | Disable color output |
| `FORCE_COLOR` | Force color output |

## User-Level Default Config

When no project config is found, Ruff falls back to a user-specific config:

- macOS: `~/Library/Application Support/ruff/ruff.toml`
- Linux: `~/.config/ruff/ruff.toml`
- Windows: `C:\Users\<User>\AppData\Roaming\ruff\ruff.toml`

## Debugging Configuration

```bash
# See which files will be analyzed
ruff check --show-files

# See resolved settings for a specific file
ruff check path/to/file.py --show-settings

# Use isolated mode (ignore all config files)
ruff check --isolated .
```
