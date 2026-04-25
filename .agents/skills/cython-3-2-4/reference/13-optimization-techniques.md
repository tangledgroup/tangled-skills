# Optimization Techniques

### Compiler Directives

Control code generation behavior:

```python
# File-wide directive
# cython: language_level=3, boundscheck=False, wraparound=False

def fast_loop(int[:] arr):
    # ... optimized code
    pass

# Local directive (overrides file-wide)
@cython.boundscheck(True)
def safe_access(int[:] arr, int index):
    return arr[index]
```

**Common directives:**

| Directive | Default | Effect when False/True |
|-----------|---------|------------------------|
| `boundscheck` | True | Skip array bounds checking (faster, unsafe) |
| `wraparound` | True | Disable negative index support (faster) |
| `cdivision` | False | Use C division (no ZeroError, true modulo) |
| `embedsignature` | False | Embed Cython signature in Python signature |
| `auto_cpdef` | False | Treat all def functions as cpdef |
| `language_level` | 2 | Python 2 vs 3 semantics |

### Performance Tips

1. **Type everything in hot paths:**
   ```python
   # Slow - all Python objects
   def slow_sum(arr):
       total = 0
       for x in arr:
           total += x
       return total
   
   # Fast - C integers
   def fast_sum(int[:] arr):
       cdef int total = 0, i
       for i in range(arr.shape[0]):
           total += arr[i]
       return total
   ```

2. **Use memoryviews for NumPy:**
   ```python
   # Slow - Python API calls
   def slow_numpy(np.ndarray arr):
       return np.sum(arr)
   
   # Fast - direct memory access
   def fast_numpy(double[:] arr):
       cdef double total = 0.0
       for i in range(arr.shape[0]):
           total += arr[i]
       return total
   ```

3. **Release GIL for CPU-bound work:**
   ```python
   def cpu_bound(int n) nogil:
       cdef int i, result = 0
       for i in range(n):
           result += expensive_calc(i)
       return result
   ```

4. **Use fused types for generic code:**
   ```python
   ctypedef fused real_types:
       float
       double
   
   cpdef squared(real_types x):
       return x * x
   ```

See [Optimization Reference](reference/06-optimization.md) for detailed strategies.
