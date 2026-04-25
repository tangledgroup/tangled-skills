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
  - https://github.com/coin-or/pulp/tree/3.3.0/examples
  - https://www.coin-or.org/
  - https://github.com/coin-or/pulp/tree/3.3.0
---
## Overview
PuLP is a linear and mixed integer programming modeler written in Python. With PuLP, it is simple to create MILP optimisation problems and solve them with the latest open-source (or proprietary) solvers. PuLP can generate MPS or LP files and call solvers such as GLPK, COIN-OR CLP/CBC, CPLEX, GUROBI, MOSEK, HiGHS, CHOCO, MIPCL, SCIP/FSCIP, COPT, and XPRESS.

PuLP is part of the COIN-OR project. It requires Python 3.9 or newer.

## When to Use
- Formulating and solving linear programming (LP) or mixed-integer programming (MIP) problems in Python
- Creating optimization models for production planning, scheduling, transportation, blending, resource allocation
- Need to switch between multiple solvers (CBC, GLPK, Gurobi, CPLEX, HiGHS, etc.) without changing model code
- Exporting/importing optimization models in MPS, LP, or JSON formats
- Performing post-optimal analysis (sensitivity, shadow prices, reduced costs)
- Working with integer, binary, or continuous decision variables

## Core Concepts
### Problem Types

**Linear Programming (LP):** Decision variables are real-valued; objective and constraints are linear expressions of the form `a1*x1 + a2*x2 + ... + an*xn <=/=/>= b`.

**Integer Programming (IP):** Some or all decision variables must take integer values. Solved using branch-and-bound.

**Mixed Integer Programming (MIP):** A mix of continuous and integer variables. Most industrial MIPs are difficult problems — solution time grows exponentially with the number of integer variables.

### The Modeling Process

1. **Identify Decision Variables** — what you can control (with clear units)
2. **Formulate Objective Function** — minimize cost or maximize profit using decision variables
3. **Formulate Constraints** — logical and problem-specific restrictions
4. **Identify Data** — variable bounds, coefficients for objective and constraints

### Essential Classes

| Class | Purpose |
|-------|---------|
| `LpProblem` | Container for a linear or integer programming problem |
| `LpVariable` | Decision variables added into constraints (created via `LpProblem.add_variable()`) |
| `LpAffineExpression` | Linear combination of variables + constant; carries constraint sense for pending constraints |
| `LpConstraint` | Constraint of the general form `sum(a_i * x_i) <=/=/>= b` backed by Rust |

### Key Constants

**Problem sense:**
- `LpMinimize` (= 1) — minimize objective
- `LpMaximize` (= -1) — maximize objective

**Variable categories:**
- `LpContinuous` — "Continuous" (default)
- `LpInteger` — "Integer"
- `LpBinary` — "Binary"

**Constraint senses:**
- `LpConstraintEQ` (= 0) — equality (`==`)
- `LpConstraintLE` (= -1) — less-than-or-equal (`<=`)
- `LpConstraintGE` (= 1) — greater-than-or-equal (`>=`)

**Solution status:**
- `LpStatusOptimal` (= 1) — "Optimal"
- `LpStatusNotSolved` (= 0) — "Not Solved"
- `LpStatusInfeasible` (= -1) — "Infeasible"
- `LpStatusUnbounded` (= -2) — "Unbounded"
- `LpStatusUndefined` (= -3) — "Undefined"

## Installation / Setup
```bash
# Core installation
pip install pulp

# With CBC solver (default, recommended for most users)
pip install pulp[cbc]

# With specific solvers
pip install pulp[gurobi]   # Gurobi
pip install pulp[cplex]    # CPLEX
pip install pulp[xpress]   # FICO XPRESS
pip install pulp[scip]     # SCIP
pip install pulp[highs]    # HiGHS
pip install pulp[copt]     # COPT
pip install pulp[mosek]    # MOSEK
pip install pulp[cylp]     # COIN-OR Cylp

# All open-source solvers at once
pip install pulp[open_py]
```

## Usage Examples
### Basic Problem (Whiskas Cat Food — Minimization)

```python
from pulp import *

# Create the problem: minimize cost
prob = LpProblem("The Whiskas Problem", LpMinimize)

# Decision variables: x1 = ChickenPercent (integer, >= 0), x2 = BeefPercent (>= 0)
x1 = LpVariable("ChickenPercent", 0, None, LpInteger)
x2 = LpVariable("BeefPercent", 0)

# Objective: minimize total ingredient cost
prob += 0.013 * x1 + 0.008 * x2, "Total Cost of Ingredients per can"

# Constraints
prob += x1 + x2 == 100, "PercentagesSum"
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "ProteinRequirement"
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "FatRequirement"
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "FibreRequirement"
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "SaltRequirement"

# Solve with default solver
prob.solve()

print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("Total Cost =", value(prob.objective))
```

### Maximization Problem (Simple)

```python
from pulp import *

prob = LpProblem("Maximize Example", LpMaximize)

x = LpVariable("x", 0, 4)      # 0 <= x <= 4
y = LpVariable("y", -1, 1)     # -1 <= y <= 1
z = LpVariable("z", 0)         # z >= 0 (no upper bound)

# Objective
prob += x + 4 * y + 9 * z, "Objective"

# Constraints
prob += x + y <= 5, "c1"
prob += x + z >= 10, "c2"
prob += -y + z == 7, "c3"

prob.solve()
print("Status:", LpStatus[prob.status])
print("x =", value(x), "y =", value(y), "z =", value(z))
print("Objective =", value(prob.objective))
```

### Binary Variables and Dictionary-Indexed Variables

```python
from pulp import *

# Create binary variables indexed by a list
items = ["A", "B", "C", "D"]
x = LpProblem("SetCover", LpMinimize)
x_vars = x.add_variable_dict("x", items, cat=LpBinary)

# Add constraints referencing dictionary keys
for item in items:
    x += x_vars[item] <= 1, f"constraint_{item}"

# Or use add_variables for multiple variables at once
y = LpProblem("MultiVar", LpMinimize)
a, b, c = y.add_variables("abc", lowBound=0)
```

### Using Different Solvers

```python
from pulp import *

prob = LpProblem("SolverTest", LpMinimize)
x = prob.add_variable("x", 0, 10)
prob += x

# Use CBC (default)
prob.solve()

# Explicitly specify a solver
prob.solve(GLPK_CMD(msg=0))        # GLPK, suppress output
prob.solve(COIN_CMD())             # CBC
prob.solve(GUROBI())               # Gurobi Python API
prob.solve(HiGHS())                # HiGHS Python API
prob.solve(CPLEX_CMD(path="/path/to/cplex"))  # CPLEX with explicit path

# Check solver availability
available = listSolvers(onlyAvailable=True)
print("Available:", available)

# Get solver by name
solver = getSolver("GUROBI", timeLimit=60)
prob.solve(solver)
```

### Export and Import Models

```python
from pulp import *

prob = LpProblem("ExportTest", LpMinimize)
x = prob.add_variable("x", 0, 4)
y = prob.add_variable("y", -1, 1)
z = prob.add_variable("z", 0, None, LpInteger)
prob += x + 4 * y + 9 * z, "obj"
prob += x + y <= 5, "c1"
prob += x + z >= 10, "c2"

# Export to LP file
prob.writeLP("model.lp")

# Export to MPS file
prob.writeMPS("model.mps")

# Export to JSON (preserves all model info including solution)
prob.to_json("model.json")

# Export to dictionary
data = prob.to_dict()

# Import from JSON
var_dict, prob_restored = LpProblem.from_json("model.json")

# Import from MPS
var_dict, prob_restored = LpProblem.fromMPS("model.mps")
```

### Multi-dimensional Variables (Sudoku Example)

```python
from pulp import *

N = 9
prob = LpProblem("Sudoku", LpMinimize)

# Binary variables: x[i,j,k] = 1 if cell (i,j) has value k
x = {}
for i in range(N):
    for j in range(N):
        for k in range(1, N + 1):
            x[i, j, k] = prob.add_variable(f"x_{i}_{j}_{k}", cat=LpBinary)

# Each cell gets exactly one value
for i in range(N):
    for j in range(N):
        prob += lpSum(x[i, j, k] for k in range(1, N + 1)) == 1, f"cell_{i}_{j}"

# Each value appears once per row
for i in range(N):
    for k in range(1, N + 1):
        prob += lpSum(x[i, j, k] for j in range(N)) == 1, f"row_{i}_val_{k}"

# Each value appears once per column
for j in range(N):
    for k in range(1, N + 1):
        prob += lpSum(x[i, j, k] for i in range(N)) == 1, f"col_{j}_val_{k}"

prob.solve()
```

## Advanced Topics
## Advanced Topics

- [Solvers And Configuration](reference/01-solvers-and-configuration.md)
- [Export Import Utilities](reference/02-export-import-utilities.md)
- [Case Studies](reference/03-case-studies.md)
- [Api Reference](reference/04-api-reference.md)

