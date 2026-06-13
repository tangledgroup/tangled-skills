# Installation, Setup and Best Practices

## Contents
- Installing Pyomo
- Installing Solvers
- Optional Dependencies
- Cython Build
- Command-Line Usage
- Best Practices

## Installing Pyomo

**pip (recommended)**:

```bash
pip install pyomo
```

**conda**:

```bash
conda install -c conda-forge pyomo
```

Pyomo supports CPython 3.10–3.14 and PyPy 3.

**Optional dependencies** (for extended functionality):

```bash
pip install 'pyomo[optional]'
```

Includes: matplotlib, networkx, numpy, openpyxl, pandas, pint, scipy, sympy, xlrd.

## Installing Solvers

Pyomo does not bundle solvers. Install separately:

**Open-source solvers via conda**:

```bash
conda install -c conda-forge ipopt    # NLP
conda install -c conda-forge cbc      # LP/MIP
conda install -c conda-forge glpk     # LP/MIP
conda install -c conda-forge highs    # LP/MIP (fast)
conda install -c conda-forge bonmin   # MINLP
conda install -c conda-forge couenne  # global MINLP
```

**Open-source solvers via pip**:

```bash
pip install highspy   # HiGHS Python wrapper
pip install cbc       # COIN-BC
pip install pyscipopt # SCIP
```

**Commercial solvers** (require licenses):
- **Gurobi**: `pip install gurobipy` + license from gurobi.com
- **CPLEX**: Install IBM ILOG CPLEX Optimization Studio
- **Xpress**: Install FICO Xpress + `pip install python-xpress`

**Verify solver availability in Pyomo**:

```python
import pyomo.environ as pyo
for name in ['cbc', 'glpk', 'ipopt', 'gurobi', 'cplex', 'highs']:
    opt = pyo.SolverFactory(name)
    print(f"{name}: {'available' if opt.available() else 'NOT available'}")
```

## Cython Build

Optional Cython compilation improves expression tree performance:

```bash
# Linux/MacOS
export PYOMO_SETUP_ARGS=--with-cython
pip install pyomo

# Windows (Command Prompt)
set PYOMO_SETUP_ARGS=--with-cython
pip install pyomo

# Windows (PowerShell)
$env:PYOMO_SETUP_ARGS="--with-cython"
pip install pyomo
```

From source:

```bash
export PYOMO_SETUP_ARGS=--with-cython
git clone https://github.com/Pyomo/pyomo.git
cd pyomo
pip install -e .
```

## Command-Line Usage

```bash
# Solve abstract model with data file
pyomo solve model.py data.dat --solver=cbc

# Solve concrete model (no data file)
pyomo solve model.py --solver=ipopt

# Show solver output
pyomo solve model.py --solver=cbc --stream-output

# Summary of results
pyomo solve model.py data.dat --summary

# Apply transformations
pyomo solve model.py data.dat --transform pyomo.gdp.bigm

# Save results
pyomo solve model.py data.dat --results-file=results.json

# Help
pyomo solve --help
```

## Best Practices

**Model construction**:
- Use `ConcreteModel` for scripting; `AbstractModel` when separating model from data
- Prefer `pyo.quicksum()` or `pyo.summation()` over Python `sum()` for large expressions
- Use `Expression` components for shared sub-expressions to avoid cloning
- Set variable bounds at declaration rather than as separate constraints
- Use `mutable=True` for parameters that change between solves

**Solver selection**:
- LP/MIP: HiGHS > CBC > GLPK (open-source); Gurobi/CPLEX (commercial)
- NLP: IPOPT (open-source); KNITRO (commercial)
- MINLP: MindtPy with OA/ECP; BONMIN/SCIP for direct solve

**Performance**:
- Use APPSI (`appsi_<solver>`) for repeated solves with parameter changes
- Use persistent solvers for iterative algorithms (Benders, column generation)
- Disable unnecessary change detection in APPSI when only parameters change
- Use `save_results=False` with persistent solvers when full results aren't needed

**Debugging**:
- Write model to `.lp` file (`model.write('model.lp')`) to inspect formulation
- Check for unbounded variables before solving
- Use IIS analysis for infeasible models
- Verify constraint satisfaction after solving with tolerance checks

**Code organization**:
- Import as `import pyomo.environ as pyo` (standard convention)
- Use rule functions for indexed components in AbstractModel
- Use `Constraint.Skip` to conditionally skip constraint generation
- Organize complex models with Blocks for modularity
