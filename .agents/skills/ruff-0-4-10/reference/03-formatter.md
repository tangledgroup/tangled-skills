# The Ruff Formatter

The Ruff formatter is an extremely fast Python code formatter designed as a drop-in replacement for Black, available via `ruff format`.

## Running the Formatter

### Basic Usage

```shell
# Format all files in current directory
ruff format

# Format specific files or directories
ruff format src/
ruff format example.py

# Check without writing (dry-run)
ruff format --check

# Show diff
ruff format --diff
```

### Combined Lint and Format

```shell
# Lint and fix, then format
ruff check --fix && ruff format

# Or in CI/CD
ruff check . && ruff format --check .
```

## Philosophy

The Ruff formatter is designed as a **drop-in replacement for Black** with:
- Near-identical output (>99.9% line compatibility on Black-formatted code)
- 20-300x faster performance
- Unified configuration with the linter
- Additional features (docstring formatting, quote style control)

## Configuration

### Basic Settings

**pyproject.toml:**
```toml
[tool.ruff.format]
# Quote style: "double" (default), "single", "preserve"
quote-style = "single"

# Indent style: "space" (default) or "tab"
indent-style = "space"

# Indent width (default: 4)
indent-width = 4

# Line ending: "auto" (default), "lf", "crlf", "cr"
line-ending = "auto"

# Respect magic trailing commas (default: true)
skip-magic-trailing-comma = false

# Format docstring code examples (default: false)
docstring-code-format = true

# Line length for docstring code (default: "dynamic")
docstring-code-line-length = 88
```

### Common Configurations

**Black-compatible (default):**
```toml
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
```

**Single quotes with tabs:**
```toml
[tool.ruff.format]
quote-style = "single"
indent-style = "tab"
indent-width = 4
```

**With docstring formatting:**
```toml
[tool.ruff.format]
docstring-code-format = true
docstring-code-line-length = 88
```

## Docstring Formatting

Ruff can automatically format Python code examples in docstrings:

### Supported Formats

- Python doctest format
- Markdown fenced code blocks (` ```python `)
- reStructuredText literal blocks
- Sphinx `code-block` and `sourcecode` directives

### Example

**Input:**
```python
def f(x):
    '''
    Something about `f`. And an example:

    .. code-block:: python

        foo, bar, quux = this_is_a_long_line(lion, hippo, lemur, bear)
    '''
    pass
```

**Output (with `docstring-code-format = true`):**
```python
def f(x):
    """
    Something about `f`. And an example:

    .. code-block:: python

        (
            foo,
            bar,
            quux,
        ) = this_is_a_long_line(
            lion,
            hippo,
            lemur,
            bear,
        )
    """
    pass
```

### Configuration

```toml
[tool.ruff.format]
# Enable docstring code formatting
docstring-code-format = true

# Use dynamic line length (matches surrounding code)
docstring-code-line-length = "dynamic"

# Or use fixed line length
docstring-code-line-length = 88
```

## Format Suppression

### fmt: on / fmt: off

Temporarily disable formatting:

```python
# fmt: off
not_formatted=3
also_not_formatted=4
# fmt: on
```

**Note:** These work at the statement level, not expression level.

### fmt: skip

Skip formatting for a single statement:

```python
a = [1, 2, 3, 4, 5]  # fmt: skip

def test(a, b, c, d, e, f) -> int:  # fmt: skip
    pass
```

### YAPF Compatibility

Ruff also recognizes YAPF pragma comments:

```python
# yapf: disable
not_formatted = True
# yapf: enable
```

## Black Compatibility

### Known Deviations

Ruff differs from Black in a few conscious ways:
- String formatting (quote style control)
- Docstring code formatting (opt-in)
- Slightly different handling of edge cases

See [Black compatibility](https://docs.astral.sh/ruff/formatter/black/) for full details.

### Migration from Black

```shell
# Install Ruff
pip install ruff

# Replace Black commands
# Before: black src/
# After:  ruff format src/

# Check formatting
# Before: black --check src/
# After:  ruff format --check src/
```

Most Black-formatted code will have <0.1% line differences.

## Performance

- **20-300x faster** than Black
- **Incremental formatting:** Only reformats changed files in watch mode
- **Parallel execution:** Uses multiple CPU cores automatically

## Troubleshooting

### Formatting Changes Too Much

Ensure you're using compatible settings:

```toml
[tool.ruff.format]
# Match Black defaults
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
```

### Docstring Code Not Formatting

Enable the feature:

```toml
[tool.ruff.format]
docstring-code-format = true
```

Check that code examples are valid Python.

### Line Length Issues

Adjust line length:

```toml
[tool.ruff]
# Global line length (default: 88)
line-length = 100

[tool.ruff.format]
# Docstring code line length
docstring-code-line-length = 88
```

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Format check
  run: ruff format --check .

- name: Auto-format (in PRs)
  run: ruff format .
```

## Next Steps

- Configure [linting](./02-linter.md) for code quality checks
- Set up [rule selection](./04-rules.md) for your project
- Customize [configuration](./06-configuration.md) for advanced settings
- Integrate with [editors](./07-integrations.md) for real-time feedback
