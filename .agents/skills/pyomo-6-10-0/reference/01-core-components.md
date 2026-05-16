# Core Modeling Components

## Contents
- Sets and RangeSets
- Parameters
- Variables
- Objectives
- Constraints
- Expressions
- Blocks
- SOS Constraints
- Suffixes

## Sets and RangeSets

Sets define index collections for other components.

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()

# Unordered set with initialization
model.I = pyo.Set(initialize=['a', 'b', 'c'])

# Ordered set (default)
model.J = pyo.Set(initialize=[1, 2, 3], ordered=True)

# RangeSet: integer range [1, 10]
model.K = pyo.RangeSet(1, 10)

# RangeSet with step
model.L = pyo.RangeSet(0, 20, step=2)  # {0, 2, 4, ..., 20}

# Set with dimension constraint
model.P = pyo.Set(dimen=2, initialize=[(1,'a'), (2,'b')])

# Jagged set (dimen=None, default)
model.Q = pyo.Set(initialize=[1, (2, 3), (4, 5, 6)])

# Virtual sets for domains
pyo.Any              # no restriction
pyo.Reals            # all real numbers
pyo.NonNegativeReals # [0, +inf)
pyo.PositiveReals    # (0, +inf)
pyo.NegativeReals    # (-inf, 0)
pyo.NonPositiveReals # (-inf, 0]
pyo.Integers         # all integers
pyo.NonNegativeIntegers
pyo.PositiveIntegers
pyo.Binary           # {0, 1} — implies bounds (0, 1)
pyo.Boolean          # {True, False}
```

Set operations (create new sets):

```python
model.union_set = model.I | model.J
model.intersect_set = model.I & model.J
model.diff_set = model.I - model.J
model.cross_set = model.I * model.J  # cross product
```

Key options: `initialize`, `within` (must be subset of another set), `validate` (callable), `filter` (callable for construction-time filtering), `ordered`.

## Parameters

Parameters hold fixed data values. Declared with `Param`:

```python
# Singleton parameter
model.demand = pyo.Param(initialize=100)

# Indexed parameter
model.cost = pyo.Param(model.I, initialize={'a': 5, 'b': 3, 'c': 7})

# Multi-indexed parameter
model.matrix = pyo.Param(model.I, model.J, initialize={(1,1): 0.5, (1,2): 0.3})

# With domain validation
model.count = pyo.Param(within=pyo.NonNegativeIntegers, initialize=5)

# Mutable parameter (can change after construction)
model.price = pyo.Param(initialize=10, mutable=True)
model.price.value = 12  # OK because mutable

# Rule-based initialization
def cost_rule(m, i):
    return 10 + i * 2

model.expensive_cost = pyo.Param(model.K, rule=cost_rule)
```

Key options: `initialize`, `within` (domain validation), `mutable` (default False), `rule` (function taking model + indexes).

## Variables

Variables are the decision variables solved for by the optimizer. Declared with `Var`:

```python
# Singleton variable
model.x = pyo.Var()

# Bounded variable
model.y = pyo.Var(bounds=(0, 10))

# Variable with domain
model.z = pyo.Var(domain=pyo.Binary)  # binary decision
model.w = pyo.Var(within=pyo.NonNegativeReals)

# Indexed variable
model.x = pyo.Var(model.I, domain=pyo.NonNegativeReals)

# Multi-indexed
model.flow = pyo.Var(model.I, model.J, bounds=(0, 100))

# Rule-based bounds
def var_bounds(m, i):
    return (lower_bound[i], upper_bound[i])

model.bounded_var = pyo.Var(model.I, bounds=var_bounds)

# Initialize variable (important for NLP solvers)
model.init_var = pyo.Var(initialize=1.0)

# Fix a variable to a specific value
model.x['a'].fix()       # x['a'] is now fixed
model.x['a'].value = 5   # set the fixed value
model.x['a'].unfix()     # make it free again

# Check if fixed
if model.x['a'].fixed:
    print("variable is fixed")
```

Key options: `domain`/`within` (value domain), `bounds` (tuple of (lb, ub)), `initialize` (starting value for NLP), `rule`.

## Objectives

Objectives define what to minimize or maximize. Declared with `Objective`:

```python
# Direct expression (ConcreteModel only)
model.obj = pyo.Objective(expr=sum(model.cost[i] * model.x[i] for i in model.I))

# Rule-based (works for both Concrete and Abstract)
def obj_rule(m):
    return sum(m.cost[i] * m.x[i] for i in m.I)

model.obj = pyo.Objective(rule=obj_rule)

# Maximization
model.max_obj = pyo.Objective(rule=obj_rule, sense=pyo.maximize)

# Using summation helper (for aligned indexes)
model.obj2 = pyo.Objective(expr=pyo.summation(model.cost, model.x))

# Multiple objectives (only one active at a time)
model.obj1 = pyo.Objective(rule=obj_rule1)
model.obj2 = pyo.Objective(rule=obj_rule2, active=False)

# Deactivate/activate
model.obj1.deactivate()
model.obj2.activate()
```

Default sense is minimization. Use `sense=pyo.maximize` for maximization.

## Constraints

Constraints restrict feasible variable values. Declared with `Constraint`:

```python
# Direct expression (ConcreteModel only)
model.c1 = pyo.Constraint(expr=model.x[1] + model.x[2] >= 10)

# Rule-based
def demand_rule(m):
    return sum(m.x[i] for i in m.I) >= m.demand

model.demand = pyo.Constraint(rule=demand_rule)

# Indexed constraints
def budget_rule(m, i):
    return m.cost[i] * m.x[i] <= m.budget[i]

model.budget = pyo.Constraint(model.I, rule=budget_rule)

# Equality constraint
model.eq = pyo.Constraint(expr=model.x[1] == model.x[2])

# Range constraint (lb <= expr <= ub)
def range_rule(m):
    return (5, model.x[1] + model.x[2], 20)

model.range_c = pyo.Constraint(rule=range_rule)

# Unbounded on one side
def lower_only(m):
    return (10, model.x[1], None)  # x[1] >= 10

def upper_only(m):
    return (None, model.x[1], 5)   # x[1] <= 5

# ConstraintList: dynamic list of constraints
model.cuts = pyo.ConstraintList()
model.cuts.add(model.x[1] + model.x[2] >= 5)
model.cuts.add(model.x[1] <= 10)

# ConstraintSet: indexed by user-defined keys
model.named_cuts = pyo.ConstraintSet()
model.named_cuts['cut1'] = model.x[1] >= 0
model.named_cuts['cut2'] = model.x[2] >= 0
```

## Expressions

Intermediate expressions improve readability and can be reused:

```python
# Named expression
model.total_cost = pyo.Expression(
    expr=sum(model.cost[i] * model.x[i] for i in model.I)
)

# Use in constraint
model.budget_constraint = pyo.Constraint(
    expr=model.total_cost <= model.budget
)

# Indexed expressions
def cost_rule(m, i):
    return m.cost[i] * m.x[i]

model.item_cost = pyo.Expression(model.I, rule=cost_rule)

# Common expression builders
pyo.summation(model.x)                        # sum of all x[i]
pyo.summation(model.c, model.x)               # sum of c[i]*x[i]
pyo.product(model.x)                          # product of all x[i]
```

## Blocks

Blocks organize model components hierarchically:

```python
model = pyo.ConcreteModel()

# Simple block
model.subproblem = pyo.Block()
model.subproblem.x = pyo.Var(domain=pyo.NonNegativeReals)
model.subproblem.obj = pyo.Objective(expr=model.subproblem.x)

# Indexed blocks
model.scenarios = pyo.Block(model.I)
for i in model.I:
    model.scenarios[i].x = pyo.Var()
    model.scenarios[i].c = pyo.Constraint(expr=model.scenarios[i].x >= 0)

# Blocks can contain other blocks (hierarchical)
model.factory = pyo.Block()
model.factory.production = pyo.Block()
model.factory.production.output = pyo.Var()
```

Blocks are the fundamental container. Models themselves are special blocks. Use `component_objects()` and `component_data_objects()` to traverse block hierarchies.

## SOS Constraints

Special Ordered Sets for specific solver capabilities:

```python
# SOS1: at most one variable is nonzero
model.sos1 = pyo.SOSConstraint(
    index=model.I,
    var=model.x,
    sos=1,
    weight=model.weight  # optional weights
)

# SOS2: at most two adjacent variables are nonzero (requires ordered set)
model.sos2 = pyo.SOSConstraint(
    index=model.J,
    var=model.x,
    sos=2
)
```

## Suffixes

Suffixes store solver-generated data like duals and slacks:

```python
# Import suffix type
from pyomo.core import Suffix, ImportSuffix

# Request dual values from solver
model.dual = Suffix(direction=Suffix.IMPORT)
results = opt.solve(model, suffixes=['dual'])

# Access dual values
for con in model.component_objects(pyo.Constraint):
    for data in con.values():
        print(f"Dual of {data}: {model.dual[data]}")

# Request reduced costs
model.rc = Suffix(direction=Suffix.IMPORT)

# Export suffixes (send to solver)
model.init = Suffix(direction=Suffix.EXPORT)
model.init[model.x[1]] = 5.0  # initial guess

# Both import and export
model.scaling = Suffix(direction=Suffix.IMPORT_EXPORT)
```

Common suffix names: `dual`, `rc` (reduced cost), `slack`.
