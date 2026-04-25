# Debugging

### Annotated HTML

Generate visual performance analysis:

```bash
cythonize -a yourmod.pyx
# Opens yourmod.html in browser showing:
# - Which lines are Python vs C
# - Color-coded by "Cyness" (how optimized)
```

### GDB Debugging

Build with debug symbols:
```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension("module", ["module.pyx"])
setup(ext_modules=cythonize([ext], gdb_debug=True))
```

Compile and debug:
```bash
python setup.py build_ext --inplace
cygdb
(gdb) cy break my_function
(gdb) cy run
(gdb) cy step
(gdb) cy next
```

### Runtime Debugging

Enable runtime checks:
```python
# In setup.py
setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={
            'boundscheck': True,
            'initializedcheck': True,
            'nonecheck': True
        }
    )
)
```
