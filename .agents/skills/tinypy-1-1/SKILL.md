---
name: tinypy-1-1
description: TinyPy 1.1 — a minimalist Python implementation in ~64k of code featuring a Lua-esque bytecode VM, garbage collection, and C API for embedding. Use when embedding TinyPy in C applications, writing TinyPy extensions, bootstrapping self-hosted toolchains, or studying minimal Python implementations with classes, closures, list comprehensions, exceptions, and modules.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.1.0"
tags:
  - python
  - embedded
  - vm
  - bytecode
  - c-api
category: languages
external_references:
  - http://www.tinypy.org/
  - http://www.philhassey.com/blog/category/tinypy/
  - http://www.tinypy.org/community.html
  - https://github.com/philhassey/tinypy/blob/wiki/Index.md
  - https://github.com/philhassey/tinypy/tree/1.1
---
## Overview
TinyPy is designed to be embeddable in C applications while supporting a reasonable subset of Python:
- Classes and single inheritance
- Functions with variable or keyword arguments
- Strings, lists, dicts, numbers (double)
- Modules, list comprehensions
- Exceptions with full traceback
- Some builtins (`print`, `range`, `min`, `max`, `str`, `float`, `int`, `len`, `abs`, `round`, `copy`, `assert`, `chr`, `ord`, `system`, `istype`, `exec`, `import`, `save`, `load`, `fpack`, `merge`)

**What's notably absent:** file I/O (beyond `save`/`load`), threading, most standard library modules — "batteries not included."

## When to Use
- **Embedding TinyPy in C applications** — use the C API (`tp.h`) to create VM instances, execute code, and exchange data
- **Writing TinyPy extensions/modules** — implement C functions exposed to TinyPy scripts via `tp_fnc()` or `tp_method()`
- **Studying minimal Python implementations** — understand bytecode compilation, GC, and VM execution at a tiny scale
- **Bootstrapping toolchains** — TinyPy compiles `.py` → `.tpc` (bytecode) using its own compiler, then the C VM executes it

## Core Concepts
### Architecture

```
Python source (.py)
    ↓ py2bc.py  (compiler bootstrapped in TinyPy itself)
Bytecode (.tpc)
    ↓ tp_exec / tp_import
Lua-esque VM with garbage collection
```

The core compiler modules (`tokenize.py`, `parse.py`, `encode.py`, `py2bc.py`) are themselves compiled to bytecode and embedded as C arrays in the final binary. This is **full bootstrapping**.

### Virtual Machine

The `tp_vm` struct holds all state:
- `builtins` — dictionary of built-in functions
- `modules` — dictionary of loaded modules
- `params` — current function call parameters
- `frames[]` — call stack (up to 256 frames)
- `cur` — index of currently executing call frame
- `regs[]` — 16384 registers per VM
- GC tri-color mark-and-sweep with white/grey/black lists
- `strings` — string interning table

### Object Types (`tp_obj`)

Every value is a union of:

| Type | Constant | Fields |
|------|----------|--------|
| None | `TP_NONE` | — |
| Number | `TP_NUMBER` | `.number.val` (double) |
| String | `TP_STRING` | `.string.val` (char*), `.string.len` (int) |
| Dict | `TP_DICT` | `.dict` (hash table) |
| List | `TP_LIST` | `.list` (dynamic array) |
| Function | `TP_FNC` | `.fnc` — function info + globals |
| Data | `TP_DATA` | `.data.val` (void*), `.data.magic` (int) |

### Key Macros

- `TP` — shorthand for `tp_vm *tp` (first parameter of every API call)
- `TP_OBJ()` — get the next positional argument from current params
- `TP_NUM()` / `TP_STR()` — typed argument access (double / const char*)
- `TP_LOOP(e)` / `TP_END` — iterate over all remaining arguments in a for loop
- `tp_True` / `tp_False` / `tp_None` — singleton objects (`tp_True` and `tp_False` are numeric 1 and 0)
- `TP_CSTR(v)` — convert any tp_obj to C string via `tp_str()`

## Building TinyPy
### Linux (GCC)

```bash
python setup.py linux          # build basic tinypy
python setup.py linux math     # with math module
python setup.py linux pygame   # with pygame (needs SDL)
./build/tinypy examples/julia.py
```

### Windows (MinGW or Visual Studio)

```bash
python setup.py mingw [modules]
python setup.py vs [modules]   # needs VS vars32.bat
```

### 64k Shrink Mode

```bash
python setup.py 64k            # strips comments, namespaces, blank lines
# Result: ~64k of source (still compiles to a binary >64k)
```

### Single-File Blob

```bash
python setup.py blob           # produces build/tinypy.c and build/tinypy.h
```

## C API Reference
See the [C API reference](reference/01-c-api-reference.md) for complete function signatures.

### Initialization & Teardown

```c
// Create a new VM instance (argc/argv become sys.argv equivalent)
tp_vm *tp = tp_init(argc, argv);

// Destroy the VM and free all memory
tp_deinit(tp);
```

### Compiling & Executing Code

```c
// Compile Python source text to bytecode
tp_obj code = tp_compile(tp, tp_string("print('hello')"), tp_string("<eval>"));

// Execute bytecode with given globals dictionary
tp_obj globals = tp_dict(tp);
tp_exec(tp, code, globals);

// One-shot eval
tp_obj result = tp_eval(tp, "2 + 3", tp_dict(tp));
```

### Calling Functions from C

```c
// Call a tinypy function by name (looked up in builtins or modules)
tp_call(tp,
    tp_get(tp, tp->builtins, tp_string("foo")),
    tp_params_v(tp, tp_string("hello"))
);

// Alternative: call via module lookup
tp_call(tp, "math", "sin", tp_params_v(tp, 1, tp_number(0.5)));
```

### Creating Functions & Methods

```c
// Register a C function as a TinyPy callable (no self)
tp_set(tp, module_dict, tp_string("my_func"), tp_fnc(tp, my_c_function));

// Register a method (receives self as first argument)
tp_set(tp, obj_dict, tp_string("my_method"), tp_method(tp, self_obj, my_c_method));

// Register a bound function (self pre-bound to None in globals)
tp_set(tp, module_dict, tp_string("bound"), tp_def(tp, my_c_function, globals));
```

### Creating & Manipulating Objects

```c
// Create primitives
tp_obj num = tp_number(3.14);
tp_obj str = tp_string("hello");
tp_obj lst = tp_list(tp);
tp_obj dct = tp_dict(tp);

// Attribute lookup (self[k])
tp_obj val = tp_get(tp, dct, tp_string("key"));

// Failsafe attribute lookup — returns 1 on success, stores result in *r
tp_obj fallback;
if (!tp_iget(tp, &fallback, dct, tp_string("missing"))) {
    // key not found
}

// Check if key exists
int has_key = tp_has(tp, dct, tp_string("key"));  // returns tp_True or tp_False

// Attribute modification (self[k] = v)
tp_set(tp, dct, tp_string("key"), tp_string("value"));

// Remove dictionary entry (works on dicts, classes, objects — not lists)
tp_del(tp, dct, tp_string("key"));

// Get length of list/dict/string
tp_obj len_val = tp_len(tp, lst);

// Truth value: 0 for numeric 0, None, empty containers; 1 otherwise
int truthy = tp_bool(tp, some_obj);

// Get string representation (calls __str__)
tp_obj repr = tp_str(tp, some_obj);

// List operations — access internal _tp_list directly
_tp_list_append(tp, lst.list.val, tp_number(1));
tp_obj item = _tp_list_get(tp, lst.list.val, 0, "index");

// Dictionary iteration
for (int i = 0; i < tp_len(tp, dct).number.val; i++) {
    tp_obj key = tp_iter(tp, dct, tp_number(i));
}
```

**Note:** For lists, `tp_get(tp, lst, tp_None)` returns the first element and **removes it** from the list (pop behavior).

### Passing Custom C Pointers (Data Objects)

```c
typedef struct {
    char *name;
    int value;
} my_struct_t;

// GC cleanup callback (called when object is collected)
void __free__(TP, tp_obj self) {
    free(self.data.val);
}

// Create a data object wrapping a C pointer with magic type tag
my_struct_t *p = malloc(sizeof(my_struct_t));
tp_obj obj = tp_data(tp, 42, p);  // magic number 42 for type checking
obj.data.info->free = __free__;   // register GC cleanup callback

// Access fields: obj.data.val, obj.data.magic, obj.data.info->free
```

### Creating Objects & Classes (OOP)

```c
// Create a new base class (derived from builtin "object")
tp_obj cls = tp_class(tp);

// Create an instance of a class
tp_obj instance = tp_object(tp);

// Set the class (meta) of an object
tp_setmeta(tp, instance, cls);  // instance.__class__ = cls
```

In TinyPy, objects are dictionaries with a "meta" dictionary attached. When attributes are accessed but not found in the object dict, they fall back to the meta dict. Use `tp_getraw()` to access the raw dict when meta is set.

### String Handling

```c
// From C string — keeps a REFERENCE (do NOT free the source)
tp_obj str = tp_string("hello");

// From partial C string — specify byte count
tp_obj partial = tp_string_n(buf, n);

// Slice an existing string — tinypy manages storage safely
tp_obj slice = tp_string_slice(tp, original_str, 0, 3);

// Safe for temporary buffers (tinypy makes its own copy)
char tmp[4] = "foo";
return tp_string_slice(tp, tp_string(tmp), 0, 3);  // safe even if tmp goes out of scope
```

### Raising Exceptions

```c
// Macro that returns immediately after raising an exception via longjmp
tp_raise(tp_None, "error: %s", message);

// The macro formats the message with printf-style arguments and longjmps
// to the nearest try/except handler in the VM.
```

### Iterating Over Arguments (TP_LOOP)

```c
tp_obj *my_variadic_func(tp_vm *tp) {
    // Get first argument normally
    tp_obj first = TP_OBJ();

    // Iterate over all remaining arguments
    tp_obj arg;
    TP_LOOP(arg)
        // do something with arg
    TP_END
}
```

### Creating Parameter Lists for Function Calls

```c
// Variadic — convenient for small numbers of args
tp_params_v(tp, 2, tp_number(1.0), tp_string("hello"));

// Array-based — for dynamic/variable-length parameter lists
tp_obj argv[] = { tp_number(1.0), tp_number(2.0), tp_number(3.0) };
tp_params_n(tp, 3, argv);
```

### Importing Modules

```c
// Import a pre-compiled .tpc module from file
tp_import(tp, "mymodule.tpc", "mymodule", NULL);

// Or pass bytecode directly (fname is ignored)
tp_import(tp, NULL, "mymodule", compiled_code_bytes);

// Built-in tp_import also supports: from x import * / from x import y
```

## Building Custom Modules
Modules are C files that provide an `init` function. The build system stitches them into the binary.

### Module Structure (`modules/mymodule/init.c`)

```c
#include "tp.h"

// C function exposed to TinyPy
static tp_obj my_add(TP) {
    double a = TP_NUM();
    double b = TP_NUM();
    return tp_number(a + b);
}

// Module init function (called during tp_init)
void mymodule_init(TP) {
    tp_obj mod = tp_dict(tp);

    // Add functions
    tp_set(tp, mod, tp_string("add"), tp_fnc(tp, my_add));

    // Add constants
    tp_set(tp, mod, tp_string("VERSION"), tp_number(1.0));

    // Register with the module registry
    tp_set(tp, tp->modules, tp_string("mymodule"), mod);
}
```

### Build Integration (`tpmain.c`)

The main file includes all module init functions:

```c
/* INCLUDE */   /* replaced by setup.py with #include directives */

void tp_builtins(TP);
void tp_args(TP, int argc, char *argv[]);

int main(int argc, char *argv[]) {
    tp_vm *tp = _tp_init();
    tp_builtins(tp);
    tp_args(tp, argc, argv);

    /* INIT */   /* replaced by setup.py with init function calls */

    // Run the main script
    void *code = ...;  // loaded bytecode
    tp_main(tp, "script.tpc", code);

    tp_deinit(tp);
    return 0;
}
```

## TinyPy Language Features
### Supported Syntax

- Arithmetic: `+`, `-`, `*`, `/`, `**` (power), `%` (modulo)
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Assignment: `=`, augmented assignment (`+=`, etc.)
- Control flow: `if/elif/else`, `while`, `for` (over lists only)
- Functions: `def name(args):`, variable args, keyword args
- Classes: `class Name(Base):`, single inheritance, `__init__`
- List comprehensions: `[x*2 for x in range(10)]`
- Tuples: `(a, b, c)` — unpacking supported
- Exceptions: `try/except` with full traceback
- Strings: `'single'` and `"double"` quotes

### Limitations

- **No generator expressions** — only list comprehensions
- **No file I/O** beyond `save()`/`load()` (binary only)
- **No threading**
- **No standard library** — only the builtins listed above
- **Variable/keyword arg mixing doesn't work** in all combinations (Lua-style)
- Numbers are all `double` — no integer types, no complex numbers

## Running TinyPy Scripts
```bash
# Run a pre-compiled bytecode file
./build/tinypy script.tpc

# Arguments become ARGV (accessible as sys.argv equivalent)
./build/tinypy script.tpc arg1 arg2

# Run the VM directly with .tpc files
./build/vm module.tpc
```

## Bootstrap Process
TinyPy's compiler is written in Python and then bootstrapped:

1. **First pass**: CPython runs `py2bc.py` to compile `tokenize.py`, `parse.py`, `encode.py`, `py2bc.py` into `.tpc` bytecode files
2. **Bootstrap**: The VM loads these `.tpc` files and runs them under the embedded TinyPy VM
3. **Second pass**: The self-hosted TinyPy compiler recompiles everything, producing optimized bytecode
4. **Final binary**: Bytecode arrays are compiled into `bc.c`, linked with the C runtime

This ensures the final binary is fully self-contained — no Python interpreter needed at runtime.

## Usage Examples
```c
#include "tinypy.h"  // or build/tinypy.h from 'blob' mode
int main() {
    tp_vm *tp = tp_init(0, NULL);
    tp_obj math_mod = tp_dict(tp);
    tp_set(tp, math_mod, tp_string("pi"), tp_number(3.14159));
    tp_set(tp, tp->modules, tp_string("mymath"), math_mod);
    tp_obj globals = tp_dict(tp);
    tp_obj code = tp_compile(tp, tp_string("print(pi * 2)"), tp_string("<script>"));
    tp_exec(tp, code, globals);
    tp_deinit(tp);
    return 0;
}
```

### Example: Math Module Pattern
See `modules/math/init.c` for a complete module. Key pattern uses a macro:

```c
#define TP_MATH_FUNC1(cfunc) \
    static tp_obj math_##cfunc(TP) { \
        double x = TP_NUM(); errno = 0; \
        double r = cfunc(x); \
        if (errno == EDOM || errno == ERANGE) \
            tp_raise(tp_None, "%s: out of range", __func__); \
        return tp_number(r); \
    }
TP_MATH_FUNC1(sin)
TP_MATH_FUNC1(cos)
```

### Example: OOP with Meta Dictionaries
```c
#include "tp.h"
static tp_obj point_init(TP) {
    tp_obj self = TP_OBJ();
    double x = TP_NUM(), y = TP_NUM();
    tp_set(tp, self, tp_string("x"), tp_number(x));
    tp_set(tp, self, tp_string("y"), tp_number(y));
    return tp_None;
}
int main() {
    tp_vm *tp = tp_init(0, NULL);
    tp_obj point_cls = tp_class(tp);
    tp_set(tp, point_cls, tp_string("__init__"),
           tp_method(tp, tp_None, point_init));
    tp_obj pt = tp_object(tp);
    tp_setmeta(tp, pt, point_cls);
    tp_call(tp, tp_get(tp, pt, tp_string("__init__")),
            tp_params_v(tp, 3, tp_number(1.0), tp_number(2.0)));
    tp_obj x_val = tp_get(tp, pt, tp_string("x"));
    printf("x = %f\n", x_val.number.val);
    tp_deinit(tp);
    return 0;
}
```

## Advanced Topics
## Advanced Topics

- [C Api Reference](reference/01-c-api-reference.md)

