# Small Fast S-Expression Library (sfsexp) in C/C++

## Contents
- Overview
- Data Structure
- Core API
- Parsing Approaches
- Internal Representation
- Build System

## Overview

Production-quality C/C++ library for parsing, creating, modifying, and serializing s-expressions. Designed for efficiency and simplicity. Used as the data protocol for the Supermon high-speed cluster monitoring system (LANL). Supports continuation-based parsing for multiple streams and limited-memory mode for embedded systems.

## Data Structure

Single opaque type:

```c
typedef struct sexp_t sexp_t;
```

S-expressions are recursively defined: an s-expression is a list of either atoms or s-expressions. Example `(a (b c) d)` has linked-list internal structure with `next` pointers between elements.

## Core API

Five primary functions in `sexp.h`:

| Function | Purpose |
| --- | --- |
| `parse_sexp(buf, len)` | Parse string buffer into sexp_t AST |
| `read_one_sexp(iowrap)` | Read one s-expression from I/O wrapper (BUFSIZ buffer) |
| `print_sexp(buf, size, sexp)` | Serialize sexp_t back to string |
| `destroy_sexp(sexp)` | Free the s-expression tree |
| `init_iowrap(...)` | Initialize I/O wrapper for streaming parse |

Convenience operators in `sexp_ops.h`:
- `hd_sexp` — head (first element)
- `tl_sexp` — tail (remaining elements)
- `next_sexp` — next sibling

## Parsing Approaches

**Small expressions** (source files, small data):
```c
init_iowrap(&iow, file);
sexp_t result = read_one_sexp(&iow);
```

Uses BUFSIZ buffer (~1024 on macOS). Returns `SEXP_ERR_INCOMPLETE` if expression exceeds buffer.

**Large expressions** (big data encoded as single sexp):
```c
FILE *fp = fopen(fname, "r");
fseek(fp, 0, SEEK_END);
size_t fsize = (size_t) ftell(fp);
fseek(fp, 0, SEEK_SET);
char *work_buf = malloc(fsize + 1);
size_t read_len = fread(work_buf, 1, fsize, fp);
work_buf[read_len] = '\0';
sexp_t the_sexp = parse_sexp(work_buf, read_len);
```

## Internal Representation

Lispy linked-list structure. Example `(a (b c) d)`:

```
    sexp_t (list)
      |
     sexp_t -- next --> sexp_t -- next --> sexp_t
      |                   |                   |
     val                 list                val
      |                   |                   |
      a                  sexp_t --> next --> sexp_t
                          |                   |
                         val                 val
                          b                   c
                      (d is the third top-level element)
```

## Build System

Autoconf-based:
```bash
./configure           # vanilla build
./configure --enable-debug              # debug mode
./configure --enable-thread-unsafe-memory-management  # cached allocation
CFLAGS=-D_SEXP_LIMIT_MEMORY_ ./configure  # embedded mode
make
make install
```

Optional CMake build in `README_cmake.txt`. Windows support via `win32/` directory (untested since 2013).
