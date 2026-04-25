# Rules

Rules are individual checks that ty performs to detect common issues in your code, such as incompatible assignments, missing imports, or invalid type annotations. Each rule focuses on a specific pattern and can be configured independently.

## Rule Levels

Each rule has a configurable severity level:

- **`error`**: Violations are reported as errors; ty exits with code 1 if any exist
- **`warn`**: Violations are reported as warnings; ty exits with code 0 (unless `--error-on-warning`)
- **`ignore`**: The rule is disabled

## Configuring Rules

### Command-Line Configuration

```shell
# Set individual rule levels
ty check \
  --warn unused-ignore-comment \
  --ignore redundant-cast \
  --error possibly-missing-attribute \
  --error possibly-missing-import

# Set all rules to same level
ty check --error all
ty check --warn all
ty check --ignore all

# Options can be repeated; later options override earlier ones
ty check --error all --ignore redundant-cast
```

### Configuration File

**pyproject.toml:**
```toml
[tool.ty.rules]
unused-ignore-comment = "warn"
redundant-cast = "ignore"
possibly-missing-attribute = "error"
possibly-missing-import = "error"

# Or set default for all rules
all = "error"
```

**ty.toml:**
```toml
[rules]
unused-ignore-comment = "warn"
redundant-cast = "ignore"
possibly-missing-attribute = "error"
possibly-missing-import = "error"
all = "error"
```

## Common Rules

### Type Checking Rules

- **`invalid-argument-type`**: Argument type doesn't match function parameter
- **`missing-argument`**: Required argument not provided
- **`unexpected-keyword-argument`**: Unknown keyword argument passed
- **`return-value-mismatch`**: Return type doesn't match annotation
- **`possibly-missing-attribute`**: Attribute may not exist on type
- **`possibly-unresolved-reference`**: Reference may not be defined
- **`possibly-unresolved-import`**: Import may not resolve

### Type Annotation Rules

- **`invalid-type-form`**: Invalid syntax in type annotation
- **`redundant-cast`**: Unnecessary `cast()` call
- **`unused-type-alias`**: Type alias defined but never used

### Code Quality Rules

- **`division-by-zero`**: Potential division by zero
- **`index-out-of-bounds`**: List/index access may be out of bounds
- **`unsupported-operator`**: Operator not supported for types

### Suppression Rules

- **`unused-ignore-comment`**: `# ty: ignore` or `# type: ignore` comment not suppressing any errors

## Rule Categories

Rules can be grouped by category for bulk configuration. See the [rules reference](https://ty.dev/rules) for complete categorization.

## Per-File Overrides

Apply different rules to specific files using overrides:

```toml
# Relax rules for test files
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]
[rules]
possibly-unresolved-reference = "ignore"
possibly-missing-import = "warn"

# Strict rules for production code
[[tool.ty.overrides]]
include = ["src/**"]
[rules]
all = "error"
```

**Glob patterns:**
- `*` matches zero or more characters except `.`
- `**` matches any number of module components
- Prefix with `!` to exclude (e.g., `!test.foo`)

See [configuration](./07-configuration.md) for detailed override configuration.

## Suppression Comments

Instead of disabling rules globally, suppress specific violations inline:

```python
# Suppress specific rule
a = 10 + "test"  # ty: ignore[unsupported-operator]

# Multiple rules
result = func()  # ty: ignore[invalid-type, possibly-unresolved-reference]

# Standard format (PEP 484)
value = unknown()  # type: ignore
```

See [suppression](./04-suppression.md) for detailed suppression patterns.

## Finding Rule Names

### From Error Messages

ty error messages include the rule name:

```
src/example.py:10:5: possibly-unresolved-reference
  Possible unresolved reference `unknown_variable`
```

Rule name is `possibly-unresolved-reference`.

### List All Rules

View all available rules and their descriptions at [ty.dev/rules](https://ty.dev/rules).

## Common Rule Configurations

### Permissive (for legacy code)

```toml
[tool.ty.rules]
all = "warn"
possibly-unresolved-reference = "ignore"
possibly-missing-import = "ignore"
```

### Balanced (recommended default)

```toml
[tool.ty.rules]
all = "error"
possibly-unresolved-reference = "warn"
unused-ignore-comment = "warn"
```

### Strict (for new code)

```toml
[tool.ty.rules]
all = "error"
```

### Test Files (relaxed)

```toml
[[tool.ty.overrides]]
include = ["tests/**"]
[rules]
possibly-unresolved-reference = "ignore"
possibly-missing-import = "ignore"
unused-ignore-comment = "ignore"
```

## Error on Warning

Treat all warnings as errors:

```shell
ty check --error-on-warning
```

Or in configuration:

```toml
[tool.ty]
error-on-warning = true
```

Useful for CI/CD to catch potential issues.

## Migration from mypy

Many mypy error codes have ty equivalents:

| mypy | ty |
|------|-----|
| `arg-type` | `invalid-argument-type` |
| `missing-return` | `missing-return-statement` |
| `name-defined` | `possibly-unresolved-reference` |
| `import-not-found` | `possibly-unresolved-import` |
| `assignment` | `invalid-assignment` |

Update suppression comments when migrating:
```python
# Before (mypy)
value = func()  # type: ignore[arg-type]

# After (ty)
value = func()  # ty: ignore[invalid-argument-type]
```

**Note:** ty respects `type: ignore` by default, so existing comments continue to work.

## Migration from Pyright

Pyright error codes are generally compatible. Update configuration from `pyrightconfig.json` to `pyproject.toml`:

```toml
# pyright: reportMissingTypeStubs = false
[tool.ty.rules]
missing-type-stub = "ignore"
```

## Troubleshooting

### Rule not recognized

Ensure rule name is correct. Check [rules reference](https://ty.dev/rules) for valid rule names.

### Configuration not taking effect

- Restart language server in editor after config changes
- Clear cache: `rm -rf ~/.cache/ty`
- Check file is named `pyproject.toml` or `ty.toml`
- Verify `[tool.ty]` section in `pyproject.toml`

### Override not matching files

Check glob patterns:
```toml
# This matches tests/foo.py but not tests/foo/__init__.py
include = ["tests/*.py"]

# This matches all Python files in tests/
include = ["tests/**/*.py"]
```

## Best Practices

1. **Start permissive, get stricter** - Begin with `warn` level, migrate to `error` as you fix issues
2. **Use overrides for different codebases** - Relax rules for tests, legacy code, or generated code
3. **Suppress specific violations, not entire rules** - Use inline comments instead of disabling rules globally
4. **Enable `unused-ignore-comment`** - Catches stale suppression comments
5. **Document rule choices** - Add comments explaining why certain rules are relaxed

## Next Steps

- Set up [suppression](./04-suppression.md) for specific violations
- Configure [environment settings](./07-configuration.md) for import resolution
- Integrate with [editors](./05-editors.md) for real-time feedback
- Set up CI/CD integration for automated checking
