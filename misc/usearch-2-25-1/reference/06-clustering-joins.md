# Clustering and Joins

## KNN Clustering

Once an HNSW index is built, USearch performs K-Nearest Neighbors clustering much faster than SciPy, UMap, or tSNE. The index itself represents a clustering structure that supports iterative deepening.

### Python Clustering

```python
clustering = index.cluster(
    min_count=10,   # Minimum cluster size
    max_count=15,   # Maximum cluster size
    threads=0,      # 0 = all cores
)

# Get cluster centroids and their sizes
centroid_keys, sizes = clustering.centroids_popularity

# Plot histogram of cluster sizes (requires matplotlib)
clustering.plot_centroids_popularity()

# Export as NetworkX graph
g = clustering.network

# Get members of a specific cluster
first_members = clustering.members_of(centroid_keys[0])

# Sub-cluster: split a cluster into smaller parts
sub_clustering = clustering.subcluster(
    centroid=centroid_keys[0],
    min_count=5, max_count=8
)
```

For 50,000 clusters on a 1M point dataset, USearch is approximately 100x faster than Scikit-Learn's K-Means.

### C++ Clustering

Single-vector clustering at a specific graph level:

```cpp
float vector[3] = {0.1f, 0.3f, 0.2f};
cluster_result_t result = index.cluster(&vector[0], index.max_level() / 2);
match_t cluster = result.cluster;
auto key = cluster.member.key;
auto distance = cluster.distance;
```

Full index clustering with auto-tuned level selection:

```cpp
index_dense_clustering_config_t config;
config.min_clusters = 1000;
config.max_clusters = 2000;
config.mode = index_dense_clustering_config_t::merge_smallest_k;

vector_key_t centroids[queries_count];
distance_t distances[queries_count];
clustering_result_t result = cluster(
    queries_begin, queries_end, config,
    &centroids, &distances, thread_pool, progress_bar);
```

## Semantic Joins

USearch implements sub-quadratic approximate joins using the Male-Optimal Stable Marriage algorithm adapted for vector similarity. Unlike search (which allows collisions), join produces a one-to-one mapping between two collections.

### Python Join

```python
men = Index(ndim=128, metric='cos')
women = Index(ndim=128, metric='cos')

# Populate both indexes...
pairs: dict = men.join(women, max_proposals=0, exact=False)
# Returns Dict[Key, Key] — one-to-one mapping
```

Parameters:
- `max_proposals` — Limit on candidates evaluated per vector (0 = unlimited)
- `exact` — Use brute-force search instead of HNSW approximation

### C++ Join

```cpp
auto result = join(
    men, women,
    men_values, women_values,
    men_metric, women_metric,
    config,        // index_join_config_t
    man_to_woman,  // Output: map men keys to women
    woman_to_man,  // Output: map women keys to men
    executor,      // Thread pool
    progress       // Progress callback
);
```

## Use Cases

**Database fuzzy matching**: Implement approximate joins in DBMS for fuzzy text matching, record deduplication, or entity resolution.

**Recommendation systems**: Match users to items by embedding both into the same vector space and performing semantic join.

**Iterative clustering**: Use `rename()` to relabel vectors with cluster IDs, then re-cluster until convergence. The HNSW graph naturally supports this iterative deepening pattern.

**Image-text matching**: Build separate indexes for image and text embeddings, then use join to find the best cross-modal pairs without O(n*m) comparison.
