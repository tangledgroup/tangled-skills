# Rules and Suppression

## Rule levels

Each rule has one of three severities:

| Level | Behavior |
|-------|----------|
| `error` | Reported as error; ty exits with code 1 |
| `warn` | Reported as warning; exit 0 (unless `--error-on-warning`) |
| `ignore` | Rule disabled entirely |

### Setting levels via CLI

```bash
ty check \
  --error all \
  --ignore redundant-cast \
  --warn unused-ignore-comment \
  --error possibly-missing-attribute
```

Options can be repeated; later options override earlier ones. Use `all` to apply to every rule.

### Setting levels in config

```toml
[tool.ty.rules]
all = "error"
redundant-cast = "ignore"
possibly-missing-attribute = "warn"
```

## Explaining rules

```bash
ty explain rule invalid-argument-type   # Details about one rule
ty explain rule                         # All rules
ty explain rule --output-format json    # Machine-readable
```

## Key rules

### Type errors (default: error)

| Rule | Description |
|------|-------------|
| `call-non-callable` | Calling a non-callable object |
| `invalid-argument-type` | Argument type incompatible with parameter |
| `invalid-assignment` | Incompatible assignment |
| `invalid-return-type` | Return type doesn't match annotation |
| `missing-argument` | Required argument missing |
| `unresolved-reference` | Name not defined |
| `unresolved-import` | Module cannot be found |
| `unresolved-attribute` | Attribute doesn't exist on type |
| `unsupported-operator` | Operator not supported for operand types |
| `invalid-method-override` | Method signature incompatible with parent |
| `invalid-overload` | Overload implementation mismatch |
| `not-iterable` / `not-subscriptable` | Using iteration/subscript on unsupported type |
| `unused-awaitable` | Coroutine/awaitable not awaited |
| `division-by-zero` | Division by zero detected statically |
| `index-out-of-bounds` | Index access out of known bounds |

### Possibly erroneous (default: warn)

| Rule | Description |
|------|-------------|
| `possibly-missing-attribute` | Attribute might not exist on some union members |
| `possibly-unresolved-reference` | Name might be undefined in some branches |
| `possibly-missing-import` | Import might fail at runtime |

### Other

| Rule | Description | Default |
|------|-------------|---------|
| `unused-ignore-comment` | Suppression comment with no matching violations | warn |
| `redundant-cast` | Cast to the same type | error |
| `deprecated` | Using deprecated symbol | warn |
| `type-assertion-failure` | `assert_type()` doesn't match inferred type | error |
| `empty-body` | Function/class body is empty (no `...`, `pass`, etc.) | error |
| `conflicting-declarations` | Symbol redeclared with incompatible type | error |

## Suppression comments

### ty-specific suppression

```python
# Single rule on a line
a = 10 + "test"  # ty: ignore[unsupported-operator]

# Multiple rules
sum_three("one", 5)  # ty: ignore[missing-argument, invalid-argument-type]

# Multi-line violations — place on first or last line
result = sum_three(  # ty: ignore[missing-argument]
    3,
    2
)

# File-level suppression (before any Python code)
# ty: ignore[invalid-argument-type]

import something
```

### Standard `type: ignore`

ty supports PEP 484's `type: ignore`:

```python
# Suppresses ALL violations on the line
result = bad_call()  # type: ignore

# Ty-specific suppression within standard format
result = bad_call()  # type: ignore[ty:invalid-argument-type]

# Mixing multiple checkers
result = bad_call()  # type: ignore[arg-type, ty:invalid-argument-type]
```

### Multiple suppression comments on one line

```python
result = calculate()  # ty: ignore[invalid-argument-type]  # fmt: skip
```

### `@no_type_check` decorator

```python
from typing import no_type_check

@no_type_check
def main():
    sum_three_numbers(1, 2)  # No error for missing argument
```

Supported on functions only (not classes).

## Unused suppression comments

When the `unused-ignore-comment` rule is enabled (default: warn), ty reports suppression comments that don't suppress any violations. These can only be suppressed with `# ty: ignore[unused-ignore-comment]` — bare `# ty: ignore` or `# type: ignore` won't work.

## Migration from mypy / pyright

### Suppression comment mapping

| Checker | Format |
|---------|--------|
| mypy | `# type: ignore[code]` |
| pyright | `# pyright: ignore[reportXyz]` |
| ty | `# ty: ignore[rule]` |

### Rule level mapping

- mypy `disable_error_code` → ty `<rule> = "ignore"`
- pyright `reportXyz = "none"` → ty `<rule> = "ignore"`
- pyright `"information"` / `"hint"` → ty `"warn"` (no direct equivalent)

### Key differences

- ty does **not** have `disallow_untyped_defs`. Use Ruff's `flake8-annotations` (ANN) rules instead.
- ty allows redeclarations; mypy would flag as error.
- ty has no plugin system (unlike mypy plugins).

See the full [mapping table](https://docs.astral.sh/ty/coming-from-mypy-or-pyright/) in ty's documentation for detailed rule-to-rule correspondence between ty, mypy, and pyright.
