# Wrapping C++ Libraries

## Basic Pattern

### Step 1: Declare C++ Classes in .pxd

```python
# mycpp.pxd
cdef extern from "MyClass.h" namespace "myns":
    # Class with default constructor
    cdef cppclass MyClass:
        MyClass() except +
        MyClass(int value) except +
        ~MyClass()
        
        int get_value()
        void set_value(int v)
        double compute()
    
    # Class with methods returning references
    cdef cppclass Container:
        Container()
        void add_item(int item)
        int& get_item(size_t index)  # Reference return
        size_t size()
    
    # Static methods
    cdef extern from "Utils.h" namespace "myns":
        int global_function(int x)
```

**Key points:**
- `except +` means constructor can throw C++ exceptions
- `~MyClass()` declares destructor
- Use `namespace` to match C++ namespaces
- Reference returns use `&` syntax

### Step 2: Create Python Wrapper in .pyx

```python
# mycpp.pyx
from mycpp cimport MyClass, Container

# distutils: language = c++

def create_and_use():
    """Create C++ object and call methods"""
    cdef MyClass obj = MyClass(42)
    
    value = obj.get_value()
    obj.set_value(100)
    result = obj.compute()
    
    return result

def use_container():
    """Use C++ container class"""
    cdef Container cont
    
    cont.add_item(1)
    cont.add_item(2)
    cont.add_item(3)
    
    # Access items via reference
    cont.get_item(0) += 10
    
    return cont.size()
```

### Step 3: Build with C++ Compiler

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "mycpp",
    ["mycpp.pyx", "MyClass.cpp"],  # Include C++ source
    language="c++",
    extra_compile_args=["-std=c++17"],
    include_dirs=["./include"]
)

setup(ext_modules=cythonize([ext]))
```

## Object Management

### Stack vs Heap Allocation

**Stack allocation (automatic cleanup):**
```python
def stack_example():
    cdef MyClass obj  # Allocated on stack
    
    # Use obj...
    
    # Destructor called automatically when function returns
```

**Heap allocation (manual cleanup):**
```python
def heap_example():
    cdef MyClass *obj = new MyClass(42)  # Heap allocated
    
    try:
        # Use obj...
        value = obj.get_value()
    finally:
        del obj  # Must manually delete!
    
    return value
```

**Recommended: Use Cython's smart pointers or wrapper classes:**
```python
cdef class ManagedCppObject:
    cdef MyClass *ptr
    
    def __init__(self, int value):
        self.ptr = new MyClass(value)
    
    def __del__(self):
        del self.ptr  # Automatic cleanup
    
    def get_value(self):
        return self.ptr.get_value()
    
    def set_value(self, int v):
        self.ptr.set_value(v)
```

## Exception Handling

### C++ Exceptions to Python

```python
cdef extern from "myclass.h":
    cdef cppclass SafeClass:
        SafeClass() except +  # Can throw
        void risky_operation() except +  # Can throw
        int safe_operation() noexcept  # Won't throw

def use_safe_class():
    cdef SafeClass obj
    
    try:
        obj.risky_operation()  # C++ exceptions caught and converted
    except Exception as e:
        print(f"Caught: {e}")
    
    obj.safe_operation()  # No exception handling needed
```

### Custom Exception Mapping

```python
cdef extern from "errors.h":
    cdef cppclass MyException:
        const char *what()
    
    cdef cppclass Calculator:
        Calculator()
        int divide(int a, int b) except "+MyException"  # Specific exception

def safe_divide(int a, int b):
    cdef Calculator calc
    
    try:
        return calc.divide(a, b)
    except ValueError as e:
        # MyException converted to Python ValueError
        raise
```

## STL Containers

### Using std::vector

```python
from libcpp.vector cimport vector

cdef class VectorWrapper:
    cdef vector[int] data
    
    def __init__(self):
        self.data.reserve(100)  # Pre-allocate
    
    def append(self, int value):
        self.data.push_back(value)
    
    def __getitem__(self, size_t index):
        return self.data[index]
    
    def __len__(self):
        return self.data.size()
    
    def clear(self):
        self.data.clear()
```

### Using std::string

```python
from libcpp.string cimport string
from cpython.str cimport PyUnicode_FromString

cdef class StringWrapper:
    cdef string internal
    
    def __init__(self, unicode text=""):
        if text:
            self.internal = text.encode('utf-8')
    
    def append(self, unicode text):
        self.internal += text.encode('utf-8')
    
    def __str__(self):
        return PyUnicode_FromString(self.internal.c_str()).decode('utf-8')
    
    def length(self):
        return self.internal.length()
```

### Using std::map

```python
from libcpp.map cimport map

cdef class MapWrapper:
    cdef map[unicode, int] data
    
    def set_value(self, unicode key, int value):
        self.data[key.encode('utf-8')] = value
    
    def get_value(self, unicode key, int default):
        cdef auto_it iterator = self.data.find(key.encode('utf-8'))
        
        if iterator != self.data.end():
            return iterator.second
        return default
    
    def contains(self, unicode key):
        return key.encode('utf-8') in self.data
```

## Templates and Generics

### Declaring Templated Classes

```python
cdef extern from "Container.h" namespace "templ":
    template<typename T>
    cdef cppclass Box:
        Box()
        Box(T value)
        T get()
        void set(T value)
    
    template<typename T>
    T box_sum(Box[T] a, Box[T] b)

# Instantiate specific types
ctypedef Box[int] IntBox
ctypedef Box[double] DoubleBox

def use_templates():
    cdef IntBox int_box = IntBox(42)
    cdef DoubleBox double_box = DoubleBox(3.14)
    
    return int_box.get(), double_box.get()
```

### Fused Types for Multiple Specializations

```python
ctypedef fused number_types:
    int
    float
    double

cdef extern from "Math.h":
    template<typename T>
    T square(T x)

cpdef number_types squared(number_types x):
    """Generates specialized versions for each type"""
    return square(x)
```

## Common Patterns

### Smart Pointers

```python
from libcpp.memory cimport unique_ptr, make_unique

cdef extern from "Resource.h":
    cdef cppclass Resource:
        Resource()
        ~Resource()
        void use()

def use_unique_ptr():
    cdef unique_ptr[Resource] ptr = make_unique[Resource]()
    
    # Use resource
    ptr.use()
    
    # Automatically deleted when ptr goes out of scope
```

### Factory Pattern Wrapper

```python
cdef extern from "Factory.h":
    cdef cppclass Shape:
        Shape()
        virtual double area()
    
    cdef cppclass Circle:
        Circle(double radius)
        double area()
    
    cdef cppclass* create_shape(string type, double param)

cdef class PythonShape:
    cdef Shape* shape
    
    def __init__(self, string type, double param):
        self.shape = create_shape(type.encode('utf-8'), param)
    
    def __del__(self):
        del self.shape
    
    def get_area(self):
        return self.shape.area()
```

### Iterator Pattern

```python
from libcpp cimport ref

cdef extern from "Iterator.h":
    cdef cppclass Container:
        Container()
        void add(int value)
        
        cdef cppclass Iterator:
            int deref()
            bint increment()
            bint done()
        
        Iterator begin()
        Iterator end()

class PythonContainer:
    def __init__(self):
        self._container = Container()
    
    def add(self, int value):
        self._container.add(value)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        cdef Container.Iterator it = self._container.begin()
        
        if not hasattr(self, '_current_iter'):
            self._current_iter = it
            self._at_end = False
        
        if self._at_end:
            raise StopIteration
        
        if self._current_iter.done():
            self._at_end = True
            raise StopIteration
        
        result = self._current_iter.deref()
        self._current_iter.increment()
        
        return result
```

## Performance Tips

### Avoid Unnecessary Copies

```python
# Bad - copies the object
cdef extern from "Large.h":
    cdef cppclass LargeObject:
        LargeObject()
        LargeObject(LargeObject& other)  # Copy constructor

def bad_pass(LargeObject obj):  # Copy on entry and exit
    process(obj)

# Good - pass by reference
def good_pass(LargeObject& obj):  # No copy
    process(obj)

# Better - use const reference for read-only
cdef void process(const LargeObject& obj) nogil:
    # Process without modification, no GIL needed
```

### Release GIL for C++ Operations

```python
cdef extern from "Compute.h":
    cdef cppclass CPUIntensive:
        CPUIntensive()
        void compute() noexcept  # Marked as not throwing

def parallel_cpp():
    cdef CPUIntensive worker
    
    with nogil:  # Safe because compute() is noexcept
        worker.compute()
```

## Debugging C++ Interop

### Check for NULL Pointers

```python
def safe_useCppObject():
    cdef MyClass* obj = create_object()
    
    if obj == NULL:
        raise RuntimeError("Failed to create object")
    
    try:
        return obj.get_value()
    finally:
        del obj
```

### Add Assertions

```python
from libcpp cimport assert as cpp_assert

def validated_operation(Container cont, size_t index):
    cpp_assert(index < cont.size())
    return cont.get_item(index)
```

See [SKILL.md](../SKILL.md) for overview and [C Libraries](07-c-libraries.md) for C wrapping basics.
