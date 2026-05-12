# Design Patterns

## Contents
- Product/Coproduct Pattern for API Design
- Functor Pattern: Uniform Transformation
- Monad Pattern: Sequencing Effects
- Initial Algebra Pattern: Recursion Schemes
- Adjunction Pattern: Free/Forgetful Duality
- Universal Property Pattern: Specification-Based Interfaces

## Product/Coproduct Pattern for API Design

**CT concept:** Products combine data (both required); coproducts offer alternatives (one of several).

**Design decision:** Model compound data as products (tuples/records) when all fields are required. Model alternatives as coproducts (tagged unions) when exactly one variant applies.

```python
# Product: all fields present
from typing import NamedTuple
class User(NamedTuple):
    name: str
    email: str
    # Both always present — categorical product

# Coproduct: exactly one variant
from typing import Union
PaymentStatus = Union[
    {"type": "pending"},
    {"type": "completed", "amount": float},
    {"type": "failed", "reason": str}
]
# Tagged union — categorical coproduct (like Either generalized)
```

**ADTs as polynomial functors:** Every algebraic data type decomposes into products and coproducts. `List a` ≅ 1 + a × List a (coproduct of unit and product). This decomposition enables systematic reasoning about data structure properties.

## Functor Pattern: Uniform Transformation

**CT concept:** A functor maps morphisms while preserving composition and identity.

**Design decision:** When a data structure needs to support "apply this function to the contained value(s)," implement the Functor pattern. The laws (`fmap(id) == id`, `fmap(g∘f) == fmap(g)∘fmap(f)`) guarantee that transformations compose correctly.

```python
# Python: container with uniform transformation
class Box:
    def __init__(self, value):
        self.value = value

    def map(self, func):
        # fmap: apply function to contained value
        return Box(func(self.value))

# Law: fmap(id) == id
assert Box(42).map(lambda x: x).value == 42

# Law: fmap(g . f) == fmap(g) . fmap(f)
b = Box(3)
assert b.map(lambda x: x * 2).map(lambda x: x + 1).value == \
       b.map(lambda x: (x * 2) + 1).value
```

**When to use:** Any wrapper type where you want to transform contents without unwrapping. Maybe, List, Result, Future all follow this pattern.

## Monad Pattern: Sequencing Effects

**CT concept:** A monad is a monoid in endofunctors — it provides `return` (unit) and `bind` (multiplication) for sequencing effectful computations.

**Design decision:** When operations produce values wrapped in a context (error, option, state, I/O), use the monad pattern to sequence them without manual unwrapping.

```python
from categories.maybe import Just, Nothing
from categories import bind

# Sequencing Maybe computations without explicit None checks
def parse_int(s):
    try:
        return Just(int(s))
    except ValueError:
        return Nothing()

def invert(x):
    if x == 0:
        return Nothing()
    return Just(1 / x)

# Chain: parse → invert, short-circuiting on any Nothing
result = bind(parse_int("42"), invert)   # Just(0.0238...)
result = bind(parse_int("abc"), invert)  # Nothing
result = bind(parse_int("0"), invert)    # Nothing
```

**Kleisli composition:** Effectful functions `a -> M b` compose via Kleisli composition, turning the monad into a category where effectful computations are ordinary morphisms.

## Initial Algebra Pattern: Recursion Schemes

**CT concept:** The initial F-algebra is the fixed point of functor F. By Lambek's lemma, the structure map is an isomorphism. Catamorphisms (folds) are the unique morphism from the initial algebra.

**Design decision:** When working with recursive data structures, use catamorphisms to reduce them to a single value. This separates the traversal pattern from the reduction logic.

```python
# Catamorphism (fold) for natural numbers
# Nat is the initial algebra for F(X) = 1 + X
def cata_nat(algebra, n):
    """Fold a natural number using an algebra (zero_val, succ_fn)"""
    zero_val, succ_fn = algebra
    result = zero_val
    for _ in range(n):
        result = succ_fn(result)
    return result

# Sum 0..n-1: start at 0, each step adds current value
total = cata_nat((0, lambda acc: acc + (total := total) if False else acc), 5)

# Simpler: list fold (catamorphism for List a, initial algebra of F(X) = 1 + a*X)
def fold_list(algebra, lst):
    nil_val, cons_fn = algebra
    result = nil_val
    for item in reversed(lst):
        result = cons_fn(item, result)
    return result

# Sum a list
total = fold_list((0, lambda x, acc: x + acc), [1, 2, 3, 4, 5])  # 15

# Any fold: map → reduce pattern is a catamorphism
upper_joined = fold_list(("", lambda x, acc: x.upper() + "," + acc), ["a", "b", "c"])
```

**Anamorphisms** (unfolds) generate recursive structures from a seed. **Hylomorphisms** combine unfold then fold — produce intermediate structure then consume it.

## Adjunction Pattern: Free/Forgetful Duality

**CT concept:** Adjunctions *F* ⊣ *G* provide optimal approximation of inverses. The left adjoint *F* is "free" (builds structure), the right adjoint *G* is "forgetful" (strips structure).

**Design decision:** When you need to generate structured data from raw input and interpret structured data back to raw output, the adjunction pattern ensures round-trip consistency via unit and counit.

```python
# Free monoid: build lists from elements (left adjoint)
# Forgetful: extract elements from lists (right adjoint)

free = list        # Set -> List: free monoid on a set
forget = lambda m: list(m)  # List -> Set: forget structure

# Unit: element -> [element] (embed into free structure)
# x -> free(x) = [x]

# Counit: flatten nested free structure
# free(forget(m)) -> m, i.e., flatten [[a,b],[c]] -> [a,b,c]
counit = lambda m: [x for sub in m for x in sub]

# Triangle identity: forget(counit(free(x))) == x
assert forget(counit(free([1, 2, 3]))) == [1, 2, 3]
```

**Practical applications:** Parsing (free) / serialization (forgetful), AST construction / code generation, event sourcing (build state from events / extract events from state).

## Universal Property Pattern: Specification-Based Interfaces

**CT concept:** Universal properties define objects by how morphisms factor through them — a specification, not an implementation.

**Design decision:** Design APIs by stating what mappings must exist and be unique, not how to construct the result internally. This enables swapping implementations without changing client code.

```python
from abc import ABC, abstractmethod

# Universal property: a "Product" interface specifies projections
# and the unique factorization property
class Product(ABC):
    """Universal property of a product: for any X with maps to A and B,
    there exists a unique map to the product that factors through projections."""

    @abstractmethod
    def proj1(self):
        """Projection to first component"""
        ...

    @abstractmethod
    def proj2(self):
        """Projection to second component"""
        ...

    @classmethod
    @abstractmethod
    def from_pair(cls, a, b):
        """Universal construction: given maps to A and B,
        construct the unique element of the product"""
        ...

# Implementation 1: tuple-based
class TupleProduct(Product):
    def __init__(self, a, b):
        self._pair = (a, b)
    def proj1(self): return self._pair[0]
    def proj2(self): return self._pair[1]
    @classmethod
    def from_pair(cls, a, b): return cls(a, b)

# Implementation 2: dict-based (same interface, different internals)
class DictProduct(Product):
    def __init__(self, a, b):
        self._data = {'first': a, 'second': b}
    def proj1(self): return self._data['first']
    def proj2(self): return self._data['second']
    @classmethod
    def from_pair(cls, a, b): return cls(a, b)

# Client code works with either implementation
def use_product(p: Product):
    return p.proj1() + p.proj2()

assert use_product(TupleProduct.from_pair(3, 4)) == 7
assert use_product(DictProduct.from_pair(3, 4)) == 7
```

This pattern — specifying interfaces by universal properties rather than implementation details — is the categorical approach to abstract data types. The interface says "here are the operations and their relationships" without dictating how they work internally.
