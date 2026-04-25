# Quantization & Precision

> **Source:** https://github.com/unum-cloud/usearch
> **Loaded from:** SKILL.md (via progressive disclosure)

## Supported Data Types

USearch supports automatic casting between input types and storage types. The `add` and `search` operations handle up-casting and down-casting transparently.

| `dtype` | Bits | Best For |
|---------|------|----------|
| `f64` | 64 | Maximum precision |
| `f32` | 32 | Default NumPy type |
| `bf16` | 16 | Recommended default on modern CPUs |
| `f16` | 16 | Widely supported half-precision |
| `e5m2` | 8 | Float8, wider range (±57344) |
| `e4m3` | 8 | Float8, higher precision (±448) |
| `e3m2` | 6, padded to 8 | Float6, MX-compatible (±28) |
| `e2m3` | 6, padded to 8 | Float6, MX-compatible (±7.5) |
| `i8` | 8 | Cosine-like metrics only |
| `u8` | 8 | Cosine-like metrics only |
| `b1` | 1 | Binary metrics (Hamming, Tanimoto, Sorensen) |

## Recommendations

- `bf16` is recommended for most modern CPUs as the default storage format
- For cosine-like metrics, `i8` quantization normalizes vectors to unit length and scales to [-127, 127]
- Binary (`b1`) quantization maps positive values to `1` and zero/negative to `0`
- When quantization is enabled, retrieval functions cannot recover original data

## Hardware Acceleration Check

```python
from usearch.index import Index

index = Index(ndim=768, metric='cos', dtype='f16')
print(index.hardware_acceleration)  # e.g. 'sapphire' (Sapphire Rapids AVX-512)

index2 = Index(ndim=166, metric='tanimoto')
print(index2.hardware_acceleration)  # e.g. 'ice'
```

## Pre-Quantization with NumKong

For types not natively representable in NumPy (`bf16`, `e5m2`, `e4m3`, `e3m2`, `e2m3`), pre-quantize with NumKong and pass raw buffers:

```python
import numkong as nk
import numpy as np
from usearch.index import Index

vectors_f32 = np.random.rand(1000, 256).astype(np.float32)
keys = np.arange(1000)

# Option 1: let USearch quantize internally
index = Index(ndim=256, metric='cos', dtype='e4m3')
index.add(keys, vectors_f32)

# Option 2: pre-quantize with NumKong and pass raw buffers
vectors_e4m3 = np.asarray(nk.Tensor(vectors_f32).astype('e4m3'))
index2 = Index(ndim=256, metric='cos', dtype='e4m3')
index2.add(keys, vectors_e4m3, dtype='e4m3')
matches = index2.search(vectors_e4m3[:5], 10, dtype='e4m3')
```

## Key Size Options

By default, 32-bit `uint32_t` keys are used. For datasets exceeding 4 billion entries:

- `uint40_t`: Supports up to 1 trillion entries, 37.5% smaller than `uint64_t`
- `uint64_t`: Full 64-bit key space

In C++, use `index_dense_big_t` for 4B+ capacity or instantiate `index_dense_gt<vector_key_t, internal_id_t>` with custom types.
