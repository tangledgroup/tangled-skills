# Fused Types

## Overview

Fused types enable generic programming in Cython — one function definition that specializes for multiple types at compile time. Similar to C++ templates or Java generics.

**Limitation:** Fused types cannot be used as attributes of extension types. Only variables and function/method arguments support fused types.

## Declaring Fused Types

```cython
# Cython syntax
ctypedef fused char_or_float:
    char
    float

ctypedef fused my_numeric:
    int
    double
    long long
```

```python
# Pure Python mode
import cython

char_or_float = cython.fused_type(cython.char, cython.float)
my_numeric = cython.fused_type(cython.int, cython.double, cython.longlong)
```

Only type names (not fused types themselves) can be constituents. Type aliases work:

```cython
ctypedef double my_double
ctypedef fused my_fused:
    int
    my_double
```

## Using Fused Types in Functions

```cython
cdef void plus_one(my_numeric x):
    print(x + 1)

# Specializes as char when called with char
plus_one(-128)   # calls char specialization

# Specializes as float when called with float
plus_one(128.0)  # calls float specialization
```

When the same fused type appears multiple times in parameters, all occurrences share the same specialization:

```cython
cdef my_numeric add(my_numeric a, my_numeric b):
    # a and b always have the same specialized type
    return a + b
```

Different fused type names specialize independently:

```cython
ctypedef fused A:
    int
    double

ctypedef fused B:
    int
    double

cdef void func(A a, B b):
    # a and b may have different specializations
    print("SAME!" if A is B else "NOT SAME!")
```

This generates all combinations: (int, int), (int, double), (double, int), (double, double).

## Fused Types with Memoryviews

Fused types are especially useful with memoryviews and pointers:

```cython
ctypedef fused numeric_t:
    int
    double

cdef void process(numeric_t[:,:] arr):
    cdef numeric_t total = 0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            total += arr[i, j]
```

All memoryviews of the same fused type share the specialization. To get independent specializations, use differently named fused types.

## Selecting Specializations

**Indexing — explicit type selection:**

```cython
cdef my_numeric add(my_numeric a, my_numeric b):
    return a + b

# Call specific specialization
result = add[double](1.0, 2.0)
result = add[int](1, 2)
```

From Python:

```python
import cython
import mymodule

mymodule.add[cython.double](1.0, 2.0)
mymodule.add[cython.int](1, 2)
```

**Calling — automatic dispatch:**

```cython
cdef double d = 1.0
cdef int i = 2

add(d, d)   # automatically calls double specialization
add(i, i)   # automatically calls int specialization
add(d, i)   # calls double specialization (first arg determines)
```

## Fused Types with Pointers

```cython
ctypedef fused T:
    int
    double

cdef void func(T *ptr):
    print(ptr[0])

# Specialize using component type, not pointer type
func[int](int_ptr)
func[double](double_ptr)
```

## Runtime Type Checking

Inside a fused function, check which specialization is active:

```cython
cdef void process(numeric_t[:] arr):
    if numeric_t is int:
        # integer-specific code path
        pass
    elif numeric_t is double:
        # floating-point specific code path
        pass
```

This enables type-specific optimizations within a single function body.

## Fused Types and NumPy

Common pattern — map fused types to NumPy dtypes:

```cython
ctypedef fused my_type:
    int
    double
    long long

def compute(my_type[:,::1] arr):
    if my_type is int:
        dtype = np.intc
    elif my_type is double:
        dtype = np.double
    elif my_type is cython.longlong:
        dtype = np.longlong

    result = np.zeros(arr.shape, dtype=dtype)
    cdef my_type[:,::1] result_view = result
    # ... operate on result_view ...
    return result
```
