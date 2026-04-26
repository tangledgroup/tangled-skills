# Vector Operations

## Dot Products

Dot products are their own family because storage type, conjugation rules, and output widening matter.

### Real Dot Products

```python
import numpy as np
import numkong as nk

a = np.random.randn(768).astype(np.float32)
b = np.random.randn(768).astype(np.float32)
result = nk.dot(a, b)
```

For complex types, `dot` computes the unconjugated product and `vdot` computes the conjugated inner product:

```python
a = (np.random.randn(256) + 1j * np.random.randn(256)).astype(np.complex64)
b = (np.random.randn(256) + 1j * np.random.randn(256)).astype(np.complex64)

dot_result = nk.dot(a, b)   # numpy.dot(a, b)
vdot_result = nk.vdot(a, b) # numpy.vdot(a, b)
```

Real low-precision inputs can be routed through explicit dtype tags when the storage buffer itself is raw bytes:

```python
raw = np.frombuffer(some_bytes, dtype=np.uint16)
nk.dot(raw, raw, dtype=nk.bfloat16)  # reinterpret uint16 as bf16
```

### Input/Output Type Rules

Real and integer dot products widen the accumulator:

- `f64` → `f64` output (compensated summation)
- `f32` → `f32` output (widened to f64 internally)
- `f16`, `bf16` → `f32` output
- `e5m2`, `e4m3` → `f32` output
- `e3m2`, `e2m3` → `f32` output (integer accumulation, exact)
- `i8` → `i32` output, `u8` → `u32` output
- `i4` → `i32` output, `u4` → `u32` output
- `u1` → `u32` output (popcount of AND)

Complex dot products:

- `f64c` → `f64c`, `f32c` → `f32c`, `f16c` → `f32c`, `bf16c` → `f32c`

## Spatial Distances

The dense distance entrypoints cover `sqeuclidean`, `euclidean`, and `angular`:

```python
a = np.random.randn(768).astype(np.float16)
b = np.random.randn(768).astype(np.float16)

sqeuclidean = nk.sqeuclidean(a, b)
euclidean   = nk.euclidean(a, b)
angular     = nk.angular(a, b)  # cosine distance: 1 - dot/(|a|*|b|)
```

### Three-Accumulator Angular Pattern

Angular distance requires three concurrent dot products in a single pass: Σaᵢ·bᵢ, Σaᵢ², and Σbᵢ². All spatial angular kernels interleave these three FMA streams so that each vector element is loaded once and immediately contributes to all three accumulators. This triples register pressure compared to a plain dot product but avoids reading two vectors three times (6n cache line fetches vs 2n).

### Reciprocal Square Root

Angular and Euclidean distances compute normalization via in-hardware reciprocal square root estimates refined by Newton-Raphson iteration. The formula is x_{n+1} = x_n · (3 - d · x_n²) / 2. NumKong selects the iteration count per platform so the final ULP bound is consistent across ISAs:

- Haswell `VRSQRT14` + one Newton-Raphson step → ~28 bits precision
- Skylake `VRSQRTPS` → ~28 bits directly (no refinement needed)
- NEON `vrsqrte` + `vrsqrts` → ~22 bits (one refinement step)

### Output Control

Most distance and dot-product entrypoints accept `out=`, `dtype=`, and `out_dtype=` keyword arguments:

```python
# Pre-allocated output with out=
out = nk.zeros((100,), dtype="float32")
nk.sqeuclidean(queries, database[:100], out=out)  # writes in-place, returns None

# Output dtype override
nk.euclidean(queries[0], database[0], out_dtype="float32")  # accumulate in f64, downcast result
```

When `out=` is provided, the function writes results in-place and returns `None`. The `out` array must be pre-allocated with the correct shape and a supported dtype.

## Set Similarity

### Binary Packed Metrics

Packed-binary metrics operate on packed bits via `np.packbits`:

```python
a_bits = np.random.randint(0, 2, size=256, dtype=np.uint8)
b_bits = np.random.randint(0, 2, size=256, dtype=np.uint8)
a, b = np.packbits(a_bits), np.packbits(b_bits)

hamming = nk.hamming(a, b, dtype="uint1")
jaccard = nk.jaccard(a, b, dtype="uint1")
```

### Integer Set Jaccard

Works on sorted ascending arrays of integer identifiers. Both inputs must be sorted in ascending order:

```python
set_a = np.array([1, 3, 5, 7, 9], dtype=np.uint32)
set_b = np.array([3, 5, 8, 9, 10], dtype=np.uint32)
jaccard_sets = nk.jaccard(set_a, set_b)  # |A ∩ B| / |A ∪ B|
```

## Elementwise Operations

Elementwise arithmetic and fused operations share the tensor infrastructure:

```python
a = np.arange(8, dtype=np.float32)
b = np.arange(8, dtype=np.float32)[::-1].copy()

scaled   = nk.scale(a, alpha=2.0, beta=1.0)      # 2 * a + 1
blended  = nk.blend(a, b, alpha=0.25, beta=0.75)
fused    = nk.fma(a, b, a, alpha=1.0, beta=1.0)  # a * b + a
```

## Reductions

### Moments

Moments reductions return `(sum, sum_of_squares)` with widened accumulation:

```python
x = np.full(4096, 255, dtype=np.uint8)
nk_sum, nk_sumsq = nk.moments(nk.Tensor(x))
naive_sum = np.sum(x, dtype=np.uint8)  # overflows immediately
# nk_sum > int(naive_sum) due to widened accumulation
```

### Min/Max

SIMD-accelerated strided reductions:

```python
matrix = nk.Tensor(np.array([
    [ 3.0,  0.0, 7.0],
    [ 1.0,  2.0, 5.0],
    [ 4.0, -1.0, 6.0],
], dtype=np.float32))

second_column = matrix[:, 1]  # strided view
idx = second_column.argmin()
mn, i0, mx, i1 = second_column.minmax()
```

On Apple M2 Pro, `nk.Tensor(... )[:, 1].argmin()` is ~2.45x faster than `np.argmin(matrix[:, 1])` on a row-major 2,000,000 × 3 float32 array.

## All-Pairs APIs and cdist

`cdist` is the NumPy/SciPy-shaped all-pairs entrypoint:

```python
queries  = np.random.randn(100, 768).astype(np.float32)
database = np.random.randn(10_000, 768).astype(np.float32)

pairwise  = nk.angular(queries, database[:100])             # rectangular broadcasted pairwise
all_pairs = nk.cdist(queries, database, metric="angular")   # scipy.spatial.distance.cdist analogue

assert np.asarray(pairwise).shape == (100, 100)
assert np.asarray(all_pairs).shape == (100, 10_000)
```

## Sparse Operations

Sparse helpers cover both sorted-index intersections and weighted sparse dot products:

```python
idx_a = np.array([1, 3, 5, 7], dtype=np.uint32)
idx_b = np.array([3, 4, 5, 8], dtype=np.uint32)
intersection_size = nk.intersect(idx_a, idx_b)  # 2 (indices 3 and 5)

val_a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
val_b = np.array([5.0, 6.0, 7.0, 8.0], dtype=np.float32)
sparse_dot = nk.sparse_dot(idx_a, val_a, idx_b, val_b)
```
