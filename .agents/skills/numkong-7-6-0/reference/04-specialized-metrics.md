# Specialized Metrics

## Probability Divergences

### Kullback-Leibler Divergence

KLD measures the information lost when one distribution approximates another:

```python
p = np.array([0.2, 0.3, 0.5], dtype=np.float32)
q = np.array([0.1, 0.3, 0.6], dtype=np.float32)

kl_forward = nk.kullbackleibler(p, q)
kl_reverse = nk.kullbackleibler(q, p)
assert kl_forward != kl_reverse  # KLD is asymmetric
```

Use cases: variational inference (ELBO objective), knowledge distillation between neural networks, information gain in decision trees, measuring fit between a model and observed data.

### Jensen-Shannon Distance

JSD provides a symmetric and bounded alternative. The distance is the square root of the symmetrized KLD through a mixture M = (P+Q)/2:

```python
js_forward = nk.jensenshannon(p, q)
js_reverse = nk.jensenshannon(q, p)
np.testing.assert_allclose(js_forward, js_reverse, atol=1e-6)  # JSD is symmetric
```

Unlike the raw divergence, d_JS is a true metric satisfying the triangle inequality. Use cases: microbiome community comparison (enterotyping), distribution drift detection, topic model evaluation, GAN theoretical foundation.

### Optimizations

**SIMD Log2 Approximation:** Skylake kernels use `VGETEXP` and `VGETMANT` to decompose floating-point values into exponent and mantissa components, then apply a polynomial approximation to the mantissa. NEON kernels use integer bit extraction instead:

```
exponent = (reinterpret_as_int(x) >> 23) - 127
mantissa = reinterpret_as_float((reinterpret_as_int(x) & 0x7FFFFF) | 0x3F800000) - 1
log2(x) ≈ exponent + c1·m + c2·m² + c3·m³ + c4·m⁴ + c5·m⁵
```

**Kahan Compensated Summation for Float64:** After each P(i)·log₂(P(i)/Q(i)) term is computed, a correction captures the low-order bits lost in the addition, keeping accumulated error bounded by O(1) ULP regardless of vector length.

### Supported Types

- `f64` → `f64` output (Kahan compensated)
- `f32` → `f32` output
- `f16`, `bf16` → `f32` output (widened)

## Geospatial Metrics

Geospatial kernels take four coordinate arrays. Inputs are in radians. Outputs are in meters.

### Vincenty Distance

Ellipsoidal earth model, higher accuracy:

```python
# Statue of Liberty → Big Ben
liberty_lat = np.array([0.7101605100], dtype=np.float64)
liberty_lon = np.array([-1.2923203180], dtype=np.float64)
big_ben_lat = np.array([0.8988567821], dtype=np.float64)
big_ben_lon = np.array([-0.0021746802], dtype=np.float64)

vincenty = nk.vincenty(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)
# ≈ 5,589,857 m
```

### Haversine Distance

Spherical earth model, ~46 km less for the same points:

```python
haversine = nk.haversine(liberty_lat, liberty_lon, big_ben_lat, big_ben_lon)
# ≈ 5,543,723 m
```

Vincenty in f32 drifts ~2 m from f64 for the same coordinates.

## Curved Metrics

Curved-space kernels use an extra metric tensor or inverse covariance.

### Bilinear Forms

Computes aᴴMb for complex vectors (conjugate transpose of a, times metric M, times b):

```python
a = (np.ones(16) + 1j * np.zeros(16)).astype(np.complex64)
b = (np.zeros(16) + 1j * np.ones(16)).astype(np.complex64)
m = np.eye(16, dtype=np.complex64)
bilinear = nk.bilinear(a, b, m)
```

NumKong's typed `nk_bilinear_*` kernels stream through rows of C with nested compensated dot products, never allocating beyond registers. For complex-valued quantum states, where the intermediate would be a 2N-element complex vector, the savings double.

### Mahalanobis Distance

Computes √((a-b)ᵀ M⁻¹ (a-b)) for real vectors with inverse covariance:

```python
x = np.ones(32, dtype=np.float32)
y = np.full(32, 2.0, dtype=np.float32)
inv_cov = np.eye(32, dtype=np.float32)
mahalanobis = nk.mahalanobis(x, y, inv_cov)
```

## Geometric Mesh Alignment

Mesh alignment returns a structured result object with fields: `rotation`, `scale`, `rmsd`, `a_centroid`, and `b_centroid`.

### Kabsch Algorithm

Finds the optimal rotation that minimizes RMSD between two point clouds (no scaling):

```python
source = np.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
], dtype=np.float32)

result = nk.kabsch(source, source.copy())
assert np.asarray(result.rotation).shape == (3, 3)
assert float(np.asarray(result.scale)) == 1.0
```

### Umeyama Algorithm

Like Kabsch but also recovers uniform scaling:

```python
target = source * 2.0
result = nk.umeyama(source, target)
assert float(np.asarray(result.rmsd)) < 1e-6   # exact alignment
assert abs(float(np.asarray(result.scale)) - 2.0) < 0.01  # recovers 2x scale
```

### Pipeline

After deinterleaving the (x, y, z) coordinates, the pipeline is the same across all ISAs: compute centroids, build the 3×3 cross-covariance matrix via outer products, decompose it with a McAdams branching-free SVD using 16 fixed Jacobi iterations, and apply a reflection correction when det(R) = -1.

Through Python bindings, NumKong's Kabsch reaches 261 M points/s — roughly 19x SciPy's `Rotation.align_vectors` at 14 M points/s, and 200x BioPython's `SVDSuperimposer` at 1.3 M points/s.

## Sparse Operations

### Index Intersection

Computes the size of the intersection between two sorted index arrays:

```python
idx_a = np.array([1, 3, 5, 7], dtype=np.uint32)
idx_b = np.array([3, 4, 5, 8], dtype=np.uint32)
intersection_size = nk.intersect(idx_a, idx_b)  # 2 (indices 3 and 5)
```

### Weighted Sparse Dot Product

Computes the dot product over shared indices:

```python
val_a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
val_b = np.array([5.0, 6.0, 7.0, 8.0], dtype=np.float32)
sparse_dot = nk.sparse_dot(idx_a, val_a, idx_b, val_b)
```
