# First-Order Logic

## Contents
- Overview and Motivation
- Syntax
- Semantics
- Deductive Systems
- Equality
- Metalogical Properties
- Limitations and Extensions

## Overview and Motivation

First-order logic (FOL), also called predicate logic or quantificational logic, extends propositional logic with predicates, functions, and quantifiers over individuals. While propositional logic treats "Socrates is a philosopher" as an atomic proposition P, FOL analyzes it as `Philosopher(Socrates)` — applying a predicate to an individual.

FOL is the standard for formalizing mathematics (Peano arithmetic, ZFC set theory) and is widely used in computer science (knowledge representation, database query languages, automated theorem proving).

## Syntax

### Alphabet

**Logical symbols:**
- Quantifiers: `∀` (universal), `∃` (existential)
- Connectives: `¬`, `∧`, `∨`, `→`, `↔`
- Equality: `=` (optional, can be added to the language)
- Variables: x, y, z, ... (countably infinite supply)
- Parentheses: `(`, `)`

**Non-logical symbols** (vary by theory):
- **Predicate symbols**: P, Q, R with specified arity (e.g., Unary(P), Binary(R))
- **Function symbols**: f, g, h with specified arity (e.g., Unary(f), Binary(g))
- **Constant symbols**: a, b, c (nullary functions)

### Formation Rules

**Terms** (denote individuals):
1. Every variable is a term.
2. Every constant symbol is a term.
3. If f is an n-ary function symbol and t1,...,tn are terms, then `f(t1,...,tn)` is a term.

**Formulas**:
1. If P is an n-ary predicate and t1,...,tn are terms, then `P(t1,...,tn)` is an atomic formula.
2. If `t1 = t2` where t1, t2 are terms, this is an atomic formula (if equality is in the language).
3. If A is a formula, then `(¬A)` is a formula.
4. If A and B are formulas, then `(A ∧ B)`, `(A ∨ B)`, `(A → B)`, `(A ↔ B)` are formulas.
5. If A is a formula and x is a variable, then `(∀x. A)` and `(∃x. A)` are formulas.

### Free and Bound Variables

- A variable occurrence is **bound** if it appears within the scope of a quantifier for that variable (e.g., the x in `∀x. P(x)`).
- A variable occurrence is **free** otherwise (e.g., the y in `∀x. R(x, y)`).
- A **sentence** (closed formula) has no free variables. Sentences have definite truth values in a given structure.

### Notational Conventions

- `∃!x. P(x)` means "there exists a unique x such that P(x)", abbreviating `∃x.(P(x) ∧ ∀y.(P(y) → (x = y)))`.
- `∀x,y. A` abbreviates `∀x. ∀y. A`.
- Mixed quantifier notation: `∀x. ∃y. R(x,y)`.

## Semantics

### First-Order Structures (Models)

A structure M consists of:
1. **Domain D**: A nonempty set of individuals (the universe of discourse).
2. **Interpretation function I**:
   - Maps each constant symbol to an element of D.
   - Maps each n-ary function symbol to a function D^n → D.
   - Maps each n-ary predicate symbol to a subset of D^n (an n-ary relation on D).
   - Maps `=` to actual equality on D (if equality is in the language).

### Truth Evaluation

Truth is defined recursively relative to a structure M and a variable assignment s:
- `M, s ⊨ P(t1,...,tn)` iff `(s(t1),...,s(tn))` is in the relation assigned to P.
- `M, s ⊨ ∀x. A` iff for every d in D, `M, s[x↦d] ⊨ A`.
- `M, s ⊨ ∃x. A` iff there exists some d in D such that `M, s[x↦d] ⊨ A`.
- Connectives evaluated as in propositional logic.

For sentences (no free variables), truth depends only on M, not on s. We write `M ⊨ A`.

### Validity, Satisfiability, Consequence

- **Valid** (`⊨ A`): True in every structure under every assignment.
- **Satisfiable**: True in at least one structure under some assignment.
- **Logical consequence** (`Gamma ⊨ phi`): Every structure satisfying all formulas in Gamma also satisfies phi.
- **Theory**: A set of sentences. A **model of a theory** is a structure satisfying all its sentences.

## Deductive Systems

### Rules of Inference (beyond propositional rules)

- **Universal Instantiation (∀E)**: From `∀x. A(x)`, infer `A(t)` for any term t.
- **Universal Generalization (∀I)**: If A(x) is derived and x does not occur free in any undischarged assumption, infer `∀x. A(x)`.
- **Existential Instantiation (∃E)**: From `∃x. A(x)`, assume `A(c)` for a fresh constant c, derive B (not containing c), then conclude B.
- **Existential Generalization (∃I)**: From `A(t)`, infer `∃x. A(x)`.

### Proof Systems

1. **Hilbert-style systems**: Axiom schemas + modus ponens + generalization rule.
2. **Natural deduction**: Propositional rules plus quantifier introduction/elimination rules.
3. **Sequent calculus (LK)**: Gentzen's system with left/right rules for each connective and quantifier.
4. **Tableaux method**: Semantic tree decomposition extended to handle quantifiers (instantiation on open branches).
5. **Resolution**: Converts formulas to clausal form, refutes by deriving empty clause. Basis of automated theorem proving (Prolog uses Horn clause resolution).

## Equality

### First-Order Logic with Equality

Standard equality axioms:
1. **Reflexivity**: `∀x. (x = x)`
2. **Substitution for predicates**: `∀x∀y. (x = y → (P(x) → P(y)))`
3. **Substitution for functions**: `∀x∀y. (x = y → f(x) = f(y))`

### Defining Equality Within a Theory

If equality is not primitive, it can be defined as Leibniz equality:
`x ≈ y` iff `∀P. (P(x) ↔ P(y))` — x and y share all properties.
This requires second-order logic for the full definition, but within a specific first-order theory, equality can be axiomatized directly.

## Metalogical Properties

### Gödel's Completeness Theorem (1929)

FOL has sound, complete, effective deductive systems. Every logically valid formula is provable, and every provable formula is valid. Logical consequence is **semidecidable** — if `Gamma ⊨ phi`, a finite proof can be found by enumerating all derivations.

### Undecidability (Church-Turing, 1936-37)

FOL is undecidable (given at least one predicate of arity ≥ 2). No algorithm determines whether an arbitrary formula is valid. This solves the Entscheidungsproblem negatively. The connection to the halting problem is central to the proof.

### Decidable Fragments

| Fragment | Description |
|---|---|
| Monadic predicate logic | Only unary predicates, no functions |
| Bernays-Schönfinkel class | Prenex form with `∃*∀*` prefix |
| Two-variable logic (C2) | Only two variables, with counting quantifiers |
| Guarded fragment | Quantifiers restricted to "guarded" contexts |
| Description logics | Used in knowledge representation (OWL) |

### Löwenheim-Skolem Theorem

If a countable FOL theory has an infinite model, it has models of every infinite cardinality. Consequences:
- No FOL theory with an infinite model can be categorical (have a unique model up to isomorphism).
- Cannot characterize countability or uncountability in FOL.
- Applied to set theories, yields Skolem's paradox.

### Compactness Theorem

A set of FOL sentences has a model iff every finite subset has a model. Consequences:
- If a formula follows from infinitely many axioms, it follows from finitely many.
- Any theory with arbitrarily large finite models has an infinite model.
- The class of all finite graphs is not an elementary class.

### Lindström's Theorem (1956)

FOL is maximal: no strictly stronger logic can also satisfy both the Löwenheim-Skolem theorem and compactness. Alternatively, no stronger logic can have a semidecidable consequence relation and satisfy Löwenheim-Skolem. This characterizes FOL uniquely among abstract logical systems.

## Limitations and Extensions

### Expressiveness Limits

- Cannot express connectedness in graphs (requires SOL).
- Cannot categorically axiomatize the natural numbers or real line.
- Cannot quantify over properties, sets, or functions.
- Many natural language constructions resist FOL formalization (quantification over properties, relative adjectives, predicate adverbials).

### Extensions

- **Many-sorted logic**: Variables have different sorts/types with separate domains. Reducible to single-sorted FOL with finitely many sorts.
- **Additional quantifiers**: Uniqueness (`∃!`), bounded quantifiers, counting quantifiers.
- **Infinitary logics (L_κλ)**: Allow infinite conjunctions/disjunctions. L_ωω is ordinary FOL; L_∞ω allows arbitrary-sized connectives.
- **Non-classical variants**: Intuitionistic FOL (rejects double negation elimination), fuzzy FOL (many-valued truth).
- **Modal extensions**: First-order modal logic with possible worlds and varying domains.
- **Fixpoint logic**: Extends FOL with least fixed points of positive operators.
- **Higher-order logics**: Quantification over predicates, sets, functions (see next reference).
