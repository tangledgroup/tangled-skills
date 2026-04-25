# Configuration

Ruff can be configured through `pyproject.toml`, `ruff.toml`, or `.ruff.toml` files.

## Configuration Files

### File Types

**pyproject.toml:** (Recommended for projects)
```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "B"]
```

**ruff.toml:** (Ruff-specific)
```toml
line-length = 88

[lint]
select = ["E", "F", "B"]
```

**.ruff.toml:** (Hidden, highest precedence)
Same format as `ruff.toml`

### File Precedence

If multiple files exist in same directory:
1. `.ruff.toml` (highest)
2. `ruff.toml`
3. `pyproject.toml` (lowest)

## Config File Discovery

Ruff searches for configuration files up the directory tree, similar to ESLint:
- Finds closest config file for each file
- Paths in config are relative to config file location
- CLI `--config` overrides all discovery

### Extending Configuration

Inherit from parent config:

```toml
[tool.ruff]
# Extend parent config
extend = "../pyproject.toml"

# Override specific settings
line-length = 100
```

## Common Settings

### Global Settings

```toml
[tool.ruff]
# Exclude directories (default includes venv, node_modules, etc.)
exclude = [".venv", "build", "dist"]

# Additional file extensions to include
extend-include = ["*.ipynb", "*.pyi"]

# Line length (default: 88, same as Black)
line-length = 88

# Indent width (default: 4)
indent-width = 4

# Target Python version (default: py38)
target-version = "py310"

# Project source directories
src = ["src", "lib"]

# Respect .gitignore files (default: true)
respect-gitignore = true
```

### Linter Settings

```toml
[tool.ruff.lint]
# Enable rules
select = ["E", "F", "B", "I", "UP"]

# Add to defaults
extend-select = ["SIM"]

# Ignore specific rules
ignore = ["E501"]

# Allow auto-fix for rules (default: ALL)
fixable = ["ALL"]

# Disable auto-fix for rules
unfixable = ["F401"]

# Enable unsafe fixes (default: false)
unsafe-fixes = true

# Per-file ignores
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["F401", "S101"]
```

### Formatter Settings

```toml
[tool.ruff.format]
# Quote style: "double" (default), "single", "preserve"
quote-style = "double"

# Indent style: "space" (default) or "tab"
indent-style = "space"

# Respect magic trailing commas (default: true)
skip-magic-trailing-comma = false

# Line ending: "auto" (default), "lf", "crlf", "cr"
line-ending = "auto"

# Format docstring code examples (default: false)
docstring-code-format = true

# Line length for docstring code (default: "dynamic")
docstring-code-line-length = 88
```

## Plugin-Specific Settings

### flake8-quotes

```toml
[tool.ruff.lint.flake8-quotes]
inline-quotes = "single"
docstring-quotes = "double"
avoid-escape = true
```

### flake8-type-checking

```toml
[tool.ruff.lint.flake8-type-checking]
runtime-evaluated-base-classes = [
    "pydantic.BaseModel",
]
```

### isort

```toml
[tool.ruff.lint.isort]
# Known first-party packages
known-first-party = ["my_package"]

# Known third-party packages
known-third-party = ["django", "flask"]

# Force single line imports
force-single-line = true

# Lines between top-level imports
lines-between-types = 1
```

### pydocstyle

```toml
[tool.ruff.lint.pydocstyle]
# Convention: "google", "numpy", "pep257"
convention = "google"
```

## Complete Example Configuration

```toml
# pyproject.toml

[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.10"

[tool.ruff]
# Exclude commonly ignored directories
exclude = [".venv", "venv", "build", "dist", "node_modules"]

# Same as Black
line-length = 88
indent-width = 4

# Target Python version
target-version = "py310"

[tool.ruff.lint]
# Enable rules
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "B",      # flake8-bugbear
    "I",      # isort
    "UP",     # pyupgrade
    "SIM",    # flake8-simplify
    "S",      # flake8-bandit (security)
]

# Ignore line length (handled by formatter)
ignore = ["E501"]

# Allow auto-fix for all rules
fixable = ["ALL"]
unfixable = []

# Per-file ignores
[tool.ruff.lint.per-file-ignores]
# Tests can have unused imports and assertions
"tests/*" = ["F401", "S101"]
# __init__.py files often have unused imports
"__init__.py" = ["F401"]

[tool.ruff.format]
# Use single quotes
quote-style = "single"

# Format docstring code examples
docstring-code-format = true

# Use dynamic line length for docstrings
docstring-code-line-length = "dynamic"
```

## Command-Line Overrides

CLI options override config files:

```shell
# Override select
ruff check --select E,F,B

# Override ignore
ruff check --ignore E501

# Override line length
ruff check --line-length 100

# Use specific config file
ruff check --config ./custom-ruff.toml
```

## Environment Variables

```bash
# Set target Python version
export RUFF_TARGET_VERSION="py310"

# Disable cache
export RUFF_NO_CACHE="true"

# Set cache directory
export RUFF_CACHE_DIR="./.ruff_cache"
```

## Troubleshooting

### Settings Not Applying

**Check file location:**
```bash
# Config should be in project root or parent
ls -la pyproject.toml
```

**Verify syntax:**
```toml
# Correct: [tool.ruff] section in pyproject.toml
[tool.ruff]
line-length = 88

# Wrong: Missing [tool.ruff] prefix
[ruff]  # Won't work in pyproject.toml
line-length = 88
```

### Per-File Ignore Not Working

**Check glob pattern:**
```toml
[tool.ruff.lint.per-file-ignores]
# Matches tests/foo.py
"tests/*.py" = ["F401"]

# Matches all Python files in tests/ recursively
"tests/**/*.py" = ["F401"]
```

### Configuration Conflicts

**Check precedence:**
- CLI options > Current config > Parent configs > Defaults
- `.ruff.toml` > `ruff.toml` > `pyproject.toml` (in same directory)

## Best Practices

1. **Use `pyproject.toml`** - Keeps Ruff config with project metadata
2. **Start with defaults** - Ruff's defaults work well for most projects
3. **Document non-obvious settings** - Add comments explaining choices
4. **Use per-file ignores** - Better than disabling rules globally
5. **Pin Ruff version** - In CI/CD to ensure consistency

## Next Steps

- Configure [rules](./04-rules.md) for your project's needs
- Set up [suppression](./05-suppression.md) for false positives
- Integrate with [editors](./07-integrations.md) and CI/CD
