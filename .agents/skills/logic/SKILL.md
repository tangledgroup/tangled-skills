---
name: logic
description: Comprehensive reference covering formal logic systems from propositional through higher-order logic, plus modal logic, soundness, and inductive reasoning. Use when working with logical formalisms, constructing proofs, analyzing arguments, building theorem provers, designing type systems, implementing satisfiability solvers, or reasoning about logical properties like validity, completeness, and expressiveness.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - logic
  - propositional-logic
  - first-order-logic
  - higher-order-logic
  - modal-logic
  - soundness
  - inductive-reasoning
category: language-runtime
external_references:
  - https://en.wikipedia.org/wiki/Propositional_logic
  - https://en.wikipedia.org/wiki/First-order_logic
  - https://en.wikipedia.org/wiki/Second-order_logic
  - https://en.wikipedia.org/wiki/Higher-order_logic
  - https://en.wikipedia.org/wiki/Modal_logic
  - https://en.wikipedia.org/wiki/Soundness
  - https://en.wikipedia.org/wiki/Inductive_reasoning
---

# Formal Logic Reference

## Overview

Formal logic provides mathematical frameworks for representing and analyzing reasoning. The hierarchy progresses from propositional logic (truth-functional connectives over atomic propositions) through first-order logic (quantifiers over individuals with predicates) to second- and higher-order logics (quantification over sets, functions, and properties). Modal logic extends these systems with operators for necessity, possibility, knowledge, obligation, and time. Soundness ensures that provable statements are true, while inductive reasoning covers non-deductive inference from specific observations to general conclusions.

## When to Use

- Building theorem provers, SAT solvers, or SMT solvers
- Designing type systems or programming language semantics
- Formalizing mathematical theories (arithmetic, set theory, geometry)
- Analyzing argument validity, soundness, and completeness
- Implementing knowledge representation and reasoning systems
- Working with modal operators in verification, epistemic reasoning, or temporal logic
- Distinguishing deductive certainty from inductive probability
- Choosing the appropriate logic level for a formalization task

## Core Concepts

**Logic hierarchy by expressive power:**

| Logic | Quantifies Over | Key Feature | Decidable? |
|---|---|---|---|
| Propositional | Nothing (atomic propositions only) | Truth-functional connectives | Yes |
| First-order (FOL) | Individuals | Predicates, universal/existential quantifiers | No (semidecidable) |
| Second-order (SOL) | Sets, relations, functions | Quantification over predicates | No |
| Higher-order (HOL) | Arbitrary nested sets | Full type hierarchy | No |
| Modal | Possible worlds | Necessity/diamond operators | Varies by system |

**Key metalogical properties:**
- **Validity**: A formula true in every interpretation (tautology).
- **Soundness**: Every provable formula is valid. If `Gamma |- phi`, then `Gamma |= phi`.
- **Completeness**: Every valid formula is provable. If `Gamma |= phi`, then `Gamma |- phi`.
- **Decidability**: An algorithm exists to determine validity of any formula.
- **Compactness**: A set has a model iff every finite subset has a model (holds for FOL, not SOL with standard semantics).
- **Lowenheim-Skolem**: Any FOL theory with an infinite model has models of every infinite cardinality.

**Notation:**
- `|-` (turnstile): Syntactic consequence / provability
- `|= ` (double turnstile): Semantic consequence / logical entailment
- `True`, `False`: Propositional constants (also written `top`, `bot`)
- `forall x. P(x)`: Universal quantification ("for all x, P holds")
- `exists x. P(x)`: Existential quantification ("there exists an x such that P holds")
- `Box phi`: Necessity ("necessarily phi")
- `Diamond phi`: Possibility ("possibly phi")

## Advanced Topics

**Propositional Logic**: Syntax, semantics, truth tables, natural deduction, axiomatic systems, and valid argument forms → [Propositional Logic](reference/01-propositional-logic.md)

**First-Order Logic**: Quantifiers, predicates, terms, free/bound variables, structures, Gödel's completeness, undecidability, decidable fragments, Lowenheim-Skolem, compactness, Lindström's theorem → [First-Order Logic](reference/02-first-order-logic.md)

**Second and Higher-Order Logic**: Quantification over sets and functions, standard vs Henkin semantics, expressive power, categoricity, deductive incompleteness, monadic fragments, computational complexity connections → [Second and Higher-Order Logic](reference/03-second-and-higher-order-logic.md)

**Modal Logic**: Kripke semantics, frames, accessibility relations, axiomatic systems (K, T, S4, S5), alethic/epistemic/temporal/deontic/doxastic modalities → [Modal Logic](reference/04-modal-logic.md)

**Soundness and Inductive Reasoning**: Weak vs strong soundness for formal systems, soundness of arguments, completeness duality, inductive generalization, prediction, causal inference, problem of induction → [Soundness and Inductive Reasoning](reference/05-soundness-and-inductive-reasoning.md)
