# Rules

Ruff supports 800+ lint rules across 50+ built-in plugins. This guide covers rule selection, popular rules, and configuration strategies.

## Rule Code Format

Each rule has a unique code: `PREFIX###` (e.g., `F401`, `E501`)
- **Prefix:** Plugin source (1-3 letters)
- **Number:** Rule identifier (3 digits)

## Selecting Rules

### Basic Selection

**pyproject.toml:**
```toml
[tool.ruff.lint]
# Enable specific categories
select = ["E", "F", "B"]

# Or enable all rules
select = ["ALL"]
```

**Command-line:**
```shell
ruff check --select E,F,B
```

### Extending Defaults

Add to Ruff's default rules (E4, E7, E9, F):

```toml
[tool.ruff.lint]
extend-select = ["B", "UP", "SIM"]
```

### Ignoring Rules

```toml
[tool.ruff.lint]
ignore = ["E501", "D100"]  # Ignore specific rules
```

## Popular Rule Categories

| Prefix | Plugin | Description | Recommended |
|--------|--------|-------------|-------------|
| **E** | pycodestyle | Style errors (indentation, whitespace) | ✅ Yes |
| **F** | Pyflakes | Syntax errors, undefined names | ✅ Yes (default) |
| **B** | flake8-bugbear | Bug detection | ✅ Yes |
| **I** | isort | Import sorting | ✅ Yes |
| **UP** | pyupgrade | Modernize syntax | ✅ Yes |
| **SIM** | flake8-simplify | Simplify code | ✅ Yes |
| **D** | pydocstyle | Docstring conventions | ⚠️ Careful |
| **N** | pep8-naming | Naming conventions | ⚠️ Careful |
| **S** | flake8-bandit | Security issues | ✅ Yes |
| **ANN** | flake8-annotations | Type annotations | ⚠️ Careful |

## Common Rules by Category

### Pyflakes (F)

| Code | Rule | Description |
|------|------|-------------|
| F401 | unused-import | `x` imported but unused |
| F402 | import-shadowedBy-loop-variable | Import shadowed by loop variable |
| F403 | star-usage | `from x import *` used |
| F405 | undefined-local-with-nested-import | Late redefinition of `x` |
| F601 | multiple-statements | Multiple statements on one line |
| F701 | break-outside-loop | `break` outside loop |
| F811 | redefined-while-unused | Redefined while unused |
| F821 | undefined-name | Undefined name `x` |
| F841 | unused-variable | Local variable `x` is assigned to but never used |

### pycodestyle (E)

| Code | Rule | Description |
|------|------|-------------|
| E402 | module-import-not-at-top-of-file | Module level import not at top |
| E501 | line-too-long | Line too long (>88 chars) |
| E701 | multiple-statements-on-one-line-colon | Multiple statements on one line (:) |
| E702 | multiple-statements-on-one-line-semicolon | Multiple statements on one line (;) |
| E711 | none-comparison | Comparison to None should be `is not` |
| E712 | true-false-comparison | Comparison to True/False should be `is` |
| E721 | type-comparison | Use `isinstance()` instead of type comparison |
| E731 | lambda-assignment | Do not assign a lambda, use a function |

### flake8-bugbear (B)

| Code | Rule | Description |
|------|------|-------------|
| B005 | strip-with-multi-characters | `str.strip()` with multi-character string |
| B006 | mutable-argument-default | Mutable default argument in function |
| B007 | loop-variable-overrides-iterator | Loop variable overrides iterator |
| B009 | getattr-with-default | `getattr(x, 'attr', None)` then check for None |
| B014 | exceptional-set-to-empty-tuple | Exception set to empty tuple |
| B018 | useless-expression | Useless expression not assigned or returned |
| B023 | function-uses-arguments-default | Function uses arguments default value |
| B026 | star-arg-unpacking-after-keyword-arg | Star arg unpacking after keyword arg |
| B904 | raise-without-from-inside-except | Use `raise ... from err` in except block |

### pyupgrade (UP)

| Code | Rule | Description | Fix |
|------|------|-------------|-----|
| UP001 | non-pep585-annotation | Use `list[x]` instead of `List[x]` | ✅ Safe |
| UP003 | non-pep604-annotation | Use `x \| y` instead of `Union[x, y]` | ✅ Safe |
| UP004 | non-pep604-annotation-optional | Use `x \| None` instead of `Optional[x]` | ✅ Safe |
| UP006 | lru-cache-without-parameters | Use `@lru_cache()` instead of `@lru_cache` | ✅ Safe |
| UP007 | format-literals | Use f-string instead of `.format()` | ✅ Safe |
| UP014 | unnecessary-cast-to-int | Unnecessary cast to int | ✅ Safe |
| UP035 | deprecated-import | Import removed in Python 3.x | ✅ Safe |

### isort (I)

| Code | Rule | Description |
|------|------|-------------|
| I001 | missing-required-import | Missing required import |
| I002 | unsorted-imports | Imports are unsorted |
| I003 | incorrectly-placed-standard-library-import | Standard library import out of order |
| I004 | incorrectly-placed-third-party-import | Third-party import out of order |

### flake8-simplify (SIM)

| Code | Rule | Description |
|------|------|-------------|
| SIM101 | multiple-with-statements | Use single `with` statement |
| SIM102 | collapsible-if | Collapsible `if` statements |
| SIM103 | needless-bool | Unnecessary bool conversion |
| SIM108 | if-else-block-instead-of-if-exp | Use ternary instead of if-else |
| SIM114 | if-with-same-true-branches | Combine `if` branches |
| SIM115 | open-file-with-context-handler | Use context manager for file open |

## Configuration Strategies

### Minimal (Default)

```toml
[tool.ruff.lint]
# Just the defaults: E4, E7, E9, F
select = ["E4", "E7", "E9", "F"]
```

### Recommended Starting Point

```toml
[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "B",      # flake8-bugbear (bugs)
    "I",      # isort (imports)
    "UP",     # pyupgrade (modernize)
]
```

### Comprehensive

```toml
[tool.ruff.lint]
select = [
    "E", "F", "B", "I", "UP",  # Core rules
    "SIM", "C4", "ISC",        # Simplifications
    "Q", "S", "T20",           # Style + security
]
ignore = [
    "E501",  # Line length (handled by formatter)
    "D",     # Docstrings (optional)
]
```

### Strict (All Rules)

```toml
[tool.ruff.lint]
select = ["ALL"]
# Ruff auto-disables conflicting rules
```

## Per-File Rule Configuration

Different rules for different files:

```toml
[tool.ruff.lint.per-file-ignores]
# Ignore unused imports in __init__.py
"__init__.py" = ["F401"]

# Relax rules for tests
"tests/*" = ["F401", "F811", "B018"]

# Ignore docstrings in stubs
"*.pyi" = ["D"]

# Multiple patterns
"**/{tests,docs,tools}/*" = ["E402"]
```

## Rule-Specific Configuration

Some rules have plugin-specific settings:

```toml
[tool.ruff.lint]
select = ["Q"]  # Enable flake8-quotes

[tool.ruff.lint.flake8-quotes]
# Use single quotes for strings
inline-quotes = "single"
docstring-quotes = "double"
avoid-escape = true
```

## Viewing Rules

```shell
# Show all available rules
ruff rule --all

# Show specific rule
ruff rule F401

# Show rule with examples
ruff rule E501 --output-format full
```

## Migration Strategies

### From Flake8

```toml
# Common Flake8 plugins and their Ruff equivalents
[tool.ruff.lint]
select = [
    "E", "W",  # pycodestyle (replaces flake8)
    "F",       # Pyflakes (built-in)
    "B",       # flake8-bugbear
    "C4",      # flake8-comprehensions
    "ISC",     # flake8-implicit-str-concat
    "Q",       # flake8-quotes
    "S",       # flake8-bandit
    "T20",     # flake8-print
]
```

### From Black + isort

```toml
[tool.ruff.lint]
select = ["I"]  # isort rules

[tool.ruff.format]
# Ruff formatter replaces Black
```

## Troubleshooting

### Too Many Errors

Start with defaults and add gradually:

```toml
[tool.ruff.lint]
# Step 1: Just F (Pyflakes)
select = ["F"]

# Step 2: Add E (pycodestyle errors)
select = ["E", "F"]

# Step 3: Add B (bugbear)
extend-select = ["B"]
```

### False Positives

Use per-file ignores or noqa comments:

```toml
[tool.ruff.lint.per-file-ignores]
"legacy/*" = ["ALL"]  # Disable all rules for legacy code
```

See [Suppression](./05-suppression.md) for details.

### Rule Not Applying

Check the rule is selected:

```shell
# Check if rule is in selected set
ruff check --select F401

# View rule documentation
ruff rule F401
```

## Next Steps

- Set up [suppression](./05-suppression.md) for false positives
- Configure the [formatter](./03-formatter.md) for code style
- Customize [configuration](./06-configuration.md) for advanced settings
- Integrate with [editors](./07-integrations.md)
