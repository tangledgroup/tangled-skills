# Configuration

ty supports persistent configuration through `pyproject.toml` or `ty.toml` files at project and user levels.

## Configuration Files

### File Discovery

ty searches for configuration in this order:

1. **Project-level:** `pyproject.toml` (in `[tool.ty]` section) or `ty.toml`
2. **User-level:** `~/.config/ty/ty.toml` (macOS/Linux) or `%APPDATA%\ty\ty.toml` (Windows)

**Precedence:**
- `ty.toml` takes precedence over `pyproject.toml` in the same directory
- Project-level overrides user-level settings
- Command-line arguments override all configuration files

### pyproject.toml Format

```toml
[tool.ty]
# ty configuration goes here

[tool.ty.rules]
possibly-unresolved-reference = "warn"

[tool.ty.environment]
python-version = "3.12"
```

### ty.toml Format

Same structure without `[tool.ty]` prefix:

```toml
# ty.toml (equivalent to [tool.ty] in pyproject.toml)

[rules]
possibly-unresolved-reference = "warn"

[environment]
python-version = "3.12"
```

### Disable Configuration Files

```shell
# Disable all config file discovery
ty check --no-config

# Use specific config file
ty check --config-file ./custom-ty.toml
```

## Rules Configuration

Configure rule severity levels:

```toml
[tool.ty.rules]
# Individual rules
possibly-missing-attribute = "error"
unused-ignore-comment = "warn"
redundant-cast = "ignore"

# Set default for all rules
all = "error"
```

**Valid severities:** `ignore`, `warn`, `error`

See [rules](./03-rules.md) for complete rule documentation.

## Environment Configuration

### Python Interpreter

```toml
[tool.ty.environment]
# Path to Python interpreter or virtual environment
python = "./.venv"
python = "./.venv/bin/python"
python = "/usr/bin/python3.12"
```

**Auto-detection order:**
1. `VIRTUAL_ENV` environment variable
2. `CONDA_PREFIX` (Conda environments)
3. `.venv` in project root
4. `python3` or `python` in PATH

### Python Version

```toml
[tool.ty.environment]
# Target Python version for type checking
python-version = "3.12"
```

**Auto-detection order:**
1. `project.requires-python` in `pyproject.toml`
2. Activated/configured Python environment
3. Default: `"3.14"`

ty will error if code uses features not supported in the specified version.

### Python Platform

```toml
[tool.ty.environment]
# Target platform for type checking
python-platform = "linux"     # linux, win32, darwin, android, ios
python-platform = "all"       # Assume code runs on any platform
```

**Default:** Current platform (`win32`, `darwin`, or `linux`)

Affects:
- Standard library stubs used
- Platform-specific code paths
- `sys.platform` conditional analysis

### Extra Paths

```toml
[tool.ty.environment]
# Additional module search paths (like MYPYPATH)
extra-paths = ["./shared", "./vendor"]
```

Paths are searched in priority order (first has highest priority).

### Project Roots

```toml
[tool.ty.environment]
# Root paths for finding first-party modules
root = ["./src", "./lib", "./vendor"]
```

**Auto-detection:** If unspecified, ty detects common layouts:
- Project root (`.`)
- `./src` (if exists and not a package)
- `./<project-name>` (if `<project-name>/<project-name>` exists)
- `./python`

### Custom Typeshed

```toml
[tool.ty.environment]
# Path to custom typeshed directory
typeshed = "/path/to/custom/typeshed"
```

If not provided, ty uses vendored typeshed stubs bundled with the binary.

## Analysis Configuration

### Allowed Unresolved Imports

Suppress `unresolved-import` diagnostics for specific modules:

```toml
[tool.ty.analysis]
allowed-unresolved-imports = [
    "test.**",           # All test modules
    "!test.foo",         # Except test.foo
    "*test*.**",         # Any module with 'test' in first component
    "third_party.**"     # All third-party modules
]
```

**Glob patterns:**
- `*` matches zero or more characters except `.`
- `**` matches any number of module components
- Prefix with `!` to exclude

Later entries take precedence when multiple patterns match.

### Replace Imports with Any

Replace module types with `typing.Any`:

```toml
[tool.ty.analysis]
replace-imports-with-any = [
    "pandas.**",    # Replace all pandas imports with Any
    "numpy.**",     # Replace all numpy imports with Any
    "!numpy.core"   # Except numpy.core
]
```

Unlike `allowed-unresolved-imports`, this replaces types even if modules can be resolved.

### Respect type: ignore Comments

```toml
[tool.ty.analysis]
# Whether to respect standard PEP 484 type: ignore comments
respect-type-ignore-comments = true  # Default: true
```

When `false`, only `# ty: ignore` comments work for suppression.

## Overrides

Apply different configurations to specific files:

```toml
# Relax rules for test files
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]
exclude = ["tests/integration/**"]

[rules]
possibly-unresolved-reference = "ignore"
possibly-missing-import = "warn"
unused-ignore-comment = "ignore"

# Strict rules for production code
[[tool.ty.overrides]]
include = ["src/**"]

[rules]
all = "error"
```

**Matching:**
- Multiple overrides can match the same file
- Later overrides take precedence
- Override rules take precedence over global rules

## Error on Warning

Treat warnings as errors:

```toml
[tool.ty]
error-on-warning = true
```

Or via command-line: `ty check --error-on-warning`

## Complete Example Configuration

```toml
# pyproject.toml

[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.28",
]

[tool.ty]
error-on-warning = false

[tool.ty.environment]
python-version = "3.12"
python-platform = "all"
extra-paths = ["./shared"]

[tool.ty.analysis]
allowed-unresolved-imports = [
    "tests.**",
    "fixtures.**",
    "third_party.**",
]
replace-imports-with-any = [
    "pandas.**",
    "numpy.**",
]
respect-type-ignore-comments = true

[tool.ty.rules]
all = "error"
possibly-unresolved-reference = "warn"
unused-ignore-comment = "warn"

# Relax rules for tests
[[tool.ty.overrides]]
include = ["tests/**"]

[rules]
possibly-unresolved-reference = "ignore"
possibly-missing-import = "ignore"
unused-ignore-comment = "ignore"

# Strict rules for production code
[[tool.ty.overrides]]
include = ["src/**"]

[rules]
all = "error"
```

## Command-Line Overrides

Command-line options override configuration files:

```shell
# Override rule level in config
ty check --error possibly-unresolved-reference

# Override Python version
ty check --python-version 3.11

# Disable all config files
ty check --no-config
```

## Troubleshooting

### Configuration Not Taking Effect

**Check file location:**
```bash
# Should be in project root or parent directory
ls -la pyproject.toml
ls -la ty.toml
```

**Verify syntax:**
```toml
# Correct: [tool.ty] section in pyproject.toml
[tool.ty]
python-version = "3.12"

# Incorrect: Missing [tool.ty] prefix
[ty]  # Won't work in pyproject.toml
python-version = "3.12"
```

**Check precedence:**
- `ty.toml` overrides `pyproject.toml` in same directory
- Project-level overrides user-level
- Command-line overrides all files

### Override Not Matching Files

**Test glob patterns:**
```toml
# This matches tests/foo.py but not tests/foo/__init__.py
include = ["tests/*.py"]

# This matches all Python files in tests/
include = ["tests/**/*.py"]

# Exclude specific files
exclude = ["tests/test_legacy.py"]
```

### Import Resolution Issues

**Specify Python environment:**
```toml
[tool.ty.environment]
python = "./.venv"
```

**Add extra paths:**
```toml
[tool.ty.environment]
extra-paths = ["./src", "./lib"]
```

**Allow unresolved imports:**
```toml
[tool.ty.analysis]
allowed-unresolved-imports = ["third_party.**"]
```

## Best Practices

1. **Use `pyproject.toml` for project-specific settings** - Keeps configuration with code
2. **Use `ty.toml` for user preferences** - Global defaults across projects
3. **Start permissive, get stricter** - Begin with `warn`, migrate to `error` as you fix issues
4. **Use overrides for different codebases** - Relax rules for tests, legacy code, or generated code
5. **Document non-obvious settings** - Add comments explaining configuration choices

## Next Steps

- Configure [rules](./03-rules.md) for your project's needs
- Set up [suppression](./04-suppression.md) for specific violations
- Integrate with your [editor](./05-editors.md) for real-time feedback
- Run `ty check` to verify configuration works
