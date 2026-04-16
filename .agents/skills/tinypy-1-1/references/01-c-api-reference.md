# TinyPy 1.1 — C API Reference

Complete reference for the TinyPy C embedding API as of version 1.1, based on the official wiki documentation.

## Types

### `tp_obj` — The Universal Object Type

```c
typedef union tp_obj {
    int type;                         // TP_NONE, TP_NUMBER, TP_STRING, etc.
    tp_number_ number;                // .type == TP_NUMBER → .number.val (double)
    tp_string_ string;                // .type == TP_STRING → .string.val (char*), .string.len (int)
    tp_dict_ dict;                    // .type == TP_DICT
    tp_list_ list;                    // .type == TP_LIST
    tp_fnc_ fnc;                      // .type == TP_FNC
    tp_data_ data;                    // .type == TP_DATA → .data.val (void*), .data.magic (int)
} tp_obj;
```

**Fields per type:**

| Type | Constant | Fields |
|------|----------|--------|
| None | `TP_NONE` | No accessible fields beyond `.type` |
| Number | `TP_NUMBER` | `.number.val` — double value |
| String | `TP_STRING` | `.string.val` — pointer to string data; `.string.len` — length in bytes |
| Dict | `TP_DICT` | `.dict` — hash table pointer |
| List | `TP_LIST` | `.list` — dynamic array pointer (`_tp_list*`) |
| Function | `TP_FNC` | `.fnc` — function info + globals |
| Data | `TP_DATA` | `.data.val` — user-provided data pointer; `.data.magic` — type tag; `.data.info->free` — GC cleanup callback |

### `tp_vm` — Virtual Machine Instance

```c
typedef struct tp_vm {
    tp_obj builtins;                  // Dictionary of builtin functions
    tp_obj modules;                   // Dictionary of loaded modules
    tp_frame_ frames[256];           // Call stack (TP_FRAMES = 256)
    tp_obj params;                    // Current function call parameters
    tp_obj *regs;                     // Register array (16384 entries)
    tp_obj root;                      // Root object for GC root tracking
    jmp_buf buf;                      // Setjmp buffer for exception handling
    int jmp;                          // Non-zero if inside try/except
    tp_obj ex;                        // Current exception object
    _tp_list *white, *grey, *black;   // GC tri-color lists
    _tp_dict *strings;                // String interning table
} tp_vm;
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `builtins` | Dictionary containing all builtin objects and functions |
| `modules` | Dictionary with all loaded modules |
| `params` | List of parameters for the current function call |
| `frames` | Array of all call frames (max 256) |
| `cur` | Index of the currently executing call frame |
| `frames[n].globals` | Dictionary of global symbols in call frame n |

### `TP` — Shorthand Macro

```c
#define TP tp_vm *tp
// Use as first parameter of every API function:  void my_func(TP) { ... }
```

## Constants & Singletons

| Constant | Description |
|----------|-------------|
| `tp_None` | The None singleton object |
| `tp_True` | Numeric value 1 (shortcut for `tp_number(1)`) |
| `tp_False` | Numeric value 0 (shortcut for `tp_number(0)`) |
| `TP_NONE`, `TP_NUMBER`, `TP_STRING`, `TP_DICT`, `TP_LIST`, `TP_FNC`, `TP_DATA` | Type constants |

## Object Creation

### Numbers

```c
tp_obj tp_number(tp_num v);  // inline static — creates a number from double
```

### Strings

```c
tp_inline static tp_obj tp_string(char const *v);           // from C string (reference kept)
tp_inline static tp_obj tp_string_n(char const *v, int n);  // from partial C string
tp_obj tp_string_slice(TP, tp_obj s, int a, int b);         // slice existing string (tinypy manages storage)
```

**Important:** `tp_string()` and `tp_string_n()` keep a **reference** to the C string — do not free it. Use `tp_string_slice()` when the source buffer may go out of scope:

```c
// Safe for temporary buffers (tinypy makes its own copy)
char test[4] = "foo";
tp_obj safe = tp_string_slice(tp, tp_string(test), 0, 3);  // works after function returns
```

The slice parameters `a` and `b` correspond to Python slice notation: `s[a:b]`.

### Lists

```c
tp_obj tp_list(TP);                                         // empty list (returns untracked if tp is NULL)
void _tp_list_append(TP, _tp_list *self, tp_obj v);         // append to list
void _tp_list_insert(TP, _tp_list *self, int n, tp_obj v);  // insert at index n
tp_obj _tp_list_get(TP, _tp_list *self, int k, const char *error);  // get element by index
tp_obj _tp_list_pop(TP, _tp_list *self, int n, const char *error);  // remove and return element at n
void _tp_list_realloc(_tp_list *self, int len);             // resize internal array
```

### Dictionaries

```c
tp_obj tp_dict(TP);                                          // empty dictionary
// Note: if you use tp_setmeta() on a dict, access raw data with tp_getraw()
```

### Functions

```c
tp_obj tp_fnc_new(TP, int type, void *val, tp_obj self, tp_obj globals);
tp_obj tp_def(TP, void *val, tp_obj globals);  // bound function (self = None)
tp_obj tp_fnc(TP, tp_obj (*)(TP));             // unbound C function
tp_obj tp_method(TP, tp_obj self, tp_obj (*)(TP));  // method with self pre-bound
```

Function type flags:
- `0` — unbound function (C signature: `tp_obj func(TP)`)
- `1` — bound/definition (self is None in globals)
- `2` — method (self is prepended to arguments)

### Data Objects (User Pointers)

```c
typedef struct _tp_data {
    int gci;
    void (*free)(TP, tp_obj);  // GC cleanup callback (optional)
} _tp_data;

tp_obj tp_data(TP, int magic, void *v);
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `magic` | Integer number associated with the data type — used to check the type of data objects |
| `v` | Pointer to user data. Only the pointer is stored; you keep all responsibility for the data it points to |

**Public fields:**
| Field | Description |
|-------|-------------|
| `.magic` | Integer number stored in the object |
| `.val` | The data pointer of the object |
| `.info->free` | If not NULL, a callback function called when the object gets destroyed |

**Example with GC cleanup:**

```c
void *__free__(TP, tp_obj self) {
    free(self.data.val);
}

tp_obj my_obj = tp_data(TP, 0, my_ptr);
my_obj.data.info->free = __free__;
```

### Classes & Objects (OOP)

```c
tp_obj tp_class(TP);      // Creates a new base class (derived from builtin "object")
tp_obj tp_object(TP);     // Creates a new object (no parent class initially)
tp_obj tp_setmeta(TP, tp_obj self, tp_obj meta);  // Set the "meta" (class/parent class) of a dict
```

In TinyPy, each dictionary can have a **meta** dictionary attached. When attributes are accessed but not found in the dictionary, they fall back to the meta dictionary. This is how classes and inheritance work:

1. `tp_class()` creates an empty class (derived from builtin "object")
2. `tp_object()` creates a new object instance with no parent class
3. `tp_setmeta(instance, cls)` sets the class of the object
4. Use `tp_getraw()` to access the raw dict when meta is set

### tp_getraw — Retrieve Raw Dict

```c
tp_obj tp_getraw(TP);
```

This builtin retrieves one dict parameter from TinyPy and returns its **raw dict**. This is very useful when implementing your own get and set functions, as it allows you to directly access the attributes stored in the dict.

## Attribute Operations

### tp_set — Attribute Modification

```c
void tp_set(TP, tp_obj self, tp_obj k, tp_obj v);
```

This is the counterpart of `tp_get`. It does the same as `self[k] = v` would do in actual TinyPy code.

### tp_get — Attribute Lookup

```c
tp_obj tp_get(TP, tp_obj self, tp_obj k);
```

Returns the result of using `self[k]` in actual code. Works for dictionaries (including classes and instantiated objects), lists, and strings.

**Special case:** If `self` is a list, `self[None]` returns the **first element** and subsequently **removes it** from the list (pop behavior).

### tp_iget — Failsafe Attribute Lookup

```c
int tp_iget(TP, tp_obj *r, tp_obj self, tp_obj k);
```

Like `tp_get`, except it returns `0` (false) if the attribute lookup failed. Otherwise returns `1` (true), and the object is returned over the reference parameter `r`.

### tp_has — Check Key Existence

```c
tp_obj tp_has(TP, tp_obj self, tp_obj k);
```

Returns `tp_True` if `self[k]` exists, `tp_False` otherwise.

### tp_del — Remove Dictionary Entry

```c
void tp_del(TP, tp_obj self, tp_obj k);
```

Removes the key `k` from `self`. Also works on classes and objects. Unlike Python, you **cannot** use this to remove list items.

## Type Operations

### tp_len — Length

```c
tp_obj tp_len(TP, tp_obj self);
```

Returns the number of items in a list or dict, or the length of a string.

### tp_bool — Truth Value

```c
int tp_bool(TP, tp_obj v);
```

Returns `0` (false) if `v` is:
- A numeric object with value exactly 0
- Of type None
- A string, list, or dictionary with length 0

Returns `1` (true) otherwise.

### tp_str — String Representation

```c
tp_obj tp_str(TP, tp_obj self);
```

Returns a string object representing `self`.

## VM Lifecycle

### tp_init — Create VM

```c
tp_vm *tp_init(int argc, char *argv[]);
```

Initializes a new virtual machine. The given parameters have the same format as `main()` arguments, and allow passing arguments to TinyPy scripts.

**Returns:** The newly created tinypy instance.

### tp_deinit — Destroy VM

```c
void tp_deinit(TP);
```

Destroys a VM instance and frees all memory used by it. Even when using only a single tinypy instance, it is good practice to call this on shutdown.

## Compilation & Execution

### tp_compile — Compile Code

```c
tp_obj tp_compile(TP, tp_obj text, tp_obj fname);
```

Compiles TinyPy source text to bytecode. The `fname` parameter is used for error messages (e.g., `"<eval>"`).

### tp_exec — Execute Bytecode

```c
tp_obj tp_exec(TP, tp_obj code, tp_obj globals);
```

Executes VM bytecode with the given globals dictionary.

### tp_eval — One-Shot Eval

```c
tp_obj tp_eval(TP, char *text, tp_obj globals);
```

One-shot: compile and execute in a single call.

### tp_call — Call a TinyPy Function from C

```c
tp_obj tp_call(TP, tp_obj self, tp_obj params);
```

Calls a TinyPy function. 

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `tp` | The VM instance |
| `self` | The object to call (the function) |
| `params` | Parameters to pass (a list from `tp_params_v()` or `tp_params_n()`) |

**Example:**
```c
tp_call(tp,
    tp_get(tp, tp->builtins, tp_string("foo")),
    tp_params_v(tp, tp_string("hello"))
);
// Looks up global function "foo" and calls it with one positional parameter
```

## Module Import

### tp_import — Import Module

```c
tp_obj tp_import(TP, char const *fname, char const *name, void *codes);
```

Imports a module.

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `fname` | Path to a file containing the module's code (ignored if `codes != NULL`) |
| `name` | The name of the module |
| `codes` | The module's bytecode pointer (if non-NULL, fname is ignored) |

**Returns:** The module object.

## Argument Handling (Inside C Functions)

### TP_OBJ() — Get Next Positional Argument

```c
#define TP_OBJ()  (tp_get(tp, tp->params, tp_None))
```

Get the next positional argument from the current function's parameter list.

### TP_NUM() / TP_STR() — Typed Arguments

```c
#define TP_NUM()  (TP_TYPE(TP_NUMBER).number.val)  // typed: double
#define TP_STR()  (TP_CSTR(TP_TYPE(TP_STRING)))    // typed: const char*
```

Access arguments with type checking.

### TP_DEFAULT(d) — Optional Arguments with Defaults

```c
#define TP_DEFAULT(d) \
    (tp->params.list.val->len ? tp_get(tp, tp->params, tp_None) : (d))
```

Get an optional argument with a default value `d` if no more arguments remain.

### TP_LOOP / TP_END — Iterate Over Remaining Arguments

```c
#define TP_LOOP(e) \
    int __l = tp->params.list.val->len; \
    int __i; for (__i=0; __i<__l; __i++) { \
    (e) = _tp_list_get(tp, tp->params.list.val, __i, "TP_LOOP");

#define TP_END }  // closes the TP_LOOP
```

If you have a function which takes a variable number of arguments:

```c
tp_obj *my_func(tp_vm *tp) {
    tp_obj first = TP_OBJ();  // get first argument normally
    tp_obj arg;
    TP_LOOP(arg)
        // do something with arg
    TP_END
}
```

## Parameter Passing

### tp_params — Initialize Parameters

```c
tp_obj tp_params(TP);
```

Initialize the parameter list for a function call. Usually you use `tp_params_n()` or `tp_params_v()` instead.

### tp_params_n — Pass Array of Parameters

```c
tp_obj tp_params_n(TP, int n, tp_obj argv[]);
```

Specify a list of objects as function call parameters.

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `n` | The number of parameters |
| `argv` | Array of n TinyPy objects to pass as parameters |

**Returns:** The parameters list. You may modify it before performing the function call.

### tp_params_v — Pass Variadic Parameters

```c
tp_obj tp_params_v(TP, int n, ...);
```

Pass parameters for a TinyPy function call using variadic arguments.

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `n` | The number of variable arguments following |
| `...` | n TinyPy objects to pass as parameters |

**Returns:** A TinyPy list object representing the current call parameters. You can modify the list before doing the function call.

## Raising Exceptions

### tp_raise — Raise Exception Macro

```c
#define tp_raise(r, fmt, ...) { \
    _tp_raise(tp, tp_printf(tp, fmt, __VA_ARGS__)); \
    return r; \
}
```

Macro to raise an exception. This macro will **return from the current function** returning `r`. The remaining parameters are used to format the exception message via `printf`-style formatting.

The macro uses `longjmp` to jump to the nearest try/except handler in the VM.

## Utility Functions & Macros

### TP_CSTR — Convert tp_obj to C String

```c
#define TP_CSTR(v) ((tp_str(tp, (v))).string.val)
```

Convert any TinyPy object to a C string by calling `tp_str()` and accessing the `.string.val` field.

### tp_ptr — Allocate Copy on Heap

```c
void *tp_ptr(tp_obj o);
```

Allocate a copy of obj on heap.

### tp_grey — Mark Object for GC

```c
void tp_grey(TP, tp_obj);
```

Mark an object as grey in the garbage collector (ready to be scanned).

### tp_track — Register GC Root

```c
tp_obj tp_track(TP, tp_obj v);
```

Register an object as a GC root so it won't be collected.

### tp_printf — Format String

```c
tp_obj tp_printf(TP, char const *fmt, ...);
```

Format a printf-style string into a TinyPy `tp_obj` string.

## Built-in Functions Available in TinyPy Scripts

| Function | Description |
|----------|-------------|
| `print(*args)` | Print values separated by spaces |
| `range([start], stop, [step])` | Return list of numbers |
| `min(*args)` / `max(*args)` | Minimum/maximum of arguments |
| `bind(func)` | Create a bound function (self = first arg) |
| `copy(obj)` | Shallow copy of list or dict |
| `len(obj)` | Length of container |
| `assert(cond)` | Raise if cond is falsy |
| `str(obj)` | String representation |
| `float(val, [base])` | Convert to number (int base for strings) |
| `int(val)` | Truncate float to integer |
| `round(val)` | Round to nearest integer |
| `abs(val)` | Absolute value |
| `system(cmd)` | Execute shell command, return exit code (**security risk**) |
| `istype(obj, type_name)` | Check type by name string |
| `chr(n)` / `ord(c)` | Character/code conversions |
| `exec(code, globals)` | Execute bytecode with given globals |
| `import(name)` | Import a module (.tpc file) |
| `save(fname, obj)` | Save binary object to file |
| `load(fname)` | Load binary object from file |
| `fpack(val)` | Pack float into bytes string |
| `merge(dict1, dict2)` | Merge dict2 into dict1 (in-place) |

## VM Constants

| Constant | Default | Description |
|----------|---------|-------------|
| `TP_GCMAX` | 4096 | GC trigger threshold |
| `TP_FRAMES` | 256 | Maximum call stack depth |
| `TP_REGS` | 16384 | Total register pool size |

## Security Warning

The `system()` builtin executes shell commands and is described in the wiki as **"a grave security flaw."** If your version of TinyPy enables this, remove it before deploying your application.
