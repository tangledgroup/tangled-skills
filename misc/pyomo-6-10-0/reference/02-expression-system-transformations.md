# Expression System and Transformations

## Contents
- Expression Tree Architecture
- Expression Classes
- Building Expressions Efficiently
- Expression Categories
- Context Managers
- Visitor Pattern
- Model Transformations

## Expression Tree Architecture

Pyomo represents all symbolic expressions as immutable trees. Interior nodes are `ExpressionBase` subclasses (operators), and leaf nodes are numeric values, Parameters, and Variables.

```
        SumExpression (+)
       /              \
ProductExpression   Number(5)
      /      \
  Var(x[1])  Number(2)
```

Expression objects are **immutable** — once created, their arguments cannot change. This prevents side effects and ensures deterministic behavior across CPython and PyPy.

### Accessing Expression Arguments

```python
expr = model.x[1] * 2 + 5
list(expr.args)     # generator of child nodes
expr.arg(0)         # first child
expr.nargs()        # number of children
```

Never access `_args_` directly — use the public API.

## Expression Classes

Standard operators map to Pyomo expression classes:

| Operation | Python Syntax | Pyomo Class |
|-----------|--------------|-------------|
| Sum | `x + y` | `SumExpression` |
| Product | `x * y` | `ProductExpression` |
| Negation | `-x` | `NegationExpression` |
| Division | `x / y` | `DivisionExpression` |
| Power | `x ** y` | `PowExpression` |
| Inequality | `x <= y` | `InequalityExpression` |
| Equality | `x == y` | `EqualityExpression` |

Additional expression types:

| Type | Example | Class |
|------|---------|-------|
| External function | `myfunc(x, y)` | `ExternalFunctionExpression` |
| If-then-else | `Expr_if(IF=x, THEN=y, ELSE=z)` | `Expr_ifExpression` |
| Intrinsic function | `pyo.sin(x)`, `pyo.exp(x)` | `UnaryFunctionExpression` |
| Absolute value | `abs(x)` | `AbsExpression` |

## Building Expressions Efficiently

For large models, use Pyomo's optimized summation utilities instead of Python's `sum()`:

```python
import pyomo.environ as pyo

# quicksum: fast sum of expression terms (faster than sum())
model.obj = pyo.Objective(expr=pyo.quicksum(model.c[i]*model.x[i] for i in model.I))

# summation: dot product of two indexed components
model.obj = pyo.Objective(expr=pyo.summation(model.c, model.x))

# sum_product: sum of products with optional coefficient
expr = pyo.sum_product(model.a, model.x, model.y)  # sum(a[i,j]*x[i]*y[j])

# prod: product of terms
expr = pyo.prod(model.x[i] for i in model.I)

# dot_product: dot product of two indexed components
expr = pyo.dot_product(model.u, model.v)
```

**Key rule**: Avoid reusing expressions in multiple constraints. Each use clones the expression. For shared sub-expressions, use `pyo.Expression`:

```python
model.shared = pyo.Expression(expr=model.x[1]**2 + model.x[2]**2)
model.c1 = pyo.Constraint(expr=model.shared <= 10)
model.c2 = pyo.Constraint(expr=model.shared >= 1)
```

## Expression Categories

Pyomo classifies expressions into four categories:

- **Constant** — no variables or mutable parameters (pure numeric)
- **Mutable** — contains mutable parameters but no variables
- **Potentially variable** — contains unfixed variables
- **Fixed** — contains only fixed variables (evaluates to a number)

Check with `expr.is_constant_type()`, `expr.is_fixed_type()`, `expr.is_potentially_variable()`.

## Context Managers

Control expression representation for performance:

```python
from pyomo.core.expr import nonlinear_expression, linear_expression

# Force nonlinear expression representation (supports all operators)
with nonlinear_expression():
    model.con = pyo.Constraint(expr=model.x**2 + pyo.sin(model.y) <= 1)

# Force linear expression representation (faster, limited to linear ops)
with linear_expression():
    model.con = pyo.Constraint(expr=model.x + model.y <= 10)
```

Use `linear_expression()` when building large sets of linear constraints for better performance.

## Visitor Pattern

Traverse and manipulate expression trees using visitors:

```python
from pyomo.core.expr import ExpressionReplacementVisitor

# Replace all instances of a variable with a value
class ReplaceVar(ExpressionReplacementVisitor):
    def visit(self, node, values):
        if type(node).__name__ == 'Variable' and node.name == 'x[1]':
            return 5.0  # replace with constant
        return super().visit(node, values)

visitor = ReplaceVar()
new_expr = visitor.walk_expression((old_expr, ()))
```

Other visitors: `ExpressionValueVisitor` (evaluate), `StreamBasedExpressionVisitor` (serialize to file format).

## Model Transformations

Transformations modify model structure. Apply via `TransformationFactory`:

```python
from pyomo.core import TransformationFactory

# Logical constraints to linear form
TransformationFactory('core.logical_to_linear').apply_to(model)

# GDP Big-M reformulation
TransformationFactory('gdp.bigm').apply_to(model)

# GDP Hull reformulation
TransformationFactory('gdp.hull').apply_to(model)

# DAE collocation discretization
from pyomo.dae import TransformationFactory as dae_TF
dae_TF.collocation.apply_to(
    model, nfe=10, scheme='LAGRANGE-RADAU',
    continuous_var=model.x, wrt=model.t
)

# Network arc expansion
from pyomo.network import Arc
Arc.expand(model)

# Symbolic to numeric (fix all parameters)
TransformationFactory('core.symbolic_to_numeric').apply_to(model)

# Preprocess: remove trivial constraints, aggregate variables
TransformationFactory('preprocess.trivial_constraints').apply_to(model)
```

Transformations are applied in-place on the model. Some transformations can be undone by storing the transformation result and calling `.revert()`.
