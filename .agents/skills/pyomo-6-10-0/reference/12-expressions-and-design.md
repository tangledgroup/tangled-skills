# Expressions and Design

## Contents
- Expression System Overview
- Building Expressions Efficiently
- Managing and Analyzing Expressions
- Model Transformations
- Component Design Philosophy

## Expression System Overview

Pyomo's expression system (Pyomo5, introduced in v5.6) uses immutable expression objects that form a tree structure. Expressions are built by combining variables, parameters, and numeric values with operators.

Key properties:
- **Immutable**: Once created, expression objects cannot be modified
- **Tree structure**: Binary operation nodes with leaf nodes (variables, parameters, numbers)
- **PyPy compatible**: Does not rely on CPython reference counting
- **Lazy construction**: Expressions are built as Python evaluates operator overloads

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()
model.x = pyo.Var()
model.y = pyo.Var()
model.p = pyo.Param(initialize=2)

# Expression tree: (x + y) * p
expr = (model.x + model.y) * model.p

# This creates an immutable expression tree
# Modifying model.x later does NOT change expr
```

## Building Expressions Efficiently

**summation()** — efficient sum of products over aligned indexes:

```python
# Sum of all values in indexed component
total = pyo.summation(model.x)  # sum(x[i] for i in I)

# Dot product of two aligned components
dot = pyo.summation(model.c, model.x)  # sum(c[i]*x[i] for i in I)
```

**product()** — product over all indexes:

```python
prod = pyo.product(model.x)  # x[1] * x[2] * ... * x[n]
```

**Expression component** — named intermediate expressions:

```python
# Avoids rebuilding the same expression multiple times
model.total_cost = pyo.Expression(
    expr=sum(model.cost[i] * model.x[i] for i in model.I)
)

# Use in multiple constraints
model.budget_c = pyo.Constraint(expr=model.total_cost <= model.budget)
model.tax_c = pyo.Constraint(expr=model.total_cost * 0.1 <= model.tax_limit)
```

**Avoiding expression bloat** — for large models, use `Expression` to cache sub-expressions rather than repeating them inline.

## Managing and Analyzing Expressions

**Traversing expression trees:**

```python
from pyomo.core.expr.current import identify_variables

# Get all variables in an expression
vars_in_expr = identify_variables(expr, sort=False)

# Check expression properties
from pyomo.core import is_constant, is_variable, is_parameter_iso
print(is_constant(expr))        # True if no variables
print(is_variable(expr))         # True if single variable
```

**Visitor pattern for expression analysis:**

```python
from pyomo.core.expr.visitor import ExpressionValueVisitor

class MyVisitor(ExpressionValueVisitor):
    def visit(self, node, data):
        # Called for each node in expression tree
        print(f"Visiting: {type(node).__name__} = {node}")
        return self._visit_childless(node, data)

    def _visit_childless(self, node, data):
        pass

visitor = MyVisitor()
visitor.dfs_postorder(expr, None)
```

**Replacing sub-expressions:**

```python
from pyomo.core.expr.current import replace_expressions

# Replace one variable with another in an expression
new_expr = replace_expressions(
    expr,
    substitute_map={model.x: model.y}
)
```

## Model Transformations

Transformations modify model structure:

```python
import pyomo.environ as pyo

# Get available transformations
from pyomo.core import TransformationFactory

# Example: remove constant constraints
transfo = TransformationFactory('core.remove_constant_constraints')
transfo.apply_to(model)

# Example: expand geometry (expand set product indexes)
transfo = TransformationFactory('core.expand_geometry')
transfo.apply_to(model)

# Example: pre-process general constraints
transfo = TransformationFactory('core.pre_process_general_constraints')
transfo.apply_to(model)

# List all available transformations
from pyomo.core.base.plugin import TransformationFactory
print(TransformationFactory.registered_names())
```

Common transformations:
- `core.remove_constant_constraints`: Remove always-satisfied constraints
- `core.expand_geometry`: Expand cross-product set indexes
- `core.pre_process_general_constraints`: Normalize constraint forms
- `core.scale_model`: Apply scaling factors (see Modeling Utilities)
- `gdp.hull` / `gdp.big_m`: GDP to MINLP reformulation
- `dae.collocation`: DAE discretization

## Component Design Philosophy

Pyomo follows a component-based architecture:

**Component hierarchy:**
- `Component`: Base class for all Pyomo components
- `ComponentData`: Individual data within indexed components
- `IndexedComponent`: Components that can be indexed (Set, Param, Var, etc.)
- `Block`: Container for other components

**Key design principles:**
- **Separation of Component and ComponentData**: `model.x` is the component (container), `model.x[1]` is the component data (individual value)
- **Blocks as containers**: Models are blocks; blocks can contain other blocks
- **Active/inactive state**: Components and blocks can be activated/deactivated without deletion
- **Rule-based construction**: AbstractModels use rule functions that receive the model and index values
- **Plugin architecture**: Solvers, transformations, and data managers are plugins

**Traversal patterns:**

```python
# All Var components (containers)
for var_comp in model.component_objects(pyo.Var, active=True):
    print(var_comp.name)

# All Var data (individual variables)
for var_data in model.component_data_objects(pyo.Var, active=True):
    print(f"{var_data.name}: {pyo.value(var_data)}")

# Descend into blocks
for block in model.descendants():
    print(type(block).__name__)

# Specific component type in subtree
for con in model.component_data_objects(pyo.Constraint, descend_into=True):
    print(con.name)
```

**descend_into** parameter controls whether to recurse into nested blocks. Default is `True` for `component_data_objects`, `False` for `component_objects`.
