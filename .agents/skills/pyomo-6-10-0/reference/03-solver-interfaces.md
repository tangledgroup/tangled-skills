# Solver Interfaces

## Contents
- SolverFactory
- File-Based (Traditional) Interface
- Persistent Solvers
- APPSI (Auto-Persistent Pyomo Solver Interfaces)
- Solver Options and Timeouts
- Termination Conditions

## SolverFactory

`SolverFactory` is the primary way to create solver instances:

```python
from pyomo.opt import SolverFactory

# File-based solvers
opt = SolverFactory('glpk')
opt = SolverFactory('ipopt')
opt = SolverFactory('gurobi')
opt = SolverFactory('cplex')

# Persistent solvers
opt = SolverFactory('gurobi_persistent')
opt = SolverFactory('cplex_persistent')

# APPSI solvers (via SolverFactory)
opt = SolverFactory('appsi_gurobi')
opt = SolverFactory('appsi_ipopt')
opt = SolverFactory('appsi_cplex')
opt = SolverFactory('appsi_highs')
opt = SolverFactory('appsi_cbc')
```

If a solver is not available, `SolverFactory` returns `None`. Check availability:

```python
opt = SolverFactory('gurobi')
if opt is None:
    print("Gurobi not available")
```

## File-Based (Traditional) Interface

The default interface writes the model to a file, calls the solver, and reads results:

```python
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()
model.x = pyo.Var([1, 2], domain=pyo.NonNegativeReals)
model.obj = pyo.Objective(expr=2*model.x[1] + 3*model.x[2])
model.c = pyo.Constraint(expr=3*model.x[1] + 4*model.x[2] >= 1)

opt = SolverFactory('glpk')
results = opt.solve(model)

# Results object
print(results.solver.status)           # 'ok', 'error', etc.
print(results.solver.termination_condition)  # 'optimal', 'infeasible', etc.
```

The solve call writes a file (LP, NL, etc.), executes the solver externally, and loads results back into the model. Variables get their `.value` attribute populated.

## Persistent Solvers

Persistent solvers maintain an in-memory solver instance, avoiding file I/O for repeated solves:

```python
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()
model.x = pyo.Var(domain=pyo.NonNegativeReals)
model.y = pyo.Var(domain=pyo.NonNegativeReals)
model.p = pyo.Param(mutable=True, initialize=1.0)
model.obj = pyo.Objective(expr=model.x**2 + model.y**2)
model.c = pyo.Constraint(expr=model.y >= model.x - model.p)

opt = SolverFactory('gurobi_persistent')

# Send entire model to solver once
opt.set_instance(model)

# Now make incremental changes and resolve
for p_val in [1, 2, 3, 4, 5]:
    model.p.value = p_val
    opt.update_instance()  # notify solver of changes
    results = opt.solve(model)
    print(f"p={p_val}: x={pyo.value(model.x):.2f}, y={pyo.value(model.y):.2f}")

opt.delete_instance()  # clean up
```

Key methods: `set_instance()`, `update_instance()`, `add_variable()`, `add_constraint()`, `delete_instance()`.

**Warning**: Users are responsible for notifying persistent solvers of model changes via `update_instance()`.

## APPSI (Auto-Persistent Pyomo Solver Interfaces)

APPSI is the modern, efficient solver interface designed for repeated solves:

```python
import pyomo.environ as pyo
from pyomo.contrib import appsi
from pyomo.common.timing import HierarchicalTimer

model = pyo.ConcreteModel()
model.x = pyo.Var()
model.y = pyo.Var()
model.p = pyo.Param(mutable=True)
model.obj = pyo.Objective(expr=model.x**2 + model.y**2)
model.c1 = pyo.Constraint(expr=model.y >= pyo.exp(model.x))
model.c2 = pyo.Constraint(expr=model.y >= (model.x - model.p)**2)

opt = appsi.solvers.Ipopt()

for p_val in range(1, 11):
    model.p.value = float(p_val)
    res = opt.solve(model)
    assert res.termination_condition == appsi.base.TerminationCondition.optimal
    print(f"p={p_val}: obj={res.best_feasible_objective:.4f}")
```

APPSI solvers: `Gurobi`, `Ipopt`, `Cplex`, `Cbc`, `HiGHS`, `MAiNGO`.

Access via SolverFactory: `SolverFactory('appsi_solvername')`.

APPSI is preferred for applications like Benders decomposition, progressive hedging, and outer-approximation where the same model structure is solved many times with small changes.

## Solver Options and Timeouts

```python
# Pass options to solver
opt = SolverFactory('ipopt')
results = opt.solve(model, options={'max_iter': 1000, 'mu_strategy': 'adaptive'})

# Timeout (seconds)
results = opt.solve(model, timelimit=300)

# Display solver output
results = opt.solve(model, tee=True)

# Specific solver executable path
opt = SolverFactory('glpk')
opt.executable = '/usr/local/bin/glpk'

# Solve with specific file format
results = opt.solve(model, format='lp')  # or 'nl', 'cpxlp', etc.
```

## Termination Conditions

Check solve results:

```python
from pyomo.opt import SolverStatus, TerminationCondition

results = opt.solve(model)

if (results.solver.status == SolverStatus.ok and
    results.solver.termination_condition == TerminationCondition.optimal):
    print("Optimal solution found")

elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Model is infeasible")

elif results.solver.termination_condition == TerminationCondition.unbounded:
    print("Model is unbounded")

else:
    print(f"Other: {results.solver.termination_condition}")
```

Common termination conditions: `optimal`, `feasible`, `infeasible`, `unbounded`, `maxEvalIterations`, `maxTimeLimit`, `error`.

For APPSI: use `appsi.base.TerminationCondition.optimal` etc.
