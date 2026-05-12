# Basic Concepts

## Contents
- Categories and Objects
- Morphisms and Their Types
- Commutative Diagrams
- Functors (Covariant and Contravariant)
- Natural Transformations
- Opposite Categories and Subcategories

## Categories and Objects

A **category** **C** consists of:
1. A class **Ob(C)** of **objects**
2. For each pair of objects *a*, *b*, a class **Hom(a, b)** (the hom-class) of **morphisms** (also called arrows or maps)
3. A **composition** operation: for *f* ∈ Hom(*a*, *b*) and *g* ∈ Hom(*b*, *c*), the composite *g* ∘ *f* ∈ Hom(*a*, *c*)

**Axioms:**
- **Associativity**: *h* ∘ (*g* ∘ *f*) = (*h* ∘ *g*) ∘ *f*
- **Identity**: For each object *x*, there exists 1*x* : *x* → *x* such that 1*b* ∘ *f* = *f* and *f* ∘ 1*a* = *f* for all *f* : *a* → *b*

The identity morphism for each object is unique.

**Notation:** *f* : *a* → *b* means "*f* is a morphism from source *a* to target *b*". Computer scientists often write *f* ; *g* for *g* ∘ *f* (left-to-right composition order).

**Examples of categories:**
- **Set**: sets and functions
- **Grp**: groups and group homomorphisms
- **Top**: topological spaces and continuous maps
- **Vect**: vector spaces and linear maps
- A **monoid** (*M*, ·, *e*) as a one-object category: single object *, morphisms are elements of *M*, composition is ·
- A **preorder** (*P*, ≤) as a category: objects are elements of *P*, at most one morphism *a* → *b* (exists iff *a* ≤ *b*)
- A **poset** is a preorder where *a* ≤ *b* and *b* ≤ *a* implies *a* = *b*

## Morphisms and Their Types

For *f* : *a* → *b*:

- **Monomorphism** (monic): left-cancellable — *f* ∘ *g*1 = *f* ∘ *g*2 implies *g*1 = *g*2. Generalizes injective functions.
- **Epimorphism** (epic): right-cancellable — *g*1 ∘ *f* = *g*2 ∘ *f* implies *g*1 = *g*2. Generalizes surjective functions.
- **Isomorphism**: there exists *g* : *b* → *a* such that *f* ∘ *g* = 1*b* and *g* ∘ *f* = 1*a*. The inverse *g* is unique. Generalizes bijective functions.
- **Bimorphism**: both monic and epic. Not necessarily an isomorphism in all categories (e.g., the inclusion *N* → *Z* in the category of monoids is bimorphic but not invertible).
- **Endomorphism**: *a* = *b*. The class end(*a*) of all endomorphisms of *a* forms a monoid under composition.
- **Automorphism**: an endomorphism that is also an isomorphism. aut(*a*) forms a group.
- **Section**: has a left inverse — exists *g* with *g* ∘ *f* = 1*a*. Every section is monic.
- **Retraction**: has a right inverse — exists *g* with *f* ∘ *g* = 1*b*. Every retraction is epic.

Three equivalent conditions for *f* being an isomorphism:
1. *f* is monic and a retraction
2. *f* is epic and a section
3. *f* has a two-sided inverse

## Commutative Diagrams

Morphisms are depicted as arrows between objects (dots/corners). A diagram **commutes** when all paths between two objects yield the same composite morphism.

**Triangle commutativity**: If *f* : *a* → *b*, *g* : *b* → *c*, and *h* : *a* → *c* satisfy *h* = *g* ∘ *f*, the triangle commutes.

**Square commutativity** (naturality condition): For natural transformation *η* between functors *F* and *G*:
```
  F(X) --F(f)--> F(Y)
   |               |
 η_X             η_Y
   |               |
  G(X) --G(f)--> G(Y)
```
Commutativity means: *η*Y ∘ *F(f)* = *G(f)* ∘ *η*X.

## Functors (Covariant and Contravariant)

**Covariant functor** *F* : **C** → **D**:
- Maps each object *x* to *F(x)*
- Maps each morphism *f* : *x* → *y* to *F(f)* : *F(x)* → *F(y)*
- Preserves identities: *F(1*x*) = 1*F(x)*
- Preserves composition: *F(g ∘ f)* = *F(g)* ∘ *F(f)*

**Contravariant functor** *F* : **C** → **D**:
- Same as covariant, but reverses arrows: *f* : *x* → *y* maps to *F(f)* : *F(y)* → *F(x)*
- Equivalently, a covariant functor **C**op → **D**

**Special kinds of functors:**
- **Full**: for every pair *x*, *y*, the map Hom(*x*, *y*) → Hom(*F(x)*, *F(y)*) is surjective
- **Faithful**: the above map is injective
- **Fully faithful**: both full and faithful (bijection on hom-classes)
- **Essentially surjective**: every object in **D** is isomorphic to *F(x)* for some *x*
- **Forgetful functor**: strips structure (e.g., Grp → Set forgets group operations, keeps underlying set)
- **Free functor**: left adjoint to a forgetful functor (e.g., free group on a set)

## Natural Transformations

Given *F*, *G* : **C** → **D**, a natural transformation *η* : *F* ⇒ *G* assigns to each object *X* a morphism *η*X* : *F(X)* → *G(X)* such that the naturality square commutes for every *f* : *X* → *Y*.

**Vertical composition**: If *η* : *F* ⇒ *G* and *θ* : *G* ⇒ *H*, then *θ* ∘ *η* : *F* ⇒ *H* is defined componentwise: (*θ* ∘ *η*)*X* = *θ*X ∘ *η*X.

**Horizontal composition**: If *η* : *F* ⇒ *G* (functors **C** → **D**) and *ξ* : *H* ⇒ *K* (functors **D** → **E**), then *ξ* ∘ *h* *η* : *H* ∘ *F* ⇒ *K* ∘ *G*.

**Natural isomorphism**: A natural transformation where each component *η*X* is an isomorphism. Two naturally isomorphic functors are "the same" up to canonical identification.

## Opposite Categories and Subcategories

**Opposite category** **C**op: same objects as **C**, but all arrows reversed. Hom_Cop(*a*, *b*) = Hom_C(*b*, *a*). Composition in **C**op reverses order: *g* ∘op *f* = *f* ∘ *g*.

**Duality principle**: Every categorical statement has a dual obtained by reversing all arrows and swapping domain/codomain. If a theorem holds in **C**, its dual holds in **C**op. This yields pairs like:
- Product ↔ Coproduct
- Limit ↔ Colimit
- Monomorphism ↔ Epimorphism
- Initial object ↔ Terminal object

**Subcategory**: A category **D** whose objects and morphisms form subclasses of those in **C**, with the same composition and identities. **D** is a **full subcategory** if Hom_D(*a*, *b*) = Hom_C(*a*, *b*) for all *a*, *b* in **D**.
