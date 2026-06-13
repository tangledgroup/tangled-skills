# Auto-Tracing

## Overview

`logfire.install_auto_tracing()` traces all function calls in specified modules by changing how those modules are imported. It must be called before importing the target modules.

```python
import logfire

logfire.configure()
logfire.install_auto_tracing(modules=['app'], min_duration=0.01)

from app.main import main
main()
```

This traces all functions in the `app` package and its submodules, but only records those taking longer than 0.01 seconds.

## Minimum Duration Filtering

The `min_duration` argument controls which functions get traced:

- A function starts being traced only after it runs longer than `min_duration` once
- If it runs faster the first few times, you won't get data about those calls
- The first call exceeding `min_duration` is also not recorded
- After exceeding once, the function is traced every time regardless of duration
- Set `min_duration=0` to trace all calls from the beginning

For tiny functions called very frequently, use `@logfire.no_auto_trace` to avoid any overhead.

## Module Filtering

The `modules` argument accepts:
- List of module names (submodules are included automatically)
- Regex patterns for flexible matching
- A filter function receiving `AutoTraceModule` objects with `name` and `filename` attributes

```python
import pathlib
import logfire

PYTHON_LIB_ROOT = str(pathlib.Path(pathlib.__file__).parent)

def should_trace(module: logfire.AutoTraceModule) -> bool:
    return not module.filename.startswith(PYTHON_LIB_ROOT)

logfire.install_auto_tracing(should_trace, min_duration=0)
```

## Excluding Functions

Use `@logfire.no_auto_trace` to exclude specific functions or classes:

```python
import logfire

@logfire.no_auto_trace
def my_function():
    def inner_function():  # Also excluded (nested)
        ...
    return other_function()

def other_function():  # NOT excluded — still traced
    ...

@logfire.no_auto_trace
class MyClass:  # All methods excluded
    def my_method(self):
        ...
```

The decorator returns the argument unchanged — zero runtime overhead. Only `@no_auto_trace` or `@logfire.no_auto_trace` are detected (aliasing won't work).

## Generator Functions

Generator functions are not traced by auto-tracing. See the advanced generators documentation for details.
