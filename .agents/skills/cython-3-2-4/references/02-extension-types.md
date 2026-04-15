# Extension Types (cdef class)

## Introduction

Extension types are Python types implemented in C for performance. They store data in C structures rather than Python dictionaries, providing:

- **Faster attribute access** - Direct C struct access vs dictionary lookup
- **Lower memory usage** - No per-instance `__dict__` overhead
- **Type safety** - Compile-time checking of attribute types
- **Python compatibility** - Can be subclassed and used like regular Python classes

## Basic Extension Type

```python
cdef class Point:
    """A 2D point with C-level coordinates"""
    
    # Private C attributes (not accessible from Python)
    cdef double x
    cdef double y
    
    # Public attributes (accessible from Python)
    cdef public string label
    
    def __init__(self, double x, double y, string label=""):
        self.x = x
        self.y = y
        self.label = label
    
    def distance_to_origin(self) -> double:
        """Calculate distance from origin"""
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    cdef double _fast_distance(self, Point other):
        """Internal C method for fast distance calculation"""
        cdef double dx = self.x - other.x
        cdef double dy = self.y - other.y
        return (dx ** 2 + dy ** 2) ** 0.5
    
    def distance_to(self, Point other) -> double:
        """Public method using fast internal calculation"""
        return self._fast_distance(other)
```

**Usage from Python:**
```python
p1 = Point(3.0, 4.0, "A")
p2 = Point(6.0, 8.0, "B")

print(p1.distance_to_origin())  # 5.0
print(p1.label)                  # "A"
# print(p1.x)                    # AttributeError! (not public)
```

## Attribute Access Control

### Private Attributes (cdef only)

Not accessible from Python:

```python
cdef class SecureData:
    cdef int secret_value  # Private
    
    def __init__(self, int value):
        self.secret_value = value
    
    def get_encrypted(self) -> string:
        return f"encrypted:{self.secret_value}"
```

```python
data = SecureData(42)
# data.secret_value  # AttributeError!
print(data.get_encrypted())  # "encrypted:42"
```

### Public Attributes (Read/Write)

Accessible from Python:

```python
cdef class Person:
    cdef public string name
    cdef public int age
    
    def __init__(self, string name, int age):
        self.name = name
        self.age = age
```

```python
person = Person("Alice", 30)
print(person.name)   # "Alice"
person.age = 31      # Can modify
```

### Readonly Attributes (Read-Only)

Readable but not writable from Python:

```python
cdef class Circle:
    cdef readonly double radius
    cdef readonly double area
    
    def __init__(self, double radius):
        self.radius = radius
        self.area = 3.14159 * radius * radius
```

```python
circle = Circle(5.0)
print(circle.radius)  # 5.0
# circle.radius = 10  # AttributeError! (readonly)
```

## Inheritance

### Extending Extension Types

```python
cdef class Animal:
    cdef public string name
    
    def __init__(self, string name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError

cdef class Dog(Animal):
    cdef public string breed
    
    def __init__(self, string name, string breed):
        super(Dog, self).__init__(name)
        self.breed = breed
    
    def speak(self):
        return f"{self.name} says Woof!"
```

### Extension Types with Python Subclasses

Extension types can be subclassed by regular Python classes:

```python
cdef class BaseCounter:
    cdef int count
    
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
    
    def get_count(self) -> int:
        return self.count

# Python subclass (loses some performance benefits)
class NamedCounter(BaseCounter):
    def __init__(self, string name):
        super().__init__()
        self.name = name  # Dynamic attribute (allowed in Python subclass)
```

## Special Methods

### Object Creation and Initialization

```python
cdef class Resource:
    cdef int id
    cdef object *handle
    
    def __cinit__(self, int id):
        """Always called, even if __init__ raises exception"""
        self.id = id
        self.handle = NULL
        print(f"Creating resource {id}")
    
    def __init__(self, int id):
        """Can raise exceptions, __cinit__ already ran"""
        if id < 0:
            raise ValueError("ID must be non-negative")
        # Initialize Python-level state
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.handle != NULL:
            close_handle(self.handle)
            self.handle = NULL
        print(f"Destroying resource {self.id}")
```

**Important:** `__cinit__` cannot access `self` attributes before they're declared, and cannot raise Python exceptions safely.

### String Representation

```python
cdef class Vector:
    cdef double x, y, z
    
    def __str__(self) -> string:
        return f"Vector({self.x}, {self.y}, {self.z})"
    
    def __repr__(self) -> string:
        return f"Vector(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})"
    
    def __format__(self, format_spec):
        return f"Vector[{format_spec}]({self.x}, {self.y}, {self.z})"
```

### Comparison Methods

```python
cdef class Comparable:
    cdef int value
    
    def __init__(self, int value):
        self.value = value
    
    def __eq__(self, object other) -> bint:
        if not isinstance(other, Comparable):
            return False
        return self.value == other.value
    
    def __lt__(self, Comparable other) -> bint:
        return self.value < other.value
    
    def __le__(self, Comparable other) -> bint:
        return self.value <= other.value
    
    def __ne__(self, object other) -> bint:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.value)
```

### Container Protocols

```python
cdef class SimpleList:
    cdef object *_items
    cdef Py_ssize_t _size
    
    def __len__(self) -> Py_ssize_t:
        return self._size
    
    def __getitem__(self, Py_ssize_t index):
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        return self._items[index]
    
    def __setitem__(self, Py_ssize_t index, object value):
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        self._items[index] = value
    
    def __iter__(self):
        cdef Py_ssize_t i
        for i in range(self._size):
            yield self._items[i]
    
    def __contains__(self, object value) -> bint:
        cdef Py_ssize_t i
        for i in range(self._size):
            if self._items[i] == value:
                return True
        return False
```

### Context Managers

```python
cdef class FileLock:
    cdef string path
    cdef int fd
    
    def __init__(self, string path):
        self.path = path
        self.fd = -1
    
    def __enter__(self):
        self.fd = open_file(self.path)
        if self.fd < 0:
            raise IOError(f"Cannot open {self.path}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fd >= 0:
            close_file(self.fd)
            self.fd = -1
        return False  # Don't suppress exceptions
```

**Usage:**
```python
with FileLock("/tmp/lock") as lock:
    # File is locked here
    pass
# File is automatically unlocked
```

## Dynamic Attributes

By default, extension types don't support arbitrary attributes. Enable with `__dict__`:

```python
cdef class FlexibleCounter:
    cdef int count
    cdef dict __dict__  # Enable dynamic attributes
    
    def __init__(self):
        self.count = 0

counter = FlexibleCounter()
counter.count = 5
counter.anything = "works!"  # Now allowed (stored in __dict__)
```

**Trade-offs:**
- ✅ Can add arbitrary attributes at runtime
- ❌ Slower attribute access (dictionary lookup)
- ❌ More memory usage per instance
- ❌ Some inheritance restrictions

## Weak References

Enable weak reference support:

```python
cdef class Observable:
    cdef dict __weakref__  # Enable weak references
    cdef list _observers
    
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        self._observers.append(observer)
```

**Usage:**
```python
import weakref

obj = Observable()
weak_obj = weakref.ref(obj)

del obj
print(weak_obj())  # None (object was destroyed)
```

## Pickling Support

### Automatic Pickling

Cython can auto-generate pickle support:

```python
# cython: auto_pickle=True

cdef class PicklableData:
    cdef public int value
    cdef public string name
    
    def __init__(self, int value, string name):
        self.value = value
        self.name = name
```

**Usage:**
```python
import pickle

data = PicklableData(42, "test")
pickled = pickle.dumps(data)
restored = pickle.loads(pickled)
print(restored.value)  # 42
```

### Manual Pickling

For more control:

```python
cdef class CustomPickle:
    cdef int data
    cdef object temp_cache  # Don't pickle this
    
    def __getstate__(self):
        """Called during pickling"""
        return {'data': self.data}
    
    def __setstate__(self, dict state):
        """Called during unpickling"""
        self.data = state['data']
        self.temp_cache = None  # Reinitialize
```

## Memory Views in Extension Types

```python
cdef class Matrix:
    cdef double[:, :] data
    cdef readonly int rows
    cdef readonly int cols
    
    def __init__(self, int rows, int cols):
        self.rows = rows
        self.cols = cols
        self.data = [[0.0] * cols for _ in range(rows)]
    
    cdef void _set_element(self, int i, int j, double value):
        self.data[i, j] = value
    
    def get_row(self, int i) -> double[:]:
        """Return memoryview of row"""
        return self.data[i, :]
```

## Common Patterns

### Singleton Pattern

```python
cdef class Singleton:
    cdef object _instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Initialize only once
        pass
```

### Factory Pattern

```python
cdef class Shape:
    cdef public string type
    
    def area(self) -> double:
        raise NotImplementedError

cdef class Circle(Shape):
    cdef double radius
    
    def __init__(self, double radius):
        self.type = "circle"
        self.radius = radius
    
    def area(self) -> double:
        return 3.14159 * self.radius ** 2

cdef class Rectangle(Shape):
    cdef double width, height
    
    def __init__(self, double width, double height):
        self.type = "rectangle"
        self.width = width
        self.height = height
    
    def area(self) -> double:
        return self.width * self.height

# Factory function
cpdef Shape create_shape(string type, **kwargs):
    if type == "circle":
        return Circle(kwargs['radius'])
    elif type == "rectangle":
        return Rectangle(kwargs['width'], kwargs['height'])
    else:
        raise ValueError(f"Unknown shape: {type}")
```

See [SKILL.md](../SKILL.md) for overview and [C Library Wrapping](07-c-libraries.md) for using extension types with C APIs.
