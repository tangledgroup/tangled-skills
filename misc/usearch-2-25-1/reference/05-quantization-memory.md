# Quantization and Memory

## Data Types

USearch supports automatic casting between input precision and storage precision. The `dtype` parameter on Index construction determines how vectors are stored:

- **f64** — 64-bit double precision, maximum accuracy
- **f32** — 32-bit float, default NumPy type
- **bf16** — BFloat16, recommended default for modern CPUs (Intel AVX-512 BF16 support)
- **f16** — IEEE 754 half precision, widely supported
- **e5m2** — Float8, wider range (+/- 57344), MX-compatible
- **e4m3** — Float8, higher precision (+/- 448), MX-compatible
- **e3m2** — Float6, padded to 8 bits (+/- 28), MX-compatible
- **e2m3** — Float6, padded to 8 bits (+/- 7.5), MX-compatible
- **u8** — Unsigned 8-bit integers
- **i8** — Signed 8-bit integers (valid only for cosine-like metrics)
- **b1** — Single-bit representations (valid only for binary metrics: Jaccard, Hamming, etc.)

When no `dtype` is specified, USearch selects hardware-dependent defaults for efficiency.

## Quantization Behavior

- Vectors are automatically down-cast or up-cast between types during add and search
- When quantizing to i8, vectors are normalized to unit length then scaled to [-127, 127]
- When quantizing to b1, scalar components > 0 become `true`, rest become `false`
- After quantization, `get()` cannot recover original precision — store originals elsewhere if needed

## NumKong Interop

For types not natively representable in NumPy (bf16, e5m2, e4m3, e3m2, e2m3), pre-quantize with NumKong and pass raw buffers:

```python
import numkong as nk
import numpy as np
from usearch.index import Index

vectors_f32 = np.random.rand(1000, 256).astype(np.float32)
keys = np.arange(1000)

# Option 1: Let USearch quantize internally
index = Index(ndim=256, metric='cos', dtype='e4m3')
index.add(keys, vectors_f32)

# Option 2: Pre-quantize with NumKong and pass raw buffers
vectors_e4m3 = np.asarray(nk.Tensor(vectors_f32).astype('e4m3'))
index2 = Index(ndim=256, metric='cos', dtype='e4m3')
index2.add(keys, vectors_e4m3, dtype='e4m3')
matches = index2.search(vectors_e4m3[:5], 10, dtype='e4m3')
```

## Memory-Mapped Disk Serving

USearch supports serving indexes from disk without loading into RAM:

```python
# Save
index.save('index.usearch')

# Load into memory
index.load('index.usearch')

# Memory-map (no RAM load) — enables 20x cost reduction on AWS
view = Index.restore('index.usearch', view=True)
# or
other_view = Index(ndim=..., metric=...)
other_view.view('index.usearch')
```

The file format supports three serialization modes:
1. **File path** — Direct disk I/O
2. **Stream callback** — Incremental serialization/reconstruction
3. **Fixed buffer / memory-mapped file** — Random access, enables external memory serving

## Multi-Index Lookups (Indexes)

For workloads targeting billions or trillions of vectors, build multiple smaller indexes and query them together:

```python
from usearch.index import Indexes

multi_index = Indexes(
    indexes=[index_a, index_b, index_c],  # Iterable[Index]
    # or
    paths=['shard1.usearch', 'shard2.usearch'],  # Iterable[PathLike]
    view=False,   # Memory-map shards
    threads=0,    # Parallel search across shards
)
matches = multi_index.search(query_vector, 10)
```

## Key Types and Capacity

Default key type is `uint32_t` (up to 4 billion entries). For larger indexes, use `uint40_t`:

- **uint32_t** — 32-bit, up to 4B entries (default)
- **uint40_t** — 40-bit, up to 1 trillion entries, 37.5% smaller than uint64
- **uint64_t** — 64-bit, full range

The `uint40_t` type is a USearch custom type that balances memory efficiency with capacity. It is available in C++ via `index_dense_big_t` or the template `index_dense_gt<vector_key_t, internal_id_t>`.

## Memory Usage Monitoring

```python
index.memory_usage        # Bytes consumed by the index
index.serialized_length   # Bytes needed for serialization
index.capacity            # Max vectors without reallocation
index.size                # Current vector count
```
