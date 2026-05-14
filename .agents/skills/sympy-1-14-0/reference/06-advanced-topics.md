# Advanced Topics

## Contents
- Simplification Functions
- Power and Logarithm Identities
- Special Functions
- Differential Equations (dsolve)
- Assumptions System
- Physics Modules
- Combinatorics and Number Theory

## Simplification Functions

### `simplify()` — General-Purpose Simplifier

Applies all major simplification operations and picks the "simplest" result by heuristics:

```python
from sympy import simplify, sin, cos, gamma, symbols
x = symbols('x')
simplify(sin(x)**2 + cos(x)**2)          # 1
simplify((x**3 + x**2 - x - 1)/(x**2 + 2*x + 1))  # x - 1
simplify(gamma(x)/gamma(x - 2))          # (x-2)*(x-1)
```

**Caveats**: `simplify()` is heuristic — it may miss simplifications (e.g., does not factor `x**2 + 2*x + 1` into `(x+1)**2`) and can be slow. Use specific functions when you know the type of simplification needed.

### Specific Simplifiers

| Function | Purpose | Example |
|----------|---------|---------|
| `trigsimp()` | Trigonometric identities | `sin(x)**2 + cos(x)**2` → `1` |
| `expand_trig()` | Expand trig (sum/double angle) | `sin(x+y)` → `sin(x)cos(y) + sin(y)cos(x)` |
| `powsimp()` | Combine powers (left-to-right) | `x**a * x**b` → `x**(a+b)` |
| `powdenest()` | Nest powers | `(x**a)**b` → `x**(a*b)` |
| `expand_log()` | Expand logarithms | `log(x*y)` → `log(x) + log(y)` |
| `logcombine()` | Combine logarithms | `log(x) + log(y)` → `log(x*y)` |
| `combsimp()` | Combinatorial simplification | `factorial(n)/factorial(n-3)` → `n*(n-2)*(n-1)` |
| `gammasimp()` | Gamma function simplification | `gamma(x)*gamma(1-x)` → `pi/sin(pi*x)` |
| `hyperexpand()` | Expand hypergeometric functions | `hyper([1,1],[2],z)` → `-log(1-z)/z` |
| `expand_func()` | Expand special functions | `gamma(x+3)` → `x*(x+1)*(x+2)*gamma(x)` |

Most power/log simplifiers respect assumptions and have a `force=True` flag to ignore them.

## Power and Logarithm Identities

SymPy does not apply power identities that are not universally true for complex numbers:

| Identity | Always True? | Example of Failure |
|----------|-------------|-------------------|
| `x**a * x**b = x**(a+b)` | Yes | — |
| `x**a * y**a = (x*y)**a` | No | `sqrt(-1)*sqrt(-1) ≠ sqrt(1)` |
| `(x**a)**b = x**(a*b)` | No | `((-1)**2)**(1/2) ≠ (-1)**1` |

Consequences: `sqrt(x**2) ≠ x` and `sqrt(x)*sqrt(y) ≠ sqrt(x*y)` in general. Use positive assumptions to enable these simplifications:

```python
x, y = symbols('x y', positive=True)
sqrt(x**2)              # x (with positive assumption)
sqrt(x)*sqrt(y)         # sqrt(x*y) (with positive assumptions)
```

In SymPy, `log` is the natural logarithm (`ln`). An alias `ln = log` is provided.

## Special Functions

### Rewrite Between Functions

Any function can be rewritten in terms of another:

```python
from sympy import tan, cos, factorial, gamma, symbols
x = symbols('x')
tan(x).rewrite(cos)              # cos(x - pi/2) / cos(x)
factorial(x).rewrite(gamma)      # gamma(x + 1)
```

### Key Special Functions

| Function | Description |
|----------|-------------|
| `factorial(n)` | n! — permutations of n items |
| `binomial(n, k)` | C(n,k) — "n choose k" |
| `gamma(z)` | Γ(z) — gamma function, generalizes factorial |
| `hyper([a],[b],z)` | Generalized hypergeometric function |
| `meijerg()` | Meijer G-function (used in integration) |
| `besselj(nu, z)` | Bessel function of the first kind |

## Differential Equations (dsolve)

Use `dsolve()` to solve ordinary differential equations symbolically:

```python
from sympy import dsolve, Eq, Function, sin, exp, symbols
t = symbols('t')
f = Function('f')

# f''(x) - 2f'(x) + f(x) = sin(x)
diffeq = Eq(f(t).diff(t, t) - 2*f(t).diff(t) + f(t), sin(t))
dsolve(diffeq, f(t))
# f(t) = (C1 + C2*t)*exp(t) + cos(t)/2

# First order: x - f(x) - cos(f(x)) = C1
dsolve(f(x).diff(x)*(1 - sin(f(x))) - 1, f(x))
```

`dsolve()` returns an `Eq` instance. Arbitrary constants appear as `C1`, `C2`, etc.

### Creating Undefined Functions

```python
from sympy import symbols, Function
f, g = symbols('f g', cls=Function)
f(x)              # f(x) — unknown function
f(x).diff(x)      # d/dx(f(x)) — unevaluated derivative
```

## Assumptions System

Symbols carry assumptions that control which simplifications are applied. By default, symbols are complex with no additional constraints.

```python
from sympy import symbols, ask, Q

x = symbols('x', positive=True)
n = symbols('n', integer=True)
z = symbols('z')  # complex, no extra assumptions

# Query assumptions
x.is_positive      # True
x.is_real          # True (positive implies real)
n.is_integer       # True
z.is_positive      # None (unknown)
```

### Common Assumption Keywords

| Keyword | Meaning |
|---------|---------|
| `positive=True` | Strictly positive real |
| `nonnegative=True` | ≥ 0 |
| `negative=True` | Strictly negative |
| `real=True` | Real number |
| `imaginary=True` | Purely imaginary |
| `integer=True` | Integer |
| `rational=True` | Rational number |
| `finite=True` / `infinite=True` | Finite/infinite value |
| `commutative=False` | Non-commutative (for matrices/operators) |

## Physics Modules

SymPy includes several physics submodules:

### `sympy.physics.mechanics` — Classical Mechanics

Supports Kane's method and Lagrange's method for multibody dynamics. Includes particles, rigid bodies, reference frames, and joints.

```python
from sympy.physics.mechanics import *
# Define reference frames, points, particles
# Build equations of motion using Kane or Lagrange
```

### `sympy.physics.vector` — Vector Mechanics

Symbolic vector algebra with reference frames, kinematics, and field operations.

### `sympy.physics.quantum` — Quantum Mechanics

Dirac notation, operators, Hilbert spaces, and tensor products.

### `sympy.physics.control` — Control Systems

State-space models, transfer functions, and system analysis for control theory.

### `sympy.physics.continuum_mechanics` — Continuum Mechanics

Beam bending problems using singularity functions.

## Combinatorics and Number Theory

### Combinatorics (`sympy.combinatorics`)

- **Permutations**: `Permutation` class for symmetric group operations
- **Permutation Groups**: `PermutationGroup` with generators, order, cosets
- **Partitions**: Integer partitions, set partitions
- **Polyhedra**: Symmetric polyhedron operations
- **Gray Codes**: Gray code generation
- **Subsets**: Subset iteration and enumeration

### Number Theory (`sympy.ntheory`)

- Prime testing, factorization, primorials
- Euler's totient, divisor functions
- Modular arithmetic, discrete logarithms
- Continued fractions
- Partitions and partition generating functions
