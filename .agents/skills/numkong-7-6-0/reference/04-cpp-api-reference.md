# C/C++ API Reference

## The C ABI

The C ABI keeps operation family, input dtype, and output policy visible in the symbol name. Every function takes inputs as `const` pointers, writes outputs through caller-provided pointers, and returns `void`. No exceptions, no errno, no setjmp/longjmp.

```c
#include <numkong/numkong.h>

nk_f32_t a[] = {1, 2, 3};
nk_f32_t b[] = {4, 5, 6};
nk_f64_t dot = 0;
nk_configure_thread(nk_capabilities());
nk_dot_f32(a, b, 3, &dot); // widened f32 → f64 output
```

For runtime-selected kernels without naming a specific ISA:

```c
nk_metric_dense_punned_t angular = 0;
nk_capability_t used = nk_cap_serial_k;
nk_find_kernel_punned(
    nk_kernel_angular_k, nk_f32_k,
    nk_capabilities(),
    (nk_kernel_punned_t *)&angular, &used);

angular(a, b, 768, &result);
```

## The C++ Layer

C++ wrappers add three things: type-level result promotion, explicit owning/non-owning containers, and allocator-aware packed objects.

```cpp
#include <numkong/numkong.hpp>
namespace nk = ashvardanian::numkong;

int main() {
    nk::f32_t a[3] = {1, 2, 3}, b[3] = {4, 5, 6};
    nk::f64_t dot {};
    nk::dot(a, b, 3, &dot);
    // Default result type is nk::f32_t::dot_result_t == nk::f64_t
}
```

The API is intentionally not STL-shaped. `vector_view`, `tensor_view`, and `matrix_view` prioritize signed strides, sub-byte storage, and kernel compatibility over resizable-container ergonomics.

## Containers

- `vector<T, A>` — owns storage, defaults to `aligned_allocator<T, 64>`
- `vector_view<T>` — const strided non-owning view
- `vector_span<T>` — mutable strided non-owning view
- `tensor<T, A, R>` — owns rank-R storage, aligned allocation
- `tensor_view<T>` / `tensor_span<T>` — view forms
- `matrix`, `matrix_view`, `matrix_span` — rank-2 aliases

```cpp
auto t = tensor<f32_t>::try_from({{1,2,3},{4,5,6},{7,8,9}});

f32_t val = t[1, -1];                        // 2D coordinate access
f32_t val2 = t[4];                           // global offset
tensor_view<f32_t> row = t[1, slice];        // second row
tensor_view<f32_t> col = t[all, 1, slice];   // second column
```

Memory ownership is explicit: `vector` and `tensor` deallocate through their allocator. Views and spans never own memory.

## Iterators

- `dim_iterator` — random-access over elements (vector), supports `index()`
- `axis_iterator` — random-access over sub-views/rows (tensor), supports `index()`
- `enumerate()` — free function returning `{index, value}` pairs

```cpp
nk::vector<nk::f16_t> v(128);
for (auto [i, val] : nk::enumerate(v))
    std::printf("[%zu] = %f\n", i, val.to_f32());

// Range-for over tensor elements
for (auto [pos, val] : matrix) { /* pos is std::array<size_t, R> */ }
for (auto [pos, ref] : matrix.span()) { ref = nk::f32_t{1}; }
```

## Scalar Types and C++23 Formatting

When `__cpp_lib_format >= 202110L`, all NumKong scalar types provide `std::formatter` specializations:

- `{}` — clean float value (`3.140625`)
- `{:#}` — annotated with hex bits (`3.140625 [0x4248]`)
- `{:.2f}` — precision forwarded (`3.14`)
- `{:x}` / `{:X}` — raw hex bits
- `{:b}` — binary bits

## Packed Matrix in C++

```cpp
auto a = nk::tensor<nk::f32_t>::try_full({2, 4}, nk::f32_t{1});
auto b = nk::tensor<nk::f32_t>::try_full({3, 4}, nk::f32_t{2});
auto packed = nk::packed_matrix<nk::f32_t>::try_pack(b.as_matrix_view());

auto dots = nk::try_dots_packed(a.as_matrix_view(), packed);
auto angulars = nk::try_angulars_packed(a.as_matrix_view(), packed);
auto euclideans = nk::try_euclideans_packed(a.as_matrix_view(), packed);
```

## Symmetric Kernels in C++

```cpp
auto vectors = nk::tensor<nk::f32_t>::try_full({100, 768}, nk::f32_t{1});
auto gram = nk::try_dots_symmetric(vectors.as_matrix_view());
auto angular_dists = nk::try_angulars_symmetric(vectors.as_matrix_view());
auto euclidean_dists = nk::try_euclideans_symmetric(vectors.as_matrix_view());
```

## Parallelism with ForkUnion

```cpp
using nk::range, nk::all, nk::slice;
fork_union.parallel_for(0, worker_count, [&](std::size_t t) {
    auto start = t * rows_per_worker;
    auto stop = std::min(start + rows_per_worker, total_rows);
    auto a_slice = a[range(start, stop), all, slice].as_matrix_view();
    auto c_slice = c[range(start, stop), all, slice].as_matrix_span();
    nk::dots_packed<value_type_>(a_slice, packed, c_slice);
});
```

## External Memory

Every kernel takes plain pointers — any CPU-accessible memory works: mmap, pinned buffers, CUDA unified memory, custom arenas.

```cpp
// Custom allocator for CUDA managed memory
template <typename T>
struct cuda_allocator {
    using value_type = T;
    T *allocate(std::size_t n) { T *p;
        cudaMallocManaged(&p, n * sizeof(T), cudaMemAttachGlobal);
        return p; }
    void deallocate(T *p, std::size_t) noexcept { cudaFree(p); }
};

nk_dot_f32(cuda_managed_ptr, cuda_managed_ptr, 1024, &dot);
auto view = nk::tensor_view<nk::f32_t>(mmap_ptr, rows, cols);
auto v = nk::vector<float, cuda_allocator<float>>::try_zeros(1024);
```

## Runtime Dispatch

`nk_configure_thread(caps)` enables CPU-specific acceleration features (e.g., Intel AMX). Must be called once per thread before using AMX operations.

```c
nk_capability_t caps = nk_capabilities();
nk_configure_thread(caps);
if (caps & nk_cap_sapphireamx_k) { /* AMX available */ }
```

## CMake Configuration

- `NK_BUILD_SHARED` — shared library, ON by default for standalone builds
- `NK_DYNAMIC_DISPATCH=1` — compile all backends, select at runtime
- `NK_COMPARE_TO_BLAS` / `NK_COMPARE_TO_MKL` — link benchmarks against system BLAS or Intel MKL
- C99 enforced for C layer, C++23 for C++ layer

## Cross-Compilation

Toolchain files in `cmake/`:

- `toolchain-aarch64-gnu.cmake` — ARM64 Linux
- `toolchain-riscv64-gnu.cmake` — RISC-V 64 Linux
- `toolchain-android-arm64.cmake` — Android ARM64 via NDK
- `toolchain-wasm.cmake` / `toolchain-wasm64.cmake` / `toolchain-wasi.cmake` — WebAssembly
