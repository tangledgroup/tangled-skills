# Callbacks

## New-Style Callbacks: extern "Python"

The preferred mechanism for callbacks in API mode. Declare callback functions with `extern "Python"` in the cdef, then implement them in Python with `@ffi.def_extern()`.

### Basic Pattern

In the build script:

```python
ffibuilder.cdef("""
    extern "Python" int my_callback(int, int);

    void library_function(int(*callback)(int, int));
""")
ffibuilder.set_source("_my_example",
    r"""
        #include <some_library.h>
    """)
```

In the application:

```python
from _my_example import ffi, lib

@ffi.def_extern()
def my_callback(x, y):
    return x + y

# Pass lib.my_callback (the cdata pointer), not my_callback (the Python function)
lib.library_function(lib.my_callback)
```

The `extern "Python"` declaration generates a static C function that invokes the attached Python function. You get a `<cdata>` pointer-to-function by accessing `lib.my_callback`.

### Group Syntax

Multiple callbacks can be grouped:

```python
ffibuilder.cdef("""
    extern "Python" {
        int foo(int);
        int bar(int);
    }
""")
```

### Error Handling

If the Python callback raises an exception, it cannot propagate to C. By default, the exception is printed to stderr and a default value (0 or NULL) is returned. Control this with:

```python
@ffi.def_extern(error=-1)
def my_callback(x):
    # if this raises, returns -1 to C
    return compute(x)

@ffi.def_extern(onerror=my_handler)
def my_callback(x):
    return compute(x)

def my_handler(exc_type, exc_value, traceback):
    # handle the exception
    log_error(exc_value)
    # optionally return a value to use as the C result
```

The `onerror` handler receives `(exception, exc_value, traceback)`. If it returns normally, nothing is printed to stderr. If it raises, both tracebacks are printed. You can access original callback arguments via `traceback.tb_frame.f_locals`.

### extern "Python+C"

By default, `extern "Python"` generates `static` C functions. Use `extern "Python+C"` for non-static (exported) functions, typically when other C source files need to call them:

```python
ffibuilder.cdef("""
    extern "Python+C" int f(int);  // not static
""")
```

### Accessing extern "Python" from set_source() C Code

If your `set_source()` C code needs to call an `extern "Python"` function, add a forward declaration:

```python
ffibuilder.set_source("_demo",
    r"""
        static int my_callback(widget_t *, event_t *);

        // C code that uses &my_callback
        void register_it() {
            event_register(&my_callback);
        }
    """)
```

## Passing Context with void*

C callbacks often include a `void *userdata` parameter for passing context. Use `ffi.new_handle()` and `ffi.from_handle()`:

```python
# Build script
ffibuilder.cdef("""
    typedef struct { ...; } event_t;
    typedef void (*event_cb_t)(event_t *evt, void *userdata);
    void event_cb_register(event_cb_t cb, void *userdata);

    extern "Python" void my_event_callback(event_t *, void *);
""")

# Application
from _demo_cffi import ffi, lib

class Widget:
    def __init__(self):
        userdata = ffi.new_handle(self)
        self._userdata = userdata  # MUST keep this alive!
        lib.event_cb_register(lib.my_event_callback, userdata)

    def process_event(self, evt):
        print("got event!")

@ffi.def_extern()
def my_event_callback(evt, userdata):
    widget = ffi.from_handle(userdata)
    widget.process_event(evt)
```

**Important:** The result of `ffi.new_handle()` must be kept alive (stored in an instance variable or global) for as long as the callback may fire. If it is garbage collected, the `void *` becomes invalid.

## Old-Style Callbacks: ffi.callback()

The legacy mechanism using `ffi.callback()`. Works in ABI mode and for backward compatibility, but has significant limitations:

```python
@ffi.callback("int(int, int)")
def myfunc(x, y):
    return x + y

# myfunc is now a <cdata 'int(*)(int, int)'>
lib.some_function(myfunc)
```

### Warnings

- Relies on libffi's callback mechanism, which may crash on less common architectures (e.g., NetBSD)
- On hardened systems (PAX, SELinux), memory protections can interfere — SELinux requires `deny_execmem` set to `off`
- On macOS, requires the `com.apple.security.cs.allow-unsigned-executable-memory` entitlement
- On Linux with systemd, `MemoryDenyWriteExecute=` setting can block it
- After `fork()`, calling `ffi.callback()` can result in crashes or arbitrary code execution

### Lifetime

Like `ffi.new()`, `ffi.callback()` returns a cdata that owns its C data. The callback is only valid while this cdata object is alive:

```python
# Good: module-level, always alive
@ffi.callback("int(int, void *)")
def my_global_callback(x, handle):
    return ffi.from_handle(handle).some_method(x)

class Foo:
    def __init__(self):
        handle = ffi.new_handle(self)
        self._handle = handle  # must be kept alive
        lib.register(my_global_callback, handle)
```

### Error Handling

Same as extern "Python" — `error` and `onerror` parameters:

```python
@ffi.callback("int(int)", error=-1, onerror=my_handler)
def my_callback(x):
    return x * 2
```

## Variadic Callbacks

Neither `extern "Python"` nor `ffi.callback()` directly supports variadic callbacks. Work around it with a C wrapper in `set_source()`:

```python
ffibuilder.cdef("""
    int (*python_callback)(int how_many, int *values);
    void *const c_callback;
""")
ffibuilder.set_source("_example",
    r"""
        #include <stdarg.h>
        #include <alloca.h>

        static int (*python_callback)(int how_many, int *values);
        static int c_callback(int how_many, ...) {
            va_list ap;
            int i, *values = alloca(how_many * sizeof(int));
            va_start(ap, how_many);
            for (i=0; i<how_many; i++)
                values[i] = va_arg(ap, int);
            va_end(ap);
            return python_callback(how_many, values);
        }
    """)
```

Then in Python:

```python
from _example import ffi, lib

@ffi.callback("int(int, int *)")
def python_callback(how_many, values):
    print(ffi.unpack(values, how_many))
    return 0

lib.python_callback = python_callback
```

## Windows Calling Conventions

On Win32, functions use either `cdecl` (default) or `stdcall` (`WINAPI`). For direct function calls, CFFI handles both automatically. But for function pointers and callbacks, the convention must be explicit:

```python
@ffi.callback("int __stdcall(int, int)")
def AddNumbers(x, y):
    return x + y
```

In cdef:

```python
ffibuilder.cdef("""
    struct foo_s {
        int (__stdcall *MyFuncPtr)(int, int);
    };
""")
```

You can use `WINAPI` as equivalent to `__stdcall` in cdef. On platforms other than 32-bit Windows, these specifiers are accepted but ignored.

## Choosing Between Styles

- **Use `extern "Python"`** for API mode — it is faster, more portable, and avoids libffi callback issues
- **Use `ffi.callback()`** only for ABI mode or backward compatibility
- Prefer `extern "Python"` even when you could use old-style callbacks, as it generates static C functions that work on hardened systems
