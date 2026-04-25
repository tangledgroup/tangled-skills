# libtcc API Reference

The `libtcc` library enables using TCC as a backend for dynamic code generation. Include `libtcc.h` from the TCC source tree.

## Overview

The idea is to give a C string containing the program you want to compile directly to `libtcc`, then access any global symbol (function or variable) defined in it.

## API Functions

### Core Lifecycle

```c
TCCState *tcc_new(void);              /* Create new compilation context */
void tcc_delete(TCCState *s);          /* Free compilation context */
```

### Configuration

```c
void tcc_set_lib_path(TCCState *s, const char *path);
/* Set CONFIG_TCCDIR at runtime (where tcclib.h and libtcc1.a live) */

void tcc_set_error_func(TCCState *s, void *error_opaque,
    void (*error_func)(void *opaque, const char *msg));
/* Set error/warning display callback */

void tcc_set_options(TCCState *s, const char *str);
/* Set options as from command line (multiple supported) */
```

### Preprocessor API

```c
int tcc_add_include_path(TCCState *s, const char *pathname);
/* Add include path (equivalent to -Idir) */

int tcc_add_sysinclude_path(TCCState *s, const char *pathname);
/* Add system include path */

void tcc_define_symbol(TCCState *s, const char *sym, const char *value);
/* Define preprocessor symbol (equivalent to -D) */

void tcc_undefine_symbol(TCCState *s, const char *sym);
/* Undefine preprocessor symbol (equivalent to -U) */
```

### Compiling

```c
int tcc_add_file(TCCState *s, const char *filename);
/* Add a file: C file, DLL, object, library, or ld script. Returns -1 on error. */

int tcc_compile_string(TCCState *s, const char *buf);
/* Compile a string containing C source. Returns -1 on error. */
```

### Linking Commands

```c
int tcc_set_output_type(TCCState *s, int output_type);
/* MUST be called before any compilation! */
```

Output types:

| Constant | Value | Description |
|----------|-------|-------------|
| `TCC_OUTPUT_MEMORY` | 1 | Output will be run in memory (default) |
| `TCC_OUTPUT_EXE` | 2 | Executable file |
| `TCC_OUTPUT_DLL` | 3 | Dynamic library |
| `TCC_OUTPUT_OBJ` | 4 | Object file |
| `TCC_OUTPUT_PREPROCESS` | 5 | Only preprocess (used internally) |

```c
int tcc_add_library_path(TCCState *s, const char *pathname);
/* Equivalent to -Lpath option */

int tcc_add_library(TCCState *s, const char *libraryname);
/* Add library (same as -l option, without 'lib' prefix or '.so' suffix) */

int tcc_add_symbol(TCCState *s, const char *name, const void *val);
/* Add a symbol to the compiled program */

int tcc_output_file(TCCState *s, const char *filename);
/* Output an executable, library, or object file. DO NOT call tcc_relocate() before. */

int tcc_run(TCCState *s, int argc, char **argv);
/* Link and run main(), return its value. DO NOT call tcc_relocate() before. */
```

### Relocation and Symbol Access

```c
int tcc_relocate(TCCState *s1, void *ptr);
/* Do all relocations (needed before using tcc_get_symbol()) */
```

Possible values for `ptr`:

| Value | Description |
|-------|-------------|
| `TCC_RELOCATE_AUTO` | Allocate and manage memory internally |
| `NULL` | Return required memory size |
| memory address | Copy code to memory passed by caller |

Returns -1 on error.

```c
#define TCC_RELOCATE_AUTO (void*)1

void *tcc_get_symbol(TCCState *s, const char *name);
/* Return symbol value or NULL if not found */
```

## Complete Example

```c
#include <stdlib.h>
#include <stdio.h>
#include "libtcc.h"

/* Function available to generated code */
int add(int a, int b) {
    return a + b;
}

const char hello[] = "Hello World!";

char my_program[] =
    "#include <tcclib.h>\n"
    "extern int add(int a, int b);\n"
#ifdef _WIN32
    " __attribute__((dllimport))\n"
#endif
    "extern const char hello[];\n"
    "int fib(int n)\n"
    "{\n"
    "    if (n <= 2) return 1;\n"
    "    else return fib(n-1) + fib(n-2);\n"
    "}\n"
    "int foo(int n)\n"
    "{\n"
    "    printf(\"%s\\n\", hello);\n"
    "    printf(\"fib(%d) = %d\\n\", n, fib(n));\n"
    "    printf(\"add(%d, %d) = %d\\n\", n, 2*n, add(n, 2*n));\n"
    "    return 0;\n"
    "}\n";

int main(int argc, char **argv)
{
    TCCState *s;
    int i;
    int (*func)(int);

    s = tcc_new();
    if (!s) {
        fprintf(stderr, "Could not create tcc state\n");
        exit(1);
    }

    /* Optional: set paths for tcclib.h and libtcc1.a */
    for (i = 1; i < argc; ++i) {
        char *a = argv[i];
        if (a[0] == '-') {
            if (a[1] == 'B')
                tcc_set_lib_path(s, a+2);
            else if (a[1] == 'I')
                tcc_add_include_path(s, a+2);
            else if (a[1] == 'L')
                tcc_add_library_path(s, a+2);
        }
    }

    /* MUST BE CALLED before any compilation */
    tcc_set_output_type(s, TCC_OUTPUT_MEMORY);

    if (tcc_compile_string(s, my_program) == -1) {
        fprintf(stderr, "Compilation error\n");
        tcc_delete(s);
        return 1;
    }

    /* Add symbols that the compiled program can use */
    tcc_add_symbol(s, "add", add);
    tcc_add_symbol(s, "hello", hello);

    /* Relocate the code */
    if (tcc_relocate(s, TCC_RELOCATE_AUTO) < 0) {
        fprintf(stderr, "Relocation error\n");
        tcc_delete(s);
        return 1;
    }

    /* Get entry symbol */
    func = (int (*)(int))tcc_get_symbol(s, "foo");
    if (!func) {
        fprintf(stderr, "Symbol not found: foo\n");
        tcc_delete(s);
        return 1;
    }

    /* Run the code */
    func(32);

    /* Cleanup */
    tcc_delete(s);
    return 0;
}
```

## Using libtcc with File Output

Instead of running in memory, you can write to files:

```c
TCCState *s = tcc_new();
tcc_set_output_type(s, TCC_OUTPUT_EXE);  /* or TCC_OUTPUT_DLL, TCC_OUTPUT_OBJ */
tcc_compile_string(s, source_code);
tcc_add_library(s, "m");                 /* link libm */
tcc_output_file(s, "output_program");    /* write executable */
tcc_delete(s);
/* Execute output_program separately */
```

## Using libtcc with Custom Memory Allocation

```c
TCCState *s = tcc_new();
tcc_set_output_type(s, TCC_OUTPUT_MEMORY);
tcc_compile_string(s, source_code);

/* Get required memory size */
int size = tcc_relocate(s, NULL);

/* Allocate your own memory */
void *mem = malloc(size);

/* Copy code to your memory */
tcc_relocate(s, mem);

/* Use symbols */
void (*func)() = tcc_get_symbol(s, "main");
func();

/* Cleanup */
free(mem);
tcc_delete(s);
```

## Important Notes

1. **`tcc_set_output_type()` must be called before any compilation** — this is a strict requirement
2. **`tcc_relocate()` must be called before `tcc_get_symbol()`** for in-memory execution
3. **`tcc_run()` and `tcc_output_file()` should NOT be called after `tcc_relocate()`** — they call relocate internally
4. **Bounds checking (`-b`) is only available on i386 when using libtcc**
5. **Dynamic libraries from TCC are not PIC** — the code cannot be shared among processes
6. **`libtcc1.a`** provides runtime support (e.g., floating point helpers). It must be accessible via `tcc_set_lib_path()` or the default search path
