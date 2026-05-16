# Mixed-Integer and Global Optimization

## Contents
- MindtPy Solver
- McPP (Multistart with Convergence Promotion)
- Multistart
- Trust Region Solver

## MindtPy Solver

MindtPy (Mixed-Integer Nonlinear Decomposition Toolbox in Pyomo) solves MINLPs using decomposition algorithms that alternate between MILP and NLP subproblems.

### Algorithms

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| **Outer-Approximation (OA)** | Alternates NLP relaxation and MILP master | Convex MINLP |
| **LP/NLP BB** | Branch-and-bound with NLP at leaves, LP relaxations at nodes | General MINLP |
| **Extended Cutting Plane (ECP)** | Sequential cutting plane on integer space | Nonconvex MINLP |
| **Global OA (GOA)** | OA with convexification for global optima | Convexifiable MINLP |
| **Regularized OA (ROA)** | OA with regularization for stability | Ill-conditioned MINLP |
| **Feasibility Pump (FP)** | Heuristic for finding feasible solutions | Feasibility finding |

### Usage

```python
import pyomo.environ as pyo
from pyomo.contrib.mindtpy import MindtPy

model = pyo.ConcreteModel()
model.x = pyo.Var(bounds=(0, 10))
model.y = pyo.Var(within=pyo.Binary)
model.obj = pyo.Objective(expr=model.x**2 + model.y)
model.con = pyo.Constraint(expr=model.x >= 3*model.y + 1)

# Solve with MindtPy
solver = MindtPy(
    mip_solver='cbc',       # MILP solver
    nlp_solver='ipopt',     # NLP solver
    strategy='OA',          # algorithm: 'OA', 'ECP', 'LP_NLP_BB', 'GOA', 'ROA'
    minlp_solver=None       # optional single MINLP solver fallback
)
results = solver.solve(model)
```

### Via SolverFactory

```python
opt = pyo.SolverFactory('mindtpy')
opt.options['strategy'] = 'OA'
opt.options['mip-solver'] = 'cbc'
opt.options['nlp-solver'] = 'ipopt'
results = opt.solve(model)
```

### Strategy Selection

- **OA**: Best for convex MINLPs (convex in x for fixed y). Fast convergence.
- **ECP**: Handles nonconvex problems. Slower but more general.
- **LP/NLP BB**: Good balance of speed and generality. Uses LP relaxations at branch nodes.
- **GOA**: For global optimization when convexification is possible.
- **ROA**: When OA oscillates or fails to converge.

## McPP (Multistart with Convergence Promotion)

McPP solves MINLPs using outer-approximation with multistart and convergence promotion strategies. It generates multiple starting points for NLP subproblems to escape local optima.

```python
opt = pyo.SolverFactory('mcpp')
opt.options['nlp_solver'] = 'ipopt'
opt.options['mip_solver'] = 'cbc'
results = opt.solve(model)
```

McPP is particularly effective for nonconvex MINLPs where the NLP relaxation has multiple local optima. It uses integer rounding, perturbation, and feasibility pump strategies to generate diverse starting points.

## Multistart

The multistart solver runs an NLP solver from multiple starting points and returns the best solution found.

```python
opt = pyo.SolverFactory('multistart')
opt.options['nlp_solver'] = 'ipopt'
opt.options['max_starts'] = 10          # number of starts
opt.options['time_limit'] = 300         # total time limit
results = opt.solve(model)
```

Multistart is for NLP problems (no integer variables). Use when the problem is nonconvex and you want to find a better local optimum.

### Starting Point Strategies

- **Random**: Random points within variable bounds
- **Grid**: Systematic grid of points
- **Latin Hypercube**: Space-filling design

## Trust Region Solver

The trust region solver implements a trust region method for global optimization of MINLPs. It maintains a trust region around the current iterate and solves subproblems within it.

```python
opt = pyo.SolverFactory('trustregion')
opt.options['nlp_solver'] = 'ipopt'
opt.options['mip_solver'] = 'cbc'
results = opt.solve(model)
```

Trust region is designed for nonconvex MINLPs where standard decomposition methods may struggle. It combines trust region strategies with branch-and-bound to systematically explore the solution space.

## Comparison and Selection

| Method | Problem Type | Convexity Requirement | Global Guarantee |
|--------|-------------|----------------------|------------------|
| MindtPy (OA) | MINLP | Convex in x | Local (convex case) |
| MindtPy (ECP) | MINLP | None | Local |
| MindtPy (GOA) | MINLP | Convexifiable | Global |
| McPP | MINLP | None | Heuristic global |
| Multistart | NLP | None | Heuristic global |
| Trust Region | MINLP | None | Heuristic global |

For provable global optimality, use Couenne or ANTIGONE directly via SolverFactory. MindtPy with GOA provides global guarantees when convexification is possible.
