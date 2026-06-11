# Second and Higher-Order Logic

## Contents
- Second-Order Logic: Quantification Scope
- Syntax and Fragments
- Semantics: Standard vs Henkin
- Expressive Power
- Deductive Systems and Incompleteness
- Higher-Order Logic
- Computational Complexity Connections

## Second-Order Logic: Quantification Scope

Second-order logic (SOL) extends first-order logic by allowing quantification over predicates, sets, and functions. Where FOL quantifies only over individuals, SOL also quantifies over properties of individuals.

**Example**: In FOL, we can say `∀x.(Human(x) → Mortal(x))` but cannot quantify over the predicate itself. In SOL:
- `∃P. P(Socrates)` — "There is a property that Socrates has."
- `∀P.(P(Socrates) → P(Plato))` — "Socrates and Plato share all properties" (Leibniz equality).

**Reachability example**: FOL cannot express ancestry from Parent(x,y). SOL can:
```
Ancestor(x, y) iff ∀S. (S(y) ∧ ∀a∀b.(S(a) ∧ Parent(b,a) → S(b)) → S(x))
```
Read: Every set containing y and closed under the parent relation also contains x.

## Syntax and Fragments

### Extended Syntax

Beyond FOL syntax, SOL adds new variable sorts:
- **Set variables** (unary relation variables): S, T, U. Atomic formula: `t ∈ S` or `S(t)`.
- **k-ary relation variables**: R. Atomic formula: `R(t1,...,tk)`.
- **k-ary function variables**: f. Term: `f(t1,...,tk)`.

Each variable sort can be universally or existentially quantified: `∀S. A`, `∃R. B`, etc.

### Fragments of SOL

| Fragment | Description | Decidable? |
|---|---|---|
| **Monadic SOL (MSO)** | Only unary (set) quantification | Yes (on trees, S2S) |
| **Weak SOL (WSO)** | Quantification over finite sets only | Varies |
| **Existential SOL (ESO/Σ¹₁)** | Form `∃S. φ` where φ is FOL | No |
| **Universal SOL (Π¹₁)** | Form `∀S. φ` where φ is FOL | No |

MSO is particularly important in computer science (Courcelle's theorem: any graph property expressible in MSO can be decided in linear time on graphs of bounded treewidth).

## Semantics: Standard vs Henkin

### Standard (Full) Semantics

Quantifiers range over **all** subsets, relations, and functions of the appropriate arity. Once the first-order domain is fixed, the second-order domains are determined (e.g., set variables range over the full powerset). This gives SOL its expressive power but breaks nice metalogical properties.

### Henkin Semantics

Each higher-order type has a separate domain that may be a **proper subset** of all possible objects of that type. Henkin semantics reduces SOL to many-sorted FOL. Under Henkin semantics:
- Gödel's completeness theorem holds.
- Compactness theorem holds.
- Löwenheim-Skolem theorems hold.
- By Lindström's theorem, Henkin models are "disguised first-order models."

The distinction is analogous to provability in ZFC vs truth in the von Neumann universe V: Henkin semantics obeys model-theoretic niceties; standard semantics has categoricity phenomena.

## Expressive Power

SOL with standard semantics is strictly more expressive than FOL:

**Least-upper-bound property** (characterizes real numbers):
```
∀S. (∃x. x ∈ S ∧ ∃b. ∀y.(y ∈ S → y ≤ b) →
     ∃s. (∀y.(y ∈ S → y ≤ s) ∧ ∀c.((∀y.(y ∈ S → y ≤ c)) → s ≤ c)))
```
No set of FOL sentences can express this (compactness theorem prevents it).

**Finiteness**: SOL can say "the domain is finite" by asserting every surjective function is injective. FOL cannot (compactness + upward Löwenheim-Skolem).

**Countability**: SOL can express that the domain is countable. FOL cannot.

**Categoricity**: The second-order theory of real numbers (complete Archimedean ordered field) has exactly one model up to isomorphism. No FOL theory with an infinite model can be categorical.

## Deductive Systems and Incompleteness

### No Complete Proof System (Standard Semantics)

By Gödel's incompleteness theorem, no deductive system for SOL with standard semantics can simultaneously satisfy:
1. **Soundness**: Every provable sentence is universally valid.
2. **Completeness**: Every universally valid sentence is provable.
3. **Effectiveness**: Proof-checking is algorithmic.

This is sometimes stated as "SOL does not admit a complete proof theory." Quine used this as an argument that SOL is not "logic" properly speaking.

### Available Deductive Systems

- **Augmented FOL**: Standard FOL system + substitution rules for second-order terms. Used in second-order arithmetic.
- **With comprehension and choice axioms**: Adds sound axioms about existence of sets defined by formulas. Complete for Henkin semantics (restricted to models satisfying these axioms).

### Non-Reducibility to FOL

Attempting to reduce SOL to FOL by expanding the domain to include sets fails because the requirement that the domain includes **all** subsets cannot be expressed in FOL (Löwenheim-Skolem yields countable "internal" models that satisfy the same FOL sentences but do not contain all subsets).

## Higher-Order Logic

Higher-order logic (HOL) generalizes SOL to arbitrary nesting depth:
- **First-order**: Quantifies over individuals.
- **Second-order**: Also quantifies over sets of individuals.
- **Third-order**: Also quantifies over sets of sets.
- **HOL**: Union of all orders — arbitrary nesting.

### Semantics

**Standard semantics**: Quantifiers range over all objects of each type. HOL admits categorical axiomatizations of natural numbers and real numbers. By Gödel, no effective, sound, and complete proof calculus exists.

**Henkin semantics**: Separate domain for each type. Equivalent to many-sorted FOL. Inherits completeness, compactness, and Löwenheim-Skolem from FOL.

### Key Properties

- **Undecidable unification**: Gérard Huet proved unifiability is undecidable in third-order logic (no algorithm decides whether an equation between second-order terms has a solution).
- **Second-order sufficiency**: Jaakko Hintikka (1955) showed that SOL can simulate any higher-order logic — for every HOL formula, there is an equisatisfiable SOL formula. The power set operation is definable in SOL.
- **Modal HOL**: Gödel's ontological proof is best studied in modal higher-order logic (at least third-order, due to quantification over properties of properties).

## Computational Complexity Connections

Descriptive complexity characterizes complexity classes by logical expressiveness on finite structures:

| Logic Fragment | Complexity Class | Theorem |
|---|---|---|
| Monadic SOL (Büchi) | REG (regular languages) | Büchi-Elgot-Trakhtenbrot (1960) |
| Existential SOL (Σ¹₁) | NP | Fagin's theorem (1974) |
| Universal SOL (Π¹₁) | co-NP | — |
| Full SOL | PH (polynomial hierarchy) | — |
| SOL + transitive closure | PSPACE | — |
| SOL + least fixed point | EXPTIME | — |
