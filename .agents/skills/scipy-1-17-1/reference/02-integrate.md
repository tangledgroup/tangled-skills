# scipy.integrate - Numerical Integration and ODE Solvers

The `scipy.integrate` module provides tools for numerical integration (quadrature) and solving ordinary differential equations (ODEs).

## Definite Integrals

### 1D Integration

```python
from scipy import integrate
import numpy as np

# Simple definite integral: ∫₀¹ x² dx = 1/3
result = integrate.quad(lambda x: x**2, 0, 1)
print(result[0])  # 0.333... (the integral value)
print(result[1])  # Error estimate

# Multiple integrals
def f(x, y):
    return x * y

result = integrate.dblquad(f, 0, 1, lambda x: 0, lambda x: 1)
```

### Integration with Singularities

```python
# Integrable singularity at x=0
result = integrate.quad(lambda x: np.sqrt(x), 0, 1)

# Specify singular points
def f(x):
    return 1 / np.sqrt(x)

result = integrate.quad(f, 0, 1, points=[0])
```

### Improper Integrals

```python
# Infinite bounds
result = integrate.quad(lambda x: np.exp(-x), 0, np.inf)

# Both bounds infinite
result = integrate.quad(lambda x: 1 / (1 + x**2), -np.inf, np.inf)
```

### Multiple Dimensions

#### Double Integrals

```python
from scipy import integrate

def integrand(y, x):
    return np.exp(-(x**2 + y**2))

# ∫₀¹∫₀¹ exp(-(x²+y²)) dy dx
result = integrate.dblquad(integrand, 0, 1, lambda x: 0, lambda x: 1)
```

#### Triple Integrals

```python
def integrand(z, y, x):
    return x * y * z

# ∫₀¹∫₀ˣ∫₀ʸ xyz dz dy dx
result = integrate.tplquad(integrand, 0, 1, lambda x: 0, lambda x: x, 
                           lambda x, y: 0, lambda x, y: y)
```

### Fixed-Order Quadrature

```python
from scipy import integrate

# Gauss-Kronrod quadrature (fixed number of points)
def f(x):
    return np.sin(x)

result = integrate.fixed_quad(f, -1, 1, n=5)  # 5-point quadrature
```

## Cumulative Integration

### Cumulative Integral

```python
from scipy import integrate
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

# Cumulative integral using trapezoidal rule
Y_cumulative = integrate.cumtrapz(y, x, initial=0)

# Using Simpson's rule (requires odd number of points)
if len(x) % 2 == 0:
    Y_simpson = integrate.cumsimpson(y, x, initial=0)
```

## Ordinary Differential Equations (ODEs)

### Solving Initial Value Problems

#### Using solve_ivp (Recommended)

```python
from scipy import integrate
import numpy as np

# Define the ODE: dy/dt = -2y
def model(t, y):
    return -2 * y

# Time points for solution
t_span = (0, 5)  # Integration interval
t_eval = np.linspace(0, 5, 100)  # Points where to evaluate solution
y0 = [1]  # Initial condition: y(0) = 1

# Solve the ODE
sol = integrate.solve_ivp(model, t_span, y0, t_eval=t_eval)

print(sol.t)   # Time points
print(sol.y)   # Solution values
```

#### System of ODEs

```python
def predator_prey(t, y):
    """Lotka-Volterra equations"""
    x, y = y  # x: prey, y: predator
    alpha, beta, delta, gamma = 1.0, 0.1, 0.02, 2.0
    
    dxdt = alpha * x - beta * x * y
    dydt = delta * x * y - gamma * y
    return [dxdt, dydt]

y0 = [10, 5]  # Initial populations
t_span = (0, 50)
t_eval = np.linspace(0, 50, 500)

sol = integrate.solve_ivp(predator_prey, t_span, y0, t_eval=t_eval)
```

### ODE Solver Methods

| Method | Type | Best For |
|--------|------|----------|
| `RK45` | Explicit Runge-Kutta (4,5) | Non-stiff problems (default) |
| `RK23` | Explicit Runge-Kutta (2,3) | Low accuracy requirements |
| `DOP853` | Explicit Runge-Kutta (8,5,3) | High accuracy requirements |
| `Radau` | Implicit Runge-Kutta | Stiff problems |
| `BDF` | Backward Differentiation Formula | Stiff problems |
| `LSODA` | Automatic stiff/non-stiff switching | Unknown problem type |

### Stiff ODEs

```python
def stiff_ode(t, y):
    return -100 * y  # Stiff: rapid decay

y0 = [1]
t_span = (0, 1)

# Use implicit method for stiff problems
sol = integrate.solve_ivp(stiff_ode, t_span, y0, method='BDF')
# or
sol = integrate.solve_ivp(stiff_ode, t_span, y0, method='Radau')
```

### ODEs with Events

```python
def crossing(t, y):
    return y[0] - 0.5  # Event when y[0] = 0.5

crossing.terminal = True  # Stop integration at event
crossing.direction = -1   # Only detect downward crossings

sol = integrate.solve_ivp(model, t_span, y0, events=crossing)
print(sol.t_events)  # Time when event occurred
```

### ODEs with Parameters

```python
def model_with_params(t, y, k, theta):
    return -k * (y - theta)

y0 = [10]
t_span = (0, 5)
params = (0.5, 2)  # k=0.5, theta=2

sol = integrate.solve_ivp(model_with_params, t_span, y0, args=params)
```

### ODE Solution Object

```python
sol = integrate.solve_ivp(model, t_span, y0, dense_output=True)

# Evaluate at arbitrary points
t_dense = np.linspace(0, 5, 200)
y_dense = sol.sol(t_dense)

# Access solution attributes
print(sol.t)           # Time points
print(sol.y)           # Solution at time points
print(sol.success)     # Boolean: True if successful
print(sol.message)     # Termination message
print(sol.nfev)        # Number of function evaluations
```

## Legacy ODE Solver (odeint)

```python
from scipy import integrate
import numpy as np

def model(y, t):
    return -2 * y  # Note: arguments are reversed from solve_ivp

y0 = [1]
t = np.linspace(0, 5, 100)

sol = integrate.odeint(model, y0, t)
```

## Quadrature of Tabulated Data

### Trapezoidal Rule

```python
from scipy import integrate
import numpy as np

x = np.linspace(0, np.pi, 100)
y = np.sin(x)

# ∫₀^π sin(x) dx ≈ 2
result = integrate.trapz(y, x)
print(result)  # ~2.0
```

### Simpson's Rule (More Accurate)

```python
# Requires odd number of points (even number of intervals)
x = np.linspace(0, np.pi, 101)  # 101 points = 100 intervals
y = np.sin(x)

result = integrate.simpson(y, x)
print(result)  # ~2.0
```

### Boole's Rule (Even More Accurate)

```python
# Requires number of points ≡ 1 (mod 4)
x = np.linspace(0, np.pi, 101)  # 101 = 4*25 + 1
y = np.sin(x)

result = integrate.simpson(y, x, method='boole')
```

## Multiple Integration (n Dimensions)

### Monte Carlo Integration

```python
from scipy import integrate

def f(x, y, z):
    return x * y * z

# ∫₀¹∫₀¹∫₀¹ xyz dx dy dz
result = integrate.nquad(f, [[0, 1], [0, 1], [0, 1]])
```

### Adaptive Quadrature in Higher Dimensions

```python
def integrand(*args):
    x, y, z = args
    return np.exp(-(x**2 + y**2 + z**2))

# Integrate over [-1, 1]³
result = integrate.nquad(integrand, [[-1, 1], [-1, 1], [-1, 1]])
```

## Common Parameters

### quad() Options

```python
result = integrate.quad(f, a, b, 
                       epsabs=1e-9,   # Absolute error tolerance
                       epsrel=1e-9,   # Relative error tolerance
                       limit=50,      # Maximum subintervals
                       points=[c],    # Points where singularities occur
                       full_output=True  # Return additional information
                      )

if full_output:
    print(result[2])  # Information dictionary with details
```

### solve_ivp() Options

```python
sol = integrate.solve_ivp(model, t_span, y0,
                          rtol=1e-6,        # Relative tolerance (default)
                          atol=1e-9,        # Absolute tolerance (default)
                          max_step=None,    # Maximum step size
                          first_step=None,  # Initial step size
                          dense_output=True,  # Compute continuous solution
                          vectorized=False   # Whether f handles vector t
                         )
```

## Troubleshooting

### Integration Fails to Converge

```python
# Increase subintervals and tolerance
result = integrate.quad(f, a, b, limit=200, epsabs=1e-12, epsrel=1e-12)

# Split the integral at problematic points
result1 = integrate.quad(f, a, c)
result2 = integrate.quad(f, c, b)
total = result1[0] + result2[0]
```

### ODE Solver Too Slow

```python
# Use larger tolerances for faster (less accurate) solution
sol = integrate.solve_ivp(model, t_span, y0, rtol=1e-4, atol=1e-6)

# For stiff problems, use implicit methods
sol = integrate.solve_ivp(model, t_span, y0, method='BDF')

# Limit output points and interpolate if needed
sol = integrate.solve_ivp(model, t_span, y0, dense_output=True)
y_at_points = sol.sol(np.linspace(t_span[0], t_span[1], 1000))
```

### Stiff vs Non-Stiff Problems

```python
# Test with different methods to detect stiffness
sol_explicit = integrate.solve_ivp(model, t_span, y0, method='RK45')
sol_implicit = integrate.solve_ivp(model, t_span, y0, method='BDF')

# If explicit method takes much longer or fails, problem is stiff
```

## See Also

- [`scipy.interpolate`](references/03-interpolate.md) - Interpolation-based integration
- [`numpy.trapezoid`](https://numpy.org/doc/stable/reference/generated/numpy.trapezoid.html) - NumPy's trapezoidal rule
- [`sympy.integrate`](https://docs.sympy.org/latest/modules/integrals/integrals.html) - Symbolic integration
