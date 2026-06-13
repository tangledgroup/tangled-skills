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

Ordinary category theory has objects and 1-morphisms. **Higher category theory** adds morphisms between morphisms (2-morphisms), then between those (3-morphisms), ad infinitum. This studies the structure behind equalities — not just that compositions are equal, but *how* they are equal via explicit isomorphism.

Primary motivation: **algebraic topology** and **homotopy theory**, where spaces have invariants at every dimension (fundamental group, higher homotopy groups). Higher categories capture these layered structures naturally.

## Strict n-Categories

Defined by induction:
- A 0-category is a set
- An (*n*+1)-category is a category enriched over *n*-**Cat**

A 2-category has objects, 1-morphisms, and 2-morphisms with strict associativity and identity laws. The category *n*-**Cat** of small *n*-categories is itself an (*n*+1)-category.

Strict higher categories are too rigid for homotopy theory, where composition should be associative only "up to coherent isomorphism."

## 2-Categories

A **2-category** has:
- **Objects** (0-cells)
- **1-morphisms** between objects
- **2-morphisms** between 1-morphisms

Two compositions:
- **Vertical**: compose 2-morphisms between same 1-morphisms (like composing natural transformations)
- **Horizontal**: compose 2-morphisms along 1-morphism composition

These satisfy the **exchange law** (interchange law).

**Key example — Cat**: 2-category of small categories, functors, and natural transformations. Natural transformations are 2-morphisms between functors.

**2-functor**: preserves objects, 1-morphisms, 2-morphisms, and both compositions strictly.

## Bicategories (Weak 2-Categories)

A **bicategory** relaxes strict 2-categories: composition of 1-morphisms is associative only up to a coherent isomorphism (the **associator**), identities hold only up to isomorphism (**unitors**). These satisfy coherence conditions (modified pentagon and triangle diagrams).

A bicategory with one object is exactly a **monoidal category**. The bicategory associator is the monoidal associator. Thus bicategories are "monoidal categories with many objects."

**Pseudofunctor**: weak analogue of 2-functor, preserving structure up to coherent isomorphism.

## Monoidal Categories as One-Object Bicategories

Monoidal category (**C**, ⊗, *I*, *α*, *λ*, *ρ*) ↔ bicategory with single object \*:
- 1-morphisms = objects of **C**
- Composition of 1-morphisms = tensor product ⊗
- 2-morphisms = morphisms of **C**
- Associator = *α* : (*A* ⊗ *B*) ⊗ *C* → *A* ⊗ (*B* ⊗ *C*)

**Symmetric monoidal category** adds braiding satisfying symmetry. Corresponds to symmetric bicategory with one object.

## Quasi-Categories

A **quasi-category** (weak Kan complex) is a simplicial set satisfying inner horn filling: every inner horn Λ^n_i → *X* (0 < i < n) extends to Δ^n → *X*.

Quasi-categories model **(infinity, 1)-categories**: morphisms at all dimensions, but all *k*-morphisms for *k* ≥ 2 are invertible.

**Joyal** showed quasi-categories form a good foundation via the Joyal model structure. **Lurie** systematized this in his work on infinity-categories and higher topos theory.

Quasi-categories excel at: limits/colimits in higher settings, homotopy-coherent diagrams, infinity-operads.

## Infinity-Groupoids and Homotopy Theory

An **infinity-groupoid** is an *n*-category where all morphisms at all levels are invertible. By the **homotopy hypothesis**, infinity-groupoids model homotopy types of topological spaces.

The fundamental infinity-groupoid Π_∞(*X*) captures: points (0-morphisms), paths (1-morphisms), homotopies between paths (2-morphisms), higher homotopies (*k*-morphisms).

**Eilenberg-MacLane spaces** K(*G*, *n*) are classified by homotopy groups, which higher categories can distinguish even when lower invariants agree.

## Topoi

A **topos** is a category behaving like sheaves on a topological space:
- Finite limits and colimits exist
- Exponentials exist (cartesian closed)
- Subobject classifier Ω exists

Topoi serve as alternative foundations for mathematics, replacing set theory. **Elementary topos theory** provides internal logic (intuitionistic higher-order logic), making topoi models of constructive mathematics.

**Grothendieck topoi** (sheaf categories) have geometric origins leading to pointless topology. The **classifying topos** for a theory encodes all its models.
