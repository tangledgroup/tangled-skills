---
name: usearch-2-25-1
description: High-performance single-file similarity search and clustering engine for vectors using HNSW algorithm with user-defined metrics, quantization, and multi-language bindings (Python, C++, Rust, JavaScript, Java, Go, C, Swift, C#, Wolfram). Use when building vector search applications, implementing approximate nearest neighbors (ANN) search, performing semantic search, molecular similarity matching, geospatial indexing, or requiring faster alternatives to FAISS with custom distance functions.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.25.1"
tags:
  - vector-search
  - ann
  - hnsw
  - similarity-search
  - clustering
  - quantization
  - simd
category: machine-learning
external_references:
  - https://github.com/unum-cloud/usearch
  - https://docs.rs/usearch/latest/usearch/
  - https://github.com/ashvardanian/numkong
  - https://unum-cloud.github.io/USearch/
  - https://unum-cloud.github.io/USearch/cpp
  - https://unum-cloud.github.io/USearch/python
  - https://www.unum.cloud/blog/2023-11-07-scaling-vector-search-with-intel
  - https://github.com/unum-cloud/USearch/tree/main/docs
---

# USearch 2.25.1

## Overview

USearch is a fast, single-header similarity search and clustering engine for vectors and arbitrary objects. It implements the HNSW (Hierarchical Navigable Small World) algorithm with SIMD-accelerated distance calculations, supporting 10+ programming languages through native bindings. The library is Apache-2.0 licensed by Unum Cloud and authored by Ash Vardanian.

Key characteristics:

- **10x faster** HNSW implementation than FAISS on Intel Sapphire Rapids hardware
- **Single C++11 header** — 3K SLOC vs FAISS's 84K SLOC
- **No required dependencies** — no BLAS, no SWIG bindings
- **User-defined metrics** with JIT compilation via Numba, Cppyy, or PeachPy
- **Hardware-agnostic quantization** from f64 down to single-bit b1x8 representations
- **Memory-mapped disk serving** for indexes too large for RAM (20x cost reduction on AWS)
- **uint40_t keys** for 4B+ vector capacity without 8-byte neighbor references
- **Thread-safe add** operations with OpenMP and custom executor support
- **SQLite extension** available for embedded database integration

Platforms: Linux, macOS, Windows, iOS, Android, WebAssembly.

## When to Use

- Building approximate nearest neighbor (ANN) search over millions or billions of vectors
- Replacing FAISS with a lighter, faster alternative that supports custom distance functions
- Implementing semantic search, recommendation systems, or image retrieval
- Molecular similarity matching using binary fingerprints (Tanimoto, Sorensen coefficients)
- Geospatial indexing with Haversine or custom Vincenty distance
- Clustering large vector collections (100x faster than Scikit-Learn for 50K clusters)
- Multi-index lookups across billions of vectors via `Indexes` federation
- Semantic joins — sub-quadratic fuzzy matching between two vector collections
- Applications requiring quantization to bf16, f16, float8 (e5m2/e4m3), or i8

## Core Concepts

**HNSW Algorithm**: USearch builds a multi-level proximity graph where each node connects to a configurable number of neighbors (`connectivity`). Search traverses from higher levels down, narrowing the candidate set at each layer. The `expansion_add` parameter controls indexing quality (analogous to `efConstruction` in the HNSW paper), and `expansion_search` controls search quality (analogous to `ef`).

**Distance Metrics**: Unlike most libraries that support only inner product and L2, USearch ships with Cosine, L2sq, Inner Product, Jaccard, Hamming, Tanimoto, Sorensen, Pearson, Haversine, Jensen-Shannon Divergence — plus arbitrary user-defined metrics compiled at runtime.

**Quantization**: Vectors are stored in the specified `dtype` (f64, f32, bf16, f16, e5m2, e4m3, e3m2, e2m3, u8, i8, b1). The add and search operations automatically cast between input type and storage type. For bf16 and float8 types not natively in NumPy, pre-quantize with NumKong and pass raw buffers.

**Keys**: Vectors are identified by integer keys (uint64_t by default). Multiple vectors can share a key when `multi=True`. Keys support rename operations for iterative clustering relabeling.

## Installation / Setup

**Python:**
```bash
pip install usearch
```

**Rust:**
```toml
[dependencies]
usearch = "2.25.1"
```

**C++**: Copy `include/usearch/*` headers into your project, or fetch via CMake:
```cmake
FetchContent_Declare(usearch GIT_REPOSITORY https://github.com/unum-cloud/USearch.git)
FetchContent_MakeAvailable(usearch)
```

**JavaScript:** `npm install usearch`
**Java:** Fat JAR download from releases.
**Go:** Go module via proxy.
**C#:** NuGet package `Cloud.Unum.USearch`.
**Swift, Objective-C, Wolfram:** Native bindings from the repository.

## Usage Examples

### Python Quickstart

```python
import numpy as np
from usearch.index import Index

index = Index(ndim=3, metric='cos', dtype='bf16')
vector = np.array([0.2, 0.6, 0.4])
index.add(42, vector)
matches = index.search(vector, 10)

assert matches[0].key == 42
assert matches[0].distance <= 0.001
```

### C++ Quickstart

```cpp
#include <usearch/index.hpp>
#include <usearch/index_dense.hpp>
using namespace unum::usearch;

metric_punned_t metric(3, metric_kind_t::l2sq_k, scalar_kind_t::f32_k);
index_dense_t index = index_dense_t::make(metric);
float vec[3] = {0.1, 0.3, 0.2};
index.reserve(10);
index.add(42, &vec[0]);
auto results = index.search(&vec[0], 5);
```

### Rust Quickstart

```rust
use usearch::{Index, IndexOptions, MetricKind, ScalarKind, new_index};

let options = IndexOptions {
    dimensions: 3,
    metric: MetricKind::IP,
    quantization: ScalarKind::BF16,
    connectivity: 0,  // auto
    expansion_add: 0,  // auto
    expansion_search: 0,  // auto
};
let index: Index = new_index(&options).unwrap();
index.reserve(10).unwrap();
let vec = [0.2f32, 0.1, 0.2];
index.add(42, &vec).unwrap();
let results = index.search(&vec, 10).unwrap();
```

## Advanced Topics

**Python SDK**: Full API reference with batch operations, clustering, serialization, and JIT metrics → See [Python SDK](reference/01-python-sdk.md)

**C++ SDK**: Header-only interface, multi-threading executors, error handling, low-level templates → See [C++ SDK](reference/02-cpp-sdk.md)

**Rust SDK**: Native bindings with custom metrics, filtering predicates, and quantization types → See [Rust SDK](reference/03-rust-sdk.md)

**Distance Metrics**: Built-in metrics, user-defined metrics via Numba/Cppyy/PeachPy, binary and geospatial metrics → See [Distance Metrics](reference/04-distance-metrics.md)

**Quantization and Memory**: dtype options, NumKong interop, uint40_t keys, disk serving with memory mapping → See [Quantization and Memory](reference/05-quantization-memory.md)

**Clustering and Joins**: KNN clustering, sub-clustering, semantic joins via stable marriage algorithm → See [Clustering and Joins](reference/06-clustering-joins.md)

**Integrations and File Format**: Database integrations (ClickHouse, DuckDB, ScyllaDB), file format specification → See [Integrations and File Format](reference/07-integrations-format.md)
