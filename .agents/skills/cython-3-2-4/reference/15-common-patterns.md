# Common Patterns

### Wrapping C Libraries

See [C Library Wrapping](reference/07-c-libraries.md) for complete guide.

Basic pattern:
```python
# mylib.pxd
cdef extern from "mylib.h":
    int c_function(int x, float y)
    void c_void_function(char *str)

# mylib.pyx
from mylib cimport c_function

def python_wrapper(int x, float y):
    return c_function(x, y)
```

### Wrapping C++ Libraries

See [C++ Library Wrapping](reference/08-cpp-libraries.md) for complete guide.

Basic pattern:
```python
# mylib.pxd
cdef extern from "MyClass.h" namespace "myns":
    cdef cppclass MyClass:
        MyClass() except +
        int get_value()
        void set_value(int v)

# mylib.pyx
from mylib cimport MyClass

def use_cpp():
    cdef MyClass obj
    obj.set_value(42)
    return obj.get_value()
```

### NumPy Integration

See [NumPy Tutorial](reference/09-numpy.md) for complete guide.

Basic pattern:
```python
# distutils: language = c
import numpy as np
cimport numpy as np

def process_array(np.ndarray[double, ndim=1] arr):
    cdef int i
    cdef double total = 0.0
    
    for i in range(arr.shape[0]):
        total += arr[i]
    
    return total
```
