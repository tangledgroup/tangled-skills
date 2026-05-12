---
name: lambda-calculus-2026-05-12
description: Formal system for expressing computation via function abstraction and application. Covers untyped lambda calculus (syntax, reduction, Church encoding), typed variants (STLC, System F), currying, and the Curry-Howard isomorphism. Use when reasoning about functions, understanding functional programming foundations, type theory, proof assistants, or implementing interpreters and compilers for functional languages.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - lambda-calculus
  - functional-programming
  - type-theory
  - church-encoding
  - currying
  - curry-howard
  - formal-systems
category: language-runtime
external_references:
  - https://en.wikipedia.org/wiki/Lambda_calculus
  - https://en.wikipedia.org/wiki/Lambda_calculus_definition
  - https://en.wikipedia.org/wiki/Typed_lambda_calculus
  - https://en.wikipedia.org/wiki/Simply_typed_lambda_calculus
  - https://en.wikipedia.org/wiki/Currying
  - https://en.wikipedia.org/wiki/Fixed-point_combinator
---

# Lambda Calculus

## Overview

The lambda calculus (λ-calculus) is a formal system for expressing computation based on function abstraction and application using variable binding and substitution. Introduced by Alonzo Church in the 1930s, the untyped lambda calculus is Turing complete — it can simulate any Turing machine and vice versa. It serves as the theoretical foundation for functional programming languages (Scheme, Haskell, ML) and connects to logic via the Curry-Howard isomorphism, where types represent propositions and terms represent proofs.

Lambda calculus treats functions as anonymous, first-class values that take exactly one argument. Multi-argument functions are handled through currying, which transforms them into chains of single-argument functions. The system is minimal: all computation arises from just three constructs — variables, abstractions, and applications — manipulated by reduction rules.

## When to Use

- Understanding the foundations of functional programming languages
- Reasoning about function behavior, substitution, and evaluation strategies
- Working with type theory, type systems, or proof assistants (Coq, Agda)
- Implementing interpreters, compilers, or evaluators for functional languages
- Studying the Curry-Howard correspondence between logic and computation
- Encoding data types and arithmetic in pure function-based systems

## Core Concepts

### Three Term Forms

Every lambda term is built from exactly three rules:

1. **Variable** — a name like `x`, `y`, `z`. Represents a parameter or free value.
2. **Abstraction** — `λx.M` defines an anonymous function taking parameter `x` with body `M`. The λ binds `x` in `M`.
3. **Application** — `(M N)` applies function `M` to argument `N`.

In BNF:

```
<term> ::= <var>
         | λ <var> . <term>
         | ( <term> <term> )
```

### Free and Bound Variables

A variable occurrence is **bound** if it falls within the scope of a λ that binds it. Otherwise it is **free**. A term with no free variables is called **closed** (a combinator).

- In `λx.x y`, the first `x` is bound, but `y` is free.
- In `λx.λy.x`, both `x` and `y` are bound — this is closed.

### Notation Conventions

- **Left-associative application**: `M N P` means `((M N) P)`.
- **Abstraction extends rightward**: `λx.M N` means `λx.(M N)`, not `(λx.M) N`.
- **Multiple abstractions contracted**: `λx.λy.M` abbreviated as `λxy.M`.
- **Outer parentheses dropped**: write `λx.x` instead of `(λx.x)`.

### Beta-Reduction (Function Application)

The core computation rule: applying a function substitutes the argument for the parameter in the body.

```
(λx.M) N →β M[x := N]
```

Example — the identity function applied to any term returns that term:

```
(λx.x) y →β y
```

Example — a constant function ignores its input:

```
((λx.λy.x) a) b →β (λy.a) b →β a
```

### Currying

Lambda calculus functions take exactly one argument. Multi-argument functions are encoded as chains of single-argument functions:

```
f(x, y) becomes λx.λy.body
f(a, b) becomes ((λx.λy.body) a) b
```

This technique, called currying, transforms a function of multiple arguments into a sequence of functions each taking one argument. It is fundamental to functional programming languages like Haskell and ML, where all functions are curried by default.

### Typed vs. Untyped

The **untyped** lambda calculus is Turing complete but allows non-terminating computations. **Typed** variants (e.g., simply typed lambda calculus) restrict expressiveness in exchange for guarantees: every well-typed term is guaranteed to terminate (strong normalization), and types serve as logical propositions via the Curry-Howard isomorphism.

### Recursion and Fixed-Point Combinators

Lambda calculus has no named functions — a term cannot refer to itself by name. This makes recursion impossible through simple self-reference. **Fixed-point combinators** solve this problem.

A fixed point of function `f` is a value where `f x = x`. A **fixed-point combinator** is a higher-order function that, given any `f`, returns one of its fixed points:

```
Y f →β f (Y f)
```

This equation means: applying `Y` to `f` produces the same result as applying `f` to `(Y f)` — effectively giving `f` a way to call itself without a name. This is how recursion works in pure lambda calculus.

The most famous fixed-point combinator is the **Y combinator**:

```
Y = λf.(λx.f (x x)) (λx.f (x x))
```

In call-by-value (strict) languages, Y loops immediately. The **Z combinator** adds an η-expansion to delay evaluation:

```
Z = λf.(λx.f (λv.x x v)) (λx.f (λv.x x v))
```

Fixed-point combinators cannot be typed in simply typed lambda calculus — they would violate strong normalization. Typed systems that need recursion add an explicit `fix` operator instead.

## Usage Examples

### Identity and Composition

```
ID   = λx.x
COMP = λfgx.(f (g x))
```

Composition applied: `COMP (λx.x) ID` reduces to `λx.ID x`, which is equivalent to `ID`.

### Church Numeral: Adding Two and Three

```
0  = λfx.x
1  = λfx.f x
2  = λfx.f (f x)
3  = λfx.f (f (f x))
PLUS = λmnfx.m f (n f x)

PLUS 2 3 →β 5 (= λfx.f (f (f (f (f x)))))
```

### Church Booleans: AND TRUE FALSE

```
TRUE  = λxy.x
FALSE = λxy.y
AND   = λp.q.p q p

AND TRUE FALSE →β FALSE
```

## Advanced Topics

**Reduction and Evaluation**: Alpha/beta/eta conversion, substitution, normal forms, confluence, evaluation strategies (call-by-name, call-by-value) → [Reduction and Evaluation](reference/01-reduction-and-evaluation.md)

**Church Encoding**: Encoding natural numbers, Booleans, pairs, lists, and recursion as pure lambda terms → [Church Encoding](reference/02-church-encoding.md)

**Typed Lambda Calculus**: Simply typed lambda calculus, typing rules, strong normalization, System F, Curry-Howard isomorphism → [Typed Lambda Calculus](reference/03-typed-lambda-calculus.md)

**Currying and Application**: Formal currying/uncurrying, contrast with partial application, role in functional programming and category theory → [Currying and Application](reference/04-currying-and-application.md)
