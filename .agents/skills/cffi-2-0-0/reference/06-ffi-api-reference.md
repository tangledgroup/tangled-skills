# FFI API Reference

## Core Constants and Exceptions

- **`ffi.NULL`**: A constant NULL of type `<cdata 'void *'>`.
- **`ffi.error`**: The Python exception raised in various error cases (don't confuse with `ffi.errno`).

## Memory Allocation

### ffi.new(cdecl, init=None)

Allocates an instance of the specified C type and returns a pointer. The type must be a pointer or array.

```python
p = ffi.new("int *")            # single int, zero-initialized
p = ffi.new("int *", 42)        # single int, initialized to 42
arr = ffi.new("int[10]")        # array of 10 ints
arr = ffi.new("int[]", n)       # variable-length array
s = ffi.new("char[]", b"hello") # byte string
```

Memory is freed when the returned `<cdata>` goes out of scope. The cdata owns the pointed-to memory.

### ffi.new_allocator(alloc=None, free=None, should_clear_after_alloc=True)

Returns a callable that allocates like `ffi.new()` but with custom alloc/free functions:

```python
my_new = ffi.new_allocator(lib.malloc, lib.free)
arr = my_new("int[]", 1000)

# Use as context manager (v1.12+)
with my_new("int[]", 1000) as arr:
    # use arr
    pass  # freed at block exit
```

Set `should_clear_after_alloc=False` for performance when initial content doesn't matter.

### ffi.release(cdata)

Releases resources held by a cdata from `ffi.new()`, `ffi.gc()`, `ffi.from_buffer()`, or custom allocator. The cdata must not be used afterward. (v1.12+)

```python
arr = ffi.new("char[]", 10_000_000)
# ... use arr ...
ffi.release(arr)  # free immediately

# Or as context manager
with ffi.from_buffer(buf) as p:
    do_something(p)
```

## Type Operations

### ffi.cast("C type", value)

Returns an instance of the named C type initialized with the given value. Casts between integers or pointers.

```python
p = ffi.new("int *")
vp = ffi.cast("void *", p)
i = ffi.cast("int", ptr_to_int)
```

### ffi.typeof(cdata_or_type)

Returns the ctype object for the given cdata or type string:

```python
ct = ffi.typeof(p)
ct = ffi.typeof("int *")
```

### ffi.sizeof(cdata_or_type)

Returns the size in bytes:

```python
ffi.sizeof("int")          # 4
ffi.sizeof("struct point") # struct size
ffi.sizeof(p)              # what p points to
```

### ffi.alignof(type)

Returns the alignment requirement of a type.

### ffi.offsetof(type, field)

Returns the byte offset of a field within a struct.

### ffi.getctype(cdata_or_type, extra="")

Returns the string representation of a C type. The `extra` parameter can add a variable name or modifier:

```python
ffi.getctype("char[80]", "a")  # "char a[80]"
ffi.getctype(ffi.typeof(x), "*")  # pointer to same type as x
```

### ffi.list_types()

Returns `(typedef_names, struct_names, union_names)` — all user type names known to this FFI instance. (v1.6+)

## String and Buffer Operations

### ffi.string(cdata, maxlen=None)

Converts C character data to Python bytes/str:

```python
# From char *
s = ffi.string(char_ptr)           # bytes until null
s = ffi.string(char_ptr, 64)       # bytes, max 64 chars

# From wchar_t *
u = ffi.string(wchar_ptr)          # unicode string

# From single char
b = ffi.string(single_char_cdata)  # bytes of length 1
```

### ffi.unpack(cdata, length)

Unpacks an array of C data into a Python value without stopping at null:

```python
data = ffi.unpack(char_ptr, 100)   # bytes of exact length
ints = ffi.unpack(int_ptr, 50)     # list of 50 ints
wide = ffi.unpack(wchar_ptr, 30)   # unicode string
```

### ffi.buffer(cdata, size=None)

Returns a buffer object referencing raw C data (zero-copy):

```python
buf = ffi.buffer(arr)       # entire array
buf = ffi.buffer(ptr, 64)   # first 64 bytes

# Read
data = buf[:]               # bytes
part = buf[0:10]            # slice as bytes

# Write
buf[0:4] = b'\x00\x01\x02\x03'
```

### ffi.from_buffer(cdecl, python_buffer, require_writable=False)

Creates a cdata pointing to Python buffer data without copying:

```python
ba = bytearray(1024)
p = ffi.from_buffer(ba)                  # <cdata 'char[]'>
p = ffi.from_buffer("int[]", ba)         # <cdata 'int[]'>
p = ffi.from_buffer("MyStruct *", buf)   # pointer to struct (v1.13+)

# Direct function argument
lib.process(ffi.from_buffer(large_bytearray))
```

## Garbage Collection

### ffi.gc(cdata, destructor, size=None)

Attaches a destructor to a cdata, called when the cdata is garbage collected:

```python
ptr = lib.my_alloc(1024)
ptr = ffi.gc(ptr, lib.my_free)
# When ptr is GC'd, lib.my_free(ptr) is called

# Remove destructor
ptr = ffi.gc(ptr, None)

# With size hint (for PyPy GC tuning)
ptr = ffi.gc(ptr, lib.my_free, 1024)
```

## Address and Error Operations

### ffi.addressof(container, field_or_index)

Gets a pointer to a struct field or array element:

```python
p = ffi.new("struct point *")
xp = ffi.addressof(p, "x")   # <cdata 'int *'> pointing to p.x

# For global variables
addr = ffi.addressof(lib, "my_global_var")
```

### ffi.errno

Thread-local read/write property for the C `errno` value from the most recent call.

### ffi.getwinerror(code=-1)

On Windows, returns `(code, message)` tuple from `GetLastError()`. Pass a specific code to format it into a message.

## Memory Operations

### ffi.memmove(dest, src, count)

Like C `memmove()` — copies `count` bytes from `src` to `dest`, handling overlapping regions safely. (v1.3+)

### ffi.memset(dest, c, count)

Like C `memset()` — sets `count` bytes of `dest` to value `c`.

## Handle Operations

### ffi.new_handle(obj)

Creates a `void *` handle that wraps a Python object:

```python
handle = ffi.new_handle(my_object)
# Pass handle to C code as void *
# Keep the handle alive!
```

### ffi.from_handle(handle)

Recovers the Python object from a handle:

```python
obj = ffi.from_handle(void_ptr_from_c)
```

## Initialization

### ffi.init_once(function, tag)

Runs `function()` exactly once, identified by `tag`. Thread-safe — parallel calls block until completion. Returns the cached result:

```python
def initlib():
    lib.initialize_my_library()

def make_foo():
    ffi.init_once(initlib, "init")
    return lib.make_foo()

# With return value
def get_max():
    return lib.get_maximum()

def process(i):
    if i > ffi.init_once(get_max, "max"):
        raise IndexError("too large")
```

## Type Conversions

### Writing Into C (Python → C)

- **integers/enums**: Python int (must be in range)
- **char**: single-character string or `<cdata char>`
- **wchar_t/char16_t/char32_t**: single unicode character
- **float/double**: Python float
- **long double**: another `<cdata>` with long double, or anything on which `float()` works
- **pointers**: compatible `<cdata>` (same type, `void*`, or array)
- **arrays**: list/tuple of items; for `char[]` also a byte string
- **struct**: list/tuple/dict of field values, or same-type `<cdata>`
- **union**: same as struct but at most one field

### Reading From C (C → Python)

- **integers/enums**: Python int (or bool for `_Bool`/`bool`)
- **char**: single-character string
- **wchar_t/charN_t**: unicode character
- **float/double**: Python float
- **long double**: `<cdata>` (to avoid precision loss; call `float()` to convert)
- **pointers/arrays/structs/unions**: `<cdata>`
- **function pointers**: callable `<cdata>`

### In Function Arguments

`item *` and `item[]` are identical in function declarations. You can pass:
- A Python byte string to a `char *` argument
- A list of integers to an `int *` argument
- `[[x, y]]` or `[{'x': 5, 'y': 10}]` to a `struct point_s *` argument

The temporary C data is created just before the call and freed afterward.

## Thread Safety

CFFI releases the GIL before calling into C libraries. This means:

- Multithreaded speedups are possible on both free-threaded and GIL-enabled Python
- The GIL does **not** protect shared C data structures
- If the wrapped C library is not thread-safe, you must add locking:

```python
import threading

lock = threading.Lock()

def thread_safe_call():
    with lock:
        return lib.unsafe_function()
```

- If the C library is thread-safe, no additional locking is needed for CFFI itself
- For per-object safety (re-entrant but not thread-safe libraries), use a non-blocking lock check:

```python
if not obj._lock.acquire(blocking=False):
    raise RuntimeError("Multithreaded use not supported")
try:
    lib.use_object(obj._handle)
finally:
    obj._lock.release()
```

Validate thread safety with ThreadSanitizer (`-fsanitize=thread`).

## CData Operations

On `<cdata>` objects:

- **integers/floats**: `int()`, `bool()`, comparison operators
- **pointers**: `[]` indexing, `+`, `-`, `bool()` (NULL check)
- **arrays**: `len()`, `iter()`, `[]`, `+`, `-`, slicing (`x[start:stop]`)
- **structs/unions**: read/write fields, `p[0].field` for pointer dereference
- **function pointers**: `bool()`, call

Boolean on primitives (v1.7+): returns `False` if zero, `True` otherwise.

Primitive cdata comparison (v1.10+): `<cdata 'int' 42>` compares equal to Python `42`.
