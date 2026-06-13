# Solvers

## Solver Architecture

PuLP supports two integration modes for each solver:

- **Command-line (`_CMD`)** — PuLP writes an LP or MPS file, executes the solver binary from the command line, and parses the output. Names end with `_CMD`: `COIN_CMD`, `GLPK_CMD`, `CPLEX_CMD`, `GUROBI_CMD`.
- **Python API** — PuLP calls the solver's native Python library directly. Names without `_CMD`: `GUROBI`, `CPLEX_PY`, `HiGHS`, `MOSEK`, `SCIP_PY`, `XPRESS`.

## Listing Available Solvers

```python
import pulp as pl

# All known solvers
solver_list = pl.listSolvers()
# ['GLPK_CMD', 'PYGLPK', 'CPLEX_CMD', 'CPLEX_PY', 'GUROBI', 'GUROBI_CMD',
#  'COIN_CMD', 'CHOCO_CMD', 'MIPCL_CMD', 'SCIP_CMD', 'HiGHS', ...]

# Only solvers currently available on this system
available = pl.listSolvers(onlyAvailable=True)

# Get a solver by name
solver = pl.getSolver('CPLEX_CMD')
solver = pl.getSolver('COIN_CMD', timeLimit=60, gapRel=0.01)
```

## COIN_CMD — CBC (Default Open-Source Solver)

CBC is the default open-source solver used by PuLP. It is invoked through `COIN_CMD`:

```python
import pulp as pl

# Default: uses cbcbox binary or cbc on PATH
solver = pl.COIN_CMD()

# Explicit path to CBC binary
solver = pl.COIN_CMD(path=r"C:\path\to\cbc.exe")

# With options
solver = pl.COIN_CMD(
    timeLimit=60,       # Maximum seconds
    gapRel=0.01,        # Relative gap tolerance (fraction)
    gapAbs=10,          # Absolute gap tolerance
    threads=4,          # Maximum threads
    msg=True,           # Show solver output
    presolve=True,      # Enable presolve
    cuts=True,          # Enable Gomory/knapsack/probing cuts
    strong=5,           # Strong branching depth (0-2147483647)
    warmStart=False,    # Use current variable values as start
    keepFiles=False,    # Keep temp files after solving
    logPath="cbc.log",  # Log file path
    timeMode='elapsed', # 'elapsed' (wall-time) or 'cpu'
    maxNodes=None,      # Maximum branch-and-bound nodes
)
```

CBC resolution order:
1. If `cbcbox` package is installed (`pip install pulp[cbc]`), PuLP uses the bundled binary
2. Otherwise, looks for `cbc` / `cbc.exe` on `PATH`
3. Use `path=` parameter to specify explicitly

## GLPK_CMD

```python
solver = pl.GLPK_CMD()
solver = pl.GLPK_CMD(path="/usr/bin/glpsol", msg=False)
```

## CPLEX

**Command-line:**
```python
solver = pl.CPLEX_CMD()
solver = pl.CPLEX_CMD(path=r"C:\Program Files\IBM\ILOG\CPLEX_Studio128\cplex\bin\x64_win64\cplex.exe")
```

**Python API:**
```python
solver = pl.CPLEX_PY()
solver = pl.CPLEX_PY(timeLimit=10)
```

Environment variables (Linux/Mac, add to `~/.bashrc`):
```bash
export CPLEX_HOME="/opt/ibm/ILOG/CPLEX_Studio128/cplex"
export PATH="${PATH}:${CPLEX_HOME}/bin/x86-64_linux"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${CPLEX_HOME}/bin/x86-64_linux"
export PYTHONPATH="${PYTHONPATH}:/opt/ibm/ILOG/CPLEX_Studio128/cplex/python/3.5/x86-64_linux"
```

## GUROBI

**Python API (preferred):**
```python
solver = pl.GUROBI()
```

**Command-line:**
```python
solver = pl.GUROBI_CMD()
solver = pl.GUROBI_CMD(path="/opt/gurobi1001/linux64/bin/gurobi_cl")
```

Environment variables (Linux/Mac):
```bash
export GUROBI_HOME="/opt/gurobi1001/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
```

## HiGHS

HiGHS is a high-performance open-source solver available via both API and command-line:

```python
# Python API (preferred)
solver = pl.HiGHS()

# Command-line
solver = pl.HiGHS_CMD()
```

## MOSEK

```python
solver = pl.MOSEK()
solver.putparam("paramname", value)
```

## SCIP

```python
# Python API
solver = pl.SCIP_PY()

# Command-line
solver = pl.SCIP_CMD()
```

## Other Solvers

- **COPT** — `pl.COPT()` (API), `pl.COPT_CMD()` (command-line), `pl.COPT_DLL()` (DLL)
- **XPRESS** — `pl.XPRESS()` (API), `pl.XPRESS_CMD()` (command-line), `pl.XPRESS_PY()` (Python API)
- **CHOCO** — `pl.CHOCO_CMD()` (constraint programming solver, command-line only)
- **MIPCL** — `pl.MIPCL_CMD()` (command-line only)
- **FSCIP** — `pl.FSCIP_CMD()` (fixed-variable SCIP, command-line only)
- **YAPOSIB** — `pl.YAPOSIB()` (API only)

## Solving with a Specific Solver

```python
# Default solver (first available)
prob.solve()

# Specific solver instance
prob.solve(pl.COIN_CMD(msg=True, timeLimit=120))

# Store result status
status = prob.solve(pl.GUROBI())
print(LpStatus[prob.status])
```

## Solver Parameters Reference

Common parameters across most solvers:

- `timeLimit` — Maximum solving time in seconds
- `gapRel` — Relative optimality gap tolerance (fraction, e.g., 0.01 for 1%)
- `gapAbs` — Absolute optimality gap tolerance
- `msg` — Boolean to show/hide solver output (`True` recommended for debugging)
- `mip` — If `False`, treat as LP even with integer variables
- `threads` — Maximum number of CPU threads (where supported)
- `warmStart` — Use current variable values as initial solution

## Solution Status Codes

After solving, check `prob.status`:

| Constant | Value | Meaning |
|----------|-------|---------|
| `LpStatusNotSolved` | 0 | Problem not yet solved |
| `LpStatusOptimal` | 1 | Optimal solution found |
| `LpStatusInfeasible` | -1 | No feasible solution exists |
| `LpStatusUnbounded` | -2 | Objective is unbounded |
| `LpStatusUndefined` | -3 | Solution status undefined |

Convert to string: `LpStatus[prob.status]` → `"Optimal"`, `"Infeasible"`, etc.

## Troubleshooting Solver Issues

**"Error while trying to execute cbc.exe"** — Install `pulp[cbc]` or ensure `cbc` is on `PATH`. In Jupyter/conda environments, the kernel's `PATH` may differ from your shell. Use `msg=True` for details.

**"No solver available"** — No solver was detected. Install one:
```bash
pip install "pulp[cbc]"
```

**Memory issues** — Large MIP models may exhaust memory. Use 64-bit Python, increase system RAM, or try a more efficient solver (HiGHS, Gurobi).

**Numerical precision problems** — Scale your data. Avoid mixing very large numbers (10^11) with small decimals. Round values when exact precision is unnecessary.
