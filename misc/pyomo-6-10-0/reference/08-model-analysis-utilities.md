# Model Analysis and Utilities

## Contents
- Irreducible Infeasible Sets (IIS)
- Incidence Analysis
- Design of Experiments (DOE)
- Model Predictive Control (MPC)
- Parameter Estimation (parmest)
- Sensitivity Toolbox
- Alternative Optimal Solutions
- Model Flattener
- Scaling and Preprocessing

## Irreducible Infeasible Sets (IIS)

When a model is infeasible, IIS identifies the minimal set of conflicting constraints.

```python
from pyomo.contrib.iis import generate_iis

model = pyo.ConcreteModel()
# ... build infeasible model ...

iis_blocks = generate_iis(model)
if iis_blocks:
    print(f"IIS found with {len(iis_blocks)} components:")
    for block in iis_blocks:
        print(f"  {block}")
else:
    print("No IIS found (may be numerically infeasible)")
```

IIS works with LP solvers that support indicator constraints or by iterative removal. Use after confirming infeasibility to diagnose which constraints conflict.

## Incidence Analysis

Analyze the structural sparsity pattern of models using incidence matrices:

```python
from pyomo.contrib.incidence_analysis import (
    generate_incidence_matrix,
    connected_components,
    DulmageMendelsohnDecomposition
)

# Build incidence matrix (variables vs constraints)
incidence = generate_incidence_matrix(model)

# Find connected components (disconnected subproblems)
components = connected_components(incidence)
for i, comp in enumerate(components):
    print(f"Component {i}: {len(comp)} variables/constraints")

# Dulmage-Mendelsohn decomposition for structural analysis
dm = DulmageMendelsohnDecomposition(incidence)
print(f"Underdetermined: {len(dm.set_x0)} vars")
print(f"Well-determined: {len(dm.set_x1)} vars")
print(f"Overdetermined: {len(dm.set_x2)} vars")
```

Useful for identifying disconnected subproblems, structural infeasibility, and variable-constraint matching.

## Design of Experiments (DOE)

Generate experimental designs for model calibration and sensitivity studies:

```python
from pyomo.contrib.doe.api import factorial, generate_scenarios

# Full factorial design
design = factorial(
    factors={'temp': (300, 500), 'pressure': (1, 10)},
    n_levels=5
)

# Generate scenario data for parameter estimation
scenarios = generate_scenarios(model, design)
```

Supports full factorial, fractional factorial, and Latin hypercube designs.

## Model Predictive Control (MPC)

pyomo.mpc provides tools for model predictive control workflows:

```python
from pyomo.contrib.mpc_tools import MPCModel

mpc = MPCModel()
mpc.load_model(model_file)
mpc.set_horizon(Np=10, Nc=5)  # prediction and control horizons
mpc.solve()
```

MPC tools handle receding horizon optimization, constraint handling, and setpoint tracking.

## Parameter Estimation (parmest)

Estimate model parameters from experimental data:

```python
from pyomo.contrib.parmest import gpp_least_squares, parallel_estimate

# Define parameters to estimate
params = ['k1', 'k2', 'Ea']

# Experimental data as list of dicts
data = [
    {'time': [0, 1, 2], 'conc_A': [1.0, 0.5, 0.25]},
    # more experiments...
]

# Global parameter estimation
results = gpp_least_squares(
    model_file='model.py',
    data_list=data,
    params=params,
    bounds={'k1': (0.01, 10), 'k2': (0.01, 10)},
    n_estimates=20
)
```

Supports least squares, maximum likelihood, and weighted objectives. Parallel execution via `parallel_estimate()`.

## Sensitivity Toolbox

Compute sensitivities of solutions with respect to parameters:

```python
from pyomo.contrib.sensitivities import SensitivityResults

# After solving the model
sens = SensitivityResults(model)
sens.compute_sensitivities(
    params=['p1', 'p2'],
    vars_of_interest=['x1', 'x2']
)
print(sens.sensitivity_dict)
```

Provides first-order sensitivities via implicit function theorem. Requires IPOPT for Lagrange multiplier information.

## Alternative Optimal Solutions

Find multiple optimal solutions with the same objective value:

```python
from pyomo.contrib.alternativeopt import find_alternative_objectives

# After finding first optimal solution
alt_results = find_alternative_objectives(
    model,
    solver_name='cbc',
    num_solutions=5
)
```

Uses cutting-plane approach to enumerate alternative optima. Useful for multi-objective trade-off analysis.

## Model Flattener

Flatten hierarchical block structures into a single-level representation:

```python
from pyomo.core.util import flatten_model

# Flatten all variables/constraints from nested blocks
flat_vars = list(flatten_model(model, type=pyo.Var))
flat_cons = list(flatten_model(model, type=pyo.Constraint))
```

Useful for counting model components, exporting to flat formats, or debugging block hierarchies.

## Scaling and Preprocessing

**Variable/constraint scaling** improves solver numerical stability:

```python
from pyomo.contrib.pynumero.interfaces import sympy_interface

# Automatic scaling
from pyomo.util.calc_var_value import set_initial_point
from pyomo.contrib.preprocessing import preprocess
```

**Preprocessing transformations**:

```python
from pyomo.core import TransformationFactory

# Remove trivial constraints (0 <= x <= 0)
TransformationFactory('preprocess.trivial_constraints').apply_to(model)

# Aggregate variables that appear identically
TransformationFactory('preprocess.aggregate_variables').apply_to(model)

# Substitute fixed variables
TransformationFactory('preprocess.substitute_fixed_vars').apply_to(model)
```

**NLWriter scaling options**:

```python
from pyomo.repn.plugins.nl_writer import NLWriter
nl = NLWriter()
nl.write(model, 'model.nl', format_version=3, include_vars=None, include_constraints=None)
```
