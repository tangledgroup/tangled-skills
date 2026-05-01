# The Ruff Formatter

## `ruff format`

The Ruff formatter is an extremely fast Python code formatter designed as a drop-in replacement for Black. It is available via `ruff format`:

```bash
ruff format                   # Format all files in the current directory.
ruff format path/to/code/     # Format all files in a specific directory.
ruff format path/to/file.py   # Format a single file.
ruff format --check           # Check without writing (CI-friendly).
ruff format --diff            # Show diff of what would change.
```

## Philosophy

The Ruff formatter's initial goal is not to innovate on code style, but to innovate on performance and provide a unified toolchain across Ruff's linter, formatter, and future tools.

It targets near-identical output when run over existing Black-formatted code. When tested over extensive Black-formatted projects like Django and Zulip, > 99.9% of lines are formatted identically.

The formatter adheres to Black's stable code style, which aims for "consistency, generality, readability and reducing git diffs."

Unlike Black, Ruff does support configuring quote style, indent style, line endings, and more — but given the focus on Black compatibility, it does not expose extensive code style configuration beyond these options.

## 2026 Style Guide

Starting with 0.15.0, Ruff formats code according to the 2026 style guide with the following changes:

- Lambda parameters are kept on the same line and lambda bodies are parenthesized to let them break across multiple lines
- Parentheses around tuples of exceptions in `except` clauses are removed on Python 3.14 and later
- A single empty line is permitted at the beginning of function bodies
- Parentheses are avoided for long `as` captures in `match` statements
- Extra spaces between escaped quotes and ending triple quotes can be omitted
- Blank lines are enforced before classes with decorators in stub files

## Markdown Code Formatting (Preview)

Starting with 0.15.0, Ruff can format Python code blocks inside Markdown files. Enable via preview mode:

```bash
ruff format --preview docs/
```

In 0.15.5+, Markdown files are discovered by default in preview mode. Code blocks are formatted based on language labels (`python`, `py`, `python3`, `py3`). Quarto Markdown language markers and `pycon` code blocks are also supported.

To configure extension mapping for Markdown code block languages:

```toml
# ruff.toml
extension = { qmd = "markdown" }
```

## Configuration

The formatter exposes a small set of configuration options:

```toml
line-length = 100

[format]
quote-style = "single"
indent-style = "tab"
docstring-code-format = true
skip-magic-trailing-comma = false
line-ending = "auto"
nested-string-quote-style = "preserve"
```

### Key Formatter Settings

- **`quote-style`** — `"double"` (default) or `"single"`. Controls which quote character the formatter uses.
- **`indent-style`** — `"space"` (default) or `"tab"`. Controls indentation character.
- **`skip-magic-trailing-comma`** — `false` (default). When `true`, disables using trailing commas as line-breaking triggers (like Black's magic trailing comma).
- **`line-ending`** — `"auto"` (default), `"lf"`, or `"crlf"`. Controls line ending style.
- **`docstring-code-format`** — `false` (default). When `true`, formats Python code examples in docstrings.
- **`docstring-code-line-length`** — `"dynamic"` (default) or a fixed integer. Line length limit for code examples in docstrings.
- **`nested-string-quote-style`** — `"preserve"` (default). Controls how nested string quotes are handled (0.15.9+).

## Docstring Formatting

When `docstring-code-format = true`, Ruff automatically formats Python code examples in docstrings. Recognized formats:

- Python doctest format
- CommonMark fenced code blocks (`python`, `py`, `python3`, `py3`, or no info string)
- reStructuredText literal blocks
- reStructuredText `code-block` and `sourcecode` directives

If the code does not parse as valid Python, or if reformatting would produce invalid Python, Ruff automatically skips it.

### Example

```toml
[format]
docstring-code-format = true
docstring-code-line-length = 20
```

With this configuration:

```python
def f(x):
    """
    Something about `f`. And an example:

    .. code-block:: python

        foo, bar, quux = this_is_a_long_line(lion, hippo, lemur, bear)
    """
    pass
```

... is reformatted as:

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

## Format Suppression

Like Black, Ruff supports `# fmt: on`, `# fmt: off`, and `# fmt: skip` pragma comments:

```python
# fmt: off
not_formatted = 3
also_not_formatted = 4
# fmt: on
```

`# fmt: on` and `# fmt: off` are enforced at the **statement level** — adding them within expressions has no effect.

Ruff also recognizes YAPF's `# yapf: disable` and `# yapf: enable`.

### `# fmt: skip`

Suppresses formatting for a case header, decorator, function definition, class definition, or the preceding statement on the same logical line:

```python
if True:
    pass
elif     False: # fmt: skip
    pass

@Test
@Test2(a,b) # fmt: skip
def test(): ...

a = [1,2,3,4,5] # fmt: skip
```

## Conflicting Lint Rules

When using Ruff as both linter and formatter, avoid these lint rules that conflict with the formatter:

- `W191` (tab-indentation)
- `E111`, `E114`, `E117` (indentation rules)
- `D206`, `D300` (docstring style rules)
- `Q000`–`Q004` (quote style rules)
- `COM812`, `COM819` (trailing comma rules)
- `ISC002` (without `ISC001` and `allow-multiline = false`)

These are not included in Ruff's default configuration. If you've enabled them, disable via `lint.ignore`.

Also avoid these isort settings with non-default values when using the formatter:

- `force-single-line`
- `force-wrap-aliases`
- `lines-after-imports`
- `lines-between-types`
- `split-on-trailing-comma`

## Exit Codes

`ruff format`:

- `0` — Success, regardless of whether files were formatted.
- `1` — Success, one or more files formatted, and `--exit-non-zero-on-format` was specified.
- `2` — Abnormal termination (invalid config, invalid CLI options, internal error).

`ruff format --check`:

- `0` — No files would be formatted.
- `1` — One or more files would be formatted.
- `2` — Abnormal termination.

## F-String Formatting

Unlike Black, Ruff formats the expression parts of f-strings (the parts inside `{...}`). It employs heuristics to determine formatting:

### Quotes in F-Strings

Ruff uses the configured quote style for f-string expressions unless it would produce invalid syntax or require more backslash escapes. It preserves original quote style when:

- Target Python < 3.12 and a self-documenting f-string contains a string literal with the configured quote style
- Target Python < 3.12 and an f-string contains any triple-quoted string with the configured quote style
- For all versions, when a self-documenting f-string format specifier contains the configured quote style

### Line Breaks in F-Strings

Starting with Python 3.12 (PEP 701), f-string expressions can span multiple lines. Ruff only splits expression parts across multiple lines if there was already a line break within any of the expression parts.

## Sorting Imports

The Ruff formatter does not sort imports. To both sort and format:

```bash
ruff check --select I --fix   # Sort imports via linter.
ruff format                   # Format code.
```

## Method Chains (Fluent Layout)

For long method chains, Ruff's preview style uses a fluent layout:

```python
# Preview style
x = (
    df
    .filter(cond)
    .agg(func)
    .merge(other)
)
```

Stable style (and Black):

```python
x = (
    df.filter(cond)
    .agg(func)
    .merge(other)
)
```
