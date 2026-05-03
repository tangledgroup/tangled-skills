---
name: tinyscheme-1-41
description: Lightweight Scheme interpreter (R5RS subset) in ~5000 lines of C, designed as an embeddable scripting engine. Opcode-based dispatch, Schorr-Deutsch-Waite GC, segment-based heap, and conditional compilation for footprint tuning (down to ~64KB). Supports closures, continuations, macros, dynamic loading, string ports, vectors, and a C FFI via vtable. Use when building or studying embedded interpreters, analyzing mark-and-sweep GC algorithms, creating opcode-dispatch VMs, integrating Scheme into C applications, or understanding Lisp evaluation cycles.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.41"
tags:
  - tinyscheme
  - scheme
  - lisp
  - interpreter
  - embedded
  - gc
  - bytecode
category: language-runtime
external_references:
  - https://en.wikipedia.org/wiki/TinyScheme
  - https://github.com/zpl-c/tinyscheme
---

# TinyScheme 1.41

## Overview

TinyScheme is a lightweight Scheme interpreter implementing a large subset of R5RS in approximately 5000 lines of C. It is designed as an **embedded scripting engine** — multiple independent interpreter instances can coexist in one process, foreign C functions integrate via a vtable interface, and compile-time feature flags tune the footprint from full-featured down to ~64KB.

The architecture follows classic Lisp design: everything is a **cell** on a managed heap, garbage collection uses the **Schorr-Deutsch-Waite link-inversion algorithm**, evaluation proceeds through an **opcode-based dispatch table** with a register machine and dump stack, and the reader/parser produces S-expressions that feed directly into the evaluator.

Key implementation choices:

- **Single-file C source** (`scheme.c` ~4960 lines) — no separate compilation units for the core
- **Segment-based heap** — cells allocated in 5000-cell segments, free list sorted by address to support consecutive allocation for vectors
- **14 cell types** packed into a `struct cell` with union storage and bit-flagged type/metadata
- **Opcode dispatch** via macro-generated enum + dispatch table from `opdefines.h`, split across 7 handler functions (`opexe_0` through `opexe_6`)
- **Two dump stack backends** — C heap (faster, no continuations) or Scheme cons cells (slower, full continuation support)
- **Conditional compilation** — 12+ feature flags control math, string ports, tracing, dynamic loading, property lists, ASCII names, character classifiers, error hooks, colon hooks, and macro support

## When to Use

- Studying how a complete Lisp interpreter works at the implementation level
- Understanding the Schorr-Deutsch-Waite garbage collection algorithm in practice
- Building or debugging embedded scripting engines in C
- Analyzing opcode-dispatch virtual machine patterns
- Integrating Scheme as a scripting language into existing C applications
- Learning about cell-based memory models, environment chains, and closure representation
- Studying reader/parser implementations for S-expression languages
- Understanding how continuations are implemented via stack capture

## Core Architecture

### Source Layout

- `source/scheme.c` — Entire interpreter: reader, evaluator, GC, I/O, printing (~4960 lines)
- `include/scheme.h` — Public API and feature flag defaults
- `include/scheme-private.h` — Internal structs (`cell`, `scheme`, `port`) and opcode enum
- `include/opdefines.h` — Macro-driven opcode definitions generating both enum and dispatch table
- `source/dynload.c` — Dynamic library loading (LoadLibrary/dlopen abstraction)
- `test/repl.c` — Standalone REPL with file loading
- `libs/init.scm` — Scheme-level library: car/cdr compositions, macros, exceptions, modules, packages

### The Cell

Every Scheme value is a `struct cell` on the managed heap. The `_flag` field packs type (5 bits), syntax flag, immutable flag, atom flag (for GC), and mark bit. The union stores either string data + length, a number (int64/double with discriminant), a port pointer, a foreign function pointer, or car/cdr pair pointers. Vectors use consecutive cells packed 2-elements-per-cell via car/cdr pairs.

### Evaluation Model

Four registers (`args`, `envir`, `code`, `dump`) plus `value` for results. The main loop (`Eval_Cycle`) dispatches on `sc->op` through the opcode table, checking argument counts and types before calling the handler. Handlers use `s_save()` to push context onto the dump stack and `s_goto()` to jump to the next opcode. `_s_return()` pops the dump stack and restores registers. This creates a cooperative coroutine-style execution model where each special form is implemented as a chain of opcodes.

### Garbage Collection

Schorr-Deutsch-Waite algorithm: mark phase traverses from roots using car/cdr fields as temporary back-pointers (link inversion), with the `T_ATOM` bit marking "car was moved." Sweep phase scans all cells in address order, reclaiming unmarked cells into the free list. Strings and ports are finalized during sweep. The free list is kept sorted by address to maintain consecutive ranges for vector allocation.

## Advanced Topics

- Cell Memory Model & Allocation → [Cell Memory Model](reference/01-cell-memory-model.md)
- Garbage Collection (Schorr-Waite) → [Garbage Collection](reference/02-garbage-collection.md)
- Opcode System & Dispatch Table → [Opcode System](reference/03-opcode-system.md)
- Evaluation Cycle & Continuations → [Evaluation Cycle](reference/04-evaluation-cycle.md)
- Reader & Writer → [Reader and Writer](reference/05-reader-writer.md)
- Environments & Symbol Table → [Environments](reference/06-environments.md)
- FFI & Embedding API → [FFI and Embedding](reference/07-ffi-and-embedding.md)
- Conditional Compilation & Library → [Compilation and Library](reference/08-compilation-and-library.md)
