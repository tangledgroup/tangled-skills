# Conditional Compilation & Library

## Contents
- Feature Flags
- Build Targets
- init.scm Architecture
- Module System Emulation
- JSON Parser
- Utility Libraries

## Feature Flags

All feature flags default to enabled in `scheme.h` and can be overridden via compiler `-D` flags. Setting a flag to `0` disables the feature; `1` enables it.

### USE_NO_FEATURES

Master disable switch. When defined, sets all of the following to 0:
- USE_MATH, USE_CHAR_CLASSIFIERS, USE_ASCII_NAMES, USE_STRING_PORTS
- USE_ERROR_HOOK, USE_TRACING, USE_COLON_HOOK, USE_DL, USE_PLIST

Produces a minimal build (~64KB object file on Linux).

### USE_MATH (default: 1)

Enables transcendental math functions: `exp`, `log`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sqrt`, `expt`, `floor`, `ceiling`, `truncate`, `round`. Requires linking with `-lm`.

### USE_CHAR_CLASSIFIERS (default: 1)

Enables character classification predicates: `char-alphabetic?`, `char-numeric?`, `char-whitespace?`, `char-upper-case?`, `char-lower-case?`. Uses `isascii()` + standard `ctype.h` functions.

### USE_ASCII_NAMES (default: 1)

Enables named control characters in `#\` notation: `#\nul`, `#\soh`, `#\stx`, ..., `#\del`. 33 named characters covering codes 0-31 and 127.

### USE_STRING_PORTS (default: 1)

Enables string I/O ports: `open-input-string`, `open-output-string`, `get-output-string`, `open-input-output-string`. Output strings auto-reallocate in 256-byte blocks (SRFI-6 compatible).

### USE_ERROR_HOOK (default: 1)

Enables `*error-hook*` — a user-defined error handler. When defined, system errors call the hook procedure instead of printing directly. Enables the `catch`/`throw` exception mechanism in init.scm.

### USE_TRACING (default: 1)

Enables `(tracing 1)` / `(tracing 0)` for debugging. Prints "Eval:" and "Apply to:" messages before each evaluation and application step.

### USE_COLON_HOOK (default: 1)

Enables `::` qualified identifier syntax: `env::symbol` transforms to `(*colon-hook* 'symbol env)`. Used by the package system in init.scm. Disabling this breaks any code using packages.

### USE_DL (default: 1)

Enables dynamic library loading via `load-extension`. Requires `dynload.c` in the build. Uses `dlopen`/`LoadLibrary` depending on platform.

### USE_PLIST (default: 1)

Enables property lists inherited from MiniScheme: `(put symbol key value)` and `(get symbol key)`. Not part of R5RS. Stored in the cdr field of symbol cells (which are conses).

### USE_SCHEME_STACK

When defined, uses Scheme cons cells for the dump stack instead of a C array. Required for proper continuation support with `call/cc`. When undefined, continuations don't work correctly but execution is faster.

### USE_MACRO (default: 1)

Enables macro support via `*compile-hook*`. Macros are closures with the `T_MACRO` flag, expanded during argument evaluation.

### STANDALONE (default: 0)

When 1, produces a standalone interpreter executable. When 0, builds as a library for embedding.

### USE_INTERFACE (default: 1)

Enables the `scheme_interface` vtable for foreign function access. Auto-enabled when USE_DL is on.

### SHOW_ERROR_LINE (default: 1)

Includes filename and line number in error messages. Tracks line numbers during reading.

## Build Targets

### Makefile (misc/makefile)

```makefile
CC = gcc -fpic -pedantic
DEBUG = -g -Wno-char-subscripts -O
FEATURES = -DSUN_DL=1 -DUSE_DL=1 -DUSE_MATH=1 -DUSE_ASCII_NAMES=0

# Targets:
all: libtinyscheme.so libtinyscheme.a scheme
```

Produces shared library, static library, and standalone executable. Platform sections for Windows, Cygwin, MinGW, Mac OS X, Solaris.

### CMakeLists.txt

```cmake
add_library(tinyscheme_static STATIC source/scheme.c source/dynload.c)
add_library(tinyscheme SHARED source/scheme.c source/dynload.c)
add_executable(tinyscheme_repl test/repl.c source/dynload.c)
add_executable(tinyscheme_test test/test.c)
```

Cross-platform CMake build. Links `-ldl -lm` on Unix, threads library everywhere.

### Footprint Tuning

- Full features: ~120KB object file
- `USE_NO_FEATURES`: ~64KB object file
- With `USE_SCHEME_STACK` undefined: faster but no continuations
- With hash table oblist disabled (`USE_OBJECT_LIST`): simpler but O(n) symbol lookup

## init.scm Architecture

The Scheme-level library (~1200 lines) provides functionality not in the C core:

### Car/Cdr Compositions (64 functions)

All combinations of car/cdr up to 4 deep: `caar`, `cadr`, `cdar`, `cddr`, ..., `cddddr`. Defined as simple lambdas in init.scm. The C code defines macros for internal use (`#define caar(p) car(car(p))`).

### Macro System

```scheme
(define *compile-hook* macro-expand-all)

(define (macro-expand form)
  ((eval (get-closure-code (eval (car form)))) form))

(define (macro-expand-all form)
  (if (macro? form)
      (macro-expand-all (macro-expand form))
      form))
```

Every lambda body is passed through `*compile-hook*` during closure creation. The default hook recursively expands macros. User-defined macros are registered via the `macro` special form (OP_MACRO0/OP_MACRO1), which creates a closure with `T_MACRO` flag.

### Exception Handling (catch/throw)

```scheme
(define-macro (catch exception-val . body)
  `(let ((,hook-save *error-hook*))
     (dynamic-wind
       (lambda () (set! *error-hook* throw))
       (lambda () ,@body)
       (lambda () (set! *error-hook* ,hook-save)))))

(define (throw msg)
  (call/cc (lambda (k)
             (set! *current-exception* k)
             (error msg))))
```

Establishes a scope where `*error-hook*` is set to `throw`. When an error occurs, it calls the hook which captures the continuation and transfers control.

### Package System

```scheme
(define-macro (package form)
  `(apply (lambda () ,@(cdr form) (current-environment))))
```

Creates a local environment containing the defined bindings. Combined with `*colon-hook*` (default: `eval`), enables qualified access: `env::symbol`.

### Stream Utilities

`head`, `tail`, `cons-stream` — lazy stream operations using promises (delay/force).

### Vector and String Helpers

`list->vector`, `vector->list`, `vector-fill!`, `string`, `list->string`, `string->list`, `string-fill!`, `string-copy`, comparison predicates (`string=?`, etc.).

### Math Utilities

`gcd`, `lcm`, `exact?`, `inexact?`, `odd?`, `even?`, `zero?`, `positive?`, `negative?`, `exact->inexact`.

### I/O Wrappers

`call-with-input-file`, `call-with-output-file`, `with-input-from-file`, `with-output-to-file`, `close-port`, `input-output-port?`.

## Module System Emulation

`t
inymodules.scm` provides Chicken-Scheme-style module emulation:

```scheme
(define-macro (module name exports . forms)
  `(begin
    (define ,name
       (apply (lambda () ,@forms (current-environment))))
    ,@(map (lambda (v) `(define ,v (eval (quote ,v) ,name))) exports)))

(define-macro (import module-name)
  `(load (string-append module-default-path
                        (symbol->string (quote ,module-name))
                        ".scm")))
```

`(module test (a c) (define a 42) (define b 43) (define c 44))` creates an environment with `a` and `c` exported to the current namespace, `b` remaining private.

## JSON Parser

`json.scm` implements a recursive descent JSON parser as a module:

```scheme
(module json (json/parse json/parse-string json/parse-file json/gen-string))
```

Uses a character-based lexer (`next-token`) with state tracking for strings, numbers, booleans, and structural tokens. The parser handles maps (`{}`), lists (`[]`), strings, numbers, `true`/`false`/`null`. Output is Scheme S-expressions: `'(map (key1 val1) (key2 val2))`.

## Utility Libraries

`utils.scm` provides:
- `reduce` — left-fold over a list with accumulator
- `partial` — partial function application
- `hash-map` / `hash-get` — alist-based hash map operations
- `with-input-from-string` — redirect input port to a string
- `print` / `println` — convenience output functions

`params.scm` provides JSON parameter marshalling with setter/getter dispatch:
- `read-from-json` — transfer JSON data to C target via setter functions
- `write-to-json` — transfer C target state to JSON via getter functions

## start-tiny.scm

The REPL startup script loads the library chain:
```scheme
(load "libs/init.scm")
(load "libs/tinymodules.scm")
(load "libs/utils.scm")
```

The `TINYSCHEMEINIT` environment variable can override the init file path.
