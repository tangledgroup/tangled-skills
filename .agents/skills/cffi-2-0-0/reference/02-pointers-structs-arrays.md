# Pointers, Structs & Arrays

## Allocating Memory with ffi.new()

`ffi.new(cdecl, init=None)` allocates an instance of the specified C type and returns a pointer to it. The type must be a pointer or array:

```python
# Allocate a single struct
p = ffi.new("struct point *")
p.x = 3
p.y = 4

# Allocate with initializer
p = ffi.new("struct point *", {"x": 3, "y": 4})
# Or with positional init (order matches field declaration)
p = ffi.new("struct point *", [3, 4])

# Allocate an array of 10 ints (zero-initialized)
arr = ffi.new("int[10]")

# Allocate variable-length array
n = 100
arr = ffi.new("int[]", n)

# Allocate a byte string
s = ffi.new("char[]", b"hello world")
```

The returned `<cdata>` object owns the memory. When it goes out of scope, the memory is freed. Keep the cdata alive as long as the pointed-to data is needed.

### Ownership Rules

After `p = ffi.new("struct-or-union *", ...)`, either `p` or `p[0]` keeps the memory alive. For other types, only the returned object itself keeps memory alive:

```python
# WRONG — allocated object goes out of scope immediately
x = ffi.cast("void *", ffi.new("char[]", b"data"))

# CORRECT — keep the original alive
buf = ffi.new("char[]", b"data")
x = ffi.cast("void *", buf)
```

## Working with Pointers

Pointers support indexing, arithmetic, and comparison:

```python
arr = ffi.new("int[10]")
arr[0] = 42
ptr = arr + 3       # pointer to arr[3]
print(ptr[0])        # same as arr[3]
diff = ptr - arr     # pointer arithmetic, returns 3

# NULL comparison
if ptr == ffi.NULL:
    print("null")
```

### Pointer Casting

`ffi.cast("C type", value)` casts between compatible types:

```python
p = ffi.new("int *")
vp = ffi.cast("void *", p)
ip = ffi.cast("int *", vp)
```

In function arguments, `item *` and `item[]` are treated identically (as per C standard). You can pass a Python byte string to a `char *` argument, or a list to an `int *` argument:

```python
lib.some_func(b"hello")        # passes as char *
lib.sum_array([1, 2, 3, 4])   # passes as int *
```

## Working with Structs

Access struct fields directly through pointer cdata:

```python
ffi.cdef("""
    struct point { int x; int y; };
""")

p = ffi.new("struct point *", {"x": 10, "y": 20})
print(p.x)   # 10
p.y = 30

# Access through dereference
print(p[0].x)  # also works for struct/union pointers
```

### Nested Structs and Unions

```python
ffi.cdef("""
    struct inner { int a; int b; };
    struct outer {
        int id;
        struct inner data;
    };
""")

o = ffi.new("struct outer *", {"id": 1, "data": {"a": 100, "b": 200}})
print(o.data.a)  # 100
```

Anonymous structs and unions are supported. Initialize with nested dicts or lists matching the declaration order.

### Variable-Length Structs

Structs with `field[]` as the last field have variable-length arrays:

```python
ffi.cdef("""
    struct header {
        int length;
        char data[];
    };
""")

h = ffi.new("struct header *", {"length": 5, "data": b"hello"})
print(ffi.sizeof(h))  # includes the array portion
```

### Sizeof and Alignment

```python
ffi.sizeof("int")           # size of type
ffi.sizeof("struct point")  # size of struct
ffi.sizeof(p)               # size of what p points to
ffi.alignof("double")       # alignment requirement
ffi.offsetof("struct point", "y")  # offset of field
```

## Working with Arrays

Arrays support indexing, iteration, length, and slicing:

```python
arr = ffi.new("int[5]", [10, 20, 30, 40, 50])
print(len(arr))    # 5
print(arr[2])      # 30

# Iterate
for val in arr:
    print(val)

# Slice (both start and stop required, no step)
slice = arr[1:4]   # view of items 1, 2, 3

# Slice assignment
arr[1:3] = [99, 88]
```

Negative indices work like in C (not Python — they are truly negative offsets).

### Char Arrays and Strings

For `char[]`, `unsigned char[]`, and `_Bool[]`, you can initialize with byte strings:

```python
arr = ffi.new("char[5]", b"hello")
arr = ffi.new("char[]", b"dynamic length string")
```

For `wchar_t[]`, `char16_t[]`, `char32_t[]`, initialize with unicode strings.

## Converting C Data to Python

### Strings from C

`ffi.string(cdata, maxlen=None)` converts C character data to Python bytes/str:

```python
# From a char * returned by a C function
name = lib.get_name()  # returns <cdata 'char *'>
py_str = ffi.string(name)  # b'username'

# With length limit
py_str = ffi.string(name, 64)

# From wchar_t * (returns unicode)
wide = lib.get_wide_name()
py_unicode = ffi.string(wide)
```

### Unpacking Arrays

`ffi.unpack(cdata, length)` unpacks an array without stopping at null:

```python
buf = ffi.new("char[100]")
# ... fill buf with data including embedded nulls ...
data = ffi.unpack(buf, 100)  # bytes of exact length
ints = ffi.unpack(int_ptr, 50)  # list of 50 integers
```

## Buffer Access

`ffi.buffer(cdata, size=None)` returns a buffer object for zero-copy memory access:

```python
arr = ffi.new("int[1000]")
buf = ffi.buffer(arr)
print(len(buf))       # 4000 bytes (1000 * sizeof(int))
print(buf[:8])        # first 8 bytes as bytes
buf[0:4] = b'\x00\x10\x00\x00'  # write raw bytes
```

`ffi.from_buffer(python_buffer, cdecl="char[]")` creates a cdata pointing to Python buffer data without copying:

```python
ba = bytearray(1024)
p = ffi.from_buffer(ba)  # <cdata 'char[]'>
# or with typed array
p = ffi.from_buffer("uint32_t[]", ba)  # array of uint32_t

# Use directly as function argument
lib.process_data(ffi.from_buffer(large_bytearray))
```

## FILE* Support

CFFI provides best-effort support for passing Python file objects to `FILE *` arguments:

```python
ffi.cdef("int fprintf(FILE *stream, const char *format, ...);")
lib = ffi.dlopen(None)

with open("output.txt", "w") as f:
    lib.fprintf(f, b"Hello %d\n", 42)
```

For finer control over buffering and closing, use `fdopen()` explicitly:

```python
ffi.cdef("""
    FILE *fdopen(int fd, const char *mode);
    int fclose(FILE *fp);
""")

myfile.flush()
newfd = os.dup(myfile.fileno())
fp = lib.fdopen(newfd, "w")
lib.write_stuff(fp)
lib.fclose(fp)
```

## Memory Management

### Custom Allocators

`ffi.new_allocator(alloc=None, free=None, should_clear_after_alloc=True)` creates a custom allocator:

```python
# Use C malloc/free for explicit control
ffi.cdef("""
    void *malloc(size_t size);
    void free(void *ptr);
""")

my_new = ffi.new_allocator(lib.malloc, lib.free)

with my_new("int[]", 1000) as arr:
    # use arr...
    pass  # freed at end of with block
```

### Releasing Memory Early

`ffi.release(cdata)` forces immediate resource release (available since v1.12):

```python
arr = ffi.new("char[]", 10_000_000)
# ... use arr ...
ffi.release(arr)  # free immediately, don't wait for GC
```

On PyPy this is particularly important to avoid excessive GC pressure from large allocations.

### Garbage Collection with ffi.gc()

`ffi.gc(cdata, destructor)` attaches a custom destructor to a cdata:

```python
# C library allocates memory
ptr = lib.my_alloc(1024)
# Wrap with automatic cleanup
ptr = ffi.gc(ptr, lib.my_free)
# When ptr goes out of Python scope, lib.my_free(ptr) is called
```
