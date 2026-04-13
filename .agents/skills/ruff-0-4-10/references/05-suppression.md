# Suppression

Ruff supports several mechanisms for suppressing lint errors, from inline comments to per-file configuration.

## noqa Comments (Inline Suppression)

### Single Rule

```python
# Ignore specific rule
x = 1  # noqa: F841

# Multiple rules on same line
i = 1  # noqa: E741, F841
```

### All Rules on Line

```python
# Ignore all violations on this line
value = unknown_function()  # noqa
```

### Multi-line Strings

For docstrings and multi-line strings, place `noqa` after the closing quote:

```python
def foo():
    """
    This is a docstring with an error.
    undefined_variable = 1  # noqa: F841
    """
    pass
```

### File-Level Suppression

Place at the top of the file before any code:

```python
# noqa: F401
# All F401 (unused import) errors ignored in this file

from unused_module import something
```

## Per-File Ignores (Configuration)

Configure different rules for different files:

**pyproject.toml:**
```toml
[tool.ruff.lint.per-file-ignores]
# Ignore unused imports in __init__.py
"__init__.py" = ["F401"]

# Relax rules for test files
"tests/*.py" = ["F401", "F811", "B018"]
"**/test_*.py" = ["S101"]  # Ignore assert usage in tests

# Ignore docstrings in stub files
"*.pyi" = ["D"]

# Multiple patterns for same rules
"**/{tests,docs,tools}/*" = ["E402"]

# Legacy code - ignore everything
"legacy/*" = ["ALL"]
```

### Glob Patterns

Ruff supports these glob patterns:
- `*` - Matches zero or more characters except `/`
- `**` - Matches zero or more directories
- `{a,b}` - Matches either `a` or `b`
- `!` - Negation (in exclude patterns)

**Examples:**
```toml
[tool.ruff.lint.per-file-ignores]
# All Python files in tests directory
"tests/**/*.py" = ["F401"]

# Specific file names
"**/{conftest,setup}.py" = ["F401"]

# Exclude specific files
"!tests/test_critical.py" = []
```

## Format Suppression

### fmt: on / fmt: off

Temporarily disable formatting:

```python
# fmt: off
not_formatted=3
also_not_formatted=4
# fmt: on
formatted_again = True
```

**Note:** Works at statement level, not expression level.

### fmt: skip

Skip formatting for single statement:

```python
a = [1, 2, 3, 4, 5]  # fmt: skip

def test(a, b, c, d, e, f) -> int:  # fmt: skip
    pass
```

### YAPF Compatibility

Ruff recognizes YAPF pragmas:

```python
# yapf: disable
not_formatted = True
# yapf: enable
```

## Suppression Best Practices

### Prefer Per-File Ignores

Instead of many `noqa` comments:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["F401", "S101"]
```

### Be Specific with noqa

```python
# Good: Specific rule
x = 1  # noqa: F841

# Bad: Ignores everything (might hide real issues)
x = 1  # noqa
```

### Document Why Suppression is Needed

```python
# Third-party library has incomplete type stubs
result = legacy_api.fetch()  # noqa: F821
# TODO: Migrate to new API when available
```

### Use for Legitimate False Positives Only

Don't suppress rules that indicate real issues. Fix the code instead.

## Unused noqa Detection

Ruff can detect unused `noqa` comments:

**Enable the rule:**
```toml
[tool.ruff.lint]
extend-select = ["F841"]  # Includes unused variable detection

# Or enable specific rule for unused noqa
extend-select = ["RUF100"]  # Unused noqa directive
```

**Command-line:**
```shell
ruff check --select RUF100
```

## Troubleshooting

### noqa Not Working

**Check syntax:**
```python
# Correct
x = 1  # noqa: F841

# Wrong (space before colon)
x = 1  # noqa : F841  # Won't work!

# Wrong (missing rule code when needed)
x = 1  # noqa  # Only works for all rules
```

### Per-File Ignore Not Matching

**Check glob pattern:**
```toml
[tool.ruff.lint.per-file-ignores]
# This matches tests/foo.py but not tests/foo/__init__.py
"tests/*.py" = ["F401"]

# This matches all Python files in tests/
"tests/**/*.py" = ["F401"]
```

**Verify file path:**
```shell
# Check if Ruff is analyzing the file
ruff check path/to/file.py --verbose
```

### Format Suppression Not Working

**Check placement:**
```python
# Correct (at statement level)
# fmt: off
x = 1
# fmt: on

# Wrong (inside expression - won't work)
[
    # fmt: off
    '1',
    # fmt: on
    '2',
]
```

## Migration from Flake8

Flake8 `# noqa` comments work with Ruff:

```python
# Flake8 (works with Ruff too)
x = 1  # noqa: F841

# Multiple rules
i = 1  # noqa: E741,F841  # Works with or without space
```

## Migration from Black

Black `# fmt: off` comments work with Ruff:

```python
# Black (works with Ruff too)
# fmt: off
not_formatted = True
# fmt: on
```

## Next Steps

- Configure [rules](./04-rules.md) for your project's needs
- Set up [per-file ignores](./06-configuration.md) in configuration
- Customize [formatter settings](./03-formatter.md) if needed
