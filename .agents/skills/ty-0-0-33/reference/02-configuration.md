# Configuration

## Configuration Files

ty searches for `pyproject.toml` (reading `[tool.ty]`) or `ty.toml` in the current and parent directories. `ty.toml` takes precedence over `pyproject.toml`.

User-level config: `~/.config/ty/ty.toml` (macOS/Linux, or `$XDG_CONFIG_HOME/ty/ty.toml`) or `%APPDATA%\ty\ty.toml` (Windows). User-level must use `ty.toml` format.

When both project and user config exist, settings are merged with project taking precedence. CLI options override all files.

```toml
# pyproject.toml
[tool.ty.rules]
index-out-of-bounds = "ignore"

# ty.toml (equivalent, no [tool.ty] prefix)
[rules]
index-out-of-bounds = "ignore"
```

## Rules

Rules are individual checks for common issues (incompatible assignments, missing imports, invalid annotations). See the [rules reference](https://ty.dev/rules) for all available rules.

### Rule Levels

- `error`: violations cause exit code 1
- `warn`: warnings only (exit code 0 by default)
- `ignore`: rule disabled

Via CLI:

```bash
ty check \
  --warn unused-ignore-comment \
  --ignore redundant-cast \
  --error possibly-missing-attribute \
  --error possibly-missing-import
```

Via config:

```toml
# pyproject.toml
[tool.ty.rules]
unused-ignore-comment = "warn"
redundant-cast = "ignore"
possibly-missing-attribute = "error"
possibly-missing-import = "error"
```

Set all rules at once with `all`:

```bash
ty check --error all
```

```toml
[tool.ty.rules]
all = "error"
```

## Overrides

Apply different rule configurations to specific files using glob patterns:

```toml
# Relax rules for test files
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"
```

Ignore a rule in generated files but retain enforcement in one file:

```toml
[[tool.ty.overrides]]
include = ["generated/**"]
exclude = ["generated/important.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "ignore"
```

Multiple overrides can match the same file, with later overrides taking precedence. Override rules take precedence over global rules for matching files.

Overrides also support per-override analysis settings:

```toml
[[tool.ty.overrides]]
include = ["src"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "ignore"

[tool.ty.overrides.analysis]
allowed-unresolved-imports = ["test.**", "!test.foo"]
replace-imports-with-any = ["pandas.**", "numpy.**"]
```

## Environment Settings

### python-version

Specifies the target Python version (format `M.m`, e.g., `"3.12"`). Affects allowed syntax and standard library type definitions.

Detection order:
1. `project.requires-python` in `pyproject.toml` (minimum version)
2. Activated/configured Python environment metadata
3. Default: `"3.14"`

```toml
[tool.ty.environment]
python-version = "3.12"
```

Supported versions: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14, 3.15.

### python-platform

Target platform for analyzing `sys.platform` conditions:

```toml
[tool.ty.environment]
python-platform = "win32"
```

Values: `"win32"`, `"darwin"`, `"android"`, `"ios"`, `"linux"`, `"all"`. Default: current platform.

### python

Path to Python environment or interpreter:

```toml
[tool.ty.environment]
python = "./custom-venv-location/.venv"
```

Can be a Python interpreter (`.venv/bin/python3`), virtual environment directory (`.venv`), or system Python prefix (`/usr`).

### root

Root paths for first-party module discovery:

```toml
[tool.ty.environment]
root = ["./src", "./lib", "./vendor"]
```

Auto-detected if unspecified. Always includes project root. Also includes `./src`, `./<project-name>`, and `./python` (if they exist and are not packages).

### extra-paths

Additional module resolution paths (similar to mypy's `MYPYPATH`):

```toml
[tool.ty.environment]
extra-paths = ["./shared/my-search-path"]
```

### typeshed

Custom typeshed directory for stdlib stubs:

```toml
[tool.ty.environment]
typeshed = "/path/to/custom/typeshed"
```

Default: vendored typeshed bundled in the binary.

## Analysis Settings

### allowed-unresolved-imports

Suppress `unresolved-import` for matching module globs:

```toml
[tool.ty.analysis]
allowed-unresolved-imports = ["test.**", "!test.foo"]
```

Glob patterns: `*` matches zero or more chars except `.`, `**` matches any number of module components. Prefix with `!` to exclude.

### replace-imports-with-any

Replace module types with `typing.Any` (even if resolvable):

```toml
[tool.ty.analysis]
replace-imports-with-any = ["pandas.**", "numpy.**"]
```

### respect-type-ignore-comments

Whether to respect `type: ignore` comments (default: `true`):

```toml
[tool.ty.analysis]
respect-type-ignore-comments = false
```

Set to `false` when using ty alongside other type checkers.

## File Exclusions

Control which files ty checks via `src.include` and `src.exclude`:

```toml
[tool.ty.src]
include = ["src", "tests"]
exclude = ["src/generated"]
```

Default exclusions include common directories (`.git`, `__pycache__`, `.venv`, etc.). Remove a default exclusion with `!`:

```toml
[tool.ty.src]
exclude = ["!**/build/"]  # Re-include build directory
```

ty respects `.gitignore` and `.ignore` files by default. Disable with `respect-ignore-files = false`.

Explicit CLI paths bypass exclusions unless `--force-exclude` is used.

Glob patterns follow PEP 639 reduced portable syntax with backslash escaping:
- `src/` — matches directory named `src`
- `*` — any chars except `/`
- `**` — zero or more path components (must form single component)
- `?` — single char except `/`
- `[abc]`, `[0-9]` — character classes

Patterns are anchored to project root. Use `**/src` for prefix matching (note: can slow file discovery).

## Module Discovery

### First-party modules

Searched in project root or `src/` by default. Configure with `environment.root`. A `./python` folder is auto-added if it exists and is not itself a package.

### Third-party modules

Discovered from the configured Python environment (virtual environment's `site-packages`). ty checks for `VIRTUAL_ENV`, then `.venv` in project root, then `python3`/`python` on PATH.

## Exit Codes

- `0`: no violations with severity `error` or higher
- `1`: violations with severity `error` or higher found
- `2`: invalid CLI options, invalid configuration, or IO errors
- `101`: internal error

Use `--exit-zero` to always exit 0. Use `--error-on-warning` to exit 1 on warnings.

## Environment Variables

- `TY_CONFIG_FILE` — path to `ty.toml` (equivalent to `--config-file`)
- `TY_LOG` — log level for verbose output (e.g., `ty=debug` for `-vv`)
- `TY_LOG_PROFILE` — set to `"1"` or `"true"` for flamegraph profiling
- `TY_MAX_PARALLELISM` — upper limit on parallel tasks
- `TY_OUTPUT_FORMAT` — output format (equivalent to `--output-format`)
- `VIRTUAL_ENV` — activated virtual environment
- `CONDA_PREFIX`, `CONDA_DEFAULT_ENV` — Conda environment detection
- `PYTHONPATH` — additional search paths
- `RAYON_NUM_THREADS` — equivalent to `TY_MAX_PARALLELISM`
- `XDG_CONFIG_HOME` — user config directory on Unix
