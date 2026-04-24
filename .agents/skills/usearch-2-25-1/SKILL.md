---
name: usearch-2-25-1
description: High-performance single-file similarity search and clustering engine for vectors using HNSW algorithm with user-defined metrics, quantization, and multi-language bindings (Python, C++, Rust, JavaScript, Java, Go, C, Swift, C#, Wolfram). Use when building vector search applications, implementing approximate nearest neighbors (ANN) search, performing semantic search, molecular similarity matching, geospatial indexing, or requiring faster alternatives to FAISS with custom distance functions.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - vector-search
  - ann
  - hnsw
  - similarity-search
  - clustering
category: machine-learning
external_references:
  - https://github.com/unum-cloud/usearch
  - https://github.com/unum-cloud/USearch/tree/main/docs
---

# USearch 2.25.1

## Overview

USearch is a smaller and faster single-file similarity search and clustering engine for vectors. It provides up to 10x faster HNSW implementation than FAISS, with a compact codebase (~3K SLOC vs FAISS's ~84K SLOC), no required dependencies, native bindings in 10+ languages, and support for user-defined metrics with JIT compilation.

Key features:
- SIMD-optimized distance kernels via NumKong (AVX2, AVX-512, ARM NEON, SVE)
- Hardware-agnostic quantization: `f64`, `f32`, `bf16`, `f16`, Float8 (`e5m2`, `e4m3`), Float6 (`e3m2`, `e2m3`), `i8`, `u8`, binary (`b1`)
- User-defined metrics with JIT compilation (Numba, Cppyy, PeachPy in Python)
- Disk-based index viewing without loading into RAM (up to 20x cost reduction)
- Binary Tanimoto and Sorensen coefficients for genomics and chemistry
- Space-efficient `uint40_t` keys (4B+ entries, 37.5% smaller than 64-bit)
- Concurrent index construction (thread-safe `add`)
- Built-in clustering and sub-clustering
- SQLite extensions for vector search in SQL

## When to Use

Use this skill when:
- Building approximate nearest neighbors (ANN) search systems
- Implementing semantic search with custom distance metrics
- Needing faster indexing than FAISS (up to 10x improvement)
- Working with binary fingerprints (molecular search, genomics)
- Performing geospatial queries with Haversine or Vincenty distances
- Building clustering pipelines on large vector datasets
- Integrating vector search into SQLite databases
- Needing lightweight deployment (< 1MB Python wheel vs FAISS ~10MB)

## Core Concepts

### HNSW Algorithm

USearch uses Hierarchical Navigable Small World (HNSW) graphs for approximate nearest neighbor search. The index builds a multi-layer proximity graph where higher layers provide long-range connections and lower layers provide fine-grained locality.

### Key Parameters

- `ndim` / `dimensions`: Number of vector dimensions
- `metric`: Distance function (`cos`, `l2sq`, `ip`, `haversine`, `tanimoto`, etc.)
- `dtype` / `quantization`: Storage precision (`f32`, `bf16`, `f16`, `i8`, `b1`, etc.)
- `connectivity`: Neighbors per graph node (default auto)
- `expansion_add`: Controls indexing recall (higher = better quality, slower build)
- `expansion_search`: Controls search quality (higher = better recall, slower search)

### Metrics

Built-in metrics include: Cosine, Inner Product, L2 Squared, Pearson, Haversine, Jensen-Shannon Divergence, Hamming, Tanimoto (Jaccard), Sorensen (Dice). Custom metrics can be defined via JIT compilation.

## Installation

**Python:** `pip install usearch`
**Rust:** `cargo add usearch`
**JavaScript/Node.js:** `npm install usearch`
**C++:** Copy `include/usearch/*` headers or use CMake FetchContent
**Java:** Download fat JAR from GitHub releases (Gradle setup)
**Go:** `go get github.com/unum-cloud/usearch/golang` (requires native library)
**C:** Include `usearch.h` header (single-file C99)

## Quickstart Examples

### Python

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

### Rust

```rust
use usearch::{Index, IndexOptions, MetricKind, ScalarKind, new_index};

let options = IndexOptions {
    dimensions: 3,
    metric: MetricKind::Cos,
    quantization: ScalarKind::BF16,
    ..Default::default()
};
let index: Index = new_index(&options).unwrap();

let vector: [f32; 3] = [0.2, 0.1, 0.2];
index.add(42, &vector).unwrap();
let results = index.search(&vector, 10).unwrap();
```

### JavaScript (Node.js)

```js
const usearch = require('usearch');
const index = new usearch.Index({ dimensions: 3, metric: 'l2sq' });
index.add(42n, new Float32Array([0.2, 0.6, 0.4]));
const results = index.search(new Float32Array([0.2, 0.6, 0.4]), 10);
```

## Serialization

All bindings support save, load, and view (memory-mapped disk access):

```python
index.save('index.usearch')
index.load('index.usearch')   # Full copy into memory
index.view('index.usearch')   # Memory-map, no RAM load
```

## Advanced Topics

- [Reference: Quantization & Precision](references/01-quantization.md)
- [Reference: User-Defined Metrics & JIT](references/02-custom-metrics.md)
- [Reference: Filtering, Clustering & Joins](references/03-filtering-clustering.md)
- [Reference: Multi-Language Bindings](references/04-bindings.md)
- [Reference: SQLite Extensions](references/05-sqlite.md)
- [Case Study: Semantic Joins via Stable Marriages](references/06-case-semantic-joins.md) — Use when matching two datasets with one-to-one or many-to-many fuzzy mappings (job matching, advertising, content recommendation, dating apps)
- [Case Study: Molecular Search at Scale](references/07-case-molecular-search.md) — Use when searching similar molecules by structure, working with binary fingerprints (genomics, cheminformatics), or building drug discovery pipelines
- [Case Study: FP8 Search & KV-Caching](references/08-case-fp8-kv-caching.md) — Use when building KV-cache-aware search for LLM inference, deploying on memory-constrained hardware, or targeting E5M2/E4M3 quantization (NumKong v7, 30+ backends, Giesen magic-number upcast)
- [Case Study: Scaling Vector Search with Intel](references/09-case-intel-scaling.md) — Use when benchmarking on Sapphire Rapids/Granite Rapids, migrating from FAISS for 10–100× speedup at 100M+ scale, or comparing CPU vs GPU vector search costs

## References

- GitHub repository: https://github.com/unum-cloud/usearch
- Documentation: https://unum-cloud.github.io/USearch/
- Python API: https://unum-cloud.github.io/USearch/python
- C++ API: https://unum-cloud.github.io/USearch/cpp
- Rust API: https://docs.rs/usearch/latest/usearch/
- NumKong (SIMD kernels): https://github.com/ashvardanian/numkong
- FAISS comparison benchmarks: https://www.unum.cloud/blog/2023-11-07-scaling-vector-search-with-intel
