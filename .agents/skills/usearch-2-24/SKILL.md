---
name: usearch-2-24
description: A skill for using USearch 2.24, a high-performance single-file similarity search and clustering engine for vectors supporting HNSW algorithm with user-defined metrics, quantization, and multi-language bindings including Python, C++, Rust, JavaScript, Java, Go, and more. Use when building vector search applications, implementing approximate nearest neighbors (ANN) search, performing semantic search, molecular similarity matching, geospatial indexing, or requiring faster alternatives to FAISS with custom distance functions.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - vector-search
  - hnsw
  - similarity-search
  - approximate-nearest-neighbors
  - embedding-search
  - faiss-alternative
  - quantization
  - clustering
  - semantic-search
category: machine-learning
required_environment_variables: []
---

# USearch 2.24

USearch is a smaller and faster single-file similarity search and clustering engine for vectors, implementing the HNSW (Hierarchical Navigable Small World) algorithm with up to 10x performance improvement over FAISS. It supports user-defined metrics, hardware-accelerated quantization (f16, bf16, i8, b1), multi-language bindings, and can serve indexes from disk without loading into RAM for significant cost reduction.

## When to Use

- Building vector search applications requiring high-performance ANN (Approximate Nearest Neighbors) search
- Implementing semantic search with custom distance metrics beyond standard cosine or L2
- Needing faster indexing than FAISS for large-scale vector collections (millions to billions)
- Performing molecular similarity search with binary metrics (Tanimoto, Sorensen)
- Geospatial applications using Haversine or Vincenty distance formulas
- Memory-constrained environments requiring quantization (f16, i8, b1)
- Multi-language projects needing cross-platform index compatibility
- Clustering large datasets faster than SciPy, UMap, or tSNE
- Implementing fuzzy joins and semantic matching in database applications

## Setup

### Python Installation

```bash
pip install usearch
```

Optional dependencies for custom metrics:

```bash
# For JIT-compiled custom metrics in Python
pip install numba

# For C++ JIT compilation
conda install -c conda-forge cppyy

# For assembly-level optimizations
pip install peachpy
```

### C++ Integration

USearch is a single-header library. Include the header file:

```cpp
#include "usearch/index.hpp"

unum::usearch::index_dense_t<> index;
```

Compile with C++11 or later. For optimal performance:

```bash
cmake -DUSEARCH_BUILD_BENCH_CPP=1 \
      -DUSEARCH_USE_OPENMP=1 \
      -DUSEARCH_USE_SIMSIMD=1 \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -B build_profile
cmake --build build_profile --config RelWithDebInfo -j
```

### Other Languages

USearch provides native bindings for:
- **Rust**: `cargo add usearch`
- **JavaScript/Node.js**: `npm install usearch`
- **Java**: Download fat-JAR from releases
- **Go**: `go get github.com/unum-cloud/usearch/go`
- **C#**: `dotnet add package Cloud.Unum.USearch`
- **Swift**, **Objective-C**, **C**, **Wolfram**

See [Core Concepts](references/01-core-concepts.md) for language-specific setup details.

## Quick Start

### Basic Vector Search

```python
import numpy as np
from usearch.index import Index

# Create index for 3-dimensional vectors
index = Index(ndim=3)

# Add a vector with key 42
vector = np.array([0.2, 0.6, 0.4])
index.add(42, vector)

# Search for nearest neighbors
matches = index.search(vector, 10)  # Find 10 nearest

assert matches[0].key == 42
assert matches[0].distance <= 0.001
```

See [Core Concepts](references/01-core-concepts.md) for detailed Index configuration and parameter explanations.

### Batch Operations

```python
import numpy as np
from usearch.index import Index

index = Index(ndim=256, metric='cos', dtype='f32')

# Add 100 vectors at once
n = 100
keys = np.arange(n)
vectors = np.random.uniform(0, 0.3, (n, 256)).astype(np.float32)
index.add(keys, vectors, threads=4)  # Parallel insertion

# Batch search
matches = index.search(vectors, 10, threads=4)
print(f"Found {len(matches)} result sets")
```

Refer to [Advanced Workflows](references/02-advanced-workflows.md) for batch processing best practices and performance tuning.

### Serialization and Disk Serving

```python
# Save index to disk
index.save('index.usearch')

# Load into memory (copies entire index)
index.load('index.usearch')

# View from disk without loading (memory-efficient)
view = Index.restore('index.usearch', view=True)

# Get metadata without loading
metadata = Index.metadata('index.usearch')
print(f"Index has {metadata.count} vectors with {metadata.ndim} dimensions")
```

See [API Reference](references/03-api-reference.md) for complete serialization API and metadata structure.

## Configuration Options

### Basic Configuration

```python
index = Index(
    ndim=768,              # Vector dimensions
    metric='cos',          # 'l2sq', 'ip', 'cos', 'haversine', etc.
    dtype='bf16',          # 'f64', 'f32', 'f16', 'bf16', 'i8', 'b1'
    connectivity=16,       # Neighbors per graph node (default: 16)
    expansion_add=128,     # Indexing recall control (default: 128)
    expansion_search=64,   # Search quality control (default: 64)
    multi=False,           # Allow multiple vectors per key
)
```

### Performance Comparison vs FAISS

| Metric | FAISS | USearch | Improvement |
|--------|-------|---------|-------------|
| Indexing 100M 96d vectors | 2.6h | 0.3h | **9.6x faster** |
| Codebase size | 84K SLOC | 3K SLOC | Maintainable |
| Supported metrics | 9 fixed | Any metric | Extensible |
| Languages | C++, Python | 10+ languages | Portable |
| Python binding size | ~10 MB | <1 MB | Deployable |

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Index configuration, metrics, quantization types, and hardware acceleration detection
- [`references/02-advanced-workflows.md`](references/02-advanced-workflows.md) - Custom metrics with Numba/Cppyy, clustering, joins, filtering, and multi-index lookups
- [`references/03-api-reference.md`](references/03-api-reference.md) - Complete API documentation including Index, Indexes, serialization, I/O utilities, and evaluation tools
- [`references/04-troubleshooting.md`](references/04-troubleshooting.md) - Common issues, performance tuning, quantization artifacts, and debugging techniques

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/usearch-2-24/`). All paths are relative to this directory.

## Troubleshooting

### Quantization Precision Loss

When using `dtype='i8'` or `dtype='f16'`, retrieval may not return exact original vectors:

```python
index = Index(ndim=768, dtype='i8')
original = np.array([0.1, 0.2, 0.3], dtype=np.float32)
index.add(1, original)
retrieved = index[1]  # May differ due to quantization
```

**Solution**: Store original vectors separately if exact retrieval is needed:

```python
import numpy as np

# External storage for originals
vectors_store = {}

index = Index(ndim=768, dtype='i8')
vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
index.add(42, vector)
vectors_store[42] = vector  # Keep original
```

### Hardware Acceleration Not Detected

Check if hardware acceleration is enabled:

```python
from usearch.index import Index

index_f16 = Index(ndim=768, metric='cos', dtype='f16')
print(f"Hardware acceleration: {index_f16.hardware_acceleration}")
# Output: 'sapphire', 'ice', 'none', etc.
```

See [Troubleshooting Guide](references/04-troubleshooting.md) for detailed diagnostics and solutions.

### Memory Usage Optimization

For large indexes, use disk viewing to reduce RAM:

```python
# Instead of loading (RAM-intensive)
# index.load('large_index.usearch')

# Use viewing (memory-mapped)
index = Index.restore('large_index.usearch', view=True)
```

This can result in 20x cost reduction on cloud platforms by serving from external storage.

## Common Patterns

### Semantic Search Pipeline

```python
from usearch.index import Index
import numpy as np

# Assume you have an embedding model
def embed_text(text):
    # Your embedding function returning np.ndarray
    pass

index = Index(ndim=768, metric='cos', dtype='f32')

# Build index
documents = ["doc1 text", "doc2 text", ...]
for i, doc in enumerate(documents):
    vector = embed_text(doc)
    index.add(i, vector)

# Search
query_vector = embed_text("search query")
matches = index.search(query_vector, 10)
for match in matches:
    print(f"Doc {match.key}: distance={match.distance}")
```

### Multi-Index Parallel Search

```python
from usearch.index import Indexes

# Create multiple smaller indexes
index1 = Index(ndim=256)
index2 = Index(ndim=256)
index3 = Index(ndim=256)

# Combine for parallel search
multi_index = Indexes(indexes=[index1, index2, index3])

# Search across all indexes simultaneously
query = np.random.rand(256).astype(np.float32)
matches = multi_index.search(query, 10, threads=4)
```

See [Advanced Workflows](references/02-advanced-workflows.md) for clustering, joins, and filtering patterns.

## Integration Examples

USearch is integrated into major databases and frameworks:

- **ClickHouse**: Vector search indexes via MergeTree engine
- **DuckDB**: Vector similarity search (VSS) extension
- **LangChain**: Vector store implementation
- **Sentence-Transformers**: Quantization and semantic search
- **ScyllaDB**: Rust-based vector store
- **TiDB/TiFlash**: C++ integration for vector indexes

For application examples including molecular search (RDKit), geospatial indexing, and multimodal search (UForm + UCall), see [Advanced Workflows](references/02-advanced-workflows.md).
