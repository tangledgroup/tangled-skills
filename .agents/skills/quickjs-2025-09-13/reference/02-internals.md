# QuickJS Internals

## Bytecode Compiler

QuickJS generates bytecode directly with no intermediate representation (no parse tree), making compilation very fast.

### Key Optimizations

- **Stack-based bytecode**: Simple and produces compact code
- **Compile-time stack size**: Maximum stack size computed per function at compile time — no runtime stack overflow checks needed
- **Compressed line number table**: Separate compressed table for debug info
- **Closure optimization**: Access to closure variables is optimized, nearly as fast as local variables
- **Direct eval in strict mode**: Optimized

## Executable Generation (qjsc)

The `qjsc` compiler generates C sources from JavaScript files.

### How It Works

1. Compile JavaScript → bytecode
2. Serialize to binary format
3. Embed bytecode in generated C source
4. Optionally generate a full `main()` function with JS engine initialization

```bash
# Full executable (default)
./qjsc -o myapp script.js

# C source only
./qjsc -c -o myapp.c script.js
gcc -o myapp myapp.c

# With link time optimization (smaller, slower compile)
./qjsc -flto -o myapp script.js

# Disable features for smaller binary
./qjsc -fno-eval -fno-regexp -o myapp script.js
```

### Feature Stripping Options

| Flag | Effect |
|------|--------|
| `-fno-eval` | Disable eval — smaller binary |
| `-fno-string-normalize` | Disable string normalization |
| `-fno-regexp` | Disable RegExp engine (~15 KiB saved) |
| `-fno-json` | Disable JSON module support |
| `-fno-proxy` | Disable Proxy support |
| `-fno-map` | Disable Map/Set |
| `-fno-typedarray` | Disable TypedArray |
| `-fno-promise` | Disable Promise support |
| `-fno-bigint` | Disable BigInt |

### Binary JSON Format

A subset of the bytecode serialization format (without functions/modules) can be used as binary JSON:

```javascript
// See tests/test_bjson.js for usage example
// WARNING: format may change between versions — do not use for persistent storage
```

## Runtime Internals

### Strings

- Stored as 8-bit or 16-bit character arrays
- Random access to characters is always fast
- C API converts to UTF-8; ASCII-only strings involve no copying

### Objects

- **Object shapes** (prototype, property names, flags) are shared between objects to save memory
- **Arrays with no holes** (except at end) are optimized
- **TypedArray accesses** are optimized

### Atoms

- Property names and certain strings stored as atoms (unique interned strings)
- Represented as 32-bit integers
- Half the atom range reserved for immediate integers 0 to 2³¹-1
- Enables fast comparison by integer equality

### Numbers

- **32-bit signed integers** or **64-bit IEEE-754 floats**
- Most operations have fast paths for the 32-bit integer case

### Garbage Collection

- **Reference counting** for automatic, deterministic object freeing
- **Cycle removal pass** when allocated memory becomes too large
- Cycle removal uses only reference counts and object content — no explicit GC roots needed in C code
- Manual cycle trigger: `std.gc()`

### JSValue Representation

| Platform | Size | Notes |
|----------|------|-------|
| 32-bit | 64-bit | NaN boxing for floats |
| 64-bit | 128-bit (2 registers) | No NaN boxing; memory less critical |

In both cases, JSValue fits exactly two CPU registers for efficient C function returns.

### Function Calls

- System stack holds JavaScript parameters and local variables
- Engine optimized for fast function calls
- No implicit stack in C API — parameters are normal C arguments

## RegExp Engine

Standalone regular expression library (~15 KiB x86 code, excluding Unicode):

- **Bytecode compiler**: Direct bytecode generation (no parse tree)
- **Backtracking with explicit stack**: No recursion on system stack
- **Simple quantifier optimization**: Avoids unnecessary recursion
- **ES2023 compliant**: Full Unicode properties support

## Unicode Library

Standalone Unicode library (~45 KiB x86 code):

- Case conversion
- Unicode normalization
- Unicode script queries
- Unicode general category queries
- All Unicode binary properties
- Compressed tables with reasonable access speed
- Updated to Unicode 15.0.0 (as of 2023-12-09)

## BigInt Implementation

- Binary two's complement notation
- Additional short bigint value for small number optimization
- BigInt support enabled even when `CONFIG_BIGNUM` is disabled
- Supported in Atomics operations
