---
name: pyomo-6-10-0
description: Python-based open-source optimization modeling language supporting LP, NLP, MINLP, MILP, QP, GDP, DAE, MPEC, and network flow models with commercial (Gurobi, CPLEX) and open-source (CBC, HiGHS, IPOPT) solver interfaces. Use when formulating mathematical optimization models in Python, connecting code to solvers, building abstract or concrete models, or needing advanced features like disjunctive programming, dynamic optimization, robust optimization, or sensitivity analysis.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - pyomo
  - optimization
  - mathematical-programming
  - modeling
  - linear-programming
  - nonlinear-programming
  - mixed-integer
category: library
external_references:
  - https://www.pyomo.org/
  - https://pyomo.readthedocs.io/en/stable/
  - https://github.com/Pyomo/pyomo/tree/6.10.0
---

# Pyomo 6.10.0

## Overview

Pyomo is a Python-based, open-source optimization modeling language supporting a diverse set of optimization capabilities for formulating, solving, and analyzing optimization models. It defines general symbolic problems, creates specific problem instances with data, and solves them using commercial (Gurobi, CPLEX, Xpress) and open-source (CBC, HiGHS, IPOPT, GLPK) solvers.

Pyomo supports: Linear Programs (LP), Nonlinear Programs (NLP), Mixed-Integer LP/MINLP, Quadratic Programs (QP), Generalized Disjunctive Programming (GDP), Differential-Algebraic Equations (DAE), Mathematical Programs with Equilibrium Constraints (MPEC), network flow models, and constraint programming via z3.

## When to Use

- Formulating mathematical optimization models in Python
- Connecting Python code to optimization solvers (persistent or file-based)
- Building abstract models with external data files or concrete models with inline data
- Modeling discrete decisions with logical constraints (GDP)
- Dynamic optimization with differential equations (DAE)
- Robust optimization under uncertainty (PyROS)
- Global optimization of nonconvex MINLP (MindtPy, McPP, multistart)
- Sensitivity analysis, parameter estimation, or design of experiments

## Quick Start

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()
model.x = pyo.Var([1, 2], domain=pyo.NonNegativeReals)
model.obj = pyo.Objective(expr=2*model.x[1] + 3*model.x[2])
model.con = pyo.Constraint(expr=3*model.x[1] + 4*model.x[2] >= 1)

opt = pyo.SolverFactory('cbc')
results = opt.solve(model)

print(f"Status: {results.solver.status}")
print(f"x[1] = {pyo.value(model.x[1]):.4f}")
print(f"x[2] = {pyo.value(model.x[2]):.4f}")
```

## Core Concepts

- **ConcreteModel** — data is supplied inline at model definition time; preferred for Python programmers
- **AbstractModel** — symbolic template instantiated with external data via `create_instance()`; preferred when separating model logic from data
- **Components** — Sets, Parameters, Variables, Objectives, Constraints, Expressions, Suffixes are the building blocks
- **Blocks** — hierarchical containers that group components; models themselves are blocks
- **Transformations** — modify model structure (e.g., GDP reformulations, DAE discretization, logical-to-linear)
- **SolverFactory** — creates solver interfaces by name (`'cbc'`, `'gurobi'`, `'ipopt'`, `'appsi_gurobi'`)

## Advanced Topics

**Core Modeling Components**: Sets, Parameters, Variables, Objectives, Constraints, Expressions, Suffixes, SOS → [Core Modeling Components](reference/01-core-modeling-components.md)
**Expression System & Transformations**: Expression tree architecture, visitors, context managers, transformation framework → [Expression System and Transformations](reference/02-expression-system-transformations.md)
**Abstract Models & Data Handling**: AbstractModel workflow, .dat files, DataPortal, native data, BuildAction → [Abstract Models and Data Handling](reference/03-abstract-models-data-handling.md)
**Solver Interfaces & APPSI**: SolverFactory, persistent solvers, APPSI auto-persistent interfaces (CBC, CPLEX, Gurobi, HiGHS, IPOPT) → [Solver Interfaces and APPSI](reference/04-solver-interfaces-appsi.md)
**Mixed-Integer & Global Optimization**: MindtPy, McPP, multistart, trust region solvers for MINLP → [Mixed-Integer and Global Optimization](reference/05-mixed-integer-global-optimization.md)
**Generalized Disjunctive Programming**: Disjunctions, logical constraints, GDPopt, PyROS robust optimization → [Generalized Disjunctive Programming](reference/06-generalized-discrete-programming.md)
**DAE, Network, and Advanced Models**: Differential-algebraic equations, collocation, network flows, MPEC, units → [DAE and Network Models](reference/07-dae-network-advanced-models.md)
**Model Analysis & Utilities**: IIS, incidence analysis, DOE, MPC, parameter estimation, sensitivity, scaling → [Model Analysis and Utilities](reference/08-model-analysis-utilities.md)
**Advanced Modeling Patterns**: Blocks, interrogating, manipulating, cloning, debugging models → [Advanced Modeling Patterns](reference/09-advanced-modeling-patterns.md)
**Kernel API (Beta)**: Alternative pyomo.kernel API with containers and conic modeling → [Kernel API Beta](reference/10-kernel-api-beta.md)
**Constraint Programming & External Solvers**: z3 interface, ExternalFunction, GAMS, direct solver modes → [Constraint Programming and External Solvers](reference/11-constraint-programming-external-solvers.md)
**Pynumero Block Numerical Tools**: NLP interfaces, linear solvers, block-structured computation → [Pynumero](reference/12-pynumero-block-numerical-tools.md)
**Installation, Setup & Best Practices**: pip/conda install, Cython build, solver setup, principles → [Installation and Setup](reference/13-installation-setup-best-practices.md)
