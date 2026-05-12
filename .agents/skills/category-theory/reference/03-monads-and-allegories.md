# Monads and Beyond

## Contents
- Monads
- Comonads
- Monoidal Categories
- F-Algebras and Initial Algebras
- Lawvere Theories
- Ends and Coends
- Enriched Categories

## Monads

A **monad** on a category **C** is a triple (*T*, *η*, *μ*) consisting of:
- An endofunctor *T* : **C** → **C**
- A natural transformation *η* : Id ⇒ *T* (the **unit**)
- A natural transformation *μ* : *T*² ⇒ *T* (the **multiplication**)

Satisfying:
1. **Left unit**: *μ* ∘ *η_T* = Id_T
2. **Right unit**: *μ* ∘ *T_η* = Id_T
3. **Associativity**: *μ* ∘ *T_μ* = *μ* ∘ *μ_T*

**Equivalently**, a monad arises from an adjunction *F* ⊣ *G*: the composite *T* = *G* ∘ *F* with *η* as the unit and *μ* = *GεF* as the multiplication. Not every monad comes from a unique adjunction, but every monad arises from at least one.

**Kleisli category** **C_T**: Same objects as **C**. Morphisms *a* → *b* are morphisms *a* → *T(b)* in **C**. Composition: *g* ∘_K *f* = *μ* ∘ *T(g)* ∘ *f*. The Kleisli construction is the free category for the monad.

**Eilenberg-Moore category** **C^T**: Objects are pairs (*A*, *α*) where *α* : *T(A)* → *A* (an **algebra for T**). Morphisms preserve the algebra structure. This is the "category of coalgebras" and is the terminal adjunction for the monad.

**Programming examples (Haskell):**
- **Maybe monad**: *T(a)* = `Maybe a`, handles optional/computation-that-may-fail
- **List monad**: *T(a)* = `[a]`, handles nondeterminism
- **State monad**: *T(a)* = `s -> (a, s)`, threads state through computations
- **IO monad**: models side effects as values in a computational context

**Monad laws in Haskell:**
```haskell
return a >>= f  ==  f a           -- left unit
m >>= return    ==  m             -- right unit
(m >>= f) >>= g == m >>= (\x -> f x >>= g)  -- associativity
```

## Comonads

A **comonad** on **C** is a triple (*W*, *ε*, *δ*):
- An endofunctor *W* : **C** → **C**
- Counit *ε* : *W* ⇒ Id
- Comultiplication *δ* : *W* ⇒ *W*²

Satisfying dual laws to monads (copunit, coassociativity).

**Programming example**: The **reader comonad** `r -> a` provides access to an environment. The **store comonad** models cellular automata and zippers.

## Monoidal Categories

A **monoidal category** is a category **C** equipped with:
- A bifunctor ⊗ : **C** × **C** → **C** (the **tensor product**)
- An object *I* (the **unit object**)
- Natural isomorphisms: associator *α*, left unitor *λ*, right unitor *ρ*

Satisfying the pentagon and triangle coherence conditions (Mac Lane's coherence theorem: all reasonable diagrams commute).

**Symmetric monoidal category**: Additionally has a braiding *γ* : *A ⊗ B* → *B ⊗ A* satisfying symmetry (*γ* ∘ *γ* = Id) and hexagon axioms.

**Key insight**: "A monad is a monoid in the category of endofunctors" (Mac Lane). The monoid multiplication is *μ*, the unit is *η*, and the tensor product is functor composition.

**Examples:**
- **Set** with cartesian product × and singleton {∗}
- **Vect** with tensor product ⊗ and base field *k*
- The category of endofunctors on **C** with functor composition

## F-Algebras and Initial Algebras

An **F-algebra** for an endofunctor *F* : **C** → **C** is a pair (*A*, *α*) where *α* : *F(A)* → *A*. A morphism of F-algebras (*A*, *α*) → (*B*, *β*) is a morphism *h* : *A* → *B* such that *h* ∘ *α* = *β* ∘ *F(h)*.

The **initial algebra** (if it exists) is an initial object in the category of F-algebras. By Lambek's lemma, the structure map of the initial algebra *α* : *F(A)* → *A* is an isomorphism.

**Programming connection**: Recursive data types are initial algebras.
- `data Nat = Zero | Succ Nat` is the initial algebra for *F(X)* = 1 + X
- `data List a = Nil | Cons a (List a)` is the initial algebra for *F(X)* = 1 + a × X

**Catamorphisms** (folds) are the unique morphisms from the initial algebra to any other F-algebra. **Anamorphisms** (unfolds) go from the terminal coalgebra.

## Lawvere Theories

A **Lawvere theory** is a category **L** with:
- Finite products
- Objects *n* for each natural number *n* (representing the n-fold product of a generic object)
- All objects are products of the generic object

Operations of an algebraic theory are morphisms in **L**. A **model** of the theory in a category **C** with finite products is a product-preserving functor **L** → **C**.

**Example**: The Lawvere theory of groups has objects *n* (free groups on n generators) and morphisms are group operations. Models in **Set** are exactly groups.

Lawvere theories provide a categorical foundation for universal algebra, connecting directly to adjunctions (the free/forgetful adjunction for any algebraic theory).

## Ends and Coends

An **end** of a functor *F* : **C**op × **C** → **Set** is a universal wedge — a generalized limit over the diagonal. Notation: ∫_c *F(c, c)*.

A **coend** is the dual colimit: ∫^c *F(c, c)*.

The Yoneda lemma can be expressed as a coend formula: any functor *F* : **C** → **Set** that is a left Kan extension along the Yoneda embedding satisfies:

*F(X)* ≅ ∫^c Hom(*c*, *X*) × *F(c)*

## Enriched Categories

An **enriched category** replaces hom-sets with objects from a monoidal category **V**. Instead of Hom(*a*, *b*) being a set, it is an object of **V**, and composition is a morphism in **V**:

⊗ : Hom(*b*, *c*) ⊗ Hom(*a*, *b*) → Hom(*a*, *c*)

**Examples:**
- **Metric spaces** as categories enriched over ([0, ∞], ≥, +, 0)
- **Vect-enriched categories**: hom-objects are vector spaces (e.g., the category of chain complexes)
- **Cat-enriched categories** = 2-categories
