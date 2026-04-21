# Guides

## Solver Configuration

### Checking Available Solvers

```python
import pulp

# All registered solvers (includes unavailable ones)
print(pulp.listSolvers())
# ['GLPK_CMD', 'COIN_CMD', 'CPLEX_CMD', 'GUROBI_CMD', 'MOSEK', 'XPRESS_CMD', ...]

# Only installed/available solvers
print(pulp.listSolvers(onlyAvailable=True))
# ['COIN_CMD', 'GLPK_CMD']  # depends on what's installed

# Get solver by name (args passed to constructor)
solver = pulp.getSolver('COIN_CMD', timeLimit=60, msg=False)
```

### CBC Solver Configuration

> **Important:** `PULP_CBC_CMD` has been removed. Use `COIN_CMD` instead.

```python
from pulp import *

# With bundled CBC (pip install pulp[cbc])
solver = COIN_CMD(timeLimit=60)

# With system binary (ensure cbc is on PATH)
solver = COIN_CMD()

# With explicit path
solver = COIN_CMD(path='/usr/bin/cbc')
```

### Getting Solver by Name

```python
import pulp

# Get solver object — args passed to constructor
solver = pulp.getSolver('COIN_CMD', timeLimit=60, msg=False)
solver = pulp.getSolver('GUROBI', timeLimit=300, mipGap=0.01)

# Use it
prob.solve(solver)
```

### Environment Variables

CMD solvers need their binary on `PATH`. Set environment variables:

```bash
# Linux/Mac
export PATH=$PATH:/opt/gurobi1102/bin
export GLPK_PATH=/usr/local/bin/glpksol

# Windows
set PATH=%PATH%;C:\gurobi1102\win64\bin
```

Or specify `path=` parameter:

```python
prob.solve(pulp.GLPK_CMD(path='/opt/glpk/bin/glpksol'))
```

## Data Utilities

### makeDict — Convert 2D Arrays to Nested Dictionaries

`makeDict` is from the `amply` plugin. It converts a 2D list into a nested dictionary with default values. Used in the official transportation case study.

```python
from amply import makeDict

# Input: 2D cost matrix with row/column labels
costs = [
    [2, 4, 5, 2, 1],  # A
    [3, 1, 3, 2, 3],  # B
]
Warehouses = ["A", "B"]
Bars = ["1", "2", "3", "4", "5"]

# Convert to nested dict: costs_dict["A"]["1"] = 2
costs_dict = makeDict([Warehouses, Bars], costs, default=0)

# Access by label
print(costs_dict["A"]["1"])   # 2
print(costs_dict["B"]["3"])   # 3

# Default value for missing keys (e.g., adding a third warehouse)
print(costs_dict["C"]["2"])   # 0 (default)
```

This pattern is essential for the transportation problem where cost matrices are naturally 2D arrays but need dictionary access by node labels.

## Model Export and Import

### Writing Models to File

```python
from pulp import *

prob = LpProblem("MyModel", LpMinimize)
x = LpVariable("x", lowBound=0)
y = LpVariable("y", lowBound=0)
prob += x + y <= 10
prob += 2*x + 3*y >= 5

# .lp file — PuLP native format (returns list of variables)
variables = prob.writeLP("model.lp")

# .mps file — standard LP interchange format (returns tuple)
result = prob.writeMPS("model.mps", mpsSense=0, rename=True, mip=True)
# result = (var_names, con_names, obj_name, pulp_names_in_column_order)

# .json file — full model state including solution values
prob.toJson("model.json")

# In-memory export
data = prob.to_dict()
```

### Reading Models from File

```python
from pulp import *

# Load from JSON — returns (variables_dict, problem)
variables_dict, loaded_prob = LpProblem.fromJson("model.json")

# Load from MPS — returns (variables_dict, problem)
variables_dict, loaded_prob = LpProblem.fromMPS("model.mps")

# Use the loaded model
loaded_prob.solve()
for name, var in variables_dict.items():
    print(f"  {name} = {var.varValue}")
```

### Export/Import Considerations

- **JSON format** preserves complete model state including status, solution values, shadow prices, and reduced costs.
- **MPS format** is an industry standard but only stores variables, constraints, and objective — no variable values or shadow prices.
- **Variable names must be unique** for import/export to work correctly.
- Variables are exported flat — nested dictionary grouping is not restored automatically.
- For JSON with NumPy/pandas data types, provide a custom encoder:

```python
import json, numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        elif isinstance(obj, np.floating): return float(obj)
        elif isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

prob.toJson("model.json", cls=NpEncoder)
```

## MIP Start (Warm Start)

Provide initial variable values to guide the solver. Supported by: CPLEX_CMD, GUROBI_CMD, COIN_CMD (CBC), CPLEX_PY, GUROBI, XPRESS, XPRESS_PY.

```python
from pulp import *

prob = LpProblem("MIPStart", LpMinimize)
x = LpVariable.dicts("x", range(5), cat='Binary')
prob += lpSum(x[i] for i in range(5)) >= 3
prob += x[0] + x[1] <= 1

# Method 1: Set initial values via bounds (CBC)
x[0].lowBound = 1; x[0].upBound = 1   # fix at 1
x[2].lowBound = 0; x[2].upBound = 0    # fix at 0

# Method 2: Use setInitialValue + fixValue
x[3].setInitialValue(1)
x[3].fixValue()

# Solve with warm start enabled
prob.solve(COIN_CMD(msg=True, warmStart=True))
```

For Python API solvers, access solver-specific variable objects after solve:

```python
solver = pulp.GUROBI()
prob.solve(solver)

# After solve, access solver-specific variable objects
for v in prob.variables():
    gurobi_var = v.solverVar  # Gurobi variable object
    print(gurobi_var.X)       # solution value
```

## Model Debugging

### Inspecting the Model

```python
# Print model as string (objective + constraints)
print(prob)

# Write to file for external inspection
prob.writeLP("debug.lp")

# List all constraints
for name, constraint in prob.constraints.items():
    print(f"  {name}: {constraint}")

# List all variables
for v in prob.variables():
    print(f"  {v.name}: [{v.lowBound}, {v.upBound}] cat={v.cat} fixed={v.isFixed()}")

# Check objective
print("Objective:", prob.objective)
```

### Common Debugging Checklist

1. **Verify variable bounds** — ensure `lowBound`/`upBound` are correct
2. **Check constraint sense** — `<=`, `>=`, `==` match intent
3. **Validate dimensions** — indexed variables match parameter shapes
4. **Test with small data** — solve with minimal instances first
5. **Check solver availability** — `pulp.listSolvers(onlyAvailable=True)`
6. **Enable solver output** — `msg=True` to see solver log
7. **Write LP file** — `prob.writeLP("debug.lp")` and inspect manually

## Common Patterns

### Conditional / If-Then Logic

Model logical conditions using binary variables:

```python
from pulp import *

x = LpVariable("x", lowBound=0, upBound=100)
y = LpVariable("y", lowBound=0, upBound=50)
z = LpVariable("z", cat='Binary')  # 1 if x > 50

M = 100  # big-M constant

prob = LpProblem("Conditional", LpMaximize)

# If z=1 then x >= 50; if z=0 then x <= 50
prob += x >= 50 - M*(1-z), "IfZ0_xLE50"
prob += x <= 50 + M*z, "IfZ1_xGE50"

# y = 10 when z=1, else y = 0
prob += y <= 10*z
prob += y >= 10*z - M*(1-z)

prob.solve()
```

### SOS (Special Ordered Sets)

Not directly supported in PuLP's core API, but achievable with binary variables:

```python
# SOS-1: at most one variable can be non-zero
# Use binary selection:
k = 3  # number of alternatives
selected = LpVariable.dicts("Sel", range(k), cat='Binary')
values = LpVariable.dicts("Val", range(k), lowBound=0)

prob += lpSum(selected[i] for i in range(k)) <= 1  # at most one active
for i in range(k):
    prob += values[i] <= M * selected[i]  # value only if selected
```

### Piecewise Linear Functions

Approximate non-linear functions with piecewise linear segments:

```python
from pulp import *

# Approximate f(x) = x^2 over [0, 10] using 5 breakpoints
breakpoints = [0, 2, 4, 6, 8, 10]
f_values = [b**2 for b in breakpoints]
n = len(breakpoints)

# Weights for lambda interpolation
lam = LpVariable.dicts("lambda", range(n), lowBound=0)
# Adjacency: at most 2 adjacent lambdas can be non-zero (SOS-2)
# PuLP doesn't have native SOS-2, use binary variables

adj = LpVariable.dicts("Adj", range(n-1), cat='Binary')

prob = LpProblem("Piecewise", LpMinimize)

# Convex combination
prob += lpSum(lam[i] for i in range(n)) == 1, "SumLam"
prob += lpSum(breakpoints[i]*lam[i] for i in range(n)) == 5, "XValue"
prob += lpSum(f_values[i]*lam[i] for i in range(n)), "YApprox"

# Adjacency constraints
for i in range(n-1):
    prob += lam[i] + lam[i+1] <= adj[i] + adj[i-1] if i > 0 else prob += lam[i] + lam[i+1] <= adj[i]

prob.solve()
```

## Performance Tips

### Reduce Model Size

```python
# BAD: Creating too many variables
# x = LpVariable.dicts("x", all_combinations, lowBound=0)  # millions of vars

# GOOD: Use aggregation or smarter formulation
# Group similar items, use fewer decision dimensions
```

### Solver Selection

| Problem Size | Recommended Solver |
|-------------|-------------------|
| Small LP (< 100 vars) | Default (CBC) |
| Medium LP (< 10K vars) | CBC, GLPK, or CPLEX/Gurobi if available |
| Large LP (> 10K vars) | CPLEX, Gurobi, MOSEK |
| Small MIP (< 500 vars) | CBC |
| Medium MIP (< 5K vars) | Gurobi, CPLEX, SCIP |
| Large MIP (> 5K vars) | Gurobi, CPLEX, COPT |

### Time Limits and Tolerances

```python
# Always set time limits for production models
solver = pulp.GUROBI(timeLimit=3600, mipGap=0.01)
prob.solve(solver)

# Relaxed gap for quick feasibility checks
quick_solver = pulp.COIN_CMD(gapRel=0.1, timeLimit=30)
```

## Troubleshooting

### Solver Not Found

```python
import pulp

# Check what's available
print(pulp.listSolvers(onlyAvailable=True))

# If solver missing, install it:
# CBC: bundled with PuLP (Linux/macOS/Windows)
# GLPK: sudo apt install glpk-utils  or  brew install glpk
# Gurobi: pip install pulp[gurobi]
# CPLEX: pip install pulp[cplex]  (Python < 3.12 on macOS)
# MOSEK: pip install pulp[mosek]
# HiGHS: pip install pulp[highs]
```

### Infeasible Model

1. Check all constraint directions (`<=` vs `>=`)
2. Verify bounds don't conflict (e.g., `lowBound=10, upBound=5`)
3. Relax constraints one at a time to find culprit
4. Use feasibility relaxation if solver supports it

### Unbounded Model

- Check for missing constraints that should bound variables
- Verify objective direction matches constraint sense
- Add explicit bounds: `upBound` on all variables

### Slow Solving

- Set `timeLimit` to prevent indefinite solving
- Tighten `mipGap` only when needed
- Try different solver — some outperform others on specific problem types
- Use `warmStart=True` with initial values
- Reduce model size: fewer variables, aggregated constraints
