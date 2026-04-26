# Distance Metrics

## Built-in Metrics

USearch provides these distance metrics out of the box, with NumKong providing SIMD-accelerated backends for most on x86 and ARM:

- **Cosine** (`cos`) — Angular distance, `1 - dot(a,b) / (||a|| * ||b||)`. Default metric.
- **L2 Squared** (`l2sq`) — Euclidean distance squared, `sum((a[i] - b[i])^2)`.
- **Inner Product** (`ip`) — `1 - sum(a[i] * b[i])`. Requires normalized vectors for meaningful similarity.
- **Haversine** (`haversine`) — Great circle distance between lat/lon coordinates, used in GIS.
- **Jaccard** (`jaccard`) — Distance between ordered sets of unique elements.
- **Hamming** (`hamming`) — Number of differing bits, for binary fingerprints.
- **Tanimoto** (`tanimoto`) — Jaccard coefficient for bit-strings, common in cheminformatics.
- **Sorensen** (`sorensen`) — Dice-Sorensen coefficient for bit-strings.
- **Pearson** (`pearson`) — Correlation between probability distributions.
- **Divergence** (`divergence`) — Jensen-Shannon similarity between probability distributions.

## User-Defined Metrics in Python

USearch allows arbitrary distance functions compiled at runtime through three approaches:

### Numba JIT

Compile a C-compatible function and pass its address:

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric

ndim = 256

@cfunc(types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32)))
def inner_product(a, b):
    a_arr = carray(a, ndim)
    b_arr = carray(b, ndim)
    c = 0.0
    for i in range(ndim):
        c += a_arr[i] * b_arr[i]
    return 1.0 - c

metric = CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
index = Index(ndim=ndim, metric=metric)
```

With explicit dimension parameter (avoids hardcoding ndim):

```python
@cfunc(types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32),
    types.uint64))
def inner_product(a, b, ndim):
    a_arr = carray(a, ndim)
    b_arr = carray(b, ndim)
    c = 0.0
    for i in range(ndim):
        c += a_arr[i] * b_arr[i]
    return 1.0 - c

metric = CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
)
```

### Cppyy with Cling

JIT-compile native C++ code with loop unrolling:

```python
import cppyy
import cppyy.ll

ndim = 256
cppyy.cppdef(f"""
float inner_product(float *a, float *b) {{
    float result = 0;
    #pragma unroll
    for (size_t i = 0; i != {ndim}; ++i)
        result += a[i] * b[i];
    return 1 - result;
}}
""")

function = cppyy.gbl.inner_product
metric = CompiledMetric(
    pointer=cppyy.ll.addressof(function),
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
)
index = Index(ndim=ndim, metric=metric)
```

### PeachPy — Handwritten Assembly

Write AVX2 assembly directly for maximum performance:

```python
from peachpy import Argument, ptr, float_, const_float_
from peachpy.x86_64 import (
    abi, Function, uarch, isa,
    GeneralPurposeRegister64, LOAD, YMMRegister,
    VMOVUPS, VXORPS, VFMADD231PS, VPERM2F128,
    VADDPS, VHADDPS, VSUBPS, RETURN,
)

ndim = 8
a = Argument(ptr(const_float_), name="a")
b = Argument(ptr(const_float_), name="b")

with Function("inner_product", (a, b), float_,
              target=uarch.default + isa.avx2) as asm_fn:
    reg_a, reg_b = GeneralPurposeRegister64(), GeneralPurposeRegister64()
    LOAD.ARGUMENT(reg_a, a)
    LOAD.ARGUMENT(reg_b, b)

    ymm_a = YMMRegister()
    ymm_b = YMMRegister()
    VMOVUPS(ymm_a, [reg_a])
    VMOVUPS(ymm_b, [reg_b])

    ymm_c = YMMRegister()
    VXORPS(ymm_c, ymm_c, ymm_c)  # Zero accumulator

    ymm_one = YMMRegister()
    VXORPS(ymm_one, ymm_one, ymm_one)

    VFMADD231PS(ymm_c, ymm_a, ymm_b)  # Fused multiply-add

    ymm_perm = YMMRegister()
    VPERM2F128(ymm_perm, ymm_c, ymm_c, 1)
    VADDPS(ymm_c, ymm_c, ymm_perm)
    VHADDPS(ymm_c, ymm_c, ymm_c)
    VHADDPS(ymm_c, ymm_c, ymm_c)

    VSUBPS(ymm_c, ymm_one, ymm_c)  # Negate: similarity to distance
    RETURN(ymm_c.as_xmm)

python_fn = asm_fn.finalize(abi.detect()).encode().load()
metric = CompiledMetric(
    pointer=python_fn.loader.code_address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
```

## Metric Signatures

- `MetricSignature.ArrayArray` — Function takes two array pointers: `f(float* a, float* b) -> float`
- `MetricSignature.ArrayArraySize` — Function takes two arrays plus dimension: `f(float* a, float* b, uint64 ndim) -> float`

## Variable-Length Vectors

Unlike KD-Trees or LSH, HNSW does not require identical vector lengths. Vectors only need to be comparable under the chosen metric. This enables obscure applications like fuzzy text matching using GZip compression ratio as a distance function, or set similarity search.

Variable-length vectors are supported in C++ but not yet exposed in Python bindings.

## Checking Hardware Acceleration

```python
from usearch.index import Index
print(Index(ndim=768, metric='cos', dtype='f16').hardware_acceleration)
# Output: "sapphire" (Intel Sapphire Rapids AVX-512) or "ice" (Intel Ice Lake) or "auto"
```

The return value indicates which SIMD backend is active. "auto" means no hardware acceleration matched the configuration.
