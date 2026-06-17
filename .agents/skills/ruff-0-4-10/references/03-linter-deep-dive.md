# Linter Deep Dive

## Rule Selection Resolution

Ruff resolves the active rule set by reconciling `select`, `extend-select`, and `ignore` from multiple sources. Priority order (highest to lowest):

1. CLI flags (`--select`, `--extend-select`, `--ignore`)
2. Current directory's config file
3. Inherited config file (via `extend`)
4. User-level default config
5. Ruff built-in defaults

The "highest-priority" `select` becomes the base, then `extend-select` adds on top, and `ignore` removes.

### Example Resolution

Given:
- Config: `select = ["E", "F"]`, `ignore = ["F401"]`
- CLI: `ruff check --extend-select B`

Result: Rules `E*`, `F*` (except `F401`), and `B*` are active.

Given:
- Config: `select = ["E", "F"]`, `ignore = ["F401"]`
- CLI: `ruff check --select F401`

Result: Only `F401` is active (CLI `--select` replaces config entirely).

## Fix Safety Model

Ruff classifies each auto-fix as **safe** or **unsafe**:

- **Safe fixes**: Preserve program semantics. Applied by default with `--fix`.
- **Unsafe fixes**: May change behavior (e.g., exception types, control flow). Require explicit opt-in.
- **Display-only**: Fix shown but never auto-applied.

### Applying Fixes

```bash
ruff check --fix                  # Safe fixes only
ruff check --fix --unsafe-fixes   # Safe + unsafe fixes
ruff check --diff                 # Preview fixes without writing
ruff check --fix-only             # Apply fixes, suppress remaining violations in output
```

### Adjusting Fix Safety Per Rule

```toml
[lint]
extend-safe-fixes = ["F601"]      # Promote F601's unsafe fix to safe
extend-unsafe-fixes = ["UP034"]   # Demote UP034's safe fix to unsafe
```

Prefixes work too: `extend-safe-fixes = ["F"]` promotes all Pyflakes fixes.

### Disabling Fixes for Specific Rules

```toml
[lint]
fixable = ["ALL"]
unfixable = ["F401"]              # Never auto-fix unused imports
```

Or selectively enable only certain fixable rules:

```toml
[lint]
fixable = ["F401", "F841"]        # Only fix these two
```

## Error Suppression System

### Inline `noqa` Comments

```python
x = 1  # noqa: F841               # Ignore specific rule
y = 2  # noqa: E741, F841         # Ignore multiple rules
z = 3  # noqa                     # Ignore all rules on this line
```

For multi-line strings (docstrings), place `noqa` after the closing quotes:

```python
"""This is a very long docstring that exceeds the line length limit by far."""  # noqa: E501
```

For import blocks, `noqa` on the first line applies to the whole block:

```python
import os  # noqa: I001
import sys
```

### File-Level Suppression

```python
# ruff: noqa                       # Ignore all rules in this file
# ruff: noqa: F841                 # Ignore specific rule everywhere
```

Ruff also respects Flake8's `# flake8: noqa` (equivalent to `# ruff: noqa`).

### Detecting Stale `noqa` Comments

The `RUF100` (unused-noqa) rule flags `noqa` directives that suppress rules not actually triggered on that line:

```bash
ruff check --extend-select RUF100 .        # Flag unused noqa
ruff check --extend-select RUF100 --fix .  # Remove unused noqa automatically
```

### Adding `noqa` During Migration

When introducing Ruff to an existing codebase, use `--add-noqa` to suppress existing violations:

```bash
ruff check --select UP --add-noqa .   # Add noqa for pyupgrade violations only
ruff check --add-noqa .               # Add noqa for all current violations
```

This lets you enforce rules going forward while gradually fixing existing issues.

## Action Comments (isort)

Ruff respects isort's action comments for selective import sorting:

| Comment | Effect |
|---|---|
| `# isort: skip_file` | Skip sorting imports in entire file |
| `# ruff: isort: skip_file` | Same (Ruff-prefixed variant) |
| `# isort: skip` | Skip the preceding import statement |
| `# isort: on` | Re-enable sorting after `off` |
| `# isort: off` | Disable sorting until `on` |
| `# isort: split` | Split combined imports into separate lines |

Unlike isort, Ruff does not respect action comments within docstrings.

## Output Formats

`ruff check --output-format <FORMAT>`:

| Format | Description |
|---|---|
| `text` / `concise` | Default: `file.py:1:1: F401 unused import` |
| `full` | Violation with source code snippet (preview default) |
| `json` | Machine-readable JSON (includes fix applicability) |
| `json-lines` | One JSON object per line |
| `github` | GitHub Actions annotations |
| `gitlab` | GitLab CI report format |
| `junit` | JUnit XML for CI pipelines |
| `pylint` | Pylint-compatible format |
| `rdjson` | Redcarpet JSON |
| `azure` | Azure DevOps pipeline format |
| `sarif` | Static Analysis Results Interchange Format |

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | No violations found (or all were auto-fixed) |
| `1` | Violations detected |
| `2` | Abnormal termination (bad config, invalid CLI, internal error) |

### Modifying Exit Behavior

```bash
ruff check --exit-zero .                # Always exit 0 (even with violations)
ruff check --exit-non-zero-on-fix .     # Exit 1 if any fixes were applied
```

## Caching

Ruff caches analysis results in `.ruff_cache/` by default. Cache is invalidated when files change.

```bash
ruff check --no-cache .                 # Disable cache reads
ruff check --cache-dir /tmp/ruff-cache .  # Custom cache location
ruff clean                              # Clear all caches
```

Set `RUFF_NO_CACHE=1` or `RUFF_CACHE_DIR=/path` via environment variables.

## Statistics

Show violation counts per rule:

```bash
ruff check --statistics .
```

Output:
```
12	F401	Unused import
5	E712	True/false comparison
3	F841	Unused variable
```
