# Reduction and Evaluation

## Contents
- Alpha-Conversion (α)
- Capture-Avoiding Substitution
- Beta-Reduction (β)
- Eta-Conversion (η)
- Redexes and Normal Forms
- Confluence and the Church-Rosser Theorem
- Evaluation Strategies

## Alpha-Conversion (α)

**α-conversion** allows renaming bound variables in an abstraction. It captures the intuition that the particular name of a bound variable does not matter.

```
λx.x   α-equivalent to   λy.y
```

Two terms differing only by α-conversion are **α-equivalent**, written `M ≡α N`.

### Rules

- Only rename variables bound by the same abstraction.
- Do not rename if it would cause a free variable to be captured by another abstraction.

Example — correct renaming:

```
λx.(λy.x y) →α λa.(λb.a b)
```

Example — incorrect renaming (would capture `z`):

```
λz.(λx.z)  -- cannot rename z to x, because x is already bound inside
```

### De Bruijn Indices

An alternative notation that eliminates names entirely by replacing bound variables with indices counting how many λs enclose the occurrence. In De Bruijn notation, all α-equivalent terms are syntactically identical, so name collision is impossible.

## Capture-Avoiding Substitution

**Substitution**, written `M[x := N]`, replaces every free occurrence of variable `x` in term `M` with term `N`, while avoiding **variable capture** (where a free variable in `N` becomes accidentally bound).

### Definition (by recursion on M)

- `x[x := N] = N`
- `y[x := N] = y` (when `y ≠ x`)
- `(P Q)[x := N] = (P[x := N]) (Q[x := N])` — distribute to both sides
- `(λx.P)[x := N] = λx.P` — bound variable, no change
- `(λy.P)[x := N] = λy.(P[x := N])` — when `y ≠ x` and `y` not free in `N`
- `(λy.P)[x := N] = λz.((P[y := z])[x := N])` — when `y ≠ x` but `y` is free in `N`; first α-rename `y` to a fresh `z`, then substitute

### Example

```
(λx.y x)[y := (λy.y)]
```

Naive substitution would give `λx.(λy.y) x` — correct here because the `y` in `λy.y` is bound. But consider:

```
(λz.(λx.z x))[z := (λx.x)]
```

Naive: `λx.(λx.x) x` — wrong! The `x` from `(λx.x)` gets captured by the inner `λx`.

Correct: α-rename the inner `x` first:

```
= (λz.λy.(z y))[z := (λx.x)]
= λy.(λx.x) y
```

## Beta-Reduction (β)

**β-reduction** is the core computation rule: applying a function to an argument substitutes the argument for the parameter in the body.

```
(λx.M) N →β M[x := N]
```

The expression `(λx.M) N` is called a **β-redex** (reducible expression). The result `M[x := N]` is its **reduct**.

### Examples

Identity:

```
(λx.x) M →β M
```

Constant function (K-combinator):

```
(λx.λy.x) A B →β (λy.A) B →β A
```

Composition:

```
((λfgx.f (g x)) (λa.a+1)) (λb.b*2) 3
→β ((λx.(λa.a+1) (x 3)))
→β (λa.a+1) (3*2)
→β (λa.a+1) 6
→β 7
```

### Beta-Equivalence

Two terms `M` and `N` are **β-equivalent** (`M =β N`) if they can both be reduced to the same term through a sequence of β-reductions (and α-conversions).

## Eta-Conversion (η)

**η-conversion** expresses extensionality: two functions are equal if they produce the same result for all arguments.

```
λx.(M x) →η M    (when x not free in M)
```

And its inverse, **η-expansion**:

```
M →η λx.(M x)    (when x not free in M)
```

Together these form **η-conversion**. It is often omitted in many treatments but is important for reasoning about function equality.

### Example (correct)

```
λx.((λy.y) x) →η (λy.y)
```

### Example (incorrect — would change meaning)

```
λx.(f x) →η f    -- only valid if x not free in f
```

If `f` contained a free `x`, this conversion would be wrong.

## Redexes and Normal Forms

A **redex** is any subterm that can be reduced (by α, β, or η rules). A term with no redexes is in **normal form** (specifically, **β-normal form** if considering only β-reduction).

### Strongly vs. Weakly Normalizing

- **Strongly normalizing**: every possible reduction sequence terminates. The term always reaches a normal form regardless of which redex is reduced first.
- **Weakly normalizing**: at least one reduction sequence terminates, but others may loop forever.

The untyped lambda calculus is neither strongly nor weakly normalizing in general. The term `Ω = (λx.x x)(λx.x x)` has no normal form — it reduces to itself forever:

```
(λx.x x)(λx.x x) →β (λx.x x)(λx.x x) →β ...
```

### Unique Normal Forms

For terms that do have a normal form (strongly or weakly normalizing), the normal form is unique up to α-conversion — guaranteed by the Church-Rosser theorem.

## Confluence and the Church-Rosser Theorem

**Confluence** (the diamond property) means: if a term `M` can reduce to both `N1` and `N2`, then there exists some term `P` that both `N1` and `N2` can reduce to.

The **Church-Rosser theorem** states that β-reduction is confluent (up to α-conversion). This implies:

- If a term has a normal form, it is unique (up to α-equivalence).
- Two terms are β-equivalent if and only if they share a common reduct.
- For strongly normalizing terms, any reduction strategy will find the normal form.
- For weakly normalizing terms, some strategies may fail (loop forever) while others succeed.

## Evaluation Strategies

An **evaluation strategy** determines which redex to reduce when multiple exist.

### Normal Order (outermost / call-by-name)

Always reduce the leftmost-outermost redex first. Arguments are not evaluated before being passed to a function.

```
(λx.y) ((λz.z z)(λz.z z))
→β y    (normal order skips the non-terminating argument)
```

Normal order is optimal: if any reduction strategy finds a normal form, normal order will find it.

### Applicative order (innermost / call-by-value)

Always reduce the leftmost-innermost redex first. Arguments are fully evaluated before being passed to a function.

```
(λx.y) ((λz.z z)(λz.z z))
→β (λx.y) ((λz.z z)(λz.z z))  →β ...  (loops forever)
```

Applicative order is used in most practical languages (Python, OCaml, Standard ML) because it matches the expected evaluation model and enables optimizations.

### Key Difference

- **Call-by-name** (normal order): arguments evaluated at use time, possibly multiple times. May terminate when call-by-value loops.
- **Call-by-value** (applicative order): arguments evaluated once before the function body. More predictable, basis for most real-world languages.
