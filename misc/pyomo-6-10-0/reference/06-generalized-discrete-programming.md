# Generalized Disjunctive Programming

## Contents
- GDP Concepts
- Disjunctions and Disjuncts
- Boolean Variables and Logical Constraints
- Reformulations (Big-M, Hull)
- GDPopt Solver
- PyROS Robust Optimization

## GDP Concepts

Generalized Disjunctive Programming (GDP) extends MILP/MINLP with disjunctions and logical propositions, enabling natural modeling of discrete decisions with conditional constraints.

A GDP models choices like "either process A or process B is active" where each choice activates different sets of equations:

```
[Y1 ∧ constraints_for_A] ∨ [Y2 ∧ constraints_for_B]
```

If `Y1 = True`, constraints for A are enforced; if `Y2 = True`, constraints for B apply. When a disjunct's indicator is `False`, its constraints are **ignored** (not violated).

## Disjunctions and Disjuncts

**Explicit syntax** — clear, named disjuncts:

```python
from pyomo.environ import ConcreteModel, Var, Constraint, Objective, exp
from pyomo.gdp import Disjunct, Disjunction

m = ConcreteModel()
m.x = Var([1, 2, 3, 4], bounds=(0, 10))

# Two alternative processes
m.unit1 = Disjunct()
m.unit1.inout = Constraint(expr=exp(m.x[2]) - 1 == m.x[1])
m.unit1.no_flow = Constraint(expr=m.x[3] + m.x[4] == 0)

m.unit2 = Disjunct()
m.unit2.inout = Constraint(expr=exp(m.x[4]/1.2) - 1 == m.x[3])
m.unit2.no_flow = Constraint(expr=m.x[1] + m.x[2] == 0)

# Exactly one must be selected (implicit XOR)
m.choose = Disjunction(expr=[m.unit1, m.unit2])
```

**Compact syntax** — concise list-of-lists:

```python
m.choose = Disjunction(expr=[
    [exp(m.x[2]) - 1 == m.x[1], m.x[3] == 0, m.x[4] == 0],
    [exp(m.x[4]/1.2) - 1 == m.x[3], m.x[1] == 0, m.x[2] == 0]
])
```

**Indexed disjunctions**:

```python
m.d = Disjunct(m.scenarios)
m.djn = Disjunction(m.groups)
m.djn[1] = [m.d[1], m.d[2]]
m.djn[2] = [m.d[3], m.d[4]]
```

Access indicator variables: `m.unit1.indicator_var` (BooleanVar).

## Boolean Variables and Logical Constraints

```python
from pyomo.environ import BooleanVar, LogicalConstraint, atleast, atmost, exactly

m.Y = BooleanVar(m.I)

# Implication: Y[1] => Y[2]
m.p = LogicalConstraint(expr=m.Y[1].implies(m.Y[2]))

# Complex logical expression
m.p2 = LogicalConstraint(expr=(m.Y[1] | m.Y[2]).implies(m.Y[3] & ~m.Y[4]))

# CP-style predicates
m.at_least = LogicalConstraint(expr=atleast(3, m.Y))     # at least 3 are True
m.at_most = LogicalConstraint(expr=atmost(2, m.Y))       # at most 2 are True
m.exactly_n = LogicalConstraint(expr=exactly(1, m.Y))    # exactly 1 is True
```

**Logical operators**:

| Operator | Syntax | Method | Function |
|----------|--------|--------|----------|
| Negation | `~Y[1]` | — | `lnot(Y[1])` |
| AND | `Y[1] & Y[2]` | `.land()` | `land()` |
| OR | `Y[1] \| Y[2]` | `.lor()` | `lor()` |
| XOR | `Y[1] ^ Y[2]` | `.xor()` | `xor()` |
| Implies | — | `.implies()` | `implies()` |
| Equiv | — | `.equivalent_to()` | `equivalent()` |

## Reformulations

GDP models must be converted to MILP/MINLP before solving with standard solvers.

**Big-M reformulation** — smaller model, looser relaxation:

```python
from pyomo.core import TransformationFactory
TransformationFactory('gdp.bigm').apply_to(m)
```

Auto-estimates M values from variable bounds. For manual control, provide a `BigM` Suffix.

**Multiple Big-M (MBM)** — tighter M values via subproblem solving:

```python
mbigm = TransformationFactory('gdp.mbigm')
mbigm.apply_to(m)
M_values = mbigm.get_all_M_values(m)
# Reuse in future runs:
mbigm.apply_to(m, bigM=M_values)
```

**Hull reformulation** — tighter relaxation, larger model:

```python
TransformationFactory('gdp.hull').apply_to(m)
```

Requires all variables in disjuncts to have bounds. Exact at solution points even for nonconvex GDP.

**Hybrid cutting plane** — BM + HR cutting planes:

```python
TransformationFactory('gdp.cuttingplane').apply_to(m)
```

## GDPopt Solver

GDPopt directly solves GDP models without explicit reformulation:

```python
from pyomo.contrib.gdpopt import GDPopt

solver = GDPopt(
    strategy='LB',          # 'LB' (Logic-Based), 'OA', 'BB'
    mip_solver='cbc',
    nlp_solver='ipopt'
)
results = solver.solve(m)
```

**Strategies**:
- **LB (Logic-Based)**: Uses logical inference to prune the search tree. Best for models with many logical constraints.
- **OA (Outer Approximation)**: Alternates between GDP master and NLP subproblems.
- **BB (Branch-and-Bound)**: Systematic enumeration on Boolean variables.

Also accessible via SolverFactory: `pyo.SolverFactory('gdpopt')`.

## PyROS Robust Optimization

PyROS (Pyomo Robust Optimization Solver) handles uncertainty in optimization parameters using adjustable robust optimization.

```python
from pyomo.contrib.pynumero import interfaces
from pyomo.contrib.pyros.core import PyROS

# Define uncertainty set
uncertainty_set = BoxSet()  # or ellipsoidal, polyhedral

solver = PyROS(
    nominal_solver='ipopt',
    robustness_solver='cbc',
    uncertainty_set=uncertainty_set
)
results = solver.solve(model)
```

PyROS computes adjustable robust solutions where decisions can adapt to realized uncertainty. Use when parameters have bounded uncertainty and you need guaranteed feasibility.
