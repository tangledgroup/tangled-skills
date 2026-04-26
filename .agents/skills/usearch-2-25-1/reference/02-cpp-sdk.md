# C++ SDK

## Overview

USearch is a single-header C++11 library. Copy `include/usearch/*` headers into your project or use CMake FetchContent:

```cmake
FetchContent_Declare(usearch GIT_REPOSITORY https://github.com/unum-cloud/USearch.git)
FetchContent_MakeAvailable(usearch)
```

The high-level interface covers 90% of use cases: `reserve()`, `add()`, `search()`, `size()`, `capacity()`, `save()`, `load()`, `view()`.

## Quickstart

```cpp
#include <usearch/index.hpp>
#include <usearch/index_dense.hpp>
using namespace unum::usearch;

int main() {
    metric_punned_t metric(3, metric_kind_t::l2sq_k, scalar_kind_t::f32_k);
    index_dense_t index = index_dense_t::make(metric);

    index.reserve(10);
    float vec[3] = {0.1f, 0.3f, 0.2f};
    index.add(42, &vec[0]);

    auto results = index.search(&vec[0], 5);
    for (std::size_t i = 0; i != results.size(); ++i)
        std::printf("Found key: %zu\n", results[i].member.key);
    return 0;
}
```

The `add` function has overloads for different vector types, casting under the hood:

```cpp
double vec_double[3] = {0.1, 0.3, 0.2};
_Float16 vec_half[3] = {0.1f, 0.3f, 0.2f};
index.add(43, {&vec_double[0], 3});
index.add(44, {&vec_half[0], 3});
```

## Serialization

```cpp
index.save("index.usearch");
index.load("index.usearch");  // Copy from disk into memory
index.view("index.usearch");  // Memory-map from disk (no RAM load)
```

## Multi-Threading

USearch does not spawn threads internally. The `add()` function is thread-safe, designed to integrate with OpenMP and custom executors:

```cpp
// OpenMP parallel add
#pragma omp parallel for
for (std::size_t i = 0; i < n; ++i)
    index.add(keys[i], span_t{vectors[i], dims});
```

### Executors

Three executor types are provided for bulk operations:

- `executor_default_t` — Fixed-size thread pool, allocate temporary memory per core
- `executor_openmp_t` — Uses OpenMP runtime
- `executor_stl_t` — Spawns `std::thread` instances
- `dummy_executor_t` — Sequential execution

```cpp
std::size_t threads = std::thread::hardware_concurrency() * 4;
executor_default_t executor(threads);
index.reserve(index_limits_t{vectors.size(), executor.size()});

executor.fixed(vectors.size(), [&](std::size_t thread, std::size_t task) {
    index.add(task, vectors[task].data(),
              index_update_config_t{.thread = thread});
});
```

## Error Handling

USearch does not use exceptions to avoid corrupted states in concurrent data structures and memory-edge scenarios. Operations return result objects convertible to bool:

```cpp
bool success;
success = (bool)index.try_reserve(10);   // Preferred over reserve()
success = (bool)index.add(42, &vec[0]);  // add_result_t
success = (bool)index.search(&vec[0], 5); // search_result_t
```

## Clustering

### Single-vector clustering

Map an external vector to its cluster centroid at a specific HNSW graph level:

```cpp
float vector[3] = {0.1f, 0.3f, 0.2f};
cluster_result_t result = index.cluster(&vector[0], index.max_level() / 2);
match_t cluster = result.cluster;
auto member = cluster.member;
auto distance = cluster.distance;
```

Pass `level=0` to traverse every level except the bottom one. Otherwise, search is limited to the specified level.

### Full index clustering

Split the entire index into clusters with auto-tuned level selection:

```cpp
index_dense_clustering_config_t config;
config.min_clusters = 1000;
config.max_clusters = 2000;
config.mode = index_dense_clustering_config_t::merge_smallest_k;

vector_key_t centroids[queries_count];
distance_t distances[queries_count];
executor_default_t thread_pool;
dummy_progress_t progress_bar;

clustering_result_t result = cluster(
    queries_begin, queries_end, config,
    &centroids, &distances, thread_pool, progress_bar);
```

## User-Defined Metrics

Built-in metrics include: `metric_cos`, `metric_ip`, `metric_l2sq`, `metric_jaccard`, `metric_hamming`, `metric_tanimoto`, `metric_sorensen`, `metric_pearson`, `metric_haversine`, `metric_divergence`.

For custom metrics, wrap a function pointer in `metric_punned_t` (a trivial type, unlike `std::function`):

```cpp
auto custom_metric = [](const void* a, const void* b) -> float {
    // Custom distance computation
    return 0.0f;
};
metric_punned_t metric_fn(3, metric_kind_t::cos_k, scalar_kind_t::f32_k);
// Assign function pointer...
```

## Advanced Interface

The low-level template interface provides full control:

```cpp
template <
    typename distance_at = default_distance_t,   // float
    typename key_at = default_key_t,             // uint64_t or uuid_t
    typename compressed_slot_at = default_slot_t, // uint32_t or uint40_t
    typename dynamic_allocator_at = std::allocator<byte_t>,
    typename tape_allocator_at = dynamic_allocator_at
>
class index_gt;
```

Key types: `uint64_t` (default), `uuid_t`. Slot types for neighbor references: `uint32_t` (default, up to 4B entries), `uint40_t` (up to 1 trillion entries, 37.5% smaller than uint64).

Use `index_dense_big_t` for 4B+ capacities, or directly instantiate `index_dense_gt<vector_key_t, internal_id_t>`.

## Default Parameters

- `default_connectivity()` — 16 neighbors per node (FAISS: 32, hnswlib: 16)
- `default_expansion_add()` — 128 construction expansion (FAISS: 40, hnswlib: 200)
- `default_expansion_search()` — 64 search expansion (FAISS: 16, hnswlib: 10)
