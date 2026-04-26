# Matrix Operations

## Packed Matrix Kernels (GEMM-like)

Packed matrix kernels are the right tool when the right-hand side is reused across many query batches. This is the GEMM-like story.

### Basic Usage

```python
import numpy as np
import numkong as nk

left  = np.random.randn(128, 768).astype(np.float32)
right = np.random.randn(10_000, 768).astype(np.float32)

right_packed = nk.dots_pack(right, dtype="float32")  # pack once, reuse many times
scores = nk.dots_packed(left, right_packed)          # equivalent to left @ right.T

assert scores.shape == (128, 10_000)
```

### What Packing Does

`nk_dots_pack_*` performs five transformations beyond simple reordering:

1. **Type pre-conversion** — mini-floats (E4M3, BFloat16, etc.) are upcast to the compute type once during packing, not on every GEMM call. This amortizes the conversion cost across all rows of A that will be multiplied against the packed B.

2. **SIMD depth padding** — rows are zero-padded to the SIMD vector width (16 for AVX-512 Float32, 64 for AVX-512 Int8), allowing inner loops to load without boundary checks.

3. **Per-column norm precomputation** — squared norms (‖b_j‖²) are computed and stored alongside the packed data, so distance kernels (`angulars_packed`, `euclideans_packed`) can reuse them without a separate pass.

4. **ISA-specific tile layout** — AMX packing interleaves BFloat16 pairs into 16×32 tiles matching `TDPBF16PS` expectations; SME packing arranges vectors at SVE granularity for `FMOPA` outer products; generic backends use simple column-major with depth padding.

5. **Power-of-2 stride breaking** — when the padded row stride is a power of 2, one extra SIMD step of padding is added. Power-of-2 strides cause cache set aliasing where consecutive rows map to the same cache sets, effectively shrinking usable L1/L2 capacity — stride-256 traversals can be ~10x slower than stride-257.

### Packed Distance Kernels

Beyond `dots_packed`, NumKong provides distance-aware packed kernels that fuse the metric epilogue into the tile loop:

- `angulars_packed` — cosine similarity without a second pass over the output matrix
- `euclideans_packed` — L2 distances using pre-computed squared norms

```python
right_packed = nk.dots_pack(right, dtype="float32")
distances = nk.euclideans_packed(left, right_packed)  # fused norm handling
```

### Runtime Rules

- Left operand (`a`) must be rank-2 with contiguous rows
- Negative strides are rejected for these matrix kernels
- `out`, when provided, must be C-contiguous with the expected dtype
- `start_row` and `end_row` split the left operand rows for parallel partitioning

### Tensor @ PackedMatrix

`Tensor @ PackedMatrix` is also supported and maps to the same packed dot-product path.

## Symmetric Kernels (SYRK-like)

Symmetric kernels compute self-similarity or self-distance matrices. They solve a different problem from packed cross-matrix kernels — they avoid duplicate `(i, j)` and `(j, i)` evaluations, naturally partitioned by row windows of one square output.

### Basic Usage

```python
vectors = np.random.randn(1024, 768).astype(np.float32)
out = nk.zeros((1024, 1024), dtype="float64")

nk.dots_symmetric(vectors, out=out, start_row=0, end_row=256)
nk.dots_symmetric(vectors, out=out, start_row=256, end_row=512)
```

### Symmetric Distance Kernels

`angulars_symmetric` and `euclideans_symmetric` benefit from reuse of dot-product-derived work inside the symmetric sweep. These are faster than a nested Python loop over `angular(a[i], a[j])`.

### Parallel Partitioning Pattern

```python
import concurrent.futures
import numpy as np
import numkong as nk

vectors = np.random.randn(4096, 768).astype(np.float32)
out = nk.zeros((4096, 4096), dtype="float64")

def symmetric_chunk(start, end):
    nk.dots_symmetric(vectors, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for start in range(0, 4096, 1024):
        pool.submit(symmetric_chunk, start, min(start + 1024, 4096))
```

## MaxSim and Late Interaction

MaxSim is the late-interaction primitive used by systems such as ColBERT. It computes Σᵢ maxⱼ angular(qᵢ, dⱼ) — a sum-of-max-similarities across token pairs — without materializing the full M × N similarity matrix.

### Python API

```python
queries   = np.random.randn(32, 128).astype(np.float32)
documents = np.random.randn(192, 128).astype(np.float32)

q_packed = nk.maxsim_pack(queries, dtype="float32")
d_packed = nk.maxsim_pack(documents, dtype="float32")
score    = nk.maxsim_packed(q_packed, d_packed)

assert np.isfinite(score)
```

### How It Works

NumKong's typed `nk_maxsim_packed_*` kernels fuse a coarse Int8-quantized screening with full-precision angular refinement on winning pairs only, packing both query and document matrices to use all 4 SME tiles as accumulators. On Apple M4 at 2048³, NumPy's f32→f32 path reaches 129 gso/s while NumKong's BFloat16 path hits 428 gso/s — over 3x faster while using half the input memory and 4x less memory overall.

## Why Not Just GEMM?

The classical BLAS GEMM computes C = αAB + βC for Float32/Float64 matrices. NumKong goes beyond this in three ways:

### Frozen Weights Justify Separating Packing from Computation

During LLM inference, a very large share of GEMM calls use a static weight matrix. This makes offline repacking a one-time cost amortized over the entire serving lifetime. NumKong's `nk_dots_pack_*` → `nk_dots_packed_*` path follows this philosophy — pack the weight matrix once, reuse it across all queries.

### Mixed Precision Demands More Than an Epilogue Addition

Modern transformer layers operate in a precision sandwich: weights stored in BFloat16/Float8, GEMM accumulated in Float32, output downcast back to BFloat16. Between GEMM calls, LayerNorm or RMSNorm re-normalizes hidden states, so the next layer is often much closer to an angular or normalized similarity computation than a plain raw dot product.

### The GEMM-for-Distances Trick Has Real Costs

The common shortcut in vector search decomposes pairwise Euclidean distance as ‖a-b‖² = ‖a‖² + ‖b‖² - 2⟨a,b⟩, precomputes norms, and calls `sgemm` for the inner-product matrix. Both FAISS and scikit-learn use this approach — and both document its limitations. Scikit-learn's docs warn of "catastrophic cancellation" in the subtraction; this has caused real bugs with ~37% error on near-identical Float32 vectors. The O(N²) postprocessing pass is not free either — NVIDIA's RAFT measured a 20–25% speedup from fusing it into the GEMM epilogue.

NumKong treats these as first-class operations rather than decomposing everything into GEMM + postprocessing.

## Memory Layout Requirements

- **Dense distances** (`dot`, `euclidean`, etc.): Rows must be contiguous (`strides[last] <= itemsize`). Strided rows (sliced columns) are rejected. `out=` can have any stride along dim 0, but inner dim must be contiguous.

- **`cdist`**: Same as dense distances. `out=` must be rank-2 with shape `(a.count, b.count)`.

- **Elementwise** (`scale`, `blend`, `fma`): Arbitrary strides (strided views are supported). `out=` must match input shape; strides are preserved.

- **Packed matrix** (`dots_packed`): Left operand: rank-2, contiguous rows, no negative strides. Output: C-contiguous with expected dtype.

- **Symmetric** (`dots_symmetric`): Contiguous rows. `out=`: C-contiguous square matrix.

- **Tensor reductions**: Arbitrary strides (strided views supported). Returns scalar or reduced tensor.
