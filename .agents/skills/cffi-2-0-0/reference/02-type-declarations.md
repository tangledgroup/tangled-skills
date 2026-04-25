# CFFI Type Declarations - Complete Guide

## Overview

CFFI uses C-like type declarations to describe the interface between Python and C. This guide covers all supported types, declaration syntax, and best practices for declaring C interfaces in CFFI.

## Basic Syntax

All type declarations go into `ffi.cdef()` or `ffibuilder.cdef()`:

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    // C-style comments work
    /* Block comments too */
    
    int add(int x, int y);
    void print_message(const char *msg);
""")
```

## Primitive Types

### Integer Types

```python
ffi.cdef("""
    char small;           # 8-bit
    short medium;         # 16-bit
    int standard;         # Usually 32-bit
    long large;           # 32 or 64-bit depending on platform
    long long huge;       # At least 64-bit
    
    unsigned char uchar;
    unsigned int uint;
    unsigned long ulong;
""")

# Fixed-width types (from stdint.h)
ffi.cdef("""
    int8_t i8;
    int16_t i16;
    int32_t i32;
    int64_t i64;
    uint8_t u8;
    uint32_t u32;
    uintptr_t ptr_int;
    size_t size;
    ssize_t signed_size;
    ptrdiff_t ptr_diff;
""")
```

### Floating-Point Types

```python
ffi.cdef("""
    float f32;            # 32-bit float
    double f64;           # 64-bit double
    long double extended; # Extended precision (platform-dependent)
""")

# Usage
from cffi import FFI
ffi = FFI()
ffi.cdef("double sqrt(double x);")
lib = ffi.dlopen(None)  # C library
result = lib.sqrt(2.0)  # Returns Python float
```

### Boolean and Void

```python
ffi.cdef("""
    _Bool boolean;        # C99 boolean (0 or 1)
    void *void_ptr;       # Generic pointer
    void noop(void);      # Function returning void
""")
```

## Pointers

### Basic Pointers

```python
ffi.cdef("""
    int *int_ptr;
    char *char_ptr;
    void *void_ptr;
    const int *const_ptr;  # Pointer to const int
    int *const ptr_const;  # Const pointer to int
""")

# Creating pointers in Python
from cffi import FFI
ffi = FFI()
ffi.cdef("int *get_pointer(void);")

lib = ffi.dlopen("mylib.so")

# Get a pointer from C
ptr = lib.get_pointer()

# Access the value
value = ptr[0]  # Dereference like array access

# Modify through pointer
ptr[0] = 42
```

### NULL Pointer

```python
ffi.cdef("char *get_path(int id);")
lib = ffi.dlopen("mylib.so")

path = lib.get_path(-1)
if path == ffi.NULL:
    print("Path not found")
else:
    print(ffi.string(path).decode())
```

### Pointer Arithmetic

```python
ffi.cdef("int *create_array(int n);")
lib = ffi.dlopen("mylib.so")

arr = lib.create_array(10)
arr[0] = 100
arr[5] = 200

# Pointer arithmetic works
ptr = arr + 3  # Points to arr[3]
ptr[0] = 300   # Sets arr[3]
```

## Arrays

### Fixed-Size Arrays

```python
ffi.cdef("""
    int fixed_array[10];
    char buffer[256];
    
    void process_array(int arr[10]);
    void process_buffer(char buf[256]);
""")

# Note: In function parameters, array syntax becomes pointer syntax
# int arr[10] in parameter is same as int *arr
```

### Variable-Length Arrays (via pointers)

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("void process(int *arr, int length);")

lib = ffi.dlopen("mylib.so")

# Create array in Python
arr = ffi.new("int[]", [1, 2, 3, 4, 5])
lib.process(arr, 5)

# Or with initial value
arr2 = ffi.new("int[10]", 0)  # 10 zeros
```

### Multi-Dimensional Arrays

```python
ffi.cdef("void matrix_multiply(double a[10][10], double b[10][10], double result[10][10]);")

# Create 2D array
from cffi import FFI
ffi = FFI()
matrix = ffi.new("double[10][10]")

# Access elements
matrix[0][0] = 1.0
matrix[5][3] = 2.5
```

## Structures

### Basic Structs

```python
ffi.cdef("""
    struct point {
        int x;
        int y;
    };
    
    struct rectangle {
        struct point top_left;
        struct point bottom_right;
    };
""")

# Usage
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    struct point {
        int x;
        int y;
    };
    struct point create_point(int x, int y);
""")

lib = ffi.dlopen("mylib.so")

# Create struct
p = ffi.new("struct point *")
p.x = 10
p.y = 20

# Or use C function
p2 = lib.create_point(5, 15)
print(f"Point: ({p2.x}, {p2.y})")
```

### Struct with Unknown Fields (API mode only)

```python
ffibuilder.cdef("""
    struct passwd {
        char *pw_name;
        char *pw_passwd;
        int pw_uid;
        int pw_gid;
        char *pw_gecos;
        char *pw_dir;
        char *pw_shell;
        // ... skip the rest
        ...;
    };
    struct passwd *getpwuid(int uid);
""")

ffibuilder.set_source("_passwd", """
    #include <pwd.h>  // Compiler fills in missing fields
""")
```

### Anonymous Structs and Unions

```python
ffi.cdef("""
    struct event {
        int type;
        union {
            int key_code;
            struct {
                int x;
                int y;
            } mouse_pos;
        } data;
    };
""")

# Access union fields
event = ffi.new("struct event *")
event.type = 1
event.data.key_code = 65  # Or event.data.mouse_pos.x = 100
```

### Struct Size and Offsets

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    struct mystuct {
        int a;
        double b;
        char c;
        long d;
    };
""")

print(f"Size: {ffi.sizeof('struct mystuct')}")
print(f"Offset of a: {ffi.offsetof('struct mystuct', 'a')}")
print(f"Offset of b: {ffi.offsetof('struct mystuct', 'b')}")
print(f"Size of b: {ffi.sizeof(ffi.typeof('struct mystuct').fields['b'])}")
```

## Unions

```python
ffi.cdef("""
    union value {
        int integer;
        float floating;
        char bytes[4];
    };
    
    union value create_value(int x);
""")

# Usage
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    union value {
        int i;
        float f;
    };
""")

v = ffi.new("union value *")
v.i = 42
print(f"As int: {v.i}")
print(f"As float: {v.f}")  # Same bits, interpreted as float
```

## Enums

```python
ffi.cdef("""
    enum color {
        RED = 1,
        GREEN = 2,
        BLUE = 3
    };
    
    enum {
        UNNAMED_RED = 10,
        UNNAMED_GREEN = 20
    };
    
    void set_color(enum color c);
""")

# Usage
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    enum color { RED, GREEN, BLUE };
    void set_color(enum color c);
""")

lib = ffi.dlopen("mylib.so")
lib.set_color(0)  # RED = 0
lib.set_color(1)  # GREEN = 1

# Or use constants if declared
ffi.cdef("""
    enum { MAX_SIZE = 1024 };
""")
lib.set_limit(ffi.C.MAX_SIZE)
```

## Typedefs

```python
ffi.cdef("""
    typedef int my_int;
    typedef struct point {
        int x, y;
    } Point;
    
    typedef void (*callback_fn)(int, void *);
    typedef struct my_struct *my_struct_ptr;
""")

# Usage with typedefs
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    typedef struct {
        int x, y;
    } Point;
    
    Point create_point(int x, int y);
""")

lib = ffi.dlopen("mylib.so")
p = lib.create_point(10, 20)
print(f"Point: ({p.x}, {p.y})")
```

## Function Pointers

### Declaring Function Pointers

```python
ffi.cdef("""
    // Basic function pointer type
    typedef int (*compare_fn)(const void *, const void *);
    
    // Function taking function pointer
    void qsort(void *base, size_t nmemb, size_t sizeof_elem, compare_fn cmp);
    
    // Callback that returns function pointer
    typedef int (*binary_op)(int, int);
    binary_op get_operation(int op_type);
""")

### Using Function Pointers with Callbacks

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    typedef int (*compare_fn)(const void *, const void *);
    void qsort(void *base, size_t nmemb, size_t sizeof_elem, compare_fn cmp);
""")

lib = ffi.dlopen(None)  # C library

# Create callback
@ffi.callback("compare_fn")
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

# Use with qsort
arr = ffi.new("int[]", [5, 2, 8, 1, 9])
lib.qsort(arr, 5, ffi.sizeof("int"), compare_ints)

print([arr[i] for i in range(5)])  # [1, 2, 5, 8, 9]
```

## Const Qualifiers

```python
ffi.cdef("""
    const int *get_constant_array(void);
    char *get_mutable_string(void);
    const char *get_readonly_string(void);
    
    void print_const(const char *str);
    void modify(char *str);
""")

# Const correctness is checked at compile time in API mode
# In ABI mode, const is mostly informational
```

## Void and Generic Pointers

### Using void*

```python
ffi.cdef("""
    void *malloc(size_t size);
    void free(void *ptr);
    void *memcpy(void *dest, const void *src, size_t n);
""")

from cffi import FFI
ffi = FFI()
ffi.cdef("void *malloc(size_t size);")

lib = ffi.dlopen(None)

# Allocate memory
ptr = lib.malloc(ffi.sizeof("int") * 10)

# Cast to specific type
int_ptr = ffi.cast("int *", ptr)
int_ptr[0] = 42

# Use as buffer
buf = ffi.buffer(ptr, ffi.sizeof("int") * 10)
```

### Casting Between Types

```python
from cffi import FFI
ffi = FFI()

# Cast pointer types
void_ptr = ffi.new("void **")
int_ptr = ffi.cast("int *", void_ptr)

# Cast values
x = ffi.cast("double", 42)  # int to double
y = ffi.cast("int", 3.14)   # float to int

# Cast function pointers
ffi.cdef("""
    typedef int (*fn1)(int);
    typedef int (*fn2)(int, int);
""")
# Be careful - CFFI won't check compatibility
```

## Complex and Float Types

```python
ffi.cdef("""
    #ifdef __GNUC__
    __complex float complex_float;
    __complex double complex_double;
    #endif
    
    _Complex float cfloat;
    _Complex double cdouble;
""")

# Note: Complex number support depends on compiler and platform
```

## Bit Fields (Limited Support)

```python
ffi.cdef("""
    struct flags {
        int flag1: 1;  # Single bit
        int flag2: 1;
        int reserved: 30;
    };
""")

# Warning: Bit field layout is compiler-dependent
# Use with caution, preferably in API mode only
```

## Declaration Limitations

### What's NOT Supported

```python
# NO preprocessor directives
ffi.cdef("""
    #ifdef FOO     # WRONG!
    int bar();
    #endif
""")

# NO includes
ffi.cdef("""
    #include <stdio.h>  # WRONG!
""")

# NO function bodies (except in ffi.verify() or set_source())
ffi.cdef("""
    int add(int x, int y) {  # WRONG!
        return x + y;
    }
""")

# NO macro definitions
ffi.cdef("""
    #define MAX_SIZE 100  # WRONG!
""")
```

### Workarounds for Limitations

**For platform-specific declarations:**
```python
import sys
if sys.platform == "win32":
    ffi.cdef("int __stdcall windows_func(int x);")
else:
    ffi.cdef("int unix_func(int x);")
```

**For macros:**
```python
# Instead of #define, declare as constant
ffi.cdef("""
    enum {
        MAX_SIZE = 100,
        MIN_SIZE = 10
    };
""")

# Or use ffi.constants
lib = ffi.dlopen("mylib.so")
value = lib.MAX_SIZE  # If exported from library
```

**For complex headers:**
```python
# Use API mode with set_source()
ffibuilder.set_source("_mymodule", """
    #include "complex_header.h"
    
    // Additional C code if needed
    static int helper_function(int x) {
        return x * 2;
    }
""")
```

## Type Inspection

### Runtime Type Information

```python
from cffi import FFI
ffi = FFI()
ffi.cdef("""
    struct point {
        int x;
        int y;
    };
    
    typedef struct point Point;
""")

# Get type object
point_type = ffi.typeof("struct point")
print(point_type)  # <cdata 'struct point'>

# Check size and alignment
print(ffi.sizeof("struct point"))      # Size in bytes
print(ffi.alignof("struct point"))     # Alignment requirement

# Get field information
for field_name in point_type.fields:
    field = point_type.fields[field_name]
    print(f"Field {field_name}: {field.type}")

# Check type compatibility
t1 = ffi.typeof("int *")
t2 = ffi.typeof("struct point *")
print(t1 == t2)  # False

# Get type of expression
p = ffi.new("struct point *")
print(ffi.typeof(p))      # struct point *
print(ffi.typeof(p.x))    # int
```

## Best Practices

1. **Copy from headers when possible**: CFFI declarations often match C headers exactly
2. **Use `...` for unknown struct fields** (API mode only)
3. **Be explicit with const qualifiers**: Helps catch bugs
4. **Use typedefs for complex types**: Improves readability
5. **Validate with API mode**: Compile-time checking catches errors early
6. **Document platform differences**: Some types vary by platform (long, pointers)
7. **Keep declarations minimal**: Only declare what you actually use

## References

- [CFFI Documentation - Using the ffi/lib objects](https://cffi.readthedocs.io/en/stable/using.html)
- [CFFI Reference](https://cffi.readthedocs.io/en/stable/ref.html)
- [C Type System](https://en.cppreference.com/w/c/language/type)
