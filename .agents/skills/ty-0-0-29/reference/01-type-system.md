# Type System

ty supports all typing features described in the [Python typing specification](https://typing.python.org/en/latest/spec/index.html). This page highlights ty's unique type system features.

## Redeclarations

ty allows reusing the same symbol with a different type within a function:

```python
from pathlib import Path

def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")  # redeclared as list[str]
    return [Path(p) for p in paths]
```

## Intersection Types

ty has first-class support for intersection types. Unlike union `A | B` (either A or B), intersection `A & B` means both A and B. Type narrowing in ty is based on intersections:

```python
def output_as_json(obj: Serializable) -> str:
    if isinstance(obj, Versioned):
        reveal_type(obj)  # reveals: Serializable & Versioned
        return str({
            "data": obj.serialize_json(),
            "version": obj.version
        })
    else:
        return obj.serialize_json()
```

Intersections with gradual types (`Any` or `Unknown`):

```python
def print_content(data: bytes):
    obj = untyped_library.deserialize(data)  # type: Unknown

    if isinstance(obj, Iterable):
        # obj is now Unknown & Iterable
        print(obj.description)
        for part in obj:
            print("*", part.description)
    else:
        print(obj.description)
```

`hasattr` narrowing also uses intersections:

```python
class Person:
    name: str

class Animal:
    species: str

def greet(being: Person | Animal | None):
    if hasattr(being, "name"):
        # being is now Person | (Animal & <Protocol with members 'name'>)
        print(f"Hello, {being.name}!")
    else:
        print("Hello there!")
```

For direct use in annotations, import `Intersection` from `ty_extensions`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import Intersection
    type SerializableVersioned = Intersection[Serializable, Versioned]

def output_as_json(obj: SerializableVersioned) -> str:
    ...
```

## Top and Bottom Materializations

Gradual types have special materializations. The top materialization of `Any` is `object`, and the top materialization of `Any & int` is `int`. For invariant generic classes, ty intersects with the top materialization during `isinstance` checks:

```python
@final
class Item: ...

def process(items: Item | list[Item]):
    if isinstance(items, list):
        reveal_type(items)  # reveals: list[Item]
```

Without `@final`, the type becomes `(Item & Top[list[Unknown]]) | list[Item]` — accounting for possible subclasses of both `Item` and `list`.

## Reachability Based on Types

ty's reachability analysis is based on type inference, detecting unreachable branches in many situations:

```python
import pydantic
from pydantic import BaseModel

PYDANTIC_V2 = pydantic.__version__.startswith("2.")

class Person(BaseModel):
    name: str

def to_json(person: Person):
    if PYDANTIC_V2:
        return person.model_dump_json()  # no error when checking with 1.x
    else:
        return person.json()  # no error when checking with 2.x
```

This works because `pydantic.__version__.startswith("2.")` can be evaluated at type-checking time.

## Gradual Guarantee

ty avoids false positives in untyped code by using `Unknown`:

```python
class RetryPolicy:
    max_retries = None

policy = RetryPolicy()
policy.max_retries = 1  # no error — max_retries is Unknown | None
```

The attribute is treated as `Unknown | None` — the type is not fully known, but `None` is definitely a possible value. Users can opt into stricter checking by adding annotations (`int | None`).

## Fixpoint Iteration

For cyclically dependent types, ty uses fixpoint iteration:

```python
class LoopingCounter:
    def __init__(self):
        self.value = 0

    def tick(self):
        self.value = (self.value + 1) % 5

# reveals: Unknown | Literal[0, 1, 2, 3, 4]
reveal_type(LoopingCounter().value)
```

ty starts with `Unknown | Literal[0]` and iterates until convergence. Without the modulo, the union would grow indefinitely — ty falls back to `int` after a certain number of iterations.

## Special Numeric Types

The Python typing spec includes a special rule where `int` can be used wherever `float` is expected:

```python
def circle_area(radius: float) -> float:
    return 3.14 * radius * radius

circle_area(2)  # OK: int is allowed where float is expected
```

ty treats `float` as meaning `int | float` and makes this explicit in type hints. Similarly, `complex` is treated as `int | float | complex`.

For strict float-only acceptance, use `ty_extensions.JustFloat`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import JustFloat
else:
    JustFloat = float

def only_actual_floats_allowed(f: JustFloat) -> None: ...

only_actual_floats_allowed(1.0)  # OK
only_actual_floats_allowed(1)    # error: invalid-argument-type
```

## Invariant Generics

`list` is invariant — `list[Subtype]` is not a subtype of `list[Supertype]`:

```python
def modify(entries: list[Entry]):
    entries.append(File("README.txt"))  # mutation

directories: list[Directory] = [Directory("Downloads")]
modify(directories)  # error — would violate list[Directory] type
```

Use `Sequence[Entry]` (covariant) for read-only access, or `Mapping[str, V]` as a covariant alternative to `dict[str, V]`.
