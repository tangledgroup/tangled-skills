# ☑ Plan: Chibi-Scheme 0.12 Skill

**Depends On:** NONE
**Created:** 2026-05-03T12:00:00Z
**Updated:** 2026-05-03T12:20:00Z
**Current Phase:** ☑ Phase 4
**Current Task:** ☑ Task 4.2

## Scope

Generate a complex skill (SKILL.md + reference/) for Chibi-Scheme 0.12, focusing on **principles and design patterns** rather than exhaustive API documentation. The user wants to understand architecture decisions: tagged pointers, precise GC, opcode VM, layered language design, hygienic macros, module hierarchy, green threads, C FFI stubber, and the philosophy of minimalism-with-correctness.

Source material collected from GitHub README and official manual (synthcode.com). No further crawling needed.

---

## ☑ Phase 1 Analyze Source Material

- ☑ Task 1.1 Identify key architectural principles from source
  - Tagged pointer representation (fixnum bits, immediate values, heap pointers)
  - Precise non-moving GC with preserve/release macros
  - Opcode-based VM with simplification optimizer
  - Layered language: core forms → primitives → default language → modules
  - Hygienic macro system (syntactic closures, identifier-level hygiene)
  - Module hierarchy (Scheme48-style layered languages, not flat R7RS)
  - Green threads per-VM with isolated heaps
  - C FFI stubber (chibi-ffi) generating shared libraries from Scheme DSL
  - Full numeric tower as default (bignums, ratios, complex)
  - UTF-8 string representation with cursor API
  - Image files for startup optimization
  - Right-to-left evaluation order
  - Static build support with clibs.c generation
- ☑ Task 1.2 Determine reference file split
  - `01-vm-and-gc.md` — tagged pointers, opcode VM, precise GC, heap model
  - `02-macros-and-modules.md` — hygienic macros, syntactic closures, module hierarchy
  - `03-embedding-and-ffi.md` — C API, contexts, chibi-ffi stubber, type system
  - `04-features-and-ecosystem.md` — numeric tower, Unicode/strings, green threads, SRFIs, standard modules, snow package manager

---

## ☑ Phase 2 Write SKILL.md

- ☑ Task 2.1 Draft YAML header (name, description, version, tags, category)
  - name: chibi-scheme-0-12
  - description: ~300 chars, WHAT + WHEN
  - category: language-runtime
  - tags: chibi-scheme, scheme, lisp, embedded-vm, c-ffi, hygienic-macros
- ☑ Task 2.2 Write Overview section
  - Minimal Scheme library for embedding in C
  - No external dependencies
  - R7RS default with full numeric tower
  - Key differentiators: layered languages, precise GC, opcode VM
- ☑ Task 2.3 Write When to Use section
  - Embedding Scheme as scripting language
  - Studying interpreter design (tagged pointers, precise GC, opcodes)
  - Building extension languages for C applications
  - Understanding hygienic macro implementation
- ☑ Task 2.4 Write Core Concepts section
  - Tagged pointer representation
  - Context/heap isolation model
  - Layered language architecture
  - Right-to-left evaluation
- ☑ Task 2.5 Write Advanced Topics navigation hub
  - Link to all 4 reference files

---

## ☑ Phase 3 Write Reference Files

- ☑ Task 3.1 Write reference/01-vm-and-gc.md
  - Tagged pointer system (bits layout, immediate vs heap values)
  - Heap model (segments, object headers, type tags)
  - Precise GC (sexp_gc_var/preserve/release pattern, why non-moving matters for C interop)
  - Opcode VM (bytecode compilation, simplification pass, disassembler)
  - Boehm GC alternative
- ☑ Task 3.2 Write reference/02-macros-and-modules.md
  - Hygienic macros: syntactic closures, identifier=? , strip-syntactic-closures
  - Low-level macro transformers (sc-macro-transformer, rsc-macro-transformer, er-macro-transformer)
  - Module hierarchy (Scheme48-style layered languages vs flat R7RS)
  - Import/export/only/except/rename/prefix
  - include/include-ci/include-shared
  - cond-expand and feature system
  - The (auto) module for auxiliary bindings
- ☑ Task 3.3 Write reference/03-embedding-and-ffi.md
  - Context lifecycle (sexp_make_context, sexp_make_eval_context, sexp_destroy_context)
  - Environment loading (sexp_load_standard_env, sexp_load_standard_ports)
  - Evaluation API (sexp_eval, sexp_eval_string, sexp_load, sexp_apply)
  - GC preservation pattern from C (sexp_gc_varN/preserveN/releaseN)
  - Adding primitives (sexp_define_foreign, sexp_register_simple_type)
  - C pointer wrapping (sexp_register_c_type, sexp_make_cpointer with finalizers)
  - chibi-ffi stubber DSL (define-c-struct, define-c, type modifiers)
  - Type system overview (predicates, constructors, accessors)
- ☑ Task 3.4 Write reference/04-features-and-ecosystem.md
  - Numeric tower: fixnums, flonums, bignums, ratios, complex
  - Unicode strings: UTF-8 internal encoding, cursor API, O(n) string-ref caveat
  - Green threads (SRFI-18): lightweight VM threads, per-thread context
  - Image files for startup optimization
  - Static builds with clibs.c
  - Compile-time feature flags (SEXP_USE_* in features.h)
  - Standard modules overview (chibi namespace: net, json, filesystem, process, etc.)
  - SRFI support (built-in vs loadable)
  - snow-chibi package manager

---

## ☑ Phase 4 Validate And Sync

- ☑ Task 4.1 Run validation checklist (depends on: Task 2.5 , Task 3.4)
  - YAML header valid, name matches directory
  - All required sections present
  - Reference files numbered correctly (01- through 04-)
  - No chained references
  - SKILL.md under 500 lines
  - Concise content, no over-explaining basics
- ☑ Task 4.2 Sync README (depends on: Task 4.1)
  - Run `python3 misc/gen-skills-table.py`
