# Case Studies

## Blending Problem — Whiskas Cat Food

Minimize ingredient cost while meeting nutritional requirements. The classic introduction to LP modeling with PuLP.

**Simplified version** (two ingredients):

```python
from pulp import *

prob = LpProblem("Whiskas", LpMinimize)
x1 = LpVariable("ChickenPercent", 0, None, LpInteger)
x2 = LpVariable("BeefPercent", 0)

prob += 0.013 * x1 + 0.008 * x2, "Total Cost"
prob += x1 + x2 == 100, "PercentagesSum"
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "ProteinRequirement"
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "FatRequirement"
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "FibreRequirement"
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "SaltRequirement"

prob.solve()
print("Status:", LpStatus[prob.status])
```

**Full version** (six ingredients with `LpVariable.dicts()`):

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
prob = LpProblem("Whiskas Full", LpMinimize)

prob += lpSum([costs[i] * ingredient_vars[i] for i in Ingredients])
prob += lpSum([ingredient_vars[i] for i in Ingredients]) == 100
prob += lpSum([proteinPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 8.0
prob += lpSum([fatPercent[i] * ingredient_vars[i] for i in Ingredients]) >= 6.0
```

Key pattern: use dictionaries for data and `LpVariable.dicts()` for indexed variables, then build constraints with list comprehensions and `lpSum()`.

## Transportation Problem — Beer Distribution

Minimize shipping cost from warehouses to bars, respecting supply limits and demand requirements.

```python
from pulp import *

Warehouses = ["A", "B"]
supply = {"A": 1000, "B": 4000}
Bars = ["1", "2", "3", "4", "5"]
demand = {"1": 500, "2": 900, "3": 1800, "4": 200, "5": 700}

costs = [[2, 4, 5, 2, 1], [3, 1, 3, 2, 3]]
costs_dict = makeDict([Warehouses, Bars], costs, 0)

prob = LpProblem("Beer Distribution", LpMinimize)
vars = LpVariable.dicts("Route", (Warehouses, Bars), 0, None, LpInteger)

prob += lpSum([vars[w][b] * costs_dict[w][b] for w in Warehouses for b in Bars])

for w in Warehouses:
    prob += lpSum([vars[w][b] for b in Bars]) <= supply[w]
for b in Bars:
    prob += lpSum([vars[w][b] for w in Warehouses]) >= demand[b]

prob.solve()
```

Key pattern: double-indexed variables via `LpVariable.dicts((list1, list2))`, supply constraints summing over destinations, demand constraints summing over sources.

## Set Partitioning — Wedding Seating

Assign guests to tables to minimize total "happiness" (proxy for seating quality), ensuring each guest sits at exactly one table.

```python
import pulp

guests = "A B C D E F G I J K L M N O P Q R".split()
max_tables = 5
max_table_size = 4

def happiness(table):
    return abs(ord(table[0]) - ord(table[-1]))

possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]

x = pulp.LpVariable.dicts("table", possible_tables, 0, 1, pulp.LpInteger)

model = pulp.LpProblem("Wedding Seating", pulp.LpMinimize)
model += pulp.lpSum([happiness(t) * x[t] for t in possible_tables])

# Maximum number of tables
model += pulp.lpSum([x[t] for t in possible_tables]) <= max_tables

# Each guest at exactly one table
for guest in guests:
    model += pulp.lpSum([x[t] for t in possible_tables if guest in t]) == 1

model.solve()
```

Key pattern: enumerate all possible subsets with `allcombinations()`, create binary variables for each subset, use exactly-one constraints for set partitioning.

## Sudoku as Feasibility Problem

No objective function — just find any assignment satisfying all Sudoku rules. Uses 729 binary variables (9 values × 81 squares).

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

# Starting numbers
input_data = [(5,1,1), (6,2,1), (8,4,1), ...]
for v, r, c in input_data:
    prob += choices[v][r][c] == 1

prob.solve()
```

Key pattern: when no optimization objective exists, create `LpProblem` without `LpMinimize`/`LpMaximize` and add no objective — just constraints.

## Two-Stage Stochastic Programming — Gemstone Tools

A production planning problem with uncertain future parameters modeled as scenarios:

```python
import pulp

products = ["wrenches", "pliers"]
scenarios = [0, 1, 2, 3]
pscenario = [0.25, 0.25, 0.25, 0.25]
wrench_earnings = [160, 160, 90, 90]
plier_earnings = [100, 100, 100, 100]
cap_assembly = [8, 10, 8, 10]
steel = {"wrenches": 1.5, "pliers": 1}
molding = {"wrenches": 1, "pliers": 1}
assembly = {"wrenches": 0.3, "pliers": 0.5}

prob = pulp.LpProblem("Gemstone Tools", pulp.LpMaximize)

production = [(j, i) for j in scenarios for i in products]
prod_vars = prob.add_variable_dict("prod", (scenarios, products), 0, None, pulp.LpContinuous)
steel_purchase = prob.add_variable("steelpurchase", 0, None, pulp.LpContinuous)

# Expected revenue minus steel cost
earnings = {(j, i): wrench_earnings[j] if i == "wrenches" else plier_earnings[j]
            for j in scenarios for i in products}

prob += pulp.lpSum([pscenario[j] * earnings[(j, i)] * prod_vars[j, i]
                     for j, i in production]) - steel_purchase * 58

# Steel constraint per scenario
for j in scenarios:
    prob += pulp.lpSum([steel[i] * prod_vars[j, i] for i in products]) - steel_purchase <= 0
    # Assembly capacity per scenario
    prob += pulp.lpSum([assembly[i] * prod_vars[j, i] for i in products]) <= cap_assembly[j]

prob.solve()
```

Key pattern: create variables indexed by (scenario, product), weight objective by scenario probability, add scenario-specific constraints.

## Cutting Stock with Column Generation

The SpongeRoll problem uses a master-subproblem decomposition:

1. **Master problem** — Minimize rolls used, subject to meeting demand for each length
2. **Sub-problem** — Find new cutting patterns with negative reduced cost using dual values
3. Iterate until no improving pattern exists

```python
from pulp import *

class Pattern:
    totalRollLength = 20
    lenOpts = ["5", "7", "9"]

    def __init__(self, name, lengths):
        self.name = name
        self.lengthsdict = dict(zip(self.lenOpts, lengths))

def masterSolve(Patterns, rollDemand, relax=True):
    prob = LpProblem("Cutting Stock", LpMinimize)
    vartype = LpContinuous if relax else LpInteger

    pattVars = LpVariable.dicts("Pattern", Patterns, 0, None, vartype)

    # Minimize total rolls
    prob += lpSum([pattVars[i] for i in Patterns])

    # Meet demand for each length
    for j in Pattern.lenOpts:
        prob += lpSum([pattVars[i] * i.lengthsdict[j] for i in Patterns]) >= rollDemand[j]

    prob.solve()
    prob.roundSolution()

    if relax:
        duals = {j: prob.constraints[f"Min{j}"].pi for j in Pattern.lenOpts}
        return duals
```

Key pattern: solve relaxed master → extract duals → sub-problem finds new column → add to master → repeat until convergence.

## Deterministic Generation Planning

Schedule thermal units and hydro storage over time to minimize generation cost:

```python
from pulp import *
from math import sin

prob = LpProblem("Generation Planning", LpMinimize)

tmax = 9
units = 5
time = list(range(tmax))
unit = list(range(units))

# Demand profile (sinusoidal)
dmin, dmax = 10.0, 150.0
demand = [dmin + (dmax - dmin) * 0.5 + 0.5 * (dmax - dmin) * sin(4 * t * 2 * pi / tmax)
          for t in time]

# Production variables (continuous)
p = LpVariable.matrix("p", (time, unit), 0)
# State variables (binary: on/off)
d = LpVariable.matrix("d", (range(tmax + 1), unit), 0, 1, LpInteger)

# Production bounds linked to state
for t in time:
    for i in unit:
        prob += p[t][i] <= (dmax / units) * d[t][i]   # max if on
        prob += p[t][i] >= (dmax / (units * 3)) * d[t][i]  # min if on

# Startup variables
u = LpVariable.matrix("u", (time, unit), 0)
for t in time:
    for i in unit:
        prob += u[t][i] >= d[t + 1][i] - d[t][i]  # startup detection

# Objective: proportional cost + startup cost
costs = [i + 1 for i in unit]
startup_costs = [100 * (i + 1) for i in unit]
prob += lpSum([lpSum([p[t][i] for t in time]) * costs[i] for i in unit])
prob += lpSum([lpSum([u[t][i] for t in time]) * startup_costs[i] for i in unit])

# Demand satisfaction
for t in time:
    prob += lpSum([p[t][i] for i in unit]) >= demand[t]

prob.solve()
```

Key pattern: `LpVariable.matrix()` for time-series variables, binary state variables linked to continuous production via Big-M constraints.
