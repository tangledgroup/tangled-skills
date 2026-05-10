---
name: usearch-2-24-0
description: High-performance single-file similarity search and clustering engine for vectors supporting HNSW algorithm with user-defined metrics, quantization, and multi-language bindings including Python, C++, Rust, JavaScript, Java, Go, and more. Use when building vector search applications, implementing approximate nearest neighbors (ANN) search, performing semantic search, molecular similarity matching, geospatial indexing, or requiring faster alternatives to FAISS with custom distance functions.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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
external_references:
  - https://github.com/unum-cloud/usearch
---

# USearch 2.24

## Overview

USearch is a smaller and faster single-file similarity search and clustering engine for vectors. It implements the HNSW (Hierarchical Navigable Small World) algorithm with SIMD-optimized distance kernels from [NumKong](https://github.com/ashvardanian/numkong), supporting over 100 distance functions across x86 and ARM architectures.

Key characteristics:
- **Single-header C++11 library** — ~3 K SLOC vs FAISS's 84 K SLOC
- **10x faster indexing** than FAISS on large datasets
- **10 language bindings** — Python, C++, Rust, JavaScript, Java, Go, C, Swift, C#, Objective-C, Wolfram
- **No required dependencies** — unlike FAISS which needs BLAS and OpenMP
- **User-defined metrics** with JIT compilation support
- **Hardware-agnostic quantization** — `f64`, `f32`, `bf16`, `f16`, `e5m2`, `e4m3`, `e3m2`, `e2m3`, `u8`, `i8`, `b1`
- **Disk-based serving** — view large indexes from disk without loading into RAM (up to 20x cost reduction on AWS)
- **40-bit key support** — address 4B+ vectors with 37.5% less memory than 64-bit keys
- **Thread-safe** concurrent index construction and search

Trusted by ClickHouse, DuckDB, ScyllaDB, TiDB, YugaByte, MemGraph, Google (UniSim), LangChain, Microsoft Semantic Kernel, and others.

## When to Use

- Building semantic search applications with embedding vectors
- Implementing approximate nearest neighbors (ANN) search at scale
- Replacing FAISS with a lighter, faster alternative
- Needing custom distance functions beyond cosine and L2
- Performing molecular similarity matching with binary fingerprints (Tanimoto/Sorensen)
- Geospatial indexing with Haversine or Vincenty distance
- Clustering large vector datasets without standalone libraries
- Memory-constrained deployments requiring quantization (`bf16`, `i8`, `b1`)
- Serving indexes from disk to reduce RAM costs

## Core Concepts

### HNSW Algorithm

USearch uses Hierarchical Navigable Small World graphs for approximate nearest neighbor search. The graph has multiple layers — higher layers enable long-range navigation, lower layers provide fine-grained local search. Key parameters control the trade-off between index quality and speed:

- **`connectivity`** — number of neighbors per graph node (default auto-tuned)
- **`expansion_add`** — controls indexing recall (higher = better recall, slower build)
- **`expansion_search`** — controls search quality (higher = better results, slower query)

### Index Types

- **Dense index** (`index_dense_t`) — standard HNSW for most use cases
- **Big index** (`index_dense_big_t`) — uses `uint40_t` for 4B+ entries
- **Multi-index** — multiple vectors per key (for chunked documents)
- **Indexes** (Python) — view multiple indexes together for parallel multi-index lookups

### Quantization

USearch automatically casts between input type and storage type. Recommended defaults:
- `bf16` — recommended for modern CPUs
- `f32` — default NumPy type, maximum compatibility
- `i8` — for cosine-like metrics only (vectors normalized to [-127, 127])
- `b1` — for binary metrics (Tanimoto, Hamming, Sorensen)

## Advanced Topics

**Python Bindings**: Complete Python API with NumPy integration, batch operations, and JIT metrics → [Python Bindings](reference/01-python-bindings.md)

**C++ API**: Core C++11 interface with templates, executors, and low-level control → [C++ API](reference/02-cpp-api.md)

**Rust Bindings**: Rust SDK with native types, filtering predicates, and SIMD features → [Rust Bindings](reference/03-rust-bindings.md)

**JavaScript Bindings**: Node.js and WASM support with BigInt keys → [JavaScript Bindings](reference/04-javascript-bindings.md)

**Other Languages**: Go, Java, C, Swift, C#, and more → [Other Languages](reference/05-other-languages.md)

**Metrics and Quantization**: Built-in metrics, user-defined metrics with JIT, scalar types → [Metrics and Quantization](reference/06-metrics-and-quantization.md)

**Advanced Topics**: Clustering, joins, exact search, multi-index, serialization → [Advanced Topics](reference/07-advanced-topics.md)
