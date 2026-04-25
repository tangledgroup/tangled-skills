# Nuitka Module and Package Compilation

Comprehensive guide to compiling extension modules, packages, controlling imports, and handling dynamic loading scenarios.

## Extension Module Compilation

### Basic Extension Module

```bash
# Compile single module as extension
python -m nuitka --module my_module.py

# Output: my_module.so (Linux/macOS) or my_module.pyd (Windows)
```

**Usage**: The compiled module replaces `my_module.py` and can be imported normally:
```python
import my_module  # Loads compiled version
```

### Important Constraints

1. **Filename must match source**: Python requires specific entry point names (`PyInit_module_name`)
2. **Cannot include other extensions**: Extension modules cannot contain other compiled extensions
3. **Version-specific**: Compiled module only works with same Python version used for compilation
4. **No recursive imports**: Use `--follow-import-to` to include dependencies (they become importable after importing main module)

### Example Extension Module

```python
# my_module.py
def expensive_computation(x):
    result = 0
    for i in range(x):
        result += i * i
    return result

def initialize():
    print("Module initialized")

if __name__ == "__main__":
    initialize()
```

Compile and use:
```bash
python -m nuitka --module my_module.py
# Creates my_module.so

# Now use in other scripts
python -c "import my_module; print(my_module.expensive_computation(1000))"
```

## Package Compilation

### Compile Entire Package

```bash
# Compile package with all submodules
python -m nuitka --standalone --follow-imports my_package

# Or as module (creates package extension)
python -m nuitka --mode=package my_package
```

**Output structure** (standalone mode):
```
my_package.dist/
├── my_package (executable)
├── python3.x.dll (or .so/.dylib)
├── my_package/
│   ├── __init__.pyc
│   ├── module1.so
│   └── module2.so
└── dependencies/
```

### Excluding Subpackages

```bash
# Exclude tests from compilation
python -m nuitka --standalone --follow-imports \
  --nofollow-import-to='*.tests' \
  --nofollow-import-to='*.test' \
  my_package

# Exclude documentation
python -m nuitka --standalone --follow-import-to=my_package \
  --nofollow-import-to='*.docs' \
  my_package/__main__.py
```

### Package with `__main__`

For packages that can be run with `python -m`:

```bash
# Compile package's __main__ as entry point
python -m nuitka --standalone my_package.__main__

# Or specify explicitly
python -m nuitka --standalone -m my_package
```

## Import Control Strategies

### Follow Imports (Recursive)

```bash
# Follow all imports (may be slow for large packages)
python -m nuitka --follow-imports program.py

# Equivalent explicit form
python -m nuitka --standalone --follow-import-to=* program.py
```

### Selective Following

```bash
# Only follow specific modules
python -m nuitka --follow-import-to=pandas,numpy,my_module program.py

# Follow package but not tests
python -m nuitka --follow-import-to=my_package \
  --nofollow-import-to='my_package.tests' \
  program.py
```

### Prevent Following

```bash
# Don't follow any imports (compile only main script)
python -m nuitka --nofollow-imports program.py

# Don't follow specific patterns
python -m nuitka --nofollow-import-to=tests,docs,benchmarks program.py

# Wildcard patterns
python -m nuitka --nofollow-import-to='*.test*' program.py
```

### Force Include Modules

For dynamic imports not detectable by static analysis:

```bash
# Include single module
python -m nuitka --include-module= dynamically_imported_module program.py

# Include multiple modules
python -m nuitka --include-module=mod1,mod2,mod3 program.py

# Include entire package
python -m nuitka --include-package=large_package program.py

# Include package submodules
python -m nuitka --include-package=package.subpackage program.py
```

### Include Plugin Directories

For dynamically loaded plugins:

```bash
# Include all .py files in directory
python -m nuitka --include-plugin-directory=plugins program.py

# Multiple plugin directories
python -m nuitka --include-plugin-directory=plugins \
  --include-plugin-directory=extensions \
  program.py
```

**Use case**: When using `__import__()` or custom importers that Nuitka cannot analyze statically.

## Dynamic Import Handling

### Problem: Runtime-Discovered Imports

Nuitka performs static analysis and may miss:
- `importlib.import_module(variable)`
- `__import__(variable)`
- Plugin systems loading modules by name
- Conditional imports based on configuration

### Solutions

#### 1. Include Module Option (Recommended)

```bash
python -m nuitka --include-module=possibly_imported program.py
```

#### 2. Nuitka Project File

Create `.nuitka-project` file or use inline comments:

```python
# nuitka-project: --include-module=dynamic_module1
# nuitka-project: --include-module=dynamic_module2
# nuitka-project: --standalone

def load_plugin(name):
    import importlib
    return importlib.import_module(name)
```

#### 3. User Plugin

Create custom plugin to handle dynamic loading (see [Plugin System](04-plugins.md)).

### Example: Plugin System

```python
# plugins/__init__.py
import os
import importlib

PLUGINS_DIR = os.path.dirname(__file__)

def load_all_plugins():
    plugins = []
    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith('.py') and not filename.startswith('_'):
            module_name = filename[:-3]
            # This dynamic import needs --include-plugin-directory
            mod = importlib.import_module(f'plugins.{module_name}')
            plugins.append(mod)
    return plugins
```

Compile with:
```bash
python -m nuitka --standalone \
  --include-plugin-directory=plugins \
  program.py
```

## Demotion (Keeping Modules Uncompiled)

### What is Demotion?

Demotion keeps modules as Python files instead of compiling to C. Benefits:
- **Faster compilation** - skip C generation for large libraries
- **Debugging** - easier to trace through uncompiled code
- **Compatibility** - avoid issues with problematic modules

### Demote Specific Modules

```bash
# Demote single module
python -m nuitka --demote=pandas program.py

# Demote multiple modules
python -m nuitka --demote=pandas,numpy,scipy program.py

# Pattern matching
python -m nuitka --demote='*tests*' program.py
```

### When to Use Demotion

1. **Very large packages** (pandas, tensorflow) - compilation takes hours
2. **Problematic modules** - compile errors or runtime issues
3. **Frequent development** - faster iteration without recompiling dependencies
4. **Debugging** - need Python-level traces through third-party code

### Demotion vs NoFollow

```bash
# --demote: Module stays as .py, still included in standalone
python -m nuitka --standalone --demote=pandas program.py

# --nofollow-import-to: Module not compiled, must be installed on target
python -m nuitka --standalone --nofollow-import-to=pandas program.py
```

**Key difference**: Demoted modules are copied to `.dist` folder; nofollow modules require installation on target.

## C Extension Handling

### Including C Extensions

Nuitka automatically handles C extensions from your Python installation:
- They are copied to `.dist` folder in standalone mode
- No compilation needed (already compiled)
- Must be compatible with target Python version

### Common C Extensions

- `numpy`, `scipy`, `pandas` - numerical computing
- `PIL` (Pillow) - image processing
- `lxml` - XML parsing
- `psycopg2` - PostgreSQL adapter

These work automatically in standalone mode, but may need plugins:

```bash
python -m nuitka --standalone --enable-plugin=numpy program.py
```

### Creating C Extensions with Nuitka

Nuitka can compile Python to extension modules that can be imported:

```bash
# Create extension from Python
python -m nuitka --module fast_module.py

# Use in other programs
python -c "import fast_module; print(fast_module.function())"
```

**Performance**: Compiled extensions are faster than pure Python, especially for:
- Tight loops
- Numeric computations
- String processing
- Function call overhead reduction

## Namespace Packages

### PEP 420 Namespace Packages

For namespace packages (no `__init__.py`):

```bash
# Include namespace package
python -m nuitka --include-package=namespace_package program.py

# May need to follow imports explicitly
python -m nuitka --follow-import-to=namespace_package.program program.py
```

### Editable Installs

Nuitka does not support editable installs (`pip install -e .`). Install normally:

```bash
# Wrong (editable install)
pip install -e ./my_package

# Right (regular install)
pip install ./my_package
# or
python setup.py install
```

## Circular Imports

### Handling Circular Dependencies

Nuitka handles most circular imports automatically. If issues occur:

```bash
# Increase recursion limit during compilation
python -m nuitka --recursion-limit=10000 program.py

# Use --full-compat for maximum compatibility
python -m nuitka --full-compat program.py
```

### Example Circular Import

```python
# module_a.py
from module_b import function_b  # Circular!

def function_a():
    return function_b() + 1

# module_b.py
from module_a import function_a

def function_b():
    return function_a() * 2
```

This compiles fine with Nuitka in most cases.

## Conditional Imports

### Platform-Specific Imports

```python
# program.py
import sys

if sys.platform == "win32":
    import win_specific  # Need to include this
else:
    import unix_specific  # And this

def main():
    # ...
    pass
```

Compile with both modules included:

```bash
python -m nuitka --include-module=win_specific \
  --include-module=unix_specific \
  --standalone program.py
```

### Optional Dependencies

```python
# program.py
try:
    import optional_feature
    HAS_OPTIONAL = True
except ImportError:
    HAS_OPTIONAL = False

def main():
    if HAS_OPTIONAL:
        optional_feature.do_something()
```

Include optional module:

```bash
python -m nuitka --include-module=optional_feature program.py
```

## Compilation Order and Dependencies

### Explicit Module Ordering

For complex dependency graphs, you can pre-compile modules:

```bash
# Compile dependencies first
python -m nuitka --module shared_utils.py
python -m nuitka --module common_module.py

# Then compile main program
python -m nuitka --standalone program.py
```

### Multiple Entry Points

For applications with multiple entry points:

```bash
# Compile each entry point separately
python -m nuitka --standalone cli_tool.py
python -m nuitka --standalone gui_app.py
python -m nuitka --standalone --module=package server_entry.py
```

Each creates independent `.dist` folder. Consider sharing common code via `--include-module`.

## Troubleshooting Import Issues

### Module Not Found at Runtime

**Symptoms**: `ModuleNotFoundError` in compiled program

**Solutions**:
1. Use `--include-module=module_name`
2. Check compilation report for import attempts
3. Verify module is importable during compilation
4. For packages, use `--include-package` instead

### Check Compilation Report

```bash
python -m nuitka --report=compilation-report.xml program.py

# Search report for failed imports
grep -i "not found" compilation-report.xml
grep -i "import" compilation-report.xml | grep -i "fail"
```

### Dynamic Import Debugging

Add debug output to see what's being imported:

```python
import sys

original_import = __import__

def debug_import(name, *args, **kwargs):
    print(f"Importing: {name}", file=sys.stderr)
    return original_import(name, *args, **kwargs)

__import__ = debug_import

# Now run your dynamic import code
```

Compile with `--include-module` for all modules printed.

### PYTHONPATH During Compilation

If your code uses custom paths:

```bash
# Set PYTHONPATH to include custom modules
export PYTHONPATH=/path/to/custom/modules:$PYTHONPATH
python -m nuitka --standalone program.py

# Or use -P flag (Python's path option)
python -P -m nuitka --standalone program.py
```

**Important**: Paths in PYTHONPATH during compilation must match runtime paths in standalone mode.
