---
name: numkong-7-6-0
description: Ultra-fast mixed-precision vector similarity and distance library with
  2000+ SIMD kernels across x86, ARM, RISC-V. Supports Float64 through packed bits
  (1-bit), automatic precision widening, Kahan-compensated summation, packed GEMM-like
  matrix reuse, symmetric SYRK-like self-distance, sparse operations, geospatial metrics,
  probability divergences, mesh alignment, and MaxSim late-interaction scoring. Use
  when computing dot products, angular/euclidean distances, binary similarity, KL/Jensen-Shannon
  divergences, Vincenty/haversine geospatial distances, Mahalanobis/bilinear curved-space
  metrics, Kabsch/Umeyama mesh alignment, packed matrix multiplication for repeated
  queries, or any vector math needing sub-byte precision (fp8, fp6, int4, bits) with
  zero hidden allocations or thread pools.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: 7.6.0
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

NumKong is an ultra-fast mixed-precision vector similarity and distance library with 2,000+ SIMD kernels across x86, ARM, RISC-V, LoongArch, WebAssembly, and PowerPC. It supports 17 numeric types from Float64 down to packed binary (1-bit), with automatic precision widening, Kahan-compensated summation, packed GEMM-like matrix reuse, symmetric SYRK-like self-distance, sparse operations, geospatial metrics, probability divergences, mesh alignment, and MaxSim late-interaction scoring.

The library ships as a ~5 MB binary with zero hidden allocations and no internal thread pools. Every kernel is validated against 118-bit extended-precision baselines with per-type ULP budgets across log-normal, uniform, and Cauchy input distributions. Results are cross-validated against OpenBLAS, Intel MKL, and Apple Accelerate.

A broader throughput comparison is maintained in [NumWars](https://github.com/ashvardanian/NumWars).

## When to Use

- Computing dot products, angular distances, or Euclidean distances on vectors of any precision from Float64 down to 1-bit packed binary
- Building vector search pipelines that need sub-byte precision (BFloat16, Float8 E4M3/E5M2, Float6 E2M3/E3M2, Int4) without GPU-dependent libraries
- Reusing a static database matrix across many query batches via the packed API (`dots_pack` → `dots_packed`)
- Computing self-similarity or self-distance matrices efficiently with symmetric kernels (`dots_symmetric`, `angulars_symmetric`)
- Performing ColBERT-style late-interaction retrieval scoring with `maxsim_packed`
- Computing Kullback-Leibler divergence, Jensen-Shannon distance, Mahalanobis distance, bilinear forms, Vincenty/haversine geospatial distances, or Kabsch/Umeyama mesh alignment
- Working in environments where thread pool ownership matters (embedded, real-time, NUMA-aware systems)
- Needing GIL-free Python kernels for `concurrent.futures` parallelism
- Replacing NumPy/SciPy/PyTorch vector operations with SIMD-optimized alternatives on CPU

## Core Concepts

### Numeric Types

NumKong supports 17 input types across floating-point, integer, binary, and complex categories:

**Floating-point:** Float64 (`f64`), Float32 (`f32`), BFloat16 (`bf16`), Float16 (`f16`), Float8 E5M2 (`e5m2`), Float8 E4M3 (`e4m3`), Float6 E3M2 (`e3m2`), Float6 E2M3 (`e2m3`)

**Integer:** Signed/unsigned Int8 (`i8`, `u8`), signed/unsigned Int4 (`i4`, `u4`)

**Binary:** Packed bits (`u1`) — 8 binary values per byte

**Complex:** Float64 complex (`f64c`), Float32 complex (`f32c`), BFloat16 complex (`bf16c`), Float16 complex (`f16c`)

### Widening Accumulation

NumKong never forces same-dtype accumulation. Low-precision inputs automatically widen to higher-precision accumulators:

- `f32` input → `f64` accumulation, `f32` output (avoids catastrophic cancellation)
- `bf16` / `f16` input → `f32` accumulation
- `e5m2` / `e4m3` input → `bf16` → `f32` accumulation on modern CPUs
- `e3m2` / `e2m3` input → integer accumulation via lookup tables (exact, no rounding)
- `i8` / `u8` input → `i32` / `u32` accumulation
- `i4` / `u4` input → `i32` / `u32` accumulation

### Compensated Summation

Float64 uses Neumaier compensated summation on serial paths and the Dot2 algorithm (Ogita-Rump-Oishi) on SIMD paths with FMA support. This achieves O(1) error growth instead of O(n), reducing numerical error by 10-50x compared to naive Float64 accumulation.

### No Hidden Allocations or Threads

NumKong never allocates memory internally and never spawns threads. The caller owns all buffers and manages parallelism. This avoids the thread oversubscription problems of OpenBLAS/MKL (where each library spawns its own pool inside your application's workers) and the hidden allocation issues that cause deadlocks after `fork()`.

### Python API Design

The Python SDK bridges the gap between NumPy and low-level native kernels. It provides:

- Buffer-protocol interoperability with NumPy, PyTorch, and other libraries (zero-copy)
- Shape-aware outputs with familiar scalar, batched, and all-pairs entrypoints
- `Tensor` objects for strided views, transpose, reshape, and axis reductions
- GIL release around dense metric calls, packed kernels, and symmetric kernels
- `out=`, `dtype=`, and `out_dtype=` parameters to avoid temporary allocations
- Direct `ml_dtypes` array support without `.view(np.uint8)` workarounds

## Installation / Setup

### Python

```bash
pip install numkong
```

Pre-built wheels available for Linux (x86_64, aarch64, riscv64, i686, ppc64le, s390x), macOS (x86_64, arm64), and Windows (AMD64, ARM64). Python 3.9 through 3.14 supported, including free-threading variants (3.13t, 3.14t).

Quick runtime check:

```python
import numkong as nk
print(nk.get_capabilities())
```

### C / C++

CMake with headers and prebuilt binaries. Supports Linux, macOS, Windows, Android.
See [include/README.md](https://github.com/ashvardanian/NumKong/blob/main/include/README.md) in the repository.

### Rust

```bash
cargo add numkong
```

Supports Linux, macOS, Windows. See [rust/README.md](https://github.com/ashvardanian/NumKong/blob/main/rust/README.md).

### JavaScript

```bash
npm install numkong
```

Supports Node.js, Bun, Deno, and browsers. See [javascript/README.md](https://github.com/ashvardanian/NumKong/blob/main/javascript/README.md).

### Swift / Go

Swift via Swift Package Manager (macOS, iOS, tvOS, watchOS). Go via `go get` (Linux, macOS, Windows via cgo).

## Usage Examples

### Basic Dot Product (Python)

```python
import numpy as np
import numkong as nk

a = np.random.randn(768).astype(np.float32)
b = np.random.randn(768).astype(np.float32)
result = nk.dot(a, b)  # widened accumulation to f64, not same-dtype
```

### Spatial Distances

```python
a = np.random.randn(768).astype(np.float16)
b = np.random.randn(768).astype(np.float16)

sqeuclidean = nk.sqeuclidean(a, b)
euclidean   = nk.euclidean(a, b)
angular     = nk.angular(a, b)  # cosine distance
```

### Packed Matrix Reuse (GEMM-like)

Pack the database once, query many times:

```python
queries  = np.random.randn(128, 768).astype(np.float32)
database = np.random.randn(10_000, 768).astype(np.float32)

packed = nk.dots_pack(database, dtype="float32")   # pack once
scores = nk.dots_packed(queries, packed)            # reuse many times
# equivalent to queries @ database.T
```

### Symmetric Self-Distance (SYRK-like)

```python
vectors = np.random.randn(1024, 768).astype(np.float32)
out = nk.zeros((1024, 1024), dtype="float64")
nk.dots_symmetric(vectors, out=out)  # skips duplicate (i,j) and (j,i) pairs
```

### Parallel Packed Kernels with GIL Release

```python
import concurrent.futures
import numpy as np
import numkong as nk

left   = np.random.randn(4096, 768).astype(np.float32)
right  = np.random.randn(8192, 768).astype(np.float32)
packed = nk.dots_pack(right, dtype="float32")
out    = nk.zeros((4096, 8192), dtype="float64")

def chunk(start, end):
    nk.dots_packed(left, packed, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for s in range(0, 4096, 1024):
        pool.submit(chunk, s, min(s + 1024, 4096))
```

### Probability Divergences

```python
p = np.array([0.2, 0.3, 0.5], dtype=np.float32)
q = np.array([0.1, 0.3, 0.6], dtype=np.float32)

kl_fwd = nk.kullbackleibler(p, q)   # asymmetric
kl_rev = nk.kullbackleibler(q, p)
jsd    = nk.jensenshannon(p, q)     # symmetric
```

### Geospatial Distances

```python
# Statue of Liberty → Big Ben (inputs in radians, output in meters)
liberty_lat  = np.array([0.7101605100], dtype=np.float64)
liberty_lon  = np.array([-1.2923203180], dtype=np.float64)
big_ben_lat  = np.array([0.8988567821], dtype=np.float64)
big_ben_lon  = np.array([-0.0021746802], dtype=np.float64)

vincenty  = nk.vincenty(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)   # ~5,589,857 m
haversine = nk.haversine(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)  # ~5,543,723 m
```

### MaxSim for ColBERT-Style Late Interaction

```python
queries   = np.random.randn(32, 128).astype(np.float32)
documents = np.random.randn(192, 128).astype(np.float32)

q_packed = nk.maxsim_pack(queries, dtype="float32")
d_packed = nk.maxsim_pack(documents, dtype="float32")
score    = nk.maxsim_packed(q_packed, d_packed)  # no intermediate matrix
```

### Mesh Alignment (Kabsch / Umeyama)

```python
source = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=np.float32)
target = source * 2.0

result = nk.umeyama(source, target)
# result.rotation: (3,3) matrix
# result.scale: ~2.0
# result.rmsd: near zero for exact alignment
```

### Tensor Views and External Memory

```python
import numpy as np
import numkong as nk

t = nk.Tensor(np.arange(12, dtype=np.float32).reshape(3, 4))
row0 = t[0, :]           # first row
col2 = t[:, 2]           # third column (strided view)
val  = t[1, 2]           # scalar: 6.0

# Zero-copy from pointer
addr = t.data_ptr
view = nk.from_pointer(addr, (3, 4), 'float32', owner=t)
```

## Advanced Topics

**Numeric Types and Precision**: Float64 through packed binary, widening rules, compensated summation, mini-floats → See [Numeric Types](reference/01-numeric-types.md)

**Vector Operations (Dot, Spatial, Set)**: Single-pair dot products, distances, and binary similarity → See [Vector Operations](reference/02-vector-operations.md)

**Matrix Operations (Packed & Symmetric)**: GEMM-like packed reuse, SYRK-like symmetric kernels, MaxSim → See [Matrix Operations](reference/03-matrix-operations.md)

**Specialized Metrics**: Probability divergences, geospatial, curved-space, mesh alignment, sparse → See [Specialized Metrics](reference/04-specialized-metrics.md)

**Python SDK Deep Dive**: Tensor objects, buffer protocol, ml_dtypes interop, memory layout rules → See [Python SDK](reference/05-python-sdk.md)

**Performance and Architecture**: ISA dispatch, SIMD backends, AMX/SME tile kernels, Ozaki F64 scheme → See [Performance & Architecture](reference/06-performance-architecture.md)
