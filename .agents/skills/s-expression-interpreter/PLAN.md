# ☑ Plan: Create s-expression-interpreter skill

**Depends On:** NONE
**Created:** 2026-05-13T12:30:00Z
**Updated:** 2026-05-13T14:00:00Z
**Current Phase:** ☑ Phase 5
**Current Task:** ☑ Task 5.8

## Source Analysis Summary

11 sources fetched and analyzed. Sources fall into 4 categories:

**Category A — Python Lisp/Scheme Interpreters (implementation tutorials):**
- `lwcarani` — Full Lisp interpreter in Python with lexer, parser, AST, SymbolTable with scoping, eval supporting defun/if/format, REPL
- `bytegoblin` — Ultra-minimal 16-line Lisp in Python (tokenize, parse, eval for add/sub only)
- `johnj` — Scheme in Python using Lark parser, tuple-based data model, special forms (quote/cond/if/define/lambda/or/and), TDD workflow

**Category B — C S-expression Library (data structure + parsing):**
- `sfsexp` — Small Fast S-Expression library in C/C++ for parsing, creating, modifying s-expressions as AST; continuation-based parser, embedded systems support

**Category C — Build Your Own Lisp Chapter 9 (C implementation tutorial):**
- `byol-ch9` — Detailed C tutorial on S-Expressions: lval struct with types (ERR/NUM/SYM/SEXPR), heap allocation, parsing with mpc, eval-sexpr, builtin_op, pop/take helpers

**Category D — Lisp/Scheme/Clojure Language Semantics:**
- `eecs390` — Academic notes on Scheme: expressions, definitions, compound values (cons/car/cdr), symbolic data, quoting, functions, parameter passing, recursion, higher-order functions
- `lispstudent-gist` — Python↔Common Lisp cheatsheet: collections, sequences, strings, regex, file I/O, numbers
- `r4rs` — R4RS Scheme standard procedures reference (booleans, equivalence predicates eq/eqv/equal)
- `lisp-lang` — Common Lisp functions tutorial: defun, funcall, apply, multiple return values
- `clojure` — Clojure functions guide: defn/fn, multi-arity, variadic, anonymous #(), apply, let/closures, Java interop
- `r7rs` — R7RS Scheme spec Chapter 4: expression types (variables, literals, procedure calls, lambda, conditionals), formal argument lists

## Overlap with Existing Skills

- `s-expression` — covers s-expression notation/data format conceptually. New skill focuses on **interpreters** that process them.
- `lisp-in-python-2026-05-03` — overlaps on Python Lisp interpreters. New skill has different sources (lwcarani, johnj vs norvig/spatters/zstix) and adds C implementations.
- `scheme-in-python-2026-05-03` — overlaps on Scheme in Python. New skill's johnj source covers similar ground but with Lark parser approach.

## Structure Decision: Complex (SKILL.md + 11 reference files)

Each of the 11 sources becomes its own reference file, organized by what it teaches and which source URL it comes from.

---

## ☑ Phase 1 Analyze Sources and Plan Structure

- ☑ Task 1.1 Fetch all 11 source URLs and read content
  - Verify each source is readable and extractable
  - Categorize sources by topic (Python interpreters, C library, C tutorial, language semantics)
- ☑ Task 1.2 Analyze overlap with existing skills
  - Check s-expression, lisp-in-python-2026-05-03, scheme-in-python-2026-05-03 for content overlap
  - Document what new skill adds vs existing skills
- ☑ Task 1.3 Define reference file structure (11 files, one per source)
  - Map each source to a reference filename and title
  - Determine SKILL.md navigation links

## ☑ Phase 2 Write Reference Files

### Phase 2A — Python Interpreter Sources

- ☑ Task 2.1 Write `reference/01-lwcarani-full-lisp-python.md` (Source: lwcarani)
  - Title: Full Lisp Interpreter in Python by Luke Carani
  - Covers: Type definitions, lexer (str.split), recursive parser/generate_ast, SymbolTable with nested scoping, eval with defun/if/format, REPL, paren matching via map-reduce
  - Goal: Complete working Lisp interpreter with function definitions and recursion

- ☑ Task 2.2 Write `reference/02-bytegoblin-minimal-lisp-python.md` (Source: bytegoblin)
  - Title: Minimal 16-Line Lisp in Python
  - Covers: Ultra-concise tokenize→parse→eval pipeline, add/sub operations only, no variables or functions
  - Goal: Demonstrate minimum viable Lisp interpreter

- ☑ Task 2.3 Write `reference/03-johnj-scheme-python.md` (Source: johnj)
  - Title: Scheme Interpreter in Python with Lark Parser
  - Covers: Lark grammar-based parsing, tuple-based data model (atom/int/float/bool/list), special forms (quote/cond/if/define/lambda/or/and), TDD workflow, printable_value output
  - Goal: Scheme interpreter using modern parser library with test-driven development

### Phase 2B — C Implementation Sources

- ☑ Task 2.4 Write `reference/04-sfsexp-c-library.md` (Source: sfsexp GitHub)
  - Title: Small Fast S-Expression Library (sfsexp) in C/C++
  - Covers: sexp_t data structure, parse_sexp/read_one_sexp API, continuation-based parser, print_sexp serialization, destroy_sexp cleanup, linked-list internal representation, embedded systems support, autoconf build
  - Goal: Production-quality s-expression parsing/manipulation library for C programs

- ☑ Task 2.5 Write `reference/05-byol-ch9-s-expressions-c.md` (Source: buildyourownlisp)
  - Title: S-Expressions in C — Build Your Own Lisp Chapter 9
  - Covers: lval struct with enum types (ERR/NUM/SYM/SEXPR), heap allocation (malloc/free), stack vs heap concepts, mpc parser rules, constructors/destructors (lval_num/lval_sym/lval_sexpr/lval_del), lval_add/lval_pop/lval_take, recursive eval-sexpr, builtin_op for arithmetic, forward declarations
  - Goal: Teach C memory management through building s-expression data structures and evaluator

### Phase 2C — Scheme Language Semantics Sources

- ☑ Task 2.6 Write `reference/06-eecs390-scheme-functional.md` (Source: eecs390)
  - Title: Introduction to Scheme — Functional Programming Notes
  - Covers: Scheme expressions (prefix notation, combinations), special forms (if/and/or/not), define for variables and procedures, lambda anonymous functions, compound values (cons/car/cdr, proper/improper lists), symbolic data and quoting, variadic arguments, parameter passing modes (call by value/reference/result/name), recursion and activation records
  - Goal: Academic foundation for understanding Scheme semantics before building interpreters

- ☑ Task 2.7 Write `reference/07-r4rs-standard-procedures.md` (Source: r4rs)
  - Title: R4RS Scheme — Standard Procedures Reference
  - Covers: Boolean values (#t/#f, only #f is false), equivalence predicates (eq?/eqv?/equal?/equalp?), their discrimination levels and behavior on different types
  - Goal: Authoritative reference for Scheme built-in procedure semantics

- ☑ Task 2.8 Write `reference/08-r7rs-expressions.md` (Source: r7rs)
  - Title: R7RS Scheme — Expression Types Specification
  - Covers: Primitive expressions (variable references, literal expressions with quote/'<datum>, procedure calls), lambda semantics (formal argument lists: fixed, variadic, dotted), conditional forms, unspecified evaluation order note vs other Lisps
  - Goal: Modern Scheme specification for expression evaluation rules

### Phase 2D — Common Lisp and Clojure Sources

- ☑ Task 2.9 Write `reference/09-lispstudent-cl-cheatsheet.md` (Source: lispstudent gist)
  - Title: Python to Common Lisp Cheatsheet
  - Covers: Equality predicates tower (eq/eql/equal/equalp/=), sequence types (list/vector/string), indexing/slicing/mutation, hash-table/alist/plist maps, LOOP macro, string operations, CL-PPCRE regex, file I/O with with-open-file, numeric tower, Alexandria/Serapeum augmentations
  - Goal: Reference for translating Python idioms to Common Lisp

- ☑ Task 2.10 Write `reference/10-lisp-lang-functions.md` (Source: lisp-lang.org)
  - Title: Common Lisp Functions Guide
  - Covers: defun for named functions, anonymous functions with lambda, funcall vs apply for indirect calling, multiple return values with values/multiple-value-bind/nth-value
  - Goal: Quick reference for Common Lisp function definition and invocation patterns

- ☑ Task 2.11 Write `reference/11-clojure-functions.md` (Source: clojure.org)
  - Title: Clojure Functions Guide
  - Covers: defn vs fn, multi-arity functions, variadic with &, anonymous #() syntax with %/%1/%2/%&, apply, let for locals, closures, Java interop (invoking Java methods vs functions)
  - Goal: Reference for Clojure function semantics and JVM interop

## ☑ Phase 3 Write SKILL.md

- ☑ Task 3.1 Draft YAML header
  - name: s-expression-interpreter
  - description covering WHAT (build/understand s-expression interpreters in Python and C) and WHEN (building Lisp/Scheme interpreters, parsing s-expressions, implementing eval-apply)
  - tags, category, external_references (all 11 URLs)
- ☑ Task 3.2 Write Overview section
  - What s-expression interpreters are
  - Why they matter (homoiconicity, code-as-data, eval-apply cycle)
  - Scope: Python implementations, C implementations, language semantics
- ☑ Task 3.3 Write When to Use section
  - Specific scenarios for loading this skill
- ☑ Task 3.4 Write Core Concepts section
  - Key concepts shared across sources (homoiconicity, eval-apply, s-expression structure, lexical scoping)
- ☑ Task 3.5 Write Advanced Topics navigation hub
  - Link to all 11 reference files with brief descriptions

## ☑ Phase 4 Validate and Finalize

- ☑ Task 4.1 Run structural validator
  - `bash scripts/validate-skill.sh --strict .agents/skills/s-expression-interpreter`
- ☑ Task 4.2 LLM judgment checks
  - Content accuracy (no hallucinated content)
  - Consistent terminology across files
  - Concise writing without over-explanation
  - Single recommended approach where applicable
- ☑ Task 4.3 Regenerate README.md skills table
  - `bash scripts/gen-skills-table.sh`

## ☑ Phase 5 Add Minimal Scheme Interpreter with Comment Support

Produce a final minimalist Python implementation of a Scheme-syntax parser and interpreter as a new reference file. The implementation builds on the lwcarani pattern (tokenize→parse→eval with SymbolTable) but targets **Scheme** semantics (R4RS/R7RS) rather than Common Lisp. Key addition: proper `;` comment handling in the tokenizer.

### Scheme Comment Semantics

Scheme supports three comment styles:
- **`;` line comments**: `;` to end of line. Four variants by indentation depth (`;;;` library, `;;` section, `;` code). Most common.
- **`#| ... |#` block comments**: Multi-line, but NOT nestable in R4RS (R7RS allows nesting).
- **`#! ... !#` nested comments**: Implementation-defined, used by Chicken/Guile.

For our minimalist parser, we support `;` line comments (the universal standard) during tokenization. Block comments are deferred — they require stateful multi-line tracking which adds complexity beyond the "minimal" scope. The tokenizer strips `;` to end-of-line before paren-padding.

### Implementation Design

The minimalist interpreter supports:
- **Tokenization**: Strip `;` comments, pad parens, split on whitespace. Handles strings (comments inside strings are preserved).
- **Parsing**: Recursive descent, returns nested Python lists as AST. Atoms: int, float, symbol.
- **Evaluation**: eval-apply cycle with SymbolTable for lexical scoping.
- **Scheme builtins**: `+`, `-`, `*`, `/`, `<`, `>`, `<=`, `>=`, `=`
- **Special forms**: `if`, `define` (variable + procedure), `lambda`, `quote`/`'`
- **Procedures**: User-defined via `(define (f x) body)` → stored as `(params, body, env)` tuple for closures.
- **REPL**: Read-eval-print loop with error handling.

### Tasks

- ☑ Task 5.1 Study Scheme comment semantics and write the tokenizer
  - Implement `tokenize(input)` that strips `;` comments (respecting string boundaries)
  - Pad parens with whitespace, split on whitespace
  - Test: `(+ 1 2) ; add one and two` → tokens without comment
  - Test: `"hello ; world"` → string preserved with semicolon inside

- ☑ Task 5.2 Write the parser
  - Implement `parse(tokens)` — recursive descent, returns nested lists
  - Atoms: int, float, symbol (str)
  - Handle `'` prefix as `(quote ...)`
  - Test parsing of multi-expression input

- ☑ Task 5.3 Write the evaluator with Scheme semantics
  - `eval(expr, env)` — eval-apply cycle
  - Numbers and symbols → lookup in env
  - Lists → procedure call or special form
  - `if`: evaluate predicate, then consequent or alternative
  - `define` (variable): bind name to evaluated value
  - `define` (procedure): `(define (f x y) body)` → store closure
  - `lambda`: return closure (params, body, captured env)
  - `quote`: return data without evaluation
  - Procedure application: eval operator + args, apply
  - Built-in arithmetic operators from Python's `operator` module

- ☑ Task 5.4 Write the REPL and error handling
  - Multi-line input support (continue on unmatched parens)
  - Print results in Scheme notation (`#t`/`#f`, lists with spaces)
  - Graceful error messages for undefined variables, bad syntax

- ☑ Task 5.5 Test the full implementation in a temp directory
  - Run comprehensive test cases covering all features
  - Verify comment handling works correctly
  - Verify closures capture environment
  - Verify procedure definitions and recursion
  - Fix any issues found (parser two-function pattern, string tokenizer, if arity, lambda as head)

- ☑ Task 5.6 Write `reference/12-minimal-scheme-interpreter-python.md`
  - Title: Minimal Scheme Interpreter in Python with Comment Support
  - Covers: Full working implementation (tokenize→parse→eval→REPL), comment semantics, Scheme-specific features
  - Include the complete code as a single copy-pasteable block
  - Document design decisions and limitations
  - Show test cases and expected output

- ☑ Task 5.7 Update SKILL.md Advanced Topics section
  - Add link to new reference file in Python Interpreter Implementations section

- ☑ Task 5.8 Validate and regenerate README
  - Run structural validator on updated skill (25/25 checks passed, 0 errors)
  - Regenerate README.md skills table (238 skills)
