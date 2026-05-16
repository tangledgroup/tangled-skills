# Specialized Modeling

## Contents
- MPEC (Complementarity Constraints)
- Pyomo Network (Flows and Connections)
- Units Handling
- SOS Constraints (Detailed)
- Suffixes (Detailed)

## MPEC (Complementarity Constraints)

`pyomo.mpec` supports Mathematical Programs with Equilibrium Constraints, where complementarity conditions `x >= 0, y >= 0, x*y = 0` model equilibrium behavior:

```python
import pyomo.environ as pyo
from pyomo.mpec import complement

model = pyo.ConcreteModel()
model.x = pyo.Var(bounds=(0, None))
model.y = pyo.Var(bounds=(0, None))

# Complementarity: x >= 0, y >= 0, x*y = 0
model.comp = complement(model.x, model.y)

# Or with expressions
model.comp2 = complement(model.x - 1, 5 - model.y)
# Means: (x-1) >= 0, (5-y) >= 0, (x-1)*(5-y) = 0

model.obj = pyo.Objective(expr=model.x + model.y)
```

Complementarity is commonly used in:
- Nash equilibrium problems
- Market clearing models
- Contact mechanics
- Variational inequalities

MPEC models typically require specialized solvers or reformulation (Schmitt-Misener, Slack-Socket, etc.):

```python
from pyomo.mpec.transforms import schmitt_misener

# Reformulate complementarity to standard constraints
schmitt_misener.apply_to(model)
```

## Pyomo Network (Flows and Connections)

Pyomo Network models systems as connected networks of units with ports and arcs:

```python
import pyomo.environ as pyo
from pyomo.network import Port, Arc

model = pyo.ConcreteModel()

# Unit 1 with output port
model.unit1 = pyo.Block()
model.unit1.output = Port(rule=lambda m: {'flow': pyo.Var(bounds=(0, 100))})

# Unit 2 with input port
model.unit2 = pyo.Block()
model.unit2.input = Port(rule=lambda m: {'flow': pyo.Var(bounds=(0, 100))})

# Arc connects ports (equates variables)
model.arc1 = Arc(
    rule=lambda m: {
        'tail': model.unit1.output,
        'head': model.unit2.input
    }
)

# Expand arc into constraints
from pyomo.network import expand_arcs
expand_arcs(model)
```

Ports group variables that flow between units. Arcs connect ports and generate equality constraints. This pattern is used in process simulation, supply chain networks, and energy systems.

**Sequential decomposition** for large networks:

```python
from pyomo.network.sequential import sequential_solve

# Solve units sequentially following arc topology
sequential_solve(model, solver=pyo.SolverFactory('ipopt'))
```

## Units Handling

Attach physical units to variables and check dimensional consistency:

```python
import pyomo.environ as pyo
from pyomo.environ import units as pyunits

model = pyo.ConcreteModel()

# Variable with units
model.length = pyo.Var(units=pyunits.m)
model.time = pyo.Var(units=pyunits.s)
model.velocity = pyo.Var(units=pyunits.m / pyunits.s)

# Constraint with unit checking
model.speed = pyo.Constraint(
    expr=model.velocity == model.length / model.time
)

# Unit conversion in expressions
model.dist_km = pyo.Expression(
    expr=pyunits.convert(model.length, to_units=pyunits.km)
)

# Check units of an expression
from pyomo.util.check_units import check_model_consistency
check_model_consistency(model)
```

Common unit categories: `m`, `km`, `s`, `hr`, `kg`, `g`, `K`, `degC`, `J`, `W`, `Pa`, `bar`, `mol`, `V`, `A`.

## SOS Constraints (Detailed)

Special Ordered Sets exploit solver-specific capabilities:

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()
model.I = pyo.Set(initialize=[1, 2, 3, 4, 5], ordered=True)
model.x = pyo.Var(model.I, domain=pyo.NonNegativeReals)
model.weight = pyo.Param(model.I, initialize={i: i for i in model.I})

# SOS1: at most one variable is nonzero
model.sos1 = pyo.SOSConstraint(
    index=model.I,
    var=model.x,
    sos=1,
    weight=model.weight
)

# SOS2: at most two adjacent variables are nonzero
# (requires ordered set, used in piecewise linear functions)
model.sos2 = pyo.SOSConstraint(
    index=model.I,
    var=model.x,
    sos=2
)
```

SOS1 is useful for mutual exclusivity. SOS2 is the basis for piecewise linear function representation in solvers that support it (Gurobi, CPLEX).

## Suffixes (Detailed)

Suffixes store solver-generated information:

```python
import pyomo.environ as pyo
from pyomo.core import Suffix

model = pyo.ConcreteModel()
model.x = pyo.Var([1, 2], domain=pyo.NonNegativeReals)
model.obj = pyo.Objective(expr=model.x[1] + model.x[2])
model.c = pyo.Constraint(expr=model.x[1] + 2*model.x[2] >= 1)

# Import dual values
model.dual = Suffix(direction=Suffix.IMPORT)

# Import reduced costs
model.rc = Suffix(direction=Suffix.IMPORT)

opt = pyo.SolverFactory('glpk')
results = opt.solve(model, suffixes=['dual', 'rc'])

# Access results
print(f"Dual of constraint: {model.dual[model.c]}")
print(f"Reduced cost of x[1]: {model.rc[model.x[1]]}")
```

**Suffix directions:**
- `Suffix.IMPORT`: Read from solver after solve
- `Suffix.EXPORT`: Send to solver before solve (e.g., initial points, warm starts)
- `Suffix.IMPORT_EXPORT`: Both directions

**Common suffix names:** `dual` (constraint duals), `rc` (variable reduced costs), `slack` (constraint slacks).
