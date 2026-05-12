# Higher Category Theory

## Contents
- Motivation and Overview
- Strict n-Categories
- 2-Categories
- Bicategories (Weak 2-Categories)
- Monoidal Categories as One-Object Bicategories
- Quasi-Categories
- Infinity-Groupoids and Homotopy Theory
- Topoi

## Motivation and Overview

Ordinary category theory has objects and 1-morphisms between them. **Higher category theory** adds morphisms between morphisms (2-morphisms), morphisms between those (3-morphisms), and so on. This allows studying the structure behind equalities themselves — not just that two compositions are equal, but *how* they are equal via an explicit isomorphism.

The primary motivation comes from **algebraic topology** and **homotopy theory**, where spaces have invariants at every dimension (fundamental group, higher homotopy groups). Higher categories capture these layered structures naturally.

## Strict n-Categories

Defined by induction:
- A 0-category is a set
- An (*n*+1)-category is a category enriched over *n*-**Cat**

So a 1-category is an ordinary category, a 2-category has objects, 1-morphisms, and 2-morphisms with strict associativity and identity laws.

The category *n*-**Cat** of small *n*-categories is itself an (*n*+1)-category.

Strict higher categories are too rigid for many applications in homotopy theory, where composition should be associative only "up to coherent isomorphism."

## 2-Categories

A **2-category** has:
- **Objects** (0-cells)
- **1-morphisms** between objects
- **2-morphisms** between 1-morphisms

Two compositions:
- **Vertical**: compose 2-morphisms between the same 1-morphisms (like composing natural transformations)
- **Horizontal**: compose 2-morphisms along 1-morphism composition

These satisfy the **exchange law** (interchange law): vertical and horizontal compositions commute in a specific way.

**Key example — Cat**: The 2-category of small categories, functors, and natural transformations. Natural transformations are the 2-morphisms between functors.

**2-functor**: Preserves objects, 1-morphisms, 2-morphisms, and both compositions strictly.

## Bicategories (Weak 2-Categories)

A **bicategory** relaxes strict 2-categories: composition of 1-morphisms is associative only up to a coherent isomorphism (the **associator**), and identities hold only up to isomorphism (the **unitors**).

These isomorphisms themselves satisfy coherence conditions (modified pentagon and triangle diagrams).

**Key insight**: A bicategory with one object is exactly a **monoidal category**. The associator of the bicategory is the associator of the monoidal structure. Thus bicategories are "monoidal categories with many objects."

**Pseudofunctor**: The weak analogue of a 2-functor, preserving structure up to coherent isomorphism rather than strictly.

## Monoidal Categories as One-Object Bicategories

A **monoidal category** (**C**, ⊗, *I*, *α*, *λ*, *ρ*) corresponds to a bicategory with a single object \*:
- 1-morphisms = objects of **C**
- Composition of 1-morphisms = tensor product ⊗
- 2-morphisms = morphisms of **C**
- Associator = *α* : (*A* ⊗ *B*) ⊗ *C* → *A* ⊗ (*B* ⊗ *C*)
- Unitors = *λ*, *ρ*

A **symmetric monoidal category** adds a braiding that satisfies the symmetry condition. This corresponds to a symmetric bicategory with one object.

## Quasi-Categories

A **quasi-category** (weak Kan complex) is a simplicial set satisfying the inner horn filling condition: every inner horn Λ^n_i → *X* (0 < i < n) can be extended to an n-simplex Δ^n → *X*.

Quasi-categories model **(infinity, 1)-categories**: categories with morphisms at all dimensions, but where all *k*-morphisms for *k* ≥ 2 are invertible.

**André Joyal** showed quasi-categories form a good foundation for higher category theory via the Joyal model structure on simplicial sets. **Jacob Lurie** systematized this in his work on infinity-categories and higher topos theory.

Quasi-categories excel at:
- Defining limits and colimits in higher settings
- Homotopy-coherent diagrams
- The theory of infinity-operads

## Infinity-Groupoids and Homotopy Theory

An **infinity-groupoid** is an *n*-category where all morphisms at all levels are invertible. By the **homotopy hypothesis**, infinity-groupoids model homotopy types of topological spaces.

The fundamental infinity-groupoid Π_∞(*X*) of a space *X* captures:
- Points (0-morphisms)
- Paths between points (1-morphisms)
- Homotopies between paths (2-morphisms)
- Higher homotopies (k-morphisms)

This connects category theory directly to algebraic topology. The **Eilenberg-MacLane spaces** K(*G*, *n*) are classified by their homotopy groups, which higher categories can distinguish even when lower invariants agree.

## Topoi

A **topos** (plural: topoi) is a category behaving like the category of sheaves on a topological space. Key properties:
- Finite limits and colimits exist
- Exponentials exist (cartesian closed)
- A subobject classifier Ω exists

Topoi serve as alternative foundations for mathematics, replacing set theory. **Elementary topos theory** provides internal logic (intuitionistic higher-order logic), making topoi models of constructive mathematics.

**Grothendieck topoi** (sheaf categories) have geometric origins and lead to ideas like pointless topology. The **classifying topos** for a theory encodes all its models.
