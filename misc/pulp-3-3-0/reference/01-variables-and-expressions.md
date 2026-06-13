# Variables and Expressions

## LpVariable Categories

Three categories control the domain of decision variables:

**LpContinuous** — Real-valued variables. Default category. Can take any value within bounds.

**LpInteger** — Integer-valued variables. Must take whole number values within bounds. Used for counting items, units, or discrete quantities.

**LpBinary** — Binary (0-1) variables. A special case of integer variables constrained to exactly 0 or 1. Used for yes/no decisions, activation flags, and logical constraints.

```python
from pulp import *

# Continuous variable: 0 <= x <= 4
x = LpVariable("x", lowBound=0, upBound=4, cat="Continuous")

# Integer variable: no lower bound, upper bound of 5
y = LpVariable("y", upBound=5, cat="Integer")

# Binary variable (equivalent to LpVariable("z", 0, 1, "Binary"))
z = LpVariable("z", cat="Binary")

# Using None for unbounded direction: -inf < w <= 0
w = LpVariable("w", None, 0)
```

In PuLP 3.3.0, variables are created through the problem object using `prob.add_variable()` or via factory methods on `LpVariable`. The older standalone `LpVariable()` constructor still works for backward compatibility.

## Creating Indexed Variables with LpVariable.dicts()

For problems with many indexed variables (e.g., one per product, route, or time period), use `LpVariable.dicts()`:

```python
# Single index — creates a flat dictionary
Ingredients = ["CHICKEN", "BEEF", "MUTTON"]
ingredient_vars = LpVariable.dicts("Ingr", Ingredients, lowBound=0)
# Access: ingredient_vars["CHICKEN"], ingredient_vars["BEEF"], etc.

# Double index — creates nested dictionaries
Warehouses = ["A", "B"]
Bars = ["1", "2", "3", "4", "5"]
vars = LpVariable.dicts("Route", (Warehouses, Bars), 0, None, LpInteger)
# Access: vars["A"]["1"], vars["B"]["3"], etc.

# Triple index — three nested levels
VALS = ROWS = COLS = range(1, 10)
choices = LpVariable.dicts("Choice", (VALS, ROWS, COLS), cat="Binary")
# Access: choices[5][3][7] — is value 5 in row 3, column 7?

# Using tuples as keys directly
possible_tables = [("Alice", "Bob"), ("Charlie", "Diana")]
x = LpVariable.dicts("table", possible_tables, 0, 1, LpInteger)
# Access: x[("Alice", "Bob")]
```

## Creating Matrix Variables with LpVariable.matrix()

For grid-like variable structures (time × unit, row × column), use `LpVariable.matrix()`:

```python
from pulp import *

# 2D matrix: time steps × thermal units
time = range(9)
unit = range(5)

# Continuous production variables, lower bound 0
p = LpVariable.matrix("p", (time, unit), lowBound=0)
# Access: p[3][2] — production at time 3, unit 2

# Binary state variables (on/off): time+1 × units (extra step for final state)
xtime = range(10)
d = LpVariable.matrix("d", (xtime, unit), 0, 1, LpInteger)
# Access: d[5][3] — is unit 3 on at time 5?

# 1D matrix (single list)
s = LpVariable.matrix("s", xtime, lowBound=0)
# Access: s[0], s[1], etc.
```

## LpAffineExpression

An `LpAffineExpression` represents a linear combination of variables plus a constant: `a1*x1 + a2*x2 + ... + constant`. It is created automatically when you combine variables with arithmetic operators.

```python
# These all create LpAffineExpression objects
expr1 = x + 4 * y + 9 * z
expr2 = lpSum([costs[i] * ingredient_vars[i] for i in Ingredients])

# Adding to problem as objective or constraint
prob += expr1, "objective name"
prob += expr2 <= 100, "constraint name"
```

## lpSum() — Efficient Summation

Use `lpSum()` instead of Python's built-in `sum()` for PuLP expressions. It avoids creating intermediate expression objects:

```python
# Preferred — efficient, single pass
total_cost = lpSum([costs[i] * vars[i] for i in Items])

# Also accepts plain numbers and variables directly
expr = lpSum([x, y, z, 5])  # x + y + z + 5

# Accepts (variable, coefficient) tuples
expr = lpSum([(x, 1), (y, 4), (z, 9)])  # 1*x + 4*y + 9*z
```

## lpDot() — Dot Product

Compute the dot product of a coefficient list and a variable list:

```python
from pulp import *

n = 15
x = LpVariable.matrix("x", list(range(n)), 0, 1, LpInteger)
a = [pow(2, k + n + 1) + pow(2, k + n + 1 - j) + 1 for j in range(1, n + 1)]

weight = lpDot(a, x)  # sum of a[i] * x[i] for all i
```

## Variable Properties

After solving, each variable exposes:

- `var.name` — The variable name string
- `var.varValue` — The optimal value (None if not solved)
- `var.lowBound` — Lower bound
- `var.upBound` — Upper bound
- `var.value()` — Returns varValue, or None safely

```python
for v in prob.variables():
    print(f"{v.name} = {v.varValue}")

# Safe access with value() helper
print("x =", value(x))  # Returns x.varValue or None
```

## fixValue() and isFixed()

Lock a variable to its current value by setting both bounds equal:

```python
x.fixValue()   # Sets lowBound = upBound = current varValue
x.isFixed()    # Returns True if bounds are equal
```
