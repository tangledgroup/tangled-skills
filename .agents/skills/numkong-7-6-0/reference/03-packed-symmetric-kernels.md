# Packed and Symmetric Kernels

## Packed Matrix Kernels (GEMM-Like)

Packed matrix kernels are the right tool when the right-hand side is reused across many query batches. This is the GEMM-like story — pack once, compute many times.

```python
import numpy as np
import numkong as nk

left = np.random.randn(128, 768).astype(np.float32)
right = np.random.randn(10_000, 768).astype(np.float32)

right_packed = nk.dots_pack(right, dtype="float32")  # pack once
scores = nk.dots_packed(left, right_packed)          # reuse many times
# equivalent to left @ right.T
```

Packing performs five transformations:

- **Type pre-conversion** — mini-floats upcast to compute type once during packing, not on every GEMM call
- **SIMD depth padding** — rows zero-padded to SIMD vector width (16 for AVX-512 Float32, 64 for AVX-512 Int8)
- **Per-column norm precomputation** — squared norms stored alongside packed data for `angulars_packed` and `euclideans_packed`
- **ISA-specific tile layout** — AMX packing interleaves BFloat16 pairs into 16×32 tiles; SME packing arranges vectors at SVE granularity
- **Power-of-2 stride breaking** — extra SIMD step of padding when padded row stride is power of 2, preventing cache set aliasing

### C API Three-Phase Interface

```c
// Phase 1: Query required buffer size
size_t packed_size = nk_dots_packed_size_f32(rows, cols);

// Phase 2: Pack into caller-owned buffer
void *packed_buffer = malloc(packed_size);
nk_dots_pack_f32(right_matrix, rows, cols, packed_buffer);

// Phase 3: Compute against many left operands
nk_dots_packed_f32(left_a, packed_buffer, out_a, ...);
nk_dots_packed_f32(left_b, packed_buffer, out_b, ...);  // reuse
```

### Memory Layout Requirements

- Left operand must be rank-2 with contiguous rows
- Negative strides rejected for matrix kernels
- `out` buffer (when provided) must be C-contiguous with expected dtype
- `start_row` and `end_row` split left operand rows for parallel partitioning
- Packed object owns its internal payload — caller-side alignment not required

### Parallel Partitioning for Packed Work

```python
import concurrent.futures

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

## Symmetric Kernels (SYRK-Like)

Symmetric kernels compute self-similarity or self-distance matrices without paying for both triangles independently. This is the SYRK-like story — one square output, partitioned by row windows.

```python
vectors = np.random.randn(1024, 768).astype(np.float32)
out = nk.zeros((1024, 1024), dtype="float64")

nk.dots_symmetric(vectors, out=out, start_row=0, end_row=256)
nk.dots_symmetric(vectors, out=out, start_row=256, end_row=512)
```

Available variants: `dots_symmetric`, `angulars_symmetric`, `euclideans_symmetric`.

### Key Differences from Packed Kernels

- Output is square and symmetric — avoids recomputing `(i, j)` and `(j, i)`
- Partitioned by output row windows, not distinct left batches against shared packed right
- `angulars_symmetric` and `euclideans_symmetric` benefit from dot-product-derived work reuse inside the symmetric sweep

### Parallel Partitioning for Symmetric Work

```python
import concurrent.futures

vectors = np.random.randn(4096, 768).astype(np.float32)
out = nk.zeros((4096, 4096), dtype="float64")

def symmetric_chunk(start, end):
    nk.dots_symmetric(vectors, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for start in range(0, 4096, 1024):
        pool.submit(symmetric_chunk, start, min(start + 1024, 4096))
```

## Why Not Just GEMM?

The classic BLAS GEMM computes `C = alpha * A @ B + beta * C` for Float32/Float64. NumKong goes beyond:

- **Frozen weights** — during LLM inference, weight matrices don't change after loading. Offline repacking is a one-time cost amortized over serving lifetime (NVIDIA TurboMind, Intel MKL packed GEMM API follow the same pattern)
- **Mixed precision sandwich** — transformer layers operate in BFloat16/Float8 with Float32 accumulation, then LayerNorm re-normalizes. Many "GEMM" workloads are semantically angular distance computation
- **GEMM-for-distances has costs** — the `||a-b||^2 = ||a||^2 + ||b||^2 - 2*<a,b>` decomposition suffers catastrophic cancellation (documented bug in scikit-learn with ~37% error on near-identical Float32 vectors). The O(N^2) postprocessing pass costs 20-25% of total time
- **Sub-byte types** — no vendor supports Int4 GEMM, and sub-byte types cannot be strided without bit-level repacking
- **Operations beyond GEMM + epilogue** — bilinear forms stream through rows with nested compensated dot products (no intermediate allocation); MaxSim fuses coarse screening with full-precision refinement

## All-Pairs APIs: cdist

`cdist` is the NumPy/SciPy-shaped all-pairs entrypoint for rectangular matrix pairs.

```python
queries = np.random.randn(100, 768).astype(np.float32)
database = np.random.randn(10_000, 768).astype(np.float32)

pairwise = nk.angular(queries, database[:100])             # (100, 100)
all_pairs = nk.cdist(queries, database, metric="angular")  # (100, 10_000)
```

Supported metrics: `"dot"`, `"angular"`, `"euclidean"`, `"sqeuclidean"`.
