# Case Studies

> **Source:** PuLP Documentation — CaseStudies/
> **Loaded from:** SKILL.md (via progressive disclosure)

## Blending Problem

A classic LP problem: blend raw materials to produce a final product at minimum cost while meeting quality specifications.

**Whiskas Cat Food Example:**
```python
from pulp import *

# Minimize cost of cat food ingredients
prob = LpProblem("The Whiskas Problem", LpMinimize)

x1 = LpVariable("ChickenPercent", 0, None, LpInteger)  # % chicken
x2 = LpVariable("BeefPercent", 0)                       # % beef

# Minimize cost
prob += 0.013 * x1 + 0.008 * x2

# Constraints
prob += x1 + x2 == 100, "Sum"
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "Protein"
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "Fat"
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "Fibre"
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "Salt"

prob.solve()
```

## Transportation Problem

Ship goods from multiple sources (factories) to multiple destinations (warehouses) at minimum cost, subject to supply and demand constraints.

**Structure:**
- Decision variables: `x[i,j]` = amount shipped from factory i to warehouse j
- Objective: minimize total shipping cost
- Constraints: supply limits at each factory, demand requirements at each warehouse

## Set Partitioning Problem (Wedding Seating)

Assign guests to tables so that each guest sits at exactly one table, minimizing total "unhappiness."

```python
import pulp

max_tables = 5
max_table_size = 4
guests = 'A B C D E F G I J K L M N O P Q R'.split()

def happiness(table):
    return abs(ord(table[0]) - ord(table[-1]))

# Generate all possible table combinations
possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]

model = pulp.LpProblem("Wedding_Seating", pulp.LpMinimize)

# Binary: 1 if this table arrangement is used
x = model.add_variable_dict('table', possible_tables, lowBound=0, upBound=1,
                            cat=pulp.LpInteger)

# Minimize total unhappiness
model += pulp.lpSum([happiness(table) * x[table] for table in possible_tables])

# At most max_tables tables
model += pulp.lpSum([x[table] for table in possible_tables]) <= max_tables

# Each guest seated at exactly one table
for guest in guests:
    model += pulp.lpSum([x[table] for table in possible_tables if guest in table]) == 1

model.solve()
```

## Two-Stage Stochastic Programming

Make decisions in stages: first-stage decisions before uncertainty is resolved, second-stage (recourse) decisions after.

**Gemstone Tools Example:**
- First stage: how many tools to produce (before knowing demand)
- Second stage: recourse actions (buy/sell) after demand realization
- Models expected value over multiple scenarios

## Sudoku as LP

Formulate Sudoku as a pure integer program with binary variables `x[i,j,k]` = 1 if cell (i,j) contains digit k.

**Constraints:**
- Each cell gets exactly one digit
- Each row contains each digit exactly once
- Each column contains each digit exactly once
- Each 3×3 box contains each digit exactly once

```python
from pulp import *

N = 9
prob = LpProblem("Sudoku", LpMinimize)

x = {}
for i in range(N):
    for j in range(N):
        for k in range(1, N + 1):
            x[i, j, k] = prob.add_variable(f"x_{i}_{j}_{k}", cat=LpBinary)

# Each cell gets exactly one value
for i in range(N):
    for j in range(N):
        prob += lpSum(x[i, j, k] for k in range(1, N + 1)) == 1

# Each value once per row
for i in range(N):
    for k in range(1, N + 1):
        prob += lpSum(x[i, j, k] for j in range(N)) == 1

# Each value once per column
for j in range(N):
    for k in range(1, N + 1):
        prob += lpSum(x[i, j, k] for i in range(N)) == 1

# Each value once per 3x3 box
for b in range(3):
    for r in range(3):
        for k in range(1, N + 1):
            prob += lpSum(x[3*b+r//3, 3*b*3+r%3*3+c, k]
                         for c in range(3)) == 1

# Add given clues (example)
clues = {(0,0): 5, (0,1): 3, ...}  # (row, col): value
for (i, j), v in clues.items():
    prob += x[i, j, v] == 1

prob.solve()
```

## Sponge Roll Cutting Stock Problem

Minimize waste when cutting large rolls of material into smaller required widths. Multiple cutting patterns are generated, and the problem decides how many rolls to cut using each pattern.

**Pattern generation:** Enumerate all feasible cutting patterns (combinations of required widths that fit in one roll).

```python
from pulp import *

# Widths needed and their demands
widths = [100, 80, 60]
demands = [50, 100, 200]
roll_width = 200

# Generate cutting patterns (manually or programmatically)
patterns = [(2, 0, 0), (1, 1, 0), (1, 0, 1), (0, 2, 0), (0, 1, 1), (0, 0, 3)]

prob = LpProblem("SpongeRoll", LpMinimize)

# How many rolls to cut using each pattern
x = prob.add_variables("pattern", len(patterns), cat=LpInteger, lowBound=0)

# Minimize total rolls used
prob += lpSum(x[i] for i in range(len(patterns)))

# Meet demand for each width
for w_idx, (w, d) in enumerate(zip(widths, demands)):
    pattern_contribution = sum(p[w_idx] * x[i] for i, p in enumerate(patterns))
    prob += pattern_contribution >= d, f"demand_{w}"

prob.solve()
```

## Computer Plant Problem

Production planning: decide how many computers to produce at each plant, using regular and overtime hours, to meet demand at minimum cost. Includes capacity constraints, labor limits, and demand satisfaction.

## Furniture Problem

Classic LP: determine the optimal product mix for a furniture manufacturer. Each product type consumes different amounts of wood, finishing time, and carpentry time. Constraints on available resources; objective is to maximize profit.

## American Steel Problem

Production scheduling for a steel company. Decisions include how much steel to produce in each time period, inventory levels, and production rates. Includes setup costs, production capacity, and demand constraints across multiple time periods.

## Beer Distribution Problem

Multi-echelon supply chain optimization: brewery → distributor → pub. Models inventory flow, backlogging, and cost minimization across the distribution network. Extensions include competitor response and warehouse capacity constraints.

## References

- Blending: https://coin-or.github.io/pulp/CaseStudies/a_blending_problem.html
- Transportation: https://coin-or.github.io/pulp/CaseStudies/a_transportation_problem.html
- Set Partitioning: https://coin-or.github.io/pulp/CaseStudies/a_set_partitioning_problem.html
- Sudoku: https://coin-or.github.io/pulp/CaseStudies/a_sudoku_problem.html
- Two-Stage Planning: https://coin-or.github.io/pulp/CaseStudies/a_two_stage_production_planning_problem.html
- All examples: https://github.com/coin-or/pulp/tree/3.3.0/examples
