---
name: python-lambda-calculus-3-1-0
description: Python library implementing Lambda calculus operations including term construction (Variable, Abstraction, Application), beta/eta reduction, alpha conversion, substitution, and visitor-based traversal. Provides Church encodings for booleans, arithmetic, pairs, and common combinators (Y, S, K, I). Use when building lambda calculus interpreters, performing symbolic term manipulation, encoding computation in pure lambda terms, or teaching functional programming concepts with Python.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - lambda-calculus
  - lambda-calculus-3-1-0
  - functional-programming
  - symbolic-computation
  - church-encoding
category: library
external_references:
  - https://pypi.org/project/lambda-calculus/
  - https://github.com/Deric-W/lambda_calculus/tree/v3.1.0
  - https://lambda-calculus.readthedocs.io/en/stable/index.html
---

# lambda_calculus 3.1.0

## Overview

`lambda_calculus` is a pure Python library implementing the core operations of Lambda calculus as an educational tool. It provides three fundamental term types — `Variable`, `Abstraction`, and `Application` — along with visitor-based traversal, beta/eta reduction, alpha conversion, and safe substitution. The library includes Church encodings for booleans, arithmetic, pairs, and well-known combinators (Y, S, K, I, B, C, W).

It is not optimized for speed and expects all terms to be finite. Infinite terms or excessively complex evaluations may raise `RecursionError`.

## When to Use

- Building lambda calculus interpreters or evaluators in Python
- Performing symbolic manipulation of lambda terms (substitution, reduction, variable analysis)
- Encoding computation using Church encodings (booleans, numbers, pairs)
- Teaching functional programming concepts with executable examples
- Implementing custom term transformations via the visitor pattern

## Installation

```bash
python3 -m pip install lambda-calculus
```

## Core Concepts

### Three Term Types

Every lambda expression is built from three constructors:

| Type | Lambda Notation | Python Class |
|------|----------------|--------------|
| Variable | `x` | `Variable("x")` |
| Abstraction | `λx.M` | `Abstraction("x", M)` |
| Application | `(M N)` | `Application(M, N)` |

### Building Terms

```python
from lambda_calculus import Variable, Abstraction, Application

# λx.x (identity)
identity = Variable("x").abstract("x")

# λx.λy.x (K combinator)
k = Variable("x").abstract("x", "y")

# Apply identity to a variable
app = identity.apply_to(Variable("a"))
```

Use `.abstract(*vars)` on any term to bind variables, and `.apply_to(*args)` to create applications. For multiple bindings/arguments, pass them positionally — they are curried from first to last.

### Analyzing Terms

```python
term = Abstraction.curried(("x", "y"), Application(Variable("x"), Variable("z")))

term.free_variables()     # {"z"}
term.bound_variables()    # {"x", "y"}
term.is_combinator()      # False (has free variable "z")
term.is_beta_normal_form()  # True
```

### Reducing Terms

```python
# Create a redex: (λx.x) a
redex = Application(identity, Variable("a"))
redex.is_redex()           # True
reduced = redex.beta_reduction()  # Variable("a")

# Full beta-normalization via visitor
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor
visitor = BetaNormalisingVisitor()
for conversion, intermediate in visitor.visit(some_term):
    print(f"{conversion}: {intermediate}")
```

### Substitution with Collision Safety

```python
# Safe substitution — raises CollisionError if free variables would be captured
term.substitute("x", replacement_term)

# Manual alpha conversion before substitution
new_abs = abstraction.alpha_conversion("z")  # rename bound variable
```

## Advanced Topics

**Terms API**: Term base class, Variable, Abstraction, Application with all methods → [Terms API](reference/01-terms-api.md)

**Visitors API**: Visitor pattern, substitution strategies, beta normalization, term traversal → [Visitors API](reference/02-visitors-api.md)

**Predefined Constructs**: Church booleans, arithmetic, pairs, combinators, letter variables → [Predefined Constructs](reference/03-predefined-constructs.md)
