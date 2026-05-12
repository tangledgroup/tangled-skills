# CTFP Curriculum

## Contents
- Central Thesis: Composition Is the Essence of Programming
- Historical Progression of Composability
- Why Now: The Multi-Core and Complexity Motivations
- Haskell as a Sketching Language
- The Physicist's Approach to Math
- Full Chapter Outline (31 Chapters)
- How to Use CTFP

## Central Thesis: Composition Is the Essence of Programming

Bartosz Milewski's "Category Theory for Programmers" (CTFP) argues that **composition is at the root of both category theory and programming**. Composition is part of the definition of a category (morphisms compose associatively with identities). Every major advance in software engineering has been about making something composable.

Side effects break composition — they are hidden from view and become unmanageable when composed. Category theory provides the mathematical framework for making effects explicit (via monads) and composition principled (via adjunctions and universal properties).

## Historical Progression of Composability

| Era | What Became Composable | Limitation |
|-----|----------------------|------------|
| Subroutines | Blocks of code | Global state coupling |
| Structured programming | Control flow | Still imperative |
| Object-oriented programming | Objects | Shared mutable state breaks composition; locks don't compose |
| Functional programming | Pure functions, ADTs, concurrency | Requires discipline; learning curve |

OOP's data hiding combined with sharing and mutation becomes a recipe for data races. Locks don't compose, and lock hiding makes deadlocks more likely. Even without concurrency, growing software complexity tests the limits of imperative scalability — side effects are getting out of hand.

## Why Now: The Multi-Core and Complexity Motivations

CTFP identifies a "phase transition" in programming:
- **Multicore revolution**: OOP buys nothing for concurrency/parallelism and encourages dangerous design
- **Functional features invading imperative languages**: lambdas in Java, rapid C++ evolution
- **Growing complexity**: side effects becoming unmanageable at scale

The metaphor: "We are now in the position of a frog that must decide if it should continue swimming in increasingly hot water, or start looking for some alternatives."

## Haskell as a Sketching Language

CTFP uses Haskell not as the implementation language but as a **language for sketching and documenting ideas** to be implemented in other languages (C++, Python). Its terse syntax and powerful type system help understand templates, data structures, and algorithms.

You don't need to become a Haskell programmer — you need it as a notation for categorical concepts, then implement in your primary language.

## The Physicist's Approach to Math

Milewski uses informal reasoning with solid mathematical theory underneath — the physicist's approach. Mathematicians require rigorous proofs; physicists make advances using hand-waving arguments that later get formalized (e.g., Dirac delta → distribution theory). The goal: accessibility without sacrificing correctness.

Reference: Saunders Mac Lane's "Category Theory for the Working Mathematician" provides the rigorous foundation behind the informal arguments.

## Full Chapter Outline (31 Chapters)

### Part One — Foundations (10 chapters)
1. **Category: The Essence of Composition** — Categories as the mathematical model of composition
2. **Types and Functions** — Types as objects, functions as morphisms in **Hask**
3. **Categories Great and Small** — Monoids, preorders, posets as categories; size considerations
4. **Kleisli Categories** — Effectful computations as morphisms in a derived category
5. **Products and Coproducts** — Universal properties of tuples and tagged unions
6. **Simple Algebraic Data Types** — ADTs as polynomial functors, fixed points
7. **Functors** — Type constructors as endofunctors, `fmap` laws
8. **Functoriality** — Functions induce functors; contravariant functors
9. **Function Types** — Exponentials, currying, cartesian closed categories
10. **Natural Transformations** — Uniform transformations between functors

### Part Two — Universal Constructions (6 chapters)
11. **Declarative Programming** — Specifying what, not how; universal properties as specifications
12. **Limits and Colimits** — General framework for products, coproducts, pullbacks, equalizers
13. **Free Monoids** — Free constructions as left adjoints to forgetful functors
14. **Representable Functors** — Functors isomorphic to Hom(–, X); Nash-Williams theorem
15. **The Yoneda Lemma** — Objects determined by their relationships; Nat(Hom(X,–), F) ≅ F(X)
16. **Yoneda Embedding** — Fully faithful embedding of C into functor category

### Part Three — Advanced Topics (15 chapters)
17. **It's All About Morphisms** — Shift from objects to morphisms as primary focus
18. **Adjunctions** — Optimal approximation of inverses; unit and counit
19. **Free/Forgetful Adjunctions** — Free constructions across algebraic structures
20. **Monads: Programmer's Definition** — Monads as composable wrappers; `return` and `>>=`
21. **Monads and Effects** — Modeling computational effects categorically
22. **Monads Categorically** — Monads as monoids in endofunctors; adjunction-derived monads
23. **Comonads** — Dual of monads; context extraction patterns
24. **F-Algebras** — Recursive data types as initial algebras; Lambek's lemma
25. **Algebras for Monads** — Eilenberg-Moore categories;-behavioral semantics
26. **Ends and Coends** — Generalized limits over diagonals; Yoneda as coend
27. **Kan Extensions** — Optimal extensions of functors along other functors
28. **Enriched Categories** — Hom-objects from monoidal categories instead of sets
29. **Topoi** — Categories as alternative foundations for mathematics
30. **Lawvere Theories** — Categorical foundation for universal algebra
31. **Monads, Monoids, and Categories** — Unifying thread: monad ⊇ monoid ⊇ category

## How to Use CTFP

- **Reading order**: Follow chapters sequentially. Each builds on previous concepts.
- **Prerequisites**: Basic programming experience. No prior category theory needed. Some Haskell helpful but introduced gradually.
- **Code examples**: Haskell for sketching categorical concepts, C++ for showing applicability beyond functional languages. Python equivalents exist via pycategories and category-theory-python libraries.
- **Available as**: Free PDF (https://github.com/hmemcpy/milewski-ctfp-pdf), blog posts (https://bartoszmilewski.com/), hardcover (Blurb), live courses.
