# Pyomo Solvers

## Contents
- GDPopt (Logic-Based GDP Solver)
- MindtPy (MINLP Decomposition)
- PyROS (Robust Optimization)
- Multistart Solver
- Trust Region Framework
- z3 SMT Interface

## GDPopt (Logic-Based GDP Solver)

GDPopt solves Generalized Disjunctive Programming models using logic-based decomposition instead of reformulation to MINLP. Most effective for nonlinear GDP models.

**Algorithms:**
- **LOA** (Logic-based Outer Approximation): Default for convex NLP subproblems
- **GLOA** (Global LOA): Uses global solver for NLP subproblems, guarantees global optimum
- **RIC** (Relaxation with Integer Cuts): Starts from master problem relaxation
- **LBB** (Logic-based Branch-and-Bound): Does not require convexity
- **LD-SDA** (Logic-based Discrete-Steepest Descent): Heuristic for large models

```python
from pyomo.environ import ConcreteModel, Var, Objective, Constraint, Binary
from pyomo.gdp import Disjunct, Disjunction
from pyomo.contrib.gdpopt import GDPopt

model = ConcreteModel()
model.y = Var([1, 2], within=Binary)

def disj1_rule(m):
    d = m.disj[1]
    d.x = Var(bounds=(0, 10))
    d.c = Constraint(expr=d.x >= 5)
    d.active_eq = Constraint(expr=d.x == model.y[1])
    return d

def disj2_rule(m):
    d = m.disj[2]
    d.x = Var(bounds=(0, 10))
    d.c = Constraint(expr=d.x >= 3)
    d.active_eq = Constraint(expr=d.x == model.y[2])
    return d

model.disj = Disjunct([1, 2], rule=lambda m, i: disj1_rule(m) if i == 1 else disj2_rule(m))
model.disjunction = Disjunction(expr=[model.disj[1], model.disj[2]])
model.obj = Objective(expr=model.disj[1].x + model.disj[2].x, sense=minimize)

solver = GDPopt()
results = solver.solve(model, option={'strategy': 'LOA', 'nlp_solver': 'ipopt', 'mip_solver': 'glpk'})
```

## MindtPy (MINLP Decomposition)

MindtPy solves Mixed-Integer Nonlinear Programs using decomposition algorithms that alternate between MILP and NLP subproblems.

**Algorithms:**
- **OA** (Outer-Approximation): Default for convex MINLPs
- **ECp** (Extended Cutting Plane): For nonconvex objectives with convex constraints
- **BP** (Big Picture / LP-NLP BB): Branch-and-bound with NLP nodes
- **GOA** (Global OA): Uses global solver for NLP subproblems
- **ROA** (Regularized OA): Adds regularization for stability
- **FP** (Feasibility Pump): Heuristic for finding feasible solutions

```python
from pyomo.environ import *
from pyomo.contrib.mindtpy import MindtPy

model = ConcreteModel()
model.x = Var(within=Reals, bounds=(0, 10))
model.y = Var(within=Binary)
model.obj = Objective(expr=model.x**2 + model.y)
model.c = Constraint(expr=model.x >= 2*model.y + 1)

solver = MindtPy(
    strategy='OA',
    mip_solver='glpk',
    nlp_solver='ipopt'
)
results = solver.solve(model)
```

For nonconvex MINLPs, use `strategy='BP'` (branch-and-bound) or `strategy='GOA'` (global).

## PyROS (Robust Optimization)

PyROS solves two-stage adjustable robust optimization problems with non-convex nominal problems.

```python
from pyomo.environ import *
from pyomo.contrib.pynumero.interfaces.csdp/csdp import CsdpSolver
from pyomo.contrib.pyros.core.run_pyros import PyROS

model = ConcreteModel()
model.x = Var(within=Reals, bounds=(0, 10))
model.y = Var(within=Reals, bounds=(0, 10))
model.obj = Objective(expr=model.x + model.y)
model.c = Constraint(expr=model.x + model.y <= 10)

# Define uncertain parameters and their sets
uncertain_params = ['param_name']
uncertainty_set = ...  # define uncertainty set

pyros = PyROS()
results = pyros.solve(
    model,
    nominal_solver='glpk',
    robustness_check_solver='glpk',
    uncertain_parameters=uncertain_params,
    constraint_list=['c'],
    epsilon=1e-6
)
```

PyROS iteratively checks robustness and adds cuts until a robust solution is found or infeasibility is proven.

## Multistart Solver

Runs a nonlinear solver from multiple starting points to escape local optima:

```python
from pyomo.environ import *
from pyomo.contrib.multistart import MS

model = ConcreteModel()
model.x = Var(bounds=(0, 10))
model.obj = Objective(expr=sin(model.x) * model.x)  # non-convex
model.c = Constraint(expr=model.x >= 1)

ms = MS()
ms.set_option('max_starts', 20)
ms.set_option('nlp_solver', 'ipopt')
results = ms.solve(model)
```

Use when the objective is known to be non-convex but a global optimum is desired. Multistart does not guarantee global optimality but increases confidence by exploring multiple basins of attraction.

## Trust Region Framework (TRF)

Solves hybrid glass-box/black-box optimization problems where parts of the system are equation-based and parts are black-box simulations:

```python
from pyomo.environ import *
from pyomo.contrib.trf import TRF

# Define model with both analytic and black-box components
model = ConcreteModel()
model.x = Var(bounds=(0, 10))
model.obj = Objective(expr=model.x**2)

# Configure TRF
trf = TRF()
trf.set_option('nlp_solver', 'ipopt')
results = trf.solve(model)
```

TRF is designed for problems where external simulations (e.g., CFD, process simulators) are coupled with analytic models.

## z3 SMT Interface

Interface to the z3 Satisfiability Modulo Theories solver:

```python
from pyomo.environ import *
from pyomo.contrib.z3 import z3_interface

model = ConcreteModel()
model.x = Var(within=Integers, bounds=(0, 100))
model.y = Var(within=Integers, bounds=(0, 100))

# z3 works with logical constraints
model.c1 = Constraint(expr=model.x + model.y <= 50)
model.c2 = Constraint(expr=model.x >= 10)

opt = SolverFactory('z3')
results = opt.solve(model)
```

Use for constraint satisfaction problems with integer and real variables, especially when logical reasoning is needed.
