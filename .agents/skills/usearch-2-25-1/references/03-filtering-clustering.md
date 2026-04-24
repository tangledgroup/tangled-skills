# Filtering, Clustering & Joins

> **Source:** https://github.com/unum-cloud/usearch
> **Loaded from:** SKILL.md (via progressive disclosure)

## Filtering with Predicates

Pass a predicate function to search that filters during graph traversal, avoiding manual paging:

### Rust

```rust
let is_odd = |key: Key| key % 2 == 1;
let query = vec![0.2, 0.1, 0.2, 0.1, 0.3];
let results = index.filtered_search(&query, 10, is_odd).unwrap();
assert!(results.keys.iter().all(|&key| key % 2 == 1));
```

### C

```c
int is_odd(usearch_key_t key, void* state) {
    return key % 2;
}

usearch_key_t found_keys[10];
usearch_distance_t found_distances[10];
usearch_filtered_search(
    index, &query[0], usearch_scalar_f32_k, 10,
    &is_odd, NULL,
    &found_keys[0], &found_distances[0], &error);
```

### Go

```go
handler := &usearch.FilteredSearchHandler{
    Callback: func(key usearch.Key, handler *usearch.FilteredSearchHandler) int {
        if key % 2 == 0 {
            return 1 // Accept
        }
        return 0 // Reject
    },
}
keys, distances, err := index.FilteredSearch(queryVector, 10, handler)
```

## Clustering

USearch performs K-Nearest Neighbors clustering using the HNSW graph structure, much faster than SciPy, UMap, or tSNE for large datasets. For 50,000 clusters on 1M points, USearch can be 100x faster than conventional methods.

### Python

```python
clustering = index.cluster(
    min_count=10,
    max_count=15,
    threads=...,
)

# Get cluster centroids and sizes
centroid_keys, sizes = clustering.centroids_popularity

# Plot histogram (requires matplotlib)
clustering.plot_centroids_popularity()

# Export as NetworkX graph
g = clustering.network

# Get members of a specific cluster
first_members = clustering.members_of(centroid_keys[0])

# Sub-cluster (iterative deepening)
sub_clustering = clustering.subcluster(min_count=..., max_count=...)
```

### C++

```cpp
// Single-vector clustering (find cluster for external vector)
some_scalar_t vector[3] = {0.1, 0.3, 0.2};
cluster_result_t result = index.cluster(&vector, index.max_level() / 2);
match_t cluster = result.cluster;
member_cref_t member = cluster.member;
distance_t distance = cluster.distance;

// Full index clustering
index_dense_clustering_config_t config;
config.min_clusters = 1000;
config.max_clusters = 2000;
config.mode = index_dense_clustering_config_t::merge_smallest_k;

vector_key_t cluster_centroids_keys[queries_count];
distance_t distances_to_centroids[queries_count];
executor_default_t thread_pool;

clustering_result_t result = cluster(
    queries_begin, queries_end,
    config,
    &cluster_centroids_keys, &distances_to_centroids,
    thread_pool, progress_bar);
```

## Joins (One-to-One, One-to-Many, Many-to-Many)

USearch supports sub-quadratic approximate joins for fuzzy matching tasks:

```python
men = Index(...)
women = Index(...)
pairs = men.join(women, max_proposals=0, exact=False)
```

This enables semantic joins — fuzzy one-to-one mappings that ban collisions among separate search results. Useful for database fuzzy-matching operations.

## Exact Search

For small datasets, bypass HNSW indexing entirely with brute-force SIMD-optimized search:

### Python

```python
from usearch.index import search, MetricKind
import numpy as np

vectors = np.random.rand(10_000, 1024).astype(np.float32)
vector = np.random.rand(1024).astype(np.float32)

# One-in-many exact search
matches = search(vectors, vector, 50, MetricKind.L2sq, exact=True)

# Many-in-many batch exact search
batch_matches = search(vectors, vectors, 50, MetricKind.L2sq, exact=True)
```

### C

```c
usearch_exact_search(
    &dataset[0][0], dataset_count, dimensions * sizeof(nk_f16_t),
    &queries[0][0], queries_count, dimensions * sizeof(nk_f16_t),
    usearch_scalar_f16_k, top_k, threads,
    &resulting_keys[0][0], sizeof(usearch_key_t) * top_k,
    &resulting_distances[0][0], sizeof(usearch_distance_t) * top_k,
    &error);
```

### Go

```go
keys, distances, err := usearch.ExactSearch(
    dataset, queries,
    datasetSize, queryCount,
    vectorDims*4, vectorDims*4,
    vectorDims, usearch.Cosine,
    maxResults, 0, // 0 threads = auto-detect
)
```

## Evaluation Tools

Python provides evaluation utilities for measuring index quality:

```python
from usearch.eval import self_recall, relevance, dcg, ndcg, random_vectors
from usearch.io import load_matrix, save_matrix

# Self-recall test
stats = self_recall(index, exact=True)
assert stats.visited_members == 0  # Exact search skips index nodes
assert stats.computed_distances == len(index)

stats = self_recall(index, exact=False)
assert stats.visited_members > 0

# Relevance scoring
vectors = random_vectors(index=index)
matches_approximate = index.search(vectors)
matches_exact = index.search(vectors, exact=True)
relevance_scores = relevance(matches_exact, matches_approximate)
print(dcg(relevance_scores), ndcg(relevance_scores))

# Load standard k-ANN binary matrix files
vectors = load_matrix('deep1B.fbin')
```

## Multi-Index Lookups (Indexes)

For billions of vectors, build multiple smaller indexes and view them together:

```python
from usearch.index import Indexes

multi_index = Indexes(
    indexes=[...],
    paths=[...],
    view=False,
    threads=0,
)
multi_index.search(...)
```

## Modifying the Index

HNSW indexes are not ideal for frequent removals or major distribution shifts. For small updates:

```python
# Get a stored vector
recovered = index[42]

# Rename a key
index.rename(43, 42)

# Remove a vector
index.remove(42)
```

## Binary Vectors (Rust)

```rust
use usearch::{Index, IndexOptions, MetricKind, ScalarKind};
use usearch::b1x8;

let index = Index::new(&IndexOptions {
    dimensions: 8,
    metric: MetricKind::Hamming,
    quantization: ScalarKind::B1x8,
    ..Default::default()
}).unwrap();

let vector42: Vec<b1x8> = vec![b1x8(0b00001111)];
let vector43: Vec<b1x8> = vec![b1x8(0b11110000)];
let query: Vec<b1x8> = vec![b1x8(0b01111000)];

index.reserve(10).unwrap();
index.add(42, &vector42).unwrap();
index.add(43, &vector43).unwrap();
let results = index.search(&query, 5).unwrap();
// results.keys[0] == 43 (distance 2.0)
// results.keys[1] == 42 (distance 6.0)
```
