# C API Reference

## VM Lifecycle

### tp_init

```c
tp_vm *tp_init(int argc, char *argv[])
```

Initializes a new virtual machine. Parameters have the same format as `main()`, allowing passing arguments to tinypy scripts via `ARGV`. Returns the newly created tinypy instance.

### tp_deinit

```c
void tp_deinit(TP)
```

Destroys a VM instance, freeing all memory used by it. Call this on shutdown even for single-instance applications.

### tp_call

```c
tp_obj tp_call(TP, const char *mod, const char *fnc, tp_obj params)
```

Calls a tinypy function by module and function name with given parameters.

Example: call global "foo" with string "hello":

```c
tp_call(tp, "BUILTINS", "foo", tp_params_v(tp, 1, tp_string("hello")));
```

### tp_exec

```c
tp_obj tp_exec(TP, tp_obj code, tp_obj globals)
```

Execute compiled bytecode in the given global namespace.

### tp_compile

```c
tp_obj tp_compile(TP, tp_obj text, tp_obj fname)
```

Compile tinypy source text to bytecode. Returns a bytecode object.

### tp_eval

```c
tp_obj tp_eval(TP, char *text, tp_obj globals)
```

Evaluate a string of tinypy code directly (compile + exec).

### tp_import

```c
tp_obj tp_import(TP, char const *fname, char const *name, void *codes)
```

Imports a module. If `codes` is provided, `fname` is ignored. Returns the module object.

## Object Construction

### tp_number

```c
tp_inline static tp_obj tp_number(tp_num v)
```

Creates a new numeric object (double).

### tp_string

```c
tp_inline static tp_obj tp_string(char const *v)
```

Creates a string from a C string. Only keeps a reference — ensure the source does not go out of scope. For managed storage, use `tp_string_slice` or `tp_printf`.

### tp_string_n

```c
tp_inline static tp_obj tp_string_n(char const *v, int n)
```

Creates a string from a C string with explicit length `n`.

### tp_string_slice

```c
tp_obj tp_string_slice(TP, tp_obj s, int a, int b)
```

Creates a new string sliced from an existing string. Unlike `tp_string`, makes its own copy — storage is always managed by tinypy. Safe to use with stack-allocated buffers:

```c
tp_obj foo(void) {
    char test[4] = "foo";
    return tp_string_slice(tp_string(test), 0, 3);
}
```

### tp_printf

```c
tp_obj tp_printf(TP, char const *fmt, ...)
```

Format a string (like `sprintf`) and return a tinypy string object with managed storage.

### tp_dict

```c
tp_obj tp_dict(TP)
```

Creates a new empty dictionary.

### tp_list

```c
tp_obj tp_list(TP)
```

Creates a new empty list.

### tp_fnc

```c
tp_obj tp_fnc(TP, tp_obj v(TP))
```

Creates a tinypy function object that calls the provided C function when invoked from script.

### tp_data

```c
tp_obj tp_data(TP, int magic, void *v)
```

Creates a new data object with a user-provided pointer and magic number for type identification. Set `data.info->free` to a callback for cleanup:

```c
void __free__(TP, tp_obj self) {
    free(self.data.val);
}
tp_obj my_obj = tp_data(TP, 0, my_ptr);
my_obj.data.info->free = __free__;
```

## Object Operations

### tp_get / tp_set

```c
tp_obj tp_get(TP, tp_obj self, tp_obj k)
void tp_set(TP, tp_obj self, tp_obj k, tp_obj v)
```

Attribute lookup and modification. Equivalent to `self[k]` and `self[k] = v`. Works for dicts (including classes/objects), lists, and strings.

Special case: `tp_get(list, None)` pops the first element from the list.

### tp_has

```c
tp_obj tp_has(TP, tp_obj self, tp_obj k)
```

Returns `tp_True` if `self[k]` exists, `tp_False` otherwise.

### tp_del

```c
void tp_del(TP, tp_obj self, tp_obj k)
```

Removes key `k` from dict `self`. Works on classes and objects too. Does not work on list items.

### tp_iget

```c
int tp_iget(TP, tp_obj *r, tp_obj self, tp_obj k)
```

Failsafe attribute lookup — returns 0 (false) if the key does not exist, otherwise stores the value in `*r` and returns 1.

### tp_len

```c
tp_obj tp_len(TP, tp_obj self)
```

Returns the length of a list, dict, or string.

### tp_str

```c
tp_obj tp_str(TP, tp_obj self)
```

Returns a string representation of any object.

### tp_bool

```c
int tp_bool(TP, tp_obj v)
```

Check truth value: false for 0, None, empty string/list/dict; true otherwise.

### tp_iter

```c
tp_obj tp_iter(TP, tp_obj self, tp_obj k)
```

Iterate through list/string elements or dict keys. Pass index 0 first, incrementing by 1 each call, up to `len(self) - 1`. For dicts, order is not guaranteed.

## Parameter Handling

### tp_params

```c
tp_obj tp_params(TP)
```

Initialize the parameter list for a function call. Usually use `tp_params_n` or `tp_params_v` instead.

### tp_params_n

```c
tp_obj tp_params_n(TP, int n, tp_obj argv[])
```

Pass an array of `n` tinypy objects as parameters.

### tp_params_v

```c
tp_obj tp_params_v(TP, int n, ...)
```

Pass `n` variable arguments as parameters:

```c
tp_params_v(tp, 3, tp_string("a"), tp_number(1), tp_None);
```

## Macros

### TP_OBJ()

```c
#define TP_OBJ() (tp_get(tp, tp->params, tp_None))
```

Retrieve the next parameter from the current function call's parameter list.

### TP_LOOP / TP_END

```c
#define TP_LOOP(e) ...
#define TP_END ...
```

Iterate over all remaining arguments after retrieving some normally:

```c
tp_obj my_func(TP) {
    tp_obj first = TP_OBJ();
    tp_obj arg;
    TP_LOOP(arg)
        /* process arg */
    TP_END
}
```

### tp_raise

```c
#define tp_raise(r, fmt, ...)
```

Raise an exception and return value `r` from the current function. Format string and arguments create the exception message.

### tp_True / tp_False

```c
#define tp_True  tp_number(1)
#define tp_False tp_number(0)
```

Boolean constants.

## Key Data Structures

### tp_obj

Union representing all tinypy values. The `type` field determines which sub-structure is valid:

- `tp.number.val` — double value (TP_NUMBER)
- `tp.string.val`, `tp.string.len` — string data and length (TP_STRING)
- `tp.dict.val` — pointer to `_tp_dict` (TP_DICT)
- `tp.list.val` — pointer to `_tp_list` (TP_LIST)
- `tp.fnc.info`, `tp.fnc.ftype`, `tp.fnc.val` — function data (TP_FNC)
- `tp.data.info`, `tp.data.val`, `tp.data.magic` — custom data (TP_DATA)

### tp_vm

The virtual machine instance containing:

- `builtins` — dictionary of builtin objects
- `modules` — dictionary of loaded modules
- `params` — current function call parameters
- `frames[]` — array of call frames
- `cur` — index of currently executing frame
- `frames[n].globals` — global symbols in frame n

## Builtin C Functions

### tp_class / tp_object / tp_setmeta / tp_getraw

These are tinypy-level builtins accessible from script:

- `tp_class(TP)` — Creates a new base class
- `tp_object(TP)` — Creates a new object (use `tp_setmeta` to assign class)
- `tp_setmeta(TP)` — Sets a dict's meta dictionary (for inheritance)
- `tp_getraw(TP)` — Retrieves the raw dict without meta lookup

### tp_system

```c
tp_obj tp_system(TP)
```

Executes a system command. Considered a security risk — remove before deploying applications.
