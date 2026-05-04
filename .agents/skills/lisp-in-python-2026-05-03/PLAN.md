# ☑ Plan: lisp-in-python-2026-05-03 skill

**Depends On:** NONE
**Created:** 2026-05-03T00:00:00Z
**Updated:** 2026-05-03T12:00:00Z
**Current Phase:** ☑ Phase 4
**Current Task:** ☑ Task 4.2

## Source Analysis Summary

Six sources studied, each implementing a minimal Lisp interpreter in Python with different approaches:

- **Norvig (lispy.html)** — Most complete. Full Scheme subset: tokenizer, recursive parser, nested Env class with lexical scoping, Procedure class, eval with 6 special forms (quote, if, define, set!, lambda, procedure-call), standard_env with math operators + list primitives, REPL. ~120 lines. Gold standard reference.
- **ByteGoblin (16-lines)** — Ultra-minimal. No real parser (strips parens only), eval_ast handles add/sub recursively. 16 lines but functionally limited — no variables, no functions, no conditionals. Good for showing the absolute minimum concept.
- **Spatters (gist)** — Class-based types (LispString, LispSymbol, LispInt, LispFloat). Proper tokenizer with error handling (LispSyntaxError), parse_list recursive parser, REPL with input counting. Only has `+` builtin. Foundation for type-safe approach.
- **Zstix (blog)** — Tutorial-style build. Regex-based lexer, recursive parser with number conversion, built-in functions as Python lambdas in global_env, custom Function dataclass, new_env with :parent chain for lexical scoping, get_var for scope lookup, keywords (`:true`/`:false`) instead of booleans, `do` special form, `fn` for user-defined functions. Turing-complete with ~150 lines. Good pedagogical structure.
- **AlJamal (homoiconic-python)** — Unique approach: "Lisp in Lisp" translated to Python. No parser needed — uses Python lists directly as S-expressions. Implements McCarthy's original eval: atom, eq, car, cdr, cons, append, assoc, pairlis primitives. Dynamic scoping via environment alist. Closest to historical Lisp 1.5 manual.
- **Misfra.me (mini-lisp)** — Go implementation inspired by Norvig + mal guide. Added tail-call optimization and call/cc (as catch!). Shows advanced features beyond basic interpreters.

## Cross-Source Patterns

- All use eval-apply cycle (eval expression, apply procedure)
- Tokenization: space-around-parens split vs regex `[()]|[^() \n]+`
- Parsing: recursive descent on token list, `(` starts building list until `)`
- Atoms: try int → float → symbol (Norvig pattern)
- Environment: dict-based with outer chain for lexical scoping
- Special forms evaluated differently than function calls (quote doesn't eval args, if selectively evals)
- Functions: closure = (params, body, captured_env), called by creating new Env frame

## My Interpreter Design

Synthesizing best elements from all sources into a clean, well-documented interpreter covering:

- **Types**: Symbol (str), Number (int|float), List (list), Boolean (True for #t, False for #f), Nil (None for '()), String
- **Parsing**: tokenize + read_from_tokens recursive descent with error messages
- **Environment**: Env class extending dict, outer chain, find() method
- **Procedures**: Procedure class capturing (parms, body, env)
- **Special forms**: quote, if, define, set!, lambda, begin, cond
- **Builtins**: arithmetic (+ - * /), comparison (> < >= <= =), list ops (car cdr cons null? length list), type checks (number? symbol? list? boolean?), misc (not print)
- **REPL**: read-eval-print loop with proper S-expression output formatting

---

## ⚙️ Phase 1 Research & Design

- ☑ Task 1.1 Analyze all six sources and extract unique patterns
  - Compare tokenization approaches (space-split vs regex)
  - Compare parsing strategies (recursive descent variants)
  - Compare environment models (dict+outer vs alist+pairlis)
  - Compare function representation (Procedure class vs dataclass vs closure tuple)
  - Compare special forms coverage across sources
  - Document findings as source analysis notes

- ☑ Task 1.2 Design the interpreter architecture
  - Define type system (Symbol, Number, List, Boolean, Nil, String)
  - Define environment model (Env class with outer chain, find method)
  - Define procedure model (Procedure class with parms/body/env)
  - Define special forms: quote, if, define, set!, lambda, begin, cond
  - Define builtins: + - * / > < >= <= = car cdr cons null? length list not print number? symbol? list? boolean?
  - Define error handling strategy (LispError with context)
  - Decide on S-expression output format

- ☑ Task 1.3 Design the skill structure
  - Determine simple vs complex (will be complex: SKILL.md + reference/)
  - Plan reference files:
    - `reference/01-architecture.md` — interpreter architecture, types, eval-apply cycle
    - `reference/02-source-comparisons.md` — how each source differs, design tradeoffs
    - `reference/03-the-complete-interpreter.md` — full interpreter code with inline documentation
    - `reference/04-extensions.md` — how to extend: tail-call optimization, call/cc, macros, strings, more builtins
  - Plan YAML header fields (name, description, version, tags, category)

## ☑ Phase 2 Write Reference Files

- ☑ Task 2.1 Write `reference/01-architecture.md`
  - Explain eval-apply cycle conceptually
  - Type system: how Python types map to Lisp values
  - Environment model: lexical scoping via Env chain
  - Parsing pipeline: tokenize → read_from_tokens → AST (nested lists)
  - Procedure model: closures as (params, body, env) triple
  - Special forms vs procedures distinction
  (depends on: Task 1.2 , Task 1.3)

- ☑ Task 2.2 Write `reference/02-source-comparisons.md`
  - Norvig: gold standard, Scheme subset, nested Env
  - ByteGoblin: ultra-minimal 16-line proof of concept
  - Spatters: class-based type system with error handling
  - Zstix: tutorial build, Function dataclass, keywords, do form
  - AlJamal: McCarthy's original "Lisp in Lisp" translated to Python
  - Misfra.me: Go implementation with tail-call + call/cc
  - Design tradeoffs: dynamic vs lexical scoping, parserless vs tokenized, alist vs dict environments
  (depends on: Task 1.1)

- ☑ Task 2.3 Write `reference/03-the-complete-interpreter.md`
  - Full Python interpreter code (~150-200 lines)
  - Section by section: types, parsing, environment, procedures, eval, REPL
  - Each section has explanatory prose + code
  - Working examples showing each feature
  (depends on: Task 1.2 , Task 2.1)

- ☑ Task 2.4 Write `reference/04-extensions.md`
  - Tail-call optimization: trampoline pattern, eval-apply restructuring
  - call/cc: continuation capture, simplified version vs full
  - Macros: define-macro, macroexpand before eval
  - Strings: tokenizer extension for quoted strings
  - Comments: semicolon-style in tokenizer
  - Additional builtins: string ops, I/O, more math
  - Derived special forms: let (derived from lambda), when/unless
  (depends on: Task 2.3)

## ☑ Phase 3 Write SKILL.md

- ☑ Task 3.1 Write SKILL.md
  - YAML header with validated fields
  - Overview: what this skill covers, the interpreter subset
  - When to Use: building Lisp interpreters, understanding eval-apply, learning language implementation
  - Core Concepts: homoiconicity, S-expressions, eval-apply cycle, lexical scoping
  - Usage Examples: running the interpreter, evaluating expressions
  - Advanced Topics section linking to reference files
  (depends on: Task 2.1 , Task 2.2 , Task 2.3 , Task 2.4)

## ☑ Phase 4 Validate & Sync

- ☑ Task 4.1 Validate against skill checklist
  - YAML header: valid block, name matches dir, description has WHAT+WHEN
  - Structure: SKILL.md + reference/ with numbered files, no chained refs
  - Content: Overview present, When to Use specific, concise, no hallucination
  - SKILL.md under 500 lines
  (depends on: Task 3.1)

- ☑ Task 4.2 Sync README
  - Run `python3 misc/gen-skills-table.py`
  (depends on: Task 4.1)
