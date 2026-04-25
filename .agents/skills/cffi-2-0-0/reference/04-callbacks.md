# CFFI Callbacks - Complete Guide

## Overview

Callbacks allow C code to call back into Python functions. This is essential for implementing event handlers, comparison functions, iterators, and other patterns where C code needs to invoke Python code.

## Basic Callback Pattern

### Simple Example

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    typedef void (*print_callback)(const char *message);
    void register_printer(print_callback cb);
""")

lib = ffi.dlopen("mylib.so")

# Create callback
@ffi.callback("print_callback")
def my_printer(message):
    python_msg = ffi.string(message).decode('utf-8')
    print(f"Python received: {python_msg}")

# Register with C library
lib.register_printer(my_printer)

# C library will call my_printer() when needed
```

### Callback with Arguments and Return Value

```python
ffi.cdef("""
    typedef int (*compare_callback)(const void *a, const void *b);
    void sort_array(int *array, int count, compare_callback cmp);
""")

lib = ffi.dlopen("mylib.so")

@ffi.callback("compare_callback")
def compare_ints(a, b):
    # a and b are pointers to int
    a_val = a[0]
    b_val = b[0]
    
    if a_val < b_val:
        return -1
    elif a_val > b_val:
        return 1
    else:
        return 0

# Use with C sorting function
array = ffi.new("int[]", [5, 2, 8, 1, 9])
lib.sort_array(array, 5, compare_ints)

print([array[i] for i in range(5)])  # [1, 2, 5, 8, 9]
```

## Callback Declaration Methods

### Using Typedef (Recommended)

```python
ffi.cdef("""
    // Define callback type
    typedef int (*string_compare)(const char *a, const char *b);
    
    // Function using callback
    void sort_strings(char **strings, int count, string_compare cmp);
""")

@ffi.callback("string_compare")
def strcmp_python(a, b):
    str_a = ffi.string(a).decode()
    str_b = ffi.string(b).decode()
    if str_a < str_b:
        return -1
    elif str_a > str_b:
        return 1
    return 0

lib = ffi.dlopen("mylib.so")
strings = [ffi.new("char[]", s.encode()) for s in ["banana", "apple", "cherry"]]
string_ptrs = ffi.new("char *[]", strings)
lib.sort_strings(string_ptrs, 3, strcmp_python)
```

### Using Inline Declaration

```python
ffi.cdef("""
    void foreach_int(int *array, int count, 
                     void (*callback)(int value, void *user_data),
                     void *user_data);
""")

@ffi.callback("void(int, void *)")
def print_value(value, user_data):
    print(f"Value: {value}, Context: {user_data[0]}")

lib = ffi.dlopen("mylib.so")
array = ffi.new("int[]", [1, 2, 3, 4, 5])
context = ffi.new("int[]", [42])
lib.foreach_int(array, 5, print_value, context)
```

## Callback with State

### Using Closure

```python
ffi.cdef("""
    typedef int (*accumulator)(int value, void *state);
    int reduce(int *array, int count, accumulator fn, int initial);
""")

lib = ffi.dlopen("mylib.so")

# Create state object
class SumAccumulator:
    def __init__(self):
        self.total = 0
        self.count = 0

state = SumAccumulator()

@ffi.callback("accumulator")
def add_value(value, state_ptr):
    # Convert void* back to Python object
    state_obj = ffi.from_handle(state_ptr, SumAccumulator)
    state_obj.total += value
    state_obj.count += 1
    return state_obj.total

array = ffi.new("int[]", [1, 2, 3, 4, 5])
result = lib.reduce(array, 5, add_value, 0)
```

### Using void* for State

```python
ffi.cdef("""
    typedef void (*iterator_callback)(int index, void *context);
    void iterate(int count, iterator_callback cb, void *context);
""")

lib = ffi.dlopen("mylib.so")

# Create C struct for context
ffi.cdef("""
    struct context {
        int *results;
        int offset;
    };
""")

context = ffi.new("struct context *")
context.results = ffi.new("int[10]")
context.offset = 100

@ffi.callback("iterator_callback")
def store_index(index, context_ptr):
    ctx = ffi.cast("struct context *", context_ptr)
    ctx.results[index] = index + ctx.offset

lib.iterate(5, store_index, context)

print([context.results[i] for i in range(5)])  # [100, 101, 102, 103, 104]
```

## Error Handling in Callbacks

### Raising Exceptions

```python
ffi.cdef("""
    typedef int (*validator)(const char *input);
    void validate_inputs(char **inputs, int count, validator fn);
""")

lib = ffi.dlopen("mylib.so")

@ffi.callback("validator")
def validate_input(input_str):
    try:
        text = ffi.string(input_str).decode('utf-8')
        value = int(text)
        if value < 0:
            raise ValueError("Negative values not allowed")
        return 1  # Valid
    except Exception as e:
        # Exceptions in callbacks are converted to error codes
        # or logged, depending on CFFI configuration
        print(f"Validation error: {e}")
        return 0  # Invalid

inputs = [ffi.new("char[]", b"42"), ffi.new("char[]", b"-5")]
input_ptrs = ffi.new("char *[]", inputs)
lib.validate_inputs(input_ptrs, 2, validate_input)
```

### Returning Error Codes

```python
ffi.cdef("""
    typedef int (*processor)(const char *data, char *output, int output_size);
    void process_batch(char **inputs, int count, processor fn);
""")

lib = ffi.dlopen("mylib.so")

@ffi.callback("processor")
def safe_processor(data, output, output_size):
    try:
        input_str = ffi.string(data).decode('utf-8')
        result = f"Processed: {input_str}".encode('utf-8')
        
        if len(result) >= output_size:
            return -1  # Buffer too small
        
        # Copy to output buffer
        for i, byte in enumerate(result):
            output[i] = byte
        output[len(result)] = 0  # Null terminate
        
        return len(result)  # Return bytes written
        
    except Exception as e:
        print(f"Error: {e}")
        return -2  # Processing error
```

## Callback Lifecycle

### Callback Lifetime

```python
from cffi import FFI
ffi = FFI()

# Callback must stay alive as long as C might call it
class CallbackHolder:
    def __init__(self):
        self.callback = None
        self.lib = ffi.dlopen("mylib.so")
        
    def create_callback(self):
        @ffi.callback("void(int)")
        def handler(value):
            print(f"Handling: {value}")
        
        # Store reference!
        self.callback = handler
        
        # Register with C
        self.lib.register_handler(handler)
        
        # C can now safely call handler

holder = CallbackHolder()
holder.create_callback()

# WRONG: Callback might be garbage collected
def bad_example():
    @ffi.callback("void(int)")
    def temp_handler(value):
        print(value)
    
    lib.register_handler(temp_handler)
    # temp_handler goes out of scope, might be GC'd!
```

### Explicit Callback Cleanup

```python
class ManagedCallback:
    def __init__(self, lib, callback_type):
        self.lib = lib
        self.callback = None
        self.callback_type = callback_type
        
    def __enter__(self):
        @ffi.callback(self.callback_type)
        def handler(*args):
            print(f"Callback called with {args}")
        
        self.callback = handler
        return self.callback
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Unregister callback
        if self.callback:
            self.lib.unregister_handler(self.callback)
            self.callback = None

# Usage
with ManagedCallback(lib, "void(int)") as cb:
    lib.register_handler(cb)
    # C can call callback safely
# Callback automatically unregistered here
```

## New-Style vs Old-Style Callbacks

### New-Style (Recommended)

```python
ffi.cdef("""
    typedef int (*my_callback)(int x, int y);
    void set_callback(my_callback cb);
""")

lib = ffi.dlopen("mylib.so")

@ffi.callback("my_callback")
def my_handler(x, y):
    return x + y

lib.set_callback(my_handler)
```

**Advantages:**
- Type-safe declaration
- Better error messages
- Supports complex types
- Preferred for new code

### Old-Style (Legacy)

```python
ffi.cdef("""
    void set_callback_raw(void *cb);
""")

lib = ffi.dlopen("mylib.so")

@ffi.callback("int(int, int)")
def old_handler(x, y):
    return x + y

# Pass callback as void*
lib.set_callback_raw(old_handler)
```

**When to use:**
- Legacy C APIs with void* callbacks
- Generic callback mechanisms
- Interfacing with older libraries

## Extern Functions (C Calling Python)

### @ffi.def_extern() for Embedding

```python
from cffi import FFI

ffibuilder = FFI()

# Declare what we'll export to C
ffibuilder.embedding_api("""
    int python_add(int x, int y);
    const char *python_greet(const char *name);
""")

# Implement in Python
ffibuilder.embedding_init_code("""
    from mymodule import ffi
    
    @ffi.def_extern()
    def python_add(x, y):
        print(f"Python adding {x} + {y}")
        return x + y
    
    @ffi.def_extern()
    def python_greet(name):
        python_name = ffi.string(name).decode('utf-8')
        greeting = f"Hello, {python_name}!".encode('utf-8')
        # Return static string (must live for duration of process)
        return ffi.new("char[]", greeting)
""")

# Build the shared library
ffibuilder.set_source("python_callbacks", "")

if __name__ == "__main__":
    ffibuilder.compile(target="libpython_callbacks.so", verbose=True)
```

### Using Extern Functions

```python
from cffi import FFI

ffi = FFI()

# Declare extern function signature
ffi.cdef("int my_extern_function(int x);")

# Define Python implementation
@ffi.def_extern()
def my_extern_function(x):
    print(f"Called from C with {x}")
    return x * 2

# Get pointer to function
func_ptr = ffi.addressof(ffi.getctype("int (*)(int)", "my_extern_function"))

# Pass to C code that expects function pointer
ffi.cdef("void call_function(int (*fn)(int));")
lib = ffi.dlopen("mylib.so")
lib.call_function(my_extern_function)
```

## Thread Safety with Callbacks

### GIL Handling

```python
from cffi import FFI
import threading

ffi = FFI()
ffi.cdef("""
    typedef void (*thread_callback)(int thread_id);
    void spawn_threads(int count, thread_callback cb);
""")

lib = ffi.dlopen("mylib.so")

lock = threading.Lock()
results = []

@ffi.callback("thread_callback")
def thread_handler(thread_id):
    # CFFI automatically acquires GIL before calling Python
    # But shared data still needs protection
    
    with lock:
        results.append(thread_id)
    
    print(f"Thread {thread_id} processed (Python thread safe)")

# C library spawns threads that call back into Python
lib.spawn_threads(4, thread_handler)
```

### Free-Threaded Python Considerations

In Python 3.14+ free-threaded builds:
- CFFI still acquires GIL for Python callbacks
- Callbacks are thread-safe by default
- No additional locking needed for Python objects
- But C-level shared state needs explicit synchronization

## Performance Considerations

### Minimizing Callback Overhead

```python
# SLOW: Many small callbacks
ffi.cdef("""
    typedef void (*item_callback)(void *item);
    void foreach_item(void **items, int count, item_callback cb);
""")

@ffi.callback("item_callback")
def process_one(item):
    # Python overhead for each call
    data = ffi.cast("int *", item)
    results.append(data[0])

# BETTER: Batch processing
ffi.cdef("""
    void process_batch(int *items, int count);
""")

lib.process_batch(array, count)  # Single call, C loops internally
```

### Callback Caching

```python
class CachedCallbacks:
    def __init__(self):
        self._callbacks = {}
        
    def get_callback(self, callback_type, func):
        # Reuse callbacks when possible
        key = (callback_type, id(func))
        if key not in self._callbacks:
            @ffi.callback(callback_type)
            def wrapper(*args):
                return func(*args)
            self._callbacks[key] = wrapper
        return self._callbacks[key]

cache = CachedCallbacks()
cb = cache.get_callback("int(int)", some_python_func)
```

## Common Callback Patterns

### Iterator Pattern

```python
ffi.cdef("""
    typedef int (*iterator_fn)(void *context, void *item);
    void iterate_collection(void *collection, iterator_fn fn, void *context);
""")

lib = ffi.dlopen("mylib.so")

collected = []

@ffi.callback("iterator_fn")
def collect_item(context, item):
    data = ffi.cast("int *", item)
    collected.append(data[0])
    return 1  # Continue iteration

collection = lib.create_collection()
lib.iterate_collection(collection, collect_item, None)
lib.free_collection(collection)

print(collected)
```

### Event Handler Pattern

```python
ffi.cdef("""
    typedef void (*event_handler)(int event_type, void *event_data);
    void register_event_handler(event_handler handler);
    void unregister_event_handler(event_handler handler);
    void dispatch_event(int event_type, void *event_data);
""")

lib = ffi.dlopen("mylib.so")

# Keep reference to prevent GC
class EventHandler:
    def __init__(self):
        self._handler = self._create_handler()
        lib.register_event_handler(self._handler)
    
    @ffi.callback("event_handler")
    def _create_handler(self, event_type, event_data):
        if event_type == 1:
            print("Click event received")
        elif event_type == 2:
            data = ffi.cast("int *", event_data)
            print(f"Value changed to {data[0]}")
    
    def __del__(self):
        lib.unregister_event_handler(self._handler)

handler = EventHandler()
# C code can now dispatch events that Python handles
```

### Comparator Pattern (for sorting)

```python
ffi.cdef("""
    typedef int (*comparator)(const void *a, const void *b, void *user_data);
    void custom_sort(void *base, size_t nmemb, size_t size, 
                     comparator cmp, void *user_data);
""")

lib = ffi.dlopen("mylib.so")

# Case-insensitive string sort
@ffi.callback("comparator")
def case_insensitive_compare(a, b, user_data):
    str_a = ffi.string(a).decode('utf-8').lower()
    str_b = ffi.string(b).decode('utf-8').lower()
    
    if str_a < str_b:
        return -1
    elif str_a > str_b:
        return 1
    return 0

strings = ["Banana", "apple", "Cherry", "banana"]
string_ptrs = ffi.new("char *[]", 
                      [ffi.new("char[]", s.encode()) for s in strings])

lib.custom_sort(string_ptrs, len(strings), ffi.sizeof("char *"), 
                case_insensitive_compare, None)

sorted_strings = [ffi.string(string_ptrs[i]).decode() for i in range(len(strings))]
print(sorted_strings)  # ['apple', 'Banana', 'banana', 'Cherry']
```

## Troubleshooting Callbacks

### Common Issues

**"Callback type not declared"**
```python
# WRONG: Type not in cdef
@ffi.callback("int(int, int)")  # Works but not ideal
def add(x, y): return x + y

# RIGHT: Declare type first
ffi.cdef("typedef int (*add_fn)(int, int);")
@ffi.callback("add_fn")
def add(x, y): return x + y
```

**Callback Called After Garbage Collection**
```python
# WRONG
def register_temp_callback():
    @ffi.callback("void()")
    def temp(): print("called")
    lib.register(temp)
    # temp might be GC'd!

# RIGHT
class CallbackManager:
    def __init__(self):
        self.callbacks = []
    
    def register_persistent(self, callback_type, func):
        @ffi.callback(callback_type)
        def wrapper(*args): return func(*args)
        self.callbacks.append(wrapper)  # Keep alive!
        lib.register(wrapper)
```

**Wrong Argument Types**
```python
# WRONG: Mismatched types
ffi.cdef("typedef void (*cb)(int);")

@ffi.callback("cb")
def handler(x):  # x is actually a pointer, not int!
    return x * 2  # Wrong!

# RIGHT: Check actual types
ffi.cdef("typedef void (*cb)(int *);")

@ffi.callback("cb")
def handler(x):  # x is int *
    return x[0] * 2  # Correct!
```

## References

- [CFFI Documentation - Callbacks](https://cffi.readthedocs.io/en/stable/using.html#callbacks-old-style)
- [CFFI Documentation - Extern Python](https://cffi.readthedocs.io/en/stable/using.html#extern-python-new-style-callbacks)
- [CFFI Embedding Guide](https://cffi.readthedocs.io/en/stable/embedding.html)
