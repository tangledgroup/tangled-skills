# Troubleshooting

### AttributeError on cdef Attributes

**Problem:** `AttributeError: 'Counter' object has no attribute 'count'`

**Cause:** `cdef` attributes are not accessible from Python by default.

**Solution:** Declare as `public` or `readonly`:
```python
cdef class Counter:
    cdef public int count  # Now accessible from Python
```

### Module Import Errors

**Problem:** `ModuleNotFoundError: No module named 'mymodule'`

**Cause:** Extension not built in correct location.

**Solution:** Use `--inplace` flag:
```bash
python setup.py build_ext --inplace
```

### Type Inference Issues

**Problem:** Code doesn't compile or is slower than expected.

**Cause:** Cython can't infer types at module level.

**Solution:** Explicitly declare global variables:
```python
# Instead of:
global_var = Counter()  # Treated as Python object

# Use:
cdef Counter global_var
global_var = Counter()
```

See [Troubleshooting Guide](reference/10-troubleshooting.md) for more issues.
