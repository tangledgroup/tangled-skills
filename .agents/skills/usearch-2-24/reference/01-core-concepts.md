# USearch Core Concepts

This reference covers fundamental concepts for using USearch 2.24, including index configuration, distance metrics, data types, quantization, and hardware acceleration.

## Index Configuration

### Constructor Parameters

```python
from usearch.index import Index

index = Index(
    ndim=768,              # Required: Number of dimensions in vectors
    metric='cos',          # Distance metric (default: 'ip' for inner product)
    dtype='f32',           # Data type for storage (default: None, auto-selects)
    connectivity=16,       # Graph connectivity M (default: 16)
    expansion_add=128,     # EF construction parameter (default: 128)
    expansion_search=64,   # EF search parameter (default: 64)
    multi=False,           # Allow multiple vectors per key (default: False)
)
```

### Parameter Details

#### `ndim` (Required)
Number of dimensions in input vectors. Must match the dimensionality of all vectors added to the index.

```python
# 3D vectors
index_3d = Index(ndim=3)

# 768-dimensional embeddings (common for BERT-like models)
index_embeddings = Index(ndim=768)

# 2048-dimensional image embeddings
index_images = Index(ndim=2048)
```

#### `metric` (Default: 'ip')
Distance metric used for similarity computation. Supported metrics:

| Metric | String Alias | Use Case | Formula |
|--------|--------------|----------|---------|
| `MetricKind.IP` | 'ip', 'dot', 'inner_product' | Cosine similarity (with normalized vectors) | 1 - (A·B) |
| `MetricKind.Cos` | 'cos', 'cosine' | Cosine distance | 1 - cosine_similarity(A, B) |
| `MetricKind.L2sq` | 'l2sq', 'l2_sq' | Euclidean distance squared | Σ(Ai - Bi)² |
| `MetricKind.Haversine` | 'haversine' | Geospatial (lat/lon) | Great circle distance |
| `MetricKind.Divergence` | 'divergence' | KL-divergence-like | Custom divergence |
| `MetricKind.Pearson` | 'pearson' | Correlation distance | 1 - pearson_correlation |
| `MetricKind.Hamming` | 'hamming' | Binary vectors | Bit differences |
| `MetricKind.Tanimoto` | 'tanimoto' | Molecular fingerprints | Jaccard-like for bits |
| `MetricKind.Sorensen` | 'sorensen' | Binary similarity | Sorensen-Dice coefficient |

**Metric Selection Guide:**
- **Text embeddings**: Use `'cos'` or `'ip'` (with normalized vectors)
- **Image embeddings**: Use `'cos'` for semantic similarity
- **Geospatial data**: Use `'haversine'` with 2D [lat, lon] vectors
- **Molecular fingerprints**: Use `'tanimoto'` with binary vectors
- **Raw Euclidean distance**: Use `'l2sq'`

#### `dtype` (Default: None)
Storage data type for quantization and memory efficiency:

| Type | String | Bytes per Element | Precision | Best For |
|------|--------|-------------------|-----------|----------|
| `ScalarKind.F64` | 'f64', 'float64' | 8 bytes | Full precision | Scientific computing |
| `ScalarKind.F32` | 'f32', 'float32' | 4 bytes | Single precision | General purpose |
| `ScalarKind.BF16` | 'bf16', 'bfloat16' | 2 bytes | Brain float | Modern CPUs (recommended) |
| `ScalarKind.F16` | 'f16', 'float16' | 2 bytes | Half precision | GPU-compatible |
| `ScalarKind.I8` | 'i8', 'int8' | 1 byte | 8-bit integer | Cosine metrics only |
| `ScalarKind.B1` | 'b1', 'b1x8', 'bits' | 0.125 bytes | 1-bit binary | Binary metrics only |

**Quantization Notes:**
- `i8` quantization: Vectors are normalized to unit length and scaled to [-127, 127]. Only valid for cosine-like metrics.
- `b1` quantization: Scalar components > 0 become `true`, others `false`. Only valid for binary metrics (Hamming, Tanimoto, Sorensen).
- Quantized indexes cannot recover original vectors exactly via `index[key]` lookup.

**Auto-selection:** When `dtype=None`, USearch selects based on hardware acceleration:
```python
index = Index(ndim=768, metric='cos')  # Auto-selects bf16 or f16 if supported
print(index.dtype)  # Shows selected type
```

#### `connectivity` (Default: 16)
Controls the number of connections per node in the HNSW graph (often called `M`).

```python
# Lower connectivity = faster indexing, less memory, slightly lower recall
index_fast = Index(ndim=256, connectivity=8)

# Higher connectivity = slower indexing, more memory, higher recall
index_accurate = Index(ndim=256, connectivity=32)
```

**Trade-offs:**
- `connectivity=8`: Fast indexing, ~97% recall@1
- `connectivity=16` (default): Balanced, ~99% recall@1
- `connectivity=32`: Slower indexing, ~99.5% recall@1

#### `expansion_add` (Default: 128)
Controls the EF (expansion factor) during index construction. Higher values improve recall but slow down insertion.

```python
# Faster indexing with slightly lower quality
index_quick = Index(ndim=256, expansion_add=64)

# Slower indexing with higher quality
index_premium = Index(ndim=256, expansion_add=256)
```

**Recommendations:**
- `expansion_add=64`: Quick prototyping, ~97% recall
- `expansion_add=128` (default): Production quality, ~99% recall
- `expansion_add=256`: Maximum quality, ~99.5% recall

#### `expansion_search` (Default: 64)
Controls the EF during search. Higher values improve recall but slow down queries.

```python
# Faster search with slightly lower recall
index_fast_search = Index(ndim=256, expansion_search=32)

# Slower search with higher recall
index_accurate_search = Index(ndim=256, expansion_search=128)
```

**Runtime override:** You can also control this per-search:
```python
matches = index.search(query_vector, 10, expansion=128)  # Override for this search
```

#### `multi` (Default: False)
Allow multiple vectors per key. When `True`, the same key can be associated with multiple vectors.

```python
index_multi = Index(ndim=3, multi=True)

# Add multiple vectors with same key
index_multi.add(42, np.array([1.0, 0.0, 0.0]))
index_multi.add(42, np.array([0.0, 1.0, 0.0]))  # Same key, different vector

# Search returns all matches, potentially with duplicate keys
matches = index_multi.search(np.array([0.9, 0.1, 0.0]), 10)
```

## Hardware Acceleration

USearch detects and utilizes hardware-specific optimizations:

```python
from usearch.index import Index

# Check hardware acceleration for different configurations
index_f16 = Index(ndim=768, metric='cos', dtype='f16')
print(index_f16.hardware_acceleration)  # 'sapphire', 'ice', 'none', etc.

index_tanimoto = Index(ndim=2048, metric='tanimoto')
print(index_tanimoto.hardware_acceleration)  # Shows acceleration for binary ops
```

**Acceleration Levels:**
- `sapphire`: Intel AVX-512 VNNI (Sapphire Rapids and newer)
- `ice`: Intel AVX2 (Skylake and newer)
- `neoverse`: ARM SVE (AWS Graviton, etc.)
- `none`: No specific acceleration detected (falls back to scalar)

**Checking library features:**
```python
from usearch.index import USES_OPENMP, USES_SIMSIMD, USES_FP16LIB

print(f"OpenMP enabled: {USES_OPENMP}")      # Parallel processing
print(f"SimSIMD enabled: {USES_SIMSIMD}")    # SIMD optimizations
print(f"FP16Lib enabled: {USES_FP16LIB}")    # Half-precision math
```

## Index Statistics and Inspection

### Basic Properties

```python
index = Index(ndim=256, metric='cos', dtype='f32')

print(f"Dimensions: {index.ndim}")           # 256
print(f"Metric: {index.metric_kind}")        # MetricKind.Cos
print(f"Data type: {index.dtype}")           # ScalarKind.F32
print(f"Count: {len(index)}")                # Number of vectors
print(f"Connectivity: {index.connectivity}")  # 16
```

### Memory Usage Estimation

```python
import numpy as np

ndim = 768
n_vectors = 1_000_000
dtype_bytes = 2  # f16 or bf16

# Rough estimate: vectors + graph structure
vector_memory = n_vectors * ndim * dtype_bytes
graph_overhead = n_vectors * 16 * 4  # 16 neighbors per node, 4 bytes each

total_mb = (vector_memory + graph_overhead) / (1024 * 1024)
print(f"Estimated memory: {total_mb:.1f} MB")
```

**Rule of thumb:** For `connectivity=16` and `dtype='f16'`:
- ~2-3 bytes per dimension per vector for graph overhead
- Total ≈ `n_vectors × ndim × (dtype_bytes + 2.5)`

## Data Types and NumPy Compatibility

USearch works seamlessly with NumPy arrays:

```python
import numpy as np
from usearch.index import Index

index = Index(ndim=3)

# Single vector (1D array)
vector_1d = np.array([0.2, 0.6, 0.4])
index.add(1, vector_1d)

# Batch of vectors (2D array)
vectors_2d = np.array([
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6],
    [0.7, 0.8, 0.9]
])
keys = [10, 20, 30]
index.add(keys, vectors_2d)

# dtype compatibility
float32_vectors = vectors_2d.astype(np.float32)
float16_vectors = vectors_2d.astype(np.float16)
int8_vectors = ((vectors_2d * 127).astype(np.int8))
```

**Supported NumPy dtypes:**
- `np.float64` → `ScalarKind.F64`
- `np.float32` → `ScalarKind.F32`
- `np.float16` → `ScalarKind.F16`
- `np.int8` → `ScalarKind.I8`
- `np.uint8` → `ScalarKind.B1` (for binary)

## Key Types and ID Capacity

USearch supports different key types for addressing vectors:

| Key Type | Range | Use Case |
|----------|-------|----------|
| `uint32_t` | 0 to 4.2B | Default, most applications |
| `uint40_t` | 0 to 1T+ | Billion-scale indexes (C++ only) |
| `uint64_t` | 0 to 18Q | Maximum capacity (Python uses this) |

**Python:** Uses 64-bit keys by default (`np.uint64`)
```python
index = Index(ndim=256)
index.add(9_999_999_999, vector)  # Large key works fine
```

**C++:** Choose key type at compile time:
```cpp
// 32-bit keys (default)
using index_t = unum::usearch::index_dense_t<>;

// 40-bit keys for billion-scale
using index_big_t = unum::usearch::index_dense_t<unum::usearch::uint40_t>;

// 64-bit keys
using index_64_t = unum::usearch::index_dense_t<uint64_t>;
```

## Best Practices

### Choosing the Right Configuration

**Text embeddings (768-1536 dimensions):**
```python
index = Index(
    ndim=768,
    metric='cos',      # Cosine similarity for text
    dtype='bf16',      # Half precision with good accuracy
    connectivity=16,   # Balanced graph
    expansion_add=128, # Good recall
    expansion_search=64
)
```

**Image embeddings (2048+ dimensions):**
```python
index = Index(
    ndim=2048,
    metric='cos',
    dtype='f16',       # f16 for high-dimensional images
    connectivity=16,
    expansion_add=200, # Higher EF for complex space
    expansion_search=100
)
```

**Geospatial (2 dimensions):**
```python
index = Index(
    ndim=2,            # [latitude, longitude]
    metric='haversine',
    dtype='f32',       # Full precision for coordinates
    connectivity=16,
    expansion_add=128,
    expansion_search=64
)
```

**Molecular fingerprints (binary, 2048 bits):**
```python
index = Index(
    ndim=2048,
    metric='tanimoto', # Tanimoto coefficient for molecules
    dtype='b1',        # Binary storage (1 bit per dimension)
    connectivity=16,
    expansion_add=128,
    expansion_search=64
)
```

### Memory vs Speed Trade-offs

**Memory-optimized:**
```python
index = Index(
    ndim=768,
    dtype='i8',        # 1 byte per dimension (cosine only)
    connectivity=8,    # Fewer graph edges
    expansion_search=32  # Faster, slightly less accurate search
)
```

**Speed-optimized:**
```python
index = Index(
    ndim=768,
    dtype='f32',       # Full precision for accuracy
    connectivity=16,
    expansion_add=256, # High-quality indexing
    expansion_search=128  # Thorough search
)
```

**Balanced (recommended default):**
```python
index = Index(
    ndim=768,
    dtype='bf16',      # Modern CPU optimization
    connectivity=16,
    expansion_add=128,
    expansion_search=64
)
```

## Common Pitfalls

### Dimension Mismatch

```python
index = Index(ndim=768)

# ERROR: Adding vector with wrong dimension
wrong_vector = np.array([0.1, 0.2, 0.3])  # Only 3 dimensions!
index.add(1, wrong_vector)  # Will raise error

# CORRECT: Match dimensions
correct_vector = np.random.rand(768).astype(np.float32)
index.add(1, correct_vector)
```

### Metric-Type Mismatch

```python
# ERROR: Using i8 quantization with non-cosine metric
index_wrong = Index(ndim=256, metric='l2sq', dtype='i8')  # Invalid!

# CORRECT: i8 only works with cosine-like metrics
index_correct = Index(ndim=256, metric='cos', dtype='i8')
```

### Binary Metric Requirements

```python
# ERROR: Using tanimoto with float vectors
index_wrong = Index(ndim=256, metric='tanimoto', dtype='f32')

# CORRECT: Binary metrics require b1 dtype
index_correct = Index(ndim=256, metric='tanimoto', dtype='b1')
binary_vectors = np.packbits(fingerprint_matrix, axis=1)  # Convert to binary
```

### Quantization Precision Loss

```python
# WARNING: Cannot recover exact original after quantization
index = Index(ndim=256, dtype='i8')
original = np.array([0.123456789, ...], dtype=np.float32)
index.add(1, original)
retrieved = index[1]  # Quantized version, not exact original!

# SOLUTION: Store originals externally if needed
vectors_cache = {1: original.copy()}
```
