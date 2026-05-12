---
name: category-theory
description: Mathematical framework for abstract structures and their relationships via categories, functors, natural transformations, limits, adjunctions, and monads. Use when reasoning about compositional program structure, understanding Haskell typeclasses (Functor/Monad/Applicative), designing abstractions in functional programming, or connecting mathematical concepts to type theory and programming language semantics.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - category-theory
  - mathematics
  - functional-programming
  - type-theory
  - monads
  - functors
category: mathematics
external_references:
  - https://en.wikipedia.org/wiki/Category_theory
  - https://en.wikipedia.org/wiki/Higher_category_theory
  - https://github.com/prathyvsh/category-theory-resources
  - https://github.com/hmemcpy/milewski-ctfp-pdf
  - https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/
  - https://pycategories.readthedocs.io/en/latest/index.html
  - https://finsberg.github.io/category-theory-python/README.html
---

# Category Theory

## Overview

Category theory is a general theory of mathematical structures and their relationships. Introduced by Samuel Eilenberg and Saunders Mac Lane in the mid-20th century for algebraic topology, it now underpins functional programming, type theory, semantics, and applied mathematics across physics, systems science, and music theory.

A **category** consists of objects and morphisms (arrows) between them. Morphisms compose associatively and every object has an identity morphism. A **functor** maps one category to another while preserving structure. A **natural transformation** relates two functors, providing a uniform way to transform their outputs across all objects.

Category theory treats structures abstractly — objects are atomic, defined only by how they relate to other objects via morphisms. This "universal property" approach lets the same patterns (products, coproducts, limits) appear uniformly across sets, groups, topological spaces, and programming types.

## When to Use

- Understanding or designing Haskell typeclasses (Functor, Monad, Applicative)
- Reasoning about compositional program structure and algebraic data types
- Connecting mathematical structures (monoids, groups, adjunctions) to code
- Studying type theory semantics via cartesian closed categories
- Working with monadic effects, free constructions, or F-algebras for recursive data
- Exploring higher-category concepts (2-categories, infinity-categories) in homotopy type theory

## Core Concepts

### Categories

A category **C** has:
- A class of **objects**
- For each pair of objects *a*, *b*, a class **Hom(a, b)** of **morphisms**
- **Composition**: for *f* : *a* → *b* and *g* : *b* → *c*, the composite *g* ∘ *f* : *a* → *c*
- **Identity**: for each object *x*, an identity morphism 1*x* : *x* → *x*

Axioms: composition is associative, and identities are left/right units.

**Prototypical example — Set**: objects are sets, morphisms are functions. Every set has an identity function, and function composition is associative.

**Other examples:**
- **Grp**: groups and group homomorphisms
- **Top**: topological spaces and continuous maps
- A **monoid** as a single-object category (morphisms = monoid elements)
- A **preorder** as a category with at most one morphism between any two objects

### Functors

A **covariant functor** *F* : **C** → **D** maps:
- Each object *x* in **C** to an object *F(x)* in **D**
- Each morphism *f* : *x* → *y* to *F(f)* : *F(x)* → *F(y)*

Preserving identities and composition: *F(1*x*) = 1*F(x)*, *F(g ∘ f) = F(g) ∘ F(f)*.

A **contravariant functor** reverses arrow direction: *f* : *x* → *y* maps to *F(f)* : *F(y)* → *F(x)*. Equivalently, a covariant functor from the opposite category **C**op.

### Natural Transformations

Given functors *F*, *G* : **C** → **D**, a **natural transformation** *η* : *F* ⇒ *G* assigns to each object *X* in **C** a morphism *η*X* : *F(X)* → *G(X)* in **D** such that for every *f* : *X* → *Y*:

```
η_Y ∘ F(f) = G(f) ∘ η_X
```

This "naturality square" commutes, meaning the transformation works uniformly regardless of which morphism you apply first. When each *η*X* is an isomorphism, *F* and *G* are **naturally isomorphic**.

## Usage Examples

### Haskell: Functor Typeclass

```haskell
class Functor f where
    fmap :: (a -> b) -> f a -> f b
```

`fmap` is the action of a functor on morphisms. The type constructor `f` forms an endofunctor on **Hask** (the category of Haskell types and functions).

### Haskell: Monad Typeclass

```haskell
class Monad m where
    return :: a -> m a
    (>>=)  :: m a -> (a -> m b) -> m b
```

A monad is a monoid in the category of endofunctors — `return` is the unit, `(>>=)` encodes multiplication via the Kleisli composition.

### Python: Using pycategories

```python
from categories import apply
from categories.maybe import Just, Nothing

f = Just(lambda x: x ** 2)
x = Just(17)
print(apply(f, x))       # Just(289)
print(apply(f, Nothing()))  # Nothing
```

## Advanced Topics

**Basic Concepts**: Categories, morphisms, functors, natural transformations in detail → [Basic Concepts](reference/01-basic-concepts.md)

**Limits and Colimits**: Universal properties, products, coproducts, adjunctions, Yoneda lemma → [Limits and Colimits](reference/02-limits-and-colimits.md)

**Monads and Beyond**: Monads, comonads, monoidal categories, F-algebras, Lawvere theories → [Monads and Beyond](reference/03-monads-and-allegories.md)

**Higher Category Theory**: 2-categories, n-categories, bicategories, quasi-categories, infinity-categories → [Higher Category Theory](reference/04-higher-category-theory.md)

**Programming Applications**: Haskell typeclasses, Python libraries, CTFP curriculum, practical connections → [Programming Applications](reference/05-programming-applications.md)
