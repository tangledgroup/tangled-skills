# How-To Patterns

## Contents
- Interrogating Models
- Manipulating Models
- Solver Recipes
- Debugging Models

## Interrogating Models

**Access variable values:**

```python
import pyomo.environ as pyo

# Single variable value (use pyo.value() to get raw Python number)
val = pyo.value(model.x)
val = pyo.value(model.x[1])

# All variables
for v in model.component_objects(pyo.Var, active=True):
    for vd in v.values():
        print(f"{vd.name}: {pyo.value(vd)}")

# Iterate over a specific variable
for i in model.I:
    print(f"x[{i}] = {pyo.value(model.x[i])}")
```

**Access dual values (requires suffix):**

```python
from pyomo.core import Suffix

model.dual = Suffix(direction=Suffix.IMPORT)
results = opt.solve(model, suffixes=['dual'])

# Dual of a constraint
dual_val = model.dual[model.c]

# Duals of indexed constraints
for i in model.I:
    print(f"Dual of c[{i}]: {model.dual[model.c[i]]}")
```

**Access reduced costs:**

```python
model.rc = Suffix(direction=Suffix.IMPORT)
results = opt.solve(model, suffixes=['rc'])
print(f"Reduced cost of x[1]: {model.rc[model.x[1]]}")
```

**Access slacks:**

```python
model.slack = Suffix(direction=Suffix.IMPORT)
results = opt.solve(model, suffixes=['slack'])
print(f"Slack of c: {model.slack[model.c]}")
```

**Display model:**

```python
model.display()                    # Display all components
model.x.display()                  # Display specific component
pyo.pprint(model)                  # Pretty print
```

## Manipulating Models

**Fix/unfix variables:**

```python
model.x[1].fix()           # Fix to current value
model.x[1].value = 5       # Set value
model.x[1].unfix()         # Make free again
model.x[1].set_value(3)    # Set value (works whether fixed or not)

# Check status
if model.x[1].fixed:
    print("fixed")
```

**Activate/deactivate constraints:**

```python
model.c.activate()     # Enable constraint
model.c.deactivate()   # Disable constraint
model.c.active         # Boolean: is it active?

# For indexed constraints
model.c[1].deactivate()
```

**Activate/deactivate objectives:**

```python
model.obj1.deactivate()
model.obj2.activate()
```

**Repeated solves with cuts:**

```python
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()
model.x = pyo.Var([1, 2, 3, 4], within=pyo.Binary)
model.obj = pyo.Objective(expr=pyo.summation(model.x))
model.cuts = pyo.ConstraintList()
opt = SolverFactory('glpk')

for iteration in range(5):
    results = opt.solve(model)

    # Add a cut to exclude the current solution
    expr = 0
    for j in model.x:
        if pyo.value(model.x[j]) < 0.5:
            expr += model.x[j]
        else:
            expr += (1 - model.x[j])
    model.cuts.add(expr >= 1)
```

**Change mutable parameters and re-solve:**

```python
model.price = pyo.Param(mutable=True, initialize=10)
# ... build model using model.price ...

for new_price in [5, 10, 15, 20]:
    model.price.value = new_price
    results = opt.solve(model)
    print(f"Price={new_price}: obj={pyo.value(model.obj):.2f}")
```

## Solver Recipes

**Warm starts:**

```python
# For persistent solvers
opt = pyo.SolverFactory('gurobi_persistent')
opt.set_instance(model)
results = opt.solve(model)  # First solve

# Modify model slightly
model.demand.value = 12
opt.update_instance()
results = opt.solve(model)  # Warm start from previous solution
```

**Solving in parallel:**

```python
from multiprocessing import Pool

def solve_scenario(args):
    model, scenario_data = args
    # Update model with scenario data
    for param_name, val in scenario_data.items():
        getattr(model, param_name).value = val
    results = opt.solve(model)
    return pyo.value(model.obj)

# Prepare scenarios
scenarios = [(model, data) for data in scenario_list]

# Solve in parallel
with Pool(4) as pool:
    objectives = pool.map(solve_scenario, scenarios)
```

**Changing temporary directory:**

```python
import tempfile
tempfile.tempdir = '/path/to/fast/disk'
# Subsequent solves will use this temp directory
```

**Specifying solver path:**

```python
opt = pyo.SolverFactory('glpk')
opt.executable = '/opt/glpk/bin/glpsol'
```

## Debugging Models

**Check model structure:**

```python
# List all components
for comp in model.component_objects():
    print(f"{comp.__class__.__name__}: {comp.name}")

# Check for unindexed vs indexed
print(model.x.is_indexed())

# Count components
n_vars = sum(1 for v in model.component_data_objects(pyo.Var))
n_cons = sum(1 for c in model.component_data_objects(pyo.Constraint))
print(f"Variables: {n_vars}, Constraints: {n_cons}")
```

**Validate expressions:**

```python
# Check if expression is constant
from pyomo.core import is_constant, is_variable, is_parameter
print(is_constant(model.x[1] + 1))   # False (has variable)
print(is_constant(2 + 3))             # True
```

**Write model to file for inspection:**

```python
# Write as LP file (human-readable)
model.write('model.lp', format='lp')

# Write as NL file (for NLP solvers)
model.write('model.nl', format='nl')

# Write as CPLEX LP
model.write('model.cpxlp', format='cpxlp')
```

**Check for NaN/Inf in values:**

```python
import math

for v in model.component_data_objects(pyo.Var):
    val = pyo.value(v)
    if math.isnan(val) or math.isinf(val):
        print(f"Warning: {v.name} has value {val}")
```
