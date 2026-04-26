# JIT Classes

## Overview

`@jitclass` (from `numba.experimental`) compiles Python classes with typed fields. All methods are compiled into nopython functions. Instance data is allocated on the heap as a C-compatible structure for direct access by compiled code, bypassing the interpreter.

## Basic Usage

Provide a specification of field names and Numba types:

```python
import numpy as np
from numba import int32, float32
from numba.experimental import jitclass

spec = [
    ('value', int32),
    ('array', float32[:]),
]

@jitclass(spec)
class Bag:
    def __init__(self, value):
        self.value = value
        self.array = np.zeros(value, dtype=np.float32)

    @property
    def size(self):
        return self.array.size

    def increment(self, val):
        for i in range(self.size):
            self.array[i] += val
        return self.array

    @staticmethod
    def add(x, y):
        return x + y

mybag = Bag(21)
```

The spec can be a list of 2-tuples or a dictionary (OrderedDict preferred for stable ordering). The class requires at least `__init__` to initialize all fields — uninitialized fields contain garbage data.

## Type Inference from Annotations

Fields can be inferred from Python type annotations using `as_numba_type`:

```python
from numba.experimental import jitclass

@jitclass
class Counter:
    value: int

    def __init__(self):
        self.value = 0

    def get(self) -> int:
        ret = self.value
        self.value += 1
        return ret
```

Annotations extend the spec for fields not already present. NumPy arrays must still be in the spec explicitly since dtype and rank cannot be expressed with type annotations alone.

## Typed Containers as Class Members

Specify `numba.typed.Dict` or `numba.typed.List` explicitly:

```python
from numba import types, typed
from numba.experimental import jitclass

@jitclass([('d', types.DictType(types.int64, types.unicode_type)),
           ('l', types.ListType(types.float64))])
class ContainerHolder:
    def __init__(self):
        self.d = typed.Dict.empty(types.int64, types.unicode_type)
        self.l = typed.List.empty_list(types.float64)

container = ContainerHolder()
container.d[1] = "apple"
container.l.append(123.0)
```

Use `numba.typeof(container_instance)` to obtain the Numba type from an existing container:

```python
from numba import typeof, typed
from numba.experimental import jitclass

d = typed.Dict()
d[1] = "apple"

@jitclass([('d', typeof(d))])
class Holder:
    def __init__(self, dict_inst):
        self.d = dict_inst
```

**Warning**: Container fields must be initialized before use. Writing to an uninitialized container causes a segmentation fault.

## Supported Operations

- Construction: `mybag = Bag(123)`
- Attribute read/write: `mybag.value`
- Method calls: `mybag.increment(3)`
- Static method calls as instance attributes: `mybag.add(1, 1)`
- Static method calls as class attributes (outside class definition): `Bag.add(1, 2)`
- Dunder methods: `mybag + otherbag`

## Supported Dunder Methods

The following dunder methods may be defined for jitclasses:

Unary: `__abs__`, `__bool__`, `__complex__`, `__float__`, `__hash__`, `__index__`, `__invert__`, `__int__`, `__len__`, `__neg__`, `__pos__`, `__str__`

Comparison: `__eq__`, `__ne__`, `__ge__`, `__gt__`, `__le__`, `__lt__`, `__contains__`

Arithmetic: `__add__`, `__sub__`, `__mul__`, `__matmul__`, `__floordiv__`, `__truediv__`, `__mod__`, `__pow__`, `__lshift__`, `__rshift__`, `__and__`, `__or__`, `__xor__`

In-place: `__iadd__` (and other in-place operators)

Indexing: `__getitem__`, `__setitem__`

## Limitations

- This is an early feature — not all compilation features are exposed
- No inheritance support
- Properties support getters and setters only
- Using jitclasses from the interpreter has boxing/unboxing overhead
- Using jitclasses within Numba compiled functions is more efficient (methods can be inlined)
