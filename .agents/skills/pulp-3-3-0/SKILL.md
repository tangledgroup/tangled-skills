---
name: pulp-3-3-0
description: Complete toolkit for PuLP 3.3.0, a Python linear and mixed-integer programming (MIP) modeling library that generates MPS/LP/JSON files and calls solvers like CBC, GLPK, CPLEX, Gurobi, MOSEK, HiGHS, COPT, and SCIP. Use when formulating optimization problems in Python, solving LP/MIP models, working with variables/constraints/objectives, configuring solver backends, or performing model export/import for external solver use.
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

PuLP (Python Linear Programming) is an LP modeler written in Python. It generates MPS, LP, or JSON files and calls solvers such as CBC, GLPK, CPLEX, Gurobi, MOSEK, COPT, CHOCO, MIPCL, HiGHS, SCIP, and XPRESS to solve linear programming (LP) and mixed-integer programming (MIP) problems.

## When to Use

- Formulating and solving linear programming (LP) problems in Python
- Mixed-integer programming (MIP) with binary, integer, or continuous variables
- Transportation, blending, scheduling, assignment, set partitioning, and resource allocation problems
- Model export/import to MPS/LP/JSON formats for external solver use
- Multi-scenario stochastic optimization
- MIP warm-starting (providing initial feasible solutions to guide the solver)

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

- **CMD solvers** — invoke solver as external binary (e.g., `COIN_CMD`, `GLPK_CMD`, `CPLEX_CMD`). Configured via `path=` for custom binary location.
- **Python API solvers** — use solver's Python library directly (e.g., `GUROBI`, `CPLEX_PY`, `MOSEK`). Accessed as solver objects.

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
pip install pulp                    # Core library
uv pip install pulp                 # With uv
```

### CBC Solver

> **Important:** CBC is no longer bundled with PuLP. Install it via the `cbc` extra or ensure the `cbc` binary is on your system `PATH`.

```bash
pip install pulp[cbc]               # Bundled CBC binary (via cbcbox wheel)
# OR: install cbc separately and ensure it's on PATH
sudo apt install coinor-cbc         # Debian/Ubuntu
brew install coin-or-cbc            # macOS
```

### Solver Extras

| Extra | Package | Description |
|-------|---------|-------------|
| `cbc` | `cbcbox` | Bundled CBC binary (replaces PULP_CBC_CMD) |
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

PuLP requires **Python 3.9+**.

## Quick Start — Blending Problem (Canonical Example)

The official PuLP case study: minimize cost of cat food while meeting nutritional requirements.

### Simplified Version (2 Ingredients)

```python
from pulp import *

# Create problem: minimize cost
prob = LpProblem("The Whiskas Problem", LpMinimize)

# Decision variables: % of chicken and beef per can
x1 = LpVariable("ChickenPercent", lowBound=0, cat='Integer')
x2 = LpVariable("BeefPercent", lowBound=0)

# Objective: minimize cost (costs per gram)
prob += 0.013 * x1 + 0.008 * x2, "Total Cost of Ingredients per can"

# Constraints
prob += x1 + x2 == 100, "PercentagesSum"
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "ProteinRequirement"
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "FatRequirement"
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "FibreRequirement"
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "SaltRequirement"

# Solve
prob.solve()

# Results
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(f"  {v.name} = {v.varValue}")
print("Total Cost =", value(prob.objective))
```

**Optimal solution:** Chicken = 33.33%, Beef = 66.67%, Total cost = $0.96/can.

### Full Version (All Six Ingredients)

```python
from pulp import *

# Parameters
Ingredients = ["CHICKEN", "BEEF", "MUTTON", "RICE", "WHEAT", "GEL"]
costs = {
    "CHICKEN": 0.013, "BEEF": 0.008, "MUTTON": 0.010,
    "RICE": 0.002, "WHEAT": 0.005, "GEL": 0.001
}
proteinPercent = {
    "CHICKEN": 0.100, "BEEF": 0.200, "MUTTON": 0.150,
    "RICE": 0.000, "WHEAT": 0.040, "GEL": 0.000
}
fatPercent = {
    "CHICKEN": 0.080, "BEEF": 0.100, "MUTTON": 0.110,
    "RICE": 0.010, "WHEAT": 0.010, "GEL": 0.000
}
fibrePercent = {
    "CHICKEN": 0.001, "BEEF": 0.005, "MUTTON": 0.003,
    "RICE": 0.100, "WHEAT": 0.150, "GEL": 0.000
}
saltPercent = {
    "CHICKEN": 0.002, "BEEF": 0.005, "MUTTON": 0.007,
    "RICE": 0.002, "WHEAT": 0.008, "GEL": 0.000
}

# Decision variables: percentage of each ingredient
ingredient_vars = prob.add_variable_dict(
    "Ingr", Ingredients, lowBound=0, cat='Continuous'
)

prob = LpProblem("The Whiskas Problem", LpMinimize)

# Objective: minimize total cost
prob += lpSum(costs[i] * ingredient_vars[i] for i in Ingredients), "Total Cost"

# Constraints
prob += lpSum(ingredient_vars[i] for i in Ingredients) == 100, "PercentagesSum"
prob += lpSum(proteinPercent[i] * ingredient_vars[i] for i in Ingredients) >= 8.0, "ProteinRequirement"
prob += lpSum(fatPercent[i] * ingredient_vars[i] for i in Ingredients) >= 6.0, "FatRequirement"
prob += lpSum(fibrePercent[i] * ingredient_vars[i] for i in Ingredients) <= 2.0, "FibreRequirement"
prob += lpSum(saltPercent[i] * ingredient_vars[i] for i in Ingredients) <= 0.4, "SaltRequirement"

prob.solve()
for i in Ingredients:
    print(f"  {i}: {value(ingredient_vars[i]):.1f}%")
print(f"Total Cost: ${value(prob.objective):.2f}")
```

**Optimal solution:** 60% Beef, 40% Gel — Total cost = $0.52/can.

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
| `'Continuous'` (or `LpContinuous`) | (-∞, ∞) or bounded range | Standard LP variables |
| `'Integer'` (or `LpInteger`) | {..., -2, -1, 0, 1, 2, ...} | MIP: counts, quantities |
| `'Binary'` | {0, 1} | MIP: yes/no, on/off, selection |

### Variable Dictionary Methods

```python
# prob.add_variable_dict(prefix, keys, lowBound=0, upBound=None, cat='Continuous')
x = prob.add_variable_dict("Prod", ["A", "B", "C"], lowBound=0)
print(x["A"])       # LpVariable object

# Matrix-style variable dicts (nested keys)
y = prob.add_variable_dict("Ship", (plants, markets), lowBound=0)
print(y["Seattle"]["New_York"])  # specific variable

# Tuples as composite keys (common in transportation / assignment)
z = prob.add_variable_dict("Route", (Warehouses, Bars), 0, None, LpInteger)
print(z["A", "1"])  # route from warehouse A to bar 1
```

### Fixing Variable Values

```python
x.fixValue()           # Fixes to initial bound value (sets lb == ub == current value)
# or set bounds equal:
x = LpVariable("x", lowBound=5, upBound=5)  # effectively fixed at 5
# Check if fixed:
print(x.isFixed())     # True if lowBound == upBound
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
solver = pulp.GUROBI(timeLimit=300, mip=True)
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

Linear combinations of variables: `a1x1 + a2x2 + ... + c`. A thin wrapper around Rust's `AffineExpr`.

```python
from pulp import *

x = LpVariable("x")
y = LpVariable("y")

# Creation methods
expr1 = x + 2*y + 3                    # arithmetic
expr2 = lpSum([x, y, 2*x])             # sum a list
expr3 = LpAffineExpression.from_dict({x: 2, y: 3})  # dict of {var: coeff}
expr4 = LpAffineExpression.empty()     # empty expression
expr5 = LpAffineExpression.from_variable(x)  # single variable
expr6 = LpAffineExpression.from_constant(5)  # constant only

# Use in constraints
prob += expr1 <= 10, "my_constraint"
```

### lpSum

Sums a list/vector of variables or expressions — the most common aggregation function:

```python
# Sum all x[i] for i in range(n)
prob += lpSum(x[i] for i in range(10)) >= 50, "total_demand"

# Weighted sum (common in objectives)
costs = [1.2, 0.8, 1.5]
prob += lpSum(c * x[i] for i, c in enumerate(costs)), "total_cost"
```

### Getting Solution Values

```python
# After solving:
for v in prob.variables():
    print(f"{v.name} = {v.varValue}")

# Or using value() function — returns float or None if not solved,
# or returns the number itself if given a numeric argument
x_val = value(x)               # returns float or None
obj_val = value(prob.objective)
scalar = value(42)             # returns 42 (passthrough for numbers)
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

# CBC — default open-source solver (install via pip install pulp[cbc])
prob.solve(pulp.COIN_CMD(timeLimit=60, msg=True))

# GLPK
prob.solve(pulp.GLPK_CMD(path='/usr/bin/glpk', timeLimit=120))

# CPLEX
prob.solve(pulp.CPLEX_CMD(timeLimit=300, mip=True, gapRel=0.01))

# Gurobi
prob.solve(pulp.GUROBI_CMD(timeLimit=600, mipGap=0.001))

# HiGHS
prob.solve(HiGHS_CMD(path='/usr/bin/highs', timeLimit=120))

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

# COPT (requires coptpy installed)
copt_solver = pulp.COPT(timeLimit=300, mipGap=0.01)
prob.solve(copt_solver)

# HiGHS (requires highspy installed)
highs_solver = HiGHS(timeLimit=300, msg=True, parallel='off')
prob.solve(highs_solver)
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
# Write .lp file (PuLP native format) — returns list of variables
variables = prob.writeLP("model.lp")

# Write .mps file — returns (var_names, con_names, obj_name, pulp_names)
result = prob.writeMPS("model.mps", mpsSense=0, rename=True, mip=True)

# Write JSON — preserves complete model state including solution values
prob.toJson("model.json")

# Export to dictionary (in-memory)
data = prob.to_dict()
```

### Import from File

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

- **JSON format** preserves complete model state including status, solution values, shadow prices, and reduced costs. It is the most comprehensive format.
- **MPS format** is an industry standard but only stores variables, constraints, and objective — it does not store variable values or shadow prices.
- **Variable names must be unique** for import/export to work correctly (PuLP uses internal IDs, but these are not exported).
- Variables are exported flat — if you had nested dictionaries, grouping is not restored automatically.
- For JSON export with NumPy/pandas data types, provide a custom encoder:

```python
import json, numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

prob.toJson("model.json", cls=NpEncoder)
```

## Advanced Patterns

### Set Partitioning — Wedding Seating Problem

Determine optimal guest seating to maximize table happiness (from official case study). A set partitioning problem partitions items into subsets where every item appears in exactly one subset.

```python
import pulp

max_tables = 5
max_table_size = 4
guests = "A B C D E F G I J K L M N O P Q R".split()

def happiness(table):
    """Max distance between first and last letter of table."""
    return abs(ord(table[0]) - ord(table[-1]))

# Generate all possible table combinations (up to max_table_size guests per table)
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]

prob = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

# Binary variable: 1 if this table configuration is used
_table_keys = ["_".join(t) for t in possible_tables]
vars_by_key = prob.add_variable_dict(
    "table_%s", (_table_keys,), lowBound=0, upBound=1, cat=pulp.LpInteger
)
x = {t: vars_by_key["_".join(t)] for t in possible_tables}

# Objective: minimize total unhappiness (sum of max distances per table)
prob += pulp.lpSum([happiness(table) * x[table] for table in possible_tables])

# At most max_tables tables
prob += pulp.lpSum([x[table] for table in possible_tables]) <= max_tables, "MaxTables"

# Each guest seated at exactly one table (set partitioning constraint)
for guest in guests:
    prob += pulp.lpSum([x[table] for table in possible_tables if guest in table]) == 1, f"Must_seat_{guest}"

prob.solve()
print(f"The chosen tables are out of a total of {len(possible_tables)}:")
for table in possible_tables:
    if x[table].value() == 1.0:
        print(table)
```

### Sudoku Solver (Constraint Satisfaction via LP)

Sudoku is modeled as a pure constraint satisfaction problem with no objective function. Binary variables encode "cell (r,c) has value v".

```python
from pulp import *

# All rows, columns and values within a Sudoku take values from 1 to 9
VALS = ROWS = COLS = range(1, 10)

# Boxes list: row and column indices of each square in each 3x3 box
Boxes = [
    [(3 * i + k + 1, 3 * j + l + 1) for k in range(3) for l in range(3)]
    for i in range(3) for j in range(3)
]

# No objective function — this is a constraint satisfaction problem
prob = LpProblem("Sudoku Problem")

# Binary decision variables: choices[v, r, c] = 1 if value v is at (r, c)
choices = prob.add_variable_dict("Choice", (VALS, ROWS, COLS), 0, 1, LpBinary)

# Each cell has exactly one value
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v, r, c] for v in VALS]) == 1

# Each value appears once per row, column, and box
for v in VALS:
    for r in ROWS:
        prob += lpSum([choices[v, r, c] for c in COLS]) == 1
    for c in COLS:
        prob += lpSum([choices[v, r, c] for r in ROWS]) == 1
    for b in Boxes:
        prob += lpSum([choices[v, r, c] for (r, c) in b]) == 1

# Given clues as constraints
input_data = [
    (5, 1, 1), (6, 2, 1), (8, 4, 1), (4, 5, 1), (7, 6, 1),
    (3, 1, 2), (9, 3, 2), (6, 7, 2), (8, 3, 3), (1, 2, 4),
    (8, 5, 4), (4, 8, 4), (7, 1, 5), (9, 2, 5), (6, 4, 5),
    (2, 6, 5), (1, 8, 5), (8, 9, 5), (5, 2, 6), (3, 5, 6),
    (9, 8, 6), (2, 7, 7), (6, 3, 8), (8, 7, 8), (7, 9, 8),
    (3, 4, 9), (1, 5, 9), (6, 6, 9), (5, 8, 9),
]
for v, r, c in input_data:
    prob += choices[v, r, c] == 1

prob.solve()
print("Status:", LpStatus[prob.status])
```

**Key insight:** Sudoku uses **no objective function**. PuLP allows this — the solver simply finds any feasible solution satisfying all constraints. To enumerate multiple solutions, add a constraint excluding the found solution and re-solve:

```python
# Exclude current solution and find next one
prob += lpSum([
    choices[v, r, c] for v in VALS for r in ROWS for c in COLS
    if value(choices[v, r, c]) == 1
]) <= 80  # At most 80 of 81 cells match
```

### Two-Stage Stochastic Production Planning

GTC produces wrenches and pliers. Steel is purchased now; assembly capacity and earnings are uncertain and revealed next period. This is a **two-stage stochastic program** with recourse.

```python
import pulp

# --- First-stage parameters (known now) ---
products = ["wrenches", "pliers"]
steel = [1.5, 1]          # steel per unit
molding = [1, 1]          # molding hours per unit
assembly = [0.3, 0.5]     # assembly hours per unit
cap_steel = 27            # total steel available
cap_molding = 21          # molding capacity
capacity_ub = [15, 16]    # max demand per product
steelprice = 58           # cost per unit of steel

# --- Scenario parameters (uncertain, known next period) ---
scenarios = [0, 1, 2, 3]
pscenario = [0.25, 0.25, 0.25, 0.25]
wrenchearnings = [160, 160, 90, 90]
plierearnings = [100, 100, 100, 100]
capassembly = [8, 10, 8, 10]   # assembly capacity per scenario

# Build parameter dictionaries
production = [(j, i) for j in scenarios for i in products]
price_dict = {
    (j, i): (wrenchearnings[j], plierearnings[j])[i]
    for j in scenarios for i in products
}
capacity_dict = dict(zip(products, capacity_ub * 4))
steel_dict = dict(zip(products, steel))
molding_dict = dict(zip(products, molding))
assembly_dict = dict(zip(products, assembly))

# --- Model ---
prob = pulp.LpProblem("Gemstone Tool Problem", pulp.LpMaximize)

# Second-stage variables: production quantity per scenario
production_vars = prob.add_variable_dict(
    "production", (scenarios, products), 0, None, pulp.LpContinuous
)

# First-stage variable: steel to purchase
steelpurchase = prob.add_variable("steelpurchase", 0, None, pulp.LpContinuous)

# Objective: expected profit minus steel cost
prob += (
    pulp.lpSum([
        pscenario[j] * price_dict[(j, i)] * production_vars[j, i]
        for (j, i) in production
    ]) - steelpurchase * steelprice,
    "TotalProfit"
)

# Per-scenario constraints
for j in scenarios:
    prob += pulp.lpSum([
        steel_dict[i] * production_vars[j, i] for i in products
    ]) - steelpurchase <= 0, f"Steel_{j}"
    prob += pulp.lpSum([
        molding_dict[i] * production_vars[j, i] for i in products
    ]) <= cap_molding, f"Molding_{j}"
    prob += pulp.lpSum([
        assembly_dict[i] * production_vars[j, i] for i in products
    ]) <= capassembly[j], f"Assembly_{j}"
    for i in products:
        prob += production_vars[j, i] <= capacity_dict[i], f"Demand_{j}_{i}"

prob.solve()
print("Status:", pulp.LpStatus[prob.status])
for v in prob.variables():
    print(f"  {v.name} = {v.varValue}")
print("Total Profit =", pulp.value(prob.objective))
```

### MIP Start (Warm Start)

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

### Debugging and Inspection

```python
# Print model as string (objective + constraints)
print(prob)

# Write model to file for external inspection
variables = prob.writeLP("debug.lp")

# List all constraints with names
for name, c in prob.constraints.items():
    print(f"  {name}: {c}")

# Check solver availability
import pulp
solvers = pulp.listSolvers(onlyAvailable=True)
print(f"Available solvers: {solvers}")

# Get solver by name
solver = pulp.getSolver('COIN_CMD', timeLimit=60, msg=False)

# Round solution to integer (for MIP problems)
prob.roundSolution()
```

## Utility Functions

### Combinations and Permutations

```python
from pulp import *

# Fixed-length combinations
list(combination(range(4), 3))   # [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]

# All combinations up to length k
list(allcombinations([1,2,3,4], 2))
# [(1,), (2,), (3,), (4,), (1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]

# Fixed-length permutations
list(permutation(range(3), 2))   # [(0,1), (0,2), (1,0), (1,2), (2,0), (2,1)]

# All permutations up to length k
list(allpermutations([1,2,3], 2))
# [(1,), (2,), (3,), (1,2), (1,3), (2,1), (2,3), (3,1), (3,2)]
```

### Value Function

```python
from pulp import *

x = LpVariable("x")
prob += x == 42
prob.solve()

# value(x) returns the solution value, or x if it's a number
value(x)           # 42.0
value(3.14)        # 3.14 (passthrough)
value(prob.objective)  # objective value after solve
```

## Reference Files

- [`references/01-solver-reference.md`](references/01-solver-reference.md) — Complete solver API reference, all solver classes and parameters
- [`references/02-examples.md`](references/02-examples.md) — Worked examples: transportation (beer distribution), blending, assignment, production planning, knapsack, diet, facility location
- [`references/03-guides.md`](references/03-guides.md) — Solver configuration, MIP start, model export/debugging, conditional logic, SOS, piecewise linear, performance tips

## Ecosystem Plugins

| Plugin | Description |
|--------|-------------|
| [**lparray**](https://github.com/qdbp/pulp-lparray) | NumPy-style arrays for PuLP variables. Broadcasting, reshaping, axis operations. Linearize min/max, abs, clip, boolean ops. |
| [**pytups**](https://pchtsp.github.io/pytups/) | `SuperDict` and `TupList` with pandas-like chaining. Transform nested dicts to flat lists and back. Works seamlessly with PuLP. |
| [**amply**](https://github.com/Pyomo/amply) | AMPL data manipulation. Load AMPL data files into PuLP models. Provides `makeDict()` for converting 2D cost matrices into nested dictionaries (used in the transportation case study). |
| [**orloge**](https://coin-or.github.io/pulp/plugins/orloge.html) | OR log parser for solver output analysis. |

## References

- Official documentation: https://coin-or.github.io/pulp/
- GitHub repository: https://github.com/coin-or/pulp
- API reference: https://coin-or.github.io/pulp/technical/pulp.html
- Solvers guide: https://coin-or.github.io/pulp/technical/solvers.html
- Case studies: https://coin-or.github.io/pulp/CaseStudies/index.html
