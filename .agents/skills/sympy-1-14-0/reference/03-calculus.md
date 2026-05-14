# Calculus

## Contents
- Derivatives
- Integrals
- Limits
- Series Expansions
- Finite Differences
- Numeric Integration

## Derivatives

Use `diff()` for symbolic differentiation. Call as a function or method.

```python
from sympy import diff, symbols, exp, cos
x, y, z = symbols('x y z')

# Single derivative
diff(cos(x), x)              # -sin(x)
diff(exp(x**2), x)           # 2*x*exp(x**2)

# Higher-order derivatives
diff(x**4, x, x, x)          # 24*x
diff(x**4, x, 3)             # 24*x (same, using count syntax)

# Mixed partial derivatives
expr = exp(x*y*z)
diff(expr, x, y, 2, z, 4)   # ∂⁷/(∂x∂y²∂z⁴) e^(xyz)

# Method form (identical)
expr.diff(x, y, 2, z, 4)
```

### Unevaluated Derivatives

Use `Derivative` to create unevaluated derivative objects:

```python
from sympy import Derivative
deriv = Derivative(expr, x, y, 2, z, 4)
# Displays as ∂⁷/(∂z⁴∂y²∂x) e^(xyz)
deriv.doit()  # evaluates to the computed result
```

Useful for delaying evaluation, printing, or when SymPy cannot compute the derivative (e.g., undefined functions).

### Derivatives of Unspecified Order

```python
from sympy import symbols
m, a, b = symbols('m n a b')
x = symbols('x')
n = symbols('n')
expr = (a*x + b)**m
expr.diff((x, n))  # ∂ⁿ/(∂xⁿ) (ax + b)^m
```

## Integrals

Use `integrate()` for symbolic integration. Supports indefinite, definite, and multiple integrals.

```python
from sympy import integrate, symbols, exp, sin, oo
x, y = symbols('x y')

# Indefinite integral
integrate(cos(x), x)                     # sin(x)

# Definite integral
integrate(exp(-x), (x, 0, oo))           # 1

# Multiple integral
integrate(exp(-x**2 - y**2), (x, -oo, oo), (y, -oo, oo))  # pi

# Parametric integral with convergence conditions
integrate(x**y * exp(-x), (x, 0, oo))    # Piecewise: Gamma(y+1) for Re(y) > -1
```

### Unevaluated Integrals

When `integrate()` cannot find a closed form, it returns an unevaluated `Integral` object:

```python
from sympy import Integral
expr = integrate(x**x, x)                # Integral(x**x, x) — unevaluated
expr = Integral(log(x)**2, x)
expr.doit()                               # x*log(x)**2 - 2*x*log(x) + 2*x
```

### Numeric Integration

Evaluate integrals numerically using `.evalf()`:

```python
from sympy import Integral, sqrt
x = symbols('x')
Integral(sqrt(2)*x, (x, 0, 1)).evalf()           # 0.707106781186548
Integral(sqrt(2)*x, (x, 0, 1)).evalf(50)         # 50-digit precision
Integral(exp(-x**2), (x, -oo, oo)).evalf()        # 1.77245385090552
```

Numeric integration works even when symbolic integration fails, including infinite intervals and singular integrands.

## Limits

Use `limit()` for symbolic limits. Use instead of `.subs()` at singularities.

```python
from sympy import limit, symbols, sin, exp, oo
x = symbols('x')

limit(sin(x)/x, x, 0)                 # 1
limit(x**2/exp(x), x, oo)             # 0

# One-sided limits
limit(1/x, x, 0, '+')                 # oo
limit(1/x, x, 0, '-')                 # -oo
```

**Important**: Do not use `.subs(x, oo)` for limits — it produces `nan` for indeterminate forms. `limit()` properly handles growth rates.

### Unevaluated Limits

```python
from sympy import Limit
expr = Limit((cos(x) - 1)/x, x, 0)
# Displays as lim (cos(x)-1)/x as x→0⁺
expr.doit()                            # 0
```

## Series Expansions

Compute asymptotic series with `.series()`:

```python
from sympy import exp, sin, symbols
x = symbols('x')

exp(sin(x)).series(x, 0, 4)
# 1 + x + x**2/2 + O(x**4)
```

Syntax: `expr.series(variable, point, order)`. Defaults: `point=0`, `order=6`.

### Order Terms (`O`)

The trailing `O(x⁴)` represents the Landau order term — all terms of power ≥ 4 are omitted. Order terms can be manipulated:

```python
x + x**3 + x**6 + O(x**4)    # x + x**3 + O(x**4)
x * O(1)                      # O(x)
```

Remove order term with `.removeO()`:

```python
exp(sin(x)).series(x, 0, 4).removeO()
# x**2/2 + x + 1
```

### Series Around Arbitrary Points

```python
exp(x - 6).series(x, x0=6)
# e^(-5) * (1 + (x-6) + (x-6)**2/2 + ...)
```

## Finite Differences

Approximate derivatives using finite difference methods:

```python
from sympy import symbols, Function, differentiate_finite, finite_diff_weights
f, g = symbols('f g', cls=Function)
x = symbols('x')

# Basic finite difference
differentiate_finite(f(x)*g(x))
# -f(x-1/2)*g(x-1/2) + f(x+1/2)*g(x+1/2)

# From Derivative object
dfdx = f(x).diff(x)
dfdx.as_finite_difference()                    # -f(x-1/2) + f(x+1/2)

# With custom step sizes
h = symbols('h')
d2fdx2 = f(x).diff(x, 2)
d2fdx2.as_finite_difference([-3*h, -h, 2*h])

# Direct weight computation
finite_diff_weights(2, [-3, -1, 2], 0)[-1][-1]
# [1/5, -1/3, 2/15]
```
