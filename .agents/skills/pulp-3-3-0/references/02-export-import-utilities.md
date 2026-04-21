# Model Export/Import and Utilities

> **Source:** PuLP Documentation — guides/how_to_export_models.html, pulp/utilities.py
> **Loaded from:** SKILL.md (via progressive disclosure)

## Export Formats

| Format | Extension | Preserves All Info? | Notes |
|--------|-----------|---------------------|-------|
| LP | `.lp` | Partial | Standard format; variables and constraints only |
| MPS | `.mps` | Partial | Industry standard; does not store variable values |
| JSON | `.json` | Full | Saves all data including status, solution values, shadow prices |
| Dictionary | Python dict | Full | In-memory representation of the model |

## Exporting Models

### To LP File

```python
from pulp import *

prob = LpProblem("Example", LpMinimize)
x = prob.add_variable("x", 0, 4)
y = prob.add_variable("y", -1, 1)
z = prob.add_variable("z", 0, None, LpInteger)
prob += x + 4 * y + 9 * z, "obj"
prob += x + y <= 5, "c1"
prob += x + z >= 10, "c2"

prob.writeLP("model.lp")
```

### To MPS File

```python
prob.writeMPS("model.mps",
              mpsSense=0,        # 0=use problem sense, 1=minimize, -1=maximize
              rename=False,      # True → normalized names (X0000000)
              mip=True,          # include integer/binary markers
              with_objsense=False)  # write OBJSENSE section
```

### To JSON File

```python
# Basic export
prob.to_json("model.json")

# With custom encoder (for numpy types)
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

prob.to_json("model.json", cls=NpEncoder)
```

### To Dictionary

```python
data = prob.to_dict()
# Structure:
# {
#   'constraints': [{'name': 'c1', 'sense': -1, 'constant': -5,
#                    'coefficients': [{'name': 'x', 'value': 1}, ...]}, ...],
#   'objective': {'name': 'obj', 'coefficients': [...]},
#   'parameters': {'name': 'Example', 'sense': 1, 'status': 0, 'sol_status': 0},
#   'variables': [{'name': 'x', 'lowBound': 0, 'upBound': 4, 'cat': 'Continuous', ...}, ...],
#   'sos1': {},
#   'sos2': {}
# }
```

## Importing Models

### From JSON

```python
var_dict, prob_restored = LpProblem.from_json("model.json")

# var_dict maps variable names to LpVariable objects
print(var_dict)  # {'x': x, 'y': y, 'z': z}

# Solve the restored problem
prob_restored.solve()

# Access solution values through the returned dictionary
print(var_dict['x'].value())  # 3.0
```

### From MPS

```python
var_dict, prob_restored = LpProblem.fromMPS("model.mps")
prob_restored.solve()
```

### From Dictionary

```python
var_dict, prob_restored = LpProblem.from_dict(data)
prob_restored.solve()
```

## Important Considerations

1. **Variable names must be unique.** PuLP uses internal IDs to distinguish variables with duplicate names, but export/import only uses names.

2. **Variables are not exported in grouped form.** Dictionary-indexed variables become a flat list. After import, reconstruct grouping manually:
   ```python
   wedding_vars, wedding_model = LpProblem.from_json("seating_model.json")
   # wedding_vars keys may be flattened like "table_('M',_'N')"
   value = wedding_vars["table_('M',_'N')"].value()
   ```

3. **JSON output includes solution data.** Exporting a solved model preserves status, variable values, shadow prices, and reduced costs. You can export a solved model and inspect it later without re-solving.

4. **numpy/pandas types in JSON.** The json module cannot serialize numpy types. Use a custom encoder (see above) or cast values with `int()` / `float()` before passing to PuLP.

## Utility Functions

### `value(x)` — Get Variable/Expression Value

```python
from pulp import *

prob = LpProblem("Test", LpMinimize)
x = prob.add_variable("x", 0, 10)
y = prob.add_variable("y", 0, 10)
prob += x + y
prob.solve()

# Get variable value
print(value(x))       # numeric value, or x if already a number
print(x.value())      # same result

# Get objective value
print(value(prob.objective))

# Works on expressions too
expr = 2 * x + 3 * y
print(value(expr))
```

### `lpSum(iterable)` — Sum of Expressions

```python
from pulp import *

x = LpVariable.dicts("x", range(5), lowBound=0)
prob = LpProblem("SumTest", LpMinimize)

# Sum all variables
prob += lpSum(x[i] for i in range(5)) <= 10, "capacity"

# Weighted sum
costs = [1, 2, 3, 4, 5]
prob += lpSum(c * x[i] for i, c in enumerate(costs)), "cost"
```

### `lpDot(list_a, list_b)` — Dot Product

```python
from pulp import *

coeffs = [1, 2, 3]
x = LpVariable.dicts("x", range(3), lowBound=0)
prob = LpProblem("DotTest", LpMinimize)

prob += lpDot(coeffs, [x[i] for i in range(3)]) <= 10, "constraint"
```

### `allcombinations(iterable, k)` — Generate Combinations

```python
from pulp import *

guests = 'A B C D E F G'.split()
# All combinations of up to 4 guests
tables = list(allcombinations(guests, 4))
# [('A',), ('B',), ..., ('A', 'B'), ('A', 'C'), ..., ('A', 'B', 'C', 'D'), ...]
```

### `makeDict(headers, array, default=None)` — Build Nested Dictionary

```python
from pulp import *

# Convert a flat list of (header1, header2, value) tuples into a nested dict
data = [('A', 'X', 1), ('A', 'Y', 2), ('B', 'X', 3)]
result = makeDict(['A', 'B'], data)
# {'A': {'X': 1, 'Y': 2}, 'B': {'X': 3}}
```

### `LpVariable.dicts(name, indices, lowBound=None, upBound=None, cat="Continuous")`

Create multiple variables indexed by a list of keys:

```python
from pulp import *

prob = LpProblem("DictTest", LpMinimize)

# Dictionary of variables
x = LpVariable.dicts("x", ["a", "b", "c"], lowBound=0)
prob += x["a"] + x["b"] <= 5

# 2D dictionary
y = LpVariable.dicts("y", range(3), range(3), cat=LpBinary)
for i in range(3):
    for j in range(3):
        prob += y[i][j] <= 1
```

### `LpProblem.add_variable(name, lowBound=None, upBound=None, cat="Continuous")`

Add a single variable to the problem (preferred over direct `LpVariable` construction):

```python
from pulp import *

prob = LpProblem("AddVarTest", LpMinimize)
x = prob.add_variable("x", lowBound=0, upBound=10, cat=LpInteger)
y = prob.add_variable("y", cat=LpBinary)
z = prob.add_variable("z")  # continuous, -inf <= z <= +inf
```

### `LpProblem.add_variables(name, n=1, lowBound=None, upBound=None, cat="Continuous")`

Add `n` variables at once, returns them as unpacked values:

```python
from pulp import *

prob = LpProblem("MultiVar", LpMinimize)
a, b, c = prob.add_variables("abc", n=3, lowBound=0)
# a, b, c are individual LpVariable objects
```

### `LpProblem.add_variable_dict(name, keys, lowBound=None, upBound=None, cat="Continuous")`

Add variables indexed by hashable keys (tuples work):

```python
from pulp import *

prob = LpProblem("DictIdx", LpMinimize)
possible_tables = [("A","B"), ("A","C"), ("B","C")]
x = prob.add_variable_dict("table", possible_tables, lowBound=0, upBound=1, cat=LpInteger)

# Access: x[("A","B")], x[("A","C")], etc.
prob += lpSum(x[table] for table in possible_tables) <= 5
```

## Problem Attributes After Solving

| Attribute | Type | Description |
|-----------|------|-------------|
| `prob.status` | int | Solver status code (use `LpStatus[status]` for string) |
| `prob.objective` | `LpAffineExpression` | The objective function expression |
| `prob.constraints` | dict[str, LpConstraint] | Named constraints |
| `v.varValue` | float or None | Value of variable v after solving |
| `c.pi` | float or None | Shadow price (dual value) of constraint c |
| `v.dj` | float or None | Reduced cost (dual value) of variable v |

See also: [Reference: Solvers and Configuration](./01-solvers-and-configuration.md)
