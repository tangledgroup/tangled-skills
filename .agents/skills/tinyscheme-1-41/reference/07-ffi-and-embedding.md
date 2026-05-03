# FFI & Embedding API

## Contents
- Interpreter Lifecycle
- Initialization
- Loading Code
- Evaluation and Calling
- Foreign Functions
- scheme_interface Vtable
- Dynamic Loading
- C→Scheme→C Nesting

## Interpreter Lifecycle

A TinyScheme interpreter is a `scheme *` struct containing all state. Multiple independent instances can coexist:

```c
scheme *sc = scheme_init_new();
/* ... use interpreter ... */
scheme_deinit(sc);
free(sc);
```

Or with custom allocators:
```c
scheme *sc = scheme_init_new_custom_alloc(my_malloc, my_free);
```

The `scheme` struct (from `scheme-private.h`) contains:
- Allocator functions (`malloc`, `free`)
- Four registers (`args`, `envir`, `code`, `dump`)
- Cell heap segments (`alloc_seg[]`, `cell_seg[]`, `free_cell`)
- Special cells (NIL, T, F, EOF_OBJ, sink)
- Symbol table (`oblist`) and global environment
- Ports (inport, outport, loadport)
- File load stack
- Dump stack for continuations
- External data pointer for foreign functions

## Initialization

```c
int scheme_init(scheme *sc) {
 return scheme_init_custom_alloc(sc, malloc, free);
}

int scheme_init_custom_alloc(scheme *sc, func_alloc malloc, func_dealloc free) {
  /* Set up number constants */
  num_zero.is_fixnum = 1; num_zero.value.ivalue = 0;
  num_one.is_fixnum = 1;  num_one.value.ivalue = 1;

  /* Initialize special cells */
  sc->NIL = &sc->_NIL;
  sc->T = &sc->_HASHT;
  sc->F = &sc->_HASHF;
  sc->EOF_OBJ = &sc->_EOF_OBJ;
  sc->sink = &sc->_sink;

  /* Allocate initial cell segments (FIRST_CELLSEGS = 3) */
  if (alloc_cellseg(sc, FIRST_CELLSEGS) != FIRST_CELLSEGS)
    return 0;

  /* Initialize oblist and global environment */
  sc->oblist = oblist_initial_value(sc);
  new_frame_in_env(sc, sc->NIL);
  sc->global_env = sc->envir;

  /* Register syntax objects: lambda, quote, define, if, begin, set!,
     let, let*, letrec, cond, delay, and, or, cons-stream, macro, case */
  assign_syntax(sc, "lambda");
  /* ... more syntax ... */

  /* Register all built-in procedures from dispatch table */
  for (i = 0; i < n; i++)
    if (dispatch_table[i].name != 0)
      assign_proc(sc, (enum scheme_opcodes)i, dispatch_table[i].name);

  /* Initialize special symbols: LAMBDA, QUOTE, QQUOTE, UNQUOTE, etc. */
  sc->LAMBDA = mk_symbol(sc, "lambda");
  /* ... more symbols ... */

  return !sc->no_memory;
}
```

Initialization creates 3 cell segments (15000 cells), sets up the global environment with all built-in procedures and syntax objects, and initializes special symbols.

## Loading Code

Two ways to load Scheme code:

```c
void scheme_load_file(scheme *sc, FILE *fin);
void scheme_load_named_file(scheme *sc, FILE *fin, const char *filename);
void scheme_load_string(scheme *sc, const char *cmd);
```

`scheme_load_file()` sets up a load port from the FILE*, enters `Eval_Cycle` from `OP_T0LVL`, and runs until EOF or error. `scheme_load_string()` does the same with an in-memory string buffer.

Typical embedding pattern:
```c
scheme *sc = scheme_init_new();
scheme_set_input_port_file(sc, stdin);
scheme_set_output_port_file(sc, stdout);

FILE *init = fopen("init.scm", "r");
scheme_load_file(sc, init);
fclose(init);

/* Now the interpreter has all library functions loaded */
```

`init.scm` (~1200 lines) provides Scheme-level utilities: car/cdr compositions, macro system, exception handling, module emulation, packages, streams, vector/string helpers.

## Evaluation and Calling

```c
pointer scheme_eval(scheme *sc, pointer obj);
pointer scheme_call(scheme *sc, pointer func, pointer args);
pointer scheme_apply0(scheme *sc, const char *procname);
```

`scheme_eval()` evaluates a Scheme expression (must already be a parsed cell):
```c
pointer scheme_eval(scheme *sc, pointer obj) {
  save_from_C_call(sc);       /* Save current C context */
  sc->envir = sc->global_env;
  sc->args = sc->NIL;
  sc->code = obj;
  Eval_Cycle(sc, OP_EVAL);
  restore_from_C_call(sc);    /* Restore C context */
  return sc->value;
}
```

`scheme_call()` applies a function to arguments:
```c
pointer scheme_call(scheme *sc, pointer func, pointer args) {
  save_from_C_call(sc);
  sc->envir = sc->global_env;
  sc->args = args;
  sc->code = func;
  Eval_Cycle(sc, OP_APPLY);
  restore_from_C_call(sc);
  return sc->value;
}
```

`scheme_apply0()` calls a named procedure with no arguments:
```c
pointer scheme_apply0(scheme *sc, const char *procname) {
  return scheme_eval(sc, cons(sc, mk_symbol(sc, procname), sc->NIL));
}
```

## Foreign Functions

Foreign functions are C functions with this signature:

```c
typedef pointer (*foreign_func)(scheme *sc, pointer args);
```

They receive the interpreter state and a Scheme list of arguments. They return a Scheme value.

Example — square function:
```c
pointer square(scheme *sc, pointer args) {
    if (args != sc->NIL && is_number(pair_car(args))) {
        double v = rvalue(pair_car(args));
        return mk_real(sc, v * v);
    }
    return sc->NIL;
}
```

Register in the global environment:
```c
scheme_define(sc, sc->global_env,
              mk_symbol(sc, "square"),
              mk_foreign_func(sc, square));

/* Or batch register: */
scheme_registerable funcs[] = {
    { square, "square" },
    { another_func, "another" }
};
scheme_register_foreign_func_list(sc, funcs, 2);
```

When called, foreign functions go through `OP_APPLY`:
```c
if (is_foreign(sc->code)) {
    push_recent_alloc(sc, sc->args, sc->NIL);  /* Protect args from GC */
    x = sc->code->_object._ff(sc, sc->args);
    s_return(sc, x);
}
```

## scheme_interface Vtable

When `USE_INTERFACE=1`, the `scheme` struct contains a `struct scheme_interface *vptr` with 50+ function pointers. Foreign functions in DLLs use this to manipulate Scheme data without accessing internal fields directly:

```c
struct scheme_interface {
  /* Constructors */
  pointer (*cons)(scheme *sc, pointer a, pointer b);
  pointer (*mk_integer)(scheme *sc, int64_t num);
  pointer (*mk_real)(scheme *sc, double num);
  pointer (*mk_symbol)(scheme *sc, const char *name);
  pointer (*mk_string)(scheme *sc, const char *str);
  pointer (*mk_character)(scheme *sc, int c);
  pointer (*mk_vector)(scheme *sc, int len);
  pointer (*mk_foreign_func)(scheme *sc, foreign_func f);

  /* Type predicates */
  int (*is_string)(pointer p);
  int (*is_number)(pointer p);
  int (*is_integer)(pointer p);
  int (*is_character)(pointer p);
  int (*is_list)(scheme *sc, pointer p);
  int (*is_pair)(pointer p);
  /* ... more predicates ... */

  /* Accessors */
  char *(*string_value)(pointer p);
  int64_t (*ivalue)(pointer p);
  double (*rvalue)(pointer p);
  pointer (*pair_car)(pointer p);
  pointer (*pair_cdr)(pointer p);
  char *(*symname)(pointer p);
  /* ... more accessors ... */

  /* I/O */
  void (*putstr)(scheme *sc, const char *s);
  void (*load_file)(scheme *sc, FILE *fin);
  void (*load_string)(scheme *sc, const char *input);
};
```

Usage in foreign functions:
```c
pointer my_func(scheme *sc, pointer args) {
    int a = sc->vptr->ivalue(sc->vptr->pair_car(args));
    return sc->vptr->mk_integer(sc, a * 2);
}
```

## Dynamic Loading

`dynload.c` provides platform-agnostic dynamic library loading:

- **Unix/Linux**: `dlopen()` / `dlsym()` / `dlclose()`
- **Windows**: `LoadLibrary()` / `GetProcAddress()` / `FreeLibrary()`

The `load-extension` procedure is registered during init:
```c
scheme_define(sc, sc->global_env,
              mk_symbol(sc, "load-extension"),
              mk_foreign_func(sc, scm_load_ext));
```

Usage from Scheme:
```scheme
(load-extension "my-module")  ; loads libmy-module.so or my-module.dll
```

The loader constructs the filename (`lib` + name + `.so` on Unix, name + `.dll` on Windows), loads it, then looks for an `init_<name>` function and calls it with the interpreter state. The init function should register any foreign functions:

```c
void init_my_module(scheme *sc) {
    scheme_define(sc, sc->global_env,
                  mk_symbol(sc, "my-func"),
                  mk_foreign_func(sc, my_func));
}
```

## C→Scheme→C Nesting

When C calls into Scheme and Scheme calls back into C (via foreign functions), the interpreter must preserve the C caller's state. This is handled by the `c_nest` stack:

```c
void save_from_C_call(scheme *sc) {
  pointer saved_data = cons(sc,
         car(sc->sink),
         cons(sc, sc->envir, sc->dump));
  sc->c_nest = cons(sc, saved_data, sc->c_nest);
  dump_stack_reset(sc);  /* Truncate dump so TS returns here */
}

void restore_from_C_call(scheme *sc) {
  car(sc->sink) = caar(sc->c_nest);
  sc->envir = cadar(sc->c_nest);
  sc->dump = cdr(cdar(sc->c_nest));
  sc->c_nest = cdr(sc->c_nest);  /* Pop */
}
```

`save_from_C_call()` is called at the start of `scheme_eval()` and `scheme_call()`. It saves the current registers and dump stack, then resets the dump so that when Scheme finishes, control returns to the C caller rather than resuming some deeper Scheme continuation.

## External Data

Foreign functions can store per-interpreter state:

```c
void scheme_set_external_data(scheme *sc, void *p);
```

The pointer is stored in `sc->ext_data` and accessible from any foreign function sharing the same interpreter instance. This enables maintaining connection pools, configuration state, or other context without global variables.
