---
name: prescheme-2026-05-03
description: Statically typed Scheme dialect that compiles to C via Hindley/Milner type inference and CPS transformations. Combines Scheme syntax, macros, and tail recursion with manual memory management and no runtime overhead. Use when building virtual machines, garbage collectors, operating systems, or embedded systems where a full Scheme implementation is too heavy but C lacks expressiveness.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026-05-03"
tags:
  - prescheme
  - scheme
  - lisp
  - static-typing
  - systems-programming
  - c-compiler
category: language-runtime
external_references:
  - https://prescheme.org/
  - https://codeberg.org/prescheme/prescheme
---

# Pre-Scheme

## Overview

Pre-Scheme is a statically typed Scheme dialect that compiles to C. Developed by Richard Kelsey and Jonathan Rees in 1986, it bootstraps the Scheme 48 virtual machine and garbage collector. The compiler uses Hindley/Milner type reconstruction and a series of correctness-preserving CPS transformations to produce C with zero runtime overhead.

A Restoration project (Andrew Whatson, NGI Zero grant, 2024) is porting the compiler from Scheme 48 to R7RS, making it runnable on Chibi, Sagittarius, Guile, and other standard Scheme implementations.

## When to Use

- Building virtual machines, garbage collectors, or operating system components where Scheme expressiveness is needed but runtime overhead is unacceptable
- Writing embedded systems code with Scheme macros and tail recursion instead of C
- Studying transformational compilation (CPS-based optimization pipelines)
- Exploring statically typed functional systems languages in the Lisp family
- Understanding how Hindley/Milner type inference applies to Scheme-like syntax
- Working with or contributing to the Pre-Scheme Restoration project

## Core Concepts

**Scheme as a systems language:** Pre-Scheme retains Scheme syntax, hygienic macros, and tail recursion, but removes features requiring a garbage collector or runtime type system. The result is code that reads like Scheme but compiles to C with manual memory management.

**Type inference over annotations:** A modified Hindley/Milner algorithm reconstructs types from usage patterns. The compiler chooses machine representations per variable and monomorphizes polymorphic procedures automatically — no manual type annotations required.

**CPS transformational compilation:** Compilation is a sequence of transformations on a single Continuation-Passing-Style intermediate representation. Each pass (eta-reduction, inlining, specialization, common-subexpression elimination) operates on the same lambda-calculus-based IR, making optimization uniform and correctness-preserving.

**Compile-time top-level:** The top-level of every Pre-Scheme file is evaluated at compile time. This builds complex data structures and procedures incrementally during compilation, then treats them as static constants in the generated C code. Runtime closures that would need heap allocation are rejected.

## Advanced Topics

**Language Semantics**: Scheme features retained, restrictions vs full Scheme, comparison with C → [Language Semantics](reference/01-language-semantics.md)

**Type System and Compiler**: Hindley/Milner inference, polymorphism, CPS IR, transformational compilation pipeline → [Type System and Compiler](reference/02-type-system-and-compiler.md)

**Memory and Low-Level Features**: Manual memory management, record types, fixed-size numerics, FFI patterns → [Memory and Low-Level Features](reference/03-memory-and-low-level.md)

**Restoration Project**: R7RS port status, planned language extensions (ADTs, sized numerics, UTF-8 strings), tooling roadmap → [Restoration and Roadmap](reference/04-restoration-and-roadmap.md)
