# Python SDK Deep Dive

## Tensor Objects

`Tensor` is a memoryview-backed object with NumPy-like metadata. It is the central container for strided views, transpose, reshape, flatten, and axis reductions.

```python
import numpy as np
import numkong as nk

t = nk.Tensor(np.arange(12, dtype=np.float32).reshape(3, 4))

print(t.shape, t.dtype, t.ndim, t.strides, t.itemsize, t.nbytes)
print(np.asarray(t))       # zero-copy array view when layout allows it
print(t.T.shape)           # transposed Tensor view
print(t.reshape(2, 6).shape)
print(t.flatten().shape)

# Slicing — row, column, and scalar access
row0 = t[0, :]             # first row, shape (4,)
col2 = t[:, 2]             # third column, strided view, shape (3,)
val  = t[1, 2]             # scalar element access → 6.0

# Reductions compose with sliced views
idx = col2.argmin()         # index of the minimum in the third column
mn, i0, mx, i1 = col2.minmax()
```

### Layout Rules

- `Tensor` preserves shape and byte strides
- Transpose and slicing can produce non-contiguous views
- General reductions accept those views
- Matrix-style packed kernels require row-contiguous left operands
- Packed and symmetric outputs require C-contiguous `out` buffers

## Buffer Protocol and Zero-Copy Interop

NumKong implements the Python buffer protocol for zero-copy interop with NumPy, PyTorch, and other buffer-aware libraries.

### NumPy Interop

```python
embeddings = np.random.randn(1024).astype(np.float32)
nk.dot(embeddings, embeddings)  # zero-copy via buffer protocol
```

### PyTorch Interop

PyTorch tensors already implement the buffer protocol:

```python
import torch

query = torch.randn(512)
nk.dot(query, query)  # buffer protocol, zero copy

# NumKong → PyTorch: 1D via buffer protocol, N-D via numpy bridge
flat = torch.frombuffer(memoryview(nk_tensor), dtype=torch.float32)
shaped = torch.as_tensor(np.asarray(nk_tensor))
```

## Pointer-Level Control

Two additional primitives cover pointer-level workflows: `data_ptr` reads the integer address out of any `Tensor`, and `from_pointer()` wraps any integer address back into one.

```python
matrix = nk.zeros((3, 4), dtype='float32')
address = matrix.data_ptr
matrix_view = nk.from_pointer(address, (3, 4), 'float32', owner=matrix)

# Wrap a NumPy array with zero copies
embeddings = np.random.randn(1024).astype(np.float32)
embeddings_view = nk.from_pointer(embeddings.ctypes.data, (1024,), 'float32', owner=embeddings)
nk.dot(embeddings, embeddings_view)  # same underlying data

# Explicit PyTorch pointer wrap
query = torch.randn(512)
query_view = nk.from_pointer(query.data_ptr(), tuple(query.shape), 'float32', owner=query)
```

The optional `owner` keeps the source object alive for the lifetime of the view.

### CUDA Unified Memory and Mapped Files

Any CPU-accessible pointer is valid:

```python
import ctypes, mmap

# CUDA unified memory (ensure CPU accessibility first)
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

## Dtype Specification

For custom float types, type objects are preferred over strings — they are faster to dispatch and provide IDE autocomplete:

```python
nk.dot(a, b, dtype=nk.bfloat16)  # works faster
nk.dot(a, b, dtype="bfloat16")   # works a bit slower
```

## Capabilities Detection

Capability detection is explicit:

```python
import numkong as nk

caps = nk.get_capabilities()
print({k: v for k, v in caps.items() if v})
```

## GIL Behavior and Parallel Partitioning

The current implementation releases the GIL around native dense metric calls and around packed and symmetric matrix kernels. This enables Python-side parallelism with `concurrent.futures`:

```python
import concurrent.futures
import numpy as np
import numkong as nk

left   = np.random.randn(4096, 768).astype(np.float32)
right  = np.random.randn(8192, 768).astype(np.float32)
packed = nk.dots_pack(right, dtype="float32")
out    = nk.zeros((4096, 8192), dtype="float64")

def packed_chunk(start, end):
    nk.dots_packed(left, packed, out=out, start_row=start, end_row=end)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for start in range(0, 4096, 1024):
        pool.submit(packed_chunk, start, min(start + 1024, 4096))
```

The intended user-facing story is external partitioning around the GIL-free kernels — not a hidden `threads=` argument.

## Memory Layout Requirements by API Family

- **Dense distances** (`dot`, `euclidean`, etc.): Rows must be contiguous (`strides[last] <= itemsize`). Strided rows (sliced columns) are rejected. `out=` can have any stride along dim 0, but inner dim must be contiguous.

- **`cdist`**: Same as dense distances. `out=` must be rank-2 with shape `(a.count, b.count)`.

- **Elementwise** (`scale`, `blend`, `fma`): Arbitrary strides (strided views are supported). `out=` must match input shape; strides are preserved.

- **Packed matrix** (`dots_packed`): Left operand: rank-2, contiguous rows, no negative strides. Output: C-contiguous with expected dtype.

- **Symmetric** (`dots_symmetric`): Contiguous rows. `out=`: C-contiguous square matrix.

- **Tensor reductions** (`sum`, `min`, `argmin`, etc.): Arbitrary strides (strided views supported). Returns scalar or reduced tensor.

## Building from Source

When building from source, the compiler requirements depend on the platform:

- macOS x86: only AVX2 available
- macOS ARM: NEON always present, SME requires Apple M4+ with Xcode 16+ (AppleClang 16+)
- RISC-V: requires Clang and LLD (GCC lacks `zvfh`, `zvfbfwma`, `zvbb` support)
- Windows: MSVC 19.44+ (Visual Studio 2022 17.14+) recommended for full AVX-512 with FP16/BF16/VNNI

Build parallelism is controlled by `NK_BUILD_PARALLEL`, which defaults to `min(cpu_count, 4)` and should be lowered in memory-constrained containers. There is no OpenMP dependency.

```bash
NK_BUILD_PARALLEL=2 pip install . --no-build-isolation
```
