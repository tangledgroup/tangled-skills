# Propositional Logic

## Contents
- Overview and Terminology
- Syntax
- Semantics
- Proof Systems
- Valid Argument Forms
- Metalogic

## Overview and Terminology

Propositional logic (also called sentential logic, propositional calculus, or zeroth-order logic) is the simplest formal logic. It deals with propositions — declarative sentences that are either true or false — and the logical connectives that combine them. It does not analyze the internal structure of propositions (no quantifiers, no predicates).

**Key terms:**
- **Proposition**: A declarative sentence with a truth value (True or False).
- **Atomic formula (atom)**: An indivisible proposition, represented by variables P, Q, R, etc.
- **Molecular formula**: A compound formula built from atoms using connectives.
- **Tautology**: A formula true under every interpretation (valid formula).
- **Contradiction**: A formula false under every interpretation (inconsistent).
- **Satisfiable**: A formula true under at least one interpretation.

## Syntax

### Connectives

The standard five connectives:

| Name | Symbol(s) | Meaning |
|---|---|---|
| Negation | `¬`, `~` | NOT |
| Conjunction | `∧`, `&`, `·` | AND |
| Disjunction | `∨`, `\|` | OR (inclusive) |
| Implication | `→`, `⊃` | IF...THEN (material conditional) |
| Biconditional | `↔`, `≡` | IF AND ONLY IF |

Additional connectives: NAND (`↑`, Sheffer stroke), NOR (`↓`, Peirce arrow), XOR (`⊕`).

### Formation Rules (Recursive Definition)

1. Every atomic propositional variable (P, Q, R, ...) is a formula.
2. If A is a formula, then `(¬A)` is a formula.
3. If A and B are formulas, then `(A ∧ B)`, `(A ∨ B)`, `(A → B)`, `(A ↔ B)` are formulas.
4. Nothing else is a formula (closure clause — excludes infinitely long formulas).

**BNF grammar:**
```
<formula> ::= P | Q | R | ...
           | (¬ <formula>)
           | (<formula> ∧ <formula>)
           | (<formula> ∨ <formula>)
           | (<formula> → <formula>)
           | (<formula> ↔ <formula>)
```

### Functional Completeness

Not all connectives are independent. A functionally complete set can define all others:
- `{¬, ∧}` is complete
- `{¬, ∨}` is complete
- `{¬, →}` is complete
- `{↑}` (NAND alone) is complete
- `{↓}` (NOR alone) is complete

## Semantics

### Interpretations (Valuations)

An interpretation assigns each atomic variable either True (T/1) or False (F/0). For n distinct atoms, there are 2^n possible interpretations. The connectives are truth-functional — the value of a compound depends only on the values of its parts.

### Truth Tables

| P | Q | ¬P | P∧Q | P∨Q | P→Q | P↔Q |
|---|---|---|---|---|---|---|
| T | T | F | T | T | T | T |
| T | F | F | F | T | F | F |
| F | T | T | F | T | T | F |
| F | F | T | F | F | T | T |

Key observations:
- `P→Q` is false only when P is True and Q is False.
- `P↔Q` is true when P and Q have the same truth value.

### Semantic Definitions

- **Truth-in-a-case**: Formula A is true under interpretation I if I assigns T to A.
- **Semantic consequence** (`Gamma |= phi`): phi is a semantic consequence of Gamma if no interpretation makes all of Gamma true and phi false.
- **Valid formula (tautology)** (`|= phi`): True under every interpretation.
- **Consistent**: True under at least one interpretation.
- **Inconsistent (contradiction)**: False under every interpretation.

### Key Theorems (Classical Logic)

- For any interpretation, a formula is either true or false (bivalence).
- No formula is both true and false under the same interpretation (non-contradiction).
- `|= phi` iff `|= (¬phi)` is inconsistent.
- `Gamma |= phi` iff `|= (A1 ∧ A2 ∧ ... ∧ An) → phi` where Gamma = {A1, ..., An}.

## Proof Systems

### Semantic Proof Systems

**Truth tables**: Exhaustively enumerate all 2^n interpretations. Valid iff the final column is all True. Exponential in variables — impractical for large n.

**Semantic tableaux (truth trees)**: More efficient than truth tables. Start with premises signed True and conclusion signed False. Apply decomposition rules branching on connectives. If every branch closes (contains a contradiction), the argument is valid.

### Syntactic Proof Systems

**Natural deduction**: Uses introduction and elimination rules for each connective, plus assumption and reductio ad absurdum (RAA). No axioms — only inference rules.

Core rules:
- **Assumption (A)**: Introduce any formula as an assumption.
- **→E (Modus Ponens)**: From `A→B` and `A`, infer `B`.
- **→I (Conditional Proof)**: If assuming A derives B, infer `A→B` (discharging the assumption).
- **∧I**: From A and B, infer `A∧B`.
- **∧E**: From `A∧B`, infer A (or B).
- **∨I**: From A, infer `A∨B` (for any B).
- **RAA (Reductio)**: If assuming A leads to contradiction, infer `¬A`.
- **↔I**: From `A→B` and `B→A`, infer `A↔B`.
- **DN (Double Negation)**: From `¬¬A`, infer A.
- **MTT (Modus Tollens)**: From `A→B` and `¬B`, infer `¬A` (derivable from MP + RAA).

**Axiomatic systems (Hilbert-style)**: Base tautologies as axioms, modus ponens as the sole inference rule.

Frege's system (1879): 6 axioms using only `→` and `¬`.
Łukasiewicz's P2: 3 axioms:
- A1: `(A → (B → A))`
- A2: `((A → (B → C)) → ((A → B) → (A → C)))`
- A3: `((¬A → ¬B) → (B → A))`

**Sequent calculus**: Gentzen's LK system representing deductions as sequents `Gamma ⊢ Delta`.

## Valid Argument Forms

| Name | Form |
|---|---|
| Modus Ponens | `P→Q, P |= Q` |
| Modus Tollens | `P→Q, ¬Q |= ¬P` |
| Hypothetical Syllogism | `P→Q, Q→R |= P→R` |
| Disjunctive Syllogism | `P∨Q, ¬P |= Q` |
| Constructive Dilemma | `P→Q, R→S, P∨R |= Q∨S` |
| Simplification | `P∧Q |= P` |
| Conjunction | `P, Q |= P∧Q` |
| Addition | `P |= P∨Q` |
| De Morgan (1) | `¬(P∧Q) ⟺ ¬P∨¬Q` |
| De Morgan (2) | `¬(P∨Q) ⟺ ¬P∧¬Q` |
| Double Negation | `P ⟺ ¬¬P` |
| Transposition | `(P→Q) ⟺ (¬Q→¬P)` |
| Material Implication | `(P→Q) ⟺ (¬P∨Q)` |
| Excluded Middle | `|= P∨¬P` |
| Non-Contradiction | `|= ¬(P∧¬P)` |
| Explosion | `P, ¬P |= Q` (from contradiction, anything follows) |

## Metalogic

Propositional logic enjoys:
- **Soundness**: Every provable formula is valid.
- **Completeness**: Every valid formula is provable.
- **Decidability**: Truth tables provide a decision procedure (exponential but effective).
- **Consistency**: No contradiction is provable.
- **Compactness**: If `Gamma |= phi`, then some finite subset of Gamma entails phi.
