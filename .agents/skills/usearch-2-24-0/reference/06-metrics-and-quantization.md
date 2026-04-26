# Metrics and Quantization

## Built-In Metrics

USearch ships with NumKong, providing over 100 SIMD-accelerated distance kernels for x86 and ARM. The built-in metrics cover spatial, binary, probabilistic, and user-defined distances.

### Spatial Metrics

- **Cosine** (`cos`) — `1 - sum(a[i]*b[i]) / (sqrt(sum(a[i]^2) * sqrt(sum(b[i]^2)))`
- **Inner Product** (`ip`) — `1 - sum(a[i] * b[i])`, for normalized vectors
- **L2 Squared** (`l2sq`) — `sum((a[i] - b[i])^2)`
- **Haversine** (`haversine`) — Great Circle distance for GIS applications (requires 2D vectors)
- **Pearson** (`pearson`) — Correlation between probability distributions
- **Divergence** (`divergence`) — Jensen-Shannon similarity

### Binary Metrics

For bit-strings and fingerprints (genomics, chemistry):

- **Hamming** (`hamming`) — Number of differing bits
- **Tanimoto** (`tanimoto`) — Jaccard coefficient: intersection / union
- **Sorensen** (`sorensen`) — Dice-Sorensen coefficient for bit-strings

## Scalar Types and Quantization

USearch automatically casts between input type and storage type. Available scalar kinds:

- `f64` — 64-bit, maximum precision
- `f32` — 32-bit, default NumPy type
- `bf16` — 16-bit Brain Float, recommended for modern CPUs
- `f16` — 16-bit IEEE half-precision
- `e5m2` — 8-bit Float8, wider range (±57344)
- `e4m3` — 8-bit Float8, higher precision (±448)
- `e3m2` — 6-bit Float6 padded to 8, MX-compatible (±28)
- `e2m3` — 6-bit Float6 padded to 8, MX-compatible (±7.5)
- `u8` — 8-bit unsigned integer, for cosine-like metrics
- `i8` — 8-bit signed integer, for cosine-like metrics (normalized to [-127, 127])
- `b1` / `b1x8` — Single-bit packed, for binary metrics

Check hardware acceleration:

```python
from usearch.index import Index
print(Index(ndim=768, metric="cos", dtype="f16").hardware_acceleration)
# Output: sapphire (Intel Sapphire Rapids), ice (ARM SVE), etc.
```

### Quantization Notes

- `i8` and `u8`: Only valid for cosine-like metrics. Vectors are normalized to unit length then scaled to full integer range.
- `b1x8`: Only valid for binary metrics. Scalars > 0 become `true`, rest become `false`.
- When quantization is enabled, "get"-like functions cannot recover original data — replicate vectors elsewhere if needed.
- For types not natively representable in NumPy (`bf16`, `e5m2`, etc.), pre-quantize with NumKong and pass raw buffers with explicit `dtype=` parameter.

## User-Defined Metrics

USearch's key differentiator is support for arbitrary user-defined metrics. This enables:
- Custom composite embeddings (image + text)
- Hybrid full-text and semantic search
- Geospatial distances beyond Haversine (Vincenty, etc.)
- Domain-specific similarity functions

### Python with Numba

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric

ndim = 256

@cfunc(types.float32(types.CPointer(types.float32), types.CPointer(types.float32)))
def custom_metric(a, b):
    a_arr = carray(a, ndim)
    b_arr = carray(b, ndim)
    result = 0.0
    for i in range(ndim):
        result += a_arr[i] * b_arr[i]
    return 1 - result

metric = CompiledMetric(
    pointer=custom_metric.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
index = Index(ndim=ndim, metric=metric, dtype=np.float32)
```

### Python with Cppyy

```python
import cppyy
import cppyy.ll

ndim = 256
cppyy.cppdef(f"""
float custom_metric(float *a, float *b) {{
    float result = 0;
#pragma unroll
    for (size_t i = 0; i != {ndim}; ++i)
        result += a[i] * b[i];
    return 1 - result;
}}
""")

function = cppyy.gbl.custom_metric
index = Index(ndim=ndim, metric=CompiledMetric(
    pointer=cppyy.ll.addressof(function),
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
))
```

### Python with PeachPy (Assembly)

Write x86 AVX2 assembly directly for maximum performance:

```python
from peachpy import Argument, ptr, float_, const_float_
from peachpy.x86_64 import (abi, Function, uarch, isa,
    GeneralPurposeRegister64, LOAD, YMMRegister,
    VMOVUPS, VXORPS, VFMADD231PS, VPERM2F128,
    VADDPS, VHADDPS, VSUBPS, RETURN)

a = Argument(ptr(const_float_), name="a")
b = Argument(ptr(const_float_), name="b")

with Function("inner_product", (a, b), float_, target=uarch.default + isa.avx2) as asm_fn:
    reg_a, reg_b = GeneralPurposeRegister64(), GeneralPurposeRegister64()
    LOAD.ARGUMENT(reg_a, a)
    LOAD.ARGUMENT(reg_b, b)

    ymm_a = YMMRegister()
    ymm_b = YMMRegister()
    VMOVUPS(ymm_a, [reg_a])
    VMOVUPS(ymm_b, [reg_b])

    ymm_c = YMMRegister()
    VXORPS(ymm_c, ymm_c, ymm_c)
    VFMADD231PS(ymm_c, ymm_a, ymm_b)

    ymm_c_perm = YMMRegister()
    VPERM2F128(ymm_c_perm, ymm_c, ymm_c, 1)
    VADDPS(ymm_c, ymm_c, ymm_c_perm)
    VHADDPS(ymm_c, ymm_c, ymm_c)
    VHADDPS(ymm_c, ymm_c, ymm_c)

    ymm_one = YMMRegister()
    VXORPS(ymm_one, ymm_one, ymm_one)
    VSUBPS(ymm_c, ymm_one, ymm_c)
    RETURN(ymm_c.as_xmm)

python_fn = asm_fn.finalize(abi.detect()).encode().load()
metric = CompiledMetric(
    pointer=python_fn.loader.code_address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
```

### C/C++ Custom Metrics

Wrap in `metric_punned_t` (a trivial type, unlike `std::function`):

```cpp
// Implement your metric function and wrap in metric_punned_t
// NumKong provides hardware-accelerated backends for common types
```

### Rust Custom Metrics

```rust
let weighted_distance = Box::new(move |a: *const f32, b: *const f32| unsafe {
    let a_slice = std::slice::from_raw_parts(a, total_dims);
    let b_slice = std::slice::from_raw_parts(b, total_dims);
    // ... compute custom distance
    1.0 - similarity
});
index.change_metric(weighted_distance);
```

### C Custom Metrics

```c
usearch_distance_t callback(void const* a, void const* b, void* state) {
    // Custom metric implementation
}

usearch_change_metric(index, callback, NULL, usearch_metric_unknown_k, &error);
```

## Variable-Length Vectors

Unlike KD-Trees or LSH, HNSW doesn't require vectors to be identical in length — they only need to be comparable. This enables obscure applications like fuzzy text matching using GZip compression ratio as a distance function.
