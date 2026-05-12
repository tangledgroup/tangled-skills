# Python Category Theory

## Contents
- pycategories Library
  - Installation and Imports
  - Data Types (Maybe, Either, Validation)
  - Typeclass Hierarchy (Semigroup → Monad)
  - Defining Custom Instances
  - Law Checking
  - Utilities
  - Quickstart Workflow
- category-theory-python Library
  - Module Structure
  - Monoid Implementations
  - Functor and Applicative
  - Property-Based Testing with Hypothesis
  - Advanced Python Typing
- Comparing the Two Libraries

## pycategories Library

A Python 3 library implementing category theory typeclasses with a Haskell-influenced interface. Provides data types (Maybe, Either, Validation), typeclass instances for built-in types, and APIs for defining custom instances with law verification.

Install: `pip install pycategories`

Source: https://gitlab.com/danielhones/pycategories

### Data Types

Each data type defines a class with data constructors that create and return objects.

**Maybe**: Represents optional values. Two constructors: `Just(value)` and `Nothing()`.

```python
from categories.maybe import Just, Nothing

x = Just(42)       # Just(42)
y = Nothing()      # Nothing
```

Pattern matching via `.match()`:

```python
data = Just("hello")
if data.match(Just):
    print(data.value)  # "hello"
else:
    print("nothing")
```

**Either**: Tagged union with `Left(error)` and `Right(value)`. For error handling with messages instead of silent failure.

**Validation**: Similar to Either but with applicative semantics — accumulates all errors instead of short-circuiting on the first.

### Typeclass Hierarchy

pycategories implements a hierarchy mirroring Haskell's typeclass system:

```
Semigroup     — associative binary operation (sappend)
  ↓
Monoid        — semigroup + identity element (mempty, mappend)
  ↓
Functor       — map function over structure (fmap)
  ↓
Applicative   — functor + pure values + apply (pure, apply)
  ↓
Monad         — applicative + sequential binding (mreturn, bind)
```

### Defining Custom Instances

Each typeclass module provides an `instance()` function to register implementations for custom types.

```python
from categories import monoid, functor, fmap, mappend

# Monoid instance for dict (merge by keys, later wins)
monoid.instance(dict,
    mempty=lambda: {},
    mappend=lambda a, b: dict(**a, **b))

# Functor instance for dict (map over values)
functor.instance(dict,
    fmap=lambda f, xs: {k: f(v) for k, v in xs.items()})

# Use them
result = mappend({'x': 1}, {'y': 2})   # {'x': 1, 'y': 2}
result = fmap(lambda x: x * 2, {'a': 3})  # {'a': 6}
```

### Law Checking

Each typeclass module provides functions that return `True`/`False` indicating whether an instance obeys its laws. Call with example values of the type being tested.

```python
from categories import monoid, functor

# Monoid laws
monoid.identity_law({'a': 1, 'b': 2})                          # True
monoid.associativity_law({'a': 1}, {'b': 2}, {'c': 3})         # True

# Functor laws
functor.identity_law({'a': 1})                                  # True
functor.composition_law(lambda x: x.upper(),                   # True
                        lambda y: y[:3],
                        {'x': 'foobar', 'y': 'bazquux'})
```

### Utilities

| Function | Purpose |
|----------|---------|
| `compose(*fs)` | Right-to-left function composition: `compose(f, g)(x) == f(g(x))` |
| `flip(f)` | Reverse argument order of a two-argument function |
| `unit(x)` | Identity function (returns its argument) |
| `fmap(f, fa)` | Apply function within functor context |
| `apply(ff, fa)` | Apply wrapped function to wrapped value (Applicative) |
| `bind(ma, f)` | Sequential binding (Monad): `ma >>= f` |
| `mappend(a, b)` | Monoid binary operation |
| `mempty(type)` | Monoid identity element |

### Quickstart Workflow

Typical pycategories workflow: data constructors → lifting with `fmap`/`apply`/`bind` → defining custom instances → verifying laws.

```python
from functools import partial
from categories import fmap
from categories.maybe import Just, Nothing
from categories.utils import compose

# Step 1: Work with data types
def maybe_read_file(path):
    if os.path.exists(path):
        with open(path) as f:
            return Just(f.read())
    return Nothing()

# Step 2: Lift functions into context
uppercased = fmap(lambda x: x.upper(), maybe_read_file("data.txt"))

# Step 3: Compose operations
process = compose(partial(fmap, print), lambda p: fmap(str.upper, maybe_read_file(p)))
process("data.txt")  # Prints content or nothing
```

## category-theory-python Library

A Python library implementing common category theory structures based on Milewski's CTFP. Uses property-based testing with Hypothesis and advanced Python typing (protocols, TypeVar bounds).

Source: https://github.com/finsberg/category-theory-python

### Module Structure

| Module | Contents |
|--------|----------|
| `core.py` | Base classes: `Monoid`, `CommutativeMonoid`, `Functor`, `Applicative`, `Atomic` |
| `monoid.py` | Concrete monoids: `String`, `IntPlus`, `IntProd`, `MaybeIntPlus`, `MaybeIntProd`, `All`, `Any` |
| `functor.py` | Functor implementations: `List`, `Maybe` (`Just`, `Nothing`) |
| `applicative.py` | Applicative implementations: `Maybe` (extends functor.Maybe), `Validation` |
| `operations.py` | Utilities: `identity()`, `compose()`, `fold()`, `foldr()`, `is_nothing()` |
| `par_operations.py` | Parallel fold using dask.delayed |

### Monoid Implementations

The library provides concrete monoid classes following the CTFP curriculum:

```python
from category_theory.monoid import IntPlus, IntProd, String, All, Any

# IntPlus: (Z, +, 0) — commutative monoid
a = IntPlus(3) + IntPlus(5)       # IntPlus(8)
e = IntPlus.e()                    # IntPlus(0)

# IntProd: (Z, *, 1) — commutative monoid
b = IntProd(3) * IntProd(5)        # IntProd(15)

# String: (String, concat, "") — commutative monoid
s = String("hello") + String(" world")  # String("hello world")

# All: (bool, AND, True) — commutative monoid
# Any: (bool, OR, False) — commutative monoid
```

**MaybeIntPlus/MaybeIntProd**: Monoids over `Optional[int]` where `None` propagates through the operation. Models partiality in monoidal computation.

### Functor and Applicative

```python
from category_theory.functor import List, Just, Nothing, maybe

# List functor
lst = List([1, 2, 3])
mapped = lst.map(lambda x: x * 2)   # List([2, 4, 6])

# Maybe functor with smart constructor
j = maybe(42)       # Just(42)
n = maybe(None)     # Nothing
mapped = j.map(lambda x: x + 1)  # Just(43)
nothing_mapped = n.map(lambda x: x + 1)  # Nothing
```

### Property-Based Testing with Hypothesis

The library uses Hypothesis for property-based testing of monoid and functor laws, ensuring correctness across random inputs:

```python
from hypothesis import given, strategies as st
from category_theory import monoid

@given(st.integers(), st.integers(), st.integers())
def test_associativity(a_, b_, c_):
    a, b, c = monoid.IntPlus(a_), monoid.IntPlus(b_), monoid.IntPlus(c_)
    assert a + (b + c) == (a + b) + c

@given(st.integers())
def test_identity(a_):
    a = monoid.IntPlus(a_)
    e = monoid.IntPlus.e()
    assert a + e == e + a == a
```

This pattern — defining typeclass instances and verifying laws with property-based testing — is the recommended approach for any custom typeclass implementation in Python.

### Advanced Python Typing

The library investigates advanced typing features:
- `typing.TypeVar` for generic parameters (`a`, `b`)
- `typing.Generic` for parameterized base classes
- `typing.TypeGuard` in `is_nothing()` for narrow type checking
- ABC (Abstract Base Classes) with `@abstractmethod` for typeclass interfaces

### Parallel Operations

`par_operations.py` provides parallel fold using dask.delayed, chunking iterables and folding each chunk in parallel before combining:

```python
from category_theory import par_operations as parop
from category_theory.monoid import IntPlus

values = [IntPlus(v) for v in range(10000)]
result = parop.fold(values, IntPlus, chunk_size=100).compute()
# result == IntPlus(49995000)
```

## Comparing the Two Libraries

| Feature | pycategories | category-theory-python |
|---------|-------------|----------------------|
| Typeclasses | Semigroup, Monoid, Functor, Applicative, Monad | Monoid, Functor, Applicative |
| Data types | Maybe, Either, Validation | Maybe (via functor/applicative), List |
| Instance API | `monoid.instance(type, mempty, mappend)` | Inheritance from base classes |
| Law checking | Built-in law functions per typeclass | Hypothesis property tests |
| Utilities | compose, flip, unit, fmap, apply, bind | identity, compose, fold, foldr |
| Testing | Unit tests | Property-based (Hypothesis) |
| Typing | Basic | Advanced (TypeVar, TypeGuard, ABC) |
| Parallel ops | No | Yes (dask.delayed) |

**Use pycategories** for: Haskell-style typeclass pattern, Monad support, Either/Validation types, built-in law checking.

**Use category-theory-python** for: CTFP curriculum alignment, property-based testing patterns, parallel folds, advanced typing study.
