# CFFI Advanced Topics - Complete Guide

## Overview

This reference covers advanced CFFI features including variadic functions, Windows calling conventions, debugging techniques, performance optimization, and complex integration patterns.

## Variadic Functions

### Declaring Variadic Functions

Variadic functions accept a variable number of arguments (like `printf`):

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    int printf(const char *format, ...);
    int fprintf(int fd, const char *format, ...);
    void vprintf(const char *format, void *ap);
    
    double my_variadic_function(double x, ...);
""")

lib = ffi.dlopen(None)  # C library for printf
```

### Calling Variadic Functions

Use `ffi.new()` to create argument lists:

```python
# Simple variadic call
lib.printf(b"Hello %s!\n", b"World")
lib.printf(b"Number: %d, Float: %f\n", 42, 3.14)

# Multiple arguments
lib.printf(b"%d + %d = %d\n", 5, 3, 5 + 3)
```

### Custom Variadic Functions

For custom variadic functions, use `ffi.argtypes` or explicit casting:

```python
ffi.cdef("int sum(int count, ...);")

lib = ffi.dlopen("mylib.so")

# Call with variable arguments
result = lib.sum(3, 10, 20, 30)  # Should return 60
```

### Variadic Functions with Pointers

```python
ffi.cdef("""
    int parse_values(const char *format, ...);
    void store_values(int count, ...);
""")

lib = ffi.dlopen("mylib.so")

# Passing pointers to variadic function
buffer = ffi.new("char[256]")
lib.parse_values(b"%d %s", 42, b"test")
```

## Windows Calling Conventions

### Standard Calling Conventions

Windows supports multiple calling conventions:

```python
ffi.cdef("""
    // Standard C convention (default)
    int standard_function(int x);
    
    // STDCALL (used by Windows API)
    int __stdcall windows_api_function(int x);
    
    // CDECL (default for variadic)
    int __cdecl cdecl_function(int x);
    
    // FASTCALL (less common)
    int __fastcall fastcall_function(int x);
""")

lib = ffi.dlopen("mydll.dll")
```

### Windows API Examples

```python
import sys
if sys.platform == "win32":
    ffi.cdef("""
        BOOL __stdcall SetWindowTextA(HWND hwnd, LPCSTR lpString);
        DWORD __stdcall GetCurrentThreadId(void);
        HANDLE __stdcall CreateFileA(
            LPCSTR lpFileName,
            DWORD dwDesiredAccess,
            DWORD dwShareMode,
            LPSECURITY_ATTRIBUTES lpSecurityAttributes,
            DWORD dwCreationDisposition,
            DWORD dwFlagsAndAttributes,
            HANDLE hTemplateFile
        );
    """)
    
    import ctypes
    lib = ffi.dlopen(ctypes.windll.kernel32)
    
    thread_id = lib.GetCurrentThreadId()
    print(f"Thread ID: {thread_id}")
```

### Finding Windows Libraries

```python
import sys
import ctypes.util

if sys.platform == "win32":
    # Use ctypes.util.find_library for system DLLs
    user32_path = ctypes.util.find_library("user32")
    lib = ffi.dlopen(user32_path)
    
    # Or use ctypes.windll for STDCALL by default
    lib = ffi.dlopen(ctypes.windll.user32.LoadLibraryA(b"mydll.dll"))
```

## Debugging CFFI Applications

### Runtime Type Inspection

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    struct point {
        int x;
        int y;
    };
    
    typedef struct point Point;
    Point* create_point(int x, int y);
""")

lib = ffi.dlopen("mylib.so")

# Inspect types
p = lib.create_point(10, 20)

print(f"Type of p: {ffi.typeof(p)}")
print(f"Size of point: {ffi.sizeof('struct point')}")
print(f"Alignment: {ffi.alignof('struct point')}")

# Check field offsets
print(f"Offset of x: {ffi.offsetof('struct point', 'x')}")
print(f"Offset of y: {ffi.offsetof('struct point', 'y')}")

# Inspect fields
point_type = ffi.typeof("struct point")
for field_name in point_type.fields:
    field = point_type.fields[field_name]
    print(f"Field '{field_name}': type={field.type}, offset={field.offset}")
```

### Memory Inspection

```python
import ctypes
from cffi import FFI

ffi = FFI()
ffi.cdef("int* create_array(int n);")

lib = ffi.dlopen("mylib.so")

arr = lib.create_array(5)

# Get pointer address
addr = ffi.addressof(arr[0])
print(f"Array address: {hex(addr)}")

# Inspect raw memory
buf = ffi.buffer(arr, ffi.sizeof("int") * 5)
print(f"Raw bytes: {list(buf)}")

# Cast to different type for inspection
char_ptr = ffi.cast("char *", arr)
for i in range(20):  # 5 ints * 4 bytes
    print(f"Byte {i}: {char_ptr[i]}")
```

### Using GDB with CFFI

```python
import sys
import os
from cffi import FFI

# Add breakpoint
def debug_break():
    import gdb  # Only works when running under gdb
    gdb.execute('break next_function')
    gdb.execute('continue')

ffi = FFI()
ffi.cdef("""
    int process_data(int *data, int size);
    void next_function(void);
""")

lib = ffi.dlopen("mylib.so")

# Run under gdb:
# gdb --args python3 script.py
# (gdb) break debug_break
# (gdb) run

data = ffi.new("int[]", [1, 2, 3, 4, 5])
debug_break()
result = lib.process_data(data, 5)
```

### Verbose Error Messages

```python
import cffi
cffi.set_debug_hook(True)  # Enable debug mode

from cffi import FFI
ffi = FFI()
ffi.cdef("int problematic_function(int x);")

lib = ffi.dlopen("mylib.so")

# Errors will include more context
try:
    result = lib.problematic_function(None)  # Wrong type
except Exception as e:
    print(f"Error with full context: {e}")
    import traceback
    traceback.print_exc()
```

## Performance Optimization

### Reducing Callback Overhead

```python
from cffi import FFI
import time

ffi = FFI()
ffi.cdef("""
    typedef int (*processor)(int value);
    void process_batch(int *data, int count, processor fn);
""")

lib = ffi.dlopen("mylib.so")

# SLOW: Python callback for each element
@ffi.callback("processor")
def slow_processor(value):
    return value * 2

data = ffi.new("int[]", list(range(1000000)))

start = time.time()
lib.process_batch(data, len(data), slow_processor)
print(f"Callback approach: {time.time() - start:.3f}s")

# FAST: Do processing in C
ffi.cdef("void process_batch_c(int *data, int count);")

start = time.time()
lib.process_batch_c(data, len(data))
print(f"C processing: {time.time() - start:.3f}s")
```

### Memory Allocation Patterns

```python
from cffi import FFI
import time

ffi = FFI()
ffi.cdef("void process_buffer(char *buf, int size);")

lib = ffi.dlopen("mylib.so")

# SLOW: Allocate new buffer each time
def slow_processing(iterations):
    for _ in range(iterations):
        buf = ffi.new("char[1024]")
        lib.process_buffer(buf, 1024)

# FAST: Reuse buffer
def fast_processing(iterations):
    buf = ffi.new("char[1024]")  # Allocate once
    for _ in range(iterations):
        lib.process_buffer(buf, 1024)

iterations = 10000

start = time.time()
slow_processing(iterations)
print(f"New allocation: {time.time() - start:.3f}s")

start = time.time()
fast_processing(iterations)
print(f"Reused buffer: {time.time() - start:.3f}s")
```

### Batch Operations

```python
from cffi import FFI

ffi = FFI()

# SLOW: Individual calls
ffi.cdef("int add(int x, int y);")

# FAST: Batch operation
ffi.cdef("void add_arrays(int *a, int *b, int *result, int count);")

lib = ffi.dlopen("mylib.so")

n = 1000000
a = ffi.new("int[]", [1] * n)
b = ffi.new("int[]", [2] * n)
result = ffi.new("int[]", [0] * n)

# Batch operation is much faster
lib.add_arrays(a, b, result, n)
```

### API Mode vs ABI Mode Performance

```python
import time

# ABI mode (in-line)
from cffi import FFI
ffi_abi = FFI()
ffi_abi.cdef("int compute(int x);")
lib_abi = ffi_abi.dlopen("mylib.so")

# API mode (out-of-line) - assume _compute module exists
from _compute import lib as lib_api

n_iterations = 100000

# Test ABI mode
start = time.time()
for i in range(n_iterations):
    lib_abi.compute(i)
abi_time = time.time() - start

# Test API mode
start = time.time()
for i in range(n_iterations):
    lib_api.compute(i)
api_time = time.time() - start

print(f"ABI mode: {abi_time:.3f}s")
print(f"API mode: {api_time:.3f}s")
print(f"Speedup: {abi_time / api_time:.2f}x")
```

## Advanced Memory Techniques

### Custom Memory Allocators

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    void *my_malloc(size_t size);
    void my_free(void *ptr);
    void *my_realloc(void *ptr, size_t size);
""")

lib = ffi.dlopen("mylib.so")

# Use custom allocator
ptr = lib.my_malloc(1024)
int_ptr = ffi.cast("int *", ptr)
int_ptr[0] = 42

# Modify size
ptr = lib.my_realloc(ptr, 2048)

# Free when done
lib.my_free(ptr)
```

### Memory-Mapped Files

```python
from cffi import FFI
import os

ffi = FFI()
ffi.cdef("""
    void *mmap(
        void *addr,
        size_t length,
        int prot,
        int flags,
        int fd,
        off_t offset
    );
    int munmap(void *addr, size_t length);
    int close(int fd);
""")

lib = ffi.dlopen(None)  # C library

# Constants
PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_SHARED = 0x1
MAP_PRIVATE = 0x2

# Memory-map a file
fd = os.open("data.bin", os.O_RDWR)
file_size = os.fstat(fd).st_size

addr = lib.mmap(
    ffi.NULL,
    file_size,
    PROT_READ | PROT_WRITE,
    MAP_SHARED,
    fd,
    0
)

# Use mapped memory
data_ptr = ffi.cast("char *", addr)
for i in range(min(100, file_size)):
    print(f"Byte {i}: {data_ptr[i]}")

# Unmap and close
lib.munmap(addr, file_size)
lib.close(fd)
```

### Zero-Copy Data Transfer

```python
import array
from cffi import FFI

ffi = FFI()
ffi.cdef("void process_floats(float *data, int count);")

lib = ffi.dlopen("mylib.so")

# Create Python array
py_array = array.array('f', [1.0, 2.0, 3.0, 4.0, 5.0])

# Get pointer to underlying data (zero-copy)
data_ptr = ffi.cast("float *", py_array.buffer_info()[0])

# Pass directly to C without copying
lib.process_floats(data_ptr, len(py_array))

# Data in py_array may be modified by C function
print(list(py_array))
```

## Complex Integration Patterns

### Wrapper Classes with Context Managers

```python
from cffi import FFI
from contextlib import contextmanager

ffi = FFI()
ffi.cdef("""
    typedef struct database Database;
    Database* db_open(const char *path);
    void db_close(Database *db);
    int db_query(Database *db, const char *query);
    const char* db_error(Database *db);
""")

lib = ffi.dlopen("mylib.so")

class Database:
    def __init__(self, path):
        self.path = path
        self._db = None
    
    def __enter__(self):
        self._db = lib.db_open(self.path.encode('utf-8'))
        if not self._db:
            error = lib.db_error(ffi.NULL)
            raise RuntimeError(f"Failed to open database: {ffi.string(error).decode()}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._db:
            lib.db_close(self._db)
            self._db = None
    
    def query(self, sql):
        if not self._db:
            raise RuntimeError("Database not open")
        
        result = lib.db_query(self._db, sql.encode('utf-8'))
        if result < 0:
            error = lib.db_error(self._db)
            raise RuntimeError(f"Query failed: {ffi.string(error).decode()}")
        
        return result

# Usage
with Database("/path/to/db.sqlite") as db:
    count = db.query("SELECT COUNT(*) FROM users")
    print(f"User count: {count}")
```

### Factory Pattern for C Objects

```python
from cffi import FFI
from typing import Dict, Type, Any

ffi = FFI()
ffi.cdef("""
    typedef struct renderer Renderer;
    Renderer* renderer_createOpenGL(void);
    Renderer* renderer_createVulkan(void);
    Renderer* renderer_createSoftware(void);
    void renderer_free(Renderer *r);
    void renderer_render(Renderer *r, int width, int height);
""")

lib = ffi.dlopen("mylib.so")

class Renderer:
    _instances: Dict[int, 'Renderer'] = {}
    
    def __init__(self, type_str: str):
        self.type = type_str
        if type_str == "opengl":
            self._renderer = lib.renderer_createOpenGL()
        elif type_str == "vulkan":
            self._renderer = lib.renderer_createVulkan()
        elif type_str == "software":
            self._renderer = lib.renderer_createSoftware()
        else:
            raise ValueError(f"Unknown renderer type: {type_str}")
        
        if not self._renderer:
            raise RuntimeError(f"Failed to create {type_str} renderer")
        
        self._id = id(self._renderer)
        Renderer._instances[self._id] = self
    
    def __del__(self):
        if hasattr(self, '_renderer') and self._renderer:
            lib.renderer_free(self._renderer)
            if self._id in Renderer._instances:
                del Renderer._instances[self._id]
    
    def render(self, width: int, height: int):
        lib.renderer_render(self._renderer, width, height)
    
    @classmethod
    def factory(cls, type_str: str) -> 'Renderer':
        return cls(type_str)

# Usage
renderers = [
    Renderer.factory("opengl"),
    Renderer.factory("vulkan"),
]

for r in renderers:
    r.render(1920, 1080)
```

### Event-Driven Architecture

```python
from cffi import FFI
import threading
from queue import Queue

ffi = FFI()
ffi.cdef("""
    typedef void (*event_callback)(int event_type, void *data, void *user_data);
    void event_loop_set_callback(event_callback cb, void *user_data);
    void event_loop_run(void);
    void event_loop_stop(void);
""")

lib = ffi.dlopen("mylib.so")

class EventSystem:
    def __init__(self):
        self.event_queue: Queue = Queue()
        self._running = False
    
    def start(self):
        self._running = True
        
        @ffi.callback("event_callback")
        def event_handler(event_type, data, user_data):
            # Convert C event to Python event
            python_event = {
                'type': event_type,
                'data': ffi.cast("int *", data)[0] if data else None
            }
            
            # Queue for Python processing
            self.event_queue.put(python_event)
        
        lib.event_loop_set_callback(event_handler, None)
        
        # Run event loop in separate thread
        self._thread = threading.Thread(target=self._run_loop)
        self._thread.start()
    
    def _run_loop(self):
        lib.event_loop_run()
    
    def stop(self):
        self._running = False
        lib.event_loop_stop()
        if hasattr(self, '_thread'):
            self._thread.join()
    
    def get_event(self, timeout=1.0):
        return self.event_queue.get(timeout=timeout)

# Usage
event_system = EventSystem()
event_system.start()

try:
    while event_system._running:
        try:
            event = event_system.get_event(timeout=1.0)
            print(f"Event: {event}")
        except:
            continue
except KeyboardInterrupt:
    event_system.stop()
```

## Troubleshooting Advanced Issues

### Stack Overflow in Recursive C Calls

```python
# Problem: Deep recursion in C can overflow stack
ffi.cdef("void recursive_function(int depth);")

lib = ffi.dlopen("mylib.so")

# Solution: Increase stack size or limit recursion
import resource

# Get current stack size
soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
print(f"Current stack: {soft} bytes")

# Increase stack size (if allowed)
try:
    resource.setrlimit(resource.RLIMIT_STACK, (hard, hard))
    print(f"Increased stack to: {hard} bytes")
except ValueError as e:
    print(f"Cannot increase stack: {e}")

# Or limit recursion depth in Python wrapper
MAX_DEPTH = 1000

def safe_recursive(depth):
    if depth > MAX_DEPTH:
        raise RecursionError(f"Maximum depth {MAX_DEPTH} exceeded")
    lib.recursive_function(depth)
```

### Handling C Exceptions

Some C++ libraries throw exceptions. Handle with care:

```python
ffi.cdef("""
    int try_catch_wrapper(void);
    const char* get_last_exception(void);
""")

lib = ffi.dlopen("mylib.so")

result = lib.try_catch_wrapper()
if result < 0:
    exc_msg = lib.get_last_exception()
    if exc_msg:
        print(f"C++ exception caught: {ffi.string(exc_msg).decode()}")
```

### Platform-Specific Bugs

```python
import sys
import platform

print(f"Platform: {platform.platform()}")
print(f"Python: {sys.version}")
print(f"Architecture: {platform.architecture()}")

# Handle platform-specific issues
if sys.platform == "darwin":
    # macOS-specific workarounds
    ffi.cdef("int macos_specific_function(void);")
elif sys.platform == "win32":
    # Windows-specific workarounds  
    ffi.cdef("int __stdcall windows_specific_function(void);")
else:
    # Linux/Unix
    ffi.cdef("int unix_specific_function(void);")
```

## References

- [CFFI Documentation - Variadic Functions](https://cffi.readthedocs.io/en/stable/using.html#variadic-function-calls)
- [CFFI Documentation - Windows Calling Conventions](https://cffi.readthedocs.io/en/stable/using.html#windows-calling-conventions)
- [Python Performance Tips](https://docs.python.org/3/library/profile.html)
- [C Standard Library Reference](https://en.cppreference.com/w/c/header)
