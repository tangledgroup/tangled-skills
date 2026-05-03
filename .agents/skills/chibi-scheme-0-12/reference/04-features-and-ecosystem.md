# Features And Ecosystem

## Contents
- Numeric Tower
- Unicode And Strings
- Green Threads
- Image Files
- Static Builds
- Compile-Time Features
- Standard Modules
- SRFI Support
- Snow Package Manager

## Numeric Tower

Chibi includes the complete numeric tower by default:

- **Fixnums** — immediate integers stored in the pointer tag (up to 2^62 on 64-bit)
- **Flonums** — IEEE 754 doubles, optionally stored as immediate values
- **Bignums** — arbitrary precision integers using GMP-style digit arrays
- **Ratios** — exact rational numbers (numerator/denominator as bignums)
- **Complex** — rectangular complex numbers with real and imaginary parts

All five types interoperate seamlessly. Operations promote to the widest type needed: `(+ 1 2.0)` returns a flonum, `(/ 1 3)` returns a ratio. Disable any layer at compile time via `SEXP_USE_BIGNUMS`, `SEXP_USE_FLONUMS`, `SEXP_USE_RATIOS`, `SEXP_USE_COMPLEX`.

## Unicode And Strings

Strings are UTF-8 encoded internally, providing direct interoperability with C libraries that use UTF-8.

**Performance caveat:** `string-ref` and `string-set!` are O(n) because they must decode UTF-8 sequences from the start. For performance-sensitive code:

- Use high-level APIs like `string-map` which iterate efficiently
- Use string ports for character-by-character processing
- Use **string cursors** for low-level byte-offset access:

```scheme
(import (srfi 130))
(let ((cs (string-cursor-start str)))
  (loop ()
    (when (string-cursor=? cs (string-cursor-end str)) (return))
    (display (string-cursor-ref str cs))
    (loop (string-cursor-next str cs))))
```

Cursors track raw byte offsets, not character indices. `string-cursor-next`/`string-cursor-prev` advance by one UTF-8 character. `(chibi loop)` provides `in-string` and `in-string-reverse` iterators that hide cursor details.

Compile with `SEXP_USE_STRING_INDEX_TABLE=1` to precompute character offsets for O(1) `string-ref`.

## Green Threads

Chibi supports lightweight VM threads (SRFI-18). Each green thread has its own context and evaluation stack within a single OS thread. The scheduler cooperatively yields at I/O operations and explicit `thread-yield` calls.

Green threads share the heap but have isolated execution state. Port I/O is multiplexed using `poll`/`select`. Thread synchronization uses mutexes, condition variables, and barriers from SRFI-18.

**Limitation:** continuations that cross C call boundaries may not behave correctly with green threads. The result of invoking a continuation created by a different thread is unspecified.

## Image Files

Chibi supports image files — serialized snapshots of the heap containing compiled modules and environments. This dramatically reduces startup time for applications that load many modules.

Create an image by saving the heap after loading desired modules. Load with `-i <image-file>`. The `snow-chibi` package manager uses images by default (disable with `--noimage`).

## Static Builds

Build a fully static executable with all Scheme libraries baked in:

```bash
make clibs.c                        # generate C source for all standard libs
make chibi-scheme-static SEXP_USE_DL=0 \
  CPPFLAGS="-DSEXP_USE_STATIC_LIBS -DSEXP_USE_STATIC_LIBS_NO_INCLUDE=0"
```

The static build cannot load external shared libraries (`SEXP_USE_DL=0`). Use the `(chibi)` language instead of `(scheme base)` since the latter requires dynamic loading.

## Compile-Time Features

Edit `chibi/features.h` or pass CPPFLAGS to control which features are compiled in:

- `SEXP_USE_BOEHM` — Boehm conservative GC instead of precise
- `SEXP_USE_DL` — dynamic linking support (default on)
- `SEXP_USE_STATIC_LIBS` — compile standard C libs statically
- `SEXP_USE_MODULES` — module system
- `SEXP_USE_GREEN_THREADS` — lightweight threads (default on)
- `SEXP_USE_SIMPLIFY` — bytecode simplification optimizer (default on)
- `SEXP_USE_BIGNUMS/FLONUMS/RATIOS/COMPLEX` — numeric tower layers
- `SEXP_USE_UTF8_STRINGS` — Unicode support (default on)
- `SEXP_USE_STRING_INDEX_TABLE` — O(1) string-ref
- `SEXP_USE_NO_FEATURES` — disable almost everything (minimal build)

## Standard Modules

Non-standard modules live in the `(chibi *)` namespace:

- **`(chibi net)`** — sockets, TCP/UDP networking
- **`(chibi net http-server)`** — simple HTTP server with servlet support
- **`(chibi json)`** — JSON read/write
- **`(chibi filesystem)`** — file operations, file descriptor objects
- **`(chibi process)`** — spawn processes, signal handling
- **`(chibi match)`** — pattern matching syntax
- **`(chibi parse)`** — parser combinators
- **`(chibi loop)`** — extensible loop syntax (like Clojure's `clojure.core/loop`)
- **`(chibi io)`** — custom ports, I/O extensions
- **`(chibi config)`** — configuration file management
- **`(chibi crypto sha2/md5)`** — SHA-2 and MD5 hashing
- **`(chibi time)`** — system time interface
- **`(chibi csv)`** — CSV parsing/formatting
- **`(chibi diff)`** — LCS algorithm, diff utilities
- **`(chibi generic)`** — CLOS-style generic methods

## SRFI Support

Built-in (no import needed): SRFI 0 (cond-expand), 6 (string ports), 23 (error), 46 (syntax-rules extensions), 62 (s-expression comments).

Loadable SRFIs include: 1 (lists), 8 (receive), 9/99 (records), 11 (let-values), 14 (character sets), 16 (case-lambda), 18 (threads), 26 (cut/cute), 33 (bitwise), 39 (parameters), 41 (streams), 64 (test suites), 69/125 (hash tables), 95 (sorting), 115 (regexps), 130 (cursor strings), 143 (fixnums), 144 (flonums), 193 (command-line), and many more.

## Snow Package Manager

`snow-chibi` is a package manager based on the Snow2 spec. Packages are distributed as `.tgz` "snowballs" containing R7RS libraries.

**Key commands:**

- `snow-chibi search <terms>` — search repository
- `snow-chibi install <names>` — install packages
- `snow-chibi show chibi.match` — dotted shorthand for `(chibi match)`
- `snow-chibi package <files>` — create a package from library files
- `snow-chibi upload <files>` — sign and upload to repository

Configuration in `$HOME/.snow/config.scm` (an alist, not evaluated code). Supports multiple Scheme implementations: Chicken, Gambit, Guile, Racket, Sagittarius, and others.
