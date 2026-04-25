# scipy.optimize - Optimization, Root-Finding, and Linear Programming

The `scipy.optimize` module provides optimization algorithms and root-finding methods for scalar, multivariate, constrained, global, and linear programming problems.

## Local Minimization of Multivariate Scalar Functions (`minimize`)

The `minimize` function provides a common interface to unconstrained and constrained minimization algorithms for multivariate scalar functions.

### Rosenbrock Function Example

To demonstrate, consider minimizing the Rosenbrock function of N variables:

$$f(\mathbf{x}) = \sum_{i=1}^{N-1} 100(x_{i+1} - x_i^2)^2 + (1 - x_i)^2$$

The minimum value is 0, achieved when $x_i = 1$. The Rosenbrock function and its derivatives are included in `scipy.optimize`.

```python
import numpy as np
from scipy.optimize import rosen, rosen_der, rosen_hess
```

### Unconstrained Minimization

#### Nelder-Mead Simplex (`method='Nelder-Mead'`)

The simplex algorithm requires only function evaluations — no gradients needed. Good for simple problems but may take longer than gradient-based methods.

```python
from scipy.optimize import minimize

x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
res = minimize(rosen, x0, method='nelder-mead',
               options={'xatol': 1e-8, 'disp': True})
# Current function value: 0.000000, Iterations: 339, Function evaluations: 571
print(res.x)  # [1. 1. 1. 1. 1.]
```

Powell's method (`method='powell'`) is another derivative-free alternative.

#### BFGS (`method='BFGS'`)

The Broyden-Fletcher-Goldfarb-Shanno algorithm uses the gradient for faster convergence. If no gradient is provided, it is estimated via first-differences.

```python
# Gradient of Rosenbrock function
def rosen_der(x):
    xm = x[1:-1]
    xm_m1 = x[:-2]
    xm_p1 = x[2:]
    der = np.zeros_like(x)
    der[1:-1] = 200*(xm - xm_m1**2) - 400*(xm_p1 - xm**2)*xm - 2*(1 - xm)
    der[0] = -400*x[0]*(x[1] - x[0]**2) - 2*(1 - x[0])
    der[-1] = 200*(x[-1] - x[-2]**2)
    return der

res = minimize(rosen, x0, method='BFGS', jac=rosen_der,
               options={'disp': True})
# Iterations: 25, Function evaluations: 30, Gradient evaluations: 30
```

**Avoiding Redundant Calculation:** When the objective and gradient share expensive computations, return both from a single function by setting `jac=True`:

```python
def f_and_df(x):
    expensive_value = expensive(x[0])
    return (-expensive_value**2,           # objective
            -2 * expensive_value * dexpensive(x[0]))  # gradient

res = minimize(f_and_df, 0.5, jac=True)  # jac=True means function returns (f, df)
```

Alternatively, use `functools.lru_cache` to memoize expensive subcomputations.

#### Newton-Conjugate-Gradient (`method='Newton-CG'`)

A modified Newton's method that uses a conjugate gradient algorithm to approximately invert the local Hessian. Requires either a Hessian function or a Hessian-vector product function.

**Full Hessian:**
```python
def rosen_hess(x):
    x = np.asarray(x)
    H = np.diag(-400*x[:-1], 1) - np.diag(400*x[:-1], -1)
    diagonal = np.zeros_like(x)
    diagonal[0] = 1200*x[0]**2 - 400*x[1] + 2
    diagonal[-1] = 200
    diagonal[1:-1] = 202 + 1200*x[1:-1]**2 - 400*x[2:]
    H = H + np.diag(diagonal)
    return H

res = minimize(rosen, x0, method='Newton-CG', jac=rosen_der, hess=rosen_hess,
               options={'xtol': 1e-8, 'disp': True})
# Iterations: 19, Function evaluations: 22
```

**Hessian-vector product (memory efficient for large problems):**
```python
def rosen_hess_p(x, p):
    x = np.asarray(x)
    Hp = np.zeros_like(x)
    Hp[0] = (1200*x[0]**2 - 400*x[1] + 2)*p[0] - 400*x[0]*p[1]
    Hp[1:-1] = (-400*x[:-2]*p[:-2] +
                 (202 + 1200*x[1:-1]**2 - 400*x[2:])*p[1:-1] -
                 400*x[1:-1]*p[2:])
    Hp[-1] = -400*x[-2]*p[-2] + 200*p[-1]
    return Hp

res = minimize(rosen, x0, method='Newton-CG', jac=rosen_der, hessp=rosen_hess_p,
               options={'xtol': 1e-8, 'disp': True})
```

#### Trust-Region Methods

**`trust-ncg`** — Trust-region Newton-Conjugate-Gradient. Fixes a step-size limit $\Delta$ and finds the optimal step inside the trust region by solving:

$$\min_{\mathbf{p}} f(\mathbf{x}_k) + \nabla f(\mathbf{x}_k)\cdot\mathbf{p} + \frac{1}{2}\mathbf{p}^T\mathbf{H}(\mathbf{x}_k)\mathbf{p}, \quad \|\mathbf{p}\| \leq \Delta$$

```python
res = minimize(rosen, x0, method='trust-ncg', jac=rosen_der, hess=rosen_hess,
               options={'gtol': 1e-8, 'disp': True})
# Also supports hessp for Hessian-vector product
```

**`trust-krylov`** — Trust-region Truncated Generalized Lanczos / Conjugate Gradient. Solves the trust-region subproblem more accurately than `trust-ncg`. Better for indefinite problems. Wraps the [TRLIB](https://arxiv.org/abs/1611.04718) implementation of GLTR.

```python
res = minimize(rosen, x0, method='trust-krylov', jac=rosen_der, hessp=rosen_hess_p,
               options={'gtol': 1e-8, 'disp': True})
```

**`trust-exact`** — Trust-region Nearly Exact. Solves trust-region subproblems almost exactly via Cholesky factorizations. Fewer iterations than other trust-region methods but does not support Hessian-vector product. Best for medium-sized problems where Hessian storage is affordable.

```python
res = minimize(rosen, x0, method='trust-exact', jac=rosen_der, hess=rosen_hess,
               options={'gtol': 1e-8, 'disp': True})
# Iterations: 13 (fewer than trust-ncg/trust-krylov)
```

### Passing Additional Arguments to Objective Functions

```python
def rosen_with_args(x, a, b):
    """Rosenbrock function with scaling factor a and offset b."""
    return sum(a*(x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0) + b

# Using args tuple
res = minimize(rosen_with_args, x0, method='nelder-mead',
               args=(0.5, 1.), options={'xatol': 1e-8})

# Using functools.partial
from functools import partial
partial_rosen = partial(rosen_with_args, a=0.5, b=1.)
res = minimize(partial_rosen, x0, method='nelder-mead', options={'xatol': 1e-8})

# Using closure / wrapped function
def rosen_kwonly(x, a, *, b):
    return sum(a*(x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0) + b

def wrapped_rosen(x):
    return rosen_kwonly(x, 0.5, b=1.)
res = minimize(wrapped_rosen, x0, method='nelder-mead')
```

### Constrained Minimization

The `minimize` function supports several algorithms for constrained problems: `trust-constr`, `SLSQP`, `COBYLA`, and `COBYQA`.

#### Trust-Region Constrained (`method='trust-constr'`)

Handles constraints of the form $c^l \leq c(x) \leq c^u$ and $x^l \leq x \leq x^u$. Uses trust-region type algorithms suitable for large-scale problems.

**Defining bounds:**
```python
from scipy.optimize import Bounds
bounds = Bounds([0, -0.5], [1.0, 2.0])  # lb, ub arrays
```

**Defining linear constraints:**
```python
from scipy.optimize import LinearConstraint
# x0 + 2*x1 <= 1,  2*x0 + x1 = 1
linear_constraint = LinearConstraint([[1, 2], [2, 1]], [-np.inf, 1], [1, 1])
```

**Defining nonlinear constraints:**
```python
from scipy.optimize import NonlinearConstraint

def cons_f(x):
    return [x[0]**2 + x[1], x[0]**2 - x[1]]

def cons_J(x):
    return [[2*x[0], 1], [2*x[0], -1]]

def cons_H(x, v):
    # Linear combination of Hessians: sum_i v_i * Hessian(c_i)
    return v[0]*np.array([[2, 0], [0, 0]]) + v[1]*np.array([[2, 0], [0, 0]])

nonlinear_constraint = NonlinearConstraint(cons_f, -np.inf, 1, jac=cons_J, hess=cons_H)
```

Hessian can also be defined as a sparse matrix or `LinearOperator`:
```python
from scipy.sparse import csc_matrix
def cons_H_sparse(x, v):
    return (v[0]*csc_matrix([[2, 0], [0, 0]]) +
            v[1]*csc_matrix([[2, 0], [0, 0]]))

nonlinear_constraint = NonlinearConstraint(cons_f, -np.inf, 1,
                                           jac=cons_J, hess=cons_H_sparse)
```

When the Hessian is difficult to compute, use approximations:
```python
from scipy.optimize import BFGS, SR1
# BFGS quasi-Newton approximation for Hessian
nonlinear_constraint = NonlinearConstraint(cons_f, -np.inf, 1, jac=cons_J, hess=BFGS())
# Finite difference for Hessian (requires user-provided Jacobian)
nonlinear_constraint = NonlinearConstraint(cons_f, -np.inf, 1, jac=cons_J, hess='2-point')
# Finite difference for Jacobian (Hessian must be provided or use BFGS)
nonlinear_constraint = NonlinearConstraint(cons_f, -np.inf, 1, jac='2-point', hess=BFGS())
```

**Solving:**
```python
x0 = np.array([0.5, 0])
res = minimize(rosen, x0, method='trust-constr', jac=rosen_der, hess=rosen_hess,
               constraints=[linear_constraint, nonlinear_constraint],
               options={'verbose': 1}, bounds=bounds)
print(res.x)  # [0.41494531 0.17010937]
```

Hessian of the objective can also be a `LinearOperator` or specified via `hessp`:
```python
def rosen_hess_linop(x):
    def matvec(p):
        return rosen_hess_p(x, p)
    from scipy.sparse.linalg import LinearOperator
    return LinearOperator((2, 2), matvec=matvec)

# Or directly with hessp
res = minimize(rosen, x0, method='trust-constr', jac=rosen_der, hessp=rosen_hess_p,
               constraints=[linear_constraint, nonlinear_constraint],
               options={'verbose': 1}, bounds=bounds)
```

Derivatives can be approximated entirely:
```python
res = minimize(rosen, x0, method='trust-constr', jac='2-point', hess=SR1(),
               constraints=[linear_constraint, nonlinear_constraint],
               options={'verbose': 1}, bounds=bounds)
```

#### SLSQP (`method='SLSQP'`)

Sequential Least SQuares Programming. Handles bounds, linear equality/inequality, and nonlinear constraints defined as dictionaries.

```python
x0 = np.array([0.5, 0])
bounds = [(0, 1), (-0.5, 2.0)]

ineq_cons = {'type': 'ineq',
             'fun': lambda x: np.array([1 - x[0] - 2*x[1],
                                        1 - x[0]**2 - x[1],
                                        1 - x[0]**2 + x[1]]),
             'jac': lambda x: np.array([[-1.0, -2.0],
                                        [-2*x[0], -1.0],
                                        [-2*x[0], 1.0]])}

eq_cons = {'type': 'eq',
           'fun': lambda x: np.array([2*x[0] + x[1] - 1]),
           'jac': lambda x: np.array([2.0, 1.0])}

res = minimize(rosen, x0, method='SLSQP', jac=rosen_der,
               constraints=[eq_cons, ineq_cons],
               options={'ftol': 1e-9, 'disp': True}, bounds=bounds)
print(res.x)  # [0.41494475 0.1701105 ]
```

### Local Minimization Solver Comparison

| Solver | Bounds | Nonlinear Constraints | Uses Gradient | Uses Hessian | Utilizes Sparsity |
|--------|--------|----------------------|---------------|--------------|-------------------|
| CG | ✓ | | ✓ | | |
| BFGS | ✓ | | ✓ | | |
| dogleg | ✓ | ✓ | ✓ | | |
| trust-ncg | ✓ | ✓ | ✓ | ✓ | |
| trust-krylov | ✓ | ✓ | ✓ | ✓ | ✓ |
| trust-exact | ✓ | ✓ | ✓ | ✓ | |
| Newton-CG | ✓ | ✓ | ✓ | ✓ | |
| Nelder-Mead | ✓ | | | | |
| Powell | ✓ | | | | |
| L-BFGS-B | ✓ | ✓ | ✓ | | |
| TNC | ✓ | ✓ | ✓ | | |
| COBYLA | ✓ | ✓ | | | |
| COBYQA | ✓ | ✓ | | | |
| SLSQP | ✓ | ✓ | ✓ | | |
| trust-constr | ✓ | ✓ | ✓ | ✓ | ✓ |

## Global Optimization

Global optimization finds the global minimum in the presence of many local minima. SciPy provides several global optimizers, each using a local minimizer (e.g., `minimize`) under the hood.

### Eggholder Function Example

```python
def eggholder(x):
    return (-(x[1] + 47) * np.sin(np.sqrt(abs(x[0]/2 + (x[1] + 47))))
            - x[0] * np.sin(np.sqrt(abs(x[0] - (x[1] + 47)))))

bounds = [(-512, 512), (-512, 512)]
```

This function has many local minima and is a classic test for global optimizers.

### Available Global Optimizers

```python
from scipy import optimize

results = {}
results['shgo'] = optimize.shgo(eggholder, bounds)
# SHGO finds multiple local minima, results.xl contains all of them

results['DA'] = optimize.dual_annealing(eggholder, bounds)
# Dual Annealing — simulated annealing variant

results['DE'] = optimize.differential_evolution(eggholder, bounds)
# Differential Evolution — population-based method
```

**SHGO with Sobol sampling:**
```python
results['shgo_sobol'] = optimize.shgo(eggholder, bounds, n=200, iters=5,
                                       sampling_method='sobol')
# Finds multiple local minima using Sobol quasi-random sequence
```

All optimizers return an `OptimizeResult` with fields: `fun`, `funl`, `message`, `nfev`, `nit`, `success`, `x`, and method-specific fields.

### Global Optimizer Comparison

| Solver | Bounds Constraints | Nonlinear Constraints | Uses Gradient | Uses Hessian |
|--------|-------------------|----------------------|---------------|--------------|
| basinhopping | (✓) | (✓) | | |
| direct | ✓ | | | |
| dual_annealing | ✓ | (✓) | (✓) | (✓) |
| differential_evolution | ✓ | ✓ | | |
| shgo | ✓ | ✓ | (✓) | (✓) |

(✓) = Depends on the chosen local minimizer.

### basinhopping Example

```python
from scipy.optimize import basinhopping

def objective(x):
    return x[0]**2 + x[1]**2 + 0.1 * np.sin(10*x[0]) * np.sin(10*x[1])

x0 = [1, 1]
result = basinhopping(objective, x0, niter=100)
```

### differential_evolution Example

```python
from scipy.optimize import differential_evolution, rosen

def rastrigin(x):
    return sum(10 * len(x) + (x**2 - 10 * np.cos(2 * np.pi * x)))

bounds = [(-5.12, 5.12)] * 10
result = differential_evolution(rastrigin, bounds)
print(result.x)  # Global minimum near [0, 0, ..., 0]
```

## Least-Squares Minimization (`least_squares`)

Solves robustified bound-constrained nonlinear least-squares problems:

$$\min_{\mathbf{x}} \frac{1}{2} \sum_{i=1}^m \rho(f_i(\mathbf{x})^2) \quad \text{subject to } \mathbf{lb} \leq \mathbf{x} \leq \mathbf{ub}$$

where $f_i(\mathbf{x})$ are residuals and $\rho(\cdot)$ is a loss function for robustness.

**Always provide the Jacobian analytically** — finite-difference estimation is slow and inaccurate.

### Enzymatic Reaction Fitting Example

```python
from scipy.optimize import least_squares

def model(x, u):
    return x[0] * (u**2 + x[1]*u) / (u**2 + x[2]*u + x[3])

def fun(x, u, y):
    return model(x, u) - y

def jac(x, u, y):
    J = np.empty((u.size, x.size))
    den = u**2 + x[2]*u + x[3]
    num = u**2 + x[1]*u
    J[:, 0] = num / den
    J[:, 1] = x[0]*u / den
    J[:, 2] = -x[0]*num*u / den**2
    J[:, 3] = -x[0]*num / den**2
    return J

u = np.array([4.0, 2.0, 1.0, 5.0e-1, 2.5e-1, 1.67e-1, 1.25e-1, 1.0e-1,
              8.33e-2, 7.14e-2, 6.25e-2])
y = np.array([1.957e-1, 1.947e-1, 1.735e-1, 1.6e-1, 8.44e-2, 6.27e-2,
              4.56e-2, 3.42e-2, 3.23e-2, 2.35e-2, 2.46e-2])
x0 = np.array([2.5, 3.9, 4.15, 3.9])

res = least_squares(fun, x0, jac=jac, bounds=(0, 100), args=(u, y), verbose=1)
print(res.x)
# [ 0.19280596  0.19130423  0.12306063  0.13607247]
```

### curve_fit (Convenience Wrapper)

```python
from scipy.optimize import curve_fit

def model(x, a, b, c):
    return a * np.exp(-b * x) + c

x_data = np.linspace(0, 4, 50)
y_data = model(x_data, 2.5, 1.3, 0.5) + np.random.normal(0, 0.1, 50)

popt, pcov = curve_fit(model, x_data, y_data)
print(f"Fitted parameters: {popt}")

# With bounds
popt, pcov = curve_fit(model, x_data, y_data,
                       bounds=([0, 0, 0], [np.inf, np.inf, np.inf]))
```

### Further Examples

- **Large-scale bundle adjustment** — demonstrates sparse Jacobian computation
- **Robust nonlinear regression** — handling outliers with robust loss functions
- **Discrete boundary-value problem** — solving large systems with bounds

## Univariate Function Minimization (`minimize_scalar`)

For single-variable functions, specialized algorithms are faster.

### Unconstrained: `method='brent'`

Brent's algorithm for locating a minimum. A bracket $(a, b, c)$ should be provided where $f(a) > f(b) < f(c)$ and $a < b < c$.

```python
from scipy.optimize import minimize_scalar

f = lambda x: (x - 2) * (x + 1)**2
res = minimize_scalar(f, method='brent')
print(res.x)  # 1.0
```

### Bounded: `method='bounded'`

Constrained minimization within a fixed interval:

```python
from scipy.special import j1

res = minimize_scalar(j1, bounds=(4, 7), method='bounded')
print(res.x)  # 5.33144184241
```

## Root Finding

### Scalar Functions (`root_scalar`, `brentq`)

```python
from scipy.optimize import root_scalar, brentq

def f(x):
    return x**2 - 4  # Root at x = 2

result = root_scalar(f, bracket=[1, 3], method='brentq')
print(result.root)  # 2.0
```

When a derivative is available, `newton()` or `halley()` can be used without bracketing:

```python
from scipy.optimize import newton

sol = newton(f, x0=1.5)
```

### Fixed-Point Solving (`fixed_point`)

A fixed point satisfies $g(x) = x$. The root of $f(x) = g(x) - x$ is the fixed point.

```python
from scipy.optimize import fixed_point

def g(x):
    return np.cos(x)  # Fixed point: cos(x) = x

sol = fixed_point(g, x0=0.5)
```

### Sets of Equations (`root`)

```python
from scipy.optimize import root

# Single transcendental equation
def func(x):
    return x + 2 * np.cos(x)

sol = root(func, 0.3)
print(sol.x)  # [-1.02986653]

# System of nonlinear equations with Jacobian
def func2(x):
    f = [x[0] * np.cos(x[1]) - 4,
         x[1]*x[0] - x[1] - 5]
    df = np.array([[np.cos(x[1]), -x[0]*np.sin(x[1])],
                   [x[1], x[0] - 1]])
    return f, df

sol = root(func2, [1, 1], jac=True, method='lm')
print(sol.x)  # [ 6.50409711  0.90841421]
```

### Root Finding for Large Problems

For large systems, dense Jacobian methods (`hybr`, `lm`) are too slow. Use inexact Newton methods:

```python
from scipy.optimize import root
import numpy as np

# Solve: (d²/dx² + d²/dy²)P + 5*(∫∫cosh(P))² = 0 on [0,1]×[0,1]
nx, ny = 75, 75
hx, hy = 1./(nx-1), 1./(ny-1)

def residual(P):
    d2x = np.zeros_like(P)
    d2y = np.zeros_like(P)
    d2x[1:-1] = (P[2:] - 2*P[1:-1] + P[:-2]) / hx/hx
    d2x[0] = (P[1] - 2*P[0] + 0) / hx/hx
    d2x[-1] = (0 - 2*P[-1] + P[-2]) / hx/hx
    d2y[:,1:-1] = (P[:,2:] - 2*P[:,1:-1] + P[:,:-2]) / hy/hy
    d2y[:,0] = (P[:,1] - 2*P[:,0] + 0) / hy/hy
    d2y[:,-1] = (1 - 2*P[:,-1] + P[:,-2]) / hy/hy
    return d2x + d2y + 5*np.cosh(P).mean()**2

guess = np.zeros((nx, ny), float)
sol = root(residual, guess, method='krylov', options={'disp': True})
# Alternatives: method='broyden2', method='anderson'
```

### Preconditioning for Large Problems

For expensive residual functions, preconditioning the Krylov solver dramatically reduces iterations:

```python
from scipy.sparse import dia_array, kron
from scipy.sparse.linalg import spilu, LinearOperator

def get_preconditioner():
    """Compute approximate inverse of Laplacian part as preconditioner."""
    diags_x = np.zeros((3, nx))
    diags_x[0,:] = 1/hx/hx
    diags_x[1,:] = -2/hx/hx
    diags_x[2,:] = 1/hx/hx
    Lx = dia_array((diags_x, [-1,0,1]), shape=(nx, nx))

    diags_y = np.zeros((3, ny))
    diags_y[0,:] = 1/hy/hy
    diags_y[1,:] = -2/hy/hy
    diags_y[2,:] = 1/hy/hy
    Ly = dia_array((diags_y, [-1,0,1]), shape=(ny, ny))

    J1 = kron(Lx, np.eye(ny)) + kron(np.eye(nx), Ly)
    J1_ilu = spilu(J1)
    M = LinearOperator(shape=(nx*ny, nx*ny), matvec=J1_ilu.solve)
    return M

sol = root(residual, guess, method='krylov',
           options={'disp': True,
                    'jac_options': {'inner_M': get_preconditioner()}})
```

With preconditioning, residual evaluations dropped from 317 to 77 for the example above.

## Linear Programming (`linprog`)

Minimizes a linear objective subject to linear equality and inequality constraints:

$$\min_x \ c^T x \quad \text{such that} \quad A_{ub}\,x \leq b_{ub},\ A_{eq}\,x = b_{eq},\ l \leq x \leq u$$

### Full Example with Maximization, Inequalities, Equalities, and Bounds

```python
from scipy.optimize import linprog
import numpy as np

# Maximize 29*x1 + 45*x2 → Minimize -29*x1 - 45*x2
c = np.array([-29.0, -45.0, 0.0, 0.0])

# Inequality constraints (all converted to ≤ form)
A_ub = np.array([[1.0, -1.0, -3.0, 0.0],
                 [-2.0, 3.0, 7.0, -3.0]])
b_ub = np.array([5.0, -10.0])

# Equality constraints
A_eq = np.array([[2.0, 8.0, 1.0, 0.0],
                 [4.0, 4.0, 0.0, 1.0]])
b_eq = np.array([60.0, 60.0])

# Variable bounds
bounds = [(0, None), (0, 6.0), (-np.inf, 0.5), (-3.0, None)]

result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                 bounds=bounds, method='highs')
print(result.x)
print(result.fun)  # Optimal objective value
```

**Key conversion rules:**
- **Maximization → Minimization:** Negate the objective coefficients
- **$\geq$ constraints:** Multiply both sides by $-1$ to convert to $\leq$
- Use `np.inf` for unbounded constraints
- The default method is `'highs'` (HiGHS solver)

### Checking Results

```python
x = np.array(result.x)
# Verify inequality slack: b_ub - A_ub @ x >= 0
print(b_ub - (A_ub @ x))
# Verify equality residual: b_eq - A_eq @ x ≈ 0
print(b_eq - (A_eq @ x))
```

## Assignment Problems (`linear_sum_assignment`)

Finds the minimum-cost assignment of rows to columns in a cost matrix.

### Swimming Relay Example

```python
from scipy.optimize import linear_sum_assignment
import numpy as np

# Cost matrix: rows = swimming styles, cols = students
cost = np.array([[43.5, 45.5, 43.4, 46.5, 46.3],  # backstroke
                 [47.1, 42.1, 39.1, 44.1, 47.8],  # breaststroke
                 [48.4, 49.6, 42.1, 44.5, 50.4],  # butterfly
                 [38.2, 36.8, 43.2, 41.2, 37.2]]) # freestyle

row_ind, col_ind = linear_sum_assignment(cost)
print(row_ind)  # [0 1 2 3]
print(col_ind)  # [0 2 3 1]

styles = np.array(["backstroke", "breaststroke", "butterfly", "freestyle"])
students = np.array(["A", "B", "C", "D", "E"])
assignment = dict(zip(styles[row_ind], students[col_ind]))
# {'backstroke': 'A', 'breaststroke': 'C', 'butterfly': 'D', 'freestyle': 'B'}

total_time = cost[row_ind, col_ind].sum()  # 163.9
```

## Mixed Integer Linear Programming (`milp`)

For problems where decision variables must be integers (binary, integer, or continuous).

### Knapsack Problem Example

```python
from scipy.optimize import milp, Bounds, LinearConstraint
import numpy as np

sizes = np.array([21, 11, 15, 9, 34, 25, 41, 52])
values = np.array([22, 12, 16, 10, 35, 26, 42, 53])
capacity = 100

# Minimize negative values (to maximize total value)
c = -values

# Binary constraints
bounds = Bounds(0, 1)
integrality = np.full_like(values, True)  # all variables are integers

# Capacity constraint
constraints = LinearConstraint(A=sizes, lb=0, ub=capacity)

res = milp(c=c, constraints=constraints,
           integrality=integrality, bounds=bounds)
print(res.x)  # [1. 1. 0. 1. 1. 1. 0. 0.]
# Select items 1, 2, 4, 5, 6 for maximum value within capacity
```

**Integrality codes:** `0` = continuous, `1` = integer, `2` = binary (use `Bounds(0, 1)` for binary).

## Custom Minimizers

Pass a callable as the `method` parameter to use a custom optimization algorithm:

```python
from scipy.optimize import minimize, OptimizeResult
import numpy as np

def custmin(fun, x0, args=(), maxfev=None, stepsize=0.1,
            maxiter=100, callback=None, **options):
    """Custom grid-search minimizer."""
    bestx = x0
    besty = fun(x0)
    funcalls = 1
    niter = 0
    improved = True

    while improved and not stop and niter < maxiter:
        improved = False
        niter += 1
        for dim in range(np.size(x0)):
            for s in [bestx[dim] - stepsize, bestx[dim] + stepsize]:
                testx = np.copy(bestx)
                testx[dim] = s
                testy = fun(testx, *args)
                funcalls += 1
                if testy < besty:
                    besty = testy
                    bestx = testx
                    improved = True
            if callback is not None:
                callback(bestx)

    return OptimizeResult(fun=besty, x=bestx, nit=niter,
                          nfev=funcalls, success=(niter > 1))

res = minimize(rosen, [1.35, 0.9, 0.8, 1.1, 1.2],
               method=custmin, options=dict(stepsize=0.05))
print(res.x)  # [1. 1. 1. 1. 1.]
```

## Parallel Execution Support

Some optimizers support parallel evaluation via the `workers` parameter:

### differential_evolution with Parallel Workers

```python
from scipy.optimize import differential_evolution, rosen, Bounds

bnds = Bounds([0., 0., 0.], [10., 10., 10.])
res = differential_evolution(rosen, bnds, workers=2, updating='deferred')
```

### minimize with Parallel Numerical Derivatives

```python
from multiprocessing import Pool
import time

def slow_func(x):
    time.sleep(0.0002)
    return rosen(x)

x0 = rng.uniform(low=0.0, high=10.0, size=(20,))

# Serial
%timeit minimize(slow_func, x0, method='L-BFGS-B')  # ~365 ms

# Parallel via Pool
with Pool(2) as pwl:
    %timeit minimize(slow_func, x0, method='L-BFGS-B',
                     options={'workers': pwl.map})  # ~70 ms
```

### Vectorized Map-like Worker

```python
def vectorized_maplike(fun, iterable):
    arr = np.array([i for i in iter(iterable)])  # shape: (S, N)
    arr_t = arr.T                                 # shape: (N, S)
    r = slow_func(arr_t)                          # vectorized evaluation
    return r

%timeit minimize(slow_func, x0, method='L-BFGS-B',
                 options={'workers': vectorized_maplike})  # ~39 ms
```

**Important notes on parallel execution:**
- The objective function must be pickleable (no lambda functions)
- Use `Pool.map` as the map-like callable to avoid process creation overhead per call
- Performance gains only materialize when the objective function is expensive
- For `differential_evolution`, vectorization is built-in via the `vectorized=True` parameter

## Common Parameters and Result Inspection

### minimize() Options

```python
options = {
    'maxiter': 1000,      # Maximum iterations
    'ftol': 1e-8,         # Function tolerance
    'gtol': 1e-5,         # Gradient tolerance
    'disp': True,         # Display convergence messages
    'return_all': False   # Return all intermediate results
}
```

### Accessing Results

```python
result = minimize(objective, x0, method='BFGS')

print(result.x)           # Solution
print(result.fun)         # Objective function value at solution
print(result.success)     # True if converged
print(result.message)     # Termination message
print(result.nit)         # Number of iterations
print(result.nfev)        # Number of function evaluations
print(result.njev)        # Number of gradient evaluations
```

## Troubleshooting

### Optimization Not Converging

```python
# Increase iterations and tighten tolerance
result = minimize(objective, x0, method='BFGS',
                  options={'maxiter': 10000, 'ftol': 1e-12})

# Try multiple methods
for method in ['Nelder-Mead', 'BFGS', 'L-BFGS-B', 'TNC']:
    result = minimize(objective, x0, method=method)
    print(f"{method}: success={result.success}, message={result.message}")
```

### Providing Analytical Derivatives (Improves Performance)

```python
def objective(x):
    return sum((x - 2)**2)

def gradient(x):
    return 2 * (x - 2)

# Pass to methods that support it
result = minimize(objective, x0, method='BFGS', jac=gradient)
```

### Scaling Issues

```python
# Scale variables to similar magnitudes
scale_factors = [1e-3, 1e6, 1.0]
def objective_scaled(x):
    x_unscaled = np.array(x) * scale_factors
    return original_objective(x_unscaled)
```

## See Also

- [`scipy.odr`](references/15-additional.md#odr-orthogonal-distance-regression) — Orthogonal distance regression
- [`scipy.stats`](references/05-stats.md) — Statistical fitting methods
- [`scipy.interpolate`](references/03-interpolate.md) — Interpolation-based smoothing
