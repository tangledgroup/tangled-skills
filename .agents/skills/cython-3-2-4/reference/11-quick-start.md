# Quick Start

### Installation

```bash
pip install Cython
```

If you need a C compiler (required for building extensions):

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential python3-dev
```

**macOS:**
```bash
xcode-select --install
```

**Windows:**
Install Visual Studio Build Tools with "Desktop development with C++"

### Hello World

Create `helloworld.py`:
```python
print("Hello World")
```

Create `setup.py`:
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("helloworld.py")
)
```

Build and run:
```bash
python setup.py build_ext --inplace
python -c "import helloworld"
# Output: Hello World
```

This produces `helloworld.so` (Linux/macOS) or `helloworld.pyd` (Windows).

### First Typed Function

Create `fibonacci.pyx`:
```python
def fib(int n):
    """Fibonacci sequence with typed parameter"""
    cdef int a = 0, b = 1, i, temp
    
    for i in range(n):
        temp = a + b
        a = b
        b = temp
        print(a)
```

Update `setup.py`:
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("fibonacci.pyx")
)
```

Build and test:
```bash
python setup.py build_ext --inplace
python
>>> import fibonacci
>>> fib(10)
1 1 2 3 5 8 13 21 34 55
```
