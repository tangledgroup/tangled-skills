# USearch Troubleshooting Guide

Common issues, performance tuning tips, and debugging techniques for USearch 2.24.

## Common Issues

### Dimension Mismatch Errors

**Symptom:** `ValueError` when adding or searching vectors.

**Cause:** Vector dimensions don't match index `ndim`.

```python
index = Index(ndim=768)

# ERROR: Wrong dimension
wrong_vector = np.array([0.1, 0.2, 0.3])  # Only 3 dimensions
index.add(1, wrong_vector)  # ValueError!
```

**Solution:** Ensure vectors match index dimensions:

```python
# Check vector shape before adding
vector = np.array([0.1, 0.2, 0.3])
assert vector.shape[0] == index.ndim, f"Expected {index.ndim} dims, got {vector.shape[0]}"

# Or reshape if needed
if vector.ndim == 1 and vector.shape[0] != index.ndim:
    raise ValueError(f"Dimension mismatch: {vector.shape[0]} vs {index.ndim}")

# For batch operations
vectors = np.random.rand(100, 768).astype(np.float32)
assert vectors.shape[1] == index.ndim
```

### Quantization Precision Loss

**Symptom:** Retrieved vectors differ from originals after using `dtype='i8'` or `dtype='f16'`.

```python
index = Index(ndim=256, dtype='i8')
original = np.array([0.123456789, ...], dtype=np.float32)
index.add(1, original)
retrieved = index[1]  # Not equal to original!

np.allclose(original, retrieved)  # False
```

**Cause:** Quantization reduces precision for memory efficiency.

**Solutions:**

1. **Store originals externally:**
```python
vectors_cache = {}

index = Index(ndim=256, dtype='i8')
index.add(42, original_vector)
vectors_cache[42] = original_vector.copy()  # Keep original
```

2. **Use higher precision dtype:**
```python
# Instead of i8 (1 byte), use f32 (4 bytes)
index = Index(ndim=256, dtype='f32')
```

3. **Accept tolerance in comparisons:**
```python
# Use loose tolerance for quantized comparisons
np.allclose(original, retrieved, atol=0.1)  # May pass with high tolerance
```

**Quantization accuracy guidelines:**
- `dtype='i8'`: ~98-99% recall for cosine metrics
- `dtype='f16'`: ~99-99.5% recall
- `dtype='bf16'`: ~99-99.5% recall (recommended)
- `dtype='f32'`: Near-exact, minimal loss

### Metric-Type Incompatibility

**Symptom:** Unexpected results or errors with certain metric/dtype combinations.

**Invalid Combinations:**

```python
# ERROR: i8 quantization only works with cosine-like metrics
index = Index(ndim=256, metric='l2sq', dtype='i8')  # Invalid!

# ERROR: Binary metrics require b1 dtype
index = Index(ndim=256, metric='tanimoto', dtype='f32')  # Invalid!
```

**Valid Combinations:**

```python
# Cosine metrics with quantization
index_cos_i8 = Index(ndim=256, metric='cos', dtype='i8')  # OK
index_cos_f16 = Index(ndim=256, metric='cos', dtype='f16')  # OK

# L2 distance with float types
index_l2_f32 = Index(ndim=256, metric='l2sq', dtype='f32')  # OK
index_l2_f16 = Index(ndim=256, metric='l2sq', dtype='f16')  # OK

# Binary metrics with b1
index_tanimoto = Index(ndim=2048, metric='tanimoto', dtype='b1')  # OK
index_hamming = Index(ndim=2048, metric='hamming', dtype='b1')  # OK
```

**Solution:** Match metrics with appropriate dtypes:

| Metric Type | Valid dtypes |
|-------------|--------------|
| Cosine/IP | f64, f32, bf16, f16, i8 |
| L2sq | f64, f32, bf16, f16 |
| Haversine | f64, f32 |
| Hamming/Tanimoto/Sorensen | b1 only |

### Hardware Acceleration Not Detected

**Symptom:** `hardware_acceleration` returns 'none' despite having modern CPU.

```python
index = Index(ndim=768, dtype='f16')
print(index.hardware_acceleration)  # 'none' (unexpected)
```

**Diagnosis:**

1. **Check library build flags:**
```python
from usearch.index import USES_SIMSIMD, USES_FP16LIB

print(f"SimSIMD enabled: {USES_SIMSIMD}")
print(f"FP16Lib enabled: {USES_FP16LIB}")
```

2. **Verify dimension compatibility:**
```python
# Some accelerations require specific dimension multiples
for ndim in [128, 256, 512, 768, 1024]:
    idx = Index(ndim=ndim, dtype='f16')
    print(f"ndim={ndim}: {idx.hardware_acceleration}")
```

3. **Check CPU instructions:**
```bash
# Linux
lscpu | grep -E 'AVX|SSE'

# Check for AVX-512
cat /proc/cpuinfo | grep avx512
```

**Solutions:**

1. **Reinstall with proper build:**
```bash
pip uninstall usearch
pip install --upgrade --no-cache-dir usearch
```

2. **Use compatible dimensions:** Some accelerations work best with dimensions divisible by 16, 32, or 64.

3. **Accept scalar fallback:** USearch still works without hardware acceleration, just slower.

### Memory Usage Exceeds Expectations

**Symptom:** Index uses more RAM than expected.

**Diagnosis:**

```python
import sys
import numpy as np

index = Index(ndim=768, dtype='f32')
vectors = np.random.rand(100_000, 768).astype(np.float32)
index.add(np.arange(100_000), vectors)

# Estimate memory usage
n_vectors = len(index)
ndim = index.ndim
dtype_bytes = 4 if index.dtype == ScalarKind.F32 else 2

# Vector storage
vector_memory = n_vectors * ndim * dtype_bytes

# Graph structure (approximate)
graph_memory = n_vectors * index.connectivity * 4  # 4 bytes per neighbor ref

total_mb = (vector_memory + graph_memory) / (1024 * 1024)
print(f"Estimated: {total_mb:.1f} MB")
```

**Expected memory formula:**
```
Total ≈ n_vectors × (ndim × dtype_bytes + connectivity × 4)
```

For `n=1M, ndim=768, dtype=f16, connectivity=16`:
- Vectors: 1M × 768 × 2 = 1.5 GB
- Graph: 1M × 16 × 4 = 64 MB
- **Total: ~1.6 GB**

**Solutions:**

1. **Use lower precision dtype:**
```python
# Instead of f32 (4 bytes), use bf16 or f16 (2 bytes)
index = Index(ndim=768, dtype='bf16')  # 50% memory reduction
```

2. **Reduce connectivity:**
```python
# Lower connectivity = smaller graph
index = Index(ndim=768, connectivity=8)  # Half the graph edges
```

3. **Use disk viewing:**
```python
# Memory-map instead of loading
index = Index.restore('large_index.usearch', view=True)
```

4. **Shard into multiple indexes:**
```python
# Split across multiple smaller indexes
indexes = [Index(ndim=768) for _ in range(4)]
# Each uses 1/4 the memory
```

### Low Recall or Poor Search Quality

**Symptom:** Search results don't include expected nearest neighbors.

**Diagnosis:**

```python
from usearch.eval import self_recall

stats = self_recall(index, exact=False)
print(f"Recall@1: {stats.recall_1:.4f}")

# Expected: >0.99 for well-configured index
# Low recall: <0.95
```

**Causes and Solutions:**

1. **Insufficient expansion during indexing:**
```python
# Increase expansion_add for better quality
index = Index(
    ndim=768,
    expansion_add=256  # Higher than default 128
)
```

2. **Insufficient expansion during search:**
```python
# Search with higher expansion
matches = index.search(query, 10, expansion=128)  # Higher than default 64
```

3. **Low connectivity:**
```python
# Increase connectivity for better graph
index = Index(ndim=768, connectivity=32)  # Higher than default 16
```

4. **Quantization loss:**
```python
# Use higher precision if recall is critical
index = Index(ndim=768, dtype='f32')  # Instead of 'i8' or 'f16'
```

**Trade-off matrix:**

| Configuration | Recall@1 | Indexing Speed | Search Speed | Memory |
|---------------|----------|----------------|--------------|--------|
| connectivity=8, exp_add=64, dtype=i8 | ~97% | Fastest | Fastest | Lowest |
| connectivity=16, exp_add=128, dtype=bf16 | ~99% | Fast | Fast | Low |
| connectivity=32, exp_add=256, dtype=f32 | ~99.5% | Slow | Moderate | Highest |

### Serialization/Deserialization Errors

**Symptom:** Index fails to save or load.

**Common Issues:**

1. **File permissions:**
```python
try:
    index.save('/protected/path/index.usearch')
except PermissionError:
    # Use writable directory
    index.save('./index.usearch')
```

2. **Insufficient disk space:**
```python
import os

# Estimate file size before saving
estimated_size = len(index) * index.ndim * 2  # Rough estimate for f16
print(f"Estimated size: {estimated_size / (1024*1024):.1f} MB")

# Check available space
import shutil
drive, _ = os.path.splitdrive('./')
total, used, free = shutil.disk_usage(drive)
print(f"Available: {free / (1024*1024*1024):.1f} GB")
```

3. **Corrupted file:**
```python
try:
    index.load('corrupted.usearch')
except Exception as e:
    print(f"Load failed: {e}")
    # Try to recover metadata
    meta = Index.metadata('corrupted.usearch')
    print(f"Metadata: {meta}")
```

**Best Practices:**

```python
# Always save with backup
import shutil

index.save('index.usearch')
shutil.copy('index.usearch', 'index.usearch.backup')

# Verify after save
index_verify = Index.restore('index.usearch')
assert len(index) == len(index_verify)
```

## Performance Tuning

### Benchmarking Your Setup

```python
import numpy as np
import time
from usearch.index import Index, self_recall

# Create test index
ndim = 768
n_vectors = 100_000

index = Index(ndim=ndim, metric='cos', dtype='bf16')
vectors = np.random.rand(n_vectors, ndim).astype(np.float32)
keys = np.arange(n_vectors)

# Benchmark indexing
start = time.time()
index.add(keys, vectors, threads=4)
index_time = time.time() - start
print(f"Indexing: {n_vectors / index_time:.0f} vectors/second")

# Benchmark search
query = np.random.rand(ndim).astype(np.float32)
n_queries = 1000

start = time.time()
for _ in range(n_queries):
    index.search(query, 10)
search_time = time.time() - start
print(f"Search: {n_queries / search_time:.0f} queries/second")

# Measure recall
stats = self_recall(index, exact=False)
print(f"Recall@1: {stats.recall_1:.4f}")
```

### Parameter Tuning Guide

**For maximum speed (prototyping):**
```python
index = Index(
    ndim=768,
    dtype='i8',           # Smallest memory footprint
    connectivity=8,       # Fewest graph edges
    expansion_add=64,     # Fastest indexing
    expansion_search=32   # Fastest search
)
# Expect ~95-97% recall
```

**For balanced performance (production):**
```python
index = Index(
    ndim=768,
    dtype='bf16',         # Good accuracy with modern CPUs
    connectivity=16,      # Balanced graph
    expansion_add=128,    # Good quality indexing
    expansion_search=64   # Good quality search
)
# Expect ~99% recall
```

**For maximum accuracy (critical applications):**
```python
index = Index(
    ndim=768,
    dtype='f32',          # Full precision
    connectivity=32,      # Dense graph
    expansion_add=256,    # Highest quality indexing
    expansion_search=128  # Thorough search
)
# Expect >99.5% recall
```

### Multi-Threading Optimization

**Batch operations with threads:**

```python
# Single-threaded (sequential)
index.add(keys, vectors, threads=1)

# Auto-detect CPU cores
index.add(keys, vectors, threads=0)  # 0 = auto

# Specify thread count
index.add(keys, vectors, threads=8)

# For search
matches = index.search(queries, 10, threads=4)
```

**Thread count guidelines:**
- `threads=0`: Auto-detect (recommended)
- `threads=1`: Single-threaded (debugging)
- `threads=N`: Use N cores (tune based on workload)

**Optimal thread count:**
```python
import os

# Usually good to use all available CPUs
n_cpus = os.cpu_count()
print(f"Available CPUs: {n_cpus}")

# For I/O-bound workloads, use fewer threads
optimal_threads = min(n_cpus, 8)
```

### Cache Optimization

**Prefetching for sequential access:**

```python
# USearch automatically prefetches during search
# For custom workloads, ensure sequential memory access

# Good: Sequential key access
for key in range(len(index)):
    vector = index[key]

# Less optimal: Random access
import random
for key in random.sample(range(len(index)), 1000):
    vector = index[key]  # More cache misses
```

**Memory alignment:**

USearch handles alignment internally, but for custom metrics:

```python
from numba import cfunc, types

# Ensure arrays are contiguous
@cfunc(types.float32(types.CPointer(types.float32), types.CPointer(types.float32)))
def metric(a, b):
    # Arrays are guaranteed to be properly aligned
    pass
```

## Debugging Techniques

### Enable Verbose Output

```python
# Progress bars for large operations
index.add(keys, vectors, log=True)

# Custom progress callback
def verbose_progress(processed, total):
    percent = (processed / total) * 100
    print(f"\rProgress: {percent:.1f}% ({processed}/{total})", end='')
    return True

index.add(keys, vectors, progress=verbose_progress)
```

### Inspect Index State

```python
# Basic properties
print(f"Size: {len(index)}")
print(f"Dimensions: {index.ndim}")
print(f"Metric: {index.metric_kind}")
print(f"Dtype: {index.dtype}")
print(f"Connectivity: {index.connectivity}")

# Memory estimate
n = len(index)
d = index.ndim
bytes_per_elem = 2 if index.dtype == ScalarKind.F16 else 4
estimated_mb = n * d * bytes_per_elem / (1024 * 1024)
print(f"Estimated vector storage: {estimated_mb:.1f} MB")

# Hardware info
print(f"Hardware acceleration: {index.hardware_acceleration}")
```

### Compare Exact vs Approximate

```python
from usearch.index import search, MetricKind

vectors = np.random.rand(1000, 256).astype(np.float32)
query = np.random.rand(256).astype(np.float32)

# Exact search (brute-force)
exact_matches = search(vectors, query, 10, MetricKind.Cos, exact=True)

# Approximate search (HNSW)
index = Index(ndim=256, metric='cos')
index.add(np.arange(1000), vectors)
approx_matches = index.search(query, 10)

# Compare results
print("Exact keys:", [m.key for m in exact_matches])
print("Approx keys:", [m.key for m in approx_matches])

# Check if top match matches
if exact_matches[0].key == approx_matches[0].key:
    print("✓ Top match agrees")
else:
    print("✗ Top match differs")
```

### Profile Search Performance

```python
from usearch.eval import self_recall

# Get detailed stats
stats = self_recall(index, exact=False)

print(f"Recall@1: {stats.recall_1:.4f}")
print(f"Visited nodes: {stats.visited_members}")
print(f"Computed distances: {stats.computed_distances}")
print(f"Efficiency: {stats.computed_distances / stats.visited_members:.2f} distances/node")

# High efficiency = good graph structure
# Low recall = need better parameters
```

### Check for Duplicate Keys

```python
# When multi=False, adding same key twice overwrites
index = Index(ndim=3, multi=False)
index.add(42, np.array([1.0, 0.0, 0.0]))
index.add(42, np.array([0.0, 1.0, 0.0]))  # Overwrites first

# Only second vector is stored
retrieved = index[42]
print(retrieved)  # [0.0, 1.0, 0.0]

# For multiple vectors per key, use multi=True
index_multi = Index(ndim=3, multi=True)
index_multi.add(42, np.array([1.0, 0.0, 0.0]))
index_multi.add(42, np.array([0.0, 1.0, 0.0]))  # Both stored
```

## Platform-Specific Issues

### Windows

**Issue:** SIMD instructions not available on older CPUs.

**Solution:** USearch falls back to scalar operations automatically.

```python
# Check detected acceleration
index = Index(ndim=256)
print(index.hardware_acceleration)  # May be 'none' on older CPUs
```

### macOS (Apple Silicon)

**Issue:** ARM-specific optimizations may differ from x86.

**Solution:** Use universal builds or ARM-specific wheels.

```bash
# Check Python architecture
python -c "import platform; print(platform.machine())"  # Should be 'arm64'

# Reinstall if needed
pip uninstall usearch
pip install --no-cache-dir usearch
```

### Linux (ARM/Graviton)

**Issue:** NEON/SVE optimizations require proper build.

**Solution:** Verify SimSIMD support:

```python
from usearch.index import USES_SIMSIMD

print(f"SimSIMD enabled: {USES_SIMSIMD}")  # Should be True
```

### Docker Containers

**Issue:** Missing CPU instruction support in container.

**Solution:** Pass CPU flags to container:

```bash
# Run with proper CPU features
docker run --privileged --cpuset-cpus="0-7" your_image

# Or specify platform
docker run --platform linux/amd64 your_image
```

## Best Practices Summary

1. **Match metric and dtype:** Use compatible combinations (see table above)
2. **Start with defaults:** `connectivity=16, expansion_add=128, expansion_search=64`
3. **Use bf16 for modern hardware:** Better accuracy than f16 on most CPUs
4. **Monitor recall:** Use `self_recall()` to verify quality
5. **Save backups:** Always keep backup of important indexes
6. **Use viewing for large indexes:** Memory-map to reduce RAM usage
7. **Parallelize batch operations:** Use `threads` parameter for speed
8. **Profile before optimizing:** Measure actual performance first
9. **Store originals if needed:** Quantization loses precision
10. **Test with exact search:** Compare HNSW results against brute-force

## Getting Help

If issues persist:

1. Check USearch version: `import usearch; print(usearch.__version__)`
2. Verify NumPy compatibility: `import numpy; print(numpy.__version__)`
3. Review build flags: `from usearch.index import USES_SIMSIMD, USES_OPENMP, USES_FP16LIB`
4. Check GitHub issues: https://github.com/unum-cloud/usearch/issues
5. Provide minimal reproducible example when asking for help
