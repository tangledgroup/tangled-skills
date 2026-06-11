# Soundness and Inductive Reasoning

## Contents
- Soundness of Arguments
- Soundness of Formal Systems
- Relation to Completeness
- Inductive Reasoning: Overview
- Types of Inductive Reasoning
- Methods of Induction
- Problem of Induction
- Comparison: Deductive vs Inductive

## Soundness of Arguments

In deductive reasoning, an argument consists of premises and a conclusion.

**Validity**: An argument is valid if the conclusion *must* be true whenever all premises are true. Equivalently, it is impossible for all premises to be true while the conclusion is false. Validity concerns logical form, not actual truth of premises.

**Soundness**: An argument is sound if and only if:
1. It is valid, AND
2. All its premises are actually true.

A sound argument guarantees a true conclusion.

### Examples

**Sound argument:**
- Premise 1: All men are mortal.
- Premise 2: Socrates is a man.
- Conclusion: Therefore, Socrates is mortal.
Valid (modus ponens form) + true premises = sound.

**Valid but unsound:**
- Premise 1: All birds can fly.
- Premise 2: Penguins are birds.
- Conclusion: Therefore, penguins can fly.
Valid (form is correct) but premise 1 is false = unsound.

## Soundness of Formal Systems

In mathematical logic, soundness applies to deductive systems (proof calculi).

### Definition

A logical system with syntactic entailment `|-` and semantic entailment `|= ` is **sound** if:
> For any set of sentences Gamma and sentence phi: if `Gamma |- phi`, then `Gamma |= phi`.

All theorems are validities. Every provable statement is semantically true.

### Weak vs Strong Soundness

| Type | Statement |
|---|---|
| **Weak soundness** | If `⊢ φ` (provable from no premises), then `⊨ φ` (true in all structures). All theorems are tautologies. |
| **Strong soundness** | If `Gamma ⊢ φ`, then `Gamma ⊨ φ`. Provable from premises implies semantic consequence. |

Strong soundness subsumes weak (empty Gamma case).

### Arithmetic Soundness

A theory T whose discourse interprets as natural numbers is **arithmetically sound** if all its theorems are actually true about standard integers. Related to ω-consistency.

### Proving Soundness

Most soundness proofs are straightforward:
1. Verify each axiom is valid (true in all interpretations).
2. Verify each inference rule preserves validity (if premises are valid, conclusion is valid).
3. For Hilbert systems: verify axioms + modus ponens (and substitution if present).

## Relation to Completeness

**Completeness** is the converse of soundness:
> If `Gamma |= phi`, then `Gamma |- phi`.

Every semantic consequence is provable. Together, soundness and completeness mean: all and only validities are provable.

### Gödel's Completeness Theorem (1929)

First-order logic is complete: every logically valid formula has a finite proof. This was first explicitly established by Gödel, building on earlier work by Skolem.

### Gödel's Incompleteness Theorem (1931)

For languages expressive enough for arithmetic, no consistent and effective deductive system is complete with respect to the *intended* interpretation. Not all sound systems are complete in this special sense (restricted to intended models). The original completeness theorem applies to *all* classical models, not just intended ones.

## Inductive Reasoning: Overview

Inductive reasoning produces conclusions that are **probable** rather than certain, given the premises. Unlike deductive reasoning where true premises guarantee a true conclusion, inductive reasoning provides support with varying degrees of strength.

**Key distinction**: Deductive = certainty (if premises true, conclusion must be true). Inductive = probability (if premises true, conclusion is likely true).

Note: Mathematical induction (proof by induction on natural numbers) is actually deductive, not inductive reasoning despite the name.

## Types of Inductive Reasoning

### Inductive Generalization

Inferring a general rule from specific observations.

**Statistical generalization**: "95% of sampled voters support X, therefore approximately 95% of all voters support X." Strength depends on sample size, representativeness, and randomness.

**Anecdotal generalization**: Drawing conclusions from personal experience or isolated cases. Generally weak — small, biased samples.

### Prediction

Inferring that future instances will resemble past instances. "The sun has risen every day; therefore it will rise tomorrow." This is the paradigmatic case of inductive inference.

### Statistical Syllogism

Quantitative form: "X% of A are B. c is an A. Therefore, probably (with confidence X%), c is a B."

Example: "90% of humans are mortal. Socrates is human. Therefore, probably (90% confidence), Socrates is mortal."

### Argument from Analogy

"A has properties P1, P2, P3, and Q. B has properties P1, P2, P3. Therefore, probably, B has property Q." Strength depends on relevance and number of shared properties.

### Causal Inference

Inferring causal relationships from correlations and patterns. "Every time A occurs, B follows. Therefore, A probably causes B." Requires ruling out confounding factors.

## Methods of Induction

### Enumerative Induction

Observe that many instances of A have property B. Conclude all (or most) A have B. The simplest inductive method — strength increases with number and diversity of observations.

### Eliminative Induction

Consider multiple hypotheses that explain the observations. Systematically eliminate hypotheses inconsistent with evidence. The surviving hypothesis is accepted. Stronger than enumerative induction when few alternatives remain.

## Problem of Induction

The **problem of induction** questions whether inductive reasoning is epistemically justified:

- **David Hume (1739)**: Induction assumes the future will resemble the past (uniformity of nature), but this assumption cannot be proven deductively (circular) or inductively (begs the question).
- **Bertrand Russell**: Highlighted that no amount of past observation guarantees future regularity.
- **Immanuel Kant**: Argued induction requires synthetic a priori principles.
- **Gilbert Harman**: Proposed inference to the best explanation as a form of induction — we accept the hypothesis that best explains all available evidence.

### Biases in Inductive Reasoning

- **Confirmation bias**: Seeking evidence that confirms existing beliefs.
- **Availability heuristic**: Overweighting readily recalled examples.
- **Base rate neglect**: Ignoring prior probabilities in favor of specific evidence.
- **Selection bias**: Non-representative samples skew generalizations.

## Comparison: Deductive vs Inductive

| Feature | Deductive | Inductive |
|---|---|---|
| Conclusion strength | Certain (if premises true) | Probable |
| Premise-conclusion link | Necessary | Supportive |
| New information | None (conclusion contained in premises) | Yes (conclusion goes beyond premises) |
| Validity/soundness | Applicable | Strength/cogency instead |
| Examples | Syllogisms, mathematical proofs | Scientific generalizations, predictions |
| Formal systems | Propositional/FOL/SOL/modal logic | Probability theory, Bayesian inference |

## Bayesian Inference

Bayesian methods formalize inductive reasoning mathematically:
- **Prior probability** P(H): Initial belief in hypothesis H.
- **Likelihood** P(E|H): Probability of evidence E given H.
- **Posterior probability** P(H|E) = P(E|H) × P(H) / P(E): Updated belief after observing E.

Bayesian inference provides a rigorous framework for updating beliefs in light of new evidence, addressing the problem of induction through degree-of-belief semantics rather than all-or-nothing truth.
