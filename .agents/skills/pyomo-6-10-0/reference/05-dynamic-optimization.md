# Dynamic Optimization with pyomo.DAE

## Contents
- Overview
- ContinuousSet
- DerivativeVar
- Integral
- Differential Equations
- Discretization Transformations
- Dynamic Model Simulation
- Dynamic Model Initialization

## Overview

pyomo.DAE allows modeling systems of differential-algebraic equations (DAEs) within Pyomo. It supports ordinary and partial differential equations, higher-order derivatives, and mixed partial derivatives. The workflow is: define continuous domains and differential equations, then apply discretization transformations to convert to an algebraic NLP/MINLP that standard solvers can handle.

```python
import pyomo.environ as pyo
from pyomo.dae import ContinuousSet, DerivativeVar, Integral
from pyomo.dae.initialization import initialize_arc
from pyomo.dae.collocation import Collocation
```

## ContinuousSet

Represents a bounded continuous domain (typically time or spatial coordinate):

```python
model = pyo.ConcreteModel()

# Time domain [0, 10]
model.t = ContinuousSet(bounds=(0, 10))

# With finite difference points (used for discretization)
model.t = ContinuousSet(bounds=(0, 10), nfi=20)  # 20 finite difference intervals

# Spatial domain
model.z = ContinuousSet(bounds=(0, 1))

# Multi-dimensional continuous set
model.tz = ContinuousSet(dimen=2, bounds=((0, 10), (0, 1)))
```

## DerivativeVar

Declares derivatives of variables with respect to continuous sets:

```python
# State variable
model.x = pyo.Var(model.t, initialize=1.0)

# First derivative dx/dt
model.dxdt = DerivativeVar(
    model.x,
    withrespect=model.t,
    initialize=0.0
)

# Second derivative d2x/dt2
model.d2xdt2 = DerivativeVar(
    model.dxdt,
    withrespect=model.t
)

# Partial derivative (multi-dimensional)
model.u = pyo.Var(model.t, model.z)
model.dudz = DerivativeVar(model.u, withrespect=model.z)
```

## Integral

Represents integrals over continuous domains:

```python
# Simple integral
model.cost = Integral(
    set=model.t,
    expr=model.x[t]**2
)

# In objective
model.obj = pyo.Objective(expr=model.cost)
```

## Differential Equations

Declare differential equations as constraints relating DerivativeVar to expressions:

```python
def ode_rule(m, t):
    return m.dxdt[t] == -0.5 * m.x[t] + m.u[t]

model.ode = pyo.Constraint(model.t, rule=ode_rule)

# Initial condition
model.ic = pyo.Constraint(expr=model.x[0] == 1.0)

# Boundary condition
model.bc = pyo.Constraint(expr=model.x[10] == 0.5)

# Algebraic constraint (no derivative)
model.alg = pyo.Constraint(model.t, rule=lambda m, t: m.y[t] == m.x[t]**2)
```

## Discretization Transformations

Convert DAE to algebraic NLP/MINLP for solving:

```python
from pyomo.dae import FinDifferenceScheme
from pyomodae.nlv.colloc_scheme import CollocationScheme

# Finite Difference (first-order backward difference)
from pyomo.dae import OrthogonalCollocation

# Option 1: Finite Difference
disc = FinDifferenceScheme(model, model.t, nfe=50)
disc.discretize()

# Option 2: Orthogonal Collocation (higher accuracy)
disc = OrthogonalCollocation(
    model,
    model.t,
    ncp=10,          # number of collocation points per interval
    nse=20,          # number of segments
    scheme='LG'      # Legendre-Gauss
)
disc.discretize()

# After discretization, solve as NLP
opt = pyo.SolverFactory('ipopt')
results = opt.solve(model)
```

Key discretization options:
- `nfe`: number of finite difference elements
- `ncp`: number of collocation points per segment
- `nse`: number of segments
- Higher `ncp` gives better accuracy but more variables/constraints

## Dynamic Model Simulation

Simulate DAE models (forward integration without optimization):

```python
from pyomo.dae import initialize_arc
from pyomo.dae.simulation import simulate

# Initialize from a known starting point
initialize_arc(model, model.t, {'x': 1.0, 'y': 0.0})

# Simulate forward
simulate(model, model.t)
```

## Dynamic Model Initialization

Good initialization is critical for dynamic optimization:

```python
from pyomo.dae.initialization import initialize_stable_eq, initialize_arc

# Initialize at stable equilibrium
initialize_stable_eq(model, model.t, solver_name='ipopt')

# Initialize along a trajectory (arc)
initialize_arc(
    model,
    model.t,
    initial_conditions={'x': 1.0},
    solver_name='ipopt'
)
```

Initialization strategies:
- `initialize_stable_eq`: Find and initialize at stable equilibrium point
- `initialize_arc`: Step through time, solving NLP at each step to build trajectory
- Manual initialization: Set `.value` on all variables before discretization
