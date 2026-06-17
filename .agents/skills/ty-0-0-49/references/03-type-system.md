# Type System Features

## Redeclarations

ty allows reusing a symbol with a different type within the same scope:

```python
def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")  # Redeclaration — allowed
    return [Path(p) for p in paths]
```

This is useful for narrowing types after transformations without introducing new variable names. mypy would flag this as a redefinition error.

## Intersection types

Intersection types `A & B` mean "both A and B" (as opposed to union `A | B` meaning "either A or B"). ty uses intersections extensively for type narrowing:

```python
def output_as_json(obj: Serializable) -> str:
    if isinstance(obj, Versioned):
        reveal_type(obj)  # Serializable & Versioned
        return str({
            "data": obj.serialize_json(),   # From Serializable
            "version": obj.version           # From Versioned
        })
```

### Intersection with Unknown

Narrowing `Unknown` (from untyped code) with `isinstance` produces intersection types:

```python
obj = untyped_library.deserialize(data)  # type: Unknown

if isinstance(obj, Iterable):
    reveal_type(obj)  # Unknown & Iterable
    print(obj.description)   # Still accessible from Unknown
    for part in obj:         # Iterable protocol works
        ...
```

### hasattr narrowing with intersections

```python
def greet(being: Person | Animal | None):
    if hasattr(being, "name"):
        # being: Person | (Animal & <Protocol with 'name'>)
        # - Person kept (has .name)
        # - Animal intersected with synthetic protocol
        # - None excluded (final type, no .name)
        print(f"Hello, {being.name}!")
```

Use `@final` on `Animal` to exclude it entirely from the narrowed type.

### Explicit intersection types

When ty is your only type checker, use `ty_extensions.Intersection`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import Intersection
    type SerializableVersioned = Intersection[Serializable, Versioned]
else:
    SerializableVersioned = Serializable  # runtime fallback

def output(obj: SerializableVersioned) -> str: ...
```

## Top and bottom materializations

Gradual types have special materializations. `Top[list[Unknown]]` means "all possible lists of any element type" (not "a list of some unknown type").

```python
@final
class Item: ...

def process(items: Item | list[Item]):
    if isinstance(items, list):
        reveal_type(items)  # list[Item] — clean because Item is @final
```

Without `@final` on `Item`, the narrowed type becomes `(Item & Top[list[Unknown]]) | list[Item]` to account for possible subclasses of both `Item` and `list`.

## Reachability based on types

ty's reachability analysis uses type inference, not just pattern matching. This enables practical version-conditional code:

```python
import pydantic
from pydantic import BaseModel

PYDANTIC_V2 = pydantic.__version__.startswith("2.")

class Person(BaseModel):
    name: str

def to_json(person: Person):
    if PYDANTIC_V2:
        return person.model_dump_json()  # Reachable with pydantic 2.x
    else:
        return person.json()             # Reachable with pydantic 1.x
```

ty evaluates `pydantic.__version__.startswith("2.")` at type-checking time and only considers the reachable branch. This works for any expression that can be statically evaluated, not just `sys.version_info` checks.

## Gradual guarantee (partially typed code)

ty is designed for adoption into existing codebases:

- Unannotated function parameters and return types are inferred as `Unknown`
- No errors are emitted for missing annotations by default
- Type errors are still reported when `Unknown` interacts with concrete types unsafely
- Use Ruff's `flake8-annotations` (ANN) rules to enforce annotation coverage if desired

## The Unknown type

`Unknown` represents types that could not be fully inferred. It behaves like `Any` but appears implicitly:

```python
from missing_module import MissingClass  # error: unresolved-import
reveal_type(MissingClass)  # Unknown
```

Unannotated attributes default to `Unknown | None`:

```python
class Message:
    data = None

def receive(msg: Message):
    reveal_type(msg.data)  # Unknown | None
    msg.data = {"color": "blue"}  # OK (Unknown absorbs any type)
    # But must handle None:
    if msg.data is not None:
        process(msg.data)
```

## Numeric type widening

Per the Python typing spec, `float` accepts `int`:

```python
def circle_area(radius: float) -> float:  # Actually means int | float
    return 3.14 * radius * radius

circle_area(2)   # OK — int accepted where float expected
```

ty makes this explicit in hover and error messages. For strict `float` only, use `ty_extensions.JustFloat`. Same pattern for `complex` → `JustComplex`.

## Generic invariance

Built-in mutable containers are invariant:

```python
def modify(entries: list[Entry]):
    entries.append(File("README.txt"))

directories: list[Directory] = [Directory("Downloads")]
modify(directories)  # Error: list[Directory] not assignable to list[Entry]
```

Use `Sequence[T]` (covariant) when mutation isn't needed:

```python
def total_size(entries: Sequence[Entry]) -> int:  # Covariant — OK
    return sum(e.size_bytes() for e in entries)
```

For read-only `dict`, use `Mapping[K, V]` instead of `dict[K, V]`.

## Callable attributes

`Callable` does not guarantee `__name__`, `__qualname__`, `__module__`, or `__doc__`. Use `getattr(operation, "__name__", "default")` or narrow with `isinstance(operation, types.FunctionType)`.
