---
name: numkong-7-6-0
description: Ultra-fast mixed-precision vector similarity and distance library with 2000+ SIMD kernels across x86, ARM, RISC-V. Supports Float64 through packed bits (1-bit), automatic precision widening, Kahan-compensated summation, packed GEMM-like matrix reuse, symmetric SYRK-like self-distance, sparse operations, geospatial metrics, probability divergences, mesh alignment, and MaxSim late-interaction scoring. Use when computing dot products, angular/euclidean distances, binary similarity, KL/Jensen-Shannon divergences, Vincenty/haversine geospatial distances, Mahalanobis/bilinear curved-space metrics, Kabsch/Umeyama mesh alignment, packed matrix multiplication for repeated queries, or any vector math needing sub-byte precision (fp8, fp6, int4, bits) with zero hidden allocations or thread pools.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - vector-similarity
  - simd
  - mixed-precision
  - dot-product
  - distance-metrics
  - packed-matrix
category: numerical-computing
external_references:
  - https://pypi.org/project/numkong/
  - https://github.com/ashvardanian/NumWars
  - https://ashvardanian.com/posts/numkong/
  - https://github.com/ashvardanian/NumKong
---

# NumKong 7.6.0

## Overview

NumKong is an ultra-fast mixed-precision vector similarity and distance library with 2,000+ SIMD kernels across x86 (AVX-512, AMX), ARM (NEON, SME, SVE), RISC-V (RVV), WebAssembly, LoongArch, and PowerPC. It covers 17 numeric types — from 6-bit floats to 64-bit complex numbers — with automatic precision widening, compensated summation, zero hidden allocations, and no internal thread pools.

The library ships as a ~5 MB binary (vs 30–705 MB for NumPy/PyTorch/JAX) with 7 language bindings: C/C++, Python, Rust, JavaScript, Swift, Go, and direct FFI. It is the successor to SimSIMD, maintaining the same design philosophy: caller-owned memory, explicit parallelism, and hardware-aware defaults (Arm prioritizes f16, x86 prioritizes bf16).

## When to Use

- Vector search and nearest-neighbor computation with mixed precision (bf16, fp8, fp6, int4, binary)
- LLM inference where frozen weights benefit from pack-once/reuse-many packed matrix kernels
- ColBERT-style late-interaction retrieval using MaxSim scoring
- Geospatial distance calculation (Vincenty ellipsoidal, Haversine spherical)
- Probability distribution comparison (KL divergence, Jensen-Shannon distance)
- 3D point cloud alignment (Kabsch rotation, Umeyama with scaling, RMSD)
- Sparse vector operations (sorted-index intersection, weighted sparse dot products)
- Curved-space metrics (Mahalanobis distance, bilinear forms for quantum computing)
- Any workload needing SIMD-accelerated vector math without hidden thread pools or allocations

## Core Concepts

### Mixed Precision with Automatic Widening

NumKong never forces output type to match storage type. Float32 inputs accumulate in Float64. Int8 inputs accumulate in Int32. BFloat16 and Float16 widen to Float32. This prevents overflow and catastrophic cancellation at the kernel level — the widening policy is part of the kernel contract, not an afterthought.

### No Hidden Threads or Allocations

NumKong does not own a thread pool and never calls malloc during computation. Parallelism is host-controlled: partition work across row ranges and dispatch through `concurrent.futures`, ForkUnion, OpenMP, or any external scheduler. The GIL is released around dense metric calls and packed/symmetric matrix kernels in Python.

### Packed Matrix Reuse

For GEMM-shaped workloads where the right-hand side is static (LLM weights, vector search databases), pack once with `dots_pack()` and reuse across many query batches. Packing performs type pre-conversion, SIMD depth padding, per-column norm precomputation, and ISA-specific tile layout — all amortized over repeated queries.

### Symmetric Self-Distance

For SYRK-shaped workloads computing self-similarity matrices, symmetric kernels skip duplicate `(i, j)` and `(j, i)` evaluations — up to 2x speedup for self-distance. Partitioned by output row windows via `start_row`/`end_row`.

### Runtime SIMD Dispatch

NumKong provides compile-time dispatch (thinner binaries, no indirection) and run-time dispatch (`nk_capabilities()` picks the best kernel on target hardware). Distributed artifacts use `NK_DYNAMIC_DISPATCH=1` by default so a single binary runs across CPU generations within an architecture.

## Installation / Setup

### Python

```python
# Pre-built wheels: Linux (x86_64, aarch64, riscv64, i686, ppc64le, s390x)
# macOS (x86_64, arm64), Windows (AMD64, ARM64)
# Python 3.9 through 3.14, including free-threading variants (3.13t, 3.14t)
import numkong as nk
print(nk.get_capabilities())
```

### C/C++

```cmake
# CMake FetchContent
include(FetchContent)
FetchContent_Declare(numkong
    GIT_REPOSITORY https://github.com/ashvardanian/NumKong.git
    GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(numkong)
target_link_libraries(my_target PRIVATE numkong)
```

```c
// C ABI — stable, versioned, callable from any FFI
#include <numkong/numkong.h>
nk_configure_thread(nk_capabilities());
nk_dot_f32(a, b, 1536, &dot_result);
```

### Other Languages

- **Rust**: `cargo add numkong`
- **JavaScript**: `npm install numkong` (Node.js, Bun, Deno, browsers)
- **Swift**: Swift Package Manager (macOS, iOS, tvOS, watchOS)
- **Go**: `go get` via cgo (Linux, macOS, Windows)

### Build Options

- `NK_DYNAMIC_DISPATCH=1` — compile all backends, select at runtime (default for distributed artifacts)
- `NK_MARCH_NATIVE` — host-tuned local build override
- `NK_BUILD_PARALLEL` — build parallelism, defaults to `min(cpu_count, 4)`
- `NK_BUILD_TEST` / `NK_BUILD_BENCH` — enable precision tests and benchmarks
- Cross-compilation toolchains in `cmake/` for aarch64, riscv64, Android, WASM

## Usage Examples

### Dot Products with Widened Accumulation

```python
import numpy as np
import numkong as nk

a = np.random.randn(1536).astype(np.float32)
b = np.random.randn(1536).astype(np.float32)
dot = nk.dot(a, b)  # f32 inputs → f64 output (widened accumulation)
```

### Spatial Distances

```python
a = np.random.randn(768).astype(np.float16)
b = np.random.randn(768).astype(np.float16)

sqeuclidean = nk.sqeuclidean(a, b)
euclidean = nk.euclidean(a, b)
angular = nk.angular(a, b)  # f16 inputs → f32 output
```

### Packed Matrix for Repeated Queries

```python
left = np.random.randn(128, 768).astype(np.float32)
right = np.random.randn(10_000, 768).astype(np.float32)

right_packed = nk.dots_pack(right, dtype="float32")  # pack once
scores = nk.dots_packed(left, right_packed)           # reuse many times
# equivalent to left @ right.T
```

### Symmetric Self-Distance with Threading

```python
import concurrent.futures

vectors = np.random.randn(4096, 768).astype(np.float32)
out = nk.zeros((4096, 4096), dtype="float64")

def chunk(start, end):
    nk.dots_symmetric(vectors, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for s in range(0, 4096, 1024):
        pool.submit(chunk, s, min(s + 1024, 4096))
```

### MaxSim Late-Interaction Scoring

```python
queries = np.random.randn(32, 128).astype(np.float32)
documents = np.random.randn(192, 128).astype(np.float32)

q = nk.maxsim_pack(queries, dtype="float32")
d = nk.maxsim_pack(documents, dtype="float32")
score = nk.maxsim_packed(q, d)
```

## Advanced Topics

**Numeric Types and Precision**: Float64 through packed bits, promotion rules, compensated summation → See [Numeric Types](reference/01-numeric-types.md)

**Operation Families**: Dot products, spatial distances, set similarity, probability divergences, geospatial, curved metrics, mesh alignment, sparse operations, MaxSim → See [Operation Families](reference/02-operation-families.md)

**Packed and Symmetric Kernels**: GEMM-like packed matrix reuse, SYRK-like symmetric self-distance, memory layout rules → See [Packed and Symmetric Kernels](reference/03-packed-symmetric-kernels.md)

**C/C++ API and Containers**: Native ABI, typed C++ wrappers, tensor views, allocators, dispatch → See [C/C++ API Reference](reference/04-cpp-api-reference.md)

**Python API Details**: Tensor objects, buffer protocol, ml_dtypes interop, cdist, elementwise ops, moments, external memory → See [Python API Reference](reference/05-python-api-reference.md)

**SIMD Backends and Optimizations**: ISA-specific kernels (AVX-512, AMX, NEON, SME, RVV, WASM), algorithmic techniques → See [SIMD Backends](reference/06-simd-backends.md)
