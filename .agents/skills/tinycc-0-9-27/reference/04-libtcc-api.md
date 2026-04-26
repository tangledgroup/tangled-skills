# libtcc API Reference

The `libtcc` library enables using TCC as a backend for dynamic code generation. You give it C source strings or files, compile them at runtime, and call the resulting functions by symbol name.

## Context Management

**`TCCState *tcc_new(void)`** — Create a new TCC compilation context.

**`void tcc_delete(TCCState *s)`** — Free a TCC compilation context.

**`void tcc_set_lib_path(TCCState *s, const char *path)`** — Set CONFIG_TCCDIR at runtime (where TCC finds its internal libraries and includes).

**`void tcc_set_error_func(TCCState *s, void *error_opaque, void (*error_func)(void *opaque, const char *msg))`** — Set error/warning display callback.

**`void tcc_set_options(TCCState *s, const char *str)`** — Set options as from command line (multiple supported) (0.9.27).

## Preprocessor

**`int tcc_add_include_path(TCCState *s, const char *pathname)`** — Add an include path.

**`int tcc_add_sysinclude_path(TCCState *s, const char *pathname)`** — Add a system include path.

**`void tcc_define_symbol(TCCState *s, const char *sym, const char *value)`** — Define preprocessor symbol `sym` with optional value.

**`void tcc_undefine_symbol(TCCState *s, const char *sym)`** — Undefine preprocessor symbol `sym`.

## Compilation

**`int tcc_add_file(TCCState *s, const char *filename)`** — Add a file (C source, DLL, object, library, or ld script). Returns -1 on error.

**`int tcc_compile_string(TCCState *s, const char *buf)`** — Compile a string containing C source. Returns -1 on error.

## Linking

**`int tcc_set_output_type(TCCState *s, int output_type)`** — Set output type. **MUST be called before any compilation.**

Output types:
- `TCC_OUTPUT_MEMORY` (1) — Output will be run in memory (default)
- `TCC_OUTPUT_EXE` (2) — Executable file
- `TCC_OUTPUT_DLL` (3) — Dynamic library
- `TCC_OUTPUT_OBJ` (4) — Object file
- `TCC_OUTPUT_PREPROCESS` (5) — Only preprocess (internal use)

**`int tcc_add_library_path(TCCState *s, const char *pathname)`** — Equivalent to `-Lpath`.

**`int tcc_add_library(TCCState *s, const char *libraryname)`** — Link a library (same name as `-l` argument).

**`int tcc_add_symbol(TCCState *s, const char *name, const void *val)`** — Add a symbol to the compiled program. Used to inject host functions into dynamically compiled code.

**`int tcc_output_file(TCCState *s, const char *filename)`** — Output an executable, library, or object file. Do not call `tcc_relocate()` before this.

**`int tcc_run(TCCState *s, int argc, char **argv)`** — Link and run `main()` function, returning its value. Do not call `tcc_relocate()` before this.

## Relocation and Symbol Resolution

**`int tcc_relocate(TCCState *s, void *ptr)`** — Perform all relocations (needed before using `tcc_get_symbol()`).

Values for `ptr`:
- `TCC_RELOCATE_AUTO` — Allocate and manage memory internally
- `NULL` — Return required memory size
- Memory address — Copy code to caller-provided memory

Returns -1 on error.

**`void *tcc_get_symbol(TCCState *s, const char *name)`** — Return symbol value or NULL if not found. Returns a function pointer that can be cast and called directly.

## Typical Workflow

```
1. tcc_new()                    → create context
2. tcc_set_output_type(s, ...)  → set output type (before compilation)
3. tcc_compile_string(s, src)   → compile C source string
   or tcc_add_file(s, "file.c") → compile from file
4. tcc_add_symbol(s, name, fn)  → inject host symbols (optional)
5. tcc_relocate(s, ...)         → relocate code
6. tcc_get_symbol(s, "main")    → get function pointer
7. call the function            → execute compiled code
8. tcc_delete(s)                → cleanup
```

For file output instead of in-memory execution:

```
1. tcc_new()
2. tcc_set_output_type(s, TCC_OUTPUT_EXE)
3. tcc_add_file(s, "program.c")
4. tcc_output_file(s, "program")
5. tcc_delete(s)
```

## Complete Example

See `tests/libtcc_test.c` in the source tree for a complete example that compiles C code from a string, injects host functions and data as symbols, relocates the code, retrieves the entry function by name, executes it, and cleans up.
