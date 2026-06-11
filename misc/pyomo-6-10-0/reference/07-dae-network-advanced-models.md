# DAE and Network Models

## Contents
- Differential-Algebraic Equations (DAE)
- ContinuousSet
- DerivativeVar
- Collocation Discretization
- Network Flows with pyomo.network
- Ports and Arcs
- MPEC (Complementarity)
- Units of Measure

## Differential-Algebraic Equations (DAE)

pyomo.DAE models systems of differential-algebraic equations for dynamic optimization. It introduces three components: `ContinuousSet`, `DerivativeVar`, and `Integral`.

### ContinuousSet

Defines continuous bounded domains (time, space) for indexing variables and constraints.

```python
from pyomo.dae import ContinuousSet

m = pyo.ConcreteModel()
m.t = ContinuousSet(bounds=(0, 10))  # time domain [0, 10]
# Or with finite element points:
m.t = ContinuousSet(bounds=(0, 10), initialize=[0, 2, 5, 8, 10])
```

### DerivativeVar

Declares variables as derivatives of other variables.

```python
from pyomo.dae import DerivativeVar

m.x = pyo.Var(m.t)
m.dxdt = DerivativeVar(m.x, wrt=m.t)  # dx/dt
# Higher-order:
m.d2xdt2 = DerivativeVar(m.x, wrt=m.t, ndx=2)  # d²x/dt²
```

### Modeling DAEs

```python
m.x = pyo.Var(m.t, initialize=0)
m.u = pyo.Var(m.t)  # control variable

def ode_rule(m, t):
    return m.dxdt[t] == -m.x[t] + m.u[t]
m.ode = pyo.Constraint(m.t, rule=ode_rule)

# Algebraic constraint
def alg_rule(m, t):
    return m.x[t] >= 0
m.alg = pyo.Constraint(m.t, rule=alg_rule)

# Initial condition
m.ic = pyo.Constraint(expr=m.x[0] == 1.0)
```

### Collocation Discretization

Transform the continuous DAE into a large NLP via simultaneous discretization:

```python
from pyomo.dae import TransformationFactory as dae_TF

dae_TF.collocation.apply_to(
    m,
    nfe=20,                      # number of finite elements
    ncp=3,                       # number of collocation points per element
    scheme='LAGRANGE-RADAU',     # or 'GAUSS', 'RADAU', 'LOBATTO'
    continuous_var=m.x,          # variables to discretize
    wrt=m.t                      # continuous set to discretize
)

# After discretization, solve as NLP
opt = pyo.SolverFactory('ipopt')
results = opt.solve(m)
```

**Scheme selection**:
- **LAGRANGE-RADAU**: Good for optimal control problems
- **GAUSS**: Highest accuracy per point
- **LOBATTO**: Includes endpoints, good for boundary conditions

### Simulation

Simulate (integrate) DAEs without optimization:

```python
from pyomo.dae import initialize_scheme
initialize_scheme(m, m.t, 'euler', nfe=100)
```

## Network Flows with pyomo.network

Model systems as connected networks of units with ports and arcs.

### Ports and Arcs

```python
from pyomo.network import Port, Arc

m = pyo.ConcreteModel()
m.x = pyo.Var()
m.y = pyo.Var()

# Create ports (collections of variables)
m.port_a = Port()
m.port_a.add(m.x)

m.port_b = Port()
m.port_b.add(m.y)

# Connect ports with an arc (equates port members)
m.arc = Arc(rule=m.port_a.connect(m.port_b))

# Expand arcs into algebraic constraints
from pyomo.network import Arc as ArcClass
ArcClass.expand(m)
# Now m has constraints: m.x == m.y
```

### Block-based Networks

```python
m.unit1 = pyo.Block()
m.unit1.x_in = pyo.Var()
m.unit1.x_out = pyo.Var()
m.unit1.port_in = Port(rule=lambda m: [m.unit1.x_in])
m.unit1.port_out = Port(rule=lambda m: [m.unit1.x_out])
m.unit1.balance = pyo.Constraint(expr=m.unit1.x_out == 2*m.unit1.x_in)

# Connect units
m.connection = Arc(
    rule=m.unit1.port_out.connect(m.unit2.port_in)
)
```

### Sequential Decomposition

Solve network models unit-by-unit in topological order:

```python
from pyomo.network import sequential

for block in sequential(m):
    # Solve each unit sequentially
    opt.solve(block)
```

## MPEC (Complementarity)

Mathematical Programs with Equilibrium Constraints model complementarity conditions:

```python
from pyomo.mpec import Complementality

m.x = pyo.Var(bounds=(0, None))
m.s = pyo.Var(bounds=(0, None))

# x >= 0, s >= 0, x * s = 0 (complementarity)
m.comp = Complementality(m.x, m.s)

# Or with constraints:
m.g = pyo.Constraint(expr=m.x + m.s >= 1)
m.comp2 = Complementality(m.g, m.s)  # g(x) >= 0, s >= 0, g(x)*s = 0
```

Solve with solvers supporting complementarity (e.g., BARON, KNITRO with MPEC mode).

## Units of Measure

Attach physical units to variables and parameters for automatic dimensional consistency:

```python
from pyomo.environ import units as pyunits

m.length = pyo.Var(units=pyunits.m)
m.time = pyo.Var(units=pyunits.s)
m.velocity = pyo.Var(units=pyunits.m/pyunits.s)

# Dimensionally consistent constraint
m.speed = pyo.Constraint(expr=m.velocity == m.length / m.time)

# Unit conversion
m.dist_km = pyo.Var(units=pyunits.km)
m.same = pyo.Constraint(expr=m.dist_km == m.length)
# Pyomo handles the conversion automatically

# Check units
print(m.length.get_units())  # m
```

Requires `pint` package: `pip install pint`.
