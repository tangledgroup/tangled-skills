# Algebra

## Contents
- Polynomial Simplification
- Equation Solving with solveset
- Systems of Equations
- Roots and Multiplicity
- Partial Fractions

## Polynomial Simplification

### `expand()` — Expand Products into Sums

```python
from sympy import expand, symbols
x, y = symbols('x y')
expand((x + 1)**2)           # x**2 + 2*x + 1
expand((x + 2)*(x - 3))      # x**2 - x - 6
```

Also expands trigonometric and other functions when combined with flags. Can produce cancellation that shrinks expressions:

```python
expand((x + 1)*(x - 2) - (x - 1)*x)  # -2
```

### `factor()` — Factor into Irreducible Polynomials

```python
from sympy import factor
factor(x**3 - x**2 + x - 1)              # (x - 1)*(x**2 + 1)
factor(x**2*z + 4*x*y*z + 4*y**2*z)      # z*(x + 2*y)**2
```

Guaranteed to factor completely over the rationals for polynomials. Opposite of `expand()`.

### `cancel()` — Canonical Form for Rational Functions

Puts rational expressions into standard `p/q` form with expanded polynomials and no common factors:

```python
from sympy import cancel
cancel((x**2 + 2*x + 1)/(x**2 + x))       # (x + 1)/x
cancel(1/x + (3*x/2 - 2)/(x - 4))         # (3*x**2/2 - 2*x - 8)/(2*x**2 - 8*x)
```

More efficient than `factor()` when only cancellation is needed.

### `collect()` — Group by Powers of a Term

```python
from sympy import collect
expr = x*y + x - 3 + 2*x**2 - z*x**2 + x**3
collected = collect(expr, x)
# x**3 + x**2*(2 - z) + x*(y + 1) - 3
collected.coeff(x, 2)  # 2 - z
```

### `factor_list()` — Structured Factor Output

Returns `(coeff, [(factor1, multiplicity1), ...])`:

```python
from sympy import factor_list
factor_list(x**2*z + 4*x*y*z + 4*y**2*z)
# (1, [(z, 1), (x + 2*y, 2)])
```

## Equation Solving with solveset

`solveset` is the preferred solver for single-variable algebraic equations. It returns sets of solutions.

```python
from sympy import solveset, symbols, sin, S
x = symbols('x')

# Polynomial
solveset(x**2 - x, x)                    # {0, 1}

# Tautology (all reals)
solveset(x - x, x, domain=S.Reals)       # ℝ

# Trigonometric
solveset(sin(x) - 1, x, domain=S.Reals)  # {2*n*pi + pi/2 | n ∈ ℤ}

# No solution
solveset(exp(x), x)                       # ∅

# Unable to find closed form
solveset(cos(x) - x, x)                  # ConditionSet
```

**Syntax**: `solveset(equation, variable, domain=S.Complexes)`

Equations can be passed as expressions (assumed equal to 0), or as `Eq(left, right)`.

```python
solveset(x**2 - 1, x)          # same as solveset(Eq(x**2, 1), x)
# {-1, 1}
```

### Return Types

| Result | Meaning |
|--------|---------|
| `FiniteSet` | Discrete set of solutions |
| `Interval` | Continuous range of solutions |
| `ImageSet` | Parametric family of solutions (e.g., trig) |
| `EmptySet` | No solutions exist |
| `ConditionSet` | Solver could not find explicit solutions |

## Systems of Equations

### Linear Systems — `linsolve`

```python
from sympy import linsolve, symbols
x, y, z = symbols('x y z')

# List of equations (assumed = 0)
linsolve([x + y + z - 1, x + y + 2*z - 3], (x, y, z))
# {(-y - 1, y, 2)}

# Augmented matrix form
from sympy import Matrix
linsolve(Matrix(([1, 1, 1, 1], [1, 1, 2, 3])), (x, y, z))
# {(-y - 1, y, 2)}
```

Solution order corresponds to the order of given symbols. Free variables appear in the solution.

### Nonlinear Systems — `nonlinsolve`

```python
from sympy import nonlinsolve, symbols, exp, sin
x, y = symbols('x y')

nonlinsolve([x*y - 1, x - 2], [x, y])        # {(2, 1/2)}
nonlinsolve([x**2 + 1, y**2 + 1], [x, y])    # complex solutions
nonlinsolve([x*y, x*y - x], [x, y])          # {(0, y)} — positive-dimensional
```

**Limitations**: `nonlinsolve` does not return LambertW-form solutions and has limited trigonometric system support. Fall back to `solve()` for those cases:

```python
from sympy import solve
solve(x*exp(x) - 1, x)           # [LambertW(1)]
solve([sin(x + y), cos(x - y)], [x, y])  # trig system
```

## Roots and Multiplicity

`solveset` reports each solution once. Use `roots()` to include multiplicity:

```python
from sympy import roots
solveset(x**3 - 6*x**2 + 9*x, x)  # {0, 3}
roots(x**3 - 6*x**2 + 9*x, x)     # {0: 1, 3: 2}
```

Output `{0: 1, 3: 2}` means root 0 has multiplicity 1, root 3 has multiplicity 2.

## Partial Fractions

`apart()` performs partial fraction decomposition:

```python
from sympy import apart
expr = (4*x**3 + 21*x**2 + 10*x + 12)/(x**4 + 5*x**3 + 5*x**2 + 4*x)
apart(expr)
# (2*x - 1)/(x**2 + x + 1) - 1/(x + 4) + 3/x
```
