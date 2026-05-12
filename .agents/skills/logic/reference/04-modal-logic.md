# Modal Logic

## Contents
- Overview and Motivation
- Syntax of Modal Operators
- Relational (Kripke) Semantics
- Axiomatic Systems
- Philosophical Modal Logics
- Applications

## Overview and Motivation

Modal logic extends classical logic with operators for modality — concepts like necessity, possibility, knowledge, obligation, and temporal progression. The formula `□P` can mean "necessarily P," "P is known," or "P is obligatory" depending on the interpretation.

First developed axiomatically by C.I. Lewis (1912), modern modal logic uses Kripke's relational semantics (mid-20th century, building on work by Prior and Hintikka). Applications span philosophy, computer science (verification, temporal logic), game theory, legal theory, and social epistemology.

## Syntax of Modal Operators

### Basic Operators

| Symbol | Reading | Dual |
|---|---|---|
| `□` (Box) | "necessarily" | `◇φ ≡ ¬□¬φ` |
| `◇` (Diamond) | "possibly" | `□φ ≡ ¬◇¬φ` |

When duals hold, one operator suffices syntactically. Some systems (e.g., non-normal modal logics) require both as primitives.

### Extended Syntax

Recursive definition for propositional modal logic:
1. If P is atomic, then P is a formula.
2. If A is a formula, then `(¬A)` is a formula.
3. If A, B are formulas, then `(A ∧ B)` is a formula.
4. If A is a formula, then `(□A)` is a formula.
5. If A is a formula, then `(◇A)` is a formula.

### Notation Variants

| Context | Necessity | Possibility |
|---|---|---|
| Alethic | `□`, `⊓` | `◇`, `⊔` |
| Epistemic | `K` (known) | `M` (consistent with knowledge) |
| Doxastic | `B` (believed) | — |
| Temporal (past) | `H` (has always been) | `P` (once was) |
| Temporal (future) | `G` (will always be) | `F` (will sometime be) |
| Deontic | `O` (obligatory) | `P` (permitted) |

Multi-modal logics use indexed operators: `□₁φ`, `□₂φ` (e.g., "I know P is permitted" = `K(O P)`).

### Modal Predicate Logic

Extends modal logic with FOL quantifiers. Example: `∀x. □P(x)` — "necessarily, everything has property P." Complications arise with varying domains across possible worlds.

## Relational (Kripke) Semantics

### Basic Notions

A **Kripke frame** is a pair `(W, R)` where:
- W is a nonempty set of **possible worlds**.
- R ⊆ W × W is an **accessibility relation**.

A **model** is a triple `(W, R, V)` where V is a **valuation** assigning each atomic proposition a subset of W (the worlds where it is true).

### Truth Conditions

Truth is evaluated relative to a world w in model M:

- `M, w ⊨ P` iff w ∈ V(P)
- `M, w ⊨ ¬A` iff not `M, w ⊨ A`
- `M, w ⊨ A ∧ B` iff `M, w ⊨ A` and `M, w ⊨ B`
- `M, w ⊨ □A` iff for all v such that wRv, `M, v ⊨ A`
- `M, w ⊨ ◇A` iff there exists v such that wRv and `M, v ⊨ A`

**Validity in a frame**: φ is valid in frame F if it is true at every world in every model based on F.
**Validity in a class of frames**: φ is valid in class C if valid in every frame in C.

### Frames and Completeness

Properties of R correspond to axioms:

| Frame Property | Axiom | Logic |
|---|---|---|
| None (minimal) | K: `□(A→B) → (□A→□B)` | **K** |
| Reflexive | T: `□A → A` | **T** (M) |
| Transitive | 4: `□A → □□A` | **S4** (= T + 4) |
| Euclidean | 5: `◇A → □◇A` | **S5** (= T + 4 + 5) |
| Symmetric | B: `A → □◇A` | **B** (= T + B) |
| Serial | D: `□A → ◇A` | **D** (deontic base) |

**Completeness**: A logic L is complete for a class of frames C if every formula valid in C is provable in L. Standard systems K, T, S4, S5, D are all sound and complete for their corresponding frame classes.

## Axiomatic Systems

### System K (Minimal Normal Modal Logic)

- All propositional tautologies
- **K axiom**: `□(A → B) → (□A → □B)`
- **Necessitation rule**: If ⊢ A, then ⊢ □A
- **Modus Ponens**: From A and A→B, infer B

### Extensions

- **T** = K + `□A → A` (reflexive frames)
- **S4** = T + `□A → □□A` (reflexive + transitive)
- **S5** = S4 + `◇A → □◇A` (equivalence relation frames)
- **D** = K + `□A → ◇A` (serial frames, used in deontic logic)

### Structural Proof Theory

Sequent calculi and tableaux methods exist for modal logics, handling the box/diamond rules with world-labeling or signed formulas.

### Decision Methods

Propositional modal logic is decidable. The finite model property holds for K, T, S4, S5 — if a formula is satisfiable, it is satisfiable in a finite model.

## Philosophical Modal Logics

### Alethic Logic

Concerns necessity and possibility:
- **Physical possibility**: Compatible with laws of nature.
- **Metaphysical possibility**: Compatible with the nature of reality (broader than physical).
- S5 is commonly used for metaphysical modality.

### Epistemic Logic

Models knowledge and belief:
- `K_i φ`: Agent i knows φ.
- Standard axioms: K (normality), T (`Kφ → φ`, only truths are known), 4 (`Kφ → KKφ`, positive introspection), 5 (`¬Kφ → K¬Kφ`, negative introspection) → **S5** for ideal knowledge.
- **Common knowledge**: `Eφ` (everyone knows) and `Cφ` (common knowledge, everyone knows that everyone knows, ad infinitum).

### Temporal Logic

Models time:
- **Linear temporal logic (LTL)**: Time is a linear sequence. Operators G (always), F (eventually), X (next), U (until).
- **Branching temporal logic (CTL/CTL*)**: Time branches. Path quantifiers A (all paths) and E (exists a path) combined with temporal operators.
- Used in model checking for verifying hardware and software systems.

### Deontic Logic

Models obligation and permission:
- `Oφ`: It is obligatory that φ.
- `Pφ`: It is permitted that φ (`Pφ ≡ ¬O¬φ`).
- Base system is **D** (not T), because obligations need not be fulfilled: `□A → ◇A` (if obligatory, then possible).
- **Paradoxes**: Ross's paradox (`OA ∨ OB` from `O(A ∨ B)`), the paradox of derived obligation.

### Doxastic Logic

Models belief:
- `Bφ`: Agent believes φ.
- System **KD45** (not T — beliefs can be false; includes 4 and 5 for introspection).
- Distinguishes knowledge (T holds) from belief (T fails).

## Applications

- **Verification**: Temporal logic for model checking (TLA+, SPIN, NuSMV).
- **Game theory**: Epistemic logic for reasoning about players' knowledge.
- **Web design**: Modal specifications for access control and security policies.
- **Legal theory**: Deontic logic for normative reasoning.
- **Social epistemology**: Multi-agent epistemic logic for distributed knowledge.
- **Set theory**: Multiverse-based set theory using modal operators.
