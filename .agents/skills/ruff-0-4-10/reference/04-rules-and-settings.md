# Rules and Settings

## Rule Categories

Ruff supports over 800 lint rules across 50+ rule categories. Key categories:

### Core Categories (enabled by default)

- **`E`** — pycodestyle errors (e.g., `E402` module import not at top of file, `E711` comparison to `None`)
- **`F`** — Pyflakes (e.g., `F401` unused import, `F821` undefined name, `F841` unused variable)

### Popular Add-On Categories

- **`UP`** — pyupgrade (modernize Python syntax, e.g., `UP035` use `collections.abc` instead of `typing`)
- **`B`** — flake8-bugbear (common bugs, e.g., `B006` mutable default argument, `B007` loop variable not used)
- **`I`** — isort (import sorting, e.g., `I001` unsorted imports, `I003` illegal import alias)
- **`D`** — pydocstyle (docstring conventions, e.g., `D100` missing docstring in public module)
- **`SIM`** — flake8-simplify (code simplification, e.g., `SIM108` use ternary instead of if-block)
- **`C9`** — McCabe complexity (`C901` function is too complex)
- **`RUF`** — Ruff-specific rules (e.g., `RUF100` unused noqa, `RUF015` unnecessary iterable allocation)

### Other Notable Categories

- **`ANN`** — flake8-annotations (missing type annotations)
- **`ARG`** — flake8-unused-arguments (unused function arguments)
- **`A`** — flake8-builtins (shadowing builtins)
- **`COM`** — flake8-commas (trailing commas)
- **`C4`** — flake8-comprehensions (comprehension simplification)
- **`DTZ`** — flake8-datetimez (naive datetime usage)
- **`EM`** — flake8-errmsg (error message formatting)
- **`ERA`** — eradicate (commented-out code detection)
- **`EXE`** — flake8-executable (executable file issues)
- **`FA`** — flake8-future-annotations (future annotations enforcement)
- **`FLY`** — flynt (f-string conversion)
- **`G`** — flake8-logging-format (logging format strings)
- **`ICN`** — flake8-import-conventions (import alias conventions)
- **`INP`** — flake8-no-pep420 (implicit namespace packages)
- **`ISC`** — flake8-implicit-str-concat (implicit string concatenation)
- **`N`** — pep8-naming (naming conventions)
- **`PD`** — pandas-vet (pandas-specific rules)
- **`PGH`** — pygrep-hooks (security-related patterns)
- **`PIE`** — flake8-pie (miscellaneous improvements)
- **`PL`** — pylint (pylint rules re-implemented in Ruff)
- **`PT`** — flake8-pytest-style (pytest style rules)
- **`PTH`** — flake8-use-pathlib (use `pathlib` instead of `os.path`)
- **`Q`** — flake8-quotes (quote style enforcement)
- **`RET`** — flake8-return (return statement simplification)
- **`RSE`** — flake8-raise (raise statement simplification)
- **`S`** — flake8-bandit (security checks)
- **`SLF`** — flake8-self (private member access)
- **`SLOT`** — flake8-slots (`__slots__` enforcement)
- **`T20`** — flake8-print (print/debugger statements)
- **`TCH`** — flake8-type-checking (type-checking import blocks)
- **`TD`** — flake8-todos (TODO comment formatting)
- **`TID`** — flake8-tidy-imports (banned APIs, relative imports)
- **`TRY`** — tryceratops (exception handling improvements)
- **`UP`** — pyupgrade (syntax modernization)
- **`W`** — pycodestyle warnings

## Key Settings

### Top-Level Settings

- **`exclude`** — List of paths to exclude (glob patterns). Default excludes `.git`, `node_modules`, `venv`, etc.
- **`extend-exclude`** — Additional paths to exclude on top of defaults.
- **`include`** — Override default file discovery patterns.
- **`extend-include`** — Add to default file discovery patterns.
- **`line-length`** — Maximum line length (default: `88`).
- **`indent-width`** — Number of spaces per indentation level (default: `4`).
- **`target-version`** — Minimum Python version (`py37`, `py38`, ..., `py314`). Default: `py310`.
- **`respect-gitignore`** — Respect `.gitignore` exclusions (default: `true`).
- **`src`** — List of source directories for import resolution.
- **`extend`** — Path to another config file to inherit from.

### Linter Settings (`[lint]`)

- **`select`** — Rule codes or prefixes to enable (default: `["E4", "E7", "E9", "F"]`).
- **`ignore`** — Rule codes or prefixes to disable.
- **`extend-select`** — Add rules on top of existing selection.
- **`fixable`** — Rules eligible for auto-fix (default: `["ALL"]`).
- **`unfixable`** — Rules ineligible for auto-fix (default: `[]`).
- **`preview`** — Enable preview mode for unstable rules (`false` by default).
- **`explicit-preview-rules`** — Require explicit selection of each preview rule.
- **`dummy-variable-rgx`** — Regex for dummy variables (default: `"^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"`).
- **`per-file-ignores`** — Dict mapping file patterns to rule codes to ignore.
- **`extend-per-file-ignores`** — Add per-file ignores on top of existing ones.
- **`task-tags`** — Task tags to recognize (default: `["TODO", "FIXME", "XXX"]`).
- **`typing-modules`** — Modules whose exports should be treated as `typing` members.
- **`typing-extensions`** — Allow fallback to `typing_extensions` (`true` by default).

### Formatter Settings (`[format]`)

- **`quote-style`** — `"double"` (default) or `"single"`.
- **`indent-style`** — `"space"` (default) or `"tab"`.
- **`skip-magic-trailing-comma`** — `false` (default).
- **`line-ending`** — `"auto"` (default), `"lf"`, or `"crlf"`.
- **`docstring-code-format`** — `false` (default).
- **`docstring-code-line-length`** — `"dynamic"` (default) or integer.
- **`preview`** — Enable preview formatting style (`false` by default).

### Plugin-Specific Settings

Many Flake8 plugins have their own configuration subsections:

**flake8-annotations** (`[lint.flake8-annotations]`):
- `allow-star-arg-any` — Suppress `ANN401` for `*args`/`**kwargs`.
- `ignore-fully-untyped` — Suppress for fully untyped declarations.
- `mypy-init-return` — Allow omitting return type for `__init__`.
- `suppress-dummy-args` — Suppress for dummy arguments.
- `suppress-none-returning` — Suppress for functions returning only `None`.

**flake8-bandit** (`[lint.flake8-bandit]`):
- `allowed-markup-calls` — Callables safe to pass to `markupsafe.Markup`.
- `check-typed-exception` — Disallow `try-except-pass` for typed exceptions.
- `hardcoded-tmp-directory` — Directories considered temporary (default: `["/tmp", "/var/tmp", "/dev/shm"]`).

**flake8-bugbear** (`[lint.flake8-bugbear]`):
- `extend-immutable-calls` — Callables to consider immutable (e.g., `["fastapi.Depends", "fastapi.Query"]`).

**flake8-comprehensions** (`[lint.flake8-comprehensions]`):
- `allow-dict-calls-with-keyword-arguments` — Allow `dict(a=1, b=2)`.

**flake8-copyright** (`[lint.flake8-copyright]`):
- `author` — Author name to enforce in copyright notice.
- `min-file-size` — Minimum file size for copyright enforcement.
- `notice-rgx` — Regex for matching copyright notices.

**flake8-import-conventions** (`[lint.flake8-import-conventions]`):
- `aliases` — Conventional import aliases (default includes `numpy=np`, `pandas=pd`, etc.).
- `extend-aliases` — Additional aliases.
- `banned-from` — Modules that should not use `from ... import`.

**flake8-pytest-style** (`[lint.flake8-pytest-style]`):
- `fixture-parentheses` — Whether `@pytest.fixture()` needs parentheses.
- `mark-parentheses` — Whether `@pytest.mark.foo()` needs parentheses.
- `parametrize-names-type` — `"csv"`, `"tuple"` (default), or `"list"`.
- `parametrize-values-type` — `"tuple"` or `"list"` (default).
- `parametrize-values-row-type` — `"tuple"` (default) or `"list"`.

**pydocstyle** (`[lint.pydocstyle]`):
- `convention` — Docstring convention: `"google"`, `"numpy"`, or `"pep257"`.
- `property-decorators` — Decorators that indicate properties.

## Preview Mode

Preview mode enables unstable features (new rules, fixes, formatter style changes). Enable via:

```toml
[lint]
preview = true    # Preview lint rules only.

[format]
preview = true    # Preview formatting style only.
```

Or via CLI: `ruff check --preview` / `ruff format --preview`.

Preview rules are **not** automatically enabled by selecting their category — you must also enable preview mode. With `explicit-preview-rules = true`, each preview rule must be selected by its exact code.

### Deprecated Rules in Preview

When preview mode is enabled, deprecated rules are disabled. If explicitly selected, an error is raised.

## Versioning Policy

Ruff uses a custom versioning scheme:

- **Minor** version increases for breaking changes (deprecated feature removal, config changes, stable rule behavior changes, stable formatter style changes).
- **Patch** version increases for bug fixes, new backwards-compatible config options, preview rules/fixes, and deprecations.

New rules are always added in preview mode and remain there for at least one minor release before stabilization.
