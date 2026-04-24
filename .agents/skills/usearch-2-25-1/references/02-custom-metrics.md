# User-Defined Metrics & JIT Compilation

> **Source:** https://github.com/unum-cloud/usearch
> **Loaded from:** SKILL.md (via progressive disclosure)

## Overview

USearch allows arbitrary user-defined distance metrics, enabling custom search for applications like composite embeddings, geospatial queries with Vincenty formula, or hybrid full-text and semantic search. This is one of USearch's key differentiators from FAISS (which supports only 9 fixed metrics).

## Python: Numba JIT

Define a compiled metric function using Numba's `@cfunc` decorator:

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric

ndim = 256
signature = types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32))

@cfunc(signature)
def inner_product(a, b):
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    c = 0.0
    for i in range(ndim):
        c += a_array[i] * b_array[i]
    return 1 - c

metric = CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
index = Index(ndim=ndim, metric=metric, dtype=np.float32)
```

### With Dynamic Dimension Size

Pass `ndim` as a third argument to avoid hardcoding:

```python
signature = types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32),
    types.uint64)

@cfunc(signature)
def inner_product(a, b, ndim):
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    c = 0.0
    for i in range(ndim):
        c += a_array[i] * b_array[i]
    return 1 - c

metric = CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
)
```

## Python: Cppyy (Cling JIT)

Use Cppyy to JIT-compile native C++ code with explicit optimizations like loop unrolling:

```python
import cppyy
import cppyy.ll

ndim = 256
cppyy.cppdef("""
float inner_product(float *a, float *b) {
    float result = 0;
#pragma unroll
    for (size_t i = 0; i != 256; ++i)
        result += a[i] * b[i];
    return 1 - result;
}
""".replace("256", str(ndim)))

function = cppyy.gbl.inner_product
index = Index(ndim=ndim, metric=CompiledMetric(
    pointer=cppyy.ll.addressof(function),
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
))
```

## Python: PeachPy (Assembly)

Write x86 assembly directly for maximum performance. Example for 8-dimensional f32 inner product using AVX2:

```python
from peachpy import Argument, ptr, float_, const_float_
from peachpy.x86_64 import (abi, Function, uarch, isa,
    GeneralPurposeRegister64, LOAD, YMMRegister,
    VMOVUPS, VFMADD231PS, VPERM2F128, VADDPS,
    VHADDPS, VXORPS, VSUBPS, RETURN)

a = Argument(ptr(const_float_), name="a")
b = Argument(ptr(const_float_), name="b")

with Function("inner_product", (a, b), float_,
              target=uarch.default + isa.avx2) as asm_function:
    reg_a, reg_b = GeneralPurposeRegister64(), GeneralPurposeRegister64()
    LOAD.ARGUMENT(reg_a, a)
    LOAD.ARGUMENT(reg_b, b)

    ymm_a, ymm_b = YMMRegister(), YMMRegister()
    VMOVUPS(ymm_a, [reg_a])
    VMOVUPS(ymm_b, [reg_b])

    ymm_c = YMMRegister()
    VXORPS(ymm_c, ymm_c, ymm_c)
    VFMADD231PS(ymm_c, ymm_a, ymm_b)

    ymm_c_permuted = YMMRegister()
    VPERM2F128(ymm_c_permuted, ymm_c, ymm_c, 1)
    VADDPS(ymm_c, ymm_c, ymm_c_permuted)
    VHADDPS(ymm_c, ymm_c, ymm_c)
    VHADDPS(ymm_c, ymm_c, ymm_c)

    ymm_one = YMMRegister()
    VXORPS(ymm_one, ymm_one, ymm_one)
    VSUBPS(ymm_c, ymm_one, ymm_c)
    RETURN(ymm_c.as_xmm)

python_function = asm_function.finalize(abi.detect()).encode().load()
metric = CompiledMetric(
    pointer=python_function.loader.code_address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
index = Index(ndim=8, metric=metric)
```

## Rust: Custom Metrics

Define a closure and pass it to `change_metric`:

```rust
use numkong::SpatialSimilarity;

let image_dimensions = 768;
let text_dimensions = 512;
let image_weights = 0.7f32;
let text_weights = 0.9f32;

let weighted_distance = Box::new(move |a: *const f32, b: *const f32| unsafe {
    let a_slice = std::slice::from_raw_parts(a, image_dimensions + text_dimensions);
    let b_slice = std::slice::from_raw_parts(b, image_dimensions + text_dimensions);

    let image_sim = f32::cosine(&a_slice[0..image_dimensions], &b_slice[0..image_dimensions]);
    let text_sim = f32::cosine(&a_slice[image_dimensions..], &b_slice[image_dimensions..]);
    let similarity = image_weights * image_sim + text_weights * text_sim / (image_weights + text_weights);

    1.0 - similarity
});

index.change_metric(weighted_distance);
// Revert to native metric:
index.change_metric_kind(MetricKind::Cos);
```

## C: Custom Metrics

Implement the `usearch_metric_t` callback interface:

```c
usearch_distance_t callback(void const* a, void const* b, void* state) {
    // Custom metric implementation
    return distance;
}

void* callback_state = NULL;
usearch_change_metric(index, callback, callback_state, usearch_metric_unknown_k, &error);

// Revert to native metric:
usearch_change_metric_kind(index, usearch_metric_cos_k, &error);
```

## Variable-Length Vectors

Unlike KD-Trees and LSH, HNSW does not require vectors to be identical in length — they only need to be comparable. This enables applications like searching for similar sets or fuzzy text matching using compression-ratio as a distance function.
