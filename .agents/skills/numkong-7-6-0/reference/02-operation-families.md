# Operation Families

## Dot Products

Compute inner products with widened accumulation. Real and integer types produce scalar results; complex types produce complex results.

```python
import numpy as np, numkong as nk

# Real dot product — f32 inputs, f64 output
a, b = np.random.randn(1536).astype(np.float32), np.random.randn(1536).astype(np.float32)
dot = nk.dot(a, b)

# Complex dot and vdot (conjugated)
a_c = (np.random.randn(256) + 1j * np.random.randn(256)).astype(np.complex64)
b_c = (np.random.randn(256) + 1j * np.random.randn(256)).astype(np.complex64)
dot_c = nk.dot(a_c, b_c)    # unconjugated
vdot_c = nk.vdot(a_c, b_c)  # conjugated (numpy.vdot equivalent)
```

C API names encode type and widening: `nk_dot_f32` (f32→f64), `nk_dot_i8` (i8→i32), `nk_dot_bf16` (bf16→f32).

## Spatial Distances

Three metrics for dense vectors: squared Euclidean, Euclidean, and angular (cosine) distance. Used in nearest-neighbor search, clustering, and dimensionality reduction.

```python
a = np.random.randn(768).astype(np.float16)
b = np.random.randn(768).astype(np.float16)

sqeuclidean = nk.sqeuclidean(a, b)  # sum((a-b)^2)
euclidean = nk.euclidean(a, b)      # sqrt(sum((a-b)^2))
angular = nk.angular(a, b)          # 1 - dot(a,b)/(||a||*||b||)
```

Angular distance uses a three-accumulator pattern: `sum(a*b)`, `sum(a^2)`, and `sum(b^2)` computed in a single pass. Reciprocal square root via Newton-Raphson refinement for final normalization.

## Set Similarity

Two modes: packed-binary metrics on bit-packed data, and integer set Jaccard on sorted identifier arrays.

```python
# Binary Hamming and Jaccard
a_bits = np.packbits(np.random.randint(0, 2, size=256, dtype=np.uint8))
b_bits = np.packbits(np.random.randint(0, 2, size=256, dtype=np.uint8))
hamming = nk.hamming(a_bits, b_bits, dtype="uint1")
jaccard = nk.jaccard(a_bits, b_bits, dtype="uint1")

# Integer set Jaccard — inputs must be sorted ascending
set_a = np.array([1, 3, 5, 7, 9], dtype=np.uint32)
set_b = np.array([3, 5, 8, 9, 10], dtype=np.uint32)
jaccard_sets = nk.jaccard(set_a, set_b)  # |A ∩ B| / |A ∪ B|
```

## Probability Divergences

Kullback-Leibler divergence (asymmetric) and Jensen-Shannon distance (symmetric, true metric). Used in variational inference, knowledge distillation, topic modeling, and distribution comparison.

```python
p = np.array([0.2, 0.3, 0.5], dtype=np.float32)
q = np.array([0.1, 0.3, 0.6], dtype=np.float32)

kl_fwd = nk.kullbackleibler(p, q)  # asymmetric: KL(P||Q) != KL(Q||P)
kl_rev = nk.kullbackleibler(q, p)

js = nk.jensenshannon(p, q)        # symmetric, bounded [0, 1]
```

Float64 paths use Kahan compensated summation. Float32 paths use SIMD log2 approximation via exponent/mantissa decomposition with polynomial approximation.

## Geospatial Metrics

Vincenty (ellipsoidal, more accurate) and Haversine (spherical, faster). Inputs in radians, outputs in meters.

```python
# Statue of Liberty → Big Ben
liberty_lat = np.array([0.7101605100], dtype=np.float64)
liberty_lon = np.array([-1.2923203180], dtype=np.float64)
big_ben_lat = np.array([0.8988567821], dtype=np.float64)
big_ben_lon = np.array([-0.0021746802], dtype=np.float64)

vincenty = nk.vincenty(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)
# ≈ 5,589,857 m (ellipsoidal baseline)
haversine = nk.haversine(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)
# ≈ 5,543,723 m (spherical, ~46 km less)
```

Float32 Vincenty drifts ~2 m from Float64 on this baseline.

## Curved Metrics

Bilinear forms and Mahalanobis distance combine vectors with an extra metric tensor or inverse covariance. Used in quantum computing (bilinear expectation values) and statistics (Mahalanobis distance).

```python
# Complex bilinear form: aᴴ M b
a = (np.ones(16) + 1j * np.zeros(16)).astype(np.complex64)
b = (np.zeros(16) + 1j * np.ones(16)).astype(np.complex64)
m = np.eye(16, dtype=np.complex64)
result = nk.bilinear(a, b, m)

# Real Mahalanobis distance: sqrt((a-b)^T M^-1 (a-b))
x = np.ones(32, dtype=np.float32)
y = np.full(32, 2.0, dtype=np.float32)
inv_cov = np.eye(32, dtype=np.float32)
dist = nk.mahalanobis(x, y, inv_cov)
```

Bilinear forms stream through rows of C with nested compensated dot products — no intermediate vector allocation.

## Mesh Alignment

Three algorithms for 3D point cloud comparison: RMSD (raw deviation), Kabsch (optimal rotation via SVD), and Umeyama (Kabsch + uniform scale factor). Used in structural biology, robotics, and computer graphics.

```python
source = np.array([[0,0,0], [1,0,0], [0,1,0]], dtype=np.float32)
target = source * 2.0

result = nk.kabsch(source, source.copy())
# result.rotation: (3,3) matrix, result.scale: 1.0

result = nk.umeyama(source, target)
# result.rmsd < 1e-6 (exact alignment), result.scale ≈ 2.0
```

Uses McAdams branching-free 3×3 SVD with fixed 16 Jacobi iterations and quaternion-accumulated rotations. Point clouds stored interleaved as [x₀,y₀,z₀, x₁,y₁,z₁, ...].

## Sparse Operations

Sorted-index intersection and weighted sparse dot products for sparse vector representations.

```python
idx_a = np.array([1, 3, 5, 7], dtype=np.uint32)
idx_b = np.array([3, 4, 5, 8], dtype=np.uint32)
intersection_size = nk.intersect(idx_a, idx_b)  # → 2 (indices 3 and 5)

val_a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
val_b = np.array([5.0, 6.0, 7.0, 8.0], dtype=np.float32)
sparse_dot = nk.sparse_dot(idx_a, val_a, idx_b, val_b)
```

## MaxSim Late-Interaction Scoring

ColBERT-style late-interaction: for each query token, find the minimum angular distance to any document token, then sum. Two-stage coarse-to-fine: i8-quantized screening finds best document per query, full-precision refinement computes final angular distance.

```python
queries = np.random.randn(32, 128).astype(np.float32)
documents = np.random.randn(192, 128).astype(np.float32)

q = nk.maxsim_pack(queries, dtype="float32")
d = nk.maxsim_pack(documents, dtype="float32")
score = nk.maxsim_packed(q, d)
```

On Apple SME, dual pre-packing (both query and document packed) uses all 4 ZA tiles as accumulators — 33% more MOPA throughput than single-sided packing. End-to-end speedup over GEMM decomposition: 5×.

## Elementwise Operations

Elementwise arithmetic and fused operations with arbitrary stride support.

```python
a = np.arange(8, dtype=np.float32)
b = np.arange(8, dtype=np.float32)[::-1].copy()

scaled = nk.scale(a, alpha=2.0, beta=1.0)      # 2 * a + 1
blended = nk.blend(a, b, alpha=0.25, beta=0.75) # 0.25*a + 0.75*b
fused = nk.fma(a, b, a, alpha=1.0, beta=1.0)    # a * b + a
```

## Reductions

Moments reductions return `(sum, sum_of_squares)` with widened accumulation. Min/max/argmin support strided views.

```python
x = np.full(4096, 255, dtype=np.uint8)
nk_sum, nk_sumsq = nk.moments(nk.Tensor(x))
# Widened accumulation — no overflow (unlike np.sum with same-width dtype)

# Strided argmin — ~2.45x faster than np.argmin on Apple M2 Pro
matrix = nk.Tensor(np.random.randn(2_000_000, 3).astype(np.float32))
idx = matrix[:, 1].argmin()  # strided column view
mn, i0, mx, i1 = matrix[:, 1].minmax()
```
