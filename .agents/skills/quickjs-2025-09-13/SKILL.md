---
name: quickjs-2025-09-13
description: Small and fast JavaScript engine supporting ES2023 with C API for embedding, qjs REPL interpreter, and qjsc bytecode compiler. Use when embedding a lightweight JS engine in C applications, compiling JS to standalone executables, running JS scripts via the qjs command line, or working with QuickJS runtime internals and garbage collection.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2025.9.13"
tags:
  - JavaScript
  - engine
  - C API
  - bytecode
  - embedding
  - ES2023
category: languages
external_references:
  - https://bellard.org/quickjs/
  - https://tc39.github.io/ecma262/2023
  - https://test262.fyi
  - https://bellard.org/quickjs/quickjs.html
  - https://github.com/bellard/quickjs
  - https://bellard.org/quickjs/Changelog
---
## Overview
QuickJS is a small, fast, and embeddable JavaScript engine that supports the ES2023 specification including modules, asynchronous generators, proxies, and BigInt. It consists of just a few C files with no external dependencies, producing executables as small as 210 KiB for a "hello world" program.

## When to Use
- Embedding a lightweight JavaScript engine in a C/C++ application
- Compiling JavaScript sources into standalone executables with no runtime dependency via `qjsc`
- Running JavaScript scripts or an interactive REPL via the `qjs` command line interpreter
- Building small tools where minimal binary size and fast startup are critical
- Working with JavaScript engines that support ES2023 with near-complete test262 compliance

## Core Concepts
### Architecture

QuickJS consists of three main components:

1. **`qjs`** — Command-line JavaScript interpreter (REPL) with syntax highlighting and completion
2. **`qjsc`** — JavaScript-to-bytecode compiler that generates C sources or standalone executables
3. **C API** (`quickjs.h`) — Embedding interface for integrating QuickJS into host applications

### Key Features

- **ES2023 Support**: Nearly complete ES2023 implementation including modules, async generators, proxies, BigInt, top-level await, and Annex B (legacy web compatibility)
- **Fast Interpreter**: Runs ~77,000 test262 tests in under 2 minutes on a single core; runtime lifecycle completes in < 300 microseconds
- **Reference Counting GC**: Deterministic memory management with automatic cycle removal
- **Bytecode Compiler**: Direct bytecode generation (no intermediate parse tree) for fast compilation and compact code
- **Standard Library**: Built-in `std` module (libc wrappers) and `os` module (system calls, workers, signals)

### Download

```bash
# Source code
curl -O https://bellard.org/quickjs/quickjs-2025-09-13-2.tar.xz
tar xf quickjs-2025-09-13-2.tar.xz

# Extras (unicode tables, benchmarks)
curl -O https://bellard.org/quickjs/quickjs-extras-2025-09-13.tar.xz
tar xf quickjs-extras-2025-09-13.tar.xz
```

### Building

```bash
cd quickjs-2025-09-13
make          # Build qjs and qjsc
make test     # Run built-in tests
# make install  # Install to /usr/local (optional)
```

On some OSes you may need `-latomics` in `LIBS` or disable `CONFIG_ATOMICS` in `quickjs.c`.

## Installation / Setup
### Quick Start with qjs

```bash
./qjs examples/hello.js                    # Run a JS file
./qjs -e 'console.log(1 + 2)'             # Evaluate an expression
./qjs -i                                   # Interactive REPL mode
./qjs --std script.js                      # Load std/os modules even for scripts
```

### Compiling with qjsc

```bash
# Generate a standalone executable
./qjsc -o hello examples/hello.js
./hello                                     # Runs with no external dependency

# Output C source only (for inspection or custom builds)
./qjsc -c -o hello.c examples/hello.js
gcc -o hello hello.c                        # Compile the generated C
```

### Command Line Options

**`qjs` interpreter:**

| Option | Description |
|--------|-------------|
| `-h`, `--help` | List options |
| `-e EXPR`, `--eval EXPR` | Evaluate expression |
| `-i`, `--interactive` | Enter interactive mode |
| `-m`, `--module` | Load as ES6 module |
| `--script` | Load as ES6 script |
| `-I file`, `--include file` | Include an additional file |
| `--std` | Make `std` and `os` modules available |
| `-d`, `--dump` | Dump memory usage stats |
| `-q`, `--quit` | Instantiate and quit |

**`qjsc` compiler:**

| Option | Description |
|--------|-------------|
| `-c` | Output bytecode in C file only |
| `-e` | Output `main()` and bytecode in C file |
| `-o output` | Set output filename |
| `-N cname` | Set C name of generated data |
| `-m` | Compile as JavaScript module |
| `-D module_name` | Compile dynamically loaded module |
| `-M module_name[,cname]` | Add external C module initialization |
| `-x` | Byte swapped output (cross compilation) |
| `-flto` | Link time optimization |
| `-fno-[eval\|string-normalize\|regexp\|...]` | Disable features for smaller binary |

## Usage Examples
### Using the std Module

```javascript
// File I/O
const f = std.open("output.txt", "w");
f.puts("Hello, World!\n");
f.close();

// Environment variables
print(std.getenv("HOME"));
std.setenv("MY_VAR", "value");
print(std.getenviron());

// URL fetching (uses curl internally)
const data = std.urlGet("https://example.com/api/data");
console.log(data);

// Extended JSON parsing (JSON5-like)
const parsed = std.parseExtJSON(`{
  // comment
  key: 'value',
  num: 0x10,
}`);
```

### Using the os Module

```javascript
// File operations
const fd = os.open("data.bin", os.O_RDONLY);
const buf = new Uint8Array(1024);
os.read(fd, buf, 0, 1024);
os.close(fd);

// Process execution
const code = os.exec(["ls", "-la"], { block: true });
print("Exit code:", code);

// Async sleep
await os.sleepAsync(500);

// Timers
const handle = os.setTimeout(() => print("timeout!"), 1000);
os.clearTimeout(handle);

// Platform detection
print(os.platform);  // "linux", "darwin", "win32", or "js"
```

### Workers (Multi-threading)

```javascript
// Main thread
const worker = new os.Worker("worker.js");
worker.postMessage({ task: "compute" });
worker.onmessage = (e) => print("Result:", e.data);

// worker.js
os.Worker.parent.postMessage({ result: 42 });
```

### Embedding QuickJS in C

```c
#include "quickjs.h"

JSRuntime *rt = JS_NewRuntime();
JSContext *ctx = JS_NewContext(rt);

// Evaluate JavaScript
JSValue result = JS_Eval(ctx, "1 + 2", 5, JS_EVAL_TYPE_GLOBAL);
// Use result...
JS_FreeValue(ctx, result);

// Cleanup
JS_FreeContext(ctx);
JS_FreeRuntime(rt);
```

## Changelog Highlights (2025-09-13)
- JSON modules and import attributes
- `JS_PrintValue()` API
- Pretty print objects in `qjs` REPL
- RegExp v flag, modifiers, and `RegExp.escape`
- `Float16Array`, `Promise.try`, `Error.isError()`
- `JS_FreePropertyEnum()` and `JS_AtomToCStringLen()` API

## Advanced Topics
## Advanced Topics

- [C Api](reference/01-c-api.md)
- [Internals](reference/02-internals.md)
- [Standard Library](reference/03-standard-library.md)
- [Specifications](reference/04-specifications.md)

