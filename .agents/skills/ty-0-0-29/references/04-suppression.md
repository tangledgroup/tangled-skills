# Suppression

Suppress specific type checking violations inline instead of disabling rules entirely. This allows you to silence false positives or permissible violations while maintaining overall type safety.

## ty Suppression Comments

### Single Rule Suppression

Add `# ty: ignore[<rule>]` at the end of the line:

```python
a = 10 + "test"  # ty: ignore[unsupported-operator]
```

### Multiple Rules on One Line

Enumerate rules separated by commas:

```python
sum_three_numbers("one", 5)  # ty: ignore[missing-argument, invalid-argument-type]
```

### Multi-line Violations

Place comment at the end of the first or last line:

```python
# On the first line
sum_three_numbers(  # ty: ignore[missing-argument]
    3,
    2
)

# Or on the last line
sum_three_numbers(
    3,
    2
)  # ty: ignore[missing-argument]
```

### File-Level Suppression

Place comment on its own line before any Python code:

```python
# ty: ignore[invalid-argument-type]

def main():
    sum_three_numbers(3, 2, "1")  # No error for this file
```

**Note:** Enumerating rule names (e.g., `[rule1, rule2]`) is optional but strongly recommended to avoid accidental suppression of other errors.

## Standard Suppression Comments (PEP 484)

ty supports the standard `type: ignore` format:

### Ignore All Violations

```python
sum_three_numbers("one", 5)  # type: ignore
```

This suppresses all violations on that line.

### Ignore Specific Rules

```python
# ty-specific rule with prefix
sum_three_numbers("one", 5)  # type: ignore[ty:invalid-argument-type]

# Combined with other type checkers
sum_three_numbers("one", 5, 2)  # type: ignore[arg-type, ty:invalid-argument-type]
```

Codes without a `ty:` prefix are ignored, allowing combined suppressions for multiple type checkers.

## Multiple Suppression Comments

Add ty suppression to lines with other tool comments:

```python
# With formatting tools
result = calculate()  # ty: ignore[invalid-argument-type]  # fmt: skip

# Order doesn't matter
value = process()  # noqa: E501  # ty: ignore[possibly-unresolved-reference]
```

## `@no_type_check` Directive

Suppress all violations inside a function:

```python
from typing import no_type_check

def sum_three_numbers(a: int, b: int, c: int) -> int:
    return a + b + c

@no_type_check
def main():
    sum_three_numbers(1, 2)  # No error for missing argument
```

**Note:** Decorating a class with `@no_type_check` is not supported.

## Unused Suppression Comments

If the `unused-ignore-comment` rule is enabled, ty reports unused suppression comments:

```python
x = 5  # ty: ignore[invalid-type]  # This will trigger unused-ignore-comment
```

**Important:** `unused-ignore-comment` violations can only be suppressed using:
```python
x = 5  # ty: ignore[unused-ignore-comment]
```

They cannot be suppressed using `# ty: ignore` without a rule code or `# type: ignore`.

## Respecting `type: ignore` Comments

By default, ty respects standard `type: ignore` comments. Disable this behavior:

```toml
[tool.ty.analysis]
respect-type-ignore-comments = false
```

When disabled, only `# ty: ignore` comments work for suppression.

**Use case:** When using ty alongside other type checkers and you prefer explicit `ty: ignore` comments.

## Suppression Best Practices

### Do Use Specific Rule Names

```python
# Good: Specific rule
result = api_call()  # ty: ignore[possibly-unresolved-reference]

# Bad: Suppresses everything
result = api_call()  # type: ignore
```

### Do Document Why Suppression is Needed

```python
# Third-party library has incomplete type stubs
response = legacy_api.fetch_data()  # ty: ignore[possibly-missing-attribute]
# TODO: Update to new API when available
```

### Don't Suppress Entire Files Unless Necessary

```python
# Prefer specific suppressions over file-level
# ty: ignore[invalid-argument-type]  # Only use for legacy files

def good_function():
    value = process()  # ty: ignore[specific-rule]  # Better
```

### Do Review Suppressions Periodically

Enable `unused-ignore-comment` to catch stale suppressions:

```toml
[tool.ty.rules]
unused-ignore-comment = "warn"
```

## Common Suppression Patterns

### Third-Party Libraries Without Stubs

```python
import legacy_library

# Suppress unresolved imports for specific module
result = legacy_library.func()  # ty: ignore[possibly-unresolved-import]
```

Or configure globally:
```toml
[tool.ty.analysis]
allowed-unresolved-imports = ["legacy_library.**"]
```

### Dynamic Code Generation

```python
@no_type_check
def generate_code(template: str) -> str:
    # Dynamic attribute access
    obj = getattr(module, template)
    return str(obj)
```

### Testing and Mocking

```python
# tests/test_module.py

# ty: ignore[possibly-unresolved-import]
from unittest.mock import patch

def test_function():
    with patch('module.func'):  # ty: ignore[possibly-missing-attribute]
        pass
```

Or relax rules for test files:
```toml
[[tool.ty.overrides]]
include = ["tests/**"]
[rules]
possibly-unresolved-reference = "ignore"
possibly-missing-import = "warn"
```

### Gradual Typing Migration

```python
# Legacy code during migration
# ty: ignore[invalid-argument-type]
# ty: ignore[missing-argument]

def legacy_function(param):  # No type annotations yet
    return process(param)
```

## Troubleshooting

### Suppression Not Working

**Check rule name:**
```python
# Wrong rule name (won't suppress)
value = func()  # ty: ignore[wrong-rule-name]

# Correct rule name from error message
value = func()  # ty: ignore[invalid-argument-type]
```

**Check comment position:**
```python
# Comment must be on same line as violation
func()
# ty: ignore[rule]  # Won't work!

func()  # ty: ignore[rule]  # Correct
```

### `type: ignore` Not Working

Ensure ty respects standard comments:

```toml
[tool.ty.analysis]
respect-type-ignore-comments = true  # Default
```

Or use ty-specific format:
```python
value = func()  # type: ignore[ty:invalid-argument-type]
```

### Multiple Type Checkers

When using multiple type checkers, use prefixed codes:

```python
# Works with both mypy and ty
value = func()  # type: ignore[arg-type, ty:invalid-argument-type]
```

## Migration Guide

### From mypy

```python
# mypy
value = func()  # type: ignore[arg-type]

# ty (both work)
value = func()  # type: ignore[arg-type]  # Still works
value = func()  # ty: ignore[invalid-argument-type]  # Preferred
```

### From Pyright

```python
# Pyright
value = func()  # type: ignore[reportInvalidArgumentType]

# ty
value = func()  # ty: ignore[invalid-argument-type]
```

## Next Steps

- Configure [rules](./03-rules.md) to set appropriate severity levels
- Set up [overrides](./07-configuration.md) for file-specific rule configuration
- Enable `unused-ignore-comment` to catch stale suppressions
- Use [analysis settings](./07-configuration.md) for import resolution control
