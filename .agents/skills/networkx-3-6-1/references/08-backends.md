# Backends and Performance

NetworkX supports third-party backends for accelerated computation through its plugin-dispatch architecture. Backends can provide GPU acceleration, parallel processing, or specialized algorithms.

## Backend Architecture

NetworkX uses the `@nx._dispatchable` decorator to enable function dispatching to backends:

```python
import networkx as nx

# Check if a function is dispatchable
func = nx.betweenness_centrality
print(hasattr(func, '__wrapped__'))  # True if dispatchable

# List available backends
nx.backends.list_backends()

# Get backend info
backend_info = nx.get_backend("cugraph")
```

## Using Backends

### Explicit Backend Usage

Specify backend for individual function calls:

```python
import networkx as nx

G = nx.erdos_renyi_graph(1000, 0.01)

# Use specific backend for one function
result = nx.betweenness_centrality(G, backend="cugraph")

# With backend-specific parameters
result = nx.betweenness_centrality(G, backend="parallel", num_workers=4)

# Create backend graph directly (if backend provides graph class)
import nx_cugraph as cugraph
G_cugraph = cugraph.CuGraph(G)  # Convert to GPU graph
result = nx.betweenness_centrality(G_cugraph)  # Automatically uses cugraph
```

### Automatic Backend Dispatch

Configure backends globally via environment variables or configuration:

```python
import networkx as nx

# Method 1: Environment variables (set before importing networkx)
# NETWORKX_BACKEND_PRIORITY=cugraph,parallel,networkx
# NETWORKX_FALLBACK_TO_NX=True

# Method 2: Python configuration
nx.config.backend_priority.algos = ["cugraph", "parallel"]
nx.config.backend_priority.generators = ["cugraph"]
nx.config.backend_priority.classes = ["cugraph"]
nx.config.fallback_to_nx = True  # Fall back to NetworkX if backend doesn't implement
nx.config.cache_converted_graphs = True  # Cache converted graphs

# Now all dispatchable functions will try backends in order
result = nx.betweenness_centrality(G)  # Uses cugraph if available
```

### Configuration Options

| Config | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `backend_priority.algos` | `NETWORKX_BACKEND_PRIORITY_ALGOS` | `[]` | Backend list for algorithm functions |
| `backend_priority.generators` | `NETWORKX_BACKEND_PRIORITY_GENERATORS` | `[]` | Backend list for graph generators |
| `backend_priority.classes` | `NETWORKX_BACKEND_PRIORITY_CLASSES` | `[]` | Backend list for graph classes |
| `fallback_to_nx` | `NETWORKX_FALLBACK_TO_NX` | `False` | Fall back to NetworkX if backend fails |
| `cache_converted_graphs` | `NETWORKX_CACHE_CONVERTED_GRAPHS` | `True` | Cache converted graphs in `G.__networkx_cache__` |

## Available Backends

### cuGraph (GPU Acceleration)

RAPIDS cuGraph for GPU-accelerated graph analytics.

```bash
# Install via conda (requires NVIDIA GPU)
conda install -c rapidsai -c nvidia cugraph python-rapids=23.10
```

```python
import networkx as nx
import rmm  # RAPIDS Memory Manager

# Set GPU memory limit if needed
rmm.reinitialize(limit="4GB")

G = nx.erdos_renyi_graph(5000, 0.001)

# Use cuGraph for PageRank (much faster on GPU for large graphs)
pr_gpu = nx.pagerank(G, backend="cugraph")

# Shortest paths on GPU
distances = nx.single_source_shortest_path_length(G, source=0, backend="cugraph")

# Connected components
components = nx.connected_components(G, backend="cugraph")
```

**Supported algorithms**: PageRank, connected components, shortest paths, BFS/DFS, triangle count

### Parallel Backend (Multi-Core CPU)

Parallel execution using multiprocessing.

```bash
pip install nx-parallel
```

```python
import networkx as nx

G = nx.barabasi_albert_graph(1000, 3)

# Parallel betweenness centrality (approximation)
bc = nx.betweenness_centrality(G, k=50, backend="parallel", num_workers=4)

# Parallel closeness centrality
cc = nx.closeness_centrality(G, backend="parallel", get_chunks=8)
```

**Supported algorithms**: Betweenness centrality, closeness centrality, some shortest paths

### GraphBLAS Backends

Linear algebra-based graph algorithms using GraphBLAS.

```bash
pip install pygraphblas  # Or sparse, exographblas
```

```python
import networkx as nx

G = nx.erdos_renyi_graph(10000, 0.001)

# Use GraphBLAS backend
bc = nx.betweenness_centrality(G, backend="graphblas")

# PageRank with GraphBLAS
pr = nx.pagerank(G, backend="graphblas", max_iter=100)
```

**Supported algorithms**: PageRank, connected components, transitive closure, matrix operations

### Rustworkx (Rust Backend)

High-performance Rust implementation.

```bash
pip install rustworkx
```

```python
import networkx as nx
import rustworkx as rx

# Convert NetworkX to rustworkx
rx_graph = nx.to_rustworkx(G)

# Or use via backend dispatch (if available)
result = nx.dijkstra_path_length(G, source, target, backend="rustworkx")
```

## Performance Comparison

```python
import networkx as nx
import time

G = nx.barabasi_albert_graph(5000, 3)

# Baseline: Pure NetworkX
start = time.time()
pr_nx = nx.pagerank(G)
time_nx = time.time() - start
print(f"NetworkX: {time_nx:.3f}s")

# With cuGraph backend (if available)
try:
    start = time.time()
    pr_gpu = nx.pagerank(G, backend="cugraph")
    time_gpu = time.time() - start
    print(f"cuGraph: {time_gpu:.3f}s")
    print(f"Speedup: {time_nx / time_gpu:.2f}x")
except Exception as e:
    print(f"cuGraph not available: {e}")

# With parallel backend
try:
    start = time.time()
    bc_parallel = nx.betweenness_centrality(G, k=100, backend="parallel", num_workers=4)
    time_parallel = time.time() - start
    print(f"Parallel: {time_parallel:.3f}s")
except Exception as e:
    print(f"Parallel not available: {e}")
```

## Backend-Specific Features

### cuGraph Features

```python
import rmm

# Manage GPU memory
rmm.reinitialize(pool_allocator=True, initial_pool_size="8GB")

# Check GPU utilization
from rmm._cuda import gpu
print(f"GPU: {gpu.get_device_name()}")

# cuGraph-specific parameters
pr = nx.pagerank(
    G, 
    backend="cugraph",
    max_iter=100,           # Max iterations
    tol=1e-6,               # Convergence tolerance
    alpha=0.85,             # Damping factor
    personalization=None    # Personalization vector
)

# BFS with GPU
bfs_tree = nx.bfs_tree(G, source=0, backend="cugraph")
```

### Parallel Backend Features

```python
# Control parallelism
bc = nx.betweenness_centrality(
    G,
    k=100,
    backend="parallel",
    num_workers=4,          # Number of CPU cores
    chunk_size=100,         # Batch size for parallel processing
    get_chunks=None         # Auto-detect optimal chunks
)

# Monitor progress (some backends support callbacks)
def progress_callback(fraction_done):
    print(f"Progress: {fraction_done*100:.1f}%")

bc = nx.betweenness_centrality(
    G, 
    k=100, 
    backend="parallel",
    num_workers=4,
    callback=progress_callback
)
```

## Debugging Backend Issues

```python
import networkx as nx

# Check available backends
print("Available backends:", nx.backends.list_backends())

# Check if function is dispatchable
func = nx.pagerank
print("Is dispatchable:", hasattr(func, '__wrapped__'))

# Check which backend will be used
G = nx.Graph()
G.add_edge(1, 2)

try:
    result = nx.pagerank(G, backend="cugraph")
    print("Backend succeeded")
except nx.NetworkXBackendError as e:
    print(f"Backend error: {e}")
except ImportError as e:
    print(f"Backend not installed: {e}")

# Force fallback to NetworkX
result = nx.pagerank(G, backend="networkx")  # Always use pure NetworkX

# Check cached conversions
if hasattr(G, '__networkx_cache__'):
    print("Cached backends:", list(G.__networkx_cache__.keys()))
```

## Memory Management

### Clearing Cached Conversions

```python
# Clear backend cache for a graph
if hasattr(G, '__networkx_cache__'):
    G.__networkx_cache__.clear()

# Disable caching globally
nx.config.cache_converted_graphs = False

# Manual memory management (for GPU backends)
import gc
gc.collect()

# For cuGraph, clear GPU memory
try:
    import rmm
    rmm.reinitialize()
except ImportError:
    pass
```

### Large Graph Handling

```python
# Process large graphs in chunks
def process_large_graph(G, chunk_size=1000):
    """Process graph in chunks to manage memory."""
    nodes = list(G.nodes())
    
    for i in range(0, len(nodes), chunk_size):
        chunk_nodes = nodes[i:i + chunk_size]
        subgraph = G.subgraph(chunk_nodes)
        
        # Process subgraph with backend
        result = nx.pagerank(subgraph, backend="cugraph")
        
        yield result
        
        # Clear memory
        del subgraph
        gc.collect()

# Usage
for chunk_result in process_large_graph(G, chunk_size=1000):
    process(chunk_result)
```

## Creating Custom Backends

Basic structure for implementing a NetworkX backend:

```python
# my_backend/__init__.py
import networkx as nx

def can_run(func, *args, **kwargs):
    """Check if backend can run this function."""
    supported_funcs = [
        'pagerank',
        'betweenness_centrality',
        'connected_components'
    ]
    return func.__name__ in supported_funcs

def should_run(func, *args, **kwargs):
    """Decide if backend should run (considering graph size, etc.)."""
    # Skip small graphs (overhead not worth it)
    for arg in args:
        if isinstance(arg, nx.Graph) and arg.number_of_nodes() < 100:
            return False
    return True

def pagerank(G, *args, **kwargs):
    """Backend implementation of PageRank."""
    # Convert NetworkX graph to backend format
    G_backend = convert_to_backend(G)
    
    # Run algorithm
    result = backend_pagerank(G_backend, *args, **kwargs)
    
    # Convert back to NetworkX format
    return convert_to_networkx(result)

# Register as entry point in setup.py or pyproject.toml
```

**Entry point registration** (in `pyproject.toml`):
```toml
[project.entry-points."networkx.backends"]
my_backend = "my_backend"

[project.entry-points."networkx.backend_info"]
my_backend = "my_backend:get_backend_info"
```

## Best Practices

1. **Test with small graphs first** to verify correctness before scaling
2. **Use caching** for repeated operations on same graph
3. **Monitor memory usage** especially with GPU backends
4. **Handle fallback gracefully** when backends are unavailable
5. **Profile performance** to ensure backend provides actual speedup
6. **Consider data transfer overhead** (CPU↔GPU, process↔process)
7. **Use appropriate backend for algorithm**:
   - GPU backends: Dense graphs, iterative algorithms (PageRank)
   - Parallel backends: Embarrassingly parallel tasks (centrality)
   - GraphBLAS: Matrix-based operations

## Troubleshooting

```python
# Backend not found?
# Check installation
import sys
sys.path  # Verify package is in path

# Try importing backend directly
try:
    import nx_cugraph
    print("cuGraph installed")
except ImportError:
    print("Install cuGraph: conda install -c rapidsai cugraph")

# Backend fails on large graphs?
# Check memory limits
import psutil
print(f"Available RAM: {psutil.virtual_memory().available / 1e9:.2f}GB")

# For GPU, check VRAM
try:
    import pynvml
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU Free Memory: {info.free / 1e9:.2f}GB")
except:
    print("NVIDIA management library not available")

# Backend gives different results?
# Some backends use approximations or different numerical precision
# Check tolerance parameters and algorithm variants
```

## Performance Tips

1. **Batch operations** when possible to amortize overhead
2. **Reuse converted graphs** via caching
3. **Choose right backend**:
   - < 1000 nodes: Pure NetworkX often fastest (no overhead)
   - 1000-10000 nodes: Parallel backend for CPU multi-core
   - > 10000 nodes: GPU backend if available
4. **Tune parameters** (workers, chunks, iterations) for your hardware
5. **Profile regularly** as backends and algorithms evolve
