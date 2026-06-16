# Configuration

## Configuration files

ty searches for configuration in the current directory and parent directories:

| File | Format | Precedence |
|------|--------|-----------|
| `ty.toml` | Top-level keys | Highest (overrides pyproject.toml) |
| `pyproject.toml` | Under `[tool.ty]` | Lower than ty.toml |
| `~/.config/ty/ty.toml` | Top-level keys (user-level) | Lowest |

When both `ty.toml` and `pyproject.toml` exist in the same directory, `ty.toml` wins entirely — the `[tool.ty]` section in `pyproject.toml` is ignored.

CLI flags override all persistent configuration.

## Rules

Configure which checks run and their severity:

```toml
# pyproject.toml
[tool.ty.rules]
all = "error"                        # Default: error for all rules
redundant-cast = "ignore"            # Disable a specific rule
possibly-unresolved-reference = "warn"  # Downgrade to warning
```

```toml
# ty.toml (same structure, no [tool.ty] prefix)
[rules]
all = "error"
redundant-cast = "ignore"
```

Valid severities: `ignore`, `warn`, `error`. Exit code is 1 when any `error`-level diagnostics are found. Use `--error-on-warning` or `[terminal].error-on-warning = true` to also fail on warnings.

## Environment settings

### Python version

```toml
[tool.ty.environment]
python-version = "3.12"
```

Supported: `3.7` through `3.15`. If unspecified, ty infers from `project.requires-python`, then the active venv, then falls back to latest stable (currently 3.14).

### Python platform

```toml
[tool.ty.environment]
python-platform = "linux"   # win32, darwin, android, ios, linux, all
```

Affects `sys.platform` specialization and conditional typeshed definitions. Defaults to the current system's platform.

### Python environment path

```toml
[tool.ty.environment]
python = "./custom-venv"    # Path to interpreter or venv directory
```

Accepts: interpreter path (`.venv/bin/python3`), venv directory (`.venv`), or `sys.prefix` (`/usr`). Usually unnecessary when using `uv run` or an activated venv.

### Source roots

```toml
[tool.ty.environment]
root = ["./src", "./lib"]   # Priority order: first has highest priority
```

Auto-detected defaults: project root (`.`), `./src`, `./python`, and `./<project-name>` if a nested `<project-name>/` package exists.

### Extra search paths

```toml
[tool.ty.environment]
extra-paths = ["./shared/stubs"]
```

Advanced option for non-standard module locations. Similar to mypy's `MYPYPATH`.

### Custom typeshed

```toml
[tool.ty.environment]
typeshed = "/path/to/custom/typeshed"
```

Override the vendored typeshed with a custom directory.

## Analysis settings

### Allowed unresolved imports

Suppress `unresolved-import` for specific modules using glob patterns:

```toml
[tool.ty.analysis]
allowed-unresolved-imports = [
    "test.**",           # All test.* modules
    "!test.foo",         # Except test.foo
    "*test*.**",         # Any module component containing 'test'
]
```

Glob syntax: `*` matches within a component, `**` matches any number of components. Prefix with `!` to exclude. Later entries take precedence.

### Replace imports with Any

Replace entire modules with `typing.Any` (suppresses all import diagnostics):

```toml
[tool.ty.analysis]
replace-imports-with-any = ["pandas.**", "numpy.**"]
```

Useful for heavy dependencies where you don't need type checking of their internals.

### Respect type: ignore comments

```toml
[tool.ty.analysis]
respect-type-ignore-comments = false  # Only accept ty: ignore, not type: ignore
```

Defaults to `true`. Set to `false` when running alongside other type checkers.

## File inclusion/exclusion

```toml
[tool.ty.src]
include = ["src", "tests"]
exclude = [
    "generated/**",
    "*.proto",
    "!generated/important.py"   # Re-include specific file
]
respect-ignore-files = true      # Respect .gitignore (default: true)
```

Default exclusions include: `.git/`, `.venv/`, `node_modules/`, `.mypy_cache/`, `dist/`, `__pycache__/`, and many more.

Glob syntax follows gitignore-style patterns. All paths are anchored relative to the project root.

## Per-file overrides

Apply different rules to specific files:

```toml
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]
exclude = ["tests/conftest.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"
invalid-assignment = "ignore"
```

Multiple overrides can match the same file; later overrides take precedence. Override rules take priority over global rules for matching files.

## Terminal settings

```toml
[tool.ty.terminal]
output-format = "concise"       # full, concise, github, gitlab, junit
error-on-warning = true          # Exit 1 on warnings too
```

## Deprecated settings

- `[tool.ty.src].root` — deprecated; use `[tool.ty.environment].root` instead

## CLI configuration override

Pass a single config option from the command line:

```bash
ty check --config 'rules.possibly-unresolved-reference = "warn"'
```

This always takes precedence over all configuration files.

## Configuration file path

```bash
ty check --config-file ./custom/ty.toml
# or set TY_CONFIG_FILE environment variable
```

When using `--config-file`, only `ty.toml` format is accepted (no `pyproject.toml`).
