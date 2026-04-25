# Advanced Numba Features

## Stencil Computations

Stencils are ideal for finite difference operations, image processing, and PDE solvers.

### Basic Stencil

```python
from numba import stencil
import numpy as np

@stencil
def laplacian_kernel(a):
    """2D Laplacian operator."""
    return (a[0, 1] + a[0, -1] + a[1, 0] + a[-1, 0] - 4 * a[0, 0])

# Apply to array
array = np.random.rand(100, 100)
result = laplacian_kernel(array)
```

### Custom Neighborhood

Specify the stencil extent explicitly:

```python
@stencil(neighborhood=(( -2, 2), (-2, 2)))
def custom_stencil(a):
    """5x5 kernel with explicit neighborhood."""
    total = 0.0
    for i in range(-2, 3):
        for j in range(-2, 3):
            total += a[i, j]
    return total / 25.0  # Average over 5x5 window

# Moving average example
@stencil(neighborhood=((-29, 0),))
def moving_average_30(a):
    """30-day trailing moving average."""
    cumul = 0.0
    for i in range(-29, 1):
        cumul += a[i]
    return cumul / 30.0
```

### Border Handling

Control how borders are handled:

```python
from numba import stencil

# Constant border (default)
@stencil(func_or_mode="constant", cval=0.0)
def kernel_constant(a):
    return a[0, 1] + a[0, -1] + a[1, 0] + a[-1, 0]

# Border elements set to cval (0.0 by default)
result = kernel_constant(array)
```

### Parallel Stencils

Enable parallel execution:

```python
from numba import njit, stencil

@njit(parallel=True)
def apply_stencil_parallel(arr):
    """Apply stencil with automatic parallelization."""
    kernel = stencil(lambda a: 0.25 * (a[0, 1] + a[0, -1] + a[1, 0] + a[-1, 0]))
    return kernel(arr)

result = apply_stencil_parallel(array)
```

### Multi-Input Stencils

Stencils can take multiple array inputs:

```python
@stencil
def advection_kernel(u, v, dt, dx):
    """2D advection stencil with velocity field."""
    u_center = u[0, 0]
    u_left = u[0, -1]
    u_right = u[0, 1]
    
    # Upwind scheme
    if v[0, 0] > 0:
        return u_center - (v[0, 0] * dt / dx) * (u_center - u_left)
    else:
        return u_center - (v[0, 0] * dt / dx) * (u_right - u_center)

# Apply
u_field = np.random.rand(100, 100)
v_field = np.ones((100, 100)) * 0.1
result = advection_kernel(u_field, v_field, dt=0.01, dx=1.0)
```

## JIT Classes

Compile Python classes for high-performance object-oriented code.

### Basic jitclass

```python
from numba import njit
from numba.experimental import jitclass
import numpy as np

# Define specification
spec = [
    ('center', np.float64),
    ('spread', np.float64),
]

@jitclass(spec)
class Gaussian1D:
    def __init__(self, center, spread):
        self.center = center
        self.spread = spread
    
    def pdf(self, x):
        from math import exp, pi, sqrt
        coef = 1.0 / (sqrt(2 * pi) * self.spread)
        return coef * exp(-0.5 * ((x - self.center) / self.spread) ** 2)
    
    def cdf_approx(self, x):
        """Approximate CDF using error function."""
        from math import erf
        z = (x - self.center) / self.spread
        return 0.5 * (1.0 + erf(z / sqrt(2)))

# Usage
gaussian = Gaussian1D(0.0, 1.0)
print(gaussian.pdf(1.0))
```

### Type Annotations

Use Python type hints for automatic spec inference:

```python
from numba import njit
from numba.experimental import jitclass
from numba import types

@jitclass
class Point2D:
    x: float
    y: float
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def distance_to_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def normalize(self):
        dist = self.distance_to_origin()
        if dist > 0:
            self.x /= dist
            self.y /= dist

point = Point2D(3.0, 4.0)
print(point.distance_to_origin())  # 5.0
```

### Nested jitclasses

jitclasses can contain other jitclasses:

```python
from numba.experimental import jitclass
import numpy as np

@jitclass
class Vector3D:
    x: float
    y: float
    z: float
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def magnitude(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

@jitclass
class Particle:
    position: Vector3D
    velocity: Vector3D
    mass: float
    
    def __init__(self, pos, vel, mass):
        self.position = pos
        self.velocity = vel
        self.mass = mass
    
    def kinetic_energy(self):
        v_mag_sq = (self.velocity.x**2 + 
                   self.velocity.y**2 + 
                   self.velocity.z**2)
        return 0.5 * self.mass * v_mag_sq

# Usage
pos = Vector3D(1.0, 2.0, 3.0)
vel = Vector3D(0.1, 0.2, 0.3)
particle = Particle(pos, vel, mass=1.0)
print(particle.kinetic_energy())
```

### Arrays in jitclasses

```python
from numba.experimental import jitclass
import numpy as np

spec = [
    ('data', np.float64[:]),
    ('scale', np.float64),
]

@jitclass(spec)
class ScaledArray:
    def __init__(self, data, scale):
        self.data = data
        self.scale = scale
    
    def scaled_sum(self):
        total = 0.0
        for i in range(self.data.shape[0]):
            total += self.data[i] * self.scale
        return total
    
    @property
    def max_value(self):
        if self.data.shape[0] == 0:
            return 0.0
        max_val = self.data[0]
        for i in range(1, self.data.shape[0]):
            if self.data[i] > max_val:
                max_val = self.data[i]
        return max_val

arr = ScaledArray(np.array([1.0, 2.0, 3.0]), scale=2.0)
print(arr.scaled_sum())      # 12.0
print(arr.max_value)         # 3.0
```

### Typed Containers in jitclasses

```python
from numba.experimental import jitclass
from numba import typed, types

# Using typed.List
spec_with_list = [
    ('values', types.ListType(types.float64)),
]

@jitclass(spec_with_list)
class Accumulator:
    def __init__(self):
        self.values = typed.List.empty_list(types.float64)
    
    def add(self, value):
        self.values.append(value)
    
    def total(self):
        total = 0.0
        for v in self.values:
            total += v
        return total
    
    def count(self):
        return len(self.values)

acc = Accumulator()
acc.add(1.0)
acc.add(2.0)
acc.add(3.0)
print(acc.total())   # 6.0
print(acc.count())   # 3
```

## Vectorize and GUVectorize

### @vectorize for UFuncs

Create NumPy universal functions:

```python
from numba import vectorize
import numpy as np

@vectorize(['float64(float64, float64)', 'float32(float32, float32)'])
def my_add(x, y):
    """Element-wise addition ufunc."""
    return x + y

# Works like NumPy ufunc
a = np.array([1.0, 2.0, 3.0])
b = np.array([4.0, 5.0, 6.0])
result = my_add(a, b)  # [5.0, 7.0, 9.0]

# Supports broadcasting
c = np.array([[1.0, 2.0], [3.0, 4.0]])
d = np.array([10.0, 20.0])
result = my_add(c, d)  # Broadcasting works!

# Supports reduction
total = my_add.reduce(a + b)  # Sum all elements
```

### Dynamic UFuncs (DUFunc)

Compile on first call with each type:

```python
@vectorize  # No signatures = dynamic compilation
def dynamic_add(x, y):
    return x + y

# Compiles for float64 on first call
result1 = dynamic_add(np.array([1.0]), np.array([2.0]))

# Compiles for int64 on first int call
result2 = dynamic_add(np.array([1]), np.array([2]))

# Compiles for complex128 on first complex call
result3 = dynamic_add(np.array([1j]), np.array([2j]))
```

### Target Selection

Choose execution target:

```python
@vectorize(['float64(float64)'], target='parallel')
def parallel_sqrt(x):
    """Multi-threaded vectorized sqrt."""
    return np.sqrt(x)

# For GPU (requires CUDA)
@vectorize(['float64(float64)'], target='cuda')
def gpu_sqrt(x):
    """GPU-accelerated sqrt."""
    return np.sqrt(x)
```

### @guvectorize for Generalized UFuncs

Create ufuncs with complex input/output shapes:

```python
from numba import guvectorize
import numpy as np

@guvectorize(['void(float64[:], float64, float64[:])'], '(n),()->(n)', target='cpu')
def add_scalar_to_array(arr, scalar, result):
    """Add scalar to each element of array."""
    for i in range(arr.shape[0]):
        result[i] = arr[i] + scalar

# Usage
arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
result = add_scalar_to_array(arr, 10.0)
print(result)  # [11.0, 12.0, 13.0, 14.0, 15.0]

# Broadcasting across multiple arrays
arrs = np.random.rand(10, 100)  # 10 arrays of length 100
scalars = np.arange(10, dtype=np.float64)  # 10 scalars
results = add_scalar_to_array(arrs, scalars)  # Shape (10, 100)
```

### Convolution Example

```python
@guvectorize(['void(float64[:], float64[:], float64[:])'], '(n),(m)->(n)', target='cpu')
def convolve_1d(signal, kernel, output):
    """1D convolution with explicit output array."""
    n = signal.shape[0]
    m = kernel.shape[0]
    
    for i in range(n):
        total = 0.0
        for j in range(m):
            sig_idx = i - j + (m // 2)
            if 0 <= sig_idx < n:
                total += signal[sig_idx] * kernel[j]
        output[i] = total

# Usage
signal = np.random.rand(1000)
kernel = np.array([0.25, 0.5, 0.25])  # Simple smoothing kernel
smoothed = convolve_1d(signal, kernel)
```

### Outer Product Example

```python
@guvectorize(['void(float64[:], float64[:], float64[:, :])'], '(n),(m)->(n,m)')
def outer_product(a, b, result):
    """Compute outer product of two vectors."""
    for i in range(a.shape[0]):
        for j in range(b.shape[0]):
            result[i, j] = a[i] * b[j]

# Usage
a = np.array([1.0, 2.0, 3.0])
b = np.array([4.0, 5.0])
result = outer_product(a, b)
print(result.shape)  # (3, 2)
```

## Typed Containers

Numba provides typed versions of Python containers for use in compiled code.

### Typed Lists

```python
from numba import njit, typed
import numpy as np

@njit
def use_typed_list():
    # Create empty list with specified type
    lst = typed.List.empty_list(types.float64)
    
    # Append elements
    for i in range(10):
        lst.append(i * 2.5)
    
    # Access by index
    first = lst[0]
    
    # Iterate
    total = 0.0
    for val in lst:
        total += val
    
    # List operations
    lst.extend([100.0, 200.0])
    lst.insert(0, -50.0)
    lst.pop()  # Remove last element
    
    return total, len(lst)

from numba import types
total, length = use_typed_list()
```

### Typed Dicts

```python
from numba import njit, typed
from numba import types

@njit
def use_typed_dict():
    # Create empty dict with key/value types
    d = typed.Dict.empty(types.int64, types.float64)
    
    # Add entries
    for i in range(10):
        d[i] = i * 3.14
    
    # Access values
    value = d[5]
    
    # Check membership
    if 3 in d:
        print("Key 3 exists")
    
    # Iterate over keys
    for key in d.keys():
        pass
    
    # Iterate over values
    total = 0.0
    for val in d.values():
        total += val
    
    # Iterate over items
    for key, val in d.items():
        d[key] = val * 2  # Update in place
    
    return total, len(d)

total, length = use_typed_dict()
```

### Typed Sets

```python
from numba import njit, typed
from numba import types

@njit
def use_typed_set():
    # Create empty set
    s = typed.Set.empty(types.int64)
    
    # Add elements
    for i in range(10):
        s.add(i * 2)  # Even numbers
    
    # Check membership
    has_4 = 4 in s
    has_5 = 5 in s  # False
    
    # Set operations
    s2 = typed.Set.empty(types.int64)
    for i in range(5, 15):
        s2.add(i * 2)
    
    # Union, intersection, difference
    union_set = s.union(s2)
    intersect_set = s.intersection(s2)
    diff_set = s.difference(s2)
    
    return len(s), len(union_set), len(intersect_set)

len_s, len_union, len_intersect = use_typed_set()
```

### Nested Containers

```python
from numba import njit, typed
from numba import types

@njit
def nested_containers():
    # List of lists
    outer = typed.List.empty_list(types.ListType(types.float64))
    for i in range(3):
        inner = typed.List.empty_list(types.float64)
        for j in range(5):
            inner.append(i * 10.0 + j)
        outer.append(inner)
    
    # Dict of lists
    d = typed.Dict.empty(types.int64, types.ListType(types.float64))
    for i in range(3):
        lst = typed.List.empty_list(types.float64)
        for j in range(5):
            lst.append(i * j)
        d[i] = lst
    
    return len(outer), len(d)

len_outer, len_dict = nested_containers()
```

## Overloading and Extending

### @overload for Custom Functions

Extend Numba with custom implementations:

```python
from numba import njit, overload
import numpy as np

@overload(np.sin)
def overloaded_sin(x):
    """Custom sin implementation for specific types."""
    if isinstance(x, types.Float):
        def sin_impl(x):
            # Custom implementation (for demonstration)
            return np.sin(x)
        return sin_impl

@njit
def use_overloaded_sin(x):
    return np.sin(x)
```

### @overload_function for New Functions

```python
from numba import njit, types
from numba.extending import overload_function

@overload_function(np.sqrt)
def sqrt_complex(x):
    """Add sqrt support for complex numbers."""
    if isinstance(x, types.Complex):
        def sqrt_impl(x):
            magnitude = (x.real**2 + x.imag**2) ** 0.5
            angle = np.arctan2(x.imag, x.real)
            sqrt_mag = magnitude ** 0.5
            return complex(
                sqrt_mag * np.cos(angle / 2),
                sqrt_mag * np.sin(angle / 2)
            )
        return sqrt_impl

@njit
def use_complex_sqrt():
    z = complex(3.0, 4.0)
    return np.sqrt(z)
```

### @overload_method for Class Methods

```python
from numba import types
from numba.extending import overload_method
import numpy as np

@overload_method(types.Array, 'custom_sum')
def array_custom_sum(arr):
    """Add custom_sum method to arrays."""
    def custom_sum_impl(arr):
        total = 0.0
        for i in range(arr.shape[0]):
            total += arr[i] ** 2
        return total
    return custom_sum_impl

@njit
def use_custom_method(arr):
    return arr.custom_sum()

arr = np.array([1.0, 2.0, 3.0])
result = use_custom_method(arr)  # 1 + 4 + 9 = 14.0
```

## Ahead-of-Time Compilation

Compile functions before runtime:

```python
from numba import cfunc
import numpy as np

@cfunc("float64(float64[:])")
def aot_sum(arr):
    """Compiled ahead of time."""
    total = 0.0
    for i in range(arr.shape[0]):
        total += arr[i]
    return total

# Function is compiled at definition time, not first call
```

### Using pycc (AOT Compiler)

Create shared libraries from Python:

```python
# file: mylib.py
from numba import exported_symbol

@exported_symbol("float64(float64[:])")
def process_array(arr):
    total = 0.0
    for i in range(arr.shape[0]):
        total += arr[i] ** 2
    return total
```

Compile with:
```bash
pycc -o mylib.so --output-dir=. mylib.py
```

Use from C/C++ or other Python processes.

## Troubleshooting Advanced Features

### jitclass Limitations

Not all Python features work in jitclasses:

```python
from numba.experimental import jitclass
import numpy as np

# Problem: Can't use Python builtins that aren't supported
@jitclass([('data', np.float64[:])])
class BadClass:
    def __init__(self, data):
        self.data = data
    
    def bad_method(self):
        # len() works, but some builtins don't
        return len(self.data)

# Solution: Use supported operations only
@jitclass([('data', np.float64[:])])
class GoodClass:
    def __init__(self, data):
        self.data = data
    
    def good_method(self):
        # Use shape[0] instead of len() for arrays
        return self.data.shape[0]
```

### Stencil Performance Tips

```python
from numba import stencil, njit

# Good: Pre-compile stencil and reuse
kernel = stencil(lambda a: 0.25 * (a[0, 1] + a[0, -1] + a[1, 0] + a[-1, 0]))

@njit(parallel=True)
def apply_multiple_times(arr):
    """Apply same stencil multiple times."""
    result = arr.copy()
    for _ in range(10):
        result = kernel(result)
    return result

# Bad: Define stencil inside loop (recompiles each time!)
```

### DUFunc Warm-up

Dynamic ufuncs compile on first call with each type:

```python
from numba import vectorize
import numpy as np

@vectorize  # Dynamic compilation
def my_ufunc(x):
    return np.sqrt(x)

# Warm up for expected types before timing
my_ufunc(np.array([1.0]))  # Warm up float64
my_ufunc(np.array([1]))    # Warm up int64

# Now benchmark
import timeit
arr = np.arange(1000000, dtype=np.float64)
time = timeit.timeit(lambda: my_ufunc(arr), number=10)
print(f"Time: {time / 10:.6f} seconds")
```
