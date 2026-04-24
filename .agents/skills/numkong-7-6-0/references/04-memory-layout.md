# Memory Layout and Parallelism

> **Source:** NumKong README, include/README.md, python/README.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## No Hidden Threads

NumKong does not manage its own thread pool. This avoids thread oversubscription when combined with external parallelism (joblib, std::thread, Tokio, GCD, OpenMP). The library exposes row-range parameters that let the caller partition work across any threading model.

Modern hardware makes "spawn N threads and split evenly" increasingly untenable:

- **Server CPUs** have hundreds of cores across sockets, chiplets, and tiles with dozens of NUMA domains
- **Consumer CPUs** pack heterogeneous core types (Intel P-cores/E-cores) at different frequencies
- **Real-time systems** cannot afford to yield the main thread to a BLAS-managed pool

## No Hidden Allocations

NumKong never allocates memory. Following Intel MKL's packed GEMM API pattern (`cblas_sgemm_pack_get_size` → `cblas_sgemm_pack` → `cblas_sgemm_compute`), NumKong exposes typed three-phase interfaces where the caller owns the buffer:

```
nk_dots_packed_size_* → nk_dots_pack_* → nk_dots_packed_*
```

This avoids problems seen in traditional BLAS: lock/unlock pairs throttling scaling, thread-unsafe allocation producing incorrect results, deadlocks after fork() due to mutex state.

## Parallelism Patterns

### GEMM-Like Packed Work (Python)

Partition left operand rows against one shared packed right-hand side:

```python
import concurrent.futures
import numpy as np
import numkong as nk

left = np.random.randn(4096, 768).astype(np.float32)
right = np.random.randn(8192, 768).astype(np.float32)
packed = nk.dots_pack(right, dtype="float32")
out = nk.zeros((4096, 8192), dtype="float64")

def packed_chunk(start, end):
    nk.dots_packed(left, packed, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for start in range(0, 4096, 1024):
        pool.submit(packed_chunk, start, min(start + 1024, 4096))
```

### SYRK-Like Symmetric Work (Python)

Partition by output row windows of one square matrix:

```python
vectors = np.random.randn(4096, 768).astype(np.float32)
out = nk.zeros((4096, 4096), dtype="float64")

def symmetric_chunk(start, end):
    nk.dots_symmetric(vectors, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for start in range(0, 4096, 1024):
        pool.submit(symmetric_chunk, start, min(start + 1024, 4096))
```

### C++ Parallel with ForkUnion

```cpp
fork_union.parallel_for(0, worker_count, [&](std::size_t t) {
    auto start = t * rows_per_worker;
    auto stop = std::min(start + rows_per_worker, total_rows);
    auto a_slice = a[range(start, stop), all, slice].as_matrix_view();
    auto c_slice = c[range(start, stop), all, slice].as_matrix_span();
    nk::dots_packed<value_type_>(a_slice, packed, c_slice);
});
```

The `parallel` Cargo feature in Rust provides the same ForkUnion-based orchestration. C++26 Executors TS (`std::execution`) is a natural fit — NumKong kernels take explicit row-range parameters and compose directly with `std::execution::bulk`.

## Memory Layout Rules

### Python Tensor Requirements

| API Family | Input Requirement | Output Requirement |
|------------|-------------------|-------------------|
| Dense distances (`dot`, `euclidean`, etc.) | Rows must be contiguous. Strided rows rejected. | `out=` can have any stride along dim 0, inner dim must be contiguous |
| `cdist` | Same as dense distances | `out=` rank-2 with shape `(a.count, b.count)` |
| Elementwise (`scale`, `blend`, `fma`) | Arbitrary strides supported | `out=` must match input shape; strides preserved |
| Packed matrix (`dots_packed`) | Left operand: rank-2, contiguous rows, no negative strides | Output: C-contiguous with expected dtype |
| Symmetric (`dots_symmetric`) | Contiguous rows | `out=`: C-contiguous square matrix |
| Tensor reductions | Arbitrary strides supported | N/A (returns scalar or reduced tensor) |

### C++ Containers

- `vector<T, A>` — owns storage, defaults to `aligned_allocator<T, 64>`
- `vector_view<T>` — const strided non-owning view
- `vector_span<T>` — mutable strided non-owning view
- `tensor<T, A, R>` — owns rank-R storage, aligned allocation
- `tensor_view<T>`, `tensor_span<T>` — view forms
- `matrix`, `matrix_view`, `matrix_span` — rank-2 aliases

Signed strides are supported by view types. Reversed and sliced views are valid for elementwise and reduction kernels. Matrix-style kernels care about row contiguity, not just total tensor contiguity. Negative strides are conceptually valid but matrix packing and packed matmul workflows are not written around them.

### C ABI

Every kernel takes plain `const` pointers for input and caller-provided pointers for output, returning `void`. No exceptions, no errno, no setjmp/longjmp. Pointers eliminate implicit casts for types with platform-dependent storage — `nk_f16_t` and `nk_bf16_t` resolve to native `__fp16`/`__bf16` when available but fall back to `unsigned short` otherwise.

```c
void nk_dot_f32(nk_f32_t const *a, nk_f32_t const *b, nk_size_t n, nk_f64_t *result);
void nk_dot_bf16(nk_bf16_t const *a, nk_bf16_t const *b, nk_size_t n, nk_f32_t *result);
```

## External Memory Addressing

Every kernel accepts any CPU-accessible memory: mmap, pinned buffers, CUDA unified memory, custom arenas.

```python
import ctypes, mmap

# CUDA unified memory
cudart = ctypes.CDLL("libcudart.so")
unified_ptr = ctypes.c_void_p()
cudart.cudaMallocManaged(ctypes.byref(unified_ptr), 4096, 1)
cudart.cudaDeviceSynchronize()
unified = nk.from_pointer(unified_ptr.value, (1024,), 'float32')

# Memory-mapped file
with open("data.bin", "r+b") as f:
    mapping = mmap.mmap(f.fileno(), 0)
    mapped = nk.from_pointer(
        ctypes.addressof(ctypes.c_char.from_buffer(mapping)),
        (1024,), 'float32', owner=mapping)
```

C++ custom allocator example:

```cpp
template <typename T>
struct cuda_allocator {
    using value_type = T;
    T *allocate(std::size_t n) { T *p;
        cudaMallocManaged(&p, n * sizeof(T), cudaMemAttachGlobal);
        return p; }
    void deallocate(T *p, std::size_t) noexcept { cudaFree(p); }
};

auto v = nk::vector<float, cuda_allocator<float>>::try_zeros(1024);
```

## GIL Behavior (Python)

The GIL is released around dense metric calls and around packed and symmetric matrix kernels. This makes NumKong compatible with `concurrent.futures`, `multiprocessing`, or any other parallelism model.
