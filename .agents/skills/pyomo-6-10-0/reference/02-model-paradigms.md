# Model Paradigms

## Contents
- ConcreteModel vs AbstractModel
- ConcreteModel Pattern
- AbstractModel Pattern
- Data Loading for AbstractModels
- The `pyomo` Command-Line Tool
- BuildAction and BuildCheck

## ConcreteModel vs AbstractModel

Pyomo supports two modeling paradigms:

| Feature | ConcreteModel | AbstractModel |
|---------|--------------|---------------|
| Data source | Hard-coded in Python | External data files |
| Construction | Immediate (eager) | Deferred until `create_instance()` |
| Expression style | Direct `expr=` or `rule=` | Rule functions only (for constraints/objectives) |
| Best for | Programmatic models, scripting | Template models with varying data |
| Data modification | Change mutable Params, re-solve | Create new instance with different data |

**Use ConcreteModel** when data is available in Python (from computation, API calls, or hardcoded). This is the preferred approach for most Python programmers.

**Use AbstractModel** when separating model structure from data, typically with `.dat` files. Useful for reusing the same model template with different datasets.

## ConcreteModel Pattern

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()

model.I = pyo.Set(initialize=[1, 2, 3])
model.cost = pyo.Param(model.I, initialize={1: 4, 2: 2, 3: 1})
model.x = pyo.Var(model.I, domain=pyo.NonNegativeReals)

# Direct expression (ConcreteModel-specific convenience)
model.obj = pyo.Objective(
    expr=sum(model.cost[i] * model.x[i] for i in model.I)
)

model.c = pyo.Constraint(
    expr=sum(model.x[i] for i in model.I) >= 10
)

# Model is fully constructed — ready to solve
```

## AbstractModel Pattern

```python
import pyomo.environ as pyo

model = pyo.AbstractModel()

model.I = pyo.Set()
model.cost = pyo.Param(model.I)
model.demand = pyo.Param()
model.x = pyo.Var(model.I, domain=pyo.NonNegativeReals)

# Rule-based (required for AbstractModel)
def obj_rule(m):
    return sum(m.cost[i] * m.x[i] for i in m.I)

model.obj = pyo.Objective(rule=obj_rule)

def demand_rule(m):
    return sum(m.x[i] for i in m.I) >= m.demand

model.c = pyo.Constraint(rule=demand_rule)

# NOT yet constructed — need data
# Instantiate with data file
instance = model.create_instance('data.dat')

# Now instance is a concrete model ready to solve
```

## Data Loading for AbstractModels

Data files use AMPL-format `.dat` syntax:

```
# data.dat
param I := A B C;
param cost :=
    A 5
    B 3
    C 7;
param demand := 100;
```

Multiple data sources:

```python
# Single file
instance = model.create_instance('data.dat')

# Multiple files (later files override earlier)
instance = model.create_instance(['base.dat', 'scenario.dat'])

# In-memory data initialization for specific params
instance = model.create_instance('data.dat')
instance.cost['A'] = 10  # only works if Param is mutable
```

For ConcreteModel, use `initialize` argument or set values directly:

```python
model.cost = pyo.Param(model.I, mutable=True)
model.cost['A'] = 5  # direct assignment
```

## The `pyomo` Command-Line Tool

Pyomo provides a CLI for solving AbstractModels without writing Python solve scripts:

```bash
# Solve with specified solver
pyomo solve model.py data.dat --solver=glpk

# Solve and display results
pyomo solve model.py data.dat --solver=glpk --log-file=output.log

# Specify output format
pyomo solve model.py data.dat --solver=ipopt --format=nl
```

The `pyomo` command supports:
- `--solver`: solver name
- `--format`: file format (lp, nl, cpxlp, etc.)
- `--log-file`: redirect solver output
- `--timing`: show timing information

## BuildAction and BuildCheck

For AbstractModels that need conditional construction logic:

```python
import pyomo.environ as pyo

model = pyo.AbstractModel()
model.x = pyo.Var()
model.use_extra = pyo.Param(default=0, within=pyo.Binary)

# BuildAction: executed during construction
def add_constraint_action(m):
    if m.use_extra == 1:
        m.extra_c = pyo.Constraint(expr=m.x >= 5)

model.action = pyo.BuildAction(rule=add_constraint_action)

# BuildCheck: validates after construction (raises if False)
def validate_check(m):
    return m.x.lb is None or m.x.lb >= 0

model.check = pyo.BuildCheck(rule=validate_check)
```

BuildActions run during `create_instance()`. BuildChecks raise errors if the rule returns False.
