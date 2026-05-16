# Pynumero — Block-Structured Numerical Tools

## Contents
- Overview
- Installation
- NLP Interfaces
- Linear Solver Interfaces
- Block Vectors and Matrices
- MPI Blocks

## Overview

Pynumero provides block-structured numerical tools for large-scale optimization, enabling efficient handling of decomposed problems with block-diagonal structure. It bridges Pyomo models with high-performance numerical libraries (SuiteSparse, MUMPS, SuperLU, KLU).

Key capabilities:
- Block-structured NLP interfaces for IPOPT
- Custom linear solvers exploiting sparsity patterns
- MPI-parallel block operations
- Automatic detection of disconnected model components

## Installation

Pynumero requires building C++ extensions with SuiteSparse dependencies:

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install libsuitesparse-dev libmumps-5.5.* libsuperlu-dev

# Build pynumero
pyomo build-extensions
```

Alternatively, build from within Python:

```python
from pyomo.contrib.pynumero.build import build_pynumero
build_pynumero()
```

Verify installation:

```python
from pyomo.contrib import pynumero
print(pynumero.__version__)
```

## NLP Interfaces

Create block-structured NLP interfaces from Pyomo models for IPOPT:

```python
from pyomo.contrib.pynumero.interfaces import pyomo_nlp

# Create NLP interface from a Pyomo model
nlp = pyomo_nlp(model)

# Evaluate components
f = nlp.obj()                  # objective value
g = nlp.con_cons()             # constraint residuals
jac = nlp.jac_c()              # constraint Jacobian
hess = nlp.hess()              # Lagrangian Hessian

# Set/get variable values
nlp.set_primals(x_values)
x = nlp.get_primals()

# Solve via IPOPT with block structure
from pyomo.contrib.pynumero.algorithms.solvers import instantiate_ipopt
ipopt_solver = instantiate_ipopt(nlp)
ipopt_solver.solve()
```

## Linear Solver Interfaces

Pynumero provides linear solvers that exploit block-diagonal structure:

```python
from pyomo.contrib.pynumero.linear_solvers import (
    mumps_direct_solver,
    klu_direct_solver,
    superlu_direct_solver
)

# Create a block-structured linear solver
solver = mumps_direct_solver(nlp.jac_c_structure())

# Solve linear system
solution = solver.solve(rhs_vector)

# Update with new Jacobian
solver.update(new_jacobian_values)
```

Available solvers: MUMPS (recommended for large problems), KLU (fast for circuit simulation), SuperLU (general sparse).

## Block Vectors and Matrices

Block-structured data containers for efficient computation:

```python
from pyomo.contrib.pynumero.block_datastructures import (
    block_vector,
    block_matrix
)

# Create block vector from dimension list
dims = [10, 20, 15]
bv = block_vector(dims)
bv[0][:] = 1.0   # first block
bv[1][5] = 2.5   # element in second block

# Create block matrix
bm = block_matrix(dims, dims)
bm[0, 0] = scipy.sparse.random(10, 10, density=0.1)
bm[1, 1] = scipy.sparse.eye(20)

# Block operations
result = bm @ bv    # matrix-vector product
```

Block structures automatically align with disconnected model components detected by incidence analysis.

## MPI Blocks

Distribute block-structured computation across MPI processes:

```python
from pyomo.contrib.pynumero.block_datastructures import mpi_block_vector
from pyomo.contrib.pynumero.algorithms.decomposition import benders_decomposition

# Parallel Benders decomposition
benders = benders_decomposition(
    master_model=model_master,
    subproblem_models=[model_sub1, model_sub2],
    master_solver='cbc',
    subproblem_solver='ipopt'
)
results = benders.solve()
```

MPI support enables parallel evaluation of disconnected subproblems within decomposition algorithms. Requires MPI-enabled Python (mpi4py).
