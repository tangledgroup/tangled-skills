---
name: pulp-3-3-0
description: Complete toolkit for PuLP 3.3.0, a Python linear and mixed-integer programming (MIP) modeler that generates MPS/LP/JSON files and calls solvers like CBC, GLPK, CPLEX, Gurobi, MOSEK, HiGHS, COPT, SCIP, XPRESS, CHOCO, and MIPCL. Use when formulating optimization problems in Python, solving LP/MIP models, working with variables/constraints/objectives, configuring solver backends, or performing model export/import for external solver use.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - optimization
  - linear-programming
  - mixed-integer-programming
  - lp
  - mip
  - operations-research
category: data-science
external_references:
  - https://coin-or.github.io/pulp/
  - https://github.com/coin-or/pulp/tree/3.3.0/examples
  - https://www.coin-or.org/
  - https://github.com/coin-or/pulp/tree/3.3.0
---

# PuLP 3.3.0

## Overview

PuLP is a linear and mixed-integer programming modeler written in Python. It enables developers to formulate optimization problems as mathematical models, then call external solvers (CBC, GLPK, CPLEX, Gurobi, MOSEK, HiGHS, COPT, SCIP, XPRESS, CHOCO, MIPCL, and others) to find optimal solutions. PuLP generates intermediate MPS or LP files and handles solver communication transparently.

Version 3.3.0 includes a Rust extension (`pulp._rustcore`) that implements the core model, variables, constraints, and affine expressions for improved performance. CBC is no longer bundled — install it separately via `pulp[cbc]` or place `cbc`/`cbc.exe` on your `PATH`.

PuLP requires Python 3.9 or newer. It supports Windows, macOS (x86_64, arm64), and Linux (x86_64, arm64).

## When to Use

- Formulating linear programming (LP) or mixed-integer programming (MIP) models in Python
- Solving blending, transportation, assignment, scheduling, cutting stock, set partitioning, and production planning problems
- Building models with large numbers of indexed variables using dictionary/matrix patterns
- Exporting models to LP, MPS, or JSON format for external solver use
- Performing column generation, two-stage stochastic programming, or constraint-based feasibility problems (e.g., Sudoku)
- Configuring and switching between multiple solver backends (CBC, GLPK, CPLEX, Gurobi, HiGHS, etc.)

## Core Concepts

**LpProblem** — The central model container. Created with a name and sense (`LpMinimize` or `LpMaximize`). Holds variables, the objective function, and constraints.

**LpVariable** — Decision variables. Three categories: `LpContinuous` (default), `LpInteger`, and `LpBinary`. Each has a name, optional lower/upper bounds, and a category.

**Objective Function** — A linear expression added to the problem with `+=`. Defines what to minimize or maximize.

**Constraints** — Linear expressions ending in `<=`, `>=`, or `==`. Added to the problem with `+=` along with an optional name string.

**lpSum()** — Efficiently sums a list of linear expressions or variables. Preferred over Python's built-in `sum()` for PuLP expressions.

**LpVariable.dicts() / LpVariable.matrix()** — Factory methods that create indexed dictionaries or matrices of variables, essential for problems with many decision variables.

**Solver** — External optimization engine (CBC, GLPK, CPLEX, Gurobi, etc.). PuLP communicates via command-line (`_CMD`) or Python API interfaces. `prob.solve()` uses the default available solver.

## Installation / Setup

Install from PyPI (recommended with CBC):

```python
# With pip
python -m pip install "pulp[cbc]"

# With uv
uv pip install "pulp[cbc]"
```

The `[cbc]` extra installs the `cbcbox` package, which bundles a CBC binary that PuLP resolves automatically. Without it, you must provide your own `cbc` on `PATH` or use another solver.

Building from source requires Rust (latest stable) and uses `maturin` for the Rust extension:

```bash
uv venv
uv pip install --group dev -e ".[cbc]"
# or with pip:
python -m pip install -e ".[cbc]"
```

## Usage Examples

### Basic LP — Minimization

```python
from pulp import *

prob = LpProblem("test1", LpMinimize)

x = LpVariable("x", 0, 4)    # 0 <= x <= 4
y = LpVariable("y", -1, 1)   # -1 <= y <= 1
z = LpVariable("z", 0)       # 0 <= z

# Objective: minimize x + 4*y + 9*z
prob += x + 4 * y + 9 * z, "obj"

# Constraints
prob += x + y <= 5, "c1"
prob += x + z >= 10, "c2"
prob += -y + z == 7, "c3"

prob.writeLP("test1.lp")
prob.solve()

print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("objective =", value(prob.objective))
```

### Blending Problem — Whiskas Cat Food

Minimize ingredient cost while meeting nutritional requirements:

```python
from pulp import *

Ingredients = ["CHICKEN", "BEEF", "MUTTON", "RICE", "WHEAT", "GEL"]

costs = {"CHICKEN": 0.013, "BEEF": 0.008, "MUTTON": 0.010,
         "RICE": 0.002, "WHEAT": 0.005, "GEL": 0.001}

proteinPercent = {"CHICKEN": 0.100, "BEEF": 0.200, "MUTTON": 0.150,
                  "RICE": 0.000, "WHEAT": 0.040, "GEL": 0.000}

fatPercent = {"CHICKEN": 0.080, "BEEF": 0.100, "MUTTON": 0.110,
              "RICE": 0.010, "WHEAT": 0.010, "GEL": 0.000}

ingredient_vars = LpVariable.dicts("Ingr", Ingredients, 0)

prob = LpProblem("Whiskas", LpMinimize)

# Minimize total cost
prob += lpSum([costs[i] * ingredient_vars[i] for i in Ingredients])

# Percentages must sum to 100
prob += lpSum([ingredient_vars[i] for i in Ingredients]) == 100

# Protein >= 8%
prob += lpSum([proteinPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 8.0

# Fat >= 6%
prob += lpSum([fatPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 6.0

prob.solve()
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(v.name, "=", v.varValue)
```

### Transportation Problem — Beer Distribution

Ship crates from warehouses to bars at minimum cost:

```python
from pulp import *

Warehouses = ["A", "B"]
supply = {"A": 1000, "B": 4000}
Bars = ["1", "2", "3", "4", "5"]
demand = {"1": 500, "2": 900, "3": 1800, "4": 200, "5": 700}

costs = [
    # Bars:  1  2  3  4  5
    [2, 4, 5, 2, 1],   # A
    [3, 1, 3, 2, 3],   # B
]
costs_dict = makeDict([Warehouses, Bars], costs, 0)

prob = LpProblem("Beer Distribution", LpMinimize)

Routes = [(w, b) for w in Warehouses for b in Bars]
vars = LpVariable.dicts("Route", (Warehouses, Bars), 0, None, LpInteger)

# Minimize transport cost
prob += lpSum([vars[w][b] * costs_dict[w][b] for (w, b) in Routes])

# Supply constraints
for w in Warehouses:
    prob += lpSum([vars[w][b] for b in Bars]) <= supply[w]

# Demand constraints
for b in Bars:
    prob += lpSum([vars[w][b] for w in Warehouses]) >= demand[b]

prob.solve()
print("Status:", LpStatus[prob.status])
```

### Sudoku as a Feasibility Problem

No objective function needed — just find values satisfying all constraints:

```python
from pulp import *

VALS = ROWS = COLS = range(1, 10)

Boxes = [
    [(3*i+k+1, 3*j+l+1) for k in range(3) for l in range(3)]
    for i in range(3) for j in range(3)
]

prob = LpProblem("Sudoku")

choices = LpVariable.dicts("Choice", (VALS, ROWS, COLS), cat="Binary")

# One value per square
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v][r][c] for v in VALS]) == 1

# Each value once per row, column, and box
for v in VALS:
    for r in ROWS:
        prob += lpSum([choices[v][r][c] for c in COLS]) == 1
    for c in COLS:
        prob += lpSum([choices[v][r][c] for r in ROWS]) == 1
    for b in Boxes:
        prob += lpSum([choices[v][r][c] for (r, c) in b]) == 1

# Starting numbers as constraints
input_data = [(5,1,1), (6,2,1), (8,4,1), (4,5,1), (7,6,1),
              (3,1,2), (9,3,2), (6,7,2)]
for v, r, c in input_data:
    prob += choices[v][r][c] == 1

prob.solve()
print("Status:", LpStatus[prob.status])
```

## Advanced Topics

**Variables and Expressions**: LpVariable categories, bounds, `LpVariable.dicts()`, `LpVariable.matrix()`, `LpAffineExpression`, `lpSum()`, `lpDot()` → [Variables and Expressions](reference/01-variables-and-expressions.md)

**Constraints**: LpConstraint, constraint senses, named constraints, dual values (shadow prices), reduced costs → [Constraints](reference/02-constraints.md)

**Solvers**: COIN_CMD (CBC), GLPK_CMD, CPLEX_CMD, GUROBI, HiGHS, MOSEK, SCIP, COPT, XPRESS, CHOCO, solver configuration, environment variables, `listSolvers()`, `getSolver()` → [Solvers](reference/03-solvers.md)

**Model Export and Import**: writeLP(), writeMPS(), toJson()/fromJson(), to_dict()/from_dict(), JSON vs MPS trade-offs → [Model Export and Import](reference/04-model-export-import.md)

**Utility Functions**: makeDict, splitDict, allcombinations, allpermutations, value(), roundSolution() → [Utility Functions](reference/05-utility-functions.md)

**Case Studies**: Blending, transportation, set partitioning (wedding seating), cutting stock with column generation, two-stage stochastic programming, Sudoku, production planning, generation scheduling → [Case Studies](reference/06-case-studies.md)
