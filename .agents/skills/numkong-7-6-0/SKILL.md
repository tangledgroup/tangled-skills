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
## Overview
NumKong is an ultra-fast mixed-precision vector similarity and distance library with 2,000+ SIMD kernels spanning x86 (Haswell through Sapphire Rapids AMX), ARM (NEON through SME), and RISC-V (RVV). It covers 17 numeric types from packed binary bits to 64-bit complex numbers, with automatic precision widening, Kahan-compensated summation, and zero hidden allocations or thread pools.

Available for C/C++, Python, Rust, JavaScript/TypeScript, Swift, Go, with pre-built wheels/packages on PyPI, npm, and crates.io.

## When to Use
- Computing dot products, angular distance, or euclidean distance with mixed precision
- Vector search workloads requiring packed matrix reuse (pack once, query many times)
- Self-similarity matrices where symmetric kernels avoid duplicate pair computation
- Low-precision storage: BFloat16, Float16, Float8 (E4M3/E5M2), Float6 (E2M3/E3M2), Int4, packed bits
- Probability divergences: KL divergence, Jensen-Shannon divergence
- Geospatial distance: Vincenty (ellipsoidal) and haversine (spherical)
- Curved-space metrics: Mahalanobis distance, bilinear forms
- Binary similarity: Hamming distance, Jaccard similarity on packed bits
- Sparse vector operations: sorted-index intersection, weighted sparse dot products
- Geometric mesh alignment: Kabsch and Umeyama algorithms
- MaxSim late-interaction scoring (ColBERT-style retrieval)

## Core Concepts
### No Hidden Threads or Allocations

NumKong never spawns threads, never allocates memory internally, and never throws exceptions. The caller owns all buffers and controls parallelism through explicit row-range partitioning. This avoids thread oversubscription with external schedulers and hidden allocation overhead.

### Automatic Precision Widening

Storage type and output type are independent. Float32 dot products accumulate in Float64. Int8 dot products accumulate in Int32. The widening policy is encoded per scalar type and per operation family.

### Packed Matrix Reuse

For GEMM-like workloads where the right-hand side matrix is reused across many query batches, pack it once with `dots_pack()` / `nk_dots_pack_*`, then reuse against any number of left operands. Packing includes type pre-conversion, SIMD depth padding, per-column norm precomputation, and ISA-specific tile layout.

### Symmetric Self-Distance

For self-similarity or self-distance matrices, symmetric kernels (`dots_symmetric`, `angulars_symmetric`, `euclideans_symmetric`) skip duplicate (i,j) and (j,i) pairs, cutting pair count nearly in half with explicit row-range partitioning for parallel execution.

## Installation / Setup
### Python

```bash
pip install numkong
```

Pre-built wheels for Linux (x86_64, aarch64, riscv64, i686, ppc64le, s390x), macOS (x86_64, arm64), and Windows (AMD64, ARM64). Python 3.9 through 3.14 supported, including free-threading variants (3.13t, 3.14t).

```python
import numkong as nk
print(nk.get_capabilities())
```

### C/C++ (CMake)

```cmake
include(FetchContent)
FetchContent_Declare(
    numkong
    GIT_REPOSITORY https://github.com/ashvardanian/NumKong.git
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(numkong)
target_link_libraries(my_target PRIVATE numkong)
```

### Rust

```toml
[dependencies]
numkong = "7"
# With parallel helpers:
# numkong = { version = "7", features = ["parallel", "std"] }
```

### JavaScript/TypeScript

```bash
npm install numkong
```

Node.js >= 22, Bun, Deno supported. WASM bundle included for browser use without native addon.

## Usage Examples
### Dot Products (Python)

```python
import numpy as np
import numkong as nk

a = np.random.randn(1536).astype(np.float32)
b = np.random.randn(1536).astype(np.float32)
dot = nk.dot(a, b)  # widened f32→f64 accumulation
```

### Dense Distances (Python)

```python
a = np.random.randn(768).astype(np.float16)
b = np.random.randn(768).astype(np.float16)

sqeuclidean = nk.sqeuclidean(a, b)
euclidean = nk.euclidean(a, b)
angular = nk.angular(a, b)
```

### All-Pairs with cdist (Python)

```python
queries = np.random.randn(100, 768).astype(np.float32)
database = np.random.randn(10_000, 768).astype(np.float32)
all_pairs = nk.cdist(queries, database, metric="angular")
```

### Packed Matrix Reuse (Python)

```python
left = np.random.randn(128, 768).astype(np.float32)
right = np.random.randn(10_000, 768).astype(np.float32)

right_packed = nk.dots_pack(right, dtype="float32")   # pack once
scores = nk.dots_packed(left, right_packed)           # reuse many times
```

### Symmetric Self-Distance (Python)

```python
vectors = np.random.randn(1024, 768).astype(np.float32)
out = nk.zeros((1024, 1024), dtype="float64")
nk.dots_symmetric(vectors, out=out)
```

### Parallel Execution (Python)

```python
import concurrent.futures
import numpy as np
import numkong as nk

left = np.random.randn(4096, 768).astype(np.float32)
right = np.random.randn(8192, 768).astype(np.float32)
packed = nk.dots_pack(right, dtype="float32")
out = nk.zeros((4096, 8192), dtype="float64")

def packed_chunk(start, end):
    nk.dots_packed(left, packed, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for start in range(0, 4096, 1024):
        pool.submit(packed_chunk, start, min(start + 1024, 4096))
```

### C API

```c
#include <numkong/numkong.h>

nk_f32_t a[] = {1, 2, 3};
nk_f32_t b[] = {4, 5, 6};
nk_f64_t dot = 0;
nk_configure_thread(nk_capabilities());
nk_dot_f32(a, b, 3, &dot);  // widened f32→f64 output
```

### Rust API

```rust
use numkong::{configure_thread, Dot};

fn main() {
    configure_thread();
    let a = [1.0_f32, 2.0, 3.0];
    let b = [4.0_f32, 5.0, 6.0];
    let dot = f32::dot(&a, &b).unwrap();
}
```

### JavaScript API

```javascript
import { dot, euclidean, angular } from "numkong";

const a = new Float32Array([1, 2, 3]);
const b = new Float32Array([4, 5, 6]);
console.log(dot(a, b));          // 32
console.log(euclidean(a, b));    // 5.196...
console.log(angular(a, b));      // cosine distance
```

## Advanced Topics
## Advanced Topics

- [Numeric Types](reference/01-numeric-types.md)
- [Operation Families](reference/02-operation-families.md)
- [Simd Backends](reference/03-simd-backends.md)
- [Memory Layout](reference/04-memory-layout.md)
- [Language Bindings](reference/05-language-bindings.md)

