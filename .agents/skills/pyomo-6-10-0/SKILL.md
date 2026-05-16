---
name: pyomo-6-10-0
description: >-
  Complete toolkit for Pyomo 6.10.0 providing algebraic modeling, optimization
  formulation, solver integration, and analysis capabilities covering LP, NLP,
  MILP, MINLP, GDP, DAE, MPEC, network flows, and robust optimization. Use when
  building Python programs that require mathematical optimization modeling,
  constraint programming, dynamic optimization, disjunctive programming, or
  post-solve analysis including infeasibility diagnostics and sensitivity analysis.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - pyomo
  - optimization
  - modeling
  - lp
  - nlp
  - minlp
  - gdp
  - dae
category: library
external_references:
  - https://www.pyomo.org/
  - https://pyomo.readthedocs.io/en/stable/
  - https://github.com/Pyomo/pyomo/tree/6.10.0
---

# Pyomo 6.10.0

## Overview

Pyomo (Python Optimization Modeling Objects) is a Python-based, open-source algebraic modeling language (AML) for formulating, solving, and analyzing optimization models. It supports LP, QP, NLP, MILP, MINLP, MIQP, and specialized paradigms including Generalized Disjunctive Programming (GDP), Dynamic Optimization via DAE, MPEC, and network flows.

Pyomo does not bundle solvers. It interfaces with commercial solvers (Gurobi, CPLEX, Xpress, KNITRO) and open-source solvers (HiGHS, GLPK, CBC, Ipopt/cyipopt, SCIP) through file-based interfaces, persistent solver interfaces, and APPSI (Auto-Persistent Pyomo Solver Interfaces).

The core import pattern is:

```python
import pyomo.environ as pyo
```

This exposes all major modeling components: `ConcreteModel`, `AbstractModel`, `Set`, `RangeSet`, `Param`, `Var`, `Objective`, `Constraint`, `Block`, `SolverFactory`, and expression utilities.

## When to Use

- Formulating mathematical optimization models (LP, QP, NLP, MILP, MINLP) in Python
- Building abstract model templates with data loaded from external sources
- Integrating with commercial or open-source optimization solvers
- Modeling dynamic systems with differential-algebraic equations (DAE)
- Solving logic-based optimization with Generalized Disjunctive Programming (GDP)
- Performing post-solve analysis: infeasibility diagnostics, sensitivity, alternative solutions
- Applying model transformations: scaling, preprocessing, discretization
- Network flow modeling with ports, arcs, and connections
- Robust optimization with uncertainty sets (PyROS)

## Quick Start — ConcreteModel

```python
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel()

# Index set
model.I = pyo.Set(initialize=['butter', 'scones'])

# Parameters
model.cost = pyo.Param(model.I, initialize={'butter': 2, 'scones': 3})
model.demand = pyo.Param(initialize=10)

# Decision variables
model.x = pyo.Var(model.I, domain=pyo.NonNegativeReals)

# Objective: minimize cost
model.obj = pyo.Objective(
    expr=sum(model.cost[i] * model.x[i] for i in model.I)
)

# Constraint: meet demand
model.meet_demand = pyo.Constraint(
    expr=sum(model.x[i] for i in model.I) >= model.demand
)

# Solve
opt = SolverFactory('glpk')
results = opt.solve(model)

# Display results
for i in model.I:
    print(f"{i}: {pyo.value(model.x[i]):.2f}")
print(f"Total cost: {pyo.value(model.obj):.2f}")
```

## Quick Start — AbstractModel with Data File

```python
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.AbstractModel()

model.I = pyo.Set()
model.cost = pyo.Param(model.I, within=pyo.NonNegativeReals)
model.demand = pyo.Param(within=pyo.NonNegativeReals)
model.x = pyo.Var(model.I, domain=pyo.NonNegativeReals)

def obj_rule(m):
    return sum(m.cost[i] * m.x[i] for i in m.I)

model.obj = pyo.Objective(rule=obj_rule)

def demand_rule(m):
    return sum(m.x[i] for i in m.I) >= m.demand

model.meet_demand = pyo.Constraint(rule=demand_rule)

# Instantiate with data file
model = model.create_instance('data.dat')

# Solve
opt = SolverFactory('glpk')
results = opt.solve(model)
```

Data file (`data.dat`):

```
param I := butter scones;
param cost :=
    butter 2
    scones 3;
param demand := 10;
```

## Advanced Topics

**Core Modeling Components**: Sets, Params, Vars, Objectives, Constraints, Expressions, Blocks → [Core Components](reference/01-core-components.md)

**Model Paradigms**: ConcreteModel vs AbstractModel, data loading, the `pyomo` CLI tool → [Model Paradigms](reference/02-model-paradigms.md)

**Solver Interfaces**: SolverFactory, persistent solvers, APPSI, solver options and timeouts → [Solver Interfaces](reference/03-solver-interfaces.md)

**Pyomo Solvers**: GDPopt, PyROS, MindtPy, Multistart, Trust Region, z3 SMT → [Pyomo Solvers](reference/04-pyomo-solvers.md)

**Dynamic Optimization (DAE)**: ContinuousSet, DerivativeVar, Integral, discretization → [Dynamic Optimization](reference/05-dynamic-optimization.md)

**Disjunctive Programming (GDP)**: Disjunct, Disjunction, LogicalConstraints, GDPopt → [Disjunctive Programming](reference/06-disjunctive-programming.md)

**Specialized Modeling**: MPEC, Network flows, Units, SOS constraints, Suffixes → [Specialized Modeling](reference/07-specialized-modeling.md)

**Analysis Tools**: IIS/MIS diagnostics, alternative solutions, community detection, DoE, MPC, parmest, sensitivity → [Analysis Tools](reference/08-analysis-tools.md)

**Modeling Utilities**: Flattener, preprocessing transformations, model scaling, latex printing → [Modeling Utilities](reference/09-modeling-utilities.md)

**How-To Patterns**: Interrogating models, manipulating models, solver recipes, debugging → [How-To Patterns](reference/10-howto-patterns.md)

**Data Management**: DataPortal, TableData, data formats for AbstractModels → [Data Management](reference/11-data-management.md)

**Expressions & Design**: Expression system, transformations, component design philosophy → [Expressions & Design](reference/12-expressions-and-design.md)
