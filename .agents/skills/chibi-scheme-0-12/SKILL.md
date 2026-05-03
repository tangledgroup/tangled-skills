---
name: chibi-scheme-0-12
description: Minimal Scheme implementation for embedding in C applications. Provides a tagged-pointer VM with precise non-moving GC, opcode-based execution with simplification optimizer, hygienic macros via syntactic closures, layered module hierarchy, green threads with isolated heaps, full R7RS compliance with complete numeric tower, and a C FFI stubber generating shared libraries from Scheme DSL. Use when embedding Scheme in C programs, studying interpreter design, building extension languages, or wrapping C libraries for use from Scheme.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.12"
tags:
  - chibi-scheme
  - scheme
  - lisp
  - embedded-vm
  - c-ffi
  - hygienic-macros
category: language-runtime
external_references:
  - https://github.com/ashinn/chibi-scheme
---

# Chibi-Scheme 0.12

## Overview

Chibi-Scheme is a minimal Scheme library with **zero external dependencies**, designed primarily for embedding in C applications as an extension and scripting language. It implements R7RS small language by default, with the full numeric tower (fixnums, flonums, bignums, exact rationals, complex numbers) enabled out of the box.

The system is built in optional layers: a small opcode VM at the bottom, C-implemented primitives above it, then the default language, module system, and standard modules. You can use whichever layer fits your needs and disable the rest at compile time via `features.h` preprocessor flags.

Key design principles:

- **Minimalism with correctness** — small footprint but does The Right Thing (full numeric tower, Unicode, hygienic macros)
- **Tagged-pointer representation** — fixnums use the low bit, immediates use specific bit patterns, heap objects carry type tags
- **Precise non-moving GC** — critical for C interop since C can hold pointers into the Scheme heap; Boehm conservative GC available as alternative
- **Opcode-based VM** — Scheme compiles to bytecode executed by a register machine with an optional simplification optimizer pass
- **Layered languages** — module hierarchy in the Scheme48 style, not flat R7RS; each layer extends the one below
- **Right-to-left evaluation order** — unlike most implementations which evaluate left-to-right

## When to Use

- Embedding Scheme as a scripting/extension language in C applications
- Studying interpreter design: tagged pointers, precise GC, opcode dispatch VMs
- Building lightweight extension languages for existing systems
- Understanding hygienic macro implementation via syntactic closures
- Wrapping C libraries for use from Scheme (via chibi-ffi stubber)
- Needing a portable Scheme runtime (Linux, BSD, macOS, Windows, Plan 9, iOS, Android, Emscripten/WASM)
- Building static executables with Scheme code baked in

## Core Concepts

### Tagged Pointers

All Scheme values are `sexp` pointers. The low bits encode the type:

- **Odd (ends in 1)**: fixnum — the integer value is the pointer shifted right
- **Ends in 00**: heap pointer — type tag stored in the object header
- **Ends in 010**: string cursor (optional)
- **Ends in 0110**: immediate symbol (optional)
- **Ends in 00001110**: immediate flonum (optional)
- **Ends in 00011110**: character
- **Ends in 00111110**: unique immediates (NULL, TRUE, FALSE)

This allows fixnums and characters to be stored directly in the pointer without heap allocation.

### Context And Heap Model

Each VM context owns a heap. Multiple contexts can coexist:

- **Child contexts** share the parent's heap but have separate evaluation stacks
- **Independent contexts** have separate heaps and can run simultaneously in different OS threads with no synchronization needed
- The `sexp_gc_varN`/`sexp_gc_preserveN`/`sexp_gc_releaseN` macro trio tells the precise GC which C-local variables hold Scheme references that must survive allocation

### Layered Language Architecture

Chibi builds languages in layers, not flat modules:

1. **Core forms** (10 built-in special forms: `define`, `set!`, `lambda`, `if`, `begin`, `quote`, `syntax-quote`, `define-syntax`, `let-syntax`, `letrec-syntax`)
2. **C primitives** — compiled-in opcodes for arithmetic, I/O, list operations
3. **Default language** — `(scheme base)` from R7RS, built on top of primitives
4. **Module system** — R7RS `define-library` with Scheme48-style layering
5. **Standard modules** — `(chibi *)` namespace for non-standard extensions

Each layer can be used independently. A minimal embedding might use only core forms and custom C primitives.

### Right-To-Left Evaluation

Chibi evaluates arguments right-to-left, which differs from most Scheme implementations (left-to-right) and many other languages. The R7RS spec says evaluation order is unspecified, so this is standards-compliant but can surprise programmers porting code.

## Advanced Topics

**VM And GC**: Tagged pointers, heap model, precise GC pattern, opcode VM, Boehm alternative → [VM And GC](reference/01-vm-and-gc.md)

**Macros And Modules**: Hygienic macros, syntactic closures, module hierarchy, import/export, cond-expand → [Macros And Modules](reference/02-macros-and-modules.md)

**Embedding And FFI**: C API, context lifecycle, evaluation, GC preservation, chibi-ffi stubber → [Embedding And FFI](reference/03-embedding-and-ffi.md)

**Features And Ecosystem**: Numeric tower, Unicode/strings, green threads, compile flags, SRFIs, standard modules, snow packages → [Features And Ecosystem](reference/04-features-and-ecosystem.md)
