# Utility Functions

## makeDict()

Converts nested list data into a nested dictionary for easy indexing. Essential for creating cost matrices, activity coefficients, and parameter tables:

```python
from pulp import *

Warehouses = ["A", "B"]
Bars = ["1", "2", "3", "4", "5"]

# Cost data as a list of lists (row = warehouse, column = bar)
costs = [
    [2, 4, 5, 2, 1],   # A -> bars 1-5
    [3, 1, 3, 2, 3],   # B -> bars 1-5
]

# Convert to nested dictionary
costs_dict = makeDict([Warehouses, Bars], costs, default=0)

# Access: costs_dict["A"]["3"] returns 5
# Missing keys return the default value (0)

# Triple nesting for 3D data
Resources = ["Lathe", "Polisher"]
Chairs = ["A", "B"]
activity = [[1, 2], [3, 1.5]]
activity_dict = makeDict([Resources, Chairs], activity)
# activity_dict["Lathe"]["A"] returns 1
```

## splitDict()

Splits a dictionary of lists into separate dictionaries, one per list element position:

```python
from pulp import *

# Dictionary where each value is a list [demand, surplus_price]
rollData = {
    "5": [100, 2.0],
    "7": [150, 3.0],
    "9": [200, 4.0],
}

rollDemand, surplusPrice = splitDict(rollData)
# rollDemand = {"5": 100, "7": 150, "9": 200}
# surplusPrice = {"5": 2.0, "7": 3.0, "9": 4.0}
```

## value()

Safely extracts the numeric value from a variable or expression:

```python
from pulp import *

# Returns varValue if available, None otherwise
print(value(x))           # Variable value
print(value(prob.objective))  # Objective value
print(value(5))           # Returns 5 (plain numbers pass through)
```

## roundSolution()

Rounds variable values after solving. Useful for MIP problems where solver returns near-integer values:

```python
prob.solve()
prob.roundSolution(epsInt=1e-05, eps=1e-07)
# Variables within epsInt of an integer are rounded to that integer
```

## allcombinations()

Returns all combinations of a set with up to `k` items. Useful for set partitioning and subset enumeration:

```python
from pulp import *

guests = ["A", "B", "C", "D", "E"]

# All possible table groupings of size up to 4
for combo in allcombinations(guests, 4):
    print(combo)
# (A,), (B,), ..., (A, B), (A, C), ..., (A, B, C, D), ...
```

## combination() and permutation()

Standard itertools-style generators:

```python
from pulp import *

# r-length combinations
for c in combination(range(4), 3):
    print(c)  # (0,1,2), (0,1,3), (0,2,3), (1,2,3)

# r-length permutations
for p in permutation(range(3), 2):
    print(p)  # (0,1), (0,2), (1,0), (1,2), (2,0), (2,1)
```

## allpermutations()

Returns all permutations of a set with up to `k` items:

```python
from pulp import *

for p in allpermutations([1, 2, 3, 4], 2):
    print(p)
# (1,), (2,), (3,), (4,), (1,2), (1,3), (1,4), (2,1), ...
```

## listSolvers() and getSolver()

Query available solvers and instantiate by name:

```python
import pulp as pl

# List all known solver types
all_solvers = pl.listSolvers()

# List only currently available solvers
available = pl.listSolvers(onlyAvailable=True)

# Get a solver by name (passes kwargs to constructor)
solver = pl.getSolver("COIN_CMD", timeLimit=60, msg=True)
```

## PulpSolverError

When solving fails, PuLP raises `pulp.PulpSolverError`. Always pass `msg=True` for diagnostic output:

```python
try:
    prob.solve(pl.COIN_CMD(msg=True))
except pulp.PulpSolverError as e:
    print(f"Solver error: {e}")
```
