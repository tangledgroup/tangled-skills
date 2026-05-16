# Data Management

## Contents
- DataPortal
- TableData
- AMPL-format .dat Files
- CSV and Other Data Formats
- Loading Data into AbstractModels

## DataPortal

`DataPortal` manages loading and storing data from external sources:

```python
import pyomo.environ as pyo
from pyomo.dataportal import DataPortal

model = pyo.ConcreteModel()
model.I = pyo.Set(initialize=[1, 2, 3])
model.cost = pyo.Param(model.I)

# Create DataPortal and connect to file
dp = DataPortal(model=model)
dp.connect(filename='data.dat', using='aml')

# Load data into model components
dp.load(model=model)

# Access data directly from portal
print(dp.data('cost'))       # All cost data
print(dp.data('cost', namespace=None))

# Store data back to file
dp.store(model=model)
dp.disconnect()
```

DataPortal internal structure: `data[namespace][symbol][index] -> value`

## TableData

Read/write tabular data from external sources:

```python
from pyomo.dataportal.plugins.table_data import TableData

# Read from CSV-like table
table = TableData()
table.initialize(filename='data.csv', header=True, delimiter=',')
table.open()
data = table.read()
table.close()
```

## AMPL-format .dat Files

The standard data format for AbstractModels:

```
# data.dat — AMPL data format

# Sets
param I := A B C D;
param J := 1 2 3;

# Scalar parameter
param demand := 100;

# Indexed parameter
param cost :=
    A 5
    B 3
    C 7
    D 2;

# Multi-indexed parameter (table format)
param matrix default 0 :=
        1    2    3
    A  0.5  0.3  0.1
    B  0.2  0.4  0.3
    C  0.1  0.2  0.5;

# Table format (alternative)
table cost_tbl ::
    param cost := [file.csv] : item , cost_val ;
```

## CSV and Other Data Formats

Load data from CSV into Pyomo parameters:

```python
import csv

model = pyo.ConcreteModel()
model.I = pyo.Set()
model.cost = pyo.Param(model.I)

# Read from CSV
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = {row['item']: float(row['cost']) for row in reader}

model.I.initialize(data.keys())
model.cost.initialize(data)
```

JSON data:

```python
import json

with open('data.json', 'r') as f:
    data = json.load(f)

model.cost.initialize(data['cost'])
```

## Loading Data into AbstractModels

```python
import pyomo.environ as pyo

model = pyo.AbstractModel()
model.I = pyo.Set()
model.cost = pyo.Param(model.I)
model.demand = pyo.Param()
model.x = pyo.Var(model.I, domain=pyo.NonNegativeReals)

def obj_rule(m):
    return sum(m.cost[i] * m.x[i] for i in m.I)

model.obj = pyo.Objective(rule=obj_rule)

def demand_rule(m):
    return sum(m.x[i] for i in m.I) >= m.demand

model.c = pyo.Constraint(rule=demand_rule)

# Instantiate from file
instance = model.create_instance('data.dat')

# Multiple data files (later overrides earlier)
instance = model.create_instance(['base.dat', 'scenario_A.dat'])

# From command line
# pyomo solve model.py data.dat --solver=glpk
```

Data can also be loaded selectively:

```python
# Load specific symbols only
instance = model.create_instance('data.dat')
instance.load_data('data2.dat', skip_existing=True)
```
