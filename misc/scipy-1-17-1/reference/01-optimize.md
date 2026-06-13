# Optimization (scipy.optimize)

## Local Minimization (minimize)

The `minimize` function provides a common interface to unconstrained and constrained minimization algorithms for multivariate scalar functions.

### Unconstrained Methods

**Nelder-Mead Simplex** (`method='Nelder-Mead'`): Simplest approach, requires only function evaluations. Good for simple problems but slower without gradient information.

```python
from scipy.optimize import minimize
import numpy as np

def rosen(x):
    return sum(100.0 * (x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0)

x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
res = minimize(rosen, x0, method='Nelder-Mead',
               options={'xatol': 1e-8})
print(res.x)  # [1. 1. 1. 1. 1.]
```

**BFGS** (`method='BFGS'`): Uses gradient information for faster convergence. If gradient not provided, estimated via finite differences. Typically requires fewer function calls than Nelder-Mead even with gradient estimation.

```python
def rosen_der(x):
    """Gradient of the Rosenbrock function."""
    xm = x[1:-1]
    der = np.zeros_like(x)
    der[1:-1] = 200*(xm - xm[:-1]**2) - 400*(xm[1:] - xm**2)*xm - 2*(1-xm)
    der[0] = -400*x[0]*(x[1] - x[0]**2) - 2*(1-x[0])
    der[-1] = 200*(x[-1] - x[-2]**2)
    return der

res = minimize(rosen, x0, method='BFGS', jac=rosen_der)
```

**Newton-CG** (`method='Newton-CG'`): Conjugate gradient method using Hessian information.

**Trust-Region methods**: `trust-ncg`, `trust-krylov`, `trust-exact` — robust methods for large-scale problems.

### Constrained Methods

**SLSQP** (`method='SLSQP'`): Sequential Least Squares Programming. Supports bounds, equality and inequality constraints. Callback functions can opt into new interface by accepting `intermediate_result` keyword argument.

```python
from scipy.optimize import minimize

def objective(x):
    return (x[0] - 1)**2 + (x[1] - 2.5)**2

cons = ({'type': 'ineq', 'fun': lambda x: x[0] - 2*x[1] + 2},
        {'type': 'ineq', 'fun': lambda x: -x[0] - 2*x[1] + 2},
        {'type': 'ineq', 'fun': lambda x: -x[0] + 2*x[1] + 2})

res = minimize(objective, [2, 0], method='SLSQP', constraints=cons)
```

**Trust-Constr** (`method='trust-constr'`): Trust-region constrained algorithm. Supports `subproblem_maxiter` option for ill-conditioned Hessians.

### Passing Extra Arguments

Three approaches to pass additional parameters:

```python
# 1. args tuple
res = minimize(rosen_with_args, x0, method='Nelder-Mead', args=(0.5, 1.0))

# 2. Wrapper function
def wrapped(x):
    return rosen_with_args(x, 0.5, b=1.0)
res = minimize(wrapped, x0, method='Nelder-Mead')

# 3. functools.partial
from functools import partial
partial_rosen = partial(rosen_with_args, a=0.5, b=1.0)
res = minimize(partial_rosen, x0, method='Nelder-Mead')
```

## Univariate Minimization (minimize_scalar)

For single-variable functions:

```python
from scipy.optimize import minimize_scalar

# Bounded minimization
res = minimize_scalar(rosen, bounds=(0, 2), method='bounded')

# Brent's method (unconstrained)
res = minimize_scalar(rosen, method='brent')
```

## Global Optimization

- `differential_evolution`: Global optimization using differential evolution algorithm
- `shgo`: Subset simulation-based global optimization
- `dual_annealing`: Simulated annealing with dual annealing schedule
- `basinhopping`: Basin-hopping global optimization
- `brute`: Brute-force search on a grid
- `direct`: DIviding RECTangles algorithm (memory leak fix in 1.17.1)

## Least-Squares Minimization (least_squares)

Solves nonlinear least-squares problems with support for bounds and sparse Jacobians:

```python
from scipy.optimize import least_squares

def residual(x):
    return x[0]**2 + x[1]**2 - 1  # constraint as residual

res = least_squares(residual, [1.0, 1.0], method='trf')
```

## Root Finding

**Scalar functions**: `root_scalar` — supports Brent, bisect, Newton, secant methods.

**Fixed-point solving**: `fixed_point` — finds fixed point of a function.

**Systems of equations**: `root` — solves F(x) = 0 for multivariate systems. Supports hybrid method (MINPACK), LM (Levenberg-Marquardt), and more.

## Linear Programming (linprog)

Solves linear programming problems:

```python
from scipy.optimize import linprog

res = linprog(c=[-1, -2, -3],
              A_ub=[[1, 1, 1]], b_ub=[4],
              bounds=(0, None), method='highs')
```

Supports HiGHS solver (updated to v1.12.0 in 1.17.1) and mixed-integer linear programming via `integrality` parameter.

## Parallel Execution

Many optimization functions support parallel execution through the `workers` or similar parameters. See the [Parallel Execution](reference/11-additional-modules.md) section for details.
