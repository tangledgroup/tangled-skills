# USearch API Reference

Complete API documentation for USearch 2.24, including all classes, methods, constants, and utility functions.

## Index Class

The primary class for creating and managing vector search indexes.

### Constructor

```python
from usearch.index import Index

index = Index(
    ndim: int,
    metric: MetricLike = 'ip',
    dtype: DTypeLike = None,
    connectivity: int = 16,
    expansion_add: int = 128,
    expansion_search: int = 64,
    multi: bool = False
)
```

**Parameters:**
- `ndim` (int, required): Number of dimensions in vectors
- `metric` (str | MetricKind | CompiledMetric, default='ip'): Distance metric
- `dtype` (str | ScalarKind | None, default=None): Storage data type
- `connectivity` (int, default=16): Graph connectivity M parameter
- `expansion_add` (int, default=128): EF construction parameter
- `expansion_search` (int, default=64): EF search parameter
- `multi` (bool, default=False): Allow multiple vectors per key

**Returns:** Index instance

**Example:**
```python
index = Index(ndim=768, metric='cos', dtype='bf16')
```

### Properties

#### `ndim` → int
Number of dimensions in the index.

```python
index = Index(ndim=256)
print(index.ndim)  # 256
```

#### `metric_kind` → MetricKind
The distance metric used by the index.

```python
index = Index(ndim=256, metric='cos')
print(index.metric_kind)  # MetricKind.Cos
```

#### `dtype` → ScalarKind
The data type used for storage.

```python
index = Index(ndim=256, dtype='f16')
print(index.dtype)  # ScalarKind.F16
```

#### `connectivity` → int
Graph connectivity parameter.

```python
print(index.connectivity)  # 16
```

#### `hardware_acceleration` → str
Detected hardware acceleration level.

```python
print(index.hardware_acceleration)  # 'sapphire', 'ice', 'neoverse', or 'none'
```

### Methods

#### `add(keys, vectors, *, copy=True, threads=0, log=False, progress=None)`

Add vectors to the index.

**Parameters:**
- `keys` (KeyOrKeysLike): Single key or iterable of keys
- `vectors` (VectorOrVectorsLike): NumPy array of shape (n_vectors, ndim) or (ndim,)
- `copy` (bool, default=True): Whether to copy vector data
- `threads` (int, default=0): Number of threads (0 = auto)
- `log` (bool | str, default=False): Show progress bar
- `progress` (callable, optional): Progress callback(processed, total) → bool

**Returns:** Keys array (generated if not provided)

**Examples:**
```python
# Single vector
index.add(42, np.array([0.1, 0.2, 0.3]))

# Batch with explicit keys
keys = [1, 2, 3]
vectors = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
index.add(keys, vectors)

# Batch with auto-generated keys
vectors = np.random.rand(1000, 256).astype(np.float32)
keys = index.add(vectors)  # Keys generated from current size

# With progress tracking
def on_progress(processed, total):
    print(f"Progress: {processed}/{total}")
    return True  # Return False to cancel
    
index.add(keys, vectors, progress=on_progress, log=True)

# Parallel insertion
index.add(keys, vectors, threads=8)
```

#### `search(vectors, count=10, *, exact=False, threads=0, expansion=None, log=False, progress=None)`

Search for nearest neighbors.

**Parameters:**
- `vectors` (VectorOrVectorsLike): Query vector(s)
- `count` (int, default=10): Number of results to return
- `exact` (bool, default=False): Use exact brute-force search
- `threads` (int, default=0): Number of threads for batch search
- `expansion` (int, optional): Override expansion_search parameter
- `log` (bool | str, default=False): Show progress bar
- `progress` (callable, optional): Progress callback

**Returns:** Matches or BatchMatches

**Examples:**
```python
# Single query
query = np.array([0.1, 0.2, 0.3])
matches = index.search(query, 10)

for match in matches:
    print(f"Key: {match.key}, Distance: {match.distance}")

# Batch query
queries = np.random.rand(100, 256).astype(np.float32)
batch_matches = index.search(queries, 10, threads=4)

print(f"Results for {len(batch_matches)} queries")
first_query_results = batch_matches[0]  # Matches for first query

# Exact search (brute-force)
exact_matches = index.search(query, 10, exact=True)

# With custom expansion
matches = index.search(query, 10, expansion=128)

# Access result arrays directly
print(batch_matches.keys)      # Array of all keys
print(batch_matches.distances) # Array of all distances
print(batch_matches.counts)    # Actual matches per query
```

#### `remove(keys)`

Remove vectors by key.

**Parameters:**
- `keys` (KeyOrKeysLike): Key(s) to remove

**Returns:** None

**Example:**
```python
index.remove(42)  # Remove single key
index.remove([1, 2, 3])  # Remove multiple keys
```

#### `__getitem__(key)` → np.ndarray

Get vector by key.

**Parameters:**
- `key` (int): Vector key

**Returns:** NumPy array of the stored vector

**Example:**
```python
vector = index[42]
print(f"Vector shape: {vector.shape}")
```

#### `save(path_or_buffer, *, stream=None)`

Serialize index to file or buffer.

**Parameters:**
- `path_or_buffer` (str | os.PathLike | bytes): File path or buffer
- `stream` (callable, optional): Stream callback for incremental serialization

**Returns:** None

**Examples:**
```python
# Save to file
index.save('index.usearch')

# Save to bytes buffer
buffer = bytearray()
index.save(buffer)

# Save with custom stream
def write_chunk(chunk):
    # Custom handling of data chunks
    pass

index.save(stream=write_chunk)
```

#### `load(path_or_buffer, *, stream=None)`

Deserialize index from file or buffer (copies into memory).

**Parameters:**
- `path_or_buffer` (str | os.PathLike | bytes): File path or buffer
- `stream` (callable, optional): Stream callback for incremental deserialization

**Returns:** None

**Example:**
```python
index.load('index.usearch')
```

#### `view(path_or_buffer, *, stream=None)`

Memory-map index from disk without loading into RAM.

**Parameters:**
- `path_or_buffer` (str | os.PathLike | bytes): File path or buffer
- `stream` (callable, optional): Stream callback

**Returns:** None

**Example:**
```python
index.view('large_index.usearch')  # Memory-mapped, no RAM copy
```

#### `cluster(*, min_count=10, max_count=100, threads=0)`

Perform clustering on indexed vectors.

**Parameters:**
- `min_count` (int, default=10): Minimum members per cluster
- `max_count` (int, default=100): Maximum number of clusters
- `threads` (int, default=0): Number of threads

**Returns:** Clustering object

**Example:**
```python
clustering = index.cluster(min_count=10, max_count=50)

centroid_keys, sizes = clustering.centroids_popularity
members = clustering.members_of(centroid_keys[0])
sub_clustering = clustering.subcluster(centroid_keys[0], min_count=5, max_count=20)
```

#### `join(other_index, *, max_proposals=0, exact=False)`

Perform fuzzy join with another index.

**Parameters:**
- `other_index` (Index): Index to join with
- `max_proposals` (int, default=0): Max matches per key (0 = one-to-one)
- `exact` (bool, default=False): Use exact matching

**Returns:** dict mapping keys from self to keys from other_index

**Example:**
```python
pairs = index1.join(index2, max_proposals=5, exact=False)
# Result: {key_from_index1: [key_from_index2, ...]}
```

### Static Methods

#### `restore(path_or_buffer, *, view=False, **kwargs)` → Index

Restore index from file with automatic configuration detection.

**Parameters:**
- `path_or_buffer` (str | os.PathLike | bytes): File path or buffer
- `view` (bool, default=False): Memory-map instead of loading
- `**kwargs`: Additional Index constructor parameters

**Returns:** Index instance

**Example:**
```python
index = Index.restore('index.usearch')
index_view = Index.restore('index.usearch', view=True)
```

#### `metadata(path_or_buffer)` → IndexMetadata

Get index metadata without loading the full index.

**Parameters:**
- `path_or_buffer` (str | os.PathLike | bytes): File path or buffer

**Returns:** IndexMetadata object with:
- `count`: Number of vectors
- `ndim`: Vector dimensions
- `metric_kind`: Distance metric
- `scalar_kind`: Data type
- `connectivity`: Graph connectivity

**Example:**
```python
meta = Index.metadata('index.usearch')
print(f"Vectors: {meta.count}, Dimensions: {meta.ndim}")
print(f"Metric: {meta.metric_kind}, Type: {meta.scalar_kind}")
```

## Indexes Class (Multi-Index)

Manages multiple indexes for parallel search.

### Constructor

```python
from usearch.index import Indexes

multi_index = Indexes(
    indexes: Iterable[Index] = None,
    paths: Iterable[os.PathLike] = None,
    view: bool = False,
    threads: int = 0
)
```

**Parameters:**
- `indexes` (Iterable[Index], optional): List of Index instances
- `paths` (Iterable[str], optional): List of file paths to load
- `view` (bool, default=False): Memory-map indexes from disk
- `threads` (int, default=0): Threads for parallel search

**Examples:**
```python
# From existing indexes
multi_index = Indexes(indexes=[index1, index2, index3])

# From file paths
multi_index = Indexes(
    paths=['shard_1.usearch', 'shard_2.usearch', 'shard_3.usearch'],
    view=True
)
```

### Methods

#### `search(vectors, count=10, *, threads=0)` → BatchMatches

Search across all indexes in parallel.

**Parameters:**
- `vectors` (VectorOrVectorsLike): Query vector(s)
- `count` (int, default=10): Results per index
- `threads` (int, default=0): Parallel threads

**Returns:** Merged and sorted BatchMatches

**Example:**
```python
query = np.random.rand(256).astype(np.float32)
matches = multi_index.search(query, 10, threads=4)
```

## Matches and BatchMatches

### Matches (Single Query Results)

Returned from single-vector search.

**Properties:**
- `keys` → np.ndarray: Array of matched keys
- `distances` → np.ndarray: Array of distances
- `counts` → int: Actual number of matches

**Access:**
```python
matches = index.search(query, 10)

# Iterate
for match in matches:
    print(match.key, match.distance)

# Index access
first_match_key = matches[0].key
first_match_distance = matches[0].distance

# Direct array access
all_keys = matches.keys
all_distances = matches.distances
actual_count = matches.counts
```

### BatchMatches (Multiple Query Results)

Returned from batch search.

**Properties:**
- `keys` → np.ndarray: 2D array [n_queries, count]
- `distances` → np.ndarray: 2D array [n_queries, count]
- `counts` → np.ndarray: Array of actual matches per query

**Access:**
```python
batch_matches = index.search(queries, 10)

# Access results for specific query
query_0_results = batch_matches[0]  # Matches object

# Get all keys and distances
all_keys = batch_matches.keys  # Shape: (n_queries, 10)
all_distances = batch_matches.distances

# Check actual match counts
for i, count in enumerate(batch_matches.counts):
    print(f"Query {i}: {count} matches")
```

## MetricKind Enum

Available distance metrics.

```python
from usearch.index import MetricKind

MetricKind.IP          # Inner product (1 - A·B)
MetricKind.Cos         # Cosine distance (1 - cosine_sim)
MetricKind.L2sq        # Squared Euclidean distance
MetricKind.Haversine   # Great circle distance (geospatial)
MetricKind.Divergence  # KL-divergence-like
MetricKind.Pearson     # Pearson correlation distance
MetricKind.Hamming     # Hamming distance (binary)
MetricKind.Tanimoto    # Tanimoto coefficient (binary)
MetricKind.Sorensen    # Sorensen-Dice coefficient (binary)
```

## ScalarKind Enum

Available data types for quantization.

```python
from usearch.index import ScalarKind

ScalarKind.F64  # 64-bit float (8 bytes)
ScalarKind.F32  # 32-bit float (4 bytes)
ScalarKind.BF16 # Brain float 16 (2 bytes)
ScalarKind.F16  # Half precision float (2 bytes)
ScalarKind.I8   # 8-bit integer (1 byte)
ScalarKind.B1   # 1-bit binary (0.125 bytes per dimension)
```

## MetricSignature Enum

Signatures for custom metrics.

```python
from usearch.index import MetricSignature

MetricSignature.ArrayArray       # float(float* a, float* b)
MetricSignature.ArrayArraySize   # float(float* a, float* b, size_t ndim)
```

## CompiledMetric NamedTuple

Container for JIT-compiled custom metrics.

```python
from usearch.index import CompiledMetric, MetricKind, MetricSignature

metric = CompiledMetric(
    pointer: int,           # Function pointer address
    kind: MetricKind,       # Metric classification
    signature: MetricSignature  # Function signature
)
```

**Example:**
```python
from numba import cfunc, types

@cfunc(types.float32(types.CPointer(types.float32), types.CPointer(types.float32)))
def custom_metric(a, b):
    # Custom distance computation
    return 1.0

metric = CompiledMetric(
    pointer=custom_metric.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray
)

index = Index(ndim=256, metric=metric)
```

## I/O Utilities

### `load_matrix(path)` → np.ndarray

Load binary matrix file (.fbin, .ibin, .hbin, .bbin).

**Parameters:**
- `path` (str | os.PathLike): Path to binary matrix file

**Returns:** NumPy array with shape (rows, columns)

**Example:**
```python
from usearch.io import load_matrix

vectors = load_matrix('dataset.fbin')
print(f"Loaded {vectors.shape[0]} vectors with {vectors.shape[1]} dimensions")
```

### `save_matrix(path, matrix)`

Save NumPy array to binary matrix file.

**Parameters:**
- `path` (str | os.PathLike): Output file path
- `matrix` (np.ndarray): 2D array to save

**Example:**
```python
from usearch.io import save_matrix

vectors = np.random.rand(1000, 256).astype(np.float32)
save_matrix('vectors.fbin', vectors)
```

## Evaluation Utilities

### `self_recall(index, *, exact=False)` → SearchStats

Compute recall@1 by searching for each vector in the index.

**Parameters:**
- `index` (Index): Index to evaluate
- `exact` (bool, default=False): Use exact search as baseline

**Returns:** SearchStats object with:
- `recall_1`: Fraction of queries where true nearest neighbor is found
- `visited_members`: Number of index nodes visited
- `computed_distances`: Number of distance computations

**Example:**
```python
from usearch.eval import self_recall

stats = self_recall(index, exact=False)
print(f"Recall@1: {stats.recall_1:.4f}")
print(f"Visited nodes: {stats.visited_members}")
print(f"Computed distances: {stats.computed_distances}")
```

### `relevance(expected_matches, actual_matches)` → np.ndarray

Compute relevance scores comparing expected vs actual results.

**Parameters:**
- `expected_matches` (BatchMatches): Ground truth results
- `actual_matches` (BatchMatches): Actual search results

**Returns:** Array of relevance scores per query

**Example:**
```python
from usearch.eval import relevance, dcg, ndcg

# Get exact and approximate results
vectors = random_vectors(index=index)
exact = index.search(vectors, exact=True)
approximate = index.search(vectors, exact=False)

# Compute metrics
rel_scores = relevance(exact, approximate)
print(f"DCG: {dcg(rel_scores)}")
print(f"NDCG: {ndcg(rel_scores)}")
```

### `random_vectors(index, *, count=10)` → np.ndarray

Generate random vectors matching index dimensions and dtype.

**Parameters:**
- `index` (Index): Index to match
- `count` (int, default=10): Number of vectors

**Returns:** NumPy array of shape (count, ndim)

**Example:**
```python
from usearch.eval import random_vectors

test_vectors = random_vectors(index, count=100)
matches = index.search(test_vectors, 10)
```

### `dcg(relevance_scores)` → float

Compute Discounted Cumulative Gain.

**Parameters:**
- `relevance_scores` (np.ndarray): Array of relevance scores

**Returns:** DCG value

### `ndcg(relevance_scores)` → float

Compute Normalized Discounted Cumulative Gain.

**Parameters:**
- `relevance_scores` (np.ndarray): Array of relevance scores

**Returns:** NDCG value (0.0 to 1.0)

## Exact Search Function

### `search(vectors, queries, count, metric, *, exact=True)` → BatchMatches

Perform exact brute-force search without building an index.

**Parameters:**
- `vectors` (np.ndarray): Database vectors of shape (n_vectors, ndim)
- `queries` (np.ndarray): Query vectors of shape (n_queries, ndim) or (ndim,)
- `count` (int): Number of results per query
- `metric` (MetricKind): Distance metric
- `exact` (bool, default=True): Use exact search

**Returns:** BatchMatches

**Example:**
```python
from usearch.index import search, MetricKind

vectors = np.random.rand(10000, 256).astype(np.float32)
query = np.random.rand(256).astype(np.float32)

# Exact search without index
matches = search(vectors, query, 10, MetricKind.L2sq, exact=True)

# Much faster than naive Python loops due to SIMD optimization
```

## Constants

### Default Parameters

```python
from usearch.index import (
    DEFAULT_CONNECTIVITY,      # 16
    DEFAULT_EXPANSION_ADD,     # 128
    DEFAULT_EXPANSION_SEARCH   # 64
)
```

### Build Configuration

```python
from usearch.index import (
    USES_OPENMP,    # True if OpenMP enabled
    USES_SIMSIMD,   # True if SimSIMD optimizations available
    USES_FP16LIB    # True if FP16 library linked
)
```

## Clustering Object

Returned from `index.cluster()`.

### Properties

#### `centroids_popularity` → Tuple[np.ndarray, np.ndarray]

Returns (centroid_keys, cluster_sizes).

```python
clustering = index.cluster(max_count=50)
centroid_keys, sizes = clustering.centroids_popularity
```

#### `network` → networkx.Graph

NetworkX graph representation of clusters.

```python
import networkx as nx

g = clustering.network
print(f"Clusters: {g.number_of_nodes()}")
```

### Methods

#### `members_of(centroid_key)` → List[int]

Get all member keys in a cluster.

```python
members = clustering.members_of(centroid_keys[0])
print(f"Cluster has {len(members)} members")
```

#### `subcluster(centroid_key, *, min_count=10, max_count=20, threads=0)` → Clustering

Perform hierarchical sub-clustering on a specific cluster.

```python
sub = clustering.subcluster(centroid_keys[0], max_count=20)
```

#### `plot_centroids_popularity()`

Plot histogram of cluster sizes (requires matplotlib).

```python
clustering.plot_centroids_popularity()
plt.show()
```

## Error Handling

### Common Exceptions

```python
from usearch.index import Index

try:
    index = Index(ndim=256)
    wrong_vector = np.array([1.0, 2.0, 3.0])  # Wrong dimension
    index.add(1, wrong_vector)
except ValueError as e:
    print(f"Dimension mismatch: {e}")

try:
    index.remove(999999)  # Non-existent key
except KeyError as e:
    print(f"Key not found: {e}")
    
try:
    Index.restore('nonexistent.usearch')
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

### Progress Callback Cancellation

Progress callbacks can cancel operations by returning False:

```python
def progress_with_cancel(processed, total):
    if processed > 1000:
        print("Cancelling operation...")
        return False  # Cancel
    return True  # Continue

try:
    index.add(keys, vectors, progress=progress_with_cancel)
except Exception as e:
    print(f"Operation cancelled: {e}")
```
