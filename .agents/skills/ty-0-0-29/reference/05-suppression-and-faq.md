# Suppression and FAQ

## Suppression Comments

### ty suppression comments

Suppress a rule violation inline with `# ty: ignore[<rule>]`:

```python
a = 10 + "test"  # ty: ignore[unsupported-operator]
```

Multi-line violations — place comment on first or last line:

```python
sum_three_numbers(  # ty: ignore[missing-argument]
    3,
    2
)

# or on the last line
sum_three_numbers(
    3,
    2
)  # ty: ignore[missing-argument]
```

Multiple rules on one line:

```python
sum_three_numbers("one", 5)  # ty: ignore[missing-argument, invalid-argument-type]
```

File-level suppression (before any Python code):

```python
# ty: ignore[invalid-argument-type]

sum_three_numbers(3, 2, "1")
```

Enumerating rule names is optional but strongly recommended.

### Standard type: ignore comments

ty supports PEP 484 `type: ignore` format:

```python
# Suppress all violations on the line
sum_three_numbers("one", 5)  # type: ignore

# Combine mypy and ty suppressions
sum_three_numbers("one", 5, 2)  # type: ignore[arg-type, ty:invalid-argument-type]
```

`type: ignore[ty:<rule>]` behaves like `ty: ignore[<rule>]`. Codes without `ty:` prefix are ignored by ty.

### Multiple suppression comments

Add `# ty: ignore` alongside other tool comments on the same line:

```python
result = calculate()  # ty: ignore[invalid-argument-type]  # fmt: skip
```

### Unused suppression comments

When `unused-ignore-comment` rule is enabled, ty reports unused `ty: ignore` and `type: ignore` comments. These can only be suppressed with `# ty: ignore[unused-ignore-comment]` — not with bare `# ty: ignore` or `# type: ignore`.

### @no_type_check directive

Suppress all violations inside a function:

```python
from typing import no_type_check

@no_type_check
def main():
    sum_three_numbers(1, 2)  # no error for missing argument
```

Decorating classes with `@no_type_check` is not supported.

## Typing FAQ

### What is the Unknown type?

`Unknown` represents types that could not be fully inferred. It behaves like `Any` but appears implicitly:

```python
from missing_module import MissingClass  # error: unresolved-import
reveal_type(MissingClass)  # Unknown
```

ty uses `Unknown | <known-type>` for the gradual guarantee, avoiding false positives in untyped code while still providing useful type information.

### Why can't I use list[Subtype] where list[Supertype] is expected?

`list` is invariant due to mutability. Use `Sequence[T]` (covariant) for read-only access:

```python
def total_size(entries: Sequence[Entry]) -> int:  # covariant
    return sum(entry.size_bytes() for entry in entries)
```

### Why does ty say Callable has no attribute __name__?

Not all callables have `__name__`. Use `getattr` with a default or `isinstance` check:

```python
name = getattr(operation, "__name__", "operation")
```

Or narrow with intersection types:

```python
if TYPE_CHECKING:
    from ty_extensions import Intersection
    type FunctionLikeCallable[R] = Intersection[Callable[[], R], FunctionType]
```

### What is Top[list[Unknown]]?

It represents "all possible lists of any element type". It appears in `isinstance(x, list)` checks when `x` could be a subclass of both the original type and `list`. Use `@final` on the class or check against the non-list type first.

### Does ty have a strict mode?

Not yet. Track [issue #1240](https://github.com/astral-sh/ty/issues/1240). In the meantime, use Ruff's `flake8-annotations` rules (ANN001, ANN002, ANN003, ANN201, ANN202, RUF045) to enforce explicit annotations.

### Why doesn't ty warn about missing type annotations?

ty infers `Unknown` for unannotated symbols without emitting errors. Use Ruff's `flake8-annotations` (`ANN`) rules for annotation enforcement.

### Why can't ty resolve my imports?

Common causes:
1. Virtual environment not discoverable — check `VIRTUAL_ENV` or `.venv`
2. Source code not in project root or `src/` — configure `environment.root`
3. Dependencies not installed — run with `-v` to see search paths
4. Compiled extensions only (`.so`/`.pyd`) — need stub files (`.pyi`)

### Does ty support monorepos?

Yes, with manual configuration:

```bash
# Run per-package
ty check --project packages/package-a
ty check --project packages/package-b
```

Or configure multiple roots:

```toml
[tool.ty.environment]
root = ["packages/package-a", "packages/package-b"]
```

Note: this treats all packages as a single project. Track [issue #819](https://github.com/astral-sh/ty/issues/819) for improvements.

### Does ty support PEP 723 inline-metadata scripts?

Single scripts can be checked with uv's `--with-requirements`:

```bash
uvx --with-requirements script.py ty check script.py
```

Multiple scripts with different dependencies are not yet recognized. Track [issue #691](https://github.com/astral-sh/ty/issues/691).

### Does ty support mypy plugins?

No. ty does not have a plugin system. Support for popular libraries (pydantic, SQLAlchemy, attrs, Django) may be added directly into ty.
