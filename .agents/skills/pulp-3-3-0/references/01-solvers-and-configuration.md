# Solvers and Configuration

> **Source:** PuLP Documentation — guides/how_to_configure_solvers.html, technical/solvers.html
> **Loaded from:** SKILL.md (via progressive disclosure)

## Solver API Types

PuLP connects to solvers in two ways:

| Type | Naming Convention | Examples | Characteristics |
|------|-------------------|----------|-----------------|
| Command-line | `*_CMD` | `COIN_CMD`, `GLPK_CMD`, `CPLEX_CMD`, `GUROBI_CMD`, `HiGHS_CMD`, `SCIP_CMD` | Writes LP/MPS to disk, calls solver binary. Slower initialization but works with any CLI solver. |
| Python API | `*_PY` (no suffix) | `COINMP_DLL`, `CPLEX_PY`, `GUROBI`, `MOSEK`, `HiGHS`, `SCIP_PY`, `XPRESS_PY` | In-process calls, no file I/O. Faster initialization, more functionality (dual prices, extreme rays, reduced costs). |

## Supported Solvers

| Solver API | Solver | License | Type |
|------------|--------|---------|------|
| `COIN_CMD` | COIN-OR CBC | Open source (EPL) | CMD |
| `GLPK_CMD` | GLPK | GPL/MPL | CMD |
| `CPLEX_CMD` / `CPLEX_PY` | IBM CPLEX | Commercial | CMD + PY |
| `GUROBI` / `GUROBI_CMD` | Gurobi | Commercial | PY + CMD |
| `MOSEK` | MOSEK | Commercial | PY |
| `HiGHS` / `HiGHS_CMD` | HiGHS | MPL 2.0 | PY + CMD |
| `SCIP_CMD` / `SCIP_PY` | SCIP | Apache 2.0 | CMD + PY |
| `XPRESS` / `XPRESS_PY` | FICO XPRESS | Commercial | PY + CMD |
| `COPT` / `COPT_CMD` | COPT | Commercial | PY + CMD |
| `CHOCO_CMD` | CHOCO | EPL | CMD |
| `MIPCL_CMD` | MIPCL | Open source | CMD |
| `CYLP` | COIN-OR Cylp | LGPL | PY |
| `FSCIP_CMD` | FSCIP | Apache 2.0 | CMD |
| `SAS94`, `SASCAS` | SAS Optimizer | Commercial | PY |
| `YAPOSIB` | Yaposib | Open source | PY |

## Checking Solver Availability

```python
import pulp as pl

# List all known solver names
all_solvers = pl.listSolvers()
print(all_solvers)
# ['GLPK_CMD', 'PYGLPK', 'CPLEX_CMD', 'CPLEX_PY', 'CPLEX_DLL', 'GUROBI',
#  'GUROBI_CMD', 'MOSEK', 'XPRESS', 'COIN_CMD', 'COINMP_DLL', 'CHOCO_CMD',
#  'MIPCL_CMD', 'SCIP_CMD', 'HiGHS', ...]

# List only available solvers
available = pl.listSolvers(onlyAvailable=True)
print(available)

# Get solver by name with parameters
solver = pl.getSolver("CPLEX_CMD")
solver = pl.getSolver("COIN_CMD", timeLimit=30, mip=True)
```

## COIN-OR CBC (`COIN_CMD`) — Default Solver

CBC is the default solver. PuLP no longer ships a bundled CBC binary or the `PULP_CBC_CMD` class. Use `COIN_CMD` instead.

**Binary resolution order:**
1. If `cbcbox` package is installed (`pip install pulp[cbc]`), use the bundled CBC binary
2. Otherwise, look for `cbc` / `cbc.exe` on PATH
3. Pass explicit `path=` to override

```python
import pulp as pl

# Default — finds cbc on PATH or from cbcbox package
solver = pl.COIN_CMD()

# Explicit path
solver = pl.COIN_CMD(path=r"C:\path\to\cbc.exe")

# With options
solver = pl.COIN_CMD(
    mip=True,           # treat as MIP even if no integer vars
    msg=True,           # show solver output
    timeLimit=60,       # max solve time in seconds
    gapRel=0.01,        # relative optimality gap (1%)
    presolve=True,      # enable presolve
    threads=4,          # number of threads
    warmStart=False,    # warm start flag
    keepFiles=False,    # delete temp files after solving
)

prob = pl.LpProblem("Test", pl.LpMinimize)
x = prob.add_variable("x", 0, 10)
prob += x
prob.solve(solver)
```

**Common `COIN_CMD` parameters:** `mip`, `msg`, `timeLimit`, `gapRel`, `gapAbs`, `presolve`, `cuts`, `strong`, `options`, `warmStart`, `keepFiles`, `path`, `threads`, `logPath`, `timeMode`, `maxNodes`

## Configuring Solver Paths

For CMD solvers, the solver binary must be discoverable:

**Option 1 — Pass path explicitly:**
```python
solver = pl.CPLEX_CMD(path="/opt/ibm/ILOG/CPLEX_Studio128/cplex/bin/x64_win64/cplex.exe")
```

**Option 2 — Set PATH environment variable (one-time setup):**
```bash
# Linux/Mac
export PATH="${PATH}:/opt/gurobi1001/linux64/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/gurobi1001/linux64/lib"

# Windows
set PATH=%PATH%;C:\gurobi1001\win64\bin
set LD_LIBRARY_PATH=%LD_LIBRARY_PATH%;C:\gurobi1001\win64\lib
```

## Solver-Specific Environment Variables

### CPLEX
```bash
export CPLEX_HOME="/opt/ibm/ILOG/CPLEX_Studio128/cplex"
export CPO_HOME="/opt/ibm/ILOG/CPLEX_Studio128/cpoptimizer"
export PATH="${PATH}:${CPLEX_HOME}/bin/x86-64_linux:${CPO_HOME}/bin/x86-64_linux"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${CPLEX_HOME}/bin/x86-64_linux:${CPO_HOME}/bin/x86-64_linux"
export PYTHONPATH="${PYTHONPATH}:/opt/ibm/ILOG/CPLEX_Studio128/cplex/python/3.5/x86-64_linux"
```

### Gurobi
```bash
export GUROBI_HOME="/opt/gurobi1001/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
```

## Temporary Files for CMD Solvers

CMD solvers write temporary LP/MPS files. Default location follows `TEMP`, `TMP`, or `TMPDIR` environment variables (in that order). PuLP deletes them after solving.

**Control temp file behavior:**
```python
# Keep files in current directory
solver = pl.COIN_CMD(keepFiles=True)

# Custom temp directory
solver = pl.COIN_CMD()
solver.tmpDir = "/path/to/temp/dir"
```

## Using Solver-Specific Functionality (Python API Solvers)

Access solver-specific APIs via the `solverModel` attribute on the problem object, populated after `buildSolverModel()` is called:

```python
import pulp

prob = pulp.LpProblem("name", pulp.LpMinimize)
x = prob.add_variable("x", lowBound=0)
prob += x

# Solve normally
solver = pulp.CPLEX_PY()
status = prob.solve(solver)

# Access CPLEX API after solving
print(prob.solverModel)  # the underlying Cplex Python object
```

**Access solver API before solving:**
```python
import pulp

prob = pulp.LpProblem("name", pulp.LpMinimize)
x = prob.add_variable("x", lowBound=0)
prob += x

solver = pulp.CPLEX_PY()
solver.buildSolverModel(prob)

# Edit solver object before solving
# e.g., load a MIP_START file for CPLEX
solver.solverModel.MIP_starts.read("model.mst")

# Call solver
solver.callSolver(prob)

# Retrieve solution values
status = solver.findSolutionValues(prob)
```

## Importing and Exporting Solver Configuration

```python
import pulp

# Export to dictionary
solver = pulp.COIN_CMD()
solver_dict = solver.toDict()
# {'keepFiles': 0, 'mip': True, 'msg': True, 'options': [],
#  'solver': 'COIN_CMD', 'timeLimit': None, 'warmStart': False}

# Export to JSON file
solver.toJson("solver_config.json")

# Import from dictionary
solver = pulp.getSolverFromDict(solver_dict)

# Import from JSON file
solver = pulp.getSolverFromJson("solver_config.json")
```

## Warm-Starting (MIP Start)

Pass initial variable values to guide the solver. Set variable `varValue` before solving:

```python
import pulp

prob = pulp.LpProblem("WarmStart", pulp.LpMinimize)
x = prob.add_variable("x", lowBound=0)
y = prob.add_variable("y", lowBound=0)
prob += x + y
prob += x <= 5

# Set initial values
x.varValue = 3
y.varValue = 2

# Solve with warm start
solver = pulp.COIN_CMD(warmStart=True)
prob.solve(solver)
```

See also: [Reference: Model Export/Import and Utilities](./02-export-import-utilities.md)
