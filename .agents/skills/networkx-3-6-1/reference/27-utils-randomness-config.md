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

NetworkX uses several decorator utilities for handling random state, file I/O, and graph type constraints. These are used internally by many algorithm functions.

```python
from networkx.utils.decorators import *

# @argmap: Map old argument names to new ones (backward compatibility)
@argmap("old_name", "new_name")
def my_func(new_name):
    pass

# @nodes_or_number: Accept either a number n or a list of nodes
#   If node is int, generates range(node); otherwise uses as-is
@nodes_or_number(nodes, default=0)
def process_nodes(node_indices):
    pass

# @not_implemented_for: Raise NetworkXNotImplemented for certain graph types
@not_implemented_for("directed", "multigraph")
def undirected_only(G):
    pass

# @np_random_state: Convert numpy random state to numpy Generator/RandomState
@np_random_state("random_state")
def np_func(random_state=None):
    return random_state

# @py_random_state: Convert Python seed to random.Random instance
@py_random_state("seed")
def py_func(seed=None):
    return seed

# @creation: Mark function as a graph creator (for backend dispatch)
@creation
def create_graph():
    pass

# @open_file: Auto-open file path arguments as file objects
#   Position 1 = first positional arg, mode='w' for writing
@open_file(1, mode='w')
def write_to_file(path, data):
    path.write(data)
```

## Miscellaneous Utilities

### Core Utility Functions

```python
from networkx.utils import *

# Arbitrary element from sequence (weighted or uniform)
elem = arbitrary_element([1, 2, 3, 4, 5])
print(elem)  # Random choice

# Flatten nested iterables into single list
flat = flatten([[1, 2], [3, [4, 5]], 6])
print(flat)  # [1, 2, 3, 4, 5, 6]

# Make list of integers from various inputs
ints = make_list_of_ints([1, 2, 3])      # [1, 2, 3]
ints2 = make_list_of_ints(range(5))     # [0, 1, 2, 3, 4]

# Convert dict to numpy array (keys → rows/cols)
arr = dict_to_numpy_array({"a": 1, "b": 2})

# Pairwise iterator: yields consecutive pairs from iterable
pairs = list(pairwise([1, 2, 3, 4]))
print(pairs)  # [(1, 2), (2, 3), (3, 4)]

# Group items by key function
groups = groups(["apple", "pie", "apricot", "banana"], key=len)
print(groups)  # {3: ['pie'], 5: ['apple', 'apricot', 'banana']}

# Create Python random state object
py_rng = create_py_random_state(42)
print(type(py_rng))  # <class 'random.Random'>

# Create NumPy random state object
np_rng = create_random_state(42)
print(type(np_rng))  # <class 'numpy.random._generator.Generator'> or RandomState
```

### UnionFind — Disjoint Set Data Structure

UnionFind (also called disjoint-set or merge-find set) tracks partitioning of elements into non-overlapping sets. Supports fast union and find operations with path compression and union-by-rank.

```python
from networkx.utils.union_find import UnionFind

# Create empty UnionFind
uf = UnionFind()

# Add elements (done automatically on first use)
uf.union(1, 2)    # Merge sets containing 1 and 2
uf.union(2, 3)    # Merge sets containing 2 and 3 (now 1,2,3 in same set)

# Find representative of element
root_1 = uf.find(1)
root_2 = uf.find(2)
print(root_1 == root_2)  # True — 1 and 2 are in the same set

# Check if two elements are in the same set
same = uf.same_set(1, 3)  # True

# Iterate over equivalence classes (partitions)
for group in uf:
    print(list(group))  # Each group is a set of equivalent elements

# Create from initial sets
uf2 = UnionFind([[1, 2, 3], [4, 5]])  # Pre-partitioned
print(list(uf2))  # [{1, 2, 3}, {4, 5}]

# Size of set containing element
size = uf.size(1)  # Number of elements in same set as 1

# Number of disjoint sets
n_sets = len(uf)

# Common use case: find connected components without full traversal
uf = UnionFind()
for u, v in edges:
    uf.union(u, v)
components = [list(group) for group in uf]
```

**Use cases**: Connected components, Kruskal's MST, cycle detection, equivalence class tracking.

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

### Random Number Generation
| Function | Description |
|----------|-------------|
| `random_permutation(n)` | Permutation of 0..n-1 |
| `arbitrary_element(seq)` | Random element from sequence |
| `random_sample(population, k)` | k elements without replacement |
| `powerlaw_sequence(n, exponent=2.5)` | Power-law distributed values |
| `reservoir(iterable, size, seed=None)` | Reservoir sampling for streams |
| `random_node(G, weight=None)` | Random node from graph |
| `random_edge(G, weight=None)` | Random edge from graph |

### Decorators
| Decorator | Description |
|-----------|-------------|
| `@argmap(old, new)` | Map old argument name to new |
| `@nodes_or_number(nodes)` | Accept int n or list of nodes |
| `@not_implemented_for(types)` | Skip for certain graph types |
| `@np_random_state(attr)` | Handle NumPy random state |
| `@py_random_state(attr)` | Handle Python random state |
| `@creation` | Mark as graph creator (backend dispatch) |
| `@open_file(pos, mode)` | Auto-open file path arg |

### Miscellaneous Utilities
| Function | Description |
|----------|-------------|
| `flatten(iterable)` | Flatten nested iterables |
| `make_list_of_ints(obj)` | Convert to list of ints |
| `dict_to_numpy_array(d)` | Dict → numpy array |
| `pairwise(iterable)` | Consecutive pairs |
| `groups(iterable, key)` | Group by key function |
| `create_py_random_state(seed)` | Python random.Random instance |
| `create_random_state(seed)` | NumPy RandomState/Generator |

### UnionFind (Disjoint Set)
| Method | Description |
|--------|-------------|
| `uf.union(a, b)` | Merge sets containing a and b |
| `uf.find(a)` | Representative of a's set |
| `uf.same_set(a, b)` | True if a, b in same set |
| `uf.size(a)` | Size of a's set |
| `len(uf)` | Number of disjoint sets |

### Configuration Reference
| Config Key | Type | Description |
|------------|------|-------------|
| `backend_priority.algos` | list | Algorithm backend priority |
| `backend_priority.generators` | list | Generator backend priority |
| `backend_priority.classes` | list | Class backend priority |
| `fallback_to_nx` | bool | Enable fallback to pure NetworkX |
| `cache_converted_graphs` | bool | Cache graph conversions |
| `drawing.element_limit` | int | Max elements for drawing |
| `drawing.np_float_weighted` | bool | Use numpy float for weighted drawing |

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
