---
name: quickjs-2025-09-13
description: Small and fast JavaScript engine supporting ES2023 with C API for embedding, qjs REPL interpreter, and qjsc bytecode compiler. Use when embedding a lightweight JS engine in C applications, compiling JS to standalone executables, running JS scripts via the qjs command line, or working with QuickJS runtime internals and garbage collection.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2025-09-13"
tags:
  - javascript
  - engine
  - es2023
  - c-api
  - embedding
  - bytecode
  - compiler
category: runtime
external_references:
  - https://bellard.org/quickjs/
  - https://tc39.github.io/ecma262/2023
  - https://test262.fyi
  - https://bellard.org/quickjs/quickjs.html
  - https://github.com/bellard/quickjs
  - https://bellard.org/quickjs/Changelog
---

# QuickJS 2025-09-13

## Overview

QuickJS is a small and embeddable JavaScript engine written in C. It supports the ES2023 specification including modules, asynchronous generators, proxies, and BigInt. At approximately 210 KiB of x86 code for a simple "hello world" program, it is one of the smallest fully-featured JavaScript engines available. It passes nearly 100% of the ECMAScript Test Suite (test262) for ES2023 features.

Key characteristics:

- **Small footprint** — just a few C files, no external dependencies
- **Fast startup** — complete runtime lifecycle in under 300 microseconds
- **ES2023 compliant** — almost complete support including Annex B (legacy web compatibility)
- **Standalone executables** — compile JavaScript sources to binaries with no external dependency
- **Reference counting GC** — deterministic behavior with cycle removal
- **C API** — simple and efficient embedding interface defined in `quickjs.h`

## When to Use

- Embedding a lightweight JavaScript engine in C/C++ applications
- Compiling JavaScript to standalone executables via `qjsc`
- Running JavaScript scripts from the command line with `qjs`
- Building custom JS runtimes with selective feature support
- Working with QuickJS internals (bytecode, garbage collection, atoms)
- Creating native C modules that expose functionality to JavaScript

## Core Concepts

**JSRuntime** — Represents a JavaScript runtime corresponding to an object heap. Multiple runtimes can exist simultaneously but cannot exchange objects. No multi-threading within a single runtime.

**JSContext** — Represents a JavaScript context (or Realm). Each context has its own global objects and system objects. Multiple contexts per runtime can share objects, similar to browser frames of the same origin.

**JSValue** — Represents any JavaScript value (primitive or object). Uses reference counting — must be explicitly duplicated with `JS_DupValue()` or freed with `JS_FreeValue()`. On 64-bit systems, JSValue is 128-bit; on 32-bit, NaN boxing is used to fit in two registers.

**Bytecode** — The compiler generates stack-based bytecode directly without an intermediate parse tree representation. Maximum stack size per function is computed at compile time, eliminating runtime stack overflow checks.

## Advanced Topics

**C API Reference**: Runtime/Context creation, JSValue handling, C functions, exceptions, script evaluation, classes, modules → [C API Reference](reference/01-c-api-reference.md)

**Standard Library**: Global objects, `std` module (file I/O, environment, HTTP), `os` module (low-level file access, signals, workers) → [Standard Library](reference/02-standard-library.md)

**Internals and Architecture**: Bytecode format, executable generation with qjsc, strings, objects, atoms, numbers, garbage collection, RegExp engine, Unicode library, BigInt representation → [Internals and Architecture](reference/03-internals-and-architecture.md)

**ES2023 Support and Modules**: Language feature coverage, module resolution, unsupported features → [ES2023 Support and Modules](reference/04-es2023-support.md)
