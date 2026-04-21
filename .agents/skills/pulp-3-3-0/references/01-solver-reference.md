# Solver Reference

## Solver Types

PuLP solvers fall into two categories based on how they connect to the underlying optimization engine:

### CMD Solvers (Command-Line)

Solver runs as an external process. PuLP writes the model to a file, invokes the solver binary, and reads results back.

| Solver Class | Binary | Description |
|-------------|--------|-------------|
| `COIN_CMD` | `cbc` / `cbc.exe` | CBC (Coin-OR Branch-and-Cut), default open-source solver |
| `GLPK_CMD` | `glpsol` | GNU Linear Programming Kit |
| `CPLEX_CMD` | `cplex` | IBM CPLEX command-line |
| `GUROBI_CMD` | `gurobi_cl` | Gurobi optimizer CLI |
| `MOSEK_CMD` | `mosek` | MOSEK CLI |
| `COPT_CMD` | `copt_cmd` | Hope Technology COPT CLI |
| `CHOCO_CMD` | `choco` | CHOCO constraint solver |
| `MIPCL_CMD` | `MipCl` | MIPCL solver |
| `SCIP_CMD` | `scip` | SCIP solver |
| `HiGHS_CMD` | `highs` | HiGHS high-performance LP/MIP solver |
| `XPRESS_CMD` | `xprimesolve` | FICO Xpress |

**Common CMD parameters:**
- `path` — path to solver binary
- `keepFiles` — if True, keep intermediate .lp/.mps files after solving
- `mip` — if False, solve as LP even with integer variables
- `msg` — suppress solver output
- `timeLimit` — max solve time in seconds
- `options` — list of extra CLI flags

### Python API Solvers

Solver runs in-process via its Python library. No file I/O needed for model transfer.

| Solver Class | Package | Description |
|-------------|---------|-------------|
| `GUROBI` | `gurobipy` | Gurobi optimizer (Python API) |
| `CPLEX_PY` | `cplex` | IBM CPLEX Python API |
| `CPLEX_DLL` | `cplex` | CPLEX via shared library |
| `MOSEK` | `mosek` | MOSEK Python API |
| `COPT` | `coptpy` | COPT Python API |
| `COINMP_DLL` | `cycoin` | COIN-OR via DLL/shared lib |
| `XPRESS` | `xpress` | FICO Xpress Python API |
| `PYGLPK` | `cyglpk` or `pyglpk` | GLPK Python bindings |
| `SCIP_PY` | `pyscipopt` | SCIP Python API |
| `HiGHS` | `highspy` | HiGHS high-performance LP/MIP solver (Python API) |

**Common Python API parameters:**
- `mip` — treat as MIP
- `msg` — show solver log
- `timeLimit` / `mipGap` / `gapRel` — termination criteria
- `threads` — parallelism
- `warmStart` — use current variable values as starting point
- `logPath` — path to solver log file
- `**solverParams` — solver-specific parameters (dot notation)

## COIN_CMD (CBC) — Default Solver

The default solver. CBC is **no longer bundled** with PuLP. Install via `pip install pulp[cbc]` (uses cbcbox wheel) or ensure the `cbc`/`cbc.exe` binary is on your system PATH.

```python
from pulp import *

# Basic usage
prob.solve(COIN_CMD(timeLimit=60, msg=True))

# Full parameter reference
solver = COIN_CMD(
    mip=True,               # Solve as MIP (default True)
    msg=True,               # Show solver output (default True)
    timeLimit=None,         # Max solve time in seconds
    gapRel=None,            # Relative MIP gap tolerance (fraction)
    gapAbs=None,            # Absolute MIP gap tolerance
    presolve=None,          # Enable/disable presolve
    cuts=None,              # Enable/disable cutting planes
    strong=None,            # Strong branching look-ahead depth
    threads=None,           # Number of threads
    options=[],             # Extra CBC command-line options
    warmStart=False,        # Use current values as start
    keepFiles=False,        # Keep .lp/.mps files after solving
    path=None,              # Path to cbc binary
    logPath=None,           # Path to log file
    timeMode='elapsed',     # 'elapsed' (wall-clock) or 'cpu'
    maxNodes=None,          # Max branch-and-bound nodes
)
```

> **Breaking change:** `PULP_CBC_CMD` has been removed. Use `COIN_CMD` instead. If no path is given, PuLP resolves the CBC binary in this order: (1) bundled via `cbcbox` package if installed, (2) system PATH.

### COIN_CMD Resolution Order

```bash
# Option 1: Install bundled CBC
pip install pulp[cbc]

# Option 2: System install
sudo apt install coinor-cbc          # Debian/Ubuntu
brew install coin-or-cbc             # macOS
```

```python
# Explicit path (always works)
solver = COIN_CMD(path='/usr/bin/cbc')
```

## GLPK_CMD

GNU Linear Programming Kit solver.

```python
from pulp import *

solver = GLPK_CMD(
    path='/usr/bin/glpksol',  # Path to glpsol binary
    msg=True,
    timeLimit=None,
    mip=True,
    options=[],
    keepFiles=False,
)
prob.solve(solver)
```

## CPLEX

Two interfaces available:

```python
from pulp import *

# CMD interface — requires cplex binary on PATH
solver_cmd = CPLEX_CMD(
    mip=True, msg=True, timeLimit=300,
    gapRel=0.01, gapAbs=None, threads=None,
    options=[], warmStart=False, keepFiles=False,
    path=None, logPath=None, maxMemory=None, maxNodes=None,
)
prob.solve(solver_cmd)

# Python API — requires cplex package
solver_py = CPLEX_PY(
    mip=True, msg=True, timeLimit=300,
    gapRel=0.01, warmStart=False, logPath=None,
    threads=None,
    # CPLEX parameters via dot notation
    advance=1,                       # parameters.advance
    barrier_algorithm=1,             # parameters.barrier.algorithm
    mip_strategy_probe=0,           # parameters.mip.strategy.probe
)
prob.solve(solver_py)

# Access solver-specific objects after solve
# prob.solverVar gives access to CPLEX variable objects
```

## Gurobi

Two interfaces available:

```python
from pulp import *

# CMD interface — requires gurobi_cl on PATH
solver_cmd = GUROBI_CMD(
    mip=True, msg=True, timeLimit=300,
    gapRel=0.01, gapAbs=None,
    options=[], warmStart=False, keepFiles=False,
    path=None, logPath=None, threads=None,
)
prob.solve(solver_cmd)

# Python API — requires gurobipy package
solver_py = GUROBI(
    mip=True, msg=True, timeLimit=300,
    gapRel=0.01, warmStart=False, logPath=None, threads=None,
    # Gurobi parameters
    Method=2,              # Optimality algorithm
    MIPFocus=1,            # MIP focus
    NodeLimit=1000,        # Max nodes
)
prob.solve(solver_py)
```

## MOSEK

```python
from pulp import *

solver = MOSEK(
    mip=True, msg=True, timeLimit=300,
    warmStart=False, logPath=None,
)
prob.solve(solver)
```

## COPT (Hope Technology)

```python
from pulp import *

# Python API
solver = COPT(
    mip=True, msg=True, timeLimit=300,
    gapRel=0.01, warmStart=False, logPath=None,
)
prob.solve(solver)

# CMD interface
solver_cmd = COPT_CMD(
    path=None, keepFiles=0, mip=True, msg=True,
    mip_start=False, warmStart=False, logfile=None,
)
prob.solve(solver_cmd)
```

## SCIP

```python
from pulp import *

solver = SCIP_CMD(
    path=None, keepFiles=False, mip=True, msg=True,
    timeLimit=None, gapRel=None, gapAbs=None,
    options=[], presolve=None, cuts=None,
    threads=None, logPath=None, maxNodes=None,
)
prob.solve(solver)
```

## HiGHS

Modern high-performance LP/MIP solver with Python API support.

```python
from pulp import *

# Python API — requires highspy package (pip install pulp[highs])
solver_py = HiGHS(
    timeLimit=300, msg=True,
    parallel='off',   # 'on', 'try', 'off'
)
prob.solve(solver_py)

# CMD interface
solver_cmd = HiGHS_CMD(
    path=None, keepFiles=False, mip=True, msg=True,
    timeLimit=None, options=[],
)
prob.solve(solver_cmd)
```

## CHOCO

```python
from pulp import *

solver = CHOCO_CMD(
    path=None, keepFiles=False, mip=True, msg=True,
    timeLimit=None, options=[],
)
prob.solve(solver)
```

## Checking Solver Availability

```python
import pulp

# All solvers registered with PuLP
all_solvers = pulp.listSolvers()
# ['GLPK_CMD', 'COIN_CMD', 'CPLEX_CMD', 'GUROBI_CMD', 'MOSEK', ...]

# Only solvers with binaries/libraries available
available = pulp.listSolvers(onlyAvailable=True)

# Get solver by name (constructor args passed through)
solver = pulp.getSolver('COIN_CMD', timeLimit=60, msg=False)
solver = pulp.getSolver(pulp.GUROBI(timeLimit=300))
```

## Solver Return Status

After `prob.solve()`, check `prob.status` against `pulp.constants.LpStatus`:

| Value | Constant | Meaning |
|-------|----------|---------|
| 0 | `LpStatusNotSolved` | Model not yet solved |
| 1 | `LpStatusOptimal` | Optimal solution found |
| -1 | `LpStatusInfeasible` | Problem is infeasible |
| -2 | `LpStatusUnbounded` | Objective is unbounded |
| -3 | `LpStatusUndefined` | Solver returned undefined status |

```python
from pulp import LpStatus
print(LpStatus[prob.status])  # e.g., "Optimal"
```

## Common Solver Parameters Reference

| Parameter | Type | Applies To | Description |
|-----------|------|-----------|-------------|
| `mip` | bool | All | False = solve as LP even with integer vars |
| `msg` | bool | All | Suppress/enable solver output |
| `timeLimit` | float | All | Max solve time (seconds) |
| `gapRel` / `mipGap` | float | MIP solvers | Relative optimality gap (fraction, e.g., 0.01 = 1%) |
| `gapAbs` | float | MIP solvers | Absolute gap tolerance |
| `threads` | int | All | Number of CPU threads |
| `warmStart` | bool | Most | Use current variable values as initial solution |
| `path` | str | CMD only | Path to solver binary |
| `keepFiles` | bool | CMD only | Retain .lp/.mps files after solving |
| `logPath` | str | Most | Path to write solver log |
| `options` | list[str] | CMD only | Extra CLI flags passed to solver |
| `maxNodes` | int | MIP | Max branch-and-bound nodes before stopping |
| `maxMemory` | float | Some | Max memory (MB) during solve |
| `presolve` | bool | CBC, SCIP | Enable/disable presolve phase |
| `cuts` | bool | CBC | Enable/disable cutting planes |
| `strong` | int | CBC | Strong branching look-ahead depth |
| `timeMode` | str | CBC | 'elapsed' (wall-clock) or 'cpu' time mode |
