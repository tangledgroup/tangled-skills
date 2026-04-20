# Utils, Randomness, and Configuration

NetworkX provides utility functions for random number generation, configuration management, and decorator utilities.

## Random Number Generation

```python
import networkx as nx
from networkx import utils

# Generate random permutation of 0..n-1
perm = nx.utils.random_permutation(10)
print(perm)  # e.g., [3, 7, 1, 9, 0, 5, 2, 8, 4, 6]

# Random element from sequence (weighted or uniform)
elem = nx.utils.arbitrary_element([1, 2, 3, 4, 5])
print(elem)  # Random choice

# Random k elements without replacement (Fisher-Yates shuffle)
sample = nx.utils.random_sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], k=3)
print(sample)  # e.g., [4, 7, 2]

# Random power-law sequence (Pareto distribution)
seq = nx.utils.powerlaw_sequence(100, exponent=2.5)
print(seq[:10])  # Power-law distributed values

# Reservoir sampling (for streaming data of unknown size)
reservoir = nx.utils.reservoir(iterable=range(1000), size=10, seed=None)
print(reservoir)  # 10 random elements from stream

# Random node selection from graph (weighted or uniform)
node = nx.utils.random_node(G, weight=None)

# Random edge selection
edge = nx.utils.random_edge(G, weight=None)
```

## Configuration Management

NetworkX uses a configuration system for backend priorities, drawing settings, and algorithm parameters.

```python
import networkx as nx

# Backend priority configuration
nx.config.backend_priority.algos = ["cugraph", "parallel"]
nx.config.backend_priority.generators = ["cugraph"]
nx.config.backend_priority.classes = ["cugraph"]

# Fallback behavior
nx.config.fallback_to_nx = True  # Fall back to pure NetworkX

# Caching
nx.config.cache_converted_graphs = True

# Drawing configuration
nx.config.drawing.element_limit = 10000  # Max elements for drawing
nx.config.drawing.np_float_weighted = True

# Check current configuration
print(nx.config.backend_priority.algos)
print(nx.config.fallback_to_nx)
```

## Decorator Utilities

NetworkX uses several decorator utilities for handling random state, file I/O, and graph type constraints.

```python
from networkx.utils import decorators as nx_dec

# @argmap: Map argument names to new names (for backward compatibility)
@nx_dec.argmap("old_name", "new_name")
def my_func(new_name):
    pass

# @nodes_or_number: Accept either a number n or a list of nodes
@nx_dec.nodes_or_number(nodes, default=0)
def process_nodes(node_indices):
    pass

# @not_implemented_for: Skip for certain graph types
@nx_dec.not_implemented_for("directed", "multigraph")
def undirected_only(G):
    pass

# @np_random_state: Handle NumPy random state arguments
@nx_dec.np_random_state("random_state")
def np_func(random_state=None):
    return random_state

# @py_random_state: Handle Python random state arguments
@nx_dec.py_random_state("seed")
def py_func(seed=None):
    return seed

# @open_file: Auto-open file path arguments as file objects
@nx_dec.open_file(1, mode='w')  # Open first positional arg as file
def write_to_file(path, data):
    path.write(data)
```

## Miscellaneous Utilities

```python
# Convert dict to numpy array
arr = nx.utils.dict_to_numpy_array({"a": 1, "b": 2})

# Create Python random state object
py_rng = nx.utils.create_py_random_state(42)

# Create NumPy random state object
np_rng = nx.utils.create_random_state(42)
```

## Summary

| Function | Description |
|----------|-------------|
| `random_permutation(n)` | Permutation of 0..n-1 |
| `arbitrary_element(seq)` | Random element from sequence |
| `random_sample(population, k)` | k elements without replacement |
| `powerlaw_sequence(n, exponent=2.5)` | Power-law distributed values |
| `reservoir(iterable, size, seed=None)` | Reservoir sampling for streams |
| `random_node(G, weight=None)` | Random node from graph |
| `random_edge(G, weight=None)` | Random edge from graph |
| `dict_to_numpy_array(d)` | Dict → numpy array |
| `create_py_random_state(seed)` | Python random.Random instance |
| `create_random_state(seed)` | NumPy RandomState instance |

## Configuration Reference

| Config Key | Type | Description |
|------------|------|-------------|
| `backend_priority.algos` | list | Algorithm backend priority |
| `backend_priority.generators` | list | Generator backend priority |
| `backend_priority.classes` | list | Class backend priority |
| `fallback_to_nx` | bool | Enable fallback to pure NetworkX |
| `cache_converted_graphs` | bool | Cache graph conversions |
| `drawing.element_limit` | int | Max elements for drawing |
| `drawing.np_float_weighted` | bool | Use numpy float for weighted drawing |
