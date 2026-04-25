# Type System

ty supports all typing features described in the [Python typing documentation](https://typing.python.org/en/latest/spec/index.html). This page highlights unique features that make ty's type system distinctive.

## Redeclarations

ty allows reusing the same symbol with a different type within the same scope:

```python
def split_paths(paths: str) -> list[Path]:
    paths: list[str] = paths.split(":")
    return [Path(p) for p in paths]
```

The `paths` parameter is first typed as `str`, then redeclared as `list[str]`. This enables more flexible code patterns without requiring intermediate variables.

**Playground:** [Try this example](https://play.ty.dev/80a74c95-a43e-4a3d-8c26-f88e879d7dcb)

## Intersection Types

ty has first-class support for intersection types. Unlike union types `A | B` (either A or B), intersection types `A & B` mean "both A and B".

### Type Narrowing with Intersections

Type narrowing in ty is based on intersections:

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

After the `isinstance` check, `obj` has type `Serializable & Versioned`, allowing access to methods from both types.

**Playground:** [Try this example](https://play.ty.dev/39241435-5e78-4ce9-817f-ce65be73a6ed)

### Intersections with Gradual Types

Intersections work with gradual types like `Any` or `Unknown`:

```python
def print_content(data: bytes):
    obj = untyped_library.deserialize(data)
    
    if isinstance(obj, Iterable):
        reveal_type(obj)  # Unknown & Iterable
        print(obj.description)  # Access attributes from Unknown
        for part in obj:  # Use as Iterable
            print("*", part.description)
    else:
        print(obj.description)
```

The intersection `Unknown & Iterable` allows using `obj` as an iterable while still accessing attributes from the original unknown type.

**Playground:** [Try this example](https://play.ty.dev/8f98820e-7306-4d69-b572-56d69ba910f)

### `hasattr` Narrowing

Intersection types are used in `hasattr` narrowing:

```python
class Person:
    name: str

class Animal:
    species: str

def greet(being: Person | Animal | None):
    if hasattr(being, "name"):
        # being is now: Person | (Animal & <Protocol with 'name'>)
        print(f"Hello, {being.name}!")
    else:
        print("Hello there!")
```

- `Person` is preserved (has `name` attribute)
- `Animal` is intersected with a synthetic protocol (subclasses might add `name`)
- `None` is excluded (final type with no `name` attribute)

**Playground:** [Try this example](https://play.ty.dev/31f2c718-516a-4a85-80e2-2a4682b818f1)

**Tip:** Make classes `@final` to exclude them from narrowed types:
```python
@final
class Animal:
    species: str
```

### Explicit Intersection Types

Use `Intersection` from `ty_extensions` for direct annotations:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ty_extensions import Intersection
    
    type SerializableVersioned = Intersection[Serializable, Versioned]

def output_as_json(obj: SerializableVersioned) -> str:
    ...
```

**Playground:** [Try this example](https://play.ty.dev/f003e901-0e45-4f45-9759-d6db9d5e66)

## Top and Bottom Materializations

Gradual types have special materializations. The **top materialization** represents the "largest" type a gradual type can materialize to.

### Top Materialization Examples

```python
@final
class Item: ...

def process(items: Item | list[Item]):
    if isinstance(items, list):
        reveal_type(items)  # list[Item]
```

When checking `isinstance(…, list)`, ty intersects with the top materialization of `list[Unknown]`.

**Playground:** [Try this example](https://play.ty.dev/f1306120-0b8d-4ed5-8362-1f2d379eae2b)

**Note:** The `@final` decorator is important. Without it, the inferred type becomes `(Item & Top[list[Unknown]]) | list[Item]` to account for classes inheriting from both `Item` and `list`.

## Reachability Based on Types

Reachability analysis in ty is based on type inference, detecting unreachable branches in more situations than pattern-matching approaches:

```python
import pydantic
from pydantic import BaseModel

PYDANTIC_V2 = pydantic.__version__.startswith("2.")

class Person(BaseModel):
    name: str

def to_json(person: Person):
    if PYDANTIC_V2:
        return person.model_dump_json()  # No error with pydantic 1.x
    else:
        return person.json()  # No error with pydantic 2.x
```

ty evaluates `pydantic.__version__.startswith("2.")` at type-checking time and only considers the reachable branch, avoiding errors for the other branch.

**Playground:** [Try this example](https://play.ty.dev/34a227bb-93d5-405e-86c3-72f57ec5642e)

## Gradual Guarantee

ty avoids false positive type errors in untyped code:

```python
class RetryPolicy:
    max_retries = None

policy = RetryPolicy()
policy.max_retries = 1  # No error!
```

Other type checkers assume `max_retries` is `None`, causing an error. ty treats it as `Unknown | None`, allowing assignment while still tracking that `None` is a possible value.

**Playground:** [Try this example](https://play.ty.dev/a5286db1-cdfd-45e7-af54-29649ba5c423)

Users can opt into stricter checking by adding type annotations:
```python
class RetryPolicy:
    max_retries: int | None = None
```

## Fixpoint Iteration

For cyclic type dependencies, ty uses fixpoint iteration to infer types:

```python
class LoopingCounter:
    def __init__(self):
        self.value = 0
    
    def tick(self):
        self.value = (self.value + 1) % 5

reveal_type(LoopingCounter().value)  # Unknown | Literal[0, 1, 2, 3, 4]
```

ty iterates until the type converges. Without the modulo, the union would grow indefinitely, falling back to `int` after a certain number of iterations.

**Playground:** [Try this example](https://play.ty.dev/64400d96-ee1b-48f3-8361-b583dddddf82)

## Comparison with Other Type Checkers

### vs mypy

| Feature | mypy | ty |
|---------|------|-----|
| Intersection types | Limited (via `cast`) | First-class support |
| Redeclarations | Not allowed | Fully supported |
| Gradual guarantee | Stricter (more errors) | More permissive |
| Reachability analysis | Pattern-based | Type-based |
| Performance | Slower | 10x-100x faster |

### vs Pyright

| Feature | Pyright | ty |
|---------|---------|-----|
| Intersection types | Narrowing only | First-class + annotations |
| Incremental analysis | Coarse-grained | Fine-grained |
| Untyped code handling | Strict | Gradual guarantee |
| Language server | Yes | Yes (faster) |

## Best Practices

1. **Use redeclarations for type refinement** - Avoid intermediate variables when narrowing types
2. **Leverage intersection types** - More precise than unions for `isinstance` checks
3. **Make classes `@final` when appropriate** - Improves type narrowing precision
4. **Embrace gradual typing** - Add annotations incrementally without breaking existing code
5. **Use `ty_extensions` for advanced patterns** - Explicit intersection types for complex scenarios

## Playground

Try ty's type system features online at [play.ty.dev](https://play.ty.dev) - perfect for experimenting and sharing examples.

## Next Steps

- Configure [rules](./03-rules.md) to control diagnostic severity
- Set up [suppression](./04-suppression.md) for legitimate edge cases
- Integrate with your [editor](./05-editors.md) for real-time type checking
- Customize [configuration](./07-configuration.md) for project-specific needs
