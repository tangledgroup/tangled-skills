# ⚙️ Plan: lisp-in-c-2026-05-03 Skill Generation

**Depends On:** NONE
**Created:** 2026-05-03T12:00:00Z
**Updated:** 2026-05-03T12:00:00Z
**Current Phase:** ⚙️ Phase 4
**Current Task:** ⚙️ Task 4.1

---

## Source Analysis (Completed During Planning)

Two sources studied:

1. **LIPS (hal-rock/lips)** — A barebones Lisp interpreter in C, inspired by Norvig's lispy. Key characteristics:
   - Linked-list-based S-expression representation (atoms + lists, no cons pairs)
   - All values stored as strings (integers only, no floats)
   - Custom hash table for environments with linear probing
   - 15 built-in functions (+, -, *, /, >, <, =, car, cdr, cons, list, eq?, display)
   - Special forms: def, if, quote (with ' syntax sugar)
   - User-defined functions via quoted lists: `(def plus1 '((x) (+ x 1)))`
   - No garbage collection (relies on short-lived usage)
   - No error handling beyond perror/segfault
   - Modular source: parse.c, eval.c, env.c, builtins.c, list.c, func.c, hash.c, print.c, interpret.c
   - Build via makeheaders + make

2. **ittrip.xyz minimal-lisp-in-c** — Tutorial-style guide covering:
   - Tokenizer (strtok-based, space/paren delimited)
   - AST with union-based Node types (NODE_NUMBER, NODE_SYMBOL, NODE_LIST)
   - Recursive descent parser building tree from tokens
   - Eval function handling numbers, symbols (env lookup), and lists
   - Environment as linked list of symbol→value bindings
   - Custom functions with parameter binding
   - REPL implementation
   - Extension patterns: error handling, garbage collection

### Overlap With Existing Skills

- **lisp-in-python-2026-05-03**: Same topic but Python host language. This skill covers C-specific concerns (memory management, structs, pointers, malloc/free). No content duplication — different implementation paradigm entirely.
- **scheme-in-python-2026-05-03**: SICP-style Scheme in Python. Different host language, different focus.
- **tinyscheme-1-41**: Production-grade embedded Scheme in C with GC, opcodes, continuations. This skill covers *building from scratch* (educational/tutorial), not studying an existing production interpreter. Different audience and use case.
- **peg-2026-05-03**: Parsing theory only, no language implementation overlap.

### Content Domain Breakdown

The skill naturally splits into 4 reference domains:

1. **Data Structures** — S-expression representation in C (linked lists vs AST nodes, union types, memory layout). This is the foundational layer.
2. **Parser and Reader** — Tokenization strategies (strtok vs char-by-char), recursive descent parsing, handling quote syntax sugar, error detection for mismatched parens.
3. **Evaluator and Environment** — The eval-apply cycle in C, hash table vs linked-list environments, lexical scoping via environment chains, user-defined function calls with parameter binding.
4. **Builtins and Extensions** — Implementing arithmetic/list/comparison builtins, REPL wiring, display/print, error handling patterns, garbage collection strategies (ref counting, mark-and-sweep), memory management discipline.

---

## ☑ Phase 1 Research and Analysis

- ☑ Task 1.1 Study LIPS source code structure and architecture
  - Analyzed all 9 source files + structs.h
  - Mapped data flow: parse → eval → builtins/call → env lookup
  - Documented key design decisions (string-only values, linked-list S-expressions, hash-table envs)

- ☑ Task 1.2 Study ittrip.xyz tutorial code and patterns
  - Tokenizer uses strtok with paren/space delimiters
  - AST uses enum + union for type-safe node variants
  - Eval function dispatches on node type
  - Environment is simple linked list (vs LIPS hash table)
  - Function definition via quoted parameter lists

- ☑ Task 1.3 Identify unique C-specific concerns vs existing lisp-in-python skill
  - Manual memory management (malloc/free, no GC by default)
  - Pointer-based data structures (linked lists, sentinel nodes)
  - Custom hash table implementation (linear probing)
  - String-as-universal-value representation
  - Type casting and void* patterns
  - Build tooling (makeheaders, make)

- ☑ Task 1.4 Determine reference file split strategy
  - 4 reference files identified (data structures, parser, evaluator, builtins/extensions)
  - Each covers a distinct implementation domain
  - Agent would load 1-2 per task
  - No chained references needed

## ☑ Phase 2 Create SKILL.md

- ☑ Task 2.1 Write YAML header
  - name: lisp-in-c-2026-05-03
  - version: "2026-05-03"
  - category: language-runtime
  - Tags: lisp, c, interpreter, eval-apply, s-expression, linked-list
  - Description formula: [Build a Lisp interpreter in C] + [parsing S-expressions, manual memory management, hash-table environments, user-defined functions, REPL] + Use when [building interpreters from scratch in C, understanding how Lisp evaluation works at the systems level, learning pointer-based data structures for language implementation, or studying the eval-apply cycle with explicit memory management]

- ☑ Task 2.2 Write Overview section
  - Synthesize both sources into a coherent narrative
  - Emphasize C-specific aspects (memory, pointers, manual GC)
  - Reference both LIPS and tutorial approaches

- ☑ Task 2.3 Write When to Use section
  - Specific scenarios for building Lisp in C
  - Distinguish from existing lisp-in-python skill

- ☑ Task 2.4 Write Core Concepts section
  - S-expressions as linked lists vs AST nodes
  - The eval-apply cycle
  - Environment chains for lexical scoping
  - Homoiconicity (code-as-data)
  - Two representation approaches: string-only atoms (LIPS) vs typed union (tutorial)

- ☑ Task 2.5 Write Quick Start section
  - Minimal working example combining both approaches
  - Show the simplest eval loop

- ☑ Task 2.6 Write Advanced Topics navigation hub
  - Link to all 4 reference files

## ☑ Phase 3 Create Reference Files

- ☑ Task 3.1 Write reference/01-data-structures.md (depends on: Task 2.1 , Task 2.4)
  - S-expression representation in C
  - LIPS approach: node + linked_list with sentinel start/end, bool atom flag, void* data
  - Tutorial approach: enum NodeType + union for type-safe variants
  - Hash table implementation (LIPS): linear probing, hash function, entry overwrites
  - Environment structure: outer pointer + storage (hash table or linked list)
  - Memory management patterns: new_node/new_list, deep copy, destroy functions
  - Comparison of both approaches with tradeoffs
  - Include code examples for both representations

- ☑ Task 3.2 Write reference/02-parser-and-reader.md (depends on: Task 2.4)
  - Tokenization: char-by-char (LIPS) vs strtok-based (tutorial)
  - Recursive descent parser for S-expressions
  - Handling parentheses nesting
  - Quote syntax sugar ('x → (quote x))
  - Building AST/list from tokens
  - Error handling: mismatched parens, EOF detection
  - Print/writer: recursive s_print function
  - Include complete tokenizer and parser code

- ☑ Task 3.3 Write reference/03-evaluator-and-environment.md (depends on: Task 2.4)
  - The eval-apply cycle in C
  - eval() dispatch: atom vs list, symbol lookup vs number passthrough
  - Special forms: if, def/define, quote
  - Built-in function dispatch
  - User-defined function call: parameter binding via new environment frame
  - Environment chain traversal for lexical scoping
  - Hash table approach (LIPS) vs linked-list approach (tutorial)
  - Truth testing in Lisp (nonzero = true)
  - Include complete eval function with both approaches

- ☑ Task 3.4 Write reference/04-builtins-and-extensions.md (depends on: Task 2.4)
  - Arithmetic builtins: +, -, *, / with string-to-long conversion
  - Comparison builtins: >, <, =
  - List operations: car, cdr, cons, list, eq?
  - Display/print: s_print recursive writer
  - Number/string conversion utilities (ltoa, p_strtol)
  - REPL implementation: stdin buffering via tmpfile
  - File interpretation mode
  - Extension patterns: error handling, garbage collection strategies
  - Memory discipline: when to free, deep copy semantics
  - Include complete builtin implementations

## ☐ Phase 4 Validate And Finalize

- ☐ Task 4.1 Run YAML header validation (depends on: Task 2.1)
  - name matches directory
  - description within 150-400 chars
  - all required fields present
  - valid YAML syntax

- ☐ Task 4.2 Validate structure (depends on: Task 2.6 , Task 3.4)
  - SKILL.md under 500 lines
  - reference/ has 4 numbered files
  - No chained references
  - All links resolve

- ☐ Task 4.3 Validate content quality (depends on: Task 3.4)
  - No hallucinated content
  - Concise, no over-explaining basics
  - Consistent terminology
  - Code examples compile conceptually
  - Single recommended approach with escape hatches

- ☐ Task 4.4 Run gen-skills-table.py and verify README update (depends on: Task 4.3)
