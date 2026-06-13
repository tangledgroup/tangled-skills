# Integration (scipy.integrate)

## Numerical Quadrature

### Single Integral (quad)

`quad` integrates a function of one variable between two points. Supports infinite limits via `np.inf`. Returns a tuple of `(result, error_estimate)`.

```python
from scipy import integrate, special
import numpy as np

# Integrate Bessel function J_2.5 from 0 to 4.5
result = integrate.quad(lambda x: special.jv(2.5, x), 0, 4.5)
print(result)  # (1.1178..., 7.87e-09)
```

Pass additional parameters via `args`:

```python
def integrand(x, a, b):
    return a * x**2 + b

I = integrate.quad(integrand, 0, 1, args=(2, 1))
print(I)  # (1.6667..., 1.85e-14)
```

Infinite limits:

```python
# Exponential integral E_n(x) = integral from 1 to inf of exp(-xt)/t^n dt
def integrand(t, n, x):
    return np.exp(-x * t) / t**n

result = integrate.quad(integrand, 1, np.inf, args=(3, 2.0))
```

**Warning**: Adaptive quadrature samples at finite points. For functions concentrated in small regions (e.g., Gaussian over large interval), use tight limits:

```python
# Good: integrate.quad(gaussian, -15, 15)
# Bad: integrate.quad(gaussian, -10000, 10000)  # returns ~0!
```

### Multiple Integration

`dblquad`, `tplquad`, and `nquad` handle multi-dimensional integration:

```python
from scipy.integrate import dblquad, nquad
import numpy as np

# Double integral with variable inner limits
area = dblquad(lambda x, y: x*y, 0, 0.5,
               lambda x: 0, lambda x: 1 - 2*x)

# N-fold integration
def f(t, x):
    return np.exp(-x * t) / t**5

result = integrate.nquad(f, [[1, np.inf], [0, np.inf]])
```

### Other Quadrature Functions

- `romberg`: Romberg integration
- `fixed_quad`: Fixed-order Gaussian quadrature
- `quasi_monte_carlo`: Quasi-Monte Carlo integration
- `monte_carlo`: Monte Carlo integration
- `nquad`: N-dimensional integration

## Ordinary Differential Equations

### Initial Value Problems (solve_ivp)

`solve_ivp` is the recommended interface for solving initial value problems:

```python
from scipy.integrate import solve_ivp
import numpy as np

def lotka_volterra(t, y, alpha=1.5, beta=1.0, delta=3.0, gamma=1.0):
    """Lotka-Volterra equations for predator-prey dynamics."""
    return [alpha*y[0] - beta*y[0]*y[1],
            -delta*y[1] + gamma*y[0]*y[1]]

sol = solve_ivp(lotka_volterra, [0, 10], [10, 5],
                method='RK45', t_eval=np.linspace(0, 10, 100))
```

**Available methods**:
- `RK45`: Explicit Runge-Kutta (4,5) — default, good for non-stiff problems
- `RK23`: Explicit Runge-Kutta (2,3) — lower overhead
- `Radau`: Implicit Runge-Kutta — stiff problems
- `BDF`: Backward Differentiation Formula — stiff problems, supports Jacobian
- `DOP853`: Dormand-Prince (8,9) — high accuracy
- `LSODA`: Automatic stiffness detection (ported from Fortran77 to C in 1.17)

### Event Detection

Detect events during integration:

```python
def zero_crossing(t, y):
    return y[0] - 0.5
zero_crossing.terminal = True  # stop integration when event occurs
zero_crossing.direction = -1   # only detect decreasing crossings

sol = solve_ivp(lotka_volterra, [0, 10], [10, 5], events=zero_crossing)
```

### Legacy ODE Interface (ode)

The `ode` class provides access to LSODA, VODE, and ZVODE integrators with callback-based interfaces. `vode` and `zvode` were ported from Fortran77 to C in 1.17.

## Boundary Value Problems (solve_bvp)

Solves two-point boundary value problems for ODEs:

```python
from scipy.integrate import solve_bvp
import numpy as np

def fun(x, y):
    return np.vstack((y[1], -x*y[0]))

def bc(ya, yb):
    return np.array([ya[0], yb[0] - 1.0])

x = np.linspace(0, 1, 5)
y = np.zeros((2, x.size))
sol = solve_bvp(fun, bc, x, y)
```

## Dense Output

For smooth interpolation of the solution between time steps, use dense output:

```python
sol = solve_ivp(lotka_volterra, [0, 10], [10, 5], method='RK45')
# Evaluate solution at arbitrary points
y_at_3 = sol.sol(3.0)
```
