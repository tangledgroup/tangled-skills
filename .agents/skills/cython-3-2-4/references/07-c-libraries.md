# Wrapping C Libraries

## Basic Pattern

### Step 1: Create .pxd Declaration File

```python
# mylib.pxd
cdef extern from "mylib.h":
    """C header contents or just include"""
    
    # Functions
    int c_function(int x, float y)
    void c_void_function(char *str)
    double *c_return_pointer(int size)
    
    # Constants
    int MYLIB_VERSION_MAJOR
    int MYLIB_VERSION_MINOR
    
    # Types
    struct my_struct:
        int field1
        double field2
        char name[64]
    
    typedef int my_int_type
```

### Step 2: Create .pyx Wrapper File

```python
# mylib.pyx
from mylib cimport c_function, c_void_function, my_struct

def python_wrapper(int x, float y):
    """Call C function from Python"""
    return c_function(x, y)

def process_string(string text):
    """Pass Python string to C"""
    cdef char *c_str = text.encode('utf-8')
    c_void_function(c_str)
```

### Step 3: Build

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "mylib",
    ["mylib.pyx", "c_source.c"],  # Include C source if needed
    include_dirs=["./include"],   # Path to headers
    libraries=["mylib"]           # Link with libmylib.so
)

setup(ext_modules=cythonize([ext]))
```

## Data Type Mapping

### Basic Types

| C Type | Cython Type | Python Type |
|--------|-------------|-------------|
| `int` | `int` | `int` |
| `float` | `float` | `float` |
| `double` | `double` | `float` |
| `char` | `char` | `str` (1 char) |
| `char*` | `char*` | `str` or `bytes` |
| `void*` | `void*` | `None` or custom |
| `size_t` | `size_t` | `int` |
| `bool` | `bint` | `bool` |

### String Handling

```python
from libc.string cimport strlen, strcpy
from cpython.bytes cimport PyBytes_FromStringAndSize

cdef extern from "string.h":
    char *strcpy(char *dest, const char *src)

def process_c_string(bytes python_bytes):
    """Python bytes to C string"""
    cdef char *c_str = python_bytes
    
    # Use C string functions
    length = strlen(c_str)
    
    return length

def return_string_to_python():
    """C string to Python"""
    cdef char *c_result = b"Hello from C"
    return PyBytes_FromStringAndSize(c_result, 14).decode('utf-8')
```

### Struct Handling

```python
cdef extern from "mylib.h":
    struct Point:
        double x
        double y
        double z
    
    Point create_point(double x, double y, double z)
    double point_distance(Point a, Point b)

# Option 1: Direct struct access
def use_struct_direct():
    cdef Point p = create_point(1.0, 2.0, 3.0)
    return point_distance(p, p)

# Option 2: Wrap in extension type
cdef class CyPoint:
    cdef Point internal
    
    def __init__(self, double x, double y, double z):
        self.internal = create_point(x, y, z)
    
    @property
    def x(self):
        return self.internal.x
    
    @x.setter
    def x(self, double value):
        self.internal.x = value
    
    def distance_to(self, CyPoint other):
        return point_distance(self.internal, other.internal)
```

## Pointer Handling

### Returning Pointers

```python
cdef extern from "allocator.h":
    int *create_array(int size) nogil
    void free_array(int *arr) nogil

class ManagedArray:
    """Python wrapper with automatic cleanup"""
    
    def __init__(self, int size):
        self.size = size
        self._ptr = create_array(size)
    
    def __getitem__(self, int index):
        if index < 0 or index >= self.size:
            raise IndexError()
        return self._ptr[index]
    
    def __setitem__(self, int index, int value):
        if index < 0 or index >= self.size:
            raise IndexError()
        self._ptr[index] = value
    
    def __del__(self):
        free_array(self._ptr)
```

### Const Pointers

```python
cdef extern from "readonly.h":
    const char *get_version_string()
    const int *get_config_array(int size)

def read_version():
    cdef const char *version = get_version_string()
    return version.decode('utf-8')
```

## Error Handling

### Exception Specification

```python
cdef extern from "mylib.h" nogil:
    int risky_operation(int x) except -1
    void may_fail() except?
    
    # No exception handling
    int always_safe(int x) noexcept

def safe_call(int x):
    """Raises Python exception if C function returns -1"""
    result = risky_operation(x)  # Automatically checked
    return result

def check_exception():
    """May raise C++ exception, caught by Cython"""
    may_fail()  # except? means "check for any exception"
```

### Error Codes to Exceptions

```python
cdef extern from "mylib.h":
    int operation(int x)
    int get_last_error()
    const char *error_string(int code)

CPDEF int wrapped_operation(int x):
    cdef int result = operation(x)
    
    if result < 0:
        cdef int err = get_last_error()
        raise RuntimeError(f"Operation failed: {error_string(err)}")
    
    return result
```

## Callbacks

### Python Callback to C

```python
cdef extern from "callback.h":
    typedef void (*callback_t)(int, void *)
    void register_callback(callback_t cb, void *user_data)
    void trigger_callback()

cdef void c_callback_wrapper(int value, void *user_data):
    """C-compatible wrapper around Python callable"""
    cdef object python_cb = <object>user_data
    python_cb(value)  # Call Python function

def register_python_callback(callable cb):
    """Register Python callable with C library"""
    register_callback(c_callback_wrapper, cb)
```

### C Callback to Python

```python
from libcpp cimport ref

cdef class WithCallback:
    cdef object _callback
    
    def __init__(self, callable callback):
        self._callback = callback
    
    cdef void on_event(self, int event_id) nogil:
        """Called from C library"""
        with gil:  # Need GIL to call Python
            self._callback(event_id)
```

## Common Patterns

### Resource Management with Context Manager

```python
cdef extern from "resource.h":
    void *open_resource(const char *path)
    void close_resource(void *handle)
    int read_data(void *handle, char *buffer, int size)

cdef class Resource:
    def __init__(self, string path):
        self.handle = open_resource(path.encode('utf-8'))
        if self.handle == NULL:
            raise IOError(f"Cannot open {path}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        close_resource(self.handle)
        return False
    
    def read(self, int size):
        cdef char *buffer = <char *>malloc(size)
        cdef int bytes_read = read_data(self.handle, buffer, size)
        
        result = buffer[:bytes_read]
        free(buffer)
        return result

# Usage
with Resource("data.bin") as res:
    data = res.read(1024)
```

### Iterator Pattern

```python
cdef extern from "iterator.h":
    void *create_iterator()
    void destroy_iterator(void *it)
    bint next_item(void *it, int *value)

class CIterator:
    def __init__(self):
        self._iterator = create_iterator()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        cdef int value
        if next_item(self._iterator, &value):
            return value
        raise StopIteration
    
    def __del__(self):
        destroy_iterator(self._iterator)

# Usage
for value in CIterator():
    print(value)
```

## Debugging C Interop

### Adding Assertions

```python
from libc.stdlib cimport abort

cdef extern from "mylib.h":
    int *create_array(int size)

def safe_create_array(int size):
    if size <= 0:
        raise ValueError("Size must be positive")
    
    cdef int *arr = create_array(size)
    
    if arr == NULL:
        raise MemoryError("Failed to allocate array")
    
    return arr
```

### Logging C Function Calls

```python
import logging
log = logging.getLogger(__name__)

cdef extern from "mylib.h":
    int compute(int x, int y)

def logged_compute(int x, int y):
    log.debug(f"Calling compute({x}, {y})")
    result = compute(x, y)
    log.debug(f"Result: {result}")
    return result
```

See [SKILL.md](../SKILL.md) for overview and [C++ Libraries](08-cpp-libraries.md) for C++ wrapping.
