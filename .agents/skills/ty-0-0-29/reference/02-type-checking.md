# Type Checking

After installing ty, use the `check` command to type check your Python code.

## Running the Type Checker

### Basic Usage

```shell
# Check all Python files in current directory
ty check

# Check specific files or directories
ty check example.py
ty check src/
ty check src/mymodule.py tests/test_mymodule.py
```

**Note:** If you're in a project, you may need to use `uv run` or activate your virtual environment first for ty to find your dependencies.

### Environment Discovery

The type checker needs to discover installed packages to check imported dependencies:

1. **Virtual environment via `VIRTUAL_ENV`** - Active virtual environment
2. **`.venv` directory** - In project root or working directory
3. **Conda environment** - Via `CONDA_PREFIX`
4. **Python in PATH** - Looks for `python3` or `python`
5. **Explicit `--python` flag** - Specify interpreter path

```shell
# Explicitly specify Python interpreter
ty check --python ./.venv/bin/python
ty check --python /usr/bin/python3.12
ty check --python ./.venv  # Directory also works
```

## File Selection

### Default Behavior

- **In a project:** Checks all Python files starting from the directory with `pyproject.toml`
- **Outside a project:** Checks all Python files in the working directory (recursively)

### Explicit File Selection

```shell
# Single file
ty check example.py

# Multiple files
ty check file1.py file2.py file3.py

# Directories
ty check src/ tests/

# Mixed
ty check src/mymodule.py tests/
```

### Exclusions

Configure which files to exclude in `pyproject.toml`:

```toml
[tool.ty.environment]
# See exclusions documentation for detailed configuration
```

See the [exclusions](./08-exclusions.md) documentation for persistent file selection configuration.

## Rule Selection and Severity

ty's diagnostics are associated with rules that can be configured:

### Command-Line Rule Configuration

```shell
# Make a rule a warning instead of error
ty check --warn unused-ignore-comment

# Ignore a specific rule
ty check --ignore redundant-cast

# Make multiple rules errors
ty check --error possibly-missing-attribute --error possibly-missing-import

# Set all rules to error
ty check --error all

# Set all rules to warning
ty check --warn all

# Ignore all rules (effectively disable checking)
ty check --ignore all
```

**Rule levels:**
- `error`: Violations are errors; ty exits with code 1 if any exist
- `warn`: Violations are warnings; ty exits with code 0 (unless `--error-on-warning`)
- `ignore`: Rule is disabled

### Persistent Configuration

Configure rules in `pyproject.toml`:

```toml
[tool.ty.rules]
possibly-missing-attribute = "error"
unused-ignore-comment = "warn"
redundant-cast = "ignore"
```

See [rules](./03-rules.md) for complete rule configuration.

## Watch Mode

Run ty in incremental watch mode for development:

```shell
ty check --watch
```

**Features:**
- Watches files for changes
- Rechecks affected files automatically
- Uses fine-grained incrementality for fast updates
- Includes files that depend on changed files

Watch mode is ideal for interactive development, providing immediate feedback as you edit code.

## Exit Codes

ty uses standard exit codes:

- **0:** No errors (may have warnings)
- **1:** Type checking errors found
- **2:** Fatal error (configuration issue, internal error)

### Error on Warning

Treat warnings as errors:

```shell
ty check --error-on-warning
```

Or in configuration:

```toml
[tool.ty]
error-on-warning = true
```

## Output Formats

### Default Output

Shows file path, line number, rule name, and diagnostic message:

```
src/example.py:10:5: possibly-unresolved-reference
  Possible unresolved reference `unknown_variable`

src/example.py:15:10: invalid-argument-type
  Argument expects type `int` but received `str`
```

### JSON Output

For CI/CD integration or custom tooling:

```shell
ty check --output-format json
```

## Common Options

```shell
# Check with specific Python version
ty check --python-version 3.12

# Check for specific platform
ty check --python-platform linux

# Show rule names in output
ty check --show-rule-names

# No color output (for logs)
ty check --no-color

# Verbose output
ty check --verbose

# Quiet mode (only show errors)
ty check --quiet
```

## Project Detection

ty automatically detects project boundaries:

1. **`pyproject.toml`** - Uses project root as starting point
2. **Workspace support** - Checks all workspace members
3. **Multiple roots** - Can specify multiple project roots

```shell
# Check from project root (auto-detects pyproject.toml)
ty check

# Specify explicit project root
ty check --project-root ./my-project
```

## Incremental Checking

ty uses incremental analysis for fast rechecking:

- **Cache-based:** Results cached on disk for faster subsequent runs
- **Fine-grained:** Only rechecks affected files and dependencies
- **Language server:** Real-time updates in editors use same incremental engine

### Clear Cache

```shell
# Clear ty's cache
rm -rf ~/.cache/ty

# Or use --no-cache flag
ty check --no-cache
```

## Platform-Specific Checking

Check code as if running on different platforms:

```shell
# Check for Windows
ty check --python-platform win32

# Check for macOS
ty check --python-platform darwin

# Check for Linux
ty check --python-platform linux

# Check for all platforms (most strict)
ty check --python-platform all
```

This affects:
- Standard library stubs used
- Platform-specific code paths
- `sys.platform` conditional analysis

## Python Version Checking

Specify target Python version:

```shell
# Check with Python 3.12 features
ty check --python-version 3.12

# Check compatibility with Python 3.8
ty check --python-version 3.8
```

ty will error if code uses features not available in the specified version.

**Auto-detection order:**
1. `project.requires-python` in `pyproject.toml`
2. Activated/configured Python environment
3. Default (3.14)

## Performance Tips

1. **Use watch mode** during development for incremental checking
2. **Configure exclusions** to skip generated code or third-party modules
3. **Set python-version** to match deployment target
4. **Use allowed-unresolved-imports** for modules without type stubs
5. **Enable language server** in editor for real-time feedback

## Troubleshooting

### "No Python interpreter found"

```shell
# Activate virtual environment or use uv run
source .venv/bin/activate
ty check

# Or specify explicitly
ty check --python ./.venv/bin/python
```

### Import errors for installed packages

Ensure ty can find your virtual environment:

```toml
[tool.ty.environment]
python = "./.venv"
```

### Too many false positives

Relax specific rules:

```toml
[tool.ty.rules]
possibly-unresolved-reference = "warn"  # Instead of error
```

Or allow unresolved imports:

```toml
[tool.ty.analysis]
allowed-unresolved-imports = ["tests.**", "fixtures.**"]
```

## Next Steps

- Configure [rules](./03-rules.md) for your project's needs
- Set up [suppression](./04-suppression.md) for legitimate false positives
- Integrate with your [editor](./05-editors.md) for real-time checking
- Customize [configuration](./07-configuration.md) for advanced settings
