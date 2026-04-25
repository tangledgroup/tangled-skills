# CFFI Memory Management - Complete Guide

## Overview

CFFI provides several mechanisms for allocating and managing memory when interfacing with C code. Understanding memory management is crucial to avoid leaks, crashes, and undefined behavior.

## ffi.new() - Allocating C Objects

### Basic Usage

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    struct point {
        int x;
        int y;
    };
""")

# Allocate single struct (returns pointer)
p = ffi.new("struct point *")
p.x = 10
p.y = 20

# Allocate array
arr = ffi.new("int[10]")
for i in range(10):
    arr[i] = i * 2

# Allocate array with initial values
arr2 = ffi.new("int[5]", [1, 2, 3, 4, 5])

# Allocate and initialize array with single value
arr3 = ffi.new("char[100]", 0)  # 100 zeros
```

### String Allocation

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("void print_string(char *str);")

lib = ffi.dlopen("mylib.so")

# Create C string from Python str
msg = ffi.new("char[]", "Hello, World!".encode('utf-8'))
lib.print_string(msg)

# Or use ffi.str() for convenience
msg2 = ffi.str("Hello")
lib.print_string(msg2)

# Create null-terminated string with specific size
buffer = ffi.new("char[256]", b"Initial content")
```

### Pointer to Pointer

```python
ffi.cdef("""
    void modify_int(int *ptr);
    int **get_double_pointer(void);
""")

# Allocate pointer to pointer
int_val = ffi.new("int *", 42)        # int * pointing to 42
double_ptr = ffi.new("int **", int_val)  # int ** pointing to int *

# Access through double pointer
print(double_ptr[0][0])  # 42

# Modify through double pointer
double_ptr[0][0] = 100
print(int_val[0])  # 100
```

### Complex Structures

```python
ffi.cdef("""
    struct node {
        int value;
        struct node *next;
    };
    
    struct matrix {
        int rows;
        int cols;
        double **data;
    };
""")

# Create linked list node
node1 = ffi.new("struct node *")
node1.value = 1
node1.next = None  # NULL

node2 = ffi.new("struct node *")
node2.value = 2
node2.next = node1

# Create 2D array (array of pointers)
rows, cols = 3, 4
matrix = ffi.new("struct matrix *")
matrix.rows = rows
matrix.cols = cols

# Allocate array of row pointers
matrix.data = ffi.new("double *[]", rows)
for i in range(rows):
    matrix.data[i] = ffi.new("double[cols]", 0.0)

# Access elements
matrix.data[0][0] = 1.5
matrix.data[2][3] = 9.9
```

## ffi.alloc() - Raw Memory Allocation

### Usage and Differences from ffi.new()

```python
from cffi import FFI
ffi = FFI()

# ffi.alloc() allocates raw memory without zero-initialization
ptr = ffi.alloc("char", 1024)  # 1024 bytes of uninitialized memory

# Must cast to appropriate type before use
char_ptr = ffi.cast("char *", ptr)
int_ptr = ffi.cast("int *", ptr)

# ffi.new() zero-initializes, ffi.alloc() does not
zeroed = ffi.new("int[10]")     # All zeros
raw = ffi.alloc("int", 10)      # Garbage values
```

### When to Use ffi.alloc()

1. **Performance**: Skip zero-initialization when you'll overwrite all bytes
2. **Reusing memory**: Allocate once, reuse multiple times
3. **Binary data**: Working with raw byte buffers
4. **Custom allocation**: Implementing your own memory management

```python
# Example: Reusable buffer
buffer = ffi.alloc("char", 65536)  # 64KB buffer

def process_data(data):
    # Reuse same buffer, no reallocation
    size = len(data)
    ffi.memmove(buffer, data, size)
    return lib.process_buffer(buffer, size)
```

## ffi.buffer() - Python Buffer Protocol

### Creating Buffers from C Memory

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("char *get_data(void);")

lib = ffi.dlopen("mylib.so")

# Get pointer to C memory
data_ptr = lib.get_data()
data_size = 1024

# Create buffer object
buf = ffi.buffer(data_ptr, data_size)

# Use with Python functions expecting bytes
bytes_data = bytes(buf)  # Copy to Python bytes
```

### Creating Buffers from Python Objects

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("void process_bytes(char *data, int size);")

lib = ffi.dlopen("mylib.so")

# From bytes object
data = b"Hello, World!"
buf = ffi.buffer(data)
lib.process_bytes(buf, len(data))

# From bytearray (mutable)
mutable = bytearray(100)
buf = ffi.buffer(mutable)
lib.process_bytes(buf, 100)
# mutable is now modified by C code

# From array.array
import array
arr = array.array('i', [1, 2, 3, 4, 5])
buf = ffi.buffer(arr)
```

### In-Place Modification

```python
# Buffer allows in-place modification of underlying data
mutable = bytearray(b"Hello")
buf = ffi.buffer(mutable)

# Modify through buffer
buf[0:5] = b"World"
print(mutable)  # bytearray(b'World')

# This is efficient - no copying
```

## Memory Copying Functions

### ffi.memmove() and ffi.memcopy()

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    void *memcpy(void *dest, const void *src, size_t n);
    void *memmove(void *dest, const void *src, size_t n);
""")

lib = ffi.dlopen(None)  # C library

# Using C functions
src = ffi.new("char[100]", b"Source data")
dst = ffi.new("char[100]")
lib.memcpy(dst, src, 50)

# Or using CFFI helpers (safer)
ffi.memmove(dst, src, 50)

# memmove handles overlapping regions correctly
buffer = ffi.new("char[100]", b"AAAAAAAAAA")
ffi.memmove(buffer + 5, buffer, 5)  # Safe overlap
```

### When to Use Each

- **memcpy**: Faster, but undefined behavior with overlapping regions
- **memmove**: Slightly slower, but safe with overlapping regions
- **ffi.memmove()**: Python wrapper around memmove, type-safe

## Memory Lifecycle and Garbage Collection

### Reference Counting

CFFI-managed memory uses Python's reference counting:

```python
from cffi import FFI
ffi = FFI()

# Memory is freed when no longer referenced
def create_temporary():
    data = ffi.new("int[1000]")  # Allocated
    # ... use data ...
    return data[0]  # Return single value

result = create_temporary()
# The int[1000] array is freed here (no references)

# Multiple references keep memory alive
data = ffi.new("char[1024]")
ref1 = data
ref2 = data
# Memory kept alive until ref1 and ref2 are gone
```

### Avoiding Memory Leaks

```python
# LEAK: Storing pointers in global list without cleanup
stored_buffers = []
def process(data):
    buffer = ffi.new("char[10000]")
    stored_buffers.append(buffer)  # Never freed!

# FIX: Clear list when done or use context manager
def process_batch(data_list):
    buffers = []
    try:
        for data in data_list:
            buffer = ffi.new("char[10000]")
            buffers.append(buffer)
            lib.process(buffer)
    finally:
        del buffers  # Free all at once
```

### Explicit Memory Release

```python
from cffi import FFI
ffi = FFI()

# For large allocations, consider explicit release
def process_large_data():
    large_buffer = ffi.new("char[1024*1024]")  # 1MB
    # ... use buffer ...
    ffi.release(large_buffer)  # Mark as releasable
    
    # Buffer still usable but will be freed sooner
    lib.process(large_buffer)
    
    return "done"

# Note: ffi.release() doesn't immediately free
# It just marks the memory as available for reuse
```

## Working with C Allocated Memory

### Memory Allocated by C Functions

```python
ffi.cdef("""
    char *create_string(void);  # Caller must free
    void free_string(char *str);
    int *create_array(int size); # Caller must free
    void free_array(int *arr);
""")

lib = ffi.dlopen("mylib.so")

# C function allocates memory
str_ptr = lib.create_string()
python_str = ffi.string(str_ptr)  # Convert to Python string
lib.free_string(str_ptr)          # Free C memory

# Array example
arr = lib.create_array(100)
# Use arr...
lib.free_array(arr)
```

### Taking Ownership of C Memory

```python
from cffi import FFI
ffi = FFI()

# Tell CFFI not to free memory it doesn't own
ffi.cdef("void *external_pointer(void);")

lib = ffi.dlopen("mylib.so")
ptr = lib.external_pointer()

# Wrap in cdata without taking ownership
cdata_ptr = ffi.cast("void *", ptr)

# Or use from_handle() for specific type
int_ptr = ffi.from_handle(ptr, "int *")

# Memory must be freed by external system, not CFFI
```

### Keeping C Pointers Alive

```python
from cffi import FFI
from ctypes import POINTER, c_void_p
ffi = FFI()

# Problem: C string becomes invalid after function returns
ffi.cdef("char *get_temp_string(void);")
lib = ffi.dlopen("mylib.so")

temp = lib.get_temp_string()
# If temp points to stack memory, it's already invalid!

# Solution: Copy the string
safe_copy = ffi.string(temp)  # Creates Python bytes copy

# For long-lived pointers, keep reference to owning object
class Resource:
    def __init__(self):
        self.data = lib.create_data()  # C allocates
        self.ptr = ffi.cast("void *", self.data)
    
    def __del__(self):
        lib.free_data(self.data)  # C frees
```

## Common Memory Patterns

### String Conversion Pattern

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    char *get_username(int uid);
    void set_config(const char *key, const char *value);
""")

lib = ffi.dlopen("mylib.so")

# C string → Python str
c_str = lib.get_username(0)
if c_str != ffi.NULL:
    python_str = ffi.string(c_str).decode('utf-8')
    print(f"Username: {python_str}")

# Python str → C string
key_c = ffi.new("char[]", b"setting_name")
value_c = ffi.new("char[]", b"setting_value")
lib.set_config(key_c, value_c)

# Or with unicode
key_unicode = ffi.new("char[]", "setting_name".encode('utf-8'))
```

### Array Processing Pattern

```python
ffi.cdef("void process_floats(float *data, int count);")

# Python list → C array → Process → Back to Python
python_list = [1.0, 2.5, 3.7, 4.2]
c_array = ffi.new("float[]", python_list)
lib.process_floats(c_array, len(python_list))
result_list = list(c_array)  # Copy back to Python

# For large arrays, use numpy if available
import numpy as np
numpy_arr = np.array([1.0, 2.5, 3.7], dtype=np.float32)
c_array = ffi.cast("float *", numpy_arr.ctypes.data)
lib.process_floats(c_array, len(numpy_arr))
```

### Struct Array Pattern

```python
ffi.cdef("""
    struct record {
        int id;
        double value;
        char name[64];
    };
    
    void process_records(struct record *records, int count);
""")

# Create array of structs
records = ffi.new("struct record[10]")

# Initialize each element
for i in range(10):
    records[i].id = i
    records[i].value = i * 1.5
    records[i].name = f"Record {i}".encode('utf-8')[:63]
    records[i].name[63] = 0  # Null terminate

# Process all at once
lib.process_records(records, 10)
```

## Debugging Memory Issues

### Checking for Leaks

```python
import gc
from cffi import FFI

ffi = FFI()

def check_for_leaks():
    # Force garbage collection
    gc.collect()
    
    # Check for cdata objects still alive
    cdata_objects = [obj for obj in gc.get_objects() 
                     if type(obj).__name__ == 'cdata']
    
    print(f"Active cdata objects: {len(cdata_objects)}")
    
    # If number grows unbounded, you have a leak
```

### Using Valgrind

```bash
# Run Python under Valgrind to detect memory issues
valgrind --leak-check=full --show-leak-kernel=yes python3 script.py

# Look for:
# - Definitely lost: CFFI bug or misuse
# - Indirectly lost: Follow the chain
# - Still reachable: Normal for long-lived objects
```

### Common Memory Errors

**Use After Free:**
```python
# WRONG
data = ffi.new("int[100]")
result = process_and_return_single_value(data)
print(data[0])  # USE AFTER FREE! data may be freed

# RIGHT
data = ffi.new("int[100]")
result = process_data(data)
value = data[0]  # Use before function might free
```

**Double Free:**
```python
# WRONG - if C code also frees
ffi.cdef("""
    char *create_string(void);
    void free_string(char *str);
""")

str_ptr = lib.create_string()
ffi.release(str_ptr)  # Tell CFFI not to free
lib.free_string(str_ptr)
del str_ptr  # Might try to free again!

# RIGHT - be explicit about ownership
str_ptr = lib.create_string()
python_str = ffi.string(str_ptr)
lib.free_string(str_ptr)  # Only C frees
```

**Stack Overflow from Large Allocations:**
```python
# WRONG - huge array on stack (in C, not Python)
ffi.cdef("void large_function(void);")

# If large_function declares large local arrays, might crash

# RIGHT - use heap allocation
buffer = ffi.new("char[1024*1024]")  # Allocated on heap via Python
```

## Best Practices

1. **Prefer ffi.new() for simplicity**: Zero-initialization prevents surprises
2. **Use ffi.buffer() for Python integration**: Efficient buffer protocol support
3. **Track ownership clearly**: Document who frees each allocation
4. **Convert strings immediately**: Don't keep C string pointers around
5. **Use context managers for cleanup**: Ensure proper resource release
6. **Avoid circular references**: Can prevent garbage collection
7. **Profile memory usage**: Use tracemalloc or similar for large applications

## References

- [CFFI Documentation - Using the ffi/lib objects](https://cffi.readthedocs.io/en/stable/using.html)
- [CFFI Reference - Memory Management](https://cffi.readthedocs.io/en/stable/ref.html)
- [Python Buffer Protocol](https://docs.python.org/3/c-api/buffer.html)
