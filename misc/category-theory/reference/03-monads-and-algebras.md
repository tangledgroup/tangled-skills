# Monads and Algebras

## Contents
- Monads
- Comonads
- Monoidal Categories
- F-Algebras and Initial Algebras
- Lawvere Theories
- Ends and Coends
- Enriched Categories

## Monads

A **monad** on **C** is a triple (*T*, *η*, *μ*):
- Endofunctor *T* : **C** → **C**
- Unit *η* : Id ⇒ *T*
- Multiplication *μ* : *T*² ⇒ *T*

Laws: left unit (*μ* ∘ *η_T* = Id_T), right unit (*μ* ∘ *T_η* = Id_T), associativity (*μ* ∘ *T_μ* = *μ* ∘ *μ_T*).

| Perspective | Description |
|-------------|-------------|
| **Math** | Monoid in the category of endofunctors (under composition). Arises from any adjunction *F* ⊣ *G* as *T* = *GF* |
| **Code** | Computational context for sequencing effects. `return`/`>>=` in Haskell, `mreturn`/`bind` in pycategories |

**Kleisli category** **C_T**: same objects as **C**, morphisms *a* → *b* are *a* → *T(b)* in **C**. Composition: *g* ∘_K *f* = *μ* ∘ *T(g)* ∘ *f*. This is the free category for the monad — programmers compose effectful computations as ordinary functions in **C_T**.

**Eilenberg-Moore category** **C^T**: objects are algebras (*A*, *α*) where *α* : *T(A)* → *A*. Morphisms preserve algebra structure. This is the terminal adjunction for the monad.

**Every monad arises from at least one adjunction**, but not uniquely. The Kleisli and Eilenberg-Moore adjunctions are the initial and terminal among all adjunctions yielding a given monad.

**Monad laws in Haskell:**
```haskell
return a >>= f  ==  f a           -- left unit
m >>= return    ==  m             -- right unit
(m >>= f) >>= g == m >>= (\x -> f x >>= g)  -- associativity
```

**Common monads:**

| Monad | Effect | Kleisli Arrow |
|-------|--------|---------------|
| `Maybe` | Partiality / failure | `a -> Maybe b` |
| `[]` (List) | Nondeterminism | `a -> [b]` |
| `State s` | Mutable state | `a -> s -> (b, s)` |
| `Reader r` | Environment access | `a -> r -> b` |
| `Writer w` | Logging / accumulation | `a -> (b, w)` |
| `IO` | Side effects | `a -> IO b` |

## Comonads

A **comonad** on **C** is a triple (*W*, *ε*, *δ*):
- Endofunctor *W*
- Counit *ε* : *W* ⇒ Id
- Comultiplication *δ* : *W* ⇒ *W*²

Satisfying dual laws (copunit, coassociativity).

| Perspective | Description |
|-------------|-------------|
| **Math** | Comonad = comonoid in endofunctors. Dual of monad |
| **Code** | Context extraction. Reader comonad `r -> a` provides environment access. Store comonad models zippers and cellular automata |

## Monoidal Categories

A **monoidal category** (**C**, ⊗, *I*, *α*, *λ*, *ρ*):
- Bifunctor ⊗ : **C** × **C** → **C** (tensor product)
- Unit object *I*
- Associator *α*, left/right unitors *λ*, *ρ*

Satisfying pentagon and triangle coherence (Mac Lane: all reasonable diagrams commute).

**Symmetric monoidal**: additionally has braiding *γ* : *A ⊗ B* → *B ⊗ A* with *γ* ∘ *γ* = Id and hexagon axioms.

**Key insight:** "A monad is a monoid in the category of endofunctors" — monoid multiplication is *μ*, unit is *η*, tensor is functor composition.

**Examples:** **Set** with × and {∗}, **Vect** with ⊗ and *k*, endofunctors under composition.

## F-Algebras and Initial Algebras

An **F-algebra** for endofunctor *F* is a pair (*A*, *α*) where *α* : *F(A)* → *A*. Morphisms preserve structure: *h* ∘ *α* = *β* ∘ *F(h)*.

The **initial algebra** is initial in the category of F-algebras. By **Lambek's lemma**, its structure map *α* : *F(A)* → *A* is an isomorphism.

| Perspective | Description |
|-------------|-------------|
| **Math** | Fixed point of an endofunctor, characterized universally |
| **Code** | Recursive data types. `data Nat = Zero \| Succ Nat` is initial algebra for *F(X)* = 1 + X. `List a` for *F(X)* = 1 + a × X |

**Catamorphisms** (folds): unique morphism from initial algebra to any F-algebra. **Anamorphisms** (unfolds): from terminal coalgebra. **Hylomorphisms**: anamorphism followed by catamorphism.

## Lawvere Theories

A **Lawvere theory** is a category **L** with finite products, objects *n* for each *n* ∈ N (the n-fold product of a generic object), all objects being products of the generic object.

Operations are morphisms in **L**. A **model** in **C** (with finite products) is a product-preserving functor **L** → **C**.

**Example:** Lawvere theory of groups — objects *n* are free groups on n generators, morphisms are group operations. Models in **Set** are exactly groups.

Lawvere theories connect to adjunctions: the free/forgetful adjunction for any algebraic theory gives a Lawvere theory.

## Ends and Coends

An **end** ∫_c *F(c, c)* is a universal wedge — generalized limit over the diagonal of *F* : **C**op × **C** → **Set**. A **coend** ∫^c *F(c, c)* is the dual colimit.

Yoneda as coend: *F(X)* ≅ ∫^c Hom(*c*, *X*) × *F(c)* for functors that are left Kan extensions along Yoneda.

## Enriched Categories

An **enriched category** replaces hom-sets with objects from a monoidal category **V**. Composition is a morphism in **V**:

⊗ : Hom(*b*, *c*) ⊗ Hom(*a*, *b*) → Hom(*a*, *c*)

**Examples:** Metric spaces enriched over ([0, ∞], ≥, +, 0), Vect-enriched categories (hom-objects are vector spaces), Cat-enriched categories = 2-categories.
