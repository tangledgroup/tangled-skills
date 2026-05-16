# Disjunctive Programming (GDP)

## Contents
- Key Concepts
- Disjunct and Disjunction
- Logical Constraints
- Modeling with pyomo.gdp
- Solving GDP Models

## Key Concepts

Generalized Disjunctive Programming (GDP) bridges propositional logic and algebraic constraints. A GDP model has the form:

```
min  f(x, z)
s.t. Ax + Bz <= d
     g(x, z) <= 0
     OR_k [ Y_ik AND { M_ik*x + N_ik*z <= e_ik, r_ik(x,z) <= 0 } ]  for k in K
     Omega(Y) = True
```

Where `Y` are boolean variables indicating which disjunct is active, and each disjunct contains its own algebraic constraints.

Core GDP components:
- **Disjunct**: A block of constraints that is either all active or all inactive
- **Disjunction**: An OR relationship between disjuncts (at least one must be true)
- **LogicalConstraint**: Propositional logic relationships (AND, OR, NOT, implies)
- **BooleanVar**: Boolean decision variables

## Disjunct and Disjunction

```python
import pyomo.environ as pyo
from pyomo.gdp import Disjunct, Disjunction

model = pyo.ConcreteModel()
model.x = pyo.Var(domain=pyo.NonNegativeReals)

# Define disjuncts as indexed Disjuncts
model.d = Disjunct([1, 2])

def disjunct1_rule(m):
    m.c1 = pyo.Constraint(expr=m.x >= 5)
    m.c2 = pyo.Constraint(expr=m.x <= 8)

def disjunct2_rule(m):
    m.c1 = pyo.Constraint(expr=m.x >= 10)
    m.c2 = pyo.Constraint(expr=m.x <= 15)

model.d[1].rule = disjunct1_rule
model.d[2].rule = disjunct2_rule

# At least one disjunct must be active
model.disjunction = Disjunction(expr=[model.d[1], model.d[2]])

# Objective
model.obj = pyo.Objective(expr=model.x)
```

Disjuncts can also contain variables specific to that disjunct:

```python
def disjunct_rule(m):
    m.local_var = pyo.Var(bounds=(0, 10))
    m.local_constraint = pyo.Constraint(expr=m.local_var >= 3)

model.d = Disjunct([1, 2], rule=disjunct_rule)
model.disj = Disjunction(expr=[model.d[1], model.d[2]])
```

## Logical Constraints

Express propositional logic between boolean variables and disjuncts:

```python
from pyomo.gdp import LogicalConstraint, BooleanVar, OR, AND, NOT, implies

model = pyo.ConcreteModel()
model.y1 = BooleanVar()
model.y2 = BooleanVar()
model.y3 = BooleanVar()

# y1 implies y2
model.logic1 = LogicalConstraint(expr=model.y1.implies(model.y2))

# y1 OR y2 must be true
model.logic2 = LogicalConstraint(expr=OR([model.y1, model.y2]))

# y1 AND y2 must both be true
model.logic3 = LogicalConstraint(expr=AND([model.y1, model.y2]))

# NOT y1
model.logic4 = LogicalConstraint(expr=NOT(model.y1))

# Link boolean to disjunct
model.d = Disjunct([1, 2])
model.d[1].indicate_var = model.y1  # d[1] active iff y1 is True
model.d[2].indicate_var = model.y2
```

## Modeling with pyomo.gdp

Complete GDP model example — choosing between two processes:

```python
import pyomo.environ as pyo
from pyomo.gdp import Disjunct, Disjunction

model = pyo.ConcreteModel()

# Binary choice: process A or process B
model.process = Disjunct([1, 2])

def process_A(m):
    m.production = pyo.Var(bounds=(100, 500))
    m.cost = pyo.Var(bounds=(0, None))
    m.prod_constraint = pyo.Constraint(expr=m.production >= 200)
    m.cost_eq = pyo.Constraint(expr=m.cost == 0.5 * m.production)

def process_B(m):
    m.production = pyo.Var(bounds=(50, 300))
    m.cost = pyo.Var(bounds=(0, None))
    m.prod_constraint = pyo.Constraint(expr=m.production >= 100)
    m.cost_eq = pyo.Constraint(expr=m.cost == 0.8 * m.production + 50)

model.process[1].rule = process_A
model.process[2].rule = process_B

# Must choose at least one
model.choose = Disjunction(expr=[model.process[1], model.process[2]])

# Minimize cost
def obj_rule(m):
    # Use indicator to select active cost
    return m.process[1].cost + m.process[2].cost

model.obj = pyo.Objective(rule=obj_rule)
```

## Solving GDP Models

GDP models require transformation to MINLP before solving, or use GDPopt directly:

**Option 1: GDPopt (recommended for nonlinear GDP)**

```python
from pyomo.contrib.gdpopt import GDPopt

solver = GDPopt()
results = solver.solve(
    model,
    option={
        'strategy': 'LOA',       # LOA, GLOA, RIC, LBB, LD-SDA
        'nlp_solver': 'ipopt',   # NLP subproblem solver
        'mip_solver': 'glpk'     # MIP master problem solver
    }
)
```

**Option 2: Big-M transformation + standard MINLP solver**

```python
from pyomo.gdp import GPBigM

transformation = GPBigM()
transformation.apply_to(model, big_m=1000)

# Now model is a standard MINLP — solve with MindtPy or external solver
opt = pyo.SolverFactory('mindtpy')
results = opt.solve(model)
```

**Option 3: Hull transformation (tighter than Big-M for convex disjuncts)**

```python
from pyomo.gdp import GPHull

transformation = GPHull()
transformation.apply_to(model)

# Solve resulting MILP/MINLP
opt = pyo.SolverFactory('gurobi')
results = opt.solve(model)
```

Choose transformation based on problem structure:
- **Hull**: Tighter relaxation, requires known variable bounds, best for convex disjuncts
- **Big-M**: Simpler, needs manual big-M values, works for any disjunct structure
- **GDPopt**: No transformation needed, uses logic-based decomposition directly
