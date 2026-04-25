# Complete API Reference

> **Source:** PuLP Documentation — technical/pulp.html, technical/solvers.html, technical/constants.html
> **Loaded from:** SKILL.md (via progressive disclosure)

## Module: `pulp`

### Core Classes

#### `LpProblem(name='NoName', sense=1)`

Container for a linear or integer programming problem.

**Parameters:**
- `name` (str) — name used in output files
- `sense` (int) — `LpMinimize` (1, default) or `LpMaximize` (-1)

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `objective` | `LpAffineExpression` | The objective function |
| `constraints` | dict[str, LpConstraint] | Named constraints |
| `status` | int | Solver return status code |

**Methods:**

- **`solve(solver=None, **kwargs) → int`** — Solve the problem. Optional `solver` argument specifies which solver to use; defaults to the default solver. Modifies problem attributes in-place with solution values.

- **`roundSolution(epsInt=1e-05, eps=1e-07)`** — Round LP variables to integer values within tolerance.

- **`setObjective(obj)`** — Set the objective function. `obj` can be `LpAffineExpression`, `LpVariable`, or numeric.

- **`writeLP(filename, writeSOS=1, mip=True, max_length=100) → list[LpVariable]`** — Write problem to `.lp` file. Returns list of variables written.

- **`writeMPS(filename, mpsSense=0, rename=False, mip=True, with_objsense=False)`** — Write problem to `.mps` file. Returns `(variable_names, constraint_names, objective_name, pulp_names_in_column_order)`.

- **`toJson(filename, *args, **kwargs)`** — Save model to JSON file. Accepts additional arguments for `json.dump()`.

- **`@classmethod fromJson(filename) → (dict[str, LpVariable], LpProblem)`** — Load model from JSON file. Returns tuple of variable dict and restored problem.

- **`@classmethod fromMPS(filename) → (dict[str, LpVariable], LpProblem)`** — Load model from MPS file.

- **`@classmethod from_dict(data) → (dict[str, LpVariable], LpProblem)`** — Restore model from dictionary representation.

- **`to_dict() → dict`** — Export model to dictionary (includes all data: variables, constraints, objective, parameters, SOS sets).

- **`variables() → list[LpVariable]`** — List of all problem variables in id order.

#### `LpVariable(_var)`

Decision variable. Created via `LpProblem.add_variable()` or `add_variables()`, `add_variable_dict()`, `add_variable_matrix()`.

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Variable name |
| `lowBound` | float or None | Lower bound (-inf if None) |
| `upBound` | float or None | Upper bound (+inf if None) |
| `cat` | str | Category: "Continuous", "Integer", or "Binary" |
| `varValue` | float or None | Solution value (set after solving) |
| `dj` | float or None | Reduced cost (set after solving) |
| `id` | int | Internal index in model's variable list |

**Methods:**
- **`value()`** — Return the solution value, or None if not solved.
- **`valueOrDefault()`** — Return solution value, or a value within bounds if not solved.
- **`fixValue()`** — Fix the variable by setting bounds to its initial value.
- **`isFixed()` → bool** — True if `lowBound == upBound`.
- **`toDict() → dict`** — Export variable to dictionary.
- **`@classmethod fromDict(problem, data)`** — Create variable from dict and add to problem.
- **`toDataclass()`** — Export to `MPSVariable` dataclass.
- **`@classmethod fromDataclass(problem, mps)`** — Create from `MPSVariable` dataclass.

#### `LpAffineExpression(_expr)`

Linear combination of variables plus a constant. Carries constraint sense for pending constraints created by `<=`, `>=`, `==`.

**Operations supported:** `+`, `-`, `*` (by scalar), unary negation, `<=`, `>=`, `==`

#### `LpConstraint(_constr)`

A single constraint: `sum(a_i * x_i) <=/=/>= b`.

**Attributes:**
- `name` — constraint name
- `coeffs` — dict mapping variables to coefficients
- `constant` — RHS constant
- `sense` — constraint sense (`LpConstraintEQ`, `LpConstraintLE`, `LpConstraintGE`)
- `pi` — shadow price (set after solving)

## Module: `pulp.constants`

### Variable Categories

| Constant | Value |
|----------|-------|
| `LpContinuous` | `"Continuous"` |
| `LpInteger` | `"Integer"` |
| `LpBinary` | `"Binary"` |

### Problem Sense

| Constant | Value |
|----------|-------|
| `LpMinimize` | 1 |
| `LpMaximize` | -1 |

### Constraint Senses

| Constant | Symbolic | Numeric |
|----------|----------|---------|
| `LpConstraintEQ` | `==` | 0 |
| `LpConstraintLE` | `<=` | -1 |
| `LpConstraintGE` | `>=` | 1 |

### Solution Status

| Constant | String | Numeric |
|----------|--------|---------|
| `LpStatusOptimal` | "Optimal" | 1 |
| `LpStatusNotSolved` | "Not Solved" | 0 |
| `LpStatusInfeasible` | "Infeasible" | -1 |
| `LpStatusUnbounded` | "Unbounded" | -2 |
| `LpStatusUndefined` | "Undefined" | -3 |

### Solution Quality

| Constant | String | Numeric |
|----------|--------|---------|
| `LpSolutionOptimal` | "Optimal Solution Found" | 1 |
| `LpSolutionNoSolutionFound` | "No Solution Found" | 0 |
| `LpSolutionStatusInfeasible` | "No Solution Exists" | -1 |
| `LpSolutionStatusUnbounded` | "Solution is Unbounded" | -2 |
| `LpSolutionIntegerFeasible` | "Solution Found" | 2 |

### Exception

- **`PulpError`** — Base exception class for PuLP errors.

## Module: `pulp.apis` — Solver Interfaces

### Base Classes

- **`LpSolver`** — Abstract base class for solver interfaces.
- **`LpSolver_CMD`** — Base class for command-line solver integrations.

### CMD Solvers

| Class | Solver | Key Parameters |
|-------|--------|----------------|
| `COIN_CMD` | CBC | `mip`, `msg`, `timeLimit`, `gapRel`, `gapAbs`, `presolve`, `cuts`, `strong`, `options`, `warmStart`, `keepFiles`, `path`, `threads`, `logPath`, `timeMode`, `maxNodes` |
| `GLPK_CMD` | GLPK | `msg`, `timeLimit`, `path`, `options`, `keepFiles`, `mip`, `tmpDir` |
| `CPLEX_CMD` | CPLEX | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |
| `GUROBI_CMD` | Gurobi | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |
| `HiGHS_CMD` | HiGHS | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles`, `warmStart` |
| `SCIP_CMD` | SCIP | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |
| `COPT_CMD` | COPT | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |
| `CHOCO_CMD` | CHOCO | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |
| `MIPCL_CMD` | MIPCL | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |
| `FSCIP_CMD` | FSCIP | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |
| `XPRESS_CMD` | XPRESS | `mip`, `msg`, `timeLimit`, `path`, `options`, `keepFiles` |

### Python API Solvers

| Class | Solver | Notes |
|-------|--------|-------|
| `COINMP_DLL` | COIN-OR CoinMP | DLL-based CBC/CLP |
| `CPLEX_PY` | IBM CPLEX | Full CPLEX Python API |
| `GUROBI` | Gurobi | Full Gurobi Python API |
| `MOSEK` | MOSEK | Full MOSEK API |
| `HiGHS` | HiGHS | Full HiGHS Python API |
| `SCIP_PY` | SCIP | SCIP Python API |
| `COPT` | COPT | COPT Python API |
| `XPRESS_PY` | FICO XPRESS | XPRESS Python API |
| `CYLP` | COIN-OR Cylp | Cython interface to COIN-OR |
| `PYGLPK` | GLPK | SWIG-wrapped GLPK |
| `YAPOSIB` | Yaposib | Simple LP solver |

### Solver Class Methods

All solver classes inherit:
- **`available() → bool`** — Check if the solver binary/library is available.
- **`actualSolve(lp, **kwargs) → int`** — Solve a well-formulated LP problem.
- **`name`** (property) — Solver name string (e.g., `"COIN_CMD"`).
- **`toDict() → dict`** — Export solver configuration.
- **`toJson(filename)`** — Export solver config to JSON file.

### Module-Level Functions

- **`listSolvers(onlyAvailable=False) → list[str]`** — List available solver names.
- **`getSolver(name, *args, **kwargs) → LpSolver`** — Create solver instance by name.
- **`getSolverFromDict(d) → LpSolver`** — Restore solver from dictionary.
- **`getSolverFromJson(filename) → LpSolver`** — Restore solver from JSON file.
- **`PulpSolverError`** — Exception raised for solver-related errors.

## Module: `pulp.utilities`

| Function | Description |
|----------|-------------|
| `value(x)` | Returns numeric value of variable/expression, or x if already a number |
| `valueOrDefault(x)` | Returns value or a default within bounds if not solved |
| `lpSum(iterable)` | Sum of affine expressions |
| `lpDot(a, b)` | Dot product of two lists (coefficients × variables) |
| `allcombinations(iterable, k)` | All combinations of up to k items |
| `allpermutations(iterable, k)` | All permutations of up to k items |
| `makeDict(headers, array, default=None)` | Build nested dict from flat list |
| `splitDict(data)` | Split a nested dictionary |
| `read_table(data, coerce_type, transpose=False)` | Parse tabular data |
| `isNumber(x) → bool` | Check if x is int or float |
| `resource_clock()` | Get child process CPU time |

## Module: `pulp.pulp` — Problem Construction Methods

### `LpProblem.add_variable(name, lowBound=None, upBound=None, cat="Continuous")`

Add a single variable to the problem.

### `LpProblem.add_variables(name, n=1, lowBound=None, upBound=None, cat="Continuous")`

Add n variables at once. Returns unpacked variables.

### `LpProblem.add_variable_dict(name, keys, lowBound=None, upBound=None, cat="Continuous")`

Add variables indexed by hashable keys.

### `LpProblem.add_variable_matrix(rows, cols, lowBound=None, upBound=None, cat="Continuous")`

Add a 2D matrix of variables.

### Expression Construction

```python
# Using operators on variables
x = prob.add_variable("x")
y = prob.add_variable("y")

expr = 3 * x + 5 * y - 10       # LpAffineExpression
prob += expr <= 20               # adds constraint

# Direct constraint syntax
prob += x + y == 10, "my_constraint"   # name is optional

# Objective function (expression without sense becomes objective)
prob += -4 * x + y, "profit"
```

## References

- API docs: https://coin-or.github.io/pulp/technical/pulp.html
- Solvers docs: https://coin-or.github.io/pulp/technical/solvers.html
- Constants docs: https://coin-or.github.io/pulp/technical/constants.html
