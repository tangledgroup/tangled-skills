---
name: hnswlib-0-9-0
description: Header-only C++ library implementing Hierarchical Navigable Small World graphs for fast approximate nearest neighbor (ANN) search with Python bindings via pybind11. Supports L2, inner product, and cosine distance spaces with SIMD-optimized distance computation (SSE/AVX/AVX512). Use when building vector search indexes requiring sub-millisecond latency at scale, implementing incremental index construction with updates and soft deletions, or needing a lightweight dependency-free ANN library as an alternative to FAISS or Annoy.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.9.0"
tags:
  - ann
  - vector-search
  - hnsw
  - nearest-neighbor
  - simd
  - cpp
  - python-bindings
category: machine-learning
external_references:
  - https://github.com/nmslib/hnswlib
---

# hnswlib 0.9.0

## Overview

hnswlib is a lightweight, header-only C++ implementation of the Hierarchical Navigable Small World (HNSW) algorithm for approximate nearest neighbor search, with optional Python bindings via pybind11. It was derived from the nmslib project but significantly simplified — no external dependencies beyond C++11, a minimal codebase of approximately 2,500 lines across six header files, and direct memory management without runtime overhead.

The library supports three distance metrics: squared L2 (Euclidean), inner product, and cosine similarity. Distance computation is auto-vectorized using SSE, AVX, or AVX512 instruction sets when available, with runtime CPU feature detection to select the optimal kernel at construction time.

Key capabilities include incremental index construction (add vectors over time without rebuilding), element updates in-place, soft deletions with optional memory reuse, filtered search via custom predicates, multi-vector document search (multiple vectors per document with document-level ranking), and epsilon-radius search with configurable stop conditions. The index serializes to a compact binary format and supports Python pickle serialization out of the box.

## When to Use

- Building ANN indexes where latency matters (sub-millisecond k-NN at millions of vectors)
- Needing incremental updates — adding, updating, or deleting vectors without full reindexing
- Working in memory-constrained environments — hnswlib has a lower memory footprint than FAISS for comparable recall
- Requiring a header-only C++ library with zero dependencies (embeddable in any C++11 project)
- Building Python services that need fast vector search with numpy integration
- Implementing custom distance functions or search stop conditions via C++ interfaces

## Core Concepts

**HNSW Algorithm**: A graph-based ANN method that constructs a multi-layer navigable small world graph. Layer 0 contains all elements with rich connectivity. Higher layers form sparse shortcuts that enable long-distance jumps during search. The graph is built greedily — each new element connects to its nearest neighbors at each layer it occupies. Search starts from the top layer and descends, using greedy routing to approach the query before performing an exhaustive exploration at layer 0.

**Graph Parameters**:
- `M` — Maximum number of bi-directional links per element at upper layers (default: 16). Level 0 allows up to `2*M`. Directly controls memory usage (~M * 8-10 bytes per element) and search quality.
- `ef_construction` — Size of the dynamic candidate list during index building (default: 200). Higher values produce better graph connectivity at the cost of slower construction.
- `ef` — Size of the dynamic candidate list during search (default: 10, must be >= k). Controls the speed/recall trade-off at query time.

**Element Levels**: Each element is assigned a random level drawn from an exponential distribution with mean `1 / ln(M)`. Elements at higher levels have fewer connections but serve as shortcuts for greedy routing. The maximum level in the graph determines the entry point for all searches.

**Memory Layout**: Level 0 data (links, vector, and label) is stored in a single contiguous `char*` array (`data_level0_memory_`) for cache efficiency. Upper layers are allocated per-element in `linkLists_`. This design minimizes fragmentation for the base layer while allowing variable-size allocations for sparse upper layers.

## Installation / Setup

### C++ Usage (Header-Only)

Copy the `hnswlib/` directory into your project and include `hnswlib.h`:

```cpp
#include "hnswlib/hnswlib.h"

// Create a distance space and index
hnswlib::L2Space space(128);
hnswlib::HierarchicalNSW<float>* index = new hnswlib::HierarchicalNSW<float>(
    &space, 100000,  // max_elements
    16,              // M
    200              // ef_construction
);

// Add vectors (raw float arrays)
float* vector_data = ...;
index->addPoint(vector_data, label_id);

// Search for k nearest neighbors
auto results = index->searchKnn(query_vector, k);

// Save and load
index->saveIndex("index.bin");
delete index;
index = new hnswlib::HierarchicalNSW<float>(&space, "index.bin");
```

### Python Bindings

Install from PyPI:

```bash
pip install hnswlib
```

Build from source (requires pybind11 and numpy):

```bash
git clone https://github.com/nmslib/hnswlib.git
cd hnswlib
pip install .
```

Set `HNSWLIB_NO_NATIVE` environment variable to skip `-march=native` compiler flag if cross-compiling.

### CMake Integration

hnswlib provides a CMake INTERFACE library:

```cmake
add_subdirectory(hnswlib)
target_link_libraries(my_app hnswlib::hnswlib)
```

## Usage Examples

### Python: Basic Index and Search

```python
import hnswlib
import numpy as np

dim = 128
num_elements = 10000

# Generate sample data (must be float32)
data = np.float32(np.random.random((num_elements, dim)))
ids = np.arange(num_elements)

# Create and initialize index
p = hnswlib.Index(space='l2', dim=dim)
p.init_index(max_elements=num_elements, ef_construction=200, M=16)

# Insert vectors
p.add_items(data, ids)

# Configure search quality (ef must be >= k)
p.set_ef(50)

# Query: returns (labels, distances) as numpy arrays
labels, distances = p.knn_query(data[:5], k=10)
```

### Python: Incremental Loading with Capacity Expansion

```python
import hnswlib
import numpy as np

dim = 16
num_elements = 10000
data = np.float32(np.random.random((num_elements, dim)))

# Build index with half capacity
p = hnswlib.Index(space='l2', dim=dim)
p.init_index(max_elements=num_elements // 2, ef_construction=100, M=16)
p.set_ef(10)
p.add_items(data[:num_elements // 2])

# Save and reload with expanded capacity
p.save_index("index.bin")
del p

p = hnswlib.Index(space='l2', dim=dim)
p.load_index("index.bin", max_elements=num_elements)
p.add_items(data[num_elements // 2:])  # Add remaining vectors
```

### Python: Filtering During Search

```python
import hnswlib
import numpy as np

dim = 16
data = np.float32(np.random.random((10000, dim)))

p = hnswlib.Index(space='l2', dim=dim)
p.init_index(max_elements=10000, ef_construction=100, M=16)
p.add_items(data, ids=np.arange(10000))

# Filter: only return even-labeled elements
filter_fn = lambda idx: idx % 2 == 0
labels, distances = p.knn_query(data[:5], k=10, filter=filter_fn, num_threads=1)
# Note: Python filter with multithreading is slow — use num_threads=1
```

### C++: Custom Filter Implementation

```cpp
#include "hnswlib/hnswlib.h"

class EvenIdFilter : public hnswlib::BaseFilterFunctor {
public:
    bool operator()(hnswlib::labeltype label_id) override {
        return label_id % 2 == 0;
    }
};

// Usage
hnswlib::L2Space space(128);
auto* index = new hnswlib::HierarchicalNSW<float>(&space, 10000, 16, 200);
// ... add data ...

EvenIdFilter filter;
auto results = index->searchKnn(query_data, k, &filter);
```

## Advanced Topics

**HNSW Algorithm Internals**: Graph construction, level assignment, greedy routing, connection heuristic → [Algorithm Details](reference/01-hnsw-algorithm.md)

**C++ API Reference**: HierarchicalNSW class, SpaceInterface, distance spaces (L2Space, InnerProductSpace), BruteforceSearch, multi-vector spaces → [C++ API](reference/02-cpp-api.md)

**Python Bindings Deep Dive**: Index and BFIndex classes, pybind11 implementation details, pickle serialization, thread model, memory layout → [Python Bindings](reference/03-python-bindings.md)

**SIMD Distance Optimization**: SSE/AVX/AVX512 kernels, runtime CPU detection, residual handling for non-aligned dimensions, distance function dispatch → [SIMD Optimizations](reference/04-simd-optimizations.md)

**Advanced Search Features**: Filtering with BaseFilterFunctor, multi-vector document search, epsilon-radius search, custom stop conditions, element deletion and replacement → [Advanced Features](reference/05-advanced-features.md)
