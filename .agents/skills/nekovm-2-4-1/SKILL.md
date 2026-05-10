---
name: nekovm-2-4-1
description: Stack-based bytecode VM and dynamically typed scripting language, primarily as a compilation target for Haxe. Provides C FFI, embeddable VM, and standalone executable generation. Deprecated since 2021-09-09, maintained for Haxe compatibility only. Use when embedding Neko as a scripting engine in C applications, writing Neko C primitives, or building Haxe projects targeting the Neko VM.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - nekovm
  - neko
  - virtual-machine
  - scripting-language
  - haxe
  - embedding
category: language-runtime
external_references:
  - https://nekovm.org/
  - https://github.com/HaxeFoundation/neko
  - https://github.com/HaxeFoundation/nekovm.org/tree/master
---

# NekoVM 2.4.1

## Overview

Neko is a high-level dynamically typed programming language with a stack-based bytecode virtual machine. It was designed as a common runtime for multiple languages — most notably as a compilation target for [Haxe](https://haxe.org/). The compiler converts `.neko` source files into `.n` bytecode modules executed by the `neko` VM binary.

Neko is **deprecated as of 2021-09-09**. No new features are planned; it is maintained only for Haxe standard library and language feature compatibility. Version 2.4.1 was released on 2025-04-15.

The VM uses a Boehm conservative garbage collector, supports JIT compilation on select platforms, and can be embedded into C applications via `libneko.so`/`neko.dll`. Extensions are written as C shared libraries (`.ndll`) using the Neko C FFI.

## When to Use

- Embedding Neko as a scripting engine inside a C application
- Writing Neko C primitives (`.ndll` extensions) that expose OS/hardware APIs
- Building Haxe projects with `neko` as the compilation target
- Designing a language compiler that targets a shared runtime
- Running legacy Neko bytecode modules or `mod_neko` Apache deployments

## Core Concepts

**Value types:** Neko has 9 value types — `null`, `int` (signed 31-bit), `float` (64-bit double), `bool`, `string` (mutable byte buffer, not encoding-specific), `array` (fixed-size, integer-indexed, not resizable), `object` (hashed-field hashtable with O(log n) access), `function` (first-class, fixed or variable arity), and `abstract` (opaque C pointer tagged with a *kind*).

**Modules:** Compiled bytecode files with `.n` extension. Each module has a `$exports` object for inter-module communication and a `$loader` for loading other modules and C primitives.

**Libraries:** `.ndll` files are shared libraries linked against `libneko`. They expose C primitives callable from Neko code via `$loader.loadprim("library@function", nargs)`.

**Prototypes:** Objects can have a prototype chain (`$objsetproto`). Missing fields are resolved recursively up the prototype, enabling class-like inheritance without per-instance method copies.

**NEKOPATH:** Environment variable listing search paths (colon-separated on Unix, semicolon on Windows) for both `.n` modules and `.ndll` libraries.

## Installation / Setup

### Pre-built binaries

Download from [GitHub Actions artifacts](https://github.com/HaxeFoundation/neko/actions?query=branch%3Amaster+is%3Asuccess). macOS snapshot via homebrew: `brew install neko --HEAD`.

### Build from source

Requires CMake 3.x and a C compiler (gcc on Linux, XCode on Mac, Visual Studio 2010+ on Windows).

```bash
mkdir build && cd build
cmake ..
make          # or msbuild ALL_BUILD.vcxproj /p:Configuration=Release on Windows
make install  # optional, default prefix /usr/local (Unix) or C:\HaxeToolkit\neko (Windows)
```

**Dependencies** (install via system packages or use `STATIC_DEPS` CMake option):

| Library | Debian/Ubuntu package |
|---------|----------------------|
| Boehm GC | `libgc-dev` |
| OpenSSL | `libssl-dev` |
| PCRE2 | `libpcre2-dev` |
| zlib | `zlib1g-dev` |
| Apache 2.x | `apache2-dev` |
| MariaDB/MySQL | `libmariadb-client-lgpl-dev-compat` |
| SQLite | `libsqlite3-dev` |
| mbed TLS | `libmbedtls-dev` |
| GTK+3 (Linux UI) | `libgtk-3-dev` |

**Key CMake options:**

- `WITH_REGEXP`, `WITH_UI`, `WITH_SSL`, `WITH_MYSQL`, `WITH_SQLITE`, `WITH_APACHE` — toggle individual ndll builds (default `ON`)
- `STATIC_DEPS` — `all` (Windows default), `none` (Unix default), or comma-separated list of libraries to link statically
- `RELOCATABLE` — set RPATH to `$ORIGIN`/`@executable_path` so VM finds libraries in its own directory (default `ON`)
- `NEKO_JIT_DISABLE` — disable JIT for all platforms (default `OFF`)

## Usage Examples

### Compile and run a Neko program

```neko
// hello.neko
$print("hello neko world!\n");
```

```bash
nekoc hello.neko   # produces hello.n
neko hello         # prints "hello neko world!"
```

### Load a module and call its exports

```neko
var m = $loader.loadmodule("mathlib", $loader);
m.add(3, 4);  // calls exported function
```

### Write a C primitive (ndll)

```c
// hello.c
#include <neko.h>

value test() {
    return alloc_string("Hello from C");
}

DEFINE_PRIM(test, 0);
```

Compile to `hello.ndll`, then use from Neko:

```neko
var p = $loader.loadprim("hello@test", 0);
$print(p());  // "Hello from C"
```

## Advanced Topics

**Language Specification**: Syntax grammar, value types, operations, arrays, strings, hashtables, objects, functions, exceptions, RTTI → [Language Spec](reference/01-language-spec.md)

**C FFI**: Writing Neko primitives in C — value manipulation, type checks, abstracts/kinds, memory management, callbacks, buffers → [C FFI](reference/02-c-ffi.md)

**VM Embedding**: Embedding NekoVM in C applications, loaders, exports, custom loaders, multithreading → [VM Embedding](reference/03-vm-embedding.md)

**Standard Libraries**: Core builtins and 20+ standard modules (Buffer, File, Socket, System, Xml, Sqlite, etc.) with type notation conventions → [Standard Libraries](reference/04-standard-libraries.md)

**Tools and Web**: CLI tools (neko, nekoc, nekoml, nekotools), mod_neko Apache module, web server, standalone executables → [Tools and Web](reference/05-tools-and-web.md)

**Architecture**: VM internals, value representation, Lua comparison, closures, OO support, FFI design, performance characteristics → [Architecture](reference/06-architecture.md)
