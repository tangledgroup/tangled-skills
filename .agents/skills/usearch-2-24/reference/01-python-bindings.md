# Python Bindings

## Installation

```sh
pip install usearch
```

Python bindings are implemented with `pybind/pybind11`. Assuming the presence of GIL, threads are spawned in the C++ layer on large insertions.

## Quickstart

```python
import numpy as np
from usearch.index import Index, Matches

index = Index(
    ndim=3,               # Number of dimensions in input vectors
    metric='cos',         # Choose 'l2sq', 'ip', 'haversine' or other, default = 'cos'
    dtype='bf16',         # Quantize to 'f16', 'e5m2', 'e4m3', etc. default = None
    connectivity=16,      # How frequent connections in the graph are, optional
    expansion_add=128,    # Control the recall of indexing, optional
    expansion_search=64,  # Control the quality of search, optional
)

vector = np.array([0.2, 0.6, 0.4])
index.add(42, vector)
matches: Matches = index.search(vector, 10)

assert len(index) == 1
assert matches[0].key == 42
assert matches[0].distance <= 0.001
assert np.allclose(index[42], vector)
```

## Serialization

```python
index.save('index.usearch')
index.load('index.usearch')   # Copy the whole index into memory
index.view('index.usearch')   # View from disk without loading in memory
```

Restore an index when you only know its path:

```python
Index.metadata('index.usearch')        # -> IndexMetadata
Index.restore('index.usearch', view=False)  # -> Index
```

## Batch Operations

Adding or querying a batch is identical to single-vector operations — the difference is in tensor shape:

```python
n = 100
keys = np.arange(n)
vectors = np.random.uniform(0, 0.3, (n, index.ndim)).astype(np.float32)

index.add(keys, vectors, threads=..., copy=...)
matches: BatchMatches = index.search(vectors, 10, threads=...)

first_query_matches: Matches = matches[0]
assert matches[0].key == 0
assert len(matches) == vectors.shape[0]
```

- `threads=0` (default) uses all available cores
- `copy=False` avoids persisting the vector inside the index if you manage its lifetime elsewhere

> When using `BatchMatches`, unused positions are filled with sentinel values (signaling NaN for distances). Check `matches.counts` for valid results.

## Scalar Quantization & NumKong Interop

USearch supports automatic casting between input type and storage type:

```python
# Option 1: let USearch quantize internally
index = Index(ndim=256, metric='cos', dtype='e4m3')
vectors_f32 = np.random.rand(1000, 256).astype(np.float32)
index.add(np.arange(1000), vectors_f32)

# Option 2: pre-quantize with NumKong and pass raw buffers
import numkong as nk
vectors_e4m3 = np.asarray(nk.Tensor(vectors_f32).astype('e4m3'))
index2 = Index(ndim=256, metric='cos', dtype='e4m3')
index2.add(np.arange(1000), vectors_e4m3, dtype='e4m3')
```

Supported `dtype` values: `f64`, `f32`, `bf16`, `f16`, `e5m2`, `e4m3`, `e3m2`, `e2m3`, `u8`, `i8`, `b1`.

## User-Defined Metrics with Numba

JIT-compile a custom metric function and pass it to the index:

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric

ndim = 256
signature = types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32))

@cfunc(signature)
def inner_product(a, b):
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    c = 0.0
    for i in range(ndim):
        c += a_array[i] * b_array[i]
    return 1 - c

index = Index(ndim=ndim, metric=CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
))
```

With explicit dimension parameter:

```python
signature = types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32),
    types.uint64)

@cfunc(signature)
def inner_product(a, b, ndim):
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    c = 0.0
    for i in range(ndim):
        c += a_array[i] * b_array[i]
    return 1 - c

index = Index(ndim=ndim, metric=CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
))
```

## Exact Search

For smaller datasets, bypass indexing and perform brute-force SIMD-optimized search:

```python
from usearch.index import search, MetricKind, Matches, BatchMatches
import numpy as np

vectors = np.random.rand(10_000, 1024).astype(np.float32)
vector = np.random.rand(1024).astype(np.float32)

one_in_many: Matches = search(vectors, vector, 50, MetricKind.L2sq, exact=True)
many_in_many: BatchMatches = search(vectors, vectors, 50, MetricKind.L2sq, exact=True)
```

USearch's exact search can be up to 20x faster than FAISS `IndexFlatL2` (2.54 ms vs 55.3 ms on Google Colab).

## Evaluation Tools

```python
from usearch.eval import self_recall, relevance, dcg, ndcg, random_vectors

# Self-recall test
stats = self_recall(index, exact=True)
assert stats.visited_members == 0
assert stats.computed_distances == len(index)

stats = self_recall(index, exact=False)
assert stats.visited_members > 0

# Relevance evaluation
vectors = random_vectors(index=index)
matches_approximate = index.search(vectors)
matches_exact = index.search(vectors, exact=True)
relevance_scores = relevance(matches_exact, matches_approximate)
print(dcg(relevance_scores), ndcg(relevance_scores))
```

## I/O Tools

Load and save standard k-ANN binary matrix files (`.fbin`, `.ibin`, `.hbin`):

```python
from usearch.io import load_matrix, save_matrix

vectors = load_matrix('deep1B.fbin')
index = Index(ndim=vectors.shape[1])
index.add(keys, vectors)
```

## Multi-Index Lookups

For billions or trillions of vectors, build multiple smaller indexes and view them together:

```python
from usearch.index import Indexes

multi_index = Indexes(
    indexes=[...],       # Iterable[Index]
    paths=[...],         # Iterable[PathLike]
    view=False,          # Memory-map from disk
    threads=0,           # Auto-detect
)
multi_index.search(...)
```

## Clustering

```python
clustering = index.cluster(min_count=10, max_count=15, threads=...)

centroid_keys, sizes = clustering.centroids_popularity
clustering.plot_centroids_popularity()  # Matplotlib histogram
g = clustering.network                  # NetworkX graph
first_members = clustering.members_of(centroid_keys[0])
sub_clustering = clustering.subcluster(min_count=..., max_count=...)
```

## Joins

Sub-quadratic approximate fuzzy and semantic joins:

```python
men = Index(...)
women = Index(...)
pairs: dict = men.join(women, max_proposals=0, exact=False)
```
