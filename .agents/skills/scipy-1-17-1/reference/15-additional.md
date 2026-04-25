# Additional SciPy Topics

This reference covers additional SciPy submodules and important topics including ODR (Orthogonal Distance Regression), datasets, differentiation, compressed sparse graph routines, parallel execution, and thread safety.

## ODR - Orthogonal Distance Regression

### Basic ODR Fitting

```python
from scipy import odr
import numpy as np

# Sample data with errors in both x and y
x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
y = np.array([0.1, 1.9, 3.8, 2.7, 6.2, 7.8])

# Estimate errors (if known)
sx = np.zeros_like(x)  # No x errors
sy = np.ones_like(y) * 0.2  # Constant y error

# Define model function
def linear_func(B, x):
    return B[0] * x + B[1]  # y = mx + b

# Create ODR model
model = odr.Model(linear_func)

# Create ODR data object
data = odr.RealData(x, y, sx=sx, sy=sy)

# Create ODR instance with initial parameter estimates
odr_instance = odr.ODR(data, model, beta0=[1.0, 0.0])

# Run regression
result = odr_instance.run()

# Access results
print(f"Parameters: {result.beta}")  # [slope, intercept]
print(f"Standard errors: {result.sd_beta}")
print(f"Residual variance: {result.res_var()}")
```

### ODR with Errors in Both Variables

```python
from scipy import odr
import numpy as np

# Data with measurement errors in both x and y
x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
y = np.array([2.1, 3.9, 6.2, 8.1, 9.8])

# Known errors in both variables
sx = np.array([0.1, 0.1, 0.15, 0.1, 0.1])  # x errors
sy = np.array([0.2, 0.2, 0.2, 0.25, 0.2])  # y errors

# Quadratic model: y = a*x² + b*x + c
def quadratic_func(B, x):
    return B[0] * x**2 + B[1] * x + B[2]

model = odr.Model(quadratic_func)
data = odr.RealData(x, y, sx=sx, sy=sy)

# Initial guess: [a, b, c]
odr_instance = odr.ODR(data, model, beta0=[0.5, 0.0, 0.0])
result = odr_instance.run()

print(f"Fitted parameters: {result.beta}")
print(f"Parameter standard deviations: {result.sd_beta}")
```

### Weighted ODR

```python
from scipy import odr
import numpy as np

# Data with weights (inverse of variance)
x = np.linspace(0, 10, 20)
y = 2 * x + 5 + np.random.randn(20) * 0.5

# Weights (higher weight = more reliable measurement)
weights = np.ones_like(y)
weights[5:10] = 2.0  # More confident in middle measurements

# Model
def line(B, x):
    return B[0] * x + B[1]

model = odr.Model(line)
data = odr.RealData(x, y)

odr_instance = odr.ODR(data, model, beta0=[1.0, 0.0])
odr_instance.set_weight(weights)
result = odr_instance.run()
```

### ODR Output and Diagnostics

```python
from scipy import odr

# After running ODR: result = odr_instance.run()

# Check convergence
print(f"Success: {result.success}")
print(f"Message: {result.info_dict['msg']}")
print(f"Iterations: {result.iterations}")

# Parameter estimates and uncertainties
beta = result.beta           # Best-fit parameters
sd_beta = result.sd_beta     # Standard deviations of parameters

# Residual analysis
output = odr_instance.output
residuals = output.residuals  # Orthogonal residuals

# Goodness of fit
print(f"Sum of squared residuals: {result.sst}")
print(f"Residual variance: {result.res_var()}")
```

## scipy.datasets - Sample Datasets

### Accessing Built-in Datasets

```python
from scipy import datasets
import numpy as np

# Note: scipy.datasets is minimal in recent versions
# Most sample data is now in other packages

# Example: Generate synthetic data instead
np.random.seed(42)
n_samples = 100
X = np.random.randn(n_samples, 2)
y = (X[:, 0] + X[:, 1] > 0).astype(int)
```

### Alternative Dataset Sources

```python
# Use scikit-learn for machine learning datasets
from sklearn import datasets
iris = datasets.load_iris()
X = iris.data
y = iris.target

# Use matplotlib sample data
import matplotlib.pyplot as plt
x, y = plt.samples  # If available

# Create synthetic data for testing
def generate_test_data(n=100):
    """Generate test dataset"""
    np.random.seed(42)
    x = np.linspace(0, 10, n)
    y = 2 * x + np.sin(x) + np.random.randn(n) * 0.5
    return x, y
```

## scipy.differentiate - Numerical Differentiation

### Finite Difference Differentiation

```python
from scipy import differentiate
import numpy as np

# Function to differentiate
def f(x):
    return x**3 + 2*x**2 - x + 1

# First derivative at a point
df_dx = differentiate.derivative(f, x=2.0, dx=1e-5)
print(f"f'(2) ≈ {df_dx}")  # Should be close to 3*2² + 4*2 - 1 = 21

# Higher-order derivatives
d2f_dx2 = differentiate.derivative(f, x=2.0, n=2, dx=1e-5)
print(f"f''(2) ≈ {d2f_dx2}")  # Should be close to 6*2 + 4 = 16
```

### Numerical Gradient for Multivariate Functions

```python
from scipy import differentiate
import numpy as np

def f_multivar(x, y):
    return x**2 + y**2 + x*y

# Gradient at a point
grad = differentiate.gradient(f_multivar, (2.0, 3.0), dx=1e-5)
print(f"∇f(2, 3) ≈ {grad}")  # [∂f/∂x, ∂f/∂y]

# Hessian matrix (second derivatives)
hessian = differentiate.hessian(f_multivar, (2.0, 3.0), dx=1e-5)
print(f"Hessian at (2, 3):\n{hessian}")
```

### Differentiation of Array Data

```python
from scipy import differentiate
import numpy as np

# Discrete data points
x = np.linspace(0, 10, 100)
y = np.sin(x) + 0.1 * np.random.randn(100)

# Numerical derivative
dy_dx = differentiate.gradient(y, x)

# Second derivative
d2y_dx2 = differentiate.gradient(dy_dx, x)
```

## scipy.sparse.csgraph - Graph Algorithms on Sparse Matrices

### Connected Components

```python
from scipy.sparse import csgraph
import numpy as np

# Create adjacency matrix (undirected graph)
n_nodes = 100
adj = np.random.rand(n_nodes, n_nodes) > 0.9  # Sparse connectivity
adj = adj.astype(int)
adj = (adj + adj.T) > 0  # Make symmetric

# Convert to sparse format
adj_sparse = scipy.sparse.csr_matrix(adj)

# Find connected components
n_components, labels = csgraph.connected_components(adj_sparse, directed=False)
print(f"Number of connected components: {n_components}")

# Get nodes in each component
for i in range(n_components):
    component_nodes = np.where(labels == i)[0]
    print(f"Component {i}: {len(component_nodes)} nodes")
```

### Shortest Path Algorithms

#### Dijkstra's Algorithm

```python
from scipy.sparse import csgraph
import numpy as np

# Weighted directed graph (adjacency matrix)
n = 100
weights = np.random.rand(n, n) * 10
weights[weights < 0.9] = 0  # Sparse graph
adj_weighted = scipy.sparse.csr_matrix(weights)

# Single-source shortest paths from node 0
distances, predecessors = csgraph.dijkstra(adj_weighted, 
                                           directed=True,
                                           indices=0,
                                           return_predecessors=True)

# Reconstruct path to node k
def reconstruct_path(predecessors, target):
    path = [target]
    current = target
    while predecessors[current] != current:
        current = predecessors[current]
        path.append(current)
    return path[::-1]

path_to_50 = reconstruct_path(predecessors, 50)
print(f"Path to node 50: {path_to_50}")
```

#### Floyd-Warshall Algorithm (All-Pairs)

```python
from scipy.sparse import csgraph
import numpy as np

# Small graph for all-pairs shortest paths
n = 50
adj = np.random.rand(n, n) * 10
adj[adj < 7] = 0  # Sparse
np.fill_diagonal(adj, 0)

# Floyd-Warshall algorithm
distances_all = csgraph.floyd_warshall(adj, directed=True)

# Distance from node i to node j
dist_5_20 = distances_all[5, 20]
print(f"Distance from node 5 to 20: {dist_5_20}")
```

### Minimum Spanning Tree

```python
from scipy.sparse import csgraph
import numpy as np

# Weighted undirected graph
n = 100
weights = np.random.rand(n, n) * 10
weights = (weights + weights.T) / 2  # Symmetric
weights[weights < 5] = 0  # Sparse
np.fill_diagonal(weights, 0)

adj_sparse = scipy.sparse.csr_matrix(weights)

# Compute minimum spanning tree
mst = csgraph.minimum_spanning_tree(adj_sparse)

# Number of edges in MST
n_edges_mst = mst.nnz // 2  # Undirected, so divide by 2
print(f"MST has {n_edges_mst} edges")

# Total weight of MST
mst_weight = mst.data.sum() / 2
print(f"Total MST weight: {mst_weight}")
```

### Random Walks and PageRank

```python
from scipy.sparse import csgraph
import numpy as np

# Create web-like graph (directed)
n = 1000
adj = np.random.rand(n, n) > 0.98  # Very sparse
adj = adj.astype(float)

adj_sparse = scipy.sparse.csr_matrix(adj)

# Compute PageRank
pagerank_scores = csgraph.pagerank(adj_sparse, 
                                    alpha=0.85,  # Damping factor
                                    maxiter=100)

# Top 10 nodes by PageRank
top_10 = np.argsort(pagerank_scores)[::-1][:10]
print(f"Top 10 nodes: {top_10}")
print(f"Their scores: {pagerank_scores[top_10]}")
```

## Parallel Execution in SciPy

### Multi-threading Configuration

```python
import os
import numpy as np

# Control number of threads for BLAS/LAPACK operations
os.environ['OMP_NUM_THREADS'] = '4'  # Set OpenMP threads

# For Intel MKL
os.environ['MKL_NUM_THREADS'] = '4'

# For OpenBLAS
os.environ['OPENBLAS_NUM_THREADS'] = '4'

# Import after setting environment variables
from scipy import linalg, integrate, optimize
```

### Parallel Processing with joblib

```python
from joblib import Parallel, delayed
from scipy import optimize
import numpy as np

# Parallel optimization over multiple initial points
def optimize_from_start(x0):
    def objective(x):
        return sum((x - 2)**2)
    
    result = optimize.minimize(objective, x0, method='BFGS')
    return result.x, result.fun

# Multiple starting points
start_points = [np.random.rand(5) for _ in range(20)]

# Parallel execution
results = Parallel(n_jobs=-1)(  # -1 uses all CPUs
    delayed(optimize_from_start)(x0) for x0 in start_points
)

# Find best result
best_result = min(results, key=lambda r: r[1])
```

### Vectorization for Performance

```python
from scipy import stats
import numpy as np

# Instead of loop (slow)
def slow_version(data):
    results = []
    for x in data:
        results.append(stats.norm.cdf(x))
    return np.array(results)

# Vectorized version (fast)
def fast_version(data):
    return stats.norm.cdf(np.array(data))

# Benchmark
data = np.random.randn(10000)
# fast_version(data) is typically 10-100x faster
```

## Thread Safety Guidelines

### Thread-Safe Operations

```python
import threading
from scipy import linalg, integrate
import numpy as np

# Most SciPy functions are thread-safe when:
# 1. They don't modify global state
# 2. Each thread uses separate arrays

def worker(thread_id):
    """Thread-safe computation"""
    A = np.random.rand(100, 100)
    b = np.random.rand(100)
    
    # This is safe - each thread has its own data
    x = linalg.solve(A, b)
    return x

# Multiple threads can run safely
threads = [threading.Thread(target=worker, args=(i,)) 
           for i in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### Thread-Unsafe Patterns to Avoid

```python
import threading
from scipy import optimize
import numpy as np

# DON'T do this - shared mutable state
shared_result = None

def unsafe_worker(x0):
    global shared_result  # Race condition!
    result = optimize.minimize(lambda x: x**2, x0)
    shared_result = result  # Multiple threads writing

# Instead, use thread-local storage or return values
def safe_worker(x0):
    result = optimize.minimize(lambda x: x**2, x0)
    return result  # Each thread returns its own result
```

### Using Process Pool for CPU-bound Tasks

```python
from multiprocessing import Pool
from scipy import integrate
import numpy as np

def integrate_function(args):
    func, a, b = args
    result, error = integrate.quad(func, a, b)
    return result, error

# List of integration tasks
tasks = [
    (lambda x: np.sin(x), 0, np.pi),
    (lambda x: np.exp(-x**2), -np.inf, np.inf),
    (lambda x: 1/(1+x**2), 0, 1),
]

# Use process pool (better for CPU-bound work)
with Pool(processes=4) as pool:
    results = pool.map(integrate_function, tasks)

print(f"Results: {[r[0] for r in results]}")
```

## Performance Tips

### Memory-Efficient Computing

```python
from scipy import sparse, linalg
import numpy as np

# Use sparse matrices for large, mostly-zero data
n = 10000
A_dense = np.random.rand(n, n) * 0.01  # 99% zeros
A_sparse = sparse.csr_matrix(A_dense < 0.01).astype(float)

# Sparse operations use less memory
b = np.random.rand(n)
x = sparse.linalg.gmres(A_sparse, b)[0]  # Iterative solver
```

### Choosing the Right Algorithm

```python
from scipy import linalg, optimize
import numpy as np

# For small problems (<100 variables), use direct methods
n_small = 50
A_small = np.random.rand(n_small, n_small)
x_small = linalg.solve(A_small, b_small)

# For large sparse problems, use iterative methods
n_large = 10000
A_large = sparse.random(n_large, n_large, density=0.001)
x_large, info = sparse.linalg.cg(A_large, b_large)

# For non-smooth optimization, use derivative-free methods
result = optimize.minimize(non_smooth_func, x0, method='Nelder-Mead')

# For smooth problems with gradients, use gradient-based methods
result = optimize.minimize(smooth_func, x0, method='BFGS', jac=gradient_func)
```

## See Also

- [`scipy.optimize`](references/01-optimize.md) - More optimization details
- [`scipy.sparse.linalg`](references/09-sparse.md) - Sparse linear algebra
- [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html) - Python parallel processing
- [`joblib`](https://joblib.readthedocs.io/) - Parallel utilities for Python
