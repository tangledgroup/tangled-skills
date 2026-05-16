# Modeling Utilities

## Contents
- Flattener
- Nonlinear Preprocessing Transformations
- Model Scaling
- Latex Printing
- aslfunctions (AMPL External Functions)

## Flattener

Convert hierarchical block-structured models into flat data structures for analysis:

```python
from pyomo.dae.flatten import flatten_variable_indices, flatten_block

# Flatten all variables indexed by a specific set
flat = flatten_variable_indices(model, model.I)
# Returns dict mapping index -> list of (variable, index_tuple)

# Flatten block structure
for var, indices in flatten_block(model):
    print(f"{var.name}: {indices}")
```

Flattening is useful for:
- Accessing all components at a particular index across the model hierarchy
- Generating reports or data exports
- Analyzing model structure without traversing blocks manually

## Nonlinear Preprocessing Transformations

`pyomo.contrib.preprocessing` provides transformations for NLPs, MINLPs, and GDPs:

```python
from pyomo.contrib.preprocessing import preprocessing as pp

# Variable Aggregator: merge variables linked by equality constraints
agg = pp.VariableAggregator()
agg.apply(model)

# Fixed Variable Detector: find de-facto fixed variables
detector = pp.FixedVarDetector()
detector.apply(model)

# Equality Propagation: propagate fixing through x = y equalities
propagator = pp.FixedVarPropagator()
propagator.apply(model)

# Bound Propagation: propagate bounds through equalities
bound_prop = pp.VarBoundPropagator()
bound_prop.apply(model)

# Trivial Constraint Deactivation: remove always-satisfied constraints
deactivator = pp.TrivialConstraintDeactivator()
deactivator.apply(model)

# Constraints to Variable Bounds: convert simple bound constraints
bound_transform = pp.ConstraintToVarBoundTransform()
bound_transform.apply(model)

# Induced Linearity: reformulate nonlinear constraints that become linear
linearity = pp.InducedLinearity()
linearity.apply(model)

# Initialize variables to midpoint of bounds
init_mid = pp.InitMidpoint()
init_mid.apply(model)

# Remove zero terms (0 * v) from constraints
zero_remover = pp.RemoveZeroTerms()
zero_remover.apply(model)
```

Apply preprocessing before solving to improve numerical stability and solver performance.

## Model Scaling

Scale model variables and constraints to improve numerical properties:

```python
import pyomo.environ as pyo
from pyomo.core import Suffix

model = pyo.ConcreteModel()
model.x = pyo.Var(bounds=(0, 10000))
model.y = pyo.Var(bounds=(0, 0.001))
model.obj = pyo.Objective(expr=model.x + model.y)
model.c = pyo.Constraint(expr=model.x * model.y >= 1)

# Define scaling factors using a Suffix
model.scaling_factor = Suffix(direction=Suffix.EXPORT)
model.scaling_factor[model.x] = 1e-3    # scale x by 0.001
model.scaling_factor[model.y] = 1e3     # scale y by 1000
model.scaling_factor[model.c] = 1.0     # constraint scaling

# Apply scaling transformation
from pyomo.core.plugins.transform.scaling import ScaleModel
scaling_transformation = ScaleModel()
scaled_model = scaling_transformation.create_scaled_model(model)

# Solve scaled model
opt = pyo.SolverFactory('ipopt')
results = opt.solve(scaled_model)

# Retrieve unscaled solution
unscaled_results = scaling_transformation.unscale_model(
    scaled_model,
    results
)
```

Scaling is critical for NLP solvers. Target scale of ~1 for all variables and constraints.

## Latex Printing

Generate LaTeX representation of models for documentation:

```python
from pyomo.util.latex import generate_latex

# Generate LaTeX for entire model
latex_str = generate_latex(model)

# Generate LaTeX for specific components
latex_str = generate_latex(model, components=[model.obj, model.c])

# With options
latex_str = generate_latex(
    model,
    label=True,           # include labels
    number=False,         # don't number equations
    align='&='            # alignment character
)

print(latex_str)
```

## aslfunctions (AMPL External Functions)

Use AMPL-style external functions in Pyomo expressions:

```python
from pyomo.environ import asl

# Access AMPL math functions
model = pyo.ConcreteModel()
model.x = pyo.Var()

# Use external functions
model.c = pyo.Constraint(
    expr=asl.log(model.x) + asl.exp(-model.x) >= 0
)

# Available functions: log, exp, sin, cos, tan, sqrt, abs,
# floor, ceil, sign, power, etc.
```

These provide AMPL-compatible function names for models ported from AMPL.
