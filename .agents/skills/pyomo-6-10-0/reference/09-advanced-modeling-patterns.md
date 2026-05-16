# Advanced Modeling Patterns

## Contents
- Blocks and Component Hierarchy
- Interrogating Models
- Manipulating Models
- Cloning and Copying
- Debugging Techniques
- Latex Printer

## Blocks and Component Hierarchy

Blocks are hierarchical containers that group components. Models themselves are blocks, and blocks can contain other blocks.

```python
m = pyo.ConcreteModel()

# Named block
m.stage1 = pyo.Block()
m.stage1.x = pyo.Var(bounds=(0, 10))
m.stage1.con = pyo.Constraint(expr=m.stage1.x >= 5)

# Indexed blocks
m.stages = pyo.Block([1, 2, 3])
for s in m.stages:
    m.stages[s].x = pyo.Var(bounds=(0, 10))
    m.stages[s].con = pyo.Constraint(expr=m.stages[s].x >= s)

# Block with rule
def stage_rule(m, s):
    m.stages2[s].x = pyo.Var(bounds=(0, s*10))
m.stages2 = pyo.Block(m.I, rule=stage_rule)
```

Blocks enable modular model construction, hierarchical decomposition, and scoped variable naming. Use blocks to represent stages in multistage problems, units in process networks, or scenarios in stochastic programming.

## Interrogating Models

After solving, access and inspect model components:

```python
import pyomo.environ as pyo

# Single variable value
val = pyo.value(model.x[1])

# All variables and values
for v in model.component_data_objects(pyo.Var, active=True):
    print(f"{v.name} = {pyo.value(v)}")

# All variables (including component objects)
for v in model.component_objects(pyo.Var, active=True):
    print(f"Component: {v.name}")
    for idx in v:
        print(f"  {idx}: {pyo.value(v[idx])}")

# Pretty-print entire model
model.pprint()

# Display specific component
model.x.display()

# Check construction status
model.is_constructed()
model.x.is_constructed()

# Count active components
n_vars = sum(1 for _ in model.component_data_objects(pyo.Var, active=True))
n_cons = sum(1 for _ in model.component_data_objects(pyo.Constraint, active=True))
```

**Traversal options**:
- `active=True` (default): only active components
- `sort=True`: sorted output
- `descendants=True`: include nested block components

## Manipulating Models

Modify models after construction for iterative algorithms:

```python
# Add constraint dynamically
model.new_con = pyo.Constraint(expr=model.x[1] <= 5)

# Remove constraint
del model.new_con

# Fix variable at current value
model.x[1].fixed = True
model.x[1].fixed = False  # unfixed

# Change variable bounds
model.x[1].setlb(0.5)
model.x[1].setub(9.5)

# Change parameter value (must be mutable=True)
model.p.value = new_value

# Deactivate/activate components
model.con.deactivate()
model.con.activate()

# ConstraintList for dynamic constraints
model.cuts = pyo.ConstraintList()
model.cuts.add(model.x[1] + model.x[2] <= 10)
model.cuts.add(model.x[1] >= 2)
# Check size:
print(model.cuts.ngroups())

# ConstraintSet for named dynamic constraints
model.named_cuts = pyo.ConstraintSet()
idx = model.named_cuts.create_index()
model.named_cuts[idx] = pyo.Constraint(expr=model.x[1] <= 5)
```

## Cloning and Copying

```python
from pyomo.core import Model

# Deep clone entire model
model2 = model.clone()

# Clone specific block
block_copy = model.stage1.clone()

# Shallow copy (references same components)
import copy
model_ref = copy.copy(model)

# Transfer components between models
from pyomo.core import transfer_label
new_model = pyo.ConcreteModel()
transfer_label(model.stage1, new_model, 'stage1')
```

Use `clone()` when you need an independent copy for comparison or repeated solves. Use `transfer_label` to move blocks between models without duplication.

## Debugging Techniques

```python
# Check for unbounded variables
for v in model.component_data_objects(pyo.Var, active=True):
    if v.is_unbounded():
        print(f"WARNING: {v.name} is unbounded")

# Check constraint violations
from pyomo.core.expr.numvalue import value
for c in model.component_data_objects(pyo.Constraint, active=True):
    body = value(c.body)
    if c.has_lower_bound() and body < value(c.lower) - 1e-6:
        print(f"VIOLATED: {c.name}, body={body}, lb={value(c.lower)}")
    if c.has_upper_bound() and body > value(c.upper) + 1e-6:
        print(f"VIOLATED: {c.name}, body={body}, ub={value(c.upper)}")

# Check variable domains
for v in model.component_data_objects(pyo.Var, active=True):
    if v.value is not None and not v.in_domain(v.value):
        print(f"OUT OF DOMAIN: {v.name} = {v.value}")

# Print model statistics
print(f"Variables: {sum(1 for _ in model.component_data_objects(pyo.Var, active=True))}")
print(f"Constraints: {sum(1 for _ in model.component_data_objects(pyo.Constraint, active=True))}")
print(f"Objectives: {sum(1 for _ in model.component_data_objects(pyo.Objective, active=True))}")

# Write model to LP file for inspection
model.write('model.lp', format='lp')
```

## Latex Printer

Generate LaTeX representation of models for documentation:

```python
from pyomo.repn import generate_standard_repn

# Print constraint in mathematical notation
repn = generate_standard_repn(model.con.body)
print(repn)

# Full model to LaTeX (via pprint with latex output)
import io
output = io.StringIO()
model.pprint(stream=output)
```

For full LaTeX model generation, use the `latex_printer` utility from `pyomo.util`.
