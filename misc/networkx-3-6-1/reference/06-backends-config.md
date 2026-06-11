# Backends and Configuration

## Backend Dispatch System

NetworkX 3.x supports dispatching function calls to optional third-party backends. Backends provide improved performance or additional functionality without changing user code.

### Enabling Backends

Three methods to enable backends:

```python
# Method 1: Per-call keyword argument
result = nx.shortest_path(G, source, target, backend="nx-parallel")

# Method 2: Environment variable
# NETWORKX_BACKEND_PRIORITY=nx-parallel
import os
os.environ["NETWORKX_BACKEND_PRIORITY"] = "nx-parallel"

# Method 3: Config setting
import networkx as nx
nx.config.backend_priority = "nx-parallel"
```

### Known Backends

- **nx-parallel** — Parallelized implementations using joblib
- **nx-cugraph** — GPU acceleration using RAPIDS cuGraph and NVIDIA GPUs
- **nx-arangodb** — ArangoDB persistence layer for NetworkX graphs
- **nx-neptune** — Offload computation to AWS Neptune Analytics

Backends need not be listed in documentation to work. Any backend implementing the NetworkX backend interface can be installed and used.

## Configuration

NetworkX 3.x introduces a global configuration system:

```python
import networkx as nx

# View current config
print(nx.config)

# Set backend priority
nx.config.backend_priority = "nx-parallel"

# Reset to default
nx.config.backend_priority = None
```

The `NetworkXConfig` class provides typed configuration access. Configuration is stored in `nx.config` (a `Config` instance).

## Randomness Control

NetworkX uses a global random state controllable via the `nx.random_state` module:

```python
import networkx as nx

# Set seed for reproducibility
nx.seed(42)

# Or use numpy random state
import numpy as np
rng = np.random.default_rng(42)
nx.set_random_state(rng)
```

## Utility Functions

### Helper Functions

```python
nx.utils.make_list_of_ints([1, "2", 3])
nx.utils.arbitrary_eq(x, y)
nx.utils.is_string_like(s)
nx.utils.flatten(iterable)
```

### Union-Find Data Structure

```python
uf = nx.union_find.UnionFind()
uf.union(1, 2)
uf.union(2, 3)
uf.find(1) == uf.find(3)  # True
```

### Cuthill-McKee Ordering

Bandwidth reduction ordering for sparse matrices:

```python
ordering = nx.utils.rcm.reverse_cuthill_mckee_ordering(G)
```

## Performance Tips

- Use graph views (`subgraph_view`, `reverse_view`) instead of copying when possible
- For large graphs, consider backend dispatch (nx-parallel for CPU parallelism, nx-cugraph for GPU)
- Use SciPy sparse arrays via `nx.to_scipy_sparse_array()` for memory-efficient matrix operations
- For algorithms that accept `weight` parameter, ensure the weight attribute is numeric
- Prefer `G.subgraph(nodes)` over creating a new graph and copying nodes/edges
- Use `nx.freeze(G)` on static graphs to prevent accidental modification
