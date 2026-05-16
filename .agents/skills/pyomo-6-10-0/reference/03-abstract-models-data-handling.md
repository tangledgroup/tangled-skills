# Abstract Models and Data Handling

## Contents
- AbstractModel Workflow
- AMPL .dat File Format
- DataPortal System
- Native Data (Python dicts/lists)
- Raw Data Dictionaries
- BuildAction Components
- Pyomo Command-Line Interface

## AbstractModel Workflow

AbstractModel separates model structure from data. Components are declared as empty templates, then populated during instantiation.

```python
import pyomo.environ as pyo

model = pyo.AbstractModel()
model.I = pyo.Set()
model.J = pyo.Set()
model.c = pyo.Param(model.J)
model.a = pyo.Param(model.I, model.J)
model.b = pyo.Param(model.I)
model.x = pyo.Var(model.J, domain=pyo.NonNegativeReals)

def obj_rule(m):
    return pyo.summation(m.c, m.x)
model.obj = pyo.Objective(rule=obj_rule)

def con_rule(m, i):
    return sum(m.a[i,j] * model.x[j] for j in model.J) >= m.b[i]
model.con = pyo.Constraint(model.I, rule=con_rule)

# Instantiate with data — returns a ConcreteModel instance
instance = model.create_instance('data.dat')
```

Key distinction: AbstractModel components use `rule` functions, not `expr`. The `create_instance()` call returns a new ConcreteModel — the original AbstractModel remains unchanged and can be re-instantiated with different data.

## AMPL .dat File Format

The standard data file format uses AMPL syntax. Semicolons terminate statements; text after `#` is a comment.

```
# data.dat
param m := 2;
param n := 3;

param I := 1 2;
param J := 1 2 3;

param c :=
    1  2.0
    2  3.0
    3  5.0
;

param a :=
    1 1  4.0
    1 2  9.0
    1 3  7.0
    2 1  8.0
    2 2  5.0
    2 3  2.0
;

param b :=
    1  23.0
    2  32.0
;
```

For tabular data, use `table` statements:

```
param a :=
    1  4  9  7
    2  8  5  2
;
```

## DataPortal System

DataPortals provide flexible data access with caching, transformation, and multiple backends.

```python
from pyomo.dataportal import DataPortal, DataFactory

# Create a dataportal from a .dat file
dp = DataPortal()
dp.add_source(source=DataFactory('data.dat'), type='asmpegd')

# Instantiate using the dataportal
instance = model.create_instance(data=dp)

# Direct data access
print(dp['c', 1])  # get parameter value
```

DataPortals support multiple sources, default values, and data transformations. They are particularly useful for large datasets or when combining data from multiple sources.

## Native Data (Python dicts/lists)

Pass Python data structures directly to `create_instance()`:

```python
data = {
    None: {
        'I': [1, 2],
        'J': [1, 2, 3],
        'c': {1: 2.0, 2: 3.0, 3: 5.0},
        'a': {(1,1): 4, (1,2): 9, (1,3): 7,
              (2,1): 8, (2,2): 5, (2,3): 2},
        'b': {1: 23, 2: 32}
    }
}
instance = model.create_instance(data=data)
```

The `None` key represents the model-level scope. This approach is ideal for programmatic data generation or integration with databases/CSV files.

## Raw Data Dictionaries

For maximum flexibility, use raw data dictionaries that bypass AMPL parsing:

```python
# Using set_items for indexed parameters
data = {
    None: {
        'J': {'set_value': [(1,), (2,), (3,)]},
        'c': {'init': {1: 2.0, 2: 3.0, 3: 5.0}},
    }
}
```

## BuildAction Components

BuildAction executes code during model construction, after data is loaded but before the model is fully usable. Essential for computed sets or derived data in AbstractModel.

```python
model = pyo.AbstractModel()
model.Nodes = pyo.Set()
model.Arcs = pyo.Set(dimen=2)
model.NodesIn = pyo.Set(model.Nodes, within=model.Nodes)
model.NodesOut = pyo.Set(model.Nodes, within=model.Nodes)

def populate_adjacency(m):
    for i, j in m.Arcs:
        m.NodesIn[j].add(i)
        m.NodesOut[i].add(j)

model.build = pyo.BuildAction(rule=populate_adjacency)
```

BuildActions fire during `create_instance()`, after all data is loaded. Multiple BuildActions execute in declaration order.

## Pyomo Command-Line Interface

Solve abstract models from the command line:

```bash
# Basic solve with default solver (glpk)
pyomo solve model.py data.dat

# Specify solver
pyomo solve model.py data.dat --solver=cbc
pyomo solve model.py data.dat --solver=cplex

# Show summary of results
pyomo solve model.py data.dat --summary

# Apply transformations before solving
pyomo solve model.py data.dat --transform pyomo.gdp.bigm

# Save results to file
pyomo solve model.py data.dat --results-file=results.json
```

For concrete models, omit the data file: `pyomo solve model.py`.
