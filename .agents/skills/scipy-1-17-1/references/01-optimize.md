# scipy.optimize - Optimization and Root-Finding

The `scipy.optimize` module provides optimization algorithms and root-finding methods for scalar, multivariate, and constrained problems.

## Function Minimization

### Unconstrained Minimization

#### Scalar Minimization

```python
from scipy.optimize import minimize_scalar

def f(x):
    return (x - 2) ** 2

# Bracketing method
result = minimize_scalar(f, bracket=(0, 2, 4))
print(result.x)  # 2.0

# Bounded method
result = minimize_scalar(f, bounds=(0, 5), method='bounded')
```

#### Multivariate Minimization

```python
from scipy.optimize import minimize
import numpy as np

def rosen(x):
    """Rosenbrock function"""
    return sum(100.0*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)

x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])

# Nelder-Mead (derivative-free)
res_nm = minimize(rosen, x0, method='Nelder-Mead')

# BFGS (requires gradient for best performance)
res_bfgs = minimize(rosen, x0, method='BFGS')

# L-BFGS-B (supports bounds)
bounds = [(0, None)] * 5  # Lower bound of 0 for all variables
res_lsb = minimize(rosen, x0, method='L-BFGS-B', bounds=bounds)
```

#### Method Selection Guide

| Method | Gradient Required | Bounds | Constraints | Best For |
|--------|-------------------|--------|-------------|----------|
| `Nelder-Mead` | No | No | No | Non-smooth functions |
| `BFGS` | Recommended | No | No | Smooth functions |
| `L-BFGS-B` | Recommended | Yes | No | Large problems with bounds |
| `TNC` | Recommended | Yes | No | Functions with noisy gradients |
| `SLSQP` | Recommended | Yes | Yes | Constrained optimization |
| `trust-constr` | Recommended | Yes | Yes | Complex constraints |

### Constrained Minimization

```python
from scipy.optimize import minimize
import numpy as np

def objective(x):
    return x[0]**2 + x[1]**2

# Initial guess
x0 = [1, 1]

# Constraints: x[0] + x[1] >= 1 (inequality)
cons = ({'type': 'ineq', 'fun': lambda x: x[0] + x[1] - 1})

# Bounds
bounds = [(0, None), (0, None)]

result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=cons)
```

### Linear Programming

```python
from scipy.optimize import linprog

# Minimize: -3x + 2y - z
c = [-3, 2, -1]

# Subject to:
# x + y + z <= 4
# 2x - y + 3z >= 2  (converted to -2x + y - 3z <= -2)
A_ub = [[1, 1, 1], [-2, 1, -3]]
b_ub = [4, -2]

# Variable bounds: x >= 0, y >= 0, z >= 0
x_bounds = (0, None)
bounds = [x_bounds, x_bounds, x_bounds]

result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
print(result.x)  # Optimal values
```

## Root-Finding

### Scalar Functions

```python
from scipy.optimize import root_scalar, brentq, bisect

def f(x):
    return x**2 - 4  # Root at x = 2

# Using bracketing (requires sign change)
result = root_scalar(f, bracket=[1, 3], method='brentq')
print(result.root)  # 2.0

# Alternative methods
root_bisect = brentq(f, 1, 3)
root_bisect = bisect(f, 1, 3)
```

### Systems of Equations

```python
from scipy.optimize import root

def equations(vars):
    x, y = vars
    return [
        x * np.exp(y) - 2,
        y * np.exp(x) - 3
    ]

x0 = [1, 1]
result = root(equations, x0, method='hybr')
print(result.x)  # Solution
```

## Curve Fitting

### Nonlinear Least Squares

```python
from scipy.optimize import curve_fit
import numpy as np

def model(x, a, b, c):
    return a * np.exp(-b * x) + c

# Generate sample data
x_data = np.linspace(0, 4, 50)
y_data = model(x_data, 2.5, 1.3, 0.5) + np.random.normal(0, 0.1, 50)

# Fit the model
popt, pcov = curve_fit(model, x_data, y_data)
print(f"Fitted parameters: {popt}")

# With parameter bounds
popt, pcov = curve_fit(model, x_data, y_data, bounds(([0, 0, 0], [np.inf, np.inf, np.inf]))
```

### Bounded Least Squares

```python
from scipy.optimize import least_squares

def residuals(params, x, y):
    a, b, c = params
    return a * np.exp(-b * x) + c - y

p0 = [1, 1, 1]
result = least_squares(residuals, p0, args=(x_data, y_data), bounds(([0, 0, 0], [np.inf, np.inf, np.inf]))
```

## Global Optimization

### Differential Evolution

```python
from scipy.optimize import differential_evolution

def rastrigin(x):
    return sum(10 * len(x) + (x**2 - 10 * np.cos(2 * np.pi * x)))

bounds = [(-5.12, 5.12)] * 10  # Bounds for each dimension

result = differential_evolution(rastrigin, bounds)
print(result.x)  # Global minimum (near [0, 0, ..., 0])
```

### Basinhopping

```python
from scipy.optimize import basinhopping

def objective(x):
    return x[0]**2 + x[1]**2 + 0.1 * np.sin(10 * x[0]) * np.sin(10 * x[1])

x0 = [1, 1]
result = basinhopping(objective, x0, niter=100)
```

## Integer Programming (Mixed Integer Linear Programming)

```python
from scipy.optimize import milp

# Minimize: -2x + y + 2z
c = [-2, 1, 2]

# Subject to:
# x + 3y + z >= 450
# x + 2y + 3z <= 600
A_ub = [[-1, -3, -1], [1, 2, 3]]  # Convert >= to <= by negation
b_ub = [-450, 600]

# Variable types: x is integer, y is continuous, z is binary
integrality = [1, 0, 2]  # 0=continuous, 1=integer, 2=binary

bounds = [(0, None), (0, None), (0, 1)]

result = milp(c, A_ub=A_ub, b_ub=b_ub, integrality=integrality, bounds=bounds)
```

## Common Parameters

### minimize() Options

```python
# Common options for all methods
options = {
    'maxiter': 1000,      # Maximum iterations
    'ftol': 1e-8,         # Function tolerance
    'gtol': 1e-5,         # Gradient tolerance
    'disp': True,         # Display convergence messages
    'return_all': False   # Return all intermediate results
}

result = minimize(objective, x0, method='BFGS', options=options)
```

### Accessing Results

```python
result = minimize(objective, x0, method='BFGS')

print(result.x)           # Solution
print(result.fun)         # Objective function value at solution
print(result.success)     # Boolean: True if successful
print(result.message)     # Termination message
print(result.nit)         # Number of iterations
print(result.nfev)        # Number of function evaluations
```

## Troubleshooting

### Optimization Not Converging

```python
# Increase iterations and tolerance
result = minimize(objective, x0, method='BFGS', 
                  options={'maxiter': 10000, 'ftol': 1e-12})

# Try different methods
for method in ['Nelder-Mead', 'BFGS', 'L-BFGS-B', 'TNC']:
    result = minimize(objective, x0, method=method)
    print(f"{method}: success={result.success}, message={result.message}")
```

### Providing Gradients (Improves Performance)

```python
def objective(x):
    return sum((x - 2)**2)

def gradient(x):
    return 2 * (x - 2)

# Pass gradient to methods that support it
result = minimize(objective, x0, method='BFGS', jac=gradient)
```

### Scaling Issues

```python
# Scale variables to similar magnitudes
from scipy.optimize import minimize

def objective_scaled(x):
    x_unscaled = x * scale_factors  # Transform back
    return original_objective(x_unscaled)

scale_factors = [1e-3, 1e6, 1.0]  # Scale each variable appropriately
```

## See Also

- [`scipy.odr`](references/15-additional.md#odr-orthogonal-distance-regression) - Orthogonal distance regression
- [`scipy.stats`](references/05-stats.md) - Statistical fitting methods
- [`scipy.interpolate`](references/03-interpolate.md) - Interpolation-based smoothing
