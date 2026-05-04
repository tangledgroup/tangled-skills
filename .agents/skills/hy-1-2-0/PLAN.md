# ☑ Plan: Hy 1.2.0 Skill Generation

**Depends On:** NONE
**Created:** 2026-05-03T00:00:00Z
**Updated:** 2026-05-03T00:05:00Z
**Current Phase:** ☑ Phase 4
**Current Task:** ☑ Task 4.2

This plan generates a complex skill for Hy 1.2.0, a Lisp dialect embedded in Python. Sources have been crawled via Jina Reader from the official docs (hylang.org/hy/doc/v1.2.0/), GitHub repos (hylang/hy, hylang/py2hy), and the homepage.

Structure: SKILL.md (hub) + 8 reference files covering all major domains.

## ⚙️ Phase 1 Research & Analysis

- ☑ Task 1.1 Crawl and analyze all source URLs
  - Completed via Jina Reader: tutorial, syntax, semantics, macros, interop, CLI, REPL, env vars, whyhy, hacking, model_patterns, API reference (all sections)
  - Also crawled: py2hy GitHub repo, hylang homepage
  - Status: All content collected and analyzed
- ☑ Task 1.2 Map content domains to reference files (depends on: Task 1.1)
  - Domain mapping determined:
    - 01: Core syntax & data types (literals, identifiers, models, expressions)
    - 02: Control flow & functions (if/cond/when/while/for/comprehensions/defn/fn/yield)
    - 03: Macros & metaprogramming (defmacro, quasiquoting, reader macros, scoping, pitfalls)
    - 04: Classes & modules (defclass, import/require, packaging, interop)
    - 05: CLI tools & REPL (hy/hy2py/hyc commands, REPL config, env vars)
    - 06: Python interoperability (mangling, py/pys macros, using Hy from Python, py2hy)
    - 07: Semantics & gotchas (implicit names, eval order, bytecode caching, tracebacks)
    - 08: Advanced topics (model patterns, hy.I/hy.R, hy.eval/hy.macroexpand, gensym)

## ☑ Phase 2 Write SKILL.md

- ☑ Task 2.1 Generate YAML header (depends on: Phase 1 - Task 1.2)
  - name: hy-1-2-0, version: "1.2.0", category: language-runtime
  - Description formula: WHAT + capabilities + WHEN
  - Tags: hy, hylang, lisp, python-embedded, macros, metaprogramming, s-expression
- ☑ Task 2.2 Write SKILL.md body (depends on: Task 2.1)
  - Overview: Hy as Lisp embedded in Python, key differentiators
  - When to Use: specific scenarios for invoking this skill
  - Quick start examples: hello world, basic operations, defn example
  - Advanced Topics navigation hub linking all 8 reference files
  - Keep under 500 lines

## ☑ Phase 3 Write Reference Files

- ☑ Task 3.1 Write reference/01-core-syntax.md (depends on: Phase 2 - Task 2.2)
  - Covers: forms, models, literals (int/float/complex/bool/None/str/bytes/tuple/list/set/dict), identifiers, symbols, keywords, dotted identifiers, mangling, strings (bracket strings, f-strings), expressions, sequential forms, syntactic sugar (' ` ~ ~@ #* #**), comments, shebang, discard prefix (#_)
  - Sources: syntax chapter, tutorial literals section
- ☑ Task 3.2 Write reference/02-control-flow-functions.md (depends on: Phase 2 - Task 2.2)
  - Covers: setv/setx/let/global/nonlocal/del, if/when/cond/match, while/for/break/continue, comprehensions (lfor/sfor/dfor/gfor), defn/fn/return/yield/await, decorators, type parameters, annotations (#^/annotate), chainc/assert
  - Sources: API reference (conditionals, loops, comprehensions, functions sections), tutorial
- ☑ Task 3.3 Write reference/03-macros-metaprogramming.md (depends on: Phase 2 - Task 2.2)
  - Covers: defmacro basics, quasiquoting (quasiquote/unquote/unquote-splice), reader macros (defreader, &reader API), macro scoping (core/global/local), require vs import, eval-when-compile/eval-and-compile/do-mac, pitfalls (name shadowing, gensym, hy.I/hy.R for subroutines), export
  - Sources: macros chapter, API reference (macros section)
- ☑ Task 3.4 Write reference/04-classes-modules.md (depends on: Phase 2 - Task 2.2)
  - Covers: defclass syntax (decorators, type params, inheritance), import syntax variants, require for macros, packaging Hy libraries (__init__.py pattern, PyPI classifiers), hy.I one-shot imports, __all__ and _hy_export_macros
  - Sources: API reference (classes, modules sections), interop chapter (packaging section)
- ☑ Task 3.5 Write reference/05-cli-repl.md (depends on: Phase 2 - Task 2.2)
  - Covers: hy command (--spy, --repl-output-fn, -m), hy2py (usage, security warning), hyc (bytecode compilation), REPL class (hy.REPL, run(), output functions, special vars *1/*2/*3/*e), startup files (HYSTARTUP, repl-ps1/repl-ps2), environment variables (HY_HISTORY, HY_SHOW_INTERNAL_ERRORS, HY_MESSAGE_WHEN_COMPILING)
  - Sources: CLI chapter, REPL chapter, env_var chapter
- ☑ Task 3.6 Write reference/06-python-interop.md (depends on: Phase 2 - Task 2.2)
  - Covers: mangling rules and hy.mangle/hy.unmangle, keyword mincing for Python reserved words, py/pys macros for embedding Python code, using Hy from Python (hy.eval, hy.read-many), using Python from Hy (import, sys.executable caveat), py2hy tool (CLI and programmatic API)
  - Sources: interop chapter, py2hy repo
- ☑ Task 3.7 Write reference/07-semantics-gotchas.md (depends on: Phase 2 - Task 2.2)
  - Covers: implicit `import hy` in every module, _hy_ temp variable prefix, unspecified evaluation order of function arguments, bytecode regeneration behavior (stale macro expansions), traceback positioning limitations, when to use py/pys vs Hy-native constructs
  - Sources: semantics chapter
- ☑ Task 3.8 Write reference/08-advanced-topics.md (depends on: Phase 2 - Task 2.2)
  - Covers: model patterns (hy.model-patterns parser combinators), hy.eval/hy.macroexpand/hy.macroexpand-1, hy.gensym for unique symbols, hy.as-model promotion, hy.repr/hy.repr-register, hy.HyReader/hy.Reader API, hyrule library overview, recommended libraries (toolz, metadict)
  - Sources: model_patterns chapter, API reference (Hy module section, Readers section), tutorial recommended libraries

## ⚙️ Phase 4 Validation & Sync

- ☑ Task 4.1 Validate all files against skill checklist (depends on: Phase 3 - Task 3.8)
  - YAML header checks (name regex, description length, version, MIT license)
  - Structure checks (directory name matches, SKILL.md under 500 lines, reference files flat with zero-padded numbering, no chained references)
  - Content checks (no hallucinated content, concise, consistent terminology, all from crawled sources)
- ☑ Task 4.2 Regenerate README skills table (depends on: Task 4.1)
  - Run: `python3 misc/gen-skills-table.py`
