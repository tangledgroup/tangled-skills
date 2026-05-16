# Kernel API (Beta)

## Contents
- Overview and Status
- Modeling Components
- Containers
- Conic Modeling
- Piecewise Functions

## Overview and Status

`pyomo.kernel` is an alternative API to the traditional `pyomo.environ` AML interface. It provides a more Pythonic, object-oriented approach to modeling with explicit container types and conic programming support.

**Beta status**: The API is fully tested and functional but may change. Models built with kernel components are **not compatible** with pyomo extensions (pyomo.dae, pyomo.gdp, PySP).

```python
from pyomo.kernel import block, variable, constraint, objective, parameter
```

## Modeling Components

Kernel components mirror AML components but with different construction patterns:

```python
from pyomo.kernel import block as blk
from pyomo.kernel import variable as var
from pyomo.kernel import constraint as cstr
from pyomo.kernel import objective as obj
from pyomo.kernel import parameter as param

# Create a block (model container)
m = blk()

# Variables
m.x = var(lb=0, ub=10, value=5)            # singleton
m.y = var(within=var.Binary)                # binary

# Parameters
m.p = param(value=3.0)

# Constraints
m.c1 = cstr(m.x + m.y >= m.p)
m.c2 = cstr(m.x <= 5)

# Objective
m.obj = obj(m.x**2 + m.y, sense='min')
```

## Containers

Kernel provides explicit container types for collections:

```python
from pyomo.kernel import (
    homogeneous_container,
    heterogeneous_container,
    dict_container,
    list_container,
    tuple_container
)

# Homogeneous container (same type)
m.vars = homogeneous_container(var, ['a', 'b', 'c'])
m.vars['a'].lb = 0

# Dict container (indexed by arbitrary keys)
m.x = dict_container(var, {1: var(lb=0), 2: var(lb=0), 3: var(lb=0)})

# List container (ordered)
m.sequence = list_container(var, [var(), var(), var()])

# Tuple container (fixed-size)
m.pair = tuple_container(var, (var(), var()))
```

Containers support iteration, indexing, and slicing like Python collections. They are the preferred way to manage indexed components in kernel models.

## Conic Modeling

Kernel supports conic programming natively:

```python
from pyomo.kernel import conic

# Second-order cone: ||Ax + b||_2 <= c'x + d
m.soc = conic.second_order_cone(
    [m.x[1], m.x[2]],   # vector part
    m.x[3]              # scalar bound
)

# Positive semidefinite cone (via matrix variable)
# Exponential cone
m.exp_cone = conic.exponential_cone(m.x[1], m.x[2], m.x[3])

# Power cone
m.pwr_cone = conic.power_cone(m.x[1], m.x[2], alpha=0.5)
```

Conic models are solved via solvers supporting conic programming (MOSEK, Gurobi, CPLEX, SCS).

## Piecewise Functions

Kernel provides piecewise linear function support:

```python
from pyomo.kernel.piecewise import piecewise

# Define breakpoints and values
breakpoints = [0, 1, 2, 3]
values = [0, 1, 3, 6]

pw = piecewise(
    x=m.x,           # input variable
    y=m.y,           # output variable
    pw_pts=breakpoints,
    fvals=values,
    repr='SOS2'      # or 'BIGM_BIN', 'CC', etc.
)
```

Kernel piecewise is integrated with the container system and supports automatic MILP reformulation.
