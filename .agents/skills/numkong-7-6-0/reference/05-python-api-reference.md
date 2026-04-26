# Python API Reference

## Tensor Objects

`Tensor` is a memoryview-backed object with NumPy-like metadata. It is the central container for strided views, transpose, reshape, flatten, and axis reductions.

```python
import numpy as np
import numkong as nk

t = nk.Tensor(np.arange(12, dtype=np.float32).reshape(3, 4))
print(t.shape, t.dtype, t.ndim, t.strides, t.itemsize, t.nbytes)
print(np.asarray(t))      # zero-copy array view when layout allows
print(t.T.shape)          # transposed Tensor view
print(t.reshape(2, 6).shape)
print(t.flatten().shape)

row0 = t[0, :]            # first row, shape (4,)
col2 = t[:, 2]            # third column, strided view, shape (3,)
val  = t[1, 2]            # scalar element access → 6.0
```

### Memory Layout Rules

- `Tensor` preserves shape and byte strides
- Transpose and slicing can produce non-contiguous views
- General reductions accept those views
- Matrix-style packed kernels require row-contiguous left operands
- Packed and symmetric outputs require C-contiguous `out` buffers

### API Family Layout Requirements

**Dense distances** (`dot`, `euclidean`, etc.): rows must be contiguous (`strides[last] <= itemsize`). Strided rows (sliced columns) are rejected. Output `out=` can have any stride along dim 0, but inner dim must be contiguous.

**`cdist`**: same as dense distances. Output `out=` must be rank-2 with shape `(a.count, b.count)`.

**Elementwise** (`scale`, `blend`, `fma`): arbitrary strides supported. Output `out=` must match input shape; strides are preserved.

**Packed matrix** (`dots_packed`): left operand rank-2, contiguous rows, no negative strides. Output C-contiguous with expected dtype.

**Symmetric** (`dots_symmetric`): contiguous rows. Output `out=`: C-contiguous square matrix.

**Tensor reductions** (`sum`, `min`, `argmin`, etc.): arbitrary strides supported. Returns scalar or reduced tensor.

## ml_dtypes Interoperability

NumKong accepts `ml_dtypes` arrays directly — no `.view(np.uint8)` workaround needed:

```python
import ml_dtypes
a = np.random.randn(100, 768).astype(np.float32).astype(ml_dtypes.bfloat16)
b = np.random.randn(100, 768).astype(np.float32).astype(ml_dtypes.bfloat16)
result = nk.cdist(a, b, "dot")  # just works
```

NumKong scalars work as NumPy dtype specifiers:

```python
arr = np.array([1.0, 2.0, 3.0], dtype=nk.bfloat16)
float(arr[0])  # → 1.0
```

### Type Name Mapping

- `ml_dtypes.bfloat16` → `nk.bfloat16` / `"bfloat16"` (identical format)
- `ml_dtypes.float8_e4m3` / `float8_e4m3fn` → `nk.float8_e4m3` / `"e4m3"` (identical)
- `ml_dtypes.float8_e5m2` → `nk.float8_e5m2` / `"e5m2"` (identical)
- `ml_dtypes.float6_e2m3fn` → `nk.float6_e2m3` / `"e2m3"` (identical)
- `ml_dtypes.float6_e3m2fn` → `nk.float6_e3m2` / `"e3m2"` (identical)
- `ml_dtypes.int4` → `"int4"` (compatible via buffer protocol)
- `ml_dtypes.uint4` → `"uint4"` (compatible via buffer protocol)

Not supported: `float8_e4m3fnuz`, `float8_e5m2fnuz`, `float8_e4m3b11fnuz`, `float8_e8m0fnu`, `float8_e3m4`, `float4_e2m1fn`, `int2`, `uint2`.

## Output Control

Most distance and dot-product entrypoints accept `out=`, `dtype=`, and `out_dtype=` keyword arguments.

```python
# Pre-allocated output with out=
out = nk.zeros((100,), dtype="float32")
nk.sqeuclidean(queries, database[:100], out=out)  # writes in-place, returns None

# Explicit input dtype for raw byte buffers
raw = np.frombuffer(some_bytes, dtype=np.uint16)
nk.dot(raw, raw, dtype=nk.bfloat16)  # reinterpret uint16 as bf16

# Output dtype override
nk.euclidean(queries[0], database[0], out_dtype="float32")  # accumulate in f64, downcast result
```

Type objects are preferred over strings — faster dispatch and IDE autocomplete: `dtype=nk.bfloat16` (fast) vs `dtype="bfloat16"` (slower).

## Scalar Types

Six scalar types with stable payload sizes:

- `nk.float16` — 1+5+10 bits, 2 bytes, range ±65504, inf/NaN
- `nk.bfloat16` — 1+8+7 bits, 2 bytes, range ±3.4×10³⁸, inf/NaN
- `nk.float8_e4m3` — 1+4+3 bits, 1 byte, range ±448, no inf, NaN
- `nk.float8_e5m2` — 1+5+2 bits, 1 byte, range ±57344, inf/NaN
- `nk.float6_e2m3` — 1+2+3 bits, 1 byte, range ±7.5, no inf/NaN
- `nk.float6_e3m2` — 1+3+2 bits, 1 byte, range ±28, no inf/NaN

## Addressing External Memory

NumKong implements the Python buffer protocol for zero-copy interop with NumPy, PyTorch, and other buffer-aware libraries.

```python
# Round-trip through integer address
matrix = nk.zeros((3, 4), dtype='float32')
address = matrix.data_ptr
matrix_view = nk.from_pointer(address, (3, 4), 'float32', owner=matrix)

# Wrap NumPy array with zero copies
embeddings = np.random.randn(1024).astype(np.float32)
embeddings_view = nk.from_pointer(embeddings.ctypes.data, (1024,), 'float32', owner=embeddings)

# PyTorch tensors via buffer protocol
import torch
query = torch.randn(512)
nk.dot(query, query)  # buffer protocol, zero copy

# CUDA unified memory
import ctypes
cudart = ctypes.CDLL("libcudart.so")
unified_ptr = ctypes.c_void_p()
cudart.cudaMallocManaged(ctypes.byref(unified_ptr), 4096, 1)
cudart.cudaDeviceSynchronize()
unified = nk.from_pointer(unified_ptr.value, (1024,), 'float32')

# Memory-mapped file
import mmap
with open("data.bin", "r+b") as f:
    mapping = mmap.mmap(f.fileno(), 0)
    mapped = nk.from_pointer(ctypes.addressof(ctypes.c_char.from_buffer(mapping)),
                             (1024,), 'float32', owner=mapping)
```

## Capabilities and GIL Behavior

```python
caps = nk.get_capabilities()
print({k: v for k, v in caps.items() if v})
```

GIL is released around dense metric calls and packed/symmetric matrix kernels. Threading model uses external partitioning with row ranges, not a hidden `threads=` argument.

## Wheel Compatibility

Pre-built wheels available on PyPI for:
- Linux: x86_64, aarch64, riscv64, i686, ppc64le, s390x
- macOS: x86_64, arm64
- Windows: AMD64, ARM64
- Python 3.9 through 3.14, including free-threading variants (3.13t, 3.14t)

Every wheel built with `NK_DYNAMIC_DISPATCH=1` — single wheel covers all CPU generations on a given architecture.
