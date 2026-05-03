# ☑ Plan: TinyScheme 1.41 Skill — Deep Implementation Study

**Depends On:** NONE
**Created:** 2026-05-03T18:25:00Z
**Updated:** 2026-05-03T17:07:45Z
**Current Phase:** ☑ Phase 11
**Current Task:** ☑ Task 11.2

This plan covers creating a comprehensive, implementation-focused skill for TinyScheme 1.41 — a lightweight Scheme interpreter implementing a subset of R5RS as an embedded scripting engine. The skill emphasizes carefully examined source code internals: memory model, GC algorithm, bytecode dispatch, evaluation cycle, reader/parser, FFI, and conditional compilation architecture.

---

## ☑ Phase 1 — Source Analysis & Structure Design

Analyze all crawled sources (already completed) and determine the reference file split for this complex skill.

- ☑ Task 1.1 Confirm source coverage completeness
  - Verify all key files studied: scheme.c (~4960 lines), scheme.h, scheme-private.h, opdefines.h, dynload.c, repl.c, test.c, init.scm, CMakeLists.txt, Manual.txt, BUILDING
  - Acceptance: All source files accounted for with section mappings

- ☑ Task 1.2 Design reference file structure (depends on: Task 1.1)
  - Determine which topics get their own reference file vs inline in SKILL.md
  - Acceptance: Clear mapping of topics → files, each reference ~200-400 lines max

## ☑ Phase 2 — Write SKILL.md (Hub File)

Create the main SKILL.md with YAML header, overview, when-to-use, core concepts summary, and navigation links to reference files.

- ☑ Task 2.1 Write YAML header and Overview section
  - Third-person description with WHAT + WHEN formula, 150-400 chars
  - Acceptance: Valid YAML, name `tinyscheme-1-41`, version `"1.41"`, category `language-runtime`

- ☑ Task 2.2 Write Core Concepts summary (depends on: Task 2.1)
  - High-level architecture: single-file C interpreter, opcode dispatch, Schorr-Waite GC, heap-based cells, conditional compilation
  - Acceptance: Concise but complete overview referencing deep-dive files

- ☑ Task 2.3 Write Advanced Topics navigation hub (depends on: Task 2.2)
  - Link to all reference files with one-line descriptions
  - Acceptance: All reference files linked, SKILL.md stays under 500 lines

## ☑ Phase 3 — Reference: Cell Memory Model & Allocation

Deep dive into how TinyScheme represents all Scheme values as cells on a managed heap.

- ☑ Task 3.1 Write reference/01-cell-memory-model.md
  - Topics to cover:
    - `struct cell` layout: `_flag` (type + GC bits), union of `_string`, `_number`, `_port`, `_ff`, `_cons`
    - Type system: `enum scheme_types` (T_STRING=1 through T_ENVIRONMENT=14), flag bits (T_SYNTAX, T_IMMUTABLE, T_ATOM, MARK)
    - Number representation: `struct num` with `is_fixnum` discriminant, `int64_t` vs `double` union
    - Symbol representation: cons of (string . properties), interned in oblist
    - Vector storage: consecutive cells packed 2-elements-per-cell via car/cdr pairs
    - Special cells: NIL, T, F, EOF_OBJ, sink — statically allocated in `struct scheme`
    - Cell allocation: segment-based heap (`CELL_SEGSIZE=5000`, `CELL_NSEGMENT=10`), free list sorted by address for consecutive vector allocation
    - Alignment via `ADJ` padding to `TYPE_BITS`-bit boundary
  - Acceptance: Every struct field and type constant explained with code snippets

## ☑ Phase 4 — Reference: Garbage Collection

Schorr-Deutsch-Waite link-inversion algorithm implementation.

- ☑ Task 4.1 Write reference/02-garbage-collection.md
  - Topics to cover:
    - Algorithm E (Knuth TAOCP Vol.1, sec. 2.3.5): Schorr-Deutsch-Waite
    - `mark()` function: link-inversion traversal using car/cdr as temporary back-pointers, `T_ATOM` bit as "moved car" flag
    - GC roots: oblist, global_env, args, envir, code, dump stack, value, inport, outport, loadport, sink's recent allocs, c_nest
    - Sweep phase: scan all cells downward (address order), unmarked → free list, strings/ports finalized via `finalize_cell()`
    - Free list maintained sorted by address to preserve consecutive ranges for vectors
    - `get_cell()`: try free list → GC → allocate new segment → fail with sink
    - `push_recent_alloc()` / `ok_to_freely_gc()`: protect objects not yet reachable from roots
    - `reserve_cells()` and `get_consecutive_cells()` for vector allocation
  - Acceptance: Step-by-step walkthrough of mark algorithm with pointer manipulation diagrams

## ☑ Phase 5 — Reference: Opcode System & Dispatch Table

The macro-generated opcode enum, dispatch table, and type-checking infrastructure.

- ☑ Task 5.1 Write reference/03-opcode-system.md
  - Topics to cover:
    - `opdefines.h`: `_OP_DEF(func_group, name, min_arity, max_arity, arg_tests, OP_ENUM)` — single source of truth
    - Enum generation: `enum scheme_opcodes` includes all OP_* from opdefines.h
    - Dispatch table: `struct op_code_info[]` with func pointer, name, arity bounds, test encoding
    - Test predicates: `is_any`, `is_string`, `is_symbol`, `is_number`, `is_integer`, `is_nonneg`, etc. — mapped to `TST_*` char codes in arg_tests_encoding string
    - `Eval_Cycle()`: main loop — check arity, run type tests on each arg, call dispatch function, repeat on return via `s_return()` restoring registers from dump stack
    - 7 dispatch functions (`opexe_0` through `opexe_6`) organized by complexity: control flow, special forms, arithmetic, predicates, I/O, reader/writer, utilities
    - `procnum(p)` maps built-in procedure cells to their opcode index
    - Syntax vs procedure distinction: syntax (special forms) have `T_SYNTAX` flag, dispatch via `syntaxnum()`
  - Acceptance: Full opcode lifecycle from definition → enum → dispatch table → runtime execution

## ☑ Phase 6 — Reference: Evaluation Cycle & Continuations

The interpreter's register machine, dump stack, and control flow implementation.

- ☑ Task 6.1 Write reference/04-evaluation-cycle.md
  - Topics to cover:
    - Four registers: `args`, `envir`, `code`, `dump` — plus `value` for results
    - Two dump stack implementations (controlled by `USE_SCHEME_STACK`):
      - C heap version: `struct dump_stack_frame[]` with auto-growth via `realloc()`
      - Scheme cons version: linked list of (op . (args . (envir . code))) — slower but supports continuations properly
    - `s_save(op, args, code)`: push current context onto dump stack
    - `_s_return(value)`: pop dump stack, restore registers, set sc->op for next iteration
    - `s_goto(op)`: jump to opcode within current Eval_Cycle iteration (no stack manipulation)
    - Core eval logic: symbol lookup → env search, pair → check syntax vs procedure, else return self
    - Macro expansion: detect macro in OP_E0ARGS, apply as closure, re-eval result via OP_DOMACRO
    - Closure application: new env frame, bind params to args (including dotted tail), execute body via OP_BEGIN
    - Continuation: `call/cc` captures dump stack into `T_CONTINUATION` cell, applying restores it
    - Special form implementations: if/cond/case/and/or/let/let*/letrec/begin/delay/quote — all via opcode chains with s_save/s_goto
  - Acceptance: Trace through example `(define (f x) (+ x 1)) (f 5)` showing register state at each step

## ☑ Phase 7 — Reference: Reader & Writer

Lexer, parser, and pretty-printer implementation.

- ☑ Task 7.1 Write reference/05-reader-writer.md
  - Topics to cover:
    - Token types: TOK_EOF, TOK_LPAREN, TOK_RPAREN, TOK_DOT, TOK_ATOM, TOK_QUOTE, TOK_COMMENT, TOK_DQUOTE, TOK_BQUOTE, TOK_COMMA, TOK_ATMARK, TOK_SHARP, TOK_SHARP_CONST, TOK_VEC
    - `token()`: skip whitespace (tracking line numbers for SHOW_ERROR_LINE), dispatch on first char
    - Atom reading: `readstr_upto()` reads until delimiter, `mk_atom()` parses number vs symbol (handles sign, decimal point, exponent, radix prefixes)
    - String reader: `readstrexp()` state machine (st_ok → st_bsl → st_x1/st_x2/st_oct1/st_oct2) for escape sequences
    - List/vector reading: OP_RDSEXPR → OP_RDLIST chain with nesting counter, handles dotted pairs via OP_RDDOT
    - Quasiquote reading: TOK_BQUOTE/TOK_COMMA/TOK_ATMARK → cons cells with QQUOTE/UNQUOTE/UNQUOTESP symbols
    - Sharp constants: `mk_sharp_const()` — #t/#f, #o/#d/#x/#b numbers, #\ characters (named + hex)
    - Writer: `atom2str()` converts each type to string, `printslashstring()` for escaped strings, `OP_P0LIST`/`OP_P1LIST` recursive printing with quote abbreviations ('`, `, ,@) and vector formatting
  - Acceptance: State machine diagram for string reader, token flow for list reading

## ☑ Phase 8 — Reference: Environments & Symbol Table

Environment frames, oblist implementations, and variable binding.

- ☑ Task 8.1 Write reference/06-environments.md
  - Topics to cover:
    - Environment structure: immutable cons of (frame . parent-env), `T_ENVIRONMENT` flag
    - Two environment backends (controlled by `USE_ALIST_ENV`):
      - Hash table version (default): global env uses vector of 461 buckets, local frames use alists — `hash_fn()` rotates and XORs chars
      - Alist version: all frames are simple association lists
    - Symbol table (oblist): two implementations (`USE_OBJECT_LIST`):
      - Hash table version: vector of 461 buckets, each bucket is alist of symbols
      - Linear list version: single cons list scanned sequentially
    - Symbol interning: case-insensitive per R5RS §2, `stricmp()` comparison, symbols are immutable cons of (string . plist)
    - `find_slot_in_env()`: walk env chain, hash to bucket if vector frame, linear scan alist for match
    - `new_frame_in_env()`, `new_slot_in_env()`, `set_slot_in_env()`, `slot_value_in_env()` — the four environment operations
  - Acceptance: Diagram showing environment chain with hash table frames

## ☑ Phase 9 — Reference: FFI & Embedding API

Foreign functions, scheme_interface vtable, embedding patterns.

- ☑ Task 9.1 Write reference/07-ffi-and-embedding.md
  - Topics to cover:
    - `scheme *` struct: complete interpreter state, multiple instances supported
    - Initialization: `scheme_init_new()` / `scheme_init_custom_alloc()` — allocates initial cell segments, sets up NIL/T/F/EOF_OBJ, creates global env, registers all built-in procedures
    - Deinitialization: `scheme_deinit()` — clears all pointers, runs final GC, frees all segments
    - Loading code: `scheme_load_file()`, `scheme_load_string()` — sets up loadport, enters Eval_Cycle from OP_T0LVL
    - Evaluation: `scheme_eval()` — wraps in save/restore for C→Scheme→C nesting safety via `c_nest` stack
    - Calling: `scheme_call(func, args)` — like eval but applies func to args
    - Foreign function type: `pointer (*foreign_func)(scheme *, pointer)` — receives sc and arg list, returns Scheme value
    - `scheme_interface` vtable (USE_INTERFACE): 50+ function pointers for type checks, constructors, accessors — used by foreign functions and DLLs
    - Dynamic loading: `dynload.c` wraps LoadLibrary/dlopen, calls `init_<module>` entry point, registers as `load-extension`
    - External data: `scheme_set_external_data()` for per-interpreter state in foreign functions
  - Acceptance: Complete embedding lifecycle example from init → load → eval → deinit

## ☑ Phase 10 — Reference: Conditional Compilation & Library

Feature flags, init.scm, and Scheme-level library architecture.

- ☑ Task 10.1 Write reference/08-compilation-and-library.md
  - Topics to cover:
    - Compile-time feature flags in scheme.h: STANDALONE, USE_MATH, USE_CHAR_CLASSIFIERS, USE_ASCII_NAMES, USE_STRING_PORTS, USE_ERROR_HOOK, USE_TRACING, USE_COLON_HOOK, USE_DL, USE_PLIST, USE_NO_FEATURES (disables all), USE_SCHEME_STACK, USE_MACRO, USE_JSON
    - Impact of each flag on code size and behavior
    - `USE_NO_FEATURES` produces ~64KB object file — minimal embedded footprint
    - init.scm (~1200 lines): Scheme-level library implementing car/cdr compositions (caar through cddddr), macro system via *compile-hook*, exception handling (catch/throw), module emulation, package system via *colon-hook*, stream utilities, vector/string helpers, JSON parsing
    - tinymodules.scm: Chicken-Scheme-style module/import emulation
    - utils.scm: reduce, partial, hash-map, with-input-from-string
    - json.scm: recursive descent JSON parser/generator as a module
  - Acceptance: Table of feature flags with size impact, init.scm architecture summary

## ☑ Phase 11 — Validation & README Sync

Validate all files and regenerate the skills table.

- ☑ Task 9.1 , Task 10.1)
  - YAML header valid, name matches directory, all required sections present
  - Reference files numbered 01-08, no chained references
  - SKILL.md under 500 lines
  - No hallucinated content — all from source code study
  - Acceptance: Zero validation errors

- ☑ Task 11.2 Sync README (depends on: Task 11.1)
  - Run `python3 misc/gen-skills-table.py`
  - Acceptance: README.md updated with new skill entry
