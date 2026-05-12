# Categories and Morphisms

## Contents
- Categories and Objects
- Morphisms and Their Types
- Commutative Diagrams
- Semigroups and Monoids
- Functors (Covariant and Contravariant)
- Natural Transformations
- Opposite Categories and Subcategories

## Categories and Objects

A **category** **C** consists of:
1. A class **Ob(C)** of **objects**
2. For each pair *a*, *b*, a class **Hom(a, b)** of **morphisms** (arrows)
3. **Composition**: for *f* : *a* → *b* and *g* : *b* → *c*, the composite *g* ∘ *f* : *a* → *c*

**Axioms:** composition is associative; every object has an identity 1*x* : *x* → *x* that is a left and right unit.

**Notation:** CS often writes *f* ; *g* for *g* ∘ *f* (left-to-right order).

| Perspective | Description |
|-------------|-------------|
| **Math** | Abstract objects + arrows with composition axioms |
| **Code** | **Hask**: types as objects, functions as morphisms. Composition = function composition |

**Examples:** **Set** (sets/functions), **Grp** (groups/homomorphisms), **Top** (spaces/continuous maps), **Vect** (vector spaces/linear maps). A monoid is a single-object category. A preorder (*P*, ≤) is a category with at most one morphism per pair.

## Morphisms and Their Types

For *f* : *a* → *b*:

- **Monomorphism** (monic): left-cancellable — *f* ∘ *g*1 = *f* ∘ *g*2 ⟹ *g*1 = *g*2. Generalizes injective.
- **Epimorphism** (epic): right-cancellable. Generalizes surjective.
- **Isomorphism**: has two-sided inverse *g* with *f* ∘ *g* = 1*b*, *g* ∘ *f* = 1*a*. Generalizes bijective.
- **Bimorphism**: both monic and epic. Not always an isomorphism (e.g., N → Z in **Mon**).
- **Endomorphism**: *a* = *b*. end(*a*) forms a monoid.
- **Automorphism**: endomorphism + isomorphism. aut(*a*) forms a group.
- **Section**: has left inverse (always monic). **Retraction**: has right inverse (always epic).

Three equivalent conditions for isomorphism: (1) monic + retraction, (2) epic + section, (3) two-sided inverse exists.

## Commutative Diagrams

Morphisms are arrows between objects. A diagram **commutes** when all paths between two objects yield the same composite.

**Naturality square** (for natural transformation *η* : *F* ⇒ *G*):
```
  F(X) --F(f)--> F(Y)
   |               |
 η_X             η_Y
   |               |
  G(X) --G(f)--> G(Y)
```
Commutativity: *η*Y ∘ *F(f)* = *G(f)* ∘ *η*X.

## Semigroups and Monoids

A **semigroup** is a set *S* with an associative binary operation: (*a* · *b*) · *c* = *a* · (*b* · *c*).

A **monoid** adds an identity element *e*: *e* · *a* = *a* · *e* = *a* for all *a*.

| Perspective | Description |
|-------------|-------------|
| **Math** | Monoid = (M, ·, e) with associativity and identity axioms |
| **Code** | `mappend(a, b)` is associative; `mempty` is identity. Strings under `+`, lists under concatenation, ints under `+` (identity 0) or `*` (identity 1) |

**Categorical view:** A monoid is exactly a category with one object. The morphisms are the monoid elements; composition is the binary operation; the identity morphism is *e*.

**Commutative monoid:** additionally *a* · *b* = *b* · *a*. Examples: (Z, +, 0), (bool, ∧, True), (bool, ∨, False).

**Monoid homomorphism** *h* : (*M*, ·, *e*) → (*N*, *,*, *e'*): preserves operation and identity — *h(a · b)* = *h(a)* * *h(b)*, *h(e)* = *e'*.

## Functors (Covariant and Contravariant)

**Covariant functor** *F* : **C** → **D** maps objects to objects and morphisms to morphisms, preserving identities and composition.

| Perspective | Description |
|-------------|-------------|
| **Math** | Structure-preserving map between categories: *F(g ∘ f)* = *F(g)* ∘ *F(f)*, *F(1*x*)* = 1*F(x)* |
| **Code** | Type constructor `F` with `fmap`. Endofunctor on **Hask**: `fmap :: (a->b) -> F a -> F b` |

**Contravariant functor** reverses arrows: *f* : *x* → *y* maps to *F(f)* : *F(y)* → *F(x)*. Equivalently, covariant **C**op → **D**.

**Special functors:**
- **Full**: surjective on hom-classes. **Faithful**: injective. **Fully faithful**: bijective.
- **Forgetful**: strips structure (Grp → Set). **Free**: left adjoint to forgetful (Set → Grp).
- **Essentially surjective**: every object in target is isomorphic to an image.

## Natural Transformations

Given *F*, *G* : **C** → **D**, a natural transformation *η* : *F* ⇒ *G* assigns *η*X* : *F(X)* → *G(X)* per object, with naturality squares commuting for every morphism.

| Perspective | Description |
|-------------|-------------|
| **Math** | Uniform family of morphisms between functor outputs, natural in the object |
| **Code** | Function converting one container to another uniformly: `toList :: Maybe a -> [a]`, `fmap id :: F a -> F a` (identity natural transformation) |

**Vertical composition**: *θ* ∘ *η* componentwise. **Horizontal composition**: *ξ* ∘h *η* across functor composition.

**Natural isomorphism**: each component is an isomorphism. Naturally isomorphic functors are "the same" up to canonical identification.

## Opposite Categories and Subcategories

**Opposite category** **C**op: same objects, all arrows reversed. Hom_Cop(*a*, *b*) = Hom_C(*b*, *a*).

**Duality principle:** Reverse all arrows in any categorical statement to get its dual. If a theorem holds in **C**, its dual holds in **C**op. Yields pairs: product ↔ coproduct, limit ↔ colimit, mono ↔ epi, initial ↔ terminal.

**Subcategory** **D** of **C**: objects and morphisms form subclasses, same composition/identities. **Full subcategory**: Hom_D(*a*, *b*) = Hom_C(*a*, *b*) for all *a*, *b* in **D**.
