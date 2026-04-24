# Operation Families

> **Source:** NumKong README, Python/C++/Rust/JS SDK docs
> **Loaded from:** SKILL.md (via progressive disclosure)

## Dot Products

Dot products are their own family because storage type, conjugation rules, and output widening matter.

```python
import numpy as np
import numkong as nk

# Real dot product (widened accumulation)
a = np.random.randn(1536).astype(np.float32)
b = np.random.randn(1536).astype(np.float32)
dot = nk.dot(a, b)

# Complex dot and vdot (conjugated)
a_c = (np.random.randn(256) + 1j * np.random.randn(256)).astype(np.complex64)
b_c = (np.random.randn(256) + 1j * np.random.randn(256)).astype(np.complex64)
dot_c = nk.dot(a_c, b_c)   # unconjugated
vdot_c = nk.vdot(a_c, b_c) # conjugated (like numpy.vdot)
```

## Dense Distances

Cover `sqeuclidean`, `euclidean`, and `angular`. The accumulator policy is not forced to match the storage dtype.

```python
a = np.random.randn(768).astype(np.float16)
b = np.random.randn(768).astype(np.float16)

sqeuclidean = nk.sqeuclidean(a, b)
euclidean = nk.euclidean(a, b)
angular = nk.angular(a, b)
```

### Output Control

Most entrypoints accept `out=`, `dtype=`, and `out_dtype=` keyword arguments:

```python
# Pre-allocated output with out=
out = nk.zeros((100,), dtype="float32")
nk.sqeuclidean(queries, database[:100], out=out)  # writes in-place, returns None

# Explicit input dtype for raw byte buffers
raw = np.frombuffer(some_bytes, dtype=np.uint16)
nk.dot(raw, raw, dtype=nk.bfloat16)  # reinterpret uint16 as bf16

# Output dtype override
nk.euclidean(queries[0], database[0], out_dtype="float32")  # accumulate in f64, downcast result
```

When `out=` is provided, the function writes results in-place and returns `None`. The `out` array must be pre-allocated with the correct shape and a supported dtype. Type objects (`nk.bfloat16`) are preferred over strings — faster dispatch and IDE autocomplete.

## All-Pairs APIs: cdist

`cdist` is the NumPy/SciPy-shaped all-pairs entrypoint, handling rectangular matrix pairs and symmetric self-distance cases.

```python
queries = np.random.randn(100, 768).astype(np.float32)
database = np.random.randn(10_000, 768).astype(np.float32)

pairwise = nk.angular(queries, database[:100])             # rectangular broadcasted pairwise
all_pairs = nk.cdist(queries, database, metric="angular")  # scipy.spatial.distance.cdist analogue
```

## Set Similarity

### Binary (Packed Bits)

Operate on packed bits via `np.packbits`:

```python
a_bits = np.random.randint(0, 2, size=256, dtype=np.uint8)
b_bits = np.random.randint(0, 2, size=256, dtype=np.uint8)
a, b = np.packbits(a_bits), np.packbits(b_bits)

hamming = nk.hamming(a, b, dtype="uint1")
jaccard = nk.jaccard(a, b, dtype="uint1")
```

### Integer Set Jaccard

Works on sorted ascending arrays of integer identifiers:

```python
set_a = np.array([1, 3, 5, 7, 9], dtype=np.uint32)  # must be sorted ascending
set_b = np.array([3, 5, 8, 9, 10], dtype=np.uint32)
jaccard_sets = nk.jaccard(set_a, set_b)  # |A ∩ B| / |A ∪ B|
```

## Probability Metrics

```python
p = np.array([0.2, 0.3, 0.5], dtype=np.float32)
q = np.array([0.1, 0.3, 0.6], dtype=np.float32)

kl_forward = nk.kullbackleibler(p, q)
kl_reverse = nk.kullbackleibler(q, p)
assert kl_forward != kl_reverse  # KLD is asymmetric

js = nk.jensenshannon(p, q)
# JSD is symmetric
```

## Geospatial Metrics

Inputs in radians, outputs in meters:

```python
import numpy as np
import numkong as nk

# Statue of Liberty → Big Ben
liberty_lat, liberty_lon = np.array([0.7101605100], dtype=np.float64), np.array([-1.2923203180], dtype=np.float64)
big_ben_lat, big_ben_lon = np.array([0.8988567821], dtype=np.float64), np.array([-0.0021746802], dtype=np.float64)

vincenty = nk.vincenty(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)    # ≈ 5,589,857 m (ellipsoidal)
haversine = nk.haversine(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)  # ≈ 5,543,723 m (spherical, ~46 km less)
```

Vincenty in f32 drifts ~2 m from f64.

## Curved Metrics

Use an extra metric tensor or inverse covariance:

```python
# Complex bilinear form: aᴴ M b
a = (np.ones(16) + 1j * np.zeros(16)).astype(np.complex64)
b = (np.zeros(16) + 1j * np.ones(16)).astype(np.complex64)
m = np.eye(16, dtype=np.complex64)
bilinear = nk.bilinear(a, b, m)

# Real Mahalanobis distance: √((a−b)ᵀ M⁻¹ (a−b))
x = np.ones(32, dtype=np.float32)
y = np.full(32, 2.0, dtype=np.float32)
inv_cov = np.eye(32, dtype=np.float32)
mahalanobis = nk.mahalanobis(x, y, inv_cov)
```

## Elementwise Operations

```python
a = np.arange(8, dtype=np.float32)
b = np.arange(8, dtype=np.float32)[::-1].copy()

scaled = nk.scale(a, alpha=2.0, beta=1.0)        # 2 * a + 1
blended = nk.blend(a, b, alpha=0.25, beta=0.75)
fused = nk.fma(a, b, a, alpha=1.0, beta=1.0)      # a * b + a
```

## Reductions

### Moments

Return `(sum, sum_of_squares)` with widened accumulation:

```python
x = np.full(4096, 255, dtype=np.uint8)
nk_sum, nk_sumsq = nk.moments(nk.Tensor(x))
naive_sum = np.sum(x, dtype=np.uint8)  # overflows immediately
assert nk_sum > int(naive_sum)
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

assert idx == 2
assert float(np.asarray(mn)) == -1.0
```

On Apple M2 Pro, `Tensor[..., 1].argmin()` on a 2M×3 float32 array is ~2.45x faster than NumPy.

## Sparse Operations

```python
idx_a = np.array([1, 3, 5, 7], dtype=np.uint32)
idx_b = np.array([3, 4, 5, 8], dtype=np.uint32)
intersection_size = nk.intersect(idx_a, idx_b)  # → 2 (indices 3 and 5)

val_a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
val_b = np.array([5.0, 6.0, 7.0, 8.0], dtype=np.float32)
sparse_dot = nk.sparse_dot(idx_a, val_a, idx_b, val_b)
```

## Geometric Mesh Alignment

Returns structured result with `rotation`, `scale`, `rmsd`, `a_centroid`, `b_centroid`:

```python
source = np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=np.float32)
result = nk.kabsch(source, source.copy())
assert np.asarray(result.rotation).shape == (3, 3)
assert float(np.asarray(result.scale)) == 1.0

# Umeyama with known 2x scaling
target = source * 2.0
result = nk.umeyama(source, target)
assert float(np.asarray(result.rmsd)) < 1e-6
assert abs(float(np.asarray(result.scale)) - 2.0) < 0.01
```

## MaxSim and Late Interaction

For ColBERT-style retrieval:

```python
queries = np.random.randn(32, 128).astype(np.float32)
documents = np.random.randn(192, 128).astype(np.float32)

q = nk.maxsim_pack(queries, dtype="float32")
d = nk.maxsim_pack(documents, dtype="float32")
score = nk.maxsim_packed(q, d)
```

## Packed Matrix Kernels (GEMM-Like)

Pack once, reuse across query batches:

```python
left = np.random.randn(128, 768).astype(np.float32)
right = np.random.randn(10_000, 768).astype(np.float32)

right_packed = nk.dots_pack(right, dtype="float32")
scores = nk.dots_packed(left, right_packed)  # equivalent to left @ right.T
assert scores.shape == (128, 10_000)
```

Packing performs five transformations: type pre-conversion, SIMD depth padding, per-column norm precomputation, ISA-specific tile layout, and power-of-2 stride breaking (extra padding to avoid cache set aliasing).

## Symmetric Kernels (SYRK-Like)

Compute self-similarity without duplicate pairs:

```python
vectors = np.random.randn(1024, 768).astype(np.float32)
out = nk.zeros((1024, 1024), dtype="float64")

nk.dots_symmetric(vectors, out=out, start_row=0, end_row=256)
nk.dots_symmetric(vectors, out=out, start_row=256, end_row=512)
```

Also available: `angulars_symmetric`, `euclideans_symmetric`.

## Tensor Objects (Python)

`Tensor` is a memoryview-backed container with NumPy-like metadata:

```python
t = nk.Tensor(np.arange(12, dtype=np.float32).reshape(3, 4))
print(t.shape, t.dtype, t.ndim, t.strides, t.itemsize, t.nbytes)

row0 = t[0, :]           # first row, shape (4,)
col2 = t[:, 2]           # third column, strided view, shape (3,)
val  = t[1, 2]           # scalar element access → 6.0

# Transpose, reshape, flatten
print(t.T.shape)
print(t.reshape(2, 6).shape)
print(t.flatten().shape)

# Reductions on sliced views
idx = col2.argmin()
mn, i0, mx, i1 = col2.minmax()
```

### Memory Layout Requirements

- Dense distances: rows must be contiguous (`strides[last] <= itemsize`). Strided rows rejected.
- `cdist`: same as dense distances; `out=` must be rank-2 with shape `(a.count, b.count)`.
- Elementwise: arbitrary strides supported; `out=` must match input shape.
- Packed matrix: left operand rank-2, contiguous rows, no negative strides; output C-contiguous.
- Symmetric: contiguous rows; `out=` C-contiguous square matrix.
- Tensor reductions: arbitrary strides supported.

### External Memory Addressing

```python
# Round-trip through integer address
matrix = nk.zeros((3, 4), dtype='float32')
address = matrix.data_ptr
matrix_view = nk.from_pointer(address, (3, 4), 'float32', owner=matrix)

# Wrap NumPy array with zero copies
embeddings = np.random.randn(1024).astype(np.float32)
embeddings_view = nk.from_pointer(embeddings.ctypes.data, (1024,), 'float32', owner=embeddings)

# PyTorch tensors (buffer protocol, zero copy)
import torch
query = torch.randn(512)
nk.dot(query, query)  # direct buffer protocol
```
