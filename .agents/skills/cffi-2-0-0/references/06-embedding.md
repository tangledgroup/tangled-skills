# CFFI Embedding - Complete Guide

## Overview

CFFI embedding allows you to create shared libraries (.so, .dll) that embed the Python interpreter and expose Python functions as C-callable exports. This enables C applications to call Python code without knowing it's Python underneath.

## Basic Embedding Pattern

### Simple Example

```python
# build_embedded_lib.py
import cffi

ffibuilder = cffi.FFI()

# Declare the API that will be exposed to C
ffibuilder.embedding_api("""
    int add_numbers(int x, int y);
    const char* greet_person(const char* name);
    void log_message(const char* message);
""")

# Set source (empty for pure Python implementation)
ffibuilder.set_source("my_python_lib", "")

# Initialize and define Python implementations
ffibuilder.embedding_init_code("""
    from my_python_lib import ffi
    
    @ffi.def_extern()
    def add_numbers(x, y):
        print(f"Python adding {x} + {y}")
        return x + y
    
    @ffi.def_extern()
    def greet_person(name):
        # Convert C string to Python
        python_name = ffi.string(name).decode('utf-8')
        greeting = f"Hello, {python_name}!"
        
        # Return static string (must live for process duration)
        # Store somewhere persistent
        greet_person._last_greeting = ffi.new("char[]", greeting.encode('utf-8'))
        return greet_person._last_greeting
    
    @ffi.def_extern()
    def log_message(message):
        python_msg = ffi.string(message).decode('utf-8')
        print(f"LOG: {python_msg}")
""")

if __name__ == "__main__":
    # Compile to shared library
    ffibuilder.compile(
        target="libmy_python_lib.so",  # .dll on Windows
        verbose=True
    )
```

### Using the Embedded Library from C

```c
// use_from_c.c
#include <stdio.h>

// Declare the functions exposed by the Python library
extern int add_numbers(int x, int y);
extern const char* greet_person(const char* name);
extern void log_message(const char* message);

int main() {
    // Call Python-implemented functions
    int sum = add_numbers(5, 3);
    printf("Sum: %d\n", sum);
    
    const char* greeting = greet_person("World");
    printf("%s\n", greeting);
    
    log_message("This is a test message");
    
    return 0;
}
```

Compile and run:
```bash
gcc -o use_from_c use_from_c.c -L. -lmy_python_lib -Wl,-rpath,.
./use_from_c
```

## Advanced Embedding Patterns

### State Management

```python
ffibuilder.embedding_api("""
    void* create_counter(void);
    void free_counter(void* counter);
    int increment(void* counter);
    int get_value(void* counter);
""")

ffibuilder.set_source("counter_lib", "")

ffibuilder.embedding_init_code("""
    from counter_lib import ffi
    
    # Store counters in a dictionary
    _counters = {}
    _next_id = 0
    
    @ffi.def_extern()
    def create_counter():
        global _next_id
        _counters[_next_id] = 0
        counter_id = _next_id
        _next_id += 1
        return ffi.new("int *", counter_id)
    
    @ffi.def_extern()
    def free_counter(counter_ptr):
        counter_id = counter_ptr[0]
        if counter_id in _counters:
            del _counters[counter_id]
    
    @ffi.def_extern()
    def increment(counter_ptr):
        counter_id = counter_ptr[0]
        if counter_id in _counters:
            _counters[counter_id] += 1
            return _counters[counter_id]
        return -1
    
    @ffi.def_extern()
    def get_value(counter_ptr):
        counter_id = counter_ptr[0]
        return _counters.get(counter_id, -1)
""")

if __name__ == "__main__":
    ffibuilder.compile(target="libcounter.so", verbose=True)
```

### Error Handling

```python
ffibuilder.embedding_api("""
    typedef struct {
        const char* message;
        int code;
    } ErrorInfo;
    
    int divide(int numerator, int denominator, ErrorInfo* error);
    void free_error(ErrorInfo* error);
""")

ffibuilder.set_source("math_lib", "")

# Global storage for error messages
_error_messages = {}
_next_error_id = 0

ffibuilder.embedding_init_code(f"""
    from math_lib import ffi
    
    _error_messages = {{}}
    _next_error_id = 0
    
    @ffi.def_extern()
    def divide(numerator, denominator, error_ptr):
        global _next_error_id
        
        if denominator == 0:
            # Create error message
            msg = "Division by zero"
            _error_messages[_next_error_id] = ffi.new("char[]", msg.encode('utf-8'))
            error_ptr[0].message = _error_messages[_next_error_id]
            error_ptr[0].code = 1
            _next_error_id += 1
            return 0
        
        # Success
        error_ptr[0].message = ffi.NULL
        error_ptr[0].code = 0
        return numerator // denominator
    
    @ffi.def_extern()
    def free_error(error_ptr):
        if error_ptr and error_ptr[0].message:
            # Note: In real code, track which messages we allocated
            pass
""")

if __name__ == "__main__":
    ffibuilder.compile(target="libmath.so", verbose=True)
```

### Complex Data Structures

```python
ffibuilder.embedding_api("""
    typedef struct Point Point;
    
    Point* point_create(double x, double y);
    void point_free(Point* p);
    double point_x(Point* p);
    double point_y(Point* p);
    void point_set(Point* p, double x, double y);
    double point_distance(Point* a, Point* b);
""")

ffibuilder.set_source("geometry_lib", "")

ffibuilder.embedding_init_code("""
    from geometry_lib import ffi
    import math
    
    @ffi.def_extern()
    def point_create(x, y):
        # Store Python tuple in cdata
        p = ffi.new("Point *")
        p.x = x
        p.y = y
        return p
    
    @ffi.def_extern()
    def point_free(p):
        ffi.release(p)
    
    @ffi.def_extern()
    def point_x(p):
        return p.x
    
    @ffi.def_extern()
    def point_y(p):
        return p.y
    
    @ffi.def_extern()
    def point_set(p, x, y):
        p.x = x
        p.y = y
    
    @ffi.def_extern()
    def point_distance(a, b):
        dx = a.x - b.x
        dy = a.y - b.y
        return math.sqrt(dx*dx + dy*dy)
""")

if __name__ == "__main__":
    ffibuilder.compile(target="libgeometry.so", verbose=True)
```

## Multi-File Embedding

### Splitting Across Modules

```python
# build_core.py
import cffi

ffibuilder = cffi.FFI()

# Core API
ffibuilder.embedding_api("""
    void init_system(void);
    void shutdown_system(void);
    int is_initialized(void);
""")

ffibuilder.set_source("core", "")

ffibuilder.embedding_init_code("""
    from core import ffi
    
    _initialized = False
    
    @ffi.def_extern()
    def init_system():
        global _initialized
        print("System initialized")
        _initialized = True
    
    @ffi.def_extern()
    def shutdown_system():
        global _initialized
        print("System shutting down")
        _initialized = False
    
    @ffi.def_extern()
    def is_initialized():
        return 1 if _initialized else 0
""")

if __name__ == "__main__":
    ffibuilder.compile(target="libcore.so", verbose=True)
```

```python
# build_plugin.py
import cffi

ffibuilder = cffi.FFI()

# Plugin API that depends on core
ffibuilder.embedding_api("""
    void* plugin_load(const char* name);
    void plugin_unload(void* plugin);
    int plugin_execute(void* plugin, const char* command);
""")

ffibuilder.set_source("plugin", "")

ffibuilder.embedding_init_code("""
    from plugin import ffi
    
    _plugins = {}
    
    @ffi.def_extern()
    def plugin_load(name):
        plugin_name = ffi.string(name).decode('utf-8')
        _plugins[len(_plugins)] = plugin_name
        return ffi.new("int *", len(_plugins) - 1)
    
    @ffi.def_extern()
    def plugin_unload(plugin):
        plugin_id = plugin[0]
        if plugin_id in _plugins:
            del _plugins[plugin_id]
    
    @ffi.def_extern()
    def plugin_execute(plugin, command):
        plugin_id = plugin[0]
        cmd = ffi.string(command).decode('utf-8')
        if plugin_id in _plugins:
            print(f"Executing {cmd} on {_plugins[plugin_id]}")
            return 1
        return 0
""")

if __name__ == "__main__":
    ffibuilder.compile(target="libplugin.so", verbose=True)
```

## Thread Safety in Embedding

### Thread-Safe Callbacks

```python
import threading
import cffi

ffibuilder = cffi.FFI()

ffibuilder.embedding_api("""
    void process_data(const char* data, int length);
""")

ffibuilder.set_source("threadsafe", "")

# Thread lock for shared state
_lock = threading.Lock()
_results = []

ffibuilder.embedding_init_code(f"""
    from threadsafe import ffi
    
    _lock = threading.Lock()
    _results = []
    
    @ffi.def_extern()
    def process_data(data_ptr, length):
        # GIL is automatically acquired
        data = ffi.buffer(data_ptr, length).raw
        
        with _lock:
            _results.append(data)
            
        print(f"Processed {length} bytes")
""")

if __name__ == "__main__":
    ffibuilder.compile(target="libthreadsafe.so", verbose=True)
```

## Free-Threaded Python Support (3.14+)

### Embedding in Free-Threaded Builds

```python
import sys
import cffi

ffibuilder = cffi.FFI()

ffibuilder.embedding_api("""
    int compute(int x);
""")

ffibuilder.set_source("freethreaded_lib", "")

# Check if we're building for free-threaded Python
FREE_THREADED = bool(__import__('sysconfig').get_config_var('Py_GIL_DISABLED'))

ffibuilder.embedding_init_code(f"""
    from freethreaded_lib import ffi
    
    @ffi.def_extern()
    def compute(x):
        # GIL is automatically managed even in free-threaded builds
        # Python code here runs with appropriate locking
        result = x * 2
        
        # If doing long computation, can release GIL manually
        # for the C-level work, but Python code always has GIL
        
        return result
""")

if __name__ == "__main__":
    ffibuilder.compile(
        target="libfreethreaded.so", 
        verbose=True
    )
```

## Testing Embedded Libraries

### Python-Side Tests

```python
# test_embedded.py
import ctypes
import os

# Load the shared library
lib_path = os.path.abspath("libmy_python_lib.so")
lib = ctypes.CDLL(lib_path)

# Configure argument and return types
lib.add_numbers.argtypes = [ctypes.c_int, ctypes.c_int]
lib.add_numbers.restype = ctypes.c_int

lib.greet_person.argtypes = [ctypes.c_char_p]
lib.greet_person.restype = ctypes.c_char_p

lib.log_message.argtypes = [ctypes.c_char_p]
lib.log_message.restype = None

# Test functions
def test_add():
    result = lib.add_numbers(5, 3)
    assert result == 8, f"Expected 8, got {result}"

def test_greet():
    greeting = lib.greet_person(b"Test")
    assert greeting is not None
    assert b"Test" in greeting

def test_log():
    lib.log_message(b"Test message")
    # Check output in logs

if __name__ == "__main__":
    test_add()
    test_greet()
    test_log()
    print("All tests passed!")
```

### C-Side Tests

```c
// test_from_c.c
#include <stdio.h>
#include <assert.h>

extern int add_numbers(int x, int y);
extern const char* greet_person(const char* name);
extern void log_message(const char* message);

int main() {
    // Test add_numbers
    int sum = add_numbers(10, 20);
    assert(sum == 30);
    printf("add_numbers test passed\n");
    
    // Test greet_person
    const char* greeting = greet_person("C User");
    assert(greeting != NULL);
    printf("greet_person test passed: %s\n", greeting);
    
    // Test log_message
    log_message("Test from C");
    printf("log_message test passed\n");
    
    printf("All C tests passed!\n");
    return 0;
}
```

Compile and run:
```bash
gcc -o test_from_c test_from_c.c -L. -lmy_python_lib -Wl,-rpath,.
./test_from_c
```

## Troubleshooting Embedding

### Common Issues

**"Python interpreter already initialized"**
```python
# Problem: Multiple embedding attempts
# Solution: Check initialization state

ffibuilder.embedding_init_code("""
    import sys
    
    # Only initialize once
    if not hasattr(sys, '_cffi_embedded_initialized'):
        sys._cffi_embedded_initialized = True
        
        @ffi.def_extern()
        def my_function(x):
            return x
""")
```

**"String returned doesn't live long enough"**
```python
# WRONG: String gets garbage collected
@ffi.def_extern()
def get_string():
    return ffi.new("char[]", "temporary".encode())  # Freed!

# RIGHT: Keep reference
_last_string = None

@ffi.def_extern()
def get_string():
    global _last_string
    _last_string = ffi.new("char[]", "persistent".encode())
    return _last_string
```

**"Segmentation fault on complex types"**
```python
# Ensure struct definitions match exactly
ffibuilder.embedding_api("""
    typedef struct {
        int x;
        double y;
    } MyStruct;
    
    MyStruct* create_struct(void);
""")

# Implementation must match
ffibuilder.embedding_init_code("""
    @ffi.def_extern()
    def create_struct():
        s = ffi.new("MyStruct *")
        s.x = 42
        s.y = 3.14
        return s
""")
```

## Deployment Considerations

### Bundling Python Interpreter

For standalone deployment, bundle the Python interpreter:

```python
# build_standalone.py
import sys
import cffi

ffibuilder = cffi.FFI()

ffibuilder.embedding_api("int hello(void);")
ffibuilder.set_source("standalone", "")

ffibuilder.embedding_init_code("""
    from standalone import ffi
    
    @ffi.def_extern()
    def hello():
        print("Hello from embedded Python!")
        return 42
""")

if __name__ == "__main__":
    # For PyInstaller or similar
    ffibuilder.compile(target="libstandalone.so", verbose=True)
```

Then use PyInstaller:
```bash
pyinstaller --onefile --add-data "libstandalone.so:." main.py
```

### Shared Library Versioning

```python
# Versioned shared library
VERSION = "1.0"

ffibuilder.compile(
    target=f"libmylib.so.{VERSION}",
    verbose=True
)

# Create symlink to latest version
import os
os.system(f"ln -sf libmylib.so.{VERSION} libmylib.so")
```

## References

- [CFFI Embedding Documentation](https://cffi.readthedocs.io/en/stable/embedding.html)
- [Python C API Reference](https://docs.python.org/3/c-api/)
- [ctypes Documentation](https://docs.python.org/3/library/ctypes.html)
