---
name: sympy-1-14-0
description: Complete toolkit for SymPy 1.14.0 providing symbolic mathematics in Python including algebra, calculus, matrices, equation solving, simplification, and printing. Use when building Python programs that require exact symbolic computation, symbolic expression manipulation, analytical differentiation/integration, equation solving, or mathematical typesetting via LaTeX output.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - sympy
  - symbolic-math
  - computer-algebra
  - python
  - mathematics
category: library
external_references:
  - https://docs.sympy.org/latest/index.html
  - https://github.com/sympy/sympy/tree/sympy-1.14.0
---

# SymPy 1.14.0

## Overview

SymPy is a Python library for symbolic mathematics. Unlike numerical libraries (NumPy, SciPy), SymPy represents mathematical objects exactly — not approximately — and manipulates expressions with unevaluated variables in symbolic form. It is written entirely in Python with no external dependencies beyond Python itself.

SymPy supports: algebraic manipulation, calculus (derivatives, integrals, limits, series), equation solving (algebraic, ODE, systems), matrix operations, simplification, combinatorics, number theory, geometry, physics, plotting, code generation, and mathematical printing (LaTeX, ASCII, Unicode).

## When to Use

- Building Python programs that require exact symbolic computation instead of floating-point arithmetic
- Manipulating mathematical expressions symbolically (expand, factor, substitute)
- Computing derivatives, integrals, limits, or series expansions analytically
- Solving algebraic equations, systems of equations, or differential equations
- Working with symbolic matrices and linear algebra
- Generating LaTeX output for mathematical formulas
- Any task where approximate numerical results are insufficient

## Core Concepts

### Symbols Must Be Declared

Unlike standalone CAS, SymPy does not auto-declare variables. Define symbols explicitly:

```python
from sympy import symbols
x, y, z = symbols('x y z')
expr = x**2 + 2*y
```

### Immutability

All SymPy expressions are immutable. Operations return new objects — nothing modifies in place:

```python
expr = x + 1
expr.subs(x, 3)  # returns 4, does not change expr
# expr is still x + 1
```

Exception: `Matrix` objects are mutable. Use `ImmutableMatrix` when immutability is required.

### Python Syntax, Not Mathematical Syntax

- Use `**` for exponentiation, not `^` (which is XOR in Python)
- Use `*` for explicit multiplication — implicit multiplication like `3x` is invalid
- Use `Eq(a, b)` for symbolic equality, not `==` (which tests structural equality)
- Expressions assumed equal to zero can omit `Eq`: `solveset(x**2 - 1, x)` solves `x² = 1`
- Python division `/` produces floats; use `Rational(1, 2)` for exact rationals

### Expression Trees

Every expression is a tree of `Add`, `Mul`, `Pow`, and function nodes. Inspect with:

```python
from sympy import srepr
srepr(x**2 + x*y)
# "Add(Pow(Symbol('x'), Integer(2)), Mul(Symbol('x'), Symbol('y')))"
```

Every expression satisfies the key invariant: `expr == expr.func(*expr.args)` or has empty `args` (leaf node).

### Assumptions on Symbols

By default, symbols are complex. Attach assumptions to enable simplifications:

```python
x = symbols('x', positive=True)
y = symbols('y', real=True)
n = symbols('n', integer=True)
```

## Usage Examples

```python
from sympy import *

# Define symbols
x, y, t = symbols('x y t')

# Symbolic expressions
expr = sin(x)**2 + cos(x)**2
simplify(expr)  # 1

# Derivatives
diff(exp(x**2), x)  # 2*x*exp(x**2)

# Integrals
integrate(exp(-x), (x, 0, oo))  # 1

# Limits
limit(sin(x)/x, x, 0)  # 1

# Equation solving
solveset(x**2 - 2, x)  # {-sqrt(2), sqrt(2)}

# Differential equations
f = Function('f')
dsolve(Eq(f(t).diff(t, t) - f(t), exp(t)), f(t))

# Matrices
M = Matrix([[1, 2], [3, 4]])
M.eigenvals()  # {2 - sqrt(5)/2: 1, 2 + sqrt(5)/2: 1}

# LaTeX output
latex(Integral(cos(x)**2, (x, 0, pi)))
# '\int\limits_{0}^{\pi} \cos^{2}{\left(x \right)}\, dx'

# Series expansion
exp(sin(x)).series(x, 0, 4)  # 1 + x + x**2/2 + O(x**4)
```

## Advanced Topics

**Core Expressions**: Symbols, expression trees, substitution, immutability, and evaluation → [Core Expressions](reference/01-core-expressions.md)

**Algebra**: Polynomial manipulation, equation solving, factorization, roots → [Algebra](reference/02-algebra.md)

**Calculus**: Differentiation, integration, limits, series expansions, finite differences → [Calculus](reference/03-calculus.md)

**Matrices**: Construction, operations, eigenvalues, RREF, nullspace, diagonalization → [Matrices](reference/04-matrices.md)

**Printing and Output**: LaTeX, ASCII/Unicode pretty-print, code generation, MathML → [Printing and Output](reference/05-printing-and-output.md)

**Advanced Topics**: Physics modules, combinatorics, special functions, assumptions system, ODE solving → [Advanced Topics](reference/06-advanced-topics.md)
