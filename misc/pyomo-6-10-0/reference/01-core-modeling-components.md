# Core Modeling Components

## Contents
- ConcreteModel vs AbstractModel
- Sets and RangeSets
- Parameters
- Variables
- Objectives
- Constraints
- Expressions
- Suffixes
- SOS Constraints

## ConcreteModel vs AbstractModel

**ConcreteModel** — data is supplied inline at model definition time. Preferred for Python programmers and most scripting use cases.

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()
model.x = pyo.Var([1, 2], domain=pyo.NonNegativeReals)
model.obj = pyo.Objective(expr=2*model.x[1] + 3*model.x[2])
model.con = pyo.Constraint(expr=3*model.x[1] + 4*model.x[2] >= 1)
```

**AbstractModel** — symbolic template instantiated with external data via `create_instance()`. Preferred when separating model logic from data files.

```python
model = pyo.AbstractModel()
model.J = pyo.Set()
model.c = pyo.Param(model.J)
model.x = pyo.Var(model.J, domain=pyo.NonNegativeReals)

def obj_rule(m):
    return pyo.summation(m.c, m.x)
model.obj = pyo.Objective(rule=obj_rule)

# Instantiate with data file
instance = model.create_instance('data.dat')
```

In abstract models, use `rule` functions (not `expr`) for objectives and constraints. Rule functions receive the model as first argument, followed by index values.

## Sets and RangeSets

**Set** — declares an indexable collection of members:

```python
model.colors = pyo.Set(initialize=['red', 'green', 'blue'])
model.nodes = pyo.Set()  # populated later via .update() or data file
model.pairs = pyo.Set(dimen=2)  # 2-tuple members
model.matrix = pyo.Set(model.rows, model.cols)  # indexed array of sets
```

**RangeSet** — concise integer/float sequences:

```python
model.R1 = pyo.RangeSet(10)        # 1..10
model.R2 = pyo.RangeSet(2, 20, 3)  # 2, 5, 8, 11, 14, 17, 20
```

**Set operations**: `|` (union), `&` (intersection), `-` (difference), `^` (symmetric difference), `*` (cross product).

**Predefined virtual sets** for domains:
- `Reals`, `PositiveReals`, `NonNegativeReals`, `NonPositiveReals`, `NegativeReals`
- `Integers`, `PositiveIntegers`, `NonNegativeIntegers`, `NegativeIntegers`, `NonPositiveIntegers`
- `Boolean` (True/False, 0/1), `Binary` ({0, 1})
- `PercentFraction` / `UnitInterval` ([0, 1])
- `Any` (all values)

Use `within` to restrict set members: `model.positive = pyo.Set(within=pyo.PositiveIntegers)`.

## Parameters

Declare data that must be provided before solving. Indexed by sets, with optional validation.

```python
# Singleton parameter
model.fixed_cost = pyo.Param(initialize=100, within=pyo.NonNegativeReals)

# Indexed parameter with default
model.cost = pyo.Param(model.J, initialize={1: 2.0, 2: 3.0}, default=0)

# Parameter with validation
def cost_validate(m, v, i):
    return v >= 0
model.validated_cost = pyo.Param(model.J, validate=cost_validate)

# Mutable parameter (can change after initialization, useful for repeated solves)
model.mutable_param = pyo.Param(initialize=5, mutable=True)
```

Key options: `default`, `initialize`, `within`, `mutable`, `validate`, `doc`.

## Variables

Decision variables whose values are determined by the solver.

```python
# Singleton variable with bounds
model.x = pyo.Var(bounds=(0, 10))

# Indexed binary variable
model.y = pyo.Var(model.J, within=pyo.Binary)

# Variable with domain and initialization
model.z = pyo.Var(model.I, domain=pyo.NonNegativeReals, initialize=1.0)

# Bounded via rule function
def var_bounds(m, i):
    return (m.lower_bound[i], m.upper_bound[i])
model.bounded = pyo.Var(model.J, bounds=var_bounds)
```

Key options: `domain`/`within`, `bounds`, `initialize`. Note that virtual sets like `Boolean` imply bounds of 0 and 1.

Access variable values after solving with `pyo.value(model.x[i])`. Fix a variable at its current value with `model.x[i].fixed = True`.

## Objectives

Declare what to minimize (default) or maximize.

```python
# Using rule function (works for both ConcreteModel and AbstractModel)
def obj_rule(m):
    return pyo.summation(m.c, m.x)
model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

# Using expr (ConcreteModel only)
model.obj = pyo.Objective(expr=2*model.x[1] + 3*model.x[2])

# Maximization
model.obj = pyo.Objective(rule=obj_rule, sense=pyo.maximize)
```

A model can have multiple objectives; the first active one is used by solvers. Use `model.obj.deactivate()` to disable an objective.

## Constraints

Enforce relationships between variables using equality (`==`) or inequality (`<=`, `>=`) expressions, or 3-tuple form `(lb, expr, ub)`.

```python
# Singleton constraint
model.con = pyo.Constraint(expr=model.x[1] + model.x[2] <= 10)

# Indexed constraint via rule
def budget_rule(m, i):
    return sum(m.cost[j] * model.x[i,j] for j in model.J) <= m.budget[i]
model.budget = pyo.Constraint(model.I, rule=budget_rule)

# 3-tuple form: (lower, expression, upper) — None means unbounded
model.ranged = pyo.Constraint(expr=(5, model.x[1] + model.x[2], 15))

# ConstraintList for dynamically adding constraints
model.cuts = pyo.ConstraintList()
model.cuts.add(model.x[1] <= 3)
model.cuts.add(model.x[2] >= 1)

# Skip constraint generation with Constraint.Skip
def conditional_rule(m, i):
    if m.param[i] == 0:
        return pyo.Constraint.Skip
    return model.x[i] >= m.param[i]
model.cond = pyo.Constraint(model.I, rule=conditional_rule)
```

## Expressions

Pyomo `Expression` objects are like mutable parameters that hold symbolic expressions rather than numeric values. Useful for building complex expressions incrementally or sharing sub-expressions.

```python
# Named expression (shared between constraints)
model.shared = pyo.Expression(expr=model.x[1]**2 + model.x[2]**2)
model.c1 = pyo.Constraint(expr=model.shared <= 10)
model.c2 = pyo.Constraint(expr=model.shared >= 1)

# Indexed expressions
model.exprs = pyo.Expression(model.I, expr={i: model.x[i]*model.p[i] for i in model.I})
```

Python functions with Pyomo operator overloading also work for building expressions:

```python
def my_func(x, c):
    return x**2 + c*x
# Returns a Pyomo expression when called with Var objects
model.con = pyo.Constraint(expr=my_func(model.x, model.c) <= 10)
```

## Suffixes

Map modeling components to arbitrary data. Used for importing solver results (duals, reduced costs) or exporting information (warm-start, branching priorities).

```python
# Import dual values from solver
model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

# Export integer data (e.g., branching priority)
model.priority = pyo.Suffix(direction=pyo.Suffix.EXPORT, datatype=pyo.Suffix.INT)

# Two-way (import and export, e.g., warm-starting)
model.warmstart = pyo.Suffix(direction=pyo.Suffix.IMPORT_EXPORT)

# Local data tagging
model.tags = pyo.Suffix()  # direction=LOCAL (default)
model.tags[model.x[1]] = 'important'
```

Directions: `LOCAL` (default), `IMPORT`, `EXPORT`, `IMPORT_EXPORT`. Data types: `FLOAT` (default), `INT`, `None` (any).

Access duals after solving: `model.dual[model.con]`.

## SOS Constraints

Special Ordered Sets for modeling piecewise functions and selection logic.

```python
# SOS1: at most one variable nonzero
model.sos1 = pyo.SOSConstraint(model.J, var=model.x, sos=1)

# SOS2: at most two adjacent variables nonzero (for piecewise linear)
model.sos2 = pyo.SOSConstraint(model.J, var=model.x, sos=2)

# Indexed SOS with weights
model.sos = pyo.SOSConstraint(
    model.J, var=model.x, weight=model.w, sos=1
)
```

SOS1 and SOS2 are recognized by NL file interface solvers (AMPL-compatible). Use `Piecewise` component for automatic piecewise linear constraint generation.
