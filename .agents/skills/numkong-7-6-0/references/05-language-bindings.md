# Language Bindings Deep Dive

> **Source:** NumKong README, python/README.md, include/README.md, javascript/README.md, rust/README.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## Supported Languages

| Language | Install | Platforms | Guide |
|----------|---------|-----------|-------|
| C / C++ | CMake, headers, prebuilt | Linux, macOS, Windows, Android | Native SDK (reference surface) |
| Python | `pip install numkong` | Linux, macOS, Windows | Main high-level SDK |
| Rust | `cargo add numkong` | Linux, macOS, Windows | Trait-first API |
| JavaScript | `npm install numkong` | Node.js, Bun, Deno, browsers | TypedArray-first API |
| Swift | Swift Package Manager | macOS, iOS, tvOS, watchOS | — |
| Go | `go get` | Linux, macOS, Windows (cGo) | — |

## Python SDK

The main high-level SDK. Combines NumPy-friendly buffers with native mixed-precision kernels, zero-copy tensor views, packed and symmetric matrix operations, sparse helpers, geometric mesh alignment, and MaxSim.

### Key Features Over NumPy/SciPy

- Mixed precision: BFloat16 through sub-byte (Float8, Float6, Int4, packed bits) with automatic widening
- Kahan summation; 0 ULP in Float32/Float64 where applicable
- Runtime SIMD dispatch (auto-selects best ISA per-thread)
- Packed matrix reuse: pack once, query many times
- Symmetric kernels: skip duplicate pairs, up to 2x speedup for self-distance
- `out=` parameter on all major entrypoints (avoids dynamic allocation)
- Fast CPython calling convention (direct METH_FASTCALL)
- GIL release on batched, packed, and symmetric kernels

### Python API Surface

```python
import numkong as nk

# Scalars and capabilities
nk.get_capabilities()
nk.zeros((rows, cols), dtype="float32")

# Dot products
nk.dot(a, b)
nk.vdot(a, b)  # conjugated (complex)

# Distances
nk.sqeuclidean(a, b)
nk.euclidean(a, b)
nk.angular(a, b)

# All-pairs
nk.cdist(queries, database, metric="angular")

# Set similarity
nk.hamming(a, b, dtype="uint1")
nk.jaccard(a, b, dtype="uint1")

# Probability
nk.kullbackleibler(p, q)
nk.jensenshannon(p, q)

# Geospatial
nk.vincenty(lat1, lon1, lat2, lon2)
nk.haversine(lat1, lon1, lat2, lon2)

# Curved
nk.bilinear(a, b, metric_tensor)
nk.mahalanobis(x, y, inv_covariance)

# Elementwise
nk.scale(a, alpha, beta)
nk.blend(a, b, alpha, beta)
nk.fma(a, b, c, alpha, beta)

# Reductions
nk.moments(tensor)       # (sum, sum_of_squares)
tensor.argmin()
tensor.minmax()          # (min, min_idx, max, max_idx)

# Sparse
nk.intersect(idx_a, idx_b)
nk.sparse_dot(idx_a, val_a, idx_b, val_b)

# Packed matrix
nk.dots_pack(right_matrix, dtype="float32")
nk.dots_packed(left_matrix, packed_right)

# Symmetric
nk.dots_symmetric(vectors, out=out, start_row=0, end_row=N)

# Mesh alignment
nk.kabsch(source, target)   # returns .rotation, .scale, .rmsd, .a_centroid, .b_centroid
nk.umeyama(source, target)

# MaxSim
nk.maxsim_pack(queries, dtype="float32")
nk.maxsim_packed(packed_q, packed_d)

# External memory
tensor.data_ptr              # integer address
nk.from_pointer(addr, shape, dtype, owner=obj)
```

### Tensor API

```python
t = nk.Tensor(np.arange(12, dtype=np.float32).reshape(3, 4))
t.shape, t.dtype, t.ndim, t.strides, t.itemsize, t.nbytes
np.asarray(t)              # zero-copy array view when layout allows
t.T                        # transposed Tensor view
t.reshape(2, 6)            # reshape
t.flatten()                # flatten
t[0, :]                    # row slice
t[:, 2]                    # column slice (strided)
t[1, 2]                    # scalar access
```

## C/C++ SDK

The reference surface. Stable, versioned ABI callable from any language that can load a shared library. No runtime overhead: no hidden thread pool, no implicit allocation, no garbage collector interaction.

### C API

```c
#include <numkong/numkong.h>

nk_f32_t a[] = {1, 2, 3};
nk_f32_t b[] = {4, 5, 6};
nk_f64_t dot = 0;
nk_configure_thread(nk_capabilities());
nk_dot_f32(a, b, 3, &dot);  // widened f32→f64 output

// Punned dispatch (runtime-selected kernel)
nk_metric_dense_punned_t angular = 0;
nk_capability_t used = nk_cap_serial_k;
nk_find_kernel_punned(nk_kernel_angular_k, nk_f32_k,
    nk_capabilities(), (nk_kernel_punned_t *)&angular, &used);
```

### C++ Layer

Adds type-level result promotion, explicit owning/non-owning containers, and allocator-aware packed objects:

```cpp
#include <numkong/numkong.hpp>
namespace nk = ashvardanian::numkong;

// Type-level result promotion
nk::f32_t a[3] = {1, 2, 3}, b[3] = {4, 5, 6};
nk::f64_t dot {};
nk::dot(a, b, 3, &dot);  // f32_t::dot_result_t == f64_t

// Tensor with slicing
auto t = nk::tensor<nk::f32_t>::try_from({
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9},
});
auto second_row = t[1, nk::all, nk::slice];
auto second_col = t[nk::all, 1, nk::slice];

// Packed matrix
auto packed = nk::packed_matrix<nk::f32_t>::try_pack(b.as_matrix_view());
auto dots = nk::try_dots_packed(a.as_matrix_view(), packed);

// std::mdspan interop
float data[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
auto md = std::mdspan<float, std::extents<std::size_t, 3, 3>>(data);
auto view = nk::matrix_view<nk::f32_t>(
    reinterpret_cast<nk::f32_t const *>(md.data_handle()),
    md.extent(0), md.extent(1));
```

### C++ Format Support

When `__cpp_lib_format >= 202110L`, all scalar types provide `std::formatter` specializations:

| Spec | Output | Description |
|------|--------|-------------|
| `{}` | `3.140625` | Clean float value |
| `{:#}` | `3.140625 [0x4248]` | Annotated with hex bits |
| `{:x}` | `4248` | Raw hex bits |
| `{:b}` | `0100001001001000` | Binary bits |

## Rust SDK

Trait-first API with static typing, explicit ownership, and strong container APIs. Most fully featured high-level SDK after Python.

```rust
use numkong::{configure_thread, Dot, VDot, JensenShannon, Jaccard, f32c, u1x8};

fn main() {
    configure_thread();

    // Dot product
    let a = [1.0_f32, 2.0, 3.0];
    let b = [4.0_f32, 5.0, 6.0];
    let dot = f32::dot(&a, &b).unwrap();

    // Complex vdot
    let ca = [f32c { re: 1.0, im: 2.0 }, f32c { re: 3.0, im: 4.0 }];
    let cb = [f32c { re: 5.0, im: 6.0 }, f32c { re: 7.0, im: 8.0 }];
    let vdot = f32c::vdot(&ca, &cb).unwrap();

    // Binary Jaccard
    let bits_a = [u1x8(0b11110000), u1x8(0b00001111)];
    let bits_b = [u1x8(0b11110000), u1x8(0b11110000)];
    let jaccard = u1x8::jaccard(&bits_a, &bits_b).unwrap();

    // Probability
    let p = [0.2_f32, 0.3, 0.5];
    let q = [0.1_f32, 0.3, 0.6];
    let jsd = f32::jensenshannon(&p, &q).unwrap();
}
```

### Rust Traits

- `Dot`, `VDot`, `Angular`, `Euclidean`
- `Hamming`, `Jaccard`
- `KullbackLeibler`, `JensenShannon`
- `Haversine`, `Vincenty`
- `Bilinear`, `Mahalanobis`
- `ReduceMoments`, `ReduceMinMax`
- `EachScale`, `EachSum`, `EachBlend`, `EachFMA`

Standard call shape: `Type::operation(&a, &b).unwrap()`. Validates f16 and bf16 interop against the `half` crate.

## JavaScript SDK

TypedArray-first API for Node.js, Bun, Deno, and browsers. Deliberately smaller than Python or Rust — focused on hot vector kernels.

```javascript
import { dot, euclidean, angular, hamming, jaccard } from "numkong";
import { toBinary, Float16Array, E4M3Array, DType } from "numkong";

// Standard TypedArrays
const a = new Float32Array([1, 2, 3]);
const b = new Float32Array([4, 5, 6]);
console.log(dot(a, b));

// Binary metrics
const ab = toBinary(new Float32Array([1, -2, 3, -4]));
const bb = toBinary(new Float32Array([1, 2, -3, -4]));
console.log(hamming(ab, bb));

// Low-precision with dtype tags
const a16 = new Float16Array([1, 2, 3]);
const b16 = new Float16Array([4, 5, 6]);
console.log(dot(a16, b16, DType.F16));

// WASM in browser (no build step)
// <script type="module">
//   import { dot } from 'https://cdn.jsdelivr.net/npm/numkong@7/wasm/numkong.js';
// </script>
```

### JavaScript Wrapper Hierarchy

- `TensorBase` — carries buffer, byteOffset, dtype
- `VectorBase` — adds rank-1 semantics
- `VectorView` — zero-copy borrowed wrapper over existing memory
- `Vector` — owns its ArrayBuffer

## Operation Coverage by Language

| Operation | C/C++ | Python | Rust | JavaScript | Swift | Go |
|-----------|-------|--------|------|------------|-------|----|
| Dot Product | ● | ● | ● | ● | ● | ● |
| Spatial Metric | ● | ● | ● | ● | ● | ● |
| Set Similarity | ● | ● | ● | ● | ● | ● |
| Geospatial | ● | ● | ● | · | ● | ● |
| Mesh Alignment | ● | ● | ● | · | · | · |
| Sparse Products | ● | ● | ● | · | · | · |
| Probability Divergences | ● | ● | ● | ● | · | ● |
| Curved Spaces | ● | ● | ● | · | · | · |
| Dots (many-to-many) | ● | ● | ● | ● | ● | ● |
| Spatials (many-to-many) | ● | ● | ● | ● | ● | ● |
| Sets (many-to-many) | ● | ● | ● | · | ● | ● |
| MaxSim Scoring | ● | ● | ● | · | ● | ● |
| Cast | ● | ● | ● | ● | · | · |
| Reduce | ● | ● | ● | · | · | · |
| Each (elementwise) | ● | ● | ● | · | · | · |
| Trigonometry | ● | ● | ● | · | · | · |

● = supported, · = not exposed in that binding
