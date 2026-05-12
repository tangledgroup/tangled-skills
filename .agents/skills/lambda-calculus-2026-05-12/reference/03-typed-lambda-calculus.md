# Typed Lambda Calculus

## Contents
- Typed vs. Untyped: Trade-offs
- Simply Typed Lambda Calculus (STLC)
- Typing Rules and Contexts
- Strong Normalization
- Type Inference
- Bidirectional Type Checking
- Beyond Simple Types
- Curry-Howard Isomorphism

## Typed vs. Untyped: Trade-offs

| Property | Untyped | Typed |
|----------|---------|-------|
| Expressiveness | Turing complete | Strictly weaker (cannot express all computable functions) |
| Termination | Not guaranteed | Guaranteed (strong normalization) for many systems |
| Provability | Limited | More theorems provable about programs |
| Self-application | Allowed `(λx.x x)(λx.x x)` | Disallowed (no type exists) |
| Recursion | Via fixed-point combinators | Requires explicit fix operator or recursive types |

Typed lambda calculi sacrifice some expressiveness for guarantees: every well-typed term terminates, and types can be interpreted as logical propositions.

## Simply Typed Lambda Calculus (STLC)

STLC is the simplest typed variant, introduced by Church in 1940 to avoid paradoxes in the original system. It has one type constructor — the arrow `→` — building function types from base types.

### Types

Given a set of **base types** (atomic types) like `o` (propositions) and `ι` (individuals), or commonly just a single base type:

```
type ::= base | type → type
```

Arrow associates to the right: `A → B → C` means `A → (B → C)`.

Examples of generated types:

```
o, ι, o → o, ι → o, o → (o → o), (o → o) → o, ...
```

### Terms

Terms are like untyped lambda calculus but with type annotations on abstractions:

```
term ::= x:A           -- variable with type
       | c              -- term constant (e.g., 0 for nat)
       | λx:A.M         -- abstraction: x has type A, body M
       | M N            -- application
```

A variable occurrence is **bound** if inside an abstraction that binds it. A term with no free variables is **closed**.

## Typing Rules and Contexts

A **typing context** (or environment) `Γ` is a set of assumptions mapping variables to types: `{x:A, y:B}`.

The **typing judgment** `Γ ⊢ M : A` reads "in context Γ, term M has type A." It is derived using four rules:

### Rule 1: Variable

```
  x:A ∈ Γ
─────────────  (Var)
  Γ ⊢ x : A
```

If the context says `x` has type `A`, then `x` indeed has type `A`.

### Rule 2: Constants

```
─────────────  (Const)
  Γ ⊢ c : A
```

Term constants have their declared base types (e.g., `0 : nat`).

### Rule 3: Abstraction (Arrow Introduction)

```
  Γ, x:A ⊢ M : B
───────────────────  (→I)
  Γ ⊢ λx:A.M : A → B
```

If `M` has type `B` assuming `x` has type `A`, then the abstraction `λx:A.M` has type `A → B`.

### Rule 4: Application (Arrow Elimination)

```
  Γ ⊢ M : A → B    Γ ⊢ N : A
───────────────────────────────  (→E)
       Γ ⊢ M N : B
```

If `M` is a function from `A` to `B`, and `N` has type `A`, then applying `M` to `N` yields type `B`.

### Examples of Closed Terms

- Identity: `Γ ⊢ λx:A.x : A → A`
- K-combinator: `Γ ⊢ λx:A.λy:B.x : A → B → A`
- S-combinator: `Γ ⊢ λf:(A→B→C).λg:(A→B).λx:A.f x (g x) : (A→B→C) → (A→B) → A → C`

### Type Order

The **order** of a type measures the depth of left-nested arrows:

- Base types: order 0
- `A → B`: order = order(A) + 1 (if A is a function type), else 1

Higher-order types allow functions that take functions as arguments.

## Strong Normalization

STLC is **strongly normalizing**: every sequence of β-reduuctions on any well-typed term eventually terminates. This was proved by Tait (1967) using the method of **logical relations** (also called "candidates of reducibility").

Consequences:

- No fixed-point combinators can be typed in STLC (they would have no normal form).
- The halting problem is decidable for STLC terms.
- Recursion requires extending the system (e.g., adding a `fix` operator or recursive types), which eliminates strong normalization.

## Type Inference

In practice, explicit type annotations on every abstraction are cumbersome. **Type inference** automatically deduces types.

### Hindley-Milner

The Hindley-Milner algorithm is terminating, sound, and complete for STLC: whenever a term is typable, the algorithm computes its **principal type** (the most general type from which all other valid types are instances).

Example: `λx.x` has principal type `α → α` (polymorphic in `α`). Specific instances include `nat → nat`, `(nat → nat) → (nat → nat)`, etc.

### Type Erasure

One approach: remove all type annotations (syntax identical to untyped lambda calculus), then run Hindley-Milner to verify the term is well-typed and compute its type.

## Bidirectional Type Checking

An alternative presentation divides typing into two judgments:

- **Synthesis** (`Γ ⊢ M ⇒ A`): compute the type `A` of term `M`.
- **Checking** (`Γ ⊢ M ⇐ A`): verify that term `M` has type `A`.

Rules:

1. Variables synthesize their type from context.
2. Constants synthesize their declared type.
3. To check `λx.M ⇐ A → B`, extend context with `x:A` and check `M ⇐ B`.
4. If `M ⇒ A → B` and `N ⇐ A`, then `M N ⇒ B`.
5. To check `M ⇐ A`, synthesize type and unify with `A`.
6. Explicitly annotated term `M:A` synthesizes type `A` (if `M ⇐ A`).

Annotations are needed only at β-redexes in this system, making it practical for real implementations.

## Beyond Simple Types

STLC is the foundation but limited — no polymorphism, no recursion, no dependent types. Extensions form a hierarchy:

### System T

Extends STLC with natural numbers and primitive recursion. All functions provably computable in Peano arithmetic are definable. Still strongly normalizing.

### System F (Polymorphic Lambda Calculus)

Adds universal quantification over types:

```
type ::= α | type → type | ∀α.type
term ::= λx:A.M | M N | λ⟨α⟩.M | M[A]
```

System F can express polymorphic functions like `λ⟨α⟩.λx:α.x` (identity for any type). From a logical perspective, it corresponds to second-order logic. Still strongly normalizing.

### Dependent Types

Types can depend on values. Enables expressing precise properties of programs as types. Foundation of:

- **Intuitionistic Type Theory** (Martin-Lof)
- **Calculus of Constructions** (Girard)
- **Logical Framework (LF)** — a pure lambda calculus with dependent types

### The Lambda Cube

Barendregt's lambda cube systematizes the relationships between typed lambda calculi along three dimensions:

1. **Polymorphism** (System F): types can be abstracted over types
2. **Dependent types** (LF): types can depend on terms
3. **Type operators** (Calculus of Constructions): types can depend on types

Each corner of the cube is a distinct calculus; STLC is at the origin (none of the three features).

### Pure Type Systems

A general framework subsuming the lambda cube. Defined by a small set of sorting rules. The simplest PTS has `Type : Type`, which leads to Girard's paradox (not normalizing).

## Curry-Howard Isomorphism

The Curry-Howard isomorphism (also called "proofs as programs") establishes a correspondence between typed lambda calculus and intuitionistic logic:

| Lambda Calculus | Logic |
|-----------------|-------|
| Type `A` | Proposition `A` |
| Term `M : A` | Proof of proposition `A` |
| `A → B` | Implication `A ⇒ B` |
| `λx:A.M` | Proof by assumption (introduce implication) |
| `M N` | Modus ponens (eliminate implication) |
| β-reduction | Proof normalization (cut elimination) |
| Inhabited type | Provable proposition (tautology) |
| Uninhabited type | Unprovable proposition |

STLC corresponds precisely to the **implicational fragment of intuitionistic propositional logic**. Extending the calculus with product types adds conjunction, with sum types adds disjunction, etc.

This isomorphism underpins proof assistants like Coq, Agda, and Idris, where writing a program of a given type is equivalent to constructing a proof of the corresponding proposition.
