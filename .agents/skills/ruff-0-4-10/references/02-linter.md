# The Ruff Linter

The Ruff Linter is an extremely fast Python linter designed as a drop-in replacement for Flake8 (plus dozens of plugins), isort, pydocstyle, pyupgrade, autoflake, and more.

## Running the Linter

### Basic Usage

```shell
# Lint all files in current directory
ruff check

# Lint specific files or directories
ruff check src/
ruff check example.py
ruff check path/to/code/

# Auto-fix fixable issues
ruff check --fix

# Watch mode (re-lint on change)
ruff check --watch
```

**Note:** As of Ruff v0.1.7, the default path is the current working directory (`.`).

### Output Formats

```shell
# Default (human-readable)
ruff check

# JSON output (for CI/CD)
ruff check --output-format json

# Concise output
ruff check --output-format concise

# Text with full paths
ruff check --output-format full
```

## Rule Selection

Ruff supports 800+ lint rules across 50+ plugins. Rules are identified by codes like `F401` (Pyflakes) or `E501` (pycodestyle).

### Default Rules

By default, Ruff enables:
- `E4`, `E7`, `E9` - pycodestyle errors
- `F` - Pyflakes

### Selecting Rules

**pyproject.toml:**
```toml
[tool.ruff.lint]
# Enable specific rules
select = ["E", "F", "B", "I", "UP"]

# Or enable all rules (use with caution)
select = ["ALL"]
```

**Command-line:**
```shell
# Add rules to defaults
ruff check --select B

# Override defaults completely
ruff check --select E,F,B,I
```

### Extending Rules

Add rules to the default set:

```toml
[tool.ruff.lint]
# Start with defaults, add more
extend-select = ["B", "UP", "SIM"]
```

**Command-line:**
```shell
ruff check --extend-select B
```

### Ignoring Rules

```toml
[tool.ruff.lint]
# Ignore specific rules
ignore = ["E501", "D100"]

# Or ignore entire categories
ignore = ["D"]  # Ignore all pydocstyle rules
```

**Command-line:**
```shell
ruff check --ignore E501
```

### Rule Selection Precedence

When multiple sources specify rules, Ruff uses this priority:
1. CLI `--select` (highest priority)
2. Current `pyproject.toml` `select`
3. Inherited config files
4. Defaults (lowest priority)

Then `extend-select` and `ignore` are applied as adjustments.

## Fixes

Ruff can automatically fix many lint violations.

### Safe vs Unsafe Fixes

**Safe fixes:** Preserve code meaning and intent
- Remove unused imports (`F401`)
- Fix syntax errors (`E999`)
- Update type annotations (`UP035`)

**Unsafe fixes:** Could change behavior
- Replace `list(...)[0]` with `next(iter(...))` (changes exception type)
- Reorder imports (might break relative imports)

### Applying Fixes

```shell
# Apply safe fixes only (default)
ruff check --fix

# Show unsafe fixes without applying
ruff check --unsafe-fixes

# Apply all fixes (safe + unsafe)
ruff check --fix --unsafe-fixes
```

**Configuration:**
```toml
[tool.ruff.lint]
# Enable unsafe fixes by default
unsafe-fixes = true
```

### Fix Safety per Rule

Adjust safety for specific rules:

```toml
[tool.ruff.lint]
# Promote unsafe fixes to safe
extend-safe-fixes = ["F601"]

# Demote safe fixes to unsafe
extend-unsafe-fixes = ["UP034"]
```

### Disabling Fixes

Limit which rules can be auto-fixed:

```toml
[tool.ruff.lint]
# Only fix these rules
fixable = ["F401", "F403"]

# Or fix everything except these
fixable = ["ALL"]
unfixable = ["F401"]
```

## Rule Categories

Ruff organizes rules into plugins:

| Prefix | Plugin | Description |
|--------|--------|-------------|
| E | pycodestyle | Error-style warnings |
| F | Pyflakes | Pyflakes rules |
| B | flake8-bugbear | Bug detection |
| I | isort | Import sorting |
| UP | pyupgrade | Modernize syntax |
| SIM | flake8-simplify | Simplify code |
| D | pydocstyle | Docstring conventions |
| N | pep8-naming | Naming conventions |
| C4 | flake8-comprehensions | Comprehension checks |
| ISC | flake8-implicit-str-concat | String concatenation |
| Q | flake8-quotes | Quote style |
| S | flake8-bandit | Security issues |
| T20 | flake8-print | Print statements |

See [Rules](./04-rules.md) for complete rule documentation.

## Recommended Configurations

### Minimal (Default)

```toml
[tool.ruff.lint]
# Use Ruff defaults: E4, E7, E9, F
select = ["E4", "E7", "E9", "F"]
```

### Popular (Recommended)

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

### Strict

```toml
[tool.ruff.lint]
select = ["ALL"]
# Or explicitly list all desired categories
select = [
    "E", "F", "B", "I", "UP", "SIM", "D", "N",
    "C4", "ISC", "Q", "S", "T20", "W", "ANN",
]
```

## Exit Codes

Ruff uses standard exit codes:
- **0:** No errors found
- **1:** Errors found (or unsafe fixes available with `--exit-non-zero-on-unfixable`)
- **2:** Fatal error (configuration issue, etc.)

### Exit on Warnings

```shell
# Exit non-zero on warnings
ruff check --exit-zero

# Exit non-zero on unfixable violations
ruff check --exit-non-zero-on-unfixable
```

## Performance Tips

1. **Use `--fix` in CI** - Auto-fix in PRs, require clean lint in main
2. **Exclude unnecessary directories** - Speed up checks by excluding venv, build dirs
3. **Enable caching** - Ruff caches results automatically (`.ruff_cache`)
4. **Parallel execution** - Ruff uses multiple CPU cores automatically

## Troubleshooting

### Rule Not Working

```toml
# Check if rule is selected
[tool.ruff.lint]
select = ["E", "F", "B"]  # Must include the category

# Or add it explicitly
extend-select = ["B009"]   # Specific rule code
```

### Too Many Errors

Start with defaults and add rules gradually:

```toml
[tool.ruff.lint]
# Step 1: Just Pyflakes
select = ["F"]

# Step 2: Add pycodestyle errors
select = ["E", "F"]

# Step 3: Add bugbear
extend-select = ["B"]
```

### False Positives

Use per-file ignores or noqa comments:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["F401", "F811"]
```

See [Suppression](./05-suppression.md) for details.

## Next Steps

- Configure [rules](./04-rules.md) for your project's needs
- Set up [suppression](./05-suppression.md) for false positives
- Configure the [formatter](./03-formatter.md) for consistent code style
- Customize [configuration](./06-configuration.md) for advanced settings
