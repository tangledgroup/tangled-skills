# Rule Categories Reference

Ruff organizes its 800+ rules into categories identified by letter prefixes. Each prefix corresponds to an upstream tool or Ruff-native rules. Select a category (e.g., `select = ["E", "F"]`) to enable all rules in that group, or select individual codes (e.g., `--select F401`).

## Default Rules

By default, Ruff enables:
- **`E4`** — pycodestyle imports (`E401`, `E402`)
- **`E7`** — pycodestyle statement errors (`E701`–`E799` subset)
- **`E9`** — pycodestyle fatal errors (`E901`–`E999`)
- **`F`** — Pyflakes (all `F` rules)

Notable exclusions from defaults: pycodestyle warnings (`W`), McCabe complexity (`C901`), and stylistic rules that overlap with the formatter.

## Major Rule Categories

### `E`, `W` — pycodestyle

| Code | Name | Description |
|---|---|---|
| `E501` | line-too-long | Line exceeds max length (conflicts with formatter) |
| `E712` | true-false-comparison | Compare to `True`/`False` directly, not `== True` |
| `E722` | bare-except | Bare `except:` without exception type |
| `W291` | trailing-whitespace | Trailing whitespace on line |
| `W293` | blank-line-with-whitespace | Blank line contains whitespace |

### `F` — Pyflakes

| Code | Name | Description |
|---|---|---|
| `F401` | unused-import | Module imported but unused (auto-fixable) |
| `F403` | star-imports | Can't detect undefined names from `*` import |
| `F821` | undefined-name | Name used but not defined |
| `F841` | unused-variable | Local variable assigned but never used |

### `I` — isort

| Code | Name | Description |
|---|---|---|
| `I001` | unsorted-imports | Imports within a section are not sorted (auto-fixable) |
| `I002` | missing-required-import | Required import is missing |

Run via: `ruff check --select I --fix`

### `UP` — pyupgrade

| Code | Name | Description |
|---|---|---|
| `UP006` | use-pep585-annotation | Use `list` instead of `typing.List` (Python 3.9+) |
| `UP007` | use-pep604-annotation | Use `X \| Y` instead of `Union[X, Y]` (Python 3.10+) |
| `UP035` | deprecated-import | Import from `collections.abc` instead of `typing` |

### `B` — flake8-bugbear

Catches likely bugs and design problems:

| Code | Name | Description |
|---|---|---|
| `B006` | mutable-arg-default | Mutable default argument (e.g., `def f(x=[])`) |
| `B007` | loop-variable-not-used | Loop variable overwritten without use |
| `B009` | getattr-with-default | `getattr(obj, "x", None)` — use `hasattr` check instead |
| `B904` | raise-without-from-inside-except | Use `raise ... from err` inside except blocks |

### `SIM` — flake8-simplify

Simplifies code patterns:

| Code | Name | Description |
|---|---|---|
| `SIM101` | duplicate-isinstance-call | Merge duplicate `isinstance()` checks |
| `SIM102` | collapsible-if | Nested `if` statements can be collapsed with `and` |
| `SIM910` | unnecessary-envelope-in-subscript | Use `x[0]` instead of `x[:][0]` |

### `C90` — McCabe complexity

| Code | Name | Description |
|---|---|---|
| `C901` | complex-structure | Function is too complex (exceeds maxMcCabe complexity) |

Not enabled by default. Configure threshold via `lint.mccabe.max-complexity`.

### `D` — pydocstyle

Docstring style enforcement. Not enabled by default:

| Code | Name | Description |
|---|---|---|
| `D100` | undocumented-public-module | Missing module docstring |
| `D103` | undocumented-public-function | Missing function docstring |
| `D205` | blank-line-after-summary | Blank line required after summary |
| `D401` | non-imperative-mood | First line should be imperative mood |

Set convention via `[lint.pydocstyle] convention = "google"` (also `"numpy"`, `"pep257"`).

### `ANN` — flake8-annotations

Type annotation checks:

| Code | Name | Description |
|---|---|---|
| `ANN001` | missing-type-function-argument | Missing type annotation for function argument |
| `ANN201` | missing-return-type-undefined | Missing return type annotation (returns `Any`) |

### `S` — flake8-bandit

Security-focused rules:

| Code | Name | Description |
|---|---|---|
| `S101` | assert | Use of `assert` detected (not safe in production) |
| `S311` | suspicious-non-crypto-random-usage | Non-cryptographic random usage |
| `S501` | flask-markup-safe | Potential XSS via `Markup(some_input)` |

### `T20` — flake8-print

| Code | Name | Description |
|---|---|---|
| `T201` | print | Found `print()` call |
| `T203` | pprint | Found `pprint()` call |

### `RUF` — Ruff-native rules

| Code | Name | Description |
|---|---|---|
| `RUF100` | unused-noqa | Unused `# noqa` directive (detects stale suppressions) |
| `RUF015` | unnecessary-iterable-allocation-for-first-element | `list(x)[0]` → `next(iter(x))` (unsafe fix) |

### Other Notable Categories

| Prefix | Source | Description |
|---|---|---|
| `A` | flake8-builtins | Shadowing Python builtins (`list`, `id`, etc.) |
| `ARG` | flake8-unused-arguments | Unused function/method arguments |
| `ASYNC` | flake8-async | Async-related issues (e.g., blocking calls in async) |
| `BLE` | flake8-blind-except | Blind except clauses |
| `COM` | flake8-commas | Trailing comma rules (`COM812`, `COM819`) |
| `CPY` | flake8-copyright | Missing copyright notices |
| `DJ` | flake8-django | Django-specific rules |
| `EM` | flake8-errmsg | Error message style checks |
| `ERA` | eradicate | Commented-out code detection |
| `EXE` | flake8-executable | Shebang/executable issues |
| `FA` | flake8-future-annotations | `from __future__ import annotations` |
| `FAST` | flake8-use-literal-star | Starred expression in function call |
| `FIX` | flake8-fixme | TODO/FIXME/HACK comments |
| `FLY` | flynt | f-string conversion opportunities |
| `G` | flake8-logging-format | Logging format string issues |
| `ICN` | flake8-import-conventions | Import alias conventions (`np` for numpy, etc.) |
| `INP` | flake8-no-pep420 | Implicit namespace packages |
| `INT` | flake8-gettext | Internationalization checks |
| `ISC` | flake8-implicit-str-concat | Implicit string concatenation |
| `LOG` | flake8-logging | Logging call issues |
| `N` | pep8-naming | Naming convention violations |
| `PD` | pandas-vet | Pandas-specific rules |
| `PERF` | perflint | Performance anti-patterns |
| `PGH` | pygrep-hooks | Pygrep hook rules |
| `PL` | Pylint | Pylint-compatible rules |
| `PT` | flake8-pytest-style | Pytest style rules |
| `PTH` | flake8-use-pathlib | Use `pathlib` instead of `os.path` |
| `Q` | flake8-quotes | Quote style rules (conflicts with formatter) |
| `RET` | flake8-return | Return statement simplification |
| `RSE` | flake8-raise | Raise statement simplification |
| `SLF` | flake8-self | Private member access (`_protected`) |
| `SLOT` | flake8-slots | Missing `__slots__` on subclasses |
| `TCH` | flake8-type-checking | Type checking import organization |
| `TD` | flake8-todos | TODO comment format checks |
| `TRY` | tryceratops | Try/except best practices |
| `UP` | pyupgrade | Modern Python syntax upgrades |
| `YTT` | flake8-2020 | Python 2/3 compatibility issues |

## Selecting Rules

```toml
# Explicit set (recommended)
[lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

# Add on top of defaults
[lint]
extend-select = ["B", "UP"]

# Enable everything (caution: includes future rules on upgrade)
[lint]
select = ["ALL"]

# Ignore specific rules
[lint]
ignore = ["E501", "W505"]
```

## The `ALL` Selector

`select = ["ALL"]` enables every rule, including those with conflicting defaults (e.g., pydocstyle conventions). Ruff automatically disables mutually conflicting rules within the `ALL` set.

Warning: new rules added in future versions will be implicitly enabled, potentially breaking CI on upgrades. Pin your Ruff version or use explicit selection.
