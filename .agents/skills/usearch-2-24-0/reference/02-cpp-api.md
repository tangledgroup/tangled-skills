# C++ API

## Installation

Copy the `include/usearch/*` headers into your project, or fetch with CMake:

```cmake
FetchContent_Declare(usearch GIT_REPOSITORY https://github.com/unum-cloud/USearch.git)
FetchContent_MakeAvailable(usearch)
```

The library is a single-header C++11 implementation. Version macros are defined in the header:

```cpp
#define USEARCH_VERSION_MAJOR 2
#define USEARCH_VERSION_MINOR 25
#define USEARCH_VERSION_PATCH 1
```

## Quickstart

```cpp
#include <usearch/index.hpp>
#include <usearch/index_dense.hpp>

using namespace unum::usearch;

int main() {
    metric_punned_t metric(3, metric_kind_t::l2sq_k, scalar_kind_t::f32_k);

    // Use index_dense_big_t for 4B+ entries
    index_dense_t index = index_dense_t::make(metric);
    float vec[3] = {0.1, 0.3, 0.2};

    index.reserve(10);
    index.add(42, &vec[0]);
    auto results = index.search(&vec[0], 5);

    for (std::size_t i = 0; i != results.size(); ++i)
        std::printf("Found key: %zu\n", results[i].member.key);
    return 0;
}
```

The `add` function is thread-safe for concurrent index construction. Overloads accept different vector types, casting under the hood:

```cpp
double vec_double[3] = {0.1, 0.3, 0.2};
_Float16 vec_half[3] = {0.1, 0.3, 0.2};
index.add(43, span_t{&vec_double[0], 3});
index.add(44, span_t{&vec_half[0], 3});
```

## Serialization

```cpp
index.save("index.usearch");
index.load("index.usearch");   // Copy from disk
index.view("index.usearch");   // Memory-map from disk
```

## Error Handling

USearch avoids exceptions to prevent corrupted states in concurrent data structures. Operations return result objects:

```cpp
bool success;
success = (bool)index.try_reserve(10);
success = (bool)index.add(42, &vec[0]);
success = (bool)index.search(&vec[0], 5);
```

## Multi-Threading with Executors

USearch focuses on thread-safe `add()` rather than internal thread pools. Integrate with your own executor:

```cpp
std::size_t executor_threads = std::thread::hardware_concurrency() * 4;
executor_default_t executor(executor_threads);

index.reserve(index_limits_t{vectors.size(), executor.size()});
executor.fixed(vectors.size(), [&](std::size_t thread, std::size_t task) {
    index.add(task, vectors[task].data(), index_update_config_t{.thread = thread});
});
```

Available executors:
- `executor_default_t` — USearch's built-in executor
- `executor_openmp_t` — uses OpenMP under the hood
- `executor_stl_t` — spawns `std::thread` instances
- `dummy_executor_t` — sequential execution

OpenMP parallel indexing:

```cpp
#pragma omp parallel for
for (std::size_t i = 0; i < n; ++i)
    native.add(key, span_t{vector, dims});
```

## Clustering

Cluster a single vector against the index:

```cpp
some_scalar_t vector[3] = {0.1, 0.3, 0.2};
cluster_result_t result = index.cluster(&vector, index.max_level() / 2);
match_t cluster = result.cluster;
member_cref_t member = cluster.member;
distance_t distance = cluster.distance;
```

Split the entire index into clusters:

```cpp
std::size_t queries_count = queries_end - queries_begin;
index_dense_clustering_config_t config;
config.min_clusters = 1000;
config.max_clusters = 2000;
config.mode = index_dense_clustering_config_t::merge_smallest_k;

vector_key_t cluster_centroids_keys[queries_count];
distance_t distances_to_cluster_centroids[queries_count];
executor_default_t thread_pool;
dummy_progress_t progress_bar;

clustering_result_t result = cluster(
    queries_begin, queries_end,
    config,
    &cluster_centroids_keys, &distances_to_cluster_centroids,
    thread_pool, progress_bar);
```

## User-Defined Metrics

Built-in metric types:
- `metric_cos_gt<scalar_t>` — Cosine/Angular distance
- `metric_ip_gt<scalar_t>` — Inner Product/Dot Product
- `metric_l2sq_gt<scalar_t>` — Squared L2/Euclidean
- `metric_jaccard_gt<scalar_t>` — Jaccard distance for ordered sets
- `metric_hamming_gt<scalar_t>` — Bit-level Hamming distance
- `metric_tanimoto_gt<scalar_t>` — Tanimoto coefficient for bit-strings
- `metric_sorensen_gt<scalar_t>` — Dice-Sorensen coefficient
- `metric_pearson_gt<scalar_t>` — Pearson correlation
- `metric_haversine_gt<scalar_t>` — Great Circle distance (GIS)
- `metric_divergence_gt<scalar_t>` — Jensen-Shannon similarity

For custom metrics, wrap your function in `metric_punned_t` — a trivial type alternative to `std::function`:

```cpp
// Implement a metric_punned_t with your custom distance function
// NumKong backends provide hardware-accelerated kernels for common types
```

## Advanced Template Interface

The low-level index template:

```cpp
template <
    typename distance_at = default_distance_t,              // float
    typename key_at = default_key_t,                        // int64_t, uuid_t
    typename compressed_slot_at = default_slot_t,           // uint32_t, uint40_t
    typename dynamic_allocator_at = std::allocator<byte_t>,
    typename tape_allocator_at = dynamic_allocator_at>
class index_gt;
```

## Hardware Detection

The header auto-detects:
- C++ version (C++11, C++17, C++20)
- OS (Windows, macOS, Linux, Android)
- Compiler (Clang, GCC, MSVC)
- Architecture (x86_64, aarch64)
- Bitness (32-bit, 64-bit)

Prefetching uses `__builtin_prefetch` on GCC or `_mm_prefetch` on x86.
