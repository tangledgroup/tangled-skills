# Analysis Tools

## Contents
- Infeasibility Diagnostics (IIS/MIS)
- Alternative (Near-)Optimal Solutions
- Community Detection
- Design of Experiments (DoE)
- Model Predictive Control (MPC)
- Parameter Estimation (parmest)
- Sensitivity Toolbox

## Infeasibility Diagnostics (IIS/MIS)

When a model is infeasible, find the minimal set of conflicting constraints.

**IIS (Infeasible Irreducible System)** — uses commercial solver capabilities:

```python
from pyomo.contrib.iis import write_iis

# Requires CPLEX, Gurobi, or Xpress
write_iis(model, 'infeasible.ilp', solver='gurobi')

# The output file identifies the irreducible infeasible subset
# In Pyomo, deactivated constraints/variables mark the IIS
```

**MIS (Minimal Intractable System)** — open-source alternative:

```python
from pyomo.contrib.mis.mis import find_mis

mis = find_mis(model, solver='glpk')
# mis contains the minimal set of conflicting constraints
for con in mis:
    print(f"Conflicting: {con}")
```

## Alternative (Near-)Optimal Solutions

Find multiple solutions within a specified gap of the optimum:

```python
from pyomo.contrib.altblock import find_alternate_solutions

# Find all solutions within 5% of optimal
solutions = find_alternate_solutions(
    model,
    opt=pyo.SolverFactory('glpk'),
    gap=0.05,       # accept solutions within 5% of optimum
    max_solutions=10
)

for sol in solutions:
    for var in model.component_objects(pyo.Var):
        for v in var.values():
            print(f"{v.name}: {sol[v]}")
    print("---")
```

## Community Detection

Identify weakly connected subproblems within a large model:

```python
from pyomo.contrib.community_detection import detect_communities

# Detect communities of variables and constraints
communities = detect_communities(
    model,
    method='sparsity',     # or 'incidence'
    n_communities=5        # target number of communities
)

# Each community is a set of connected variables/constraints
for i, community in enumerate(communities):
    print(f"Community {i}: {len(community)} components")
```

Useful for decomposing large models into independently solvable subproblems.

## Design of Experiments (DoE)

Systematically explore model behavior across parameter spaces:

```python
from pyomo.contrib.doe.api import factorial_design, run_doe

# Define factors (parameters to vary)
factors = [
    ('temperature', (300, 500)),   # (min, max)
    ('pressure', (1, 10)),
    ('concentration', (0.1, 1.0))
]

# Generate experimental design
design = factorial_design(factors, n_runs=20)

# Run experiments
results = run_doe(
    model,
    design,
    solver=pyo.SolverFactory('ipopt'),
    response_variables=['output_var']
)
```

## Model Predictive Control (MPC)

Implement receding-horizon optimization for dynamic systems:

```python
from pyomo.contrib.mpc_tools import MPCModel

mpc = MPCModel(
    model=model,
    time_horizon=10,
    control_horizon=5,
    solver=pyo.SolverFactory('ipopt')
)

# Run MPC step
control_actions = mpc.step(measurements={'sensor1': 25.0})

# Execute control actions, then call mpc.step() again next timestep
```

MPC solves an optimization problem at each timestep using current measurements and a predictive model, then implements only the first control action.

## Parameter Estimation (parmest)

Estimate model parameters from experimental data:

```python
from pyomo.contrib.parmest import globalsens, fixedparameterest

# Define observable variables and their measured values
observables = ['output1', 'output2']
parameters = [model.k1, model.k2]
data = pd.DataFrame({
    'output1': [1.2, 3.4, 5.6],
    'output2': [0.8, 2.1, 4.3]
})

# Fixed parameter estimation (optimize parameters to fit data)
results = fixedparameterest.GP_estimate_parameters(
    bounds=[(0, 10), (0, 10)],
    observables=observables,
    parameters=parameters,
    data=data,
    model_construction=lambda: build_model(),
    solver_name='ipopt'
)
```

## Sensitivity Toolbox

Compute approximate solutions for perturbed parameters using sIPOPT:

```python
from pyomo.contrib.sensitivity_tool import SensitivityToolbox

st = SensitivityToolbox()

# Solve base case
results = st.solve(model, solver='sipopt')

# Get sensitivity of solution w.r.t. parameter changes
sensitivities = st.get_sensitivities(
    model,
    parameters=[model.p1, model.p2],
    variables=[model.x1, model.x2]
)

# Evaluate at perturbed parameter values
perturbed_solution = st.evaluate(
    model,
    parameter_values={model.p1: 5.0, model.p2: 10.0}
)
```

Requires sIPOPT and k_aug installation. Provides fast approximate solutions for small parameter perturbations without re-solving.
