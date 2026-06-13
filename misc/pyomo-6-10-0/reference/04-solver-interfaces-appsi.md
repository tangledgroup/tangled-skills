# Solver Interfaces and APPSI

## Contents
- SolverFactory Interface
- Standard Solve Workflow
- Persistent Solvers
- APPSI (Auto-Persistent Pyomo Solver Interfaces)
- Result Handling
- Solver Selection Guide

## SolverFactory Interface

`SolverFactory` creates solver instances by name. It is the primary entry point for solving models.

```python
import pyomo.environ as pyo

# Create solver instance
opt = pyo.SolverFactory('cbc')        # open-source LP/MIP
opt = pyo.SolverFactory('gurobi')      # commercial LP/MIP/NLP
opt = pyo.SolverFactory('ipopt')       # open-source NLP
opt = pyo.SolverFactory('cplex')       # commercial
opt = pyo.SolverFactory('highs')       # open-source LP/MIP (fast)

# Check if solver is available
if opt.available():
    results = opt.solve(model)
else:
    print(f"Solver '{opt.name}' not available")
```

Common solver names: `cbc`, `glpk`, `cplex`, `gurobi`, `ipopt`, `highs`, `bonmin`, `couenne`, `scip`.

## Standard Solve Workflow

The standard file-based interface writes the model to a file (LP, NL, etc.), calls the solver, and reads results back.

```python
import pyomo.environ as pyo
from pyomo.opt import SolverFactory, TerminationCondition

model = pyo.ConcreteModel()
model.x = pyo.Var([1, 2], domain=pyo.NonNegativeReals)
model.obj = pyo.Objective(expr=2*model.x[1] + 3*model.x[2])
model.con = pyo.Constraint(expr=3*model.x[1] + 4*model.x[2] >= 1)

opt = SolverFactory('cbc')
results = opt.solve(model, tee=False)  # tee=True shows solver output

# Check termination
if results.solver.termination_condition == TerminationCondition.optimal:
    print(f"Optimal objective: {pyo.value(model.obj):.4f}")
    for i in model.x:
        print(f"x[{i}] = {pyo.value(model.x[i]):.4f}")
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Model is infeasible")
else:
    print(f"Termination: {results.solver.termination_condition}")
```

Set solver options via `opt.options`:

```python
opt.options['timeLimit'] = 300      # 5-minute time limit
opt.options['threads'] = 4          # use 4 threads
opt.options['logFile'] = 'solver.log'
```

## Persistent Solvers

Persistent solvers keep the model in solver memory, enabling efficient incremental updates without rewriting files. Essential for Benders decomposition, column generation, and iterative algorithms.

```python
opt = pyo.SolverFactory('gurobi_persistent')

# Load model into solver
opt.set_instance(model)
results = opt.solve()

# Add new constraint incrementally
model.new_con = pyo.Constraint(expr=model.x[1] <= 5)
opt.add_constraint(model.new_con)
results = opt.solve()  # only sends the new constraint

# Remove constraint
opt.remove_constraint(model.new_con)
del model.new_con

# Update variable bounds (variables can be modified in place)
model.x[1].setlb(0.5)
opt.update_var(model.x[1])
```

For indexed variables/constraints, iterate over `.values()`:

```python
for v in model.x.values():
    opt.add_var(v)
for c in model.con.values():
    opt.add_constraint(c)
```

**Performance tip**: Use `save_results=False` when you don't need the full results object:

```python
results = opt.solve(save_results=False, load_solutions=False)
opt.load_vars()  # load variable values directly
# Or load subset:
opt.load_vars(model.x)
```

**Warning**: Users are responsible for notifying persistent solvers of all changes. If a component is replaced on the model, remove the old one from the solver first.

## APPSI (Auto-Persistent Pyomo Solver Interfaces)

APPSI provides auto-persistent solver interfaces with superior performance for repeated solves. Automatically tracks model changes and updates only what changed.

```python
from pyomo.contrib import appsi
import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.x = pyo.Var()
m.y = pyo.Var()
m.p = pyo.Param(mutable=True)
m.obj = pyo.Objective(expr=m.x**2 + m.y**2)
m.c1 = pyo.Constraint(expr=m.y >= pyo.exp(m.x))
m.c2 = pyo.Constraint(expr=m.y >= (m.x - m.p)**2)

# Direct APPSI usage
opt = appsi.solvers.Ipopt()
for p_val in range(1, 11):
    m.p.value = float(p_val)
    res = opt.solve(m)

# Via SolverFactory (pattern: appsi_<solver>)
opt_ipopt = pyo.SolverFactory('appsi_ipopt')
opt_highs = pyo.SolverFactory('appsi_highs')
opt_cbc = pyo.SolverFactory('appsi_cbc')
opt_gurobi = pyo.SolverFactory('appsi_gurobi')
opt_cplex = pyo.SolverFactory('appsi_cplex')
```

**Supported APPSI solvers**: CBC, CPLEX, Gurobi, HiGHS, IPOPT.

**Optimization for known change patterns**: Disable unnecessary checks:

```python
opt.update_config.check_for_new_or_removed_constraints = False
opt.update_config.check_for_new_or_removed_vars = False
opt.update_config.update_constraints = False
opt.update_config.update_vars = False
# Now only parameter value changes are detected — much faster
```

**Solver configuration**:

```python
opt.config.stream_solver = True          # show solver output
opt.solver_options['max_iter'] = 20      # solver-specific option
opt.config.load_solutions = True         # auto-load solutions
```

APPSI requires building extensions: `pyomo build-extensions` or `from pyomo.contrib.appsi.build import build_appsi; build_appsi()`.

## Result Handling

The results object contains solver status and solution data:

```python
from pyomo.opt import TerminationCondition, SolverStatus

# Termination conditions
results.solver.termination_condition  # optimal, infeasible, etc.
results.solver.status                  # ok, warning, error

# Objective value
pyo.value(model.obj)                   # from model after solve
results.problem.objective              # from results object

# Variable values (loaded into model by default)
pyo.value(model.x[1])

# Access all variable values
for v in instance.component_data_objects(pyo.Var, active=True):
    print(f"{v.name} = {pyo.value(v)}")
```

Common `TerminationCondition` values: `optimal`, `feasible`, `infeasible`, `infeasible_or_unbounded`, `unbounded`, `maxTimeLimit`, `iterationLimit`, `other`.

## Solver Selection Guide

| Problem Type | Recommended Solvers |
|-------------|-------------------|
| LP (linear) | HiGHS, CBC, CPLEX, Gurobi |
| MIP (mixed-integer linear) | Gurobi, CPLEX, HiGHS, CBC, SCIP |
| NLP (nonlinear) | IPOPT, KNITRO |
| MINLP (mixed-integer nonlinear) | MindtPy (decomposition), BONMIN, SCIP |
| Global MINLP | Couenne, ANTIGONE, MindtPy (GOA) |
| QP (quadratic) | CPLEX, Gurobi, IPOPT |
