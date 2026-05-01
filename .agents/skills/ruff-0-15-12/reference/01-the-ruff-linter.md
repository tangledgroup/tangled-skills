# The Ruff Linter

## `ruff check`

`ruff check` is the primary entrypoint to the Ruff linter. It accepts a list of files or directories, and lints all discovered Python files, optionally fixing any fixable errors. When linting a directory, Ruff searches for Python files recursively:

```bash
ruff check                  # Lint files in the current directory.
ruff check --fix            # Lint and auto-fix.
ruff check --watch          # Lint and re-lint on change.
ruff check path/to/code/    # Lint files in a specific directory.
```

For the full list of supported options, run `ruff check --help`.

## Rule Selection

The set of enabled rules is controlled via `lint.select`, `lint.extend-select`, and `lint.ignore` settings.

Ruff's linter mirrors Flake8's rule code system: each rule code consists of a one-to-three letter prefix followed by three digits (e.g., `F401`). The prefix indicates the source of the rule (e.g., `F` for Pyflakes, `E` for pycodestyle, `ANN` for flake8-annotations).

Rule selectors accept either a full rule code (e.g., `F401`) or any valid prefix (e.g., `F`).

### Expanded Default Rule Set (Preview)

Starting with 0.15.2, preview mode enables a significantly expanded default rule set of 412 rules, up from the stable default set of 59 rules. The new rules are mostly a superset of the stable defaults, with some rules removed from preview defaults (e.g., `E401`, `E402`, `E701`-`E743`, `F403`-`F406`, `F722`).

To restore the old defaults in preview mode:

```toml
[lint]
select = ["E4", "E7", "E9", "F"]
```

### Recommended Guidelines

- Prefer `lint.select` over `lint.extend-select` to make your rule set explicit.
- Use `ALL` with discretion — it implicitly enables new rules on every upgrade.
- Start with a small set of rules (`select = ["E", "F"]`) and add categories one at a time.

### Example: Popular Rules Configuration

```toml
[lint]
select = [
    "E",      # pycodestyle
    "F",      # Pyflakes
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
    "I",      # isort
]
```

### Rule Resolution Priority

When Ruff reconciles `select` and `ignore` from multiple sources (config files, CLI), it uses the highest-priority `select` as the basis, then applies `extend-select` and `ignore` adjustments. CLI options have higher priority than config files, and the current config file has higher priority than inherited ones.

For example, with `select = ["E", "F"]` and `ignore = ["F401"]` in config:

- `ruff check --select F401` — enforces only `F401` (CLI overrides config).
- `ruff check --extend-select B` — enforces `E`, `F`, and `B`, except `F401`.

## Fixes

Ruff supports automatic fixes for a variety of lint errors. Enable fixes with `--fix`:

```bash
ruff check --fix
```

### Fix Safety

Ruff labels fixes as **safe** or **unsafe**:

- **Safe fixes** retain the meaning and intent of your code. They preserve runtime behavior and only remove comments when deleting entire statements (e.g., removing unused imports).
- **Unsafe fixes** could change runtime behavior, remove comments, or both.

For example, `RUF015` (unnecessary-iterable-allocation-for-first-element) replaces `list(...)[0]` with `next(iter(...))`, which is much faster but changes the exception type from `IndexError` to `StopIteration` for empty collections. This makes it an unsafe fix.

By default, Ruff only enables safe fixes. Enable unsafe fixes with:

```bash
ruff check --fix --unsafe-fixes
```

Or in configuration:

```toml
[lint]
unsafe-fixes = true
```

### Fix Safety Per Rule

Adjust fix safety per rule using `extend-safe-fixes` and `extend-unsafe-fixes`:

```toml
[lint]
extend-safe-fixes = ["F601"]       # Promote F601 unsafe fix to safe.
extend-unsafe-fixes = ["UP034"]    # Demote UP034 safe fix to unsafe.
```

### Disabling Fixes

Limit which rules Ruff should fix using `fixable` and `unfixable`:

```toml
[lint]
fixable = ["ALL"]
unfixable = ["F401"]   # Don't auto-fix unused imports.
```

Or only enable fixes for specific rules:

```toml
[lint]
fixable = ["F401"]     # Only fix unused imports.
```

## Error Suppression

### Configuration-Level

To omit a lint rule everywhere, add it to `lint.ignore`:

```toml
[lint]
ignore = ["E501"]   # Ignore line-too-long everywhere.
```

To omit rules within specific files, use `lint.per-file-ignores`:

```toml
[lint.per-file-ignores]
"__init__.py" = ["E402"]
"**/{tests,docs,tools}/*" = ["E402"]
```

### Inline `noqa` Comments

Ruff supports a `noqa` system similar to Flake8:

```python
# Ignore F841 on this line.
x = 1  # noqa: F841

# Ignore multiple rules.
i = 1  # noqa: E741, F841

# Ignore all violations on a line.
x = 1  # noqa
```

For multi-line strings (docstrings), place `noqa` after the closing triple quote:

```python
"""Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consectetur adipiscing elit."""  # noqa: E501
```

### Own-Line Ignore Comments (Preview)

Place an ignore comment above the line to cover an entire logical line:

```python
# ruff: ignore[ARG001]  # Covers the entire function signature
def foo(
    arg1,
    arg2,
):
    pass

# ruff: ignore[E501]  # Covers the entire list literal
things = [
    "really long string literal ...",
    "really long string literal ...",
]
```

### Block-Level Suppression

Use `disable`/`enable` pairs for range suppressions:

```python
# ruff: disable[E501]
VALUE_1 = "Lorem ipsum dolor sit amet ..."
VALUE_2 = "Lorem ipsum dolor sit amet ..."
# ruff: enable[E501]
```

If no matching `enable` is found, Ruff treats it as an implicit range (until reaching a logical scope indented less than the starting comment). An explicit `RUF104` diagnostic is produced for implicit ranges.

### File-Level Suppression

Ignore all violations across an entire file:

```python
# ruff: noqa
```

Or specific rules:

```python
# ruff: noqa: F841
```

In preview mode (0.15.12+), use `file-ignore`:

```python
# ruff: file-ignore[F401, ARG001]
```

Ruff also respects Flake8's `# flake8: noqa` directive.

### Detecting Unused Suppressions

Enable `RUF100` to flag unused `noqa` comments:

```bash
ruff check --extend-select RUF100
```

Remove unused suppressions with `--fix`:

```bash
ruff check --extend-select RUF100 --fix
```

### Adding Suppressions Automatically

Use `--add-noqa` to automatically add `noqa` directives to all violating lines:

```bash
ruff check --add-noqa
ruff check --select UP035 --add-noqa .   # Add noqa for specific rule.
```

### isort Action Comments

Ruff respects isort's action comments:

- `# isort: skip_file` — Skip import sorting for the entire file.
- `# isort: on` / `# isort: off` — Toggle import sorting.
- `# isort: skip` — Skip a single import.
- `# isort: split` — Split import blocks.

Ruff also recognizes `# ruff:` prefixed variants (e.g., `# ruff: isort: skip_file`).

## Exit Codes

- `0` — No violations found, or all violations were auto-fixed.
- `1` — Violations were found.
- `2` — Ruff terminated abnormally (invalid config, invalid CLI options, internal error).

Flags that alter exit behavior:

- `--exit-zero` — Always exit with `0`, even if violations found.
- `--exit-non-zero-on-fix` — Exit with `1` if any files were modified via fix.
