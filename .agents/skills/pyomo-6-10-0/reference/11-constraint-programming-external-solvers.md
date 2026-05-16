# Constraint Programming and External Solvers

## Contents
- z3 Constraint Programming Interface
- ExternalFunction
- GAMS Solver Interface
- Direct and Persistent Solver Modes (CPLEX, Gurobi, Xpress)

## z3 Constraint Programming Interface

Pyomo integrates with the z3 theorem prover for constraint programming and satisfiability modulo theories (SMT):

```python
from pyomo.contrib.z3 import z3_interface

# Use z3 as a solver for logical/arithmetical constraints
opt = pyo.SolverFactory('z3')
results = opt.solve(model)
```

z3 is particularly effective for models with:
- Integer arithmetic and modular constraints
- Bit-vector operations
- String constraints
- Complex logical combinations

**Limitations**: z3 does not support general nonlinear continuous optimization. Use for discrete/CP problems or as a feasibility checker within decomposition algorithms.

## ExternalFunction

Call external C/C++ functions from Pyomo models, enabling custom nonlinear evaluations:

```python
from pyomo.core import ExternalFunction

# Define an external function (takes shared library path and function name)
my_func = ExternalFunction(
    libname='mylib.so',   # or .dll on Windows
    funcname='my_function'
)

# Use in model
model.y = pyo.Var()
model.con = pyo.Constraint(expr=model.y == my_func(model.x[1], model.x[2]))
```

The external function must be compiled as a shared library with C calling convention. Pyomo passes double-precision arguments and receives a double-precision result. External functions support automatic differentiation via numerical methods in IPOPT.

## GAMS Solver Interface

Access GAMS solvers through Pyomo's GAMS interface:

```python
opt = pyo.SolverFactory('gams')
opt.options['mip'] = 'cplex'    # set GAMS MIP solver
opt.options['nlp'] = 'conopt'   # set GAMS NLP solver
results = opt.solve(model)
```

The GAMS interface writes the model in GAMS format and invokes the GAMS system. Requires a licensed GAMS installation. Useful when specific GAMS solvers (CONOPT, RMIN, BNDMIP) are needed.

## Direct and Persistent Solver Modes

Pyomo provides multiple interface modes for commercial solvers:

**Standard (file-based)**: Writes model to file, calls solver externally.
```python
opt = pyo.SolverFactory('gurobi')
results = opt.solve(model)
```

**Persistent**: Keeps model in solver memory via Python API.
```python
opt = pyo.SolverFactory('gurobi_persistent')
opt.set_instance(model)
# Add/remove components incrementally...
results = opt.solve()
```

**APPSI (Auto-Persistent)**: Automatic change detection with persistent backend.
```python
opt = pyo.SolverFactory('appsi_gurobi')
results = opt.solve(model)
```

**Direct (solver-specific)**: Some solvers offer direct Python API access.
```python
# Gurobi direct mode via gurobipy
opt = pyo.SolverFactory('gurobi_direct')
```

### Mode Comparison

| Mode | Speed (first solve) | Speed (re-solve) | Change Detection | Use Case |
|------|-------------------|-----------------|------------------|----------|
| Standard | Slow (file I/O) | Slow (file I/O) | N/A | One-off solves |
| Persistent | Medium (API setup) | Fast | Manual | Iterative algorithms |
| APPSI | Medium (build required) | Very fast | Automatic | Repeated parametric solves |
| Direct | Fast | Fast | Manual | Advanced solver features |

### CPLEX Modes

```python
pyo.SolverFactory('cplex')              # standard
pyo.SolverFactory('cplex_persistent')   # persistent
pyo.SolverFactory('appsi_cplex')        # APPSI
```

### Gurobi Modes

```python
pyo.SolverFactory('gurobi')              # standard
pyo.SolverFactory('gurobi_persistent')   # persistent
pyo.SolverFactory('gurobi_direct')       # direct (gurobipy)
pyo.SolverFactory('appsi_gurobi')        # APPSI
```

### Xpress Modes

```python
pyo.SolverFactory('xpress')               # standard
pyo.SolverFactory('xpress_persistent')    # persistent
```
