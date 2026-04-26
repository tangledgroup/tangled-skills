# Constraints

## Adding Constraints

Constraints are linear expressions with a relational operator (`<=`, `>=`, or `==`). They are added to the problem using `+=`:

```python
from pulp import *

prob = LpProblem("Example", LpMinimize)
x = LpVariable("x", 0, 4)
y = LpVariable("y", -1, 1)
z = LpVariable("z", 0, cat=LpInteger)

# Less than or equal
prob += x + y <= 5, "c1"

# Greater than or equal
prob += x + z >= 10, "c2"

# Equality
prob += -y + z == 7.5, "c3"
```

The second argument (a string name) is optional but recommended for debugging and solver output clarity.

## Constraint Senses

Each constraint has a sense:

- `-1` for `<=` constraints
- `1` for `>=` constraints
- `0` for `==` constraints

Access the constraint object via `prob.constraints[name]`:

```python
c = prob.constraints["c1"]
print(c.sense)  # -1 for <=
```

## Dual Values (Shadow Prices) and Reduced Costs

After solving, each constraint has a dual value (`pi`) representing the shadow price — how much the objective would improve per unit relaxation of the constraint:

```python
prob.solve()

# Shadow price of constraint c1
shadow_price = prob.constraints["c1"].pi

# Reduced cost of variable x
reduced_cost = x.dj
```

Shadow prices are meaningful for LP problems. For MIP problems, they may not be available or meaningful depending on the solver.

## Accessing Constraints from LpProblem

The `prob.constraints` attribute provides access to all constraints in model order:

```python
for constraint in prob.constraints:
    print(constraint.name, constraint.sense)
```

## Common Constraint Patterns

### Sum constraints with lpSum()

```python
# All ingredients must sum to 100%
prob += lpSum([ingredient_vars[i] for i in Ingredients]) == 100

# Total production cannot exceed capacity
prob += lpSum([production[t][u] for u in units]) <= max_capacity
```

### Conditional constraints with Big-M

For "if-then" logic, use binary variables with large coefficients:

```python
M = 10000  # Big-M value
y = LpVariable("activate", cat="Binary")
x = LpVariable("production", 0)

# If y=1, then x >= min_production; if y=0, constraint is relaxed
prob += x >= min_production * y
prob += x <= M * y
```

### Linking continuous and binary variables

Common in unit commitment problems:

```python
# Production p[t][i] must be 0 if unit i is off (d[t][i] = 0)
# and between pmin and pmax if unit i is on (d[t][i] = 1)
for t in time:
    for i in units:
        prob += p[t][i] <= pmax[i] * d[t][i]   # upper bound link
        prob += p[t][i] >= pmin[i] * d[t][i]   # lower bound link
```

### Exactly-one constraints

Ensure exactly one option is selected from a set:

```python
# Each guest seated at exactly one table
for guest in guests:
    prob += lpSum([x[table] for table in possible_tables if guest in table]) == 1
```

## Debugging Infeasible Problems

When a model returns `Infeasible`:

1. **Add slack variables** — Replace hard constraints with soft ones using penalty variables to identify which constraint causes infeasibility.

2. **Remove constraints incrementally** — Comment out constraints one by one until the problem becomes feasible, then isolate the culprit.

3. **Export and inspect** — Use `prob.writeLP("debug.lp")` to open the LP file in a text editor and verify constraints are built correctly.

4. **Check solver logs** — Pass `msg=True` to the solver for detailed output:

```python
prob.solve(COIN_CMD(msg=True))
```

5. **Check numerical precision** — Very large numbers (e.g., 100000000000) alongside small decimals can cause numerical issues. Round values when possible.

6. **Check for duplicated variables or constraints** — Variables with identical coefficients across all constraints and the objective, or duplicate constraints, can confuse solvers.
