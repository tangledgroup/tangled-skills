# Programming Applications

## Contents
- Haskell Typeclasses and Category Theory
- Category Theory for Programmers (CTFP) Curriculum
- Python Libraries
- Composition as the Essence of Programming
- Algebraic Data Types Categorically
- Monadic Effects

## Haskell Typeclasses and Category Theory

Haskell's typeclass system directly encodes categorical structures. The category **Hask** has Haskell types as objects and functions as morphisms.

### Functor

```haskell
class Functor f where
    fmap :: (a -> b) -> f a -> f b
```

Laws (expressing functor axioms):
```haskell
fmap id  ==  id                    -- preserves identities
fmap (g . f) == fmap g . fmap f    -- preserves composition
```

Type constructors like `Maybe`, `[]` (lists), `IO`, and `(->) r` (reader) are endofunctors on **Hask**.

### Applicative

```haskell
class Functor f => Applicative f where
    pure  :: a -> f a
    (<*>) :: f (a -> b) -> f a -> f b
```

Represents a monoidal functor — it can lift pure values and apply functions within a context. Laws ensure compositionality.

### Monad

```haskell
class Applicative m => Monad m where
    return :: a -> m a
    (>>=)  :: m a -> (a -> m b) -> m b
```

Laws:
```haskell
return a >>= f  ==  f a
m >>= return    ==  m
(m >>= f) >>= g ==  m >>= (\x -> f x >>= g)
```

A monad encodes a computational context where values can be sequenced. Categorically, it is a monoid in the category of endofunctors under composition.

### Other Typeclasses

- **Foldable**: catamorphisms over functors
- **Traversable**: combines Functor and Foldable
- **Category** (from `Control.Category`): abstracts composition and identity for any arrow type
- **Arrow**: generalized morphisms with splitting and joining

## Category Theory for Programmers (CTFP) Curriculum

Bartosz Milewski's free book bridges category theory and programming. It uses Haskell and C++ examples, introducing concepts through code.

**Part One — Foundations:**
1. Category: The Essence of Composition
2. Types and Functions
3. Categories Great and Small
4. Kleisli Categories
5. Products and Coproducts
6. Simple Algebraic Data Types
7. Functors
8. Functoriality
9. Function Types
10. Natural Transformations

**Part Two — Universal Constructions:**
1. Declarative Programming
2. Limits and Colimits
3. Free Monoids
4. Representable Functors
5. The Yoneda Lemma
6. Yoneda Embedding

**Part Three — Advanced Topics:**
1. It's All About Morphisms
2. Adjunctions
3. Free/Forgetful Adjunctions
4. Monads: Programmer's Definition
5. Monads and Effects
6. Monads Categorically
7. Comonads
8. F-Algebras
9. Algebras for Monads
10. Ends and Coends
11. Kan Extensions
12. Enriched Categories
13. Topoi
14. Lawvere Theories
15. Monads, Monoids, and Categories

Available as a free PDF at https://github.com/hmemcpy/milewski-ctfp-pdf/ and as blog posts at https://bartoszmilewski.com/.

## Python Libraries

### pycategories

A Python 3 library implementing category theory typeclasses with a Haskell-influenced interface.

```python
from categories import apply
from categories.maybe import Just, Nothing

f = Just(lambda x: x ** 2)
x = Just(17)
print(apply(f, x))        # Just(289)
print(apply(f, Nothing()))  # Nothing

# Defining monoid instances
from categories import mappend, mempty, monoid
monoid.instance(dict, lambda: {}, lambda a, b: dict(**a, **b))
print(mappend({'foo': 'bar'}, {'rhu': 'barb'}))
# {'foo': 'bar', 'rhu': 'barb'}
```

Install: `pip install pycategories`

Source: https://gitlab.com/danielhones/pycategories

### category-theory-python

A Python library implementing common category theory structures, based on Milewski's CTFP. Covers monoids, functors, applicative functors, and monads with advanced Python typing.

Topics covered:
- Monoids (complete)
- Functors (in progress)
- Applicative Functors (in progress)
- Monads

Uses property-based testing with Hypothesis. Targets the latest Python version for full typing support.

Source: https://github.com/finsberg/category-theory-python

## Composition as the Essence of Programming

Milewski's central thesis: **composition is the essence of programming**, and composition is at the root of category theory (it is part of the definition of a category).

Historical progression of composability:
1. **Subroutines**: Made blocks of code composable
2. **Structured programming**: Made control flow composable
3. **Object-oriented programming**: Composes objects, but struggles with shared mutable state
4. **Functional programming**: Composes pure functions and algebraic data types; makes concurrency composable

Side effects don't scale — they are hidden from view and become unmanageable when composed. Category theory provides the mathematical framework for making effects explicit (via monads) and composition principled (via adjunctions and universal properties).

## Algebraic Data Types Categorically

Algebraic Data Types (ADTs) correspond directly to categorical products and coproducts:

```haskell
-- Product type (categorical product)
data Pair a b = Pair a b

-- Coproduct type (categorical coproduct)
data Either a b = Left a | Right b

-- Combined: ADT as polynomial functor
data List a = Nil | Cons a (List a)
-- Isomorphic to: 1 + a × X (fixed point)
```

The isomorphism between `List a` and the fixed point of *F(X)* = 1 + a × X is exactly the initial algebra isomorphism from Lambek's lemma.

**Recursion schemes**: Catamorphisms (folds), anamorphisms (unfolds), hylomorphisms, and paramorphisms are all derived from the universal properties of initial algebras and terminal coalgebras.

## Monadic Effects

Monads model computational effects categorically:

| Monad | Effect Modeled | Kleisli Arrow |
|-------|---------------|---------------|
| `Maybe` | Partiality / failure | `a -> Maybe b` |
| `[]` (List) | Nondeterminism | `a -> [b]` |
| `IO` | Side effects | `a -> IO b` |
| `State s` | Mutable state | `a -> (s -> (b, s))` |
| `Reader r` | Environment access | `a -> (r -> b)` |
| `Writer w` | Logging / accumulation | `a -> (b, w)` |

The Kleisli category **C_T** for a monad *T* has the same objects as **C** but morphisms *a* → *b* are morphisms *a* → *T(b)* in **C**. This lets programmers compose effectful computations using ordinary function composition within the Kleisli category.
