# Formatter Deep Dive

## Black Compatibility

Ruff's formatter targets near-identical output to Black. On extensive Black-formatted projects (Django, Zulip), >99.9% of lines are formatted identically. When migrating from Black, expect minimal diffs on the margins.

The formatter adheres to Black's stable code style: consistency, generality, readability, and reduced git diffs.

### Known Intentional Deviations

Ruff differs from Black in a few conscious ways where Ruff's behavior was deemed more consistent or simpler to implement. These deviations are limited and tracked in the [Ruff issue tracker](https://github.com/astral-sh/ruff/issues?q=is%3Aopen+is%3Aissue+label%3Aformatter).

## Formatter Configuration

```toml
[format]
quote-style = "double"                # "double" or "single"
indent-style = "space"                # "space" or "tab"
skip-magic-trailing-comma = false     # Respect trailing commas for line breaks
line-ending = "auto"                  # "auto", "lf", "cr", "crlf"
docstring-code-format = false         # Format code in docstrings
docstring-code-line-length = "dynamic"  # "dynamic" or integer
```

Unlike Black, Ruff allows configuring quote style, indent style, and line endings. However, it does not expose extensive style configuration — the goal is minimal opinionation with maximum performance.

## Docstring Code Formatting

When `docstring-code-format = true`, the formatter automatically formats Python code examples inside docstrings:

- Python doctest format
- CommonMark fenced code blocks (`python`, `py`, `python3`, `py3`, or no info string)
- reStructuredText literal blocks
- reStructuredText `code-block` and `sourcecode` directives

Code that doesn't parse as valid Python is skipped. Reformatted code that would produce invalid Python is also skipped.

### Dynamic Line Length

With `docstring-code-line-length = "dynamic"` (default), the formatter respects the surrounding code's line length limit even when docstrings are indented. This prevents exceeding the configured `line-length`.

Set a fixed value for explicit control:

```toml
[format]
docstring-code-format = true
docstring-code-line-length = 80
```

## Format Suppression Pragmas

### Block Suppression (`# fmt: off` / `# fmt: on`)

Enforced at the **statement level**, not expression level:

```python
# fmt: off
not_formatted = 3
also_not_formatted = 4
# fmt: on
```

Placing `# fmt: off` inside an expression has no effect — the entire statement is formatted:

```python
# This does NOT suppress formatting of list entries:
[
    # fmt: off   # Ignored here — not at statement level
    '1',
    '2',
]

# Correct: apply to the whole statement:
# fmt: off
[
    '1',
    '2',
]
# fmt: on
```

### Single-Statement Skip (`# fmt: skip`)

Appends to the end of a statement, case header, decorator, function/class definition:

```python
if True:
    pass
elif False:  # fmt: skip
    pass

@Test
@Test2  # fmt: skip
def test(): ...

a = [1, 2, 3, 4, 5]  # fmt: skip

def test(a, b, c, d, e, f) -> int:  # fmt: skip
    pass
```

Inside expressions, `# fmt: skip` has no effect. Apply it to the full statement instead:

```python
# Wrong — skips nothing:
a = call(
    [
        '1',  # fmt: skip   # Ignored
        '2',
    ],
    b
)

# Correct:
a = call(
  [
    '1',
    '2',
  ],
  b
)  # fmt: skip
```

### YAPF Compatibility

Ruff recognizes YAPF's `# yapf: disable` and `# yapf: enable`, treating them as equivalent to `# fmt: off` and `# fmt: on`.

## Conflicting Lint Rules

When using both linter and formatter, avoid enabling these lint rules as they conflict with formatting decisions:

### Indentation Rules
- `W191` — tab-indentation
- `E111` — indentation-with-invalid-multiple
- `E114` — indentation-with-invalid-multiple-comment
- `E117` — over-indented
- `D206` — indent-with-spaces

### Quote Rules
- `D300` — triple-single-quotes
- `Q000`–`Q003` — flake8-quotes rules

### Trailing Comma Rules
- `COM812` — missing-trailing-comma
- `COM819` — prohibited-trailing-comma

### String Concatenation Rules
- `ISC001` — single-line-implicit-string-concatenation
- `ISC002` — multi-line-implicit-string-concatenation

### Line Length
- `E501` — line-too-long (formatter makes best-effort but may still exceed in some cases)

None of these are in Ruff's defaults. If you've enabled their parent categories (e.g., `Q`, `W`), add them to `lint.ignore`.

### Incompatible isort Settings

Avoid non-default values for:
- `force-single-line`
- `force-wrap-aliases`
- `lines-after-imports`
- `lines-between-types`
- `split-on-trailing-comma`

If incompatible rules are detected, `ruff format` emits warnings.

## Exit Codes

| Command | Code | Meaning |
|---|---|---|
| `ruff format` | 0 | Success (regardless of whether files changed) |
| `ruff format` | 2 | Abnormal termination |
| `ruff format --check` | 0 | All files already formatted |
| `ruff format --check` | 1 | Files would be reformatted |
| `ruff format --check` | 2 | Abnormal termination |

## Preview Style

Ruff supports Black's preview formatting style behind its own `preview` flag:

```toml
[format]
preview = true
```

```bash
ruff format --preview
```

Preview formatting changes are promoted to stable through minor releases.

## Import Sorting

The formatter does not sort imports. Use the linter:

```bash
ruff check --select I --fix   # Sort imports
ruff format                   # Then format
```

A unified lint+format command is planned for future versions.
