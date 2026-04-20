---
name: pulp-3-3-0
description: Complete toolkit for PuLP 3.3.0, a Python linear and mixed-integer programming (MIP) modeling library that generates MPS/LP files and calls solvers like CBC, GLPK, CPLEX, Gurobi, MOSEK, and COPT. Use when formulating optimization problems in Python, solving LP/MIP models, working with variables/constraints/objectives, configuring solver backends, or performing sensitivity/what-if analysis on linear programs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.3.0"
tags:
  - linear-programming
  - optimization
  - mip
  - operations-research
  - python
category: programming
external_references:
  - https://coin-or.github.io/pulp/
  - https://github.com/coin-or/pulp/tree/3.3.0
---

# PuLP 3.3.0

PuLP (Python Linear Programming) is an LP modeler written in Python. It generates MPS or LP files and calls solvers such as CBC, GLPK, CPLEX, Gurobi, MOSEK, COPT, CHOCO, MIPCL, and SCIP to solve linear programming and mixed-integer programming problems.

## When to Use

- Formulating and solving linear programming (LP) problems in Python
- Mixed-integer programming (MIP) with binary, integer, or continuous variables
- Transportation, blending, scheduling, assignment, and resource allocation problems
- Sensitivity analysis on optimal solutions
- Model export to MPS/LP/JSON formats for external solver use
- Multi-scenario stochastic optimization

## Core Concepts

### Problem Types

| Type | Description | Variables |
|------|-------------|-----------|
| LP (Linear Program) | All variables continuous, linear objective/constraints | Continuous only |
| MIP (Mixed Integer) | Some variables restricted to integer values | Mixed continuous + integer |
| Binary MIP | All variables restricted to {0, 1} | Binary only |

### Mathematical Form

A standard LP has the form:

```
minimize (or maximize)   c^T * x
subject to               A * x <= b
                         lb <= x <= ub
```

PuLP models this through three building blocks: **variables**, **objective function**, and **constraints**.

### Solver Architecture

PuLP separates model formulation from solving. Solvers integrate via two patterns:

- **CMD solvers** - invoke solver as external binary (e.g., `COIN_CMD`, `GLPK_CMD`, `CPLEX_CMD`). Configured via `path=` for custom binary location.
- **Python API solvers** - use solver's Python library directly (e.g., `GUROBI`, `CPLEX_PY`, `MOSEK`). Accessed as solver objects.

Check available solvers:

```python
import pulp
# All registered solvers
print(pulp.listSolvers())
# Only installed/available solvers
print(pulp.listSolvers(onlyAvailable=True))
# Get solver by name with arguments
solver = pulp.getSolver('COIN_CMD', timeLimit=60)
```

## Installation

```bash
pip install pulp                    # Core library (CBC binary bundled for Linux/macOS/Windows)
uvx pip install "pulp"              # With uv
```

### Solver Extras

| Extra | Package | Description |
|-------|---------|-------------|
| `gurobi` | `gurobipy` | Gurobi Python API |
| `cplex` | `cplex` | CPLEX Python API (Python < 3.12 on macOS) |
| `mosek` | `mosek` | MOSEK Python API |
| `xpress` | `xpress` | FICO Xpress Python API |
| `copt` | `coptpy` | COPT Python API |
| `scip` | `pyscipopt` | SCIP Python API |
| `highs` | `highspy` | HiGHS solver |
| `open_py` | `cylp`, `highspy`, `pyscipopt` | Open-source Python APIs |
| `public_py` | `gurobipy`, `coptpy`, `xpress`, `cplex` | Public Python APIs |

```bash
pip install pulp[gurobi]            # Gurobi support
pip install pulp[cplex]             # CPLEX support (Python < 3.12 on macOS)
pip install pulp[mosek]             # MOSEK support
pip install pulp[highs]             # HiGHS support
```

PuLP requires **Python 3.9+**. CBC is bundled with PuLP for Linux (i32/i64/arm64), macOS (i64), and Windows (i32/i64).

## Quick Start

### Basic LP - Dog Food Problem (Whiskas)

Minimize cost of dog food while meeting nutritional requirements:

```python
from pulp import *

# Create problem: minimize cost
prob = LpProblem("The Whiskas Problem", LpMinimize)

# Decision variables: % of chicken and beef per can
x1 = LpVariable("ChickenPercent", lowBound=0, cat='Integer')  # >= 0
x2 = LpVariable("BeefPercent", lowBound=0)                      # >= 0 (no upper bound)

# Objective: minimize cost (costs per unit)
prob += 0.013 * x1 + 0.008 * x2, "Total Cost"

# Constraints
prob += x1 + x2 == 100, "PercentagesSum"                          # must sum to 100%
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "ProteinRequirement"     # >= 8% protein
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "FatRequirement"         # >= 6% fat
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "FibreRequirement"       # <= 2% fibre
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "SaltRequirement"        # <= 0.4% salt

# Solve with default solver
prob.solve()

# Results
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(f"  {v.name} = {v.varValue}")
print("Total Cost =", value(prob.objective))
```

### MIP - Sudoku Solver

Use binary variables and `lpSum` for constraint programming:

```python
from pulp import *

VALS = ROWS = COLS = range(1, 10)
Boxes = [
    [(3*i + k + 1, 3*j + l + 1) for k in range(3) for l in range(3)]
    for i in range(3) for j in range(3)
]

prob = LpProblem("Sudoku Problem")

# Binary decision variables: value v at position (r, c)
choices = LpVariable.dicts("Choice", (VALS, ROWS, COLS), cat='Binary')

# Each cell has exactly one value
for r in ROWS:
    for c in COLS:
        prob += lpSum(choices[v][r][c] for v in VALS) == 1

# Each value appears once per row, column, and box
for v in VALS:
    for r in ROWS:
        prob += lpSum(choices[v][r][c] for c in COLS) == 1
    for c in COLS:
        prob += lpSum(choices[v][r][c] for r in ROWS) == 1
    for b in Boxes:
        prob += lpSum(choices[v][r][c] for (r, c) in b) == 1

# Fixed clues as constraints
clues = [(5,1,1),(6,2,1),(8,4,1),(4,5,1),(7,6,1),
         (3,1,2),(9,3,2),(6,7,2),(8,3,3),(1,2,4)]
for v, r, c in clues:
    prob += choices[v][r][c] == 1

prob.solve()

# Extract solution
solution = [[value(choices[v][r][c]) for v in VALS] for r in ROWS for c in COLS]
```

## Variables

### Creating Variables

```python
from pulp import *

# Single variable: name, lowBound, upBound, category
x = LpVariable("x", lowBound=0, upBound=10, cat='Continuous')   # 0 <= x <= 10
y = LpVariable("y", lowBound=0, cat='Integer')                  # y >= 0, integer
z = LpVariable("z", cat='Binary')                               # z in {0, 1}
w = LpVariable("w")                                             # free (unbounded)

# Dictionary of variables (common pattern for indexed models)
prices = ["wrenches", "pliers"]
production = LpVariable.dicts("Prod", prices, lowBound=0, cat='Continuous')

# Multi-dimensional variables via nested dicts
rows, cols = range(3), range(4)
x_matrix = {r: LpVariable.dicts(f"x_{r}", cols, lowBound=0) for r in rows}

# Access
print(production["wrenches"])     # LpVariable object
print(x.varValue)                 # value after solve
print(z.isFixed())                # True if fixed
```

### Variable Categories (`cat`)

| Category | Values | Use case |
|----------|--------|----------|
| `'Continuous'` | (-∞, ∞) or bounded range | Standard LP variables |
| `'Integer'` | {..., -2, -1, 0, 1, 2, ...} | MIP: counts, quantities |
| `'Binary'` | {0, 1} | MIP: yes/no, on/off, selection |

### Fixing Variable Values

```python
x.fixValue()           # Fixes to initial bound value
# or set bounds equal:
x = LpVariable("x", lowBound=5, upBound=5)  # effectively fixed at 5
```

## Problem Object

### Creating and Configuring Problems

```python
from pulp import *

# Create problem with name and objective sense
prob = LpProblem("MyProblem", LpMinimize)   # or LpMaximize

# Key attributes (after solve):
prob.status       # solver status code
prob.objective    # LpAffineExpression - the objective
prob.constraints  # dict of constraint names -> LpConstraint objects
prob.variables()  # list of all LpVariable objects in model
```

### Adding Variables and Constraints

```python
# Add variable directly to problem (preferred pattern)
x = prob.add_variable("x", lowBound=0, cat='Continuous')

# Or create standalone, then add to problem
y = LpVariable("y", lowBound=0)
prob += y

# Add constraint: prob += expression + name_string
prob += x + y <= 10, "capacity_limit"

# Constraints use comparison operators directly on expressions:
prob += lpSum(x[i] for i in range(5)) >= 100, "demand"
prob += x * 2 + y * 3 == 10, "equality"
```

### Setting the Objective

```python
# Method 1: add to problem with += (also works as constraint)
prob += 3*x + 5*y, "TotalProfit"

# Method 2: setObjective
prob.setObjective(3*x + 5*y)
```

### Solving

```python
# Solve with default solver
prob.solve()

# Solve with specific solver
solver = pulp.GUROBI(timeLimit=300, mip= True)
prob.solve(solver)

# Or inline
prob.solve(pulp.COIN_CMD(timeLimit=60, msg=False))

# Check status
print(LpStatus[prob.status])
# 'Optimal', 'Not Solved', 'Infeasible', 'Unbounded', 'Undefined'
```

### LpStatus Codes

| Code | Constant | Meaning |
|------|----------|---------|
| 0 | `LpStatusNotSolved` | Model not solved yet |
| 1 | `LpStatusOptimal` | Optimal solution found |
| -1 | `LpStatusInfeasible` | No feasible solution |
| -2 | `LpStatusUnbounded` | Objective unbounded |
| -3 | `LpStatusUndefined` | Solver returned undefined status |

## Expressions and Constraints

### LpAffineExpression

Linear combinations of variables: `a1x1 + a2x2 + ... + c`

```python
from pulp import *

x = LpVariable("x")
y = LpVariable("y")

# Creation methods
expr1 = x + 2*y + 3                    # arithmetic
expr2 = lpSum([x, y, 2*x])             # sum a list
expr3 = LpAffineExpression.from_dict({x: 2, y: 3})  # dict of {var: coeff}
expr4 = LpAffineExpression.empty()     # empty expression

# Use in constraints
prob += expr1 <= 10, "my_constraint"
```

### lpSum

Sums a list/vector of variables or expressions - the most common aggregation function:

```python
# Sum all x[i] for i in range(n)
prob += lpSum(x[i] for i in range(10)) >= 50, "total_demand"

# Weighted sum (common in objectives)
costs = [1.2, 0.8, 1.5]
prob += lpSum(c * x[i] for i, c in enumerate(costs)), "total_cost"
```

### Adding Constraints

```python
# Syntax: prob += expression + "constraint_name"
# The comparison operator (=, <=, >=) sets the constraint sense

prob += x + y == 100, "sum_to_100"       # equality
prob += 2*x + 3*y <= 50, "resource_limit" # less-than-or-equal
prob += x >= 5, "min_x"                   # greater-than-or-equal

# Indexed constraints (common pattern)
demands = [10, 20, 15]
for i, d in enumerate(demands):
    prob += lpSum(x[i][j] for j in range(3)) >= d, f"demand_{i}"

# Access constraints after creation
print(prob.constraints["resource_limit"])  # LpConstraint object
```

### Getting Solution Values

```python
# After solving:
for v in prob.variables():
    print(f"{v.name} = {v.varValue}")

# Or using value() function
x_val = value(x)        # returns float or None if not solved
obj_val = value(prob.objective)

# Shadow prices (dual values) and slack - access via solver-specific attributes
```

## Solvers

### Solver Configuration

Every solver accepts common parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `mip` | bool | If False, treat as LP even with integer vars (default True) |
| `msg` | bool | Show solver output/log (default True) |
| `timeLimit` | float | Max solve time in seconds |
| `path` | str | Path to solver binary (CMD solvers only) |
| `options` | list[str] | Extra solver-specific options |

### CMD Solvers (Command-Line)

```python
from pulp import *

# CBC - default open-source solver (included with PuLP via cbcbox)
prob.solve(pulp.COIN_CMD(timeLimit=60, msg=True))

# GLPK
prob.solve(pulp.GLPK_CMD(path='/usr/bin/glpk', timeLimit=120))

# CPLEX
prob.solve(pulp.CPLEX_CMD(timeLimit=300, mip=True, gapRel=0.01))

# Gurobi
prob.solve(pulp.GUROBI_CMD(timeLimit=600, mipGap=0.001))

# SCIP
prob.solve(pulp.SCIP_CMD(timeLimit=120))
```

### Python API Solvers

```python
from pulp import *

# Gurobi (requires gurobipy installed)
gurobi_solver = pulp.GUROBI(timeLimit=300, mipGap=0.01, msg=True)
prob.solve(gurobi_solver)

# CPLEX (requires cplex installed)
cplex_solver = pulp.CPLEX_PY(timeLimit=300, gapRel=0.001)
prob.solve(cplex_solver)

# MOSEK (requires mosek installed)
mosek_solver = pulp.MOSEK(msg=True)
prob.solve(mosek_solver)

# COPT (Requires copt installed)
copt_solver = pulp.COPT(timeLimit=300, mipGap=0.01)
prob.solve(copt_solver)
```

### Solver Parameters (Python API)

Solver-specific parameters can be passed as kwargs:

```python
# Gurobi parameters via dot notation
solver = pulp.GUROBI(
    timeLimit=300,
    mipGap=0.01,
    threads=4,
    logPath="/tmp/gurobi.log"
)

# CPLEX parameters via dot notation
solver = pulp.CPLEX_PY(
    timeLimit=300,
    gapRel=0.001,
    advance=1,           # equivalent to parameters.advance = 1
    barrier_algorithm=1  # equivalent to parameters.barrier.algorithm = 1
)
```

## Model Export and Import

### Export Formats

```python
# Write .lp file (PuLP native format)
prob.writeLP("model.lp")

# Write .mps file
prob.writeMPS("model.mps", mpsSense=0, rename=True, mip=True)

# Write JSON
prob.toJson("model.json")
```

### Import from JSON

```python
# Load model and variables from JSON file
variables_dict, loaded_prob = LpProblem.fromJson("model.json")
```

## Advanced Patterns

### Indexed/Parametric Models

The recommended pattern for real-world models uses dictionaries and list comprehensions:

```python
from pulp import *

# Parameters
plants = ["Seattle", "San_Diego"]
markets = ["New_York", "Chicago", "Topeka"]
capacity = {"Seattle": 355, "San_Diego": 600}
demand = {"New_York": 325, "Chicago": 300, "Topeka": 275}
distance = {
    ("Seattle", "New_York"): 2.5, ("Seattle", "Chicago"): 1.7,
    ("Seattle", "Topeka"): 1.8,   ("San_Diego", "New_York"): 2.5,
    ("San_Diego", "Chicago"): 1.8, ("San_Diego", "Topeka"): 1.4
}
freight = 90  # cost per unit per 1000 miles

# Decision variables: shipments from each plant to each market
shipments = LpVariable.dicts("Ship", (plants, markets), lowBound=0, cat='Continuous')

# Problem
prob = LpProblem("Transportation Problem", LpMinimize)

# Objective: minimize total shipping cost
prob += lpSum(
    shipments[i][j] * distance[i][j] * freight / 1000
    for i in plants for j in markets
), "TotalCost"

# Supply constraints
for i in plants:
    prob += lpSum(shipments[i][j] for j in markets) <= capacity[i], f"Supply_{i}"

# Demand constraints
for j in markets:
    prob += lpSum(shipments[i][j] for i in plants) == demand[j], f"Demand_{j}"

prob.solve()
```

### Stochastic / Two-Stage Optimization

```python
from pulp import *

# First stage: decision before uncertainty is resolved
steel = LpVariable("SteelPurchase", lowBound=0, cat='Continuous')

# Second stage: decisions after scenario realization
scenarios = [0, 1, 2, 3]
products = ["wrenches", "pliers"]
production_vars = LpVariable.dicts("Prod", (scenarios, products), lowBound=0)

# Scenario probabilities and returns
probabilities = [0.25, 0.25, 0.25, 0.25]
returns = {0: [160, 100], 1: [160, 100], 2: [90, 100], 3: [90, 100]}

prob = LpProblem("Stochastic Production", LpMaximize)

# Objective: expected profit minus steel cost
prob += lpSum(
    probabilities[s] * (returns[s][0]*production_vars[s][0] + returns[s][1]*production_vars[s][1])
    for s in scenarios
) - steel * 58, "ExpectedProfit"

# First-stage constraint: steel budget
prob += steel <= 27, "SteelBudget"

# Second-stage constraints per scenario
for s in scenarios:
    prob += production_vars[s][0] + production_vars[s][1] <= 21, f"Molding_{s}"
```

### MIP Start (Warm Start)

Pre-assign variable values before solving to guide the solver:

```python
from pulp import *

prob = LpProblem("MIPStart", LpMinimize)
x = LpVariable.dicts("x", range(5), cat='Binary')
prob += lpSum(x[i] for i in range(5)) >= 3
prob += x[0] + x[1] <= 1

# Set initial values (MIP start)
x[0].lowBound = 1; x[0].upBound = 1  # fix to 1
# or set bounds to same value for warm start hint

prob.solve(pulp.COIN_CMD(warmStart=True))
```

### Debugging and Inspection

```python
# Print model as string
print(prob)

# Write model to file for inspection
prob.writeLP("debug.lp")

# List all constraints with names
for name, c in prob.constraints.items():
    print(f"  {name}: {c}")

# Check solver availability
import pulp
solvers = pulp.listSolvers(onlyAvailable=True)
print(f"Available solvers: {solvers}")

# Get solver by name
solver = pulp.getSolver('COIN_CMD', timeLimit=60, msg=False)
```

## Reference Files

- [`references/01-solver-reference.md`](references/01-solver-reference.md) - Complete solver API reference, all solver classes and parameters
- [`references/02-examples.md`](references/02-examples.md) - Worked examples: transportation, blending, scheduling, stochastic optimization
- [`references/03-guides.md`](references/03-guides.md) - Solver configuration, MIP start, model export/debugging

## References

- Official documentation: https://coin-or.github.io/pulp/
- GitHub repository: https://github.com/coin-or/pulp
- API reference: https://coin-or.github.io/pulp/technical/pulp.html
- Solvers guide: https://coin-or.github.io/pulp/technical/solvers.html
