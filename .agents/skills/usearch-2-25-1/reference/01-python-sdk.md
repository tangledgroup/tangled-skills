# Python SDK

## Index Construction

The `Index` class is the primary interface. Parameters control the HNSW graph structure and storage precision:

```python
from usearch.index import Index

index = Index(
    ndim=3,               # Number of dimensions in input vectors
    metric='cos',         # 'l2sq', 'ip', 'haversine', or other MetricKind
    dtype='bf16',         # Storage precision: 'f64', 'f32', 'bf16', 'f16',
                          # 'e5m2', 'e4m3', 'e3m2', 'e2m3', 'u8', 'i8', 'b1'
    connectivity=16,      # Neighbors per graph node (M in HNSW paper)
    expansion_add=128,    # Indexing quality (efConstruction)
    expansion_search=64,  # Search quality (ef)
    multi=False,          # Allow multiple vectors per key
    path=None,            # Optional file path for save/load
    view=False,           # Memory-map from disk instead of loading into RAM
    enable_key_lookups=True,  # Enable index[key] retrieval
)
```

Default `connectivity` is 16 (vs 32 in FAISS). Default `expansion_add` is 128 (vs 40 in FAISS). Default `expansion_search` is 64 (vs 16 in FAISS). When set to 0, auto-tuning selects values based on hardware.

## Adding Vectors

Single vector:
```python
import numpy as np
vector = np.array([0.2, 0.6, 0.4])
index.add(42, vector)
```

Batch vectors:
```python
n = 100
keys = np.arange(n)
vectors = np.random.uniform(0, 0.3, (n, index.ndim)).astype(np.float32)
index.add(keys, vectors, threads=0, copy=True)
```

The `threads=0` default uses all available cores. Set `copy=False` when you can guarantee the lifetime of the primary vector store during construction.

## Searching

Single query:
```python
from usearch.index import Matches
matches: Matches = index.search(vector, 10)
print(matches.keys, matches.distances)
```

Batch queries return `BatchMatches`:
```python
from usearch.index import BatchMatches
vectors_batch = np.random.rand(50, index.ndim).astype(np.float32)
batch: BatchMatches = index.search(vectors_batch, 10, threads=0)

# Access individual query results
first_query: Matches = batch[0]

# Check actual counts per query (sentinel values fill unused positions)
print(batch.counts)
```

Exact (brute-force) search bypasses the HNSW graph:
```python
matches = index.search(vector, 10, exact=True)
```

## Serialization

Save to file:
```python
index.save('index.usearch')
```

Load into memory:
```python
index.load('index.usearch')
```

Memory-map from disk (no RAM load, enables serving large indexes):
```python
index.view('index.usearch')
# or
view = Index.restore('index.usearch', view=True)
```

Read metadata without loading:
```python
meta = Index.metadata('index.usearch')
```

## Batch Operations

USearch Python bindings support batch add and search natively. The index structure is concurrent by design, so `add` is thread-safe for parallel construction. When using `BatchMatches`, unused positions contain sentinel values (signaling NaN for distances). Always check `batch.counts` for actual result counts.

```python
# Batch insert with progress callback
index.add(keys, vectors, threads=4, log=True, progress=lambda done, total: done / total)
```

## Tooling

Load/save standard k-ANN binary matrix files (.bbin, .fbin, .hbin):
```python
from usearch.io import load_matrix, save_matrix
vectors = load_matrix('deep1B.fbin')
index.add(keys, vectors)
```

Evaluate index quality:
```python
from usearch.eval import self_recall, relevance, dcg, ndcg

stats = self_recall(index, exact=False)
# stats.visited_members, stats.computed_distances

# Compare approximate vs exact results
matches_approx = index.search(vectors, 10)
matches_exact = index.search(vectors, 10, exact=True)
scores = relevance(matches_exact, matches_approx)
print(dcg(scores), ndcg(scores))
```

## Index Properties

Access configuration and statistics:

```python
index.ndim              # Number of dimensions
index.metric            # MetricKind or CompiledMetric
index.dtype             # ScalarKind storage type
index.connectivity      # Neighbors per node
index.expansion_add     # Construction expansion factor
index.expansion_search  # Search expansion factor
index.size              # Number of vectors indexed
index.capacity          # Max vectors without reallocation
index.memory_usage      # Bytes consumed
index.serialized_length # Bytes for serialization
index.nlevels           # Number of HNSW graph levels
index.max_level         # Maximum level in graph
index.hardware_acceleration  # ISA name (e.g., "sapphire", "ice") or "auto"
index.jit               # True if metric was JIT-compiled
index.multi             # Multi-value per key enabled
```

Level statistics:
```python
stats = index.level_stats(0)  # nodes, edges, max_edges, allocated_bytes
all_levels = index.levels_stats  # List of stats for each level
```

## Other Operations

Remove vectors:
```python
index.remove([42, 43], compact=False, threads=0)
```

Rename keys (useful in iterative clustering):
```python
index.rename(from_=[42, 43], to=[100, 101])
```

Retrieve stored vectors:
```python
vector = index.get(42)  # Returns ndarray or None
vectors = index.get([42, 43])  # Returns tuple of ndarrays
```

Compute pairwise distances between indexed keys:
```python
dist = index.pairwise_distance(42, 43)  # Single float
matrix = index.pairwise_distance([1,2,3], [4,5,6])  # ndarray
```

Check key membership:
```python
index.contains(42)  # bool
index.count(42)     # int (number of vectors under key)
```

Clear and reset:
```python
index.clear()   # Erase vectors, keep allocated space
index.reset()   # Full reset, return memory to OS
index.copy()    # Deep copy the index
```
