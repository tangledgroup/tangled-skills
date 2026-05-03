---
name: hy-1-2-0
description: Lisp dialect embedded in Python providing prefix S-expression syntax, compile-time macros, quasiquoting, reader macros, and seamless access to all Python built-ins and third-party libraries. Use when writing Hy programs, creating or using Hy macros, converting between Python and Hy code with hy2py/py2hy, debugging Hy compilation or bytecode caching issues, configuring the Hy REPL, or building Lisp-style metaprogramming on the Python platform.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.2.0"
tags:
  - hy
  - hylang
  - lisp
  - python-embedded
  - macros
  - metaprogramming
  - s-expression
category: language-runtime
external_references:
  - https://hylang.org/
  - https://github.com/hylang/hy/tree/1.2.0
  - https://github.com/hylang/py2hy
compatibility: Python 3.10+
---

# Hy 1.2.0 (Crackers and Snacks)

## Overview

Hy is a multi-paradigm Lisp dialect compiled to Python AST. It uses prefix S-expression syntax with parentheses-delimited forms, compiles to Python bytecode, and runs on CPython or PyPy. All Python built-ins and third-party libraries are directly available. Hy adds Lisp features: compile-time macros (regular and reader), quasiquoting, homoiconic model objects, bracket strings, f-strings with Hy expressions, and generalized n-ary operators.

Hy is not a standalone language — it compiles to Python AST which Python executes. Runtime semantics follow Python exactly; only syntax and compile-time features differ.

## When to Use

- Writing programs in Hy's Lisp-style prefix syntax
- Creating or debugging macros (regular macros with `defmacro`, reader macros with `defreader`)
- Converting Python code to Hy (`hy2py` for Hy→Python, `py2hy` for Python→Hy)
- Configuring the Hy REPL (startup files, custom output functions, prompts)
- Debugging compilation issues (stale bytecode, macro expansion order, implicit names)
- Building DSLs or domain-specific syntax extensions via reader macros
- Using Hy's metaprogramming tools (`hy.eval`, `hy.macroexpand`, model patterns)
- Packaging Hy libraries for PyPI

## Quick Start

**Hello world:**

```hy
(print "Hy, world!")
```

**Basic operations (prefix syntax, n-ary operators):**

```hy
(+ 1 2 3)          ; => 6
(- (* (+ 1 3 88) 2) 8)  ; => 176
(setv x 42)        ; variable assignment
(= x 42)           ; equality (== in Python, = in Hy)
```

**Functions:**

```hy
(defn fib [n]
  (if (< n 2)
    n
    (+ (fib (- n 1)) (fib (- n 2)))))

(print (fib 8))  ; => 21
```

**Macros (compile-time code generation):**

```hy
(defmacro do-while [condition #* body]
  `(do
     ~@body
     (while ~condition
       ~@body)))

(setv x 0)
(do-while x
  (print "Executed once."))
```

**Run and translate:**

```bash
hy myprogram.hy              ; run Hy file
hy                           ; start REPL
echo "(+ 1 2)" | hy2py       ; => 1 + 2
python3 -m py2hy code.py     ; Python → Hy
hyc compile myfile.hy        ; pre-compile to bytecode
```

## Advanced Topics

**Core Syntax & Data Types**: Forms, models, literals, identifiers, mangling, strings, expressions, syntactic sugar → [Core Syntax](reference/01-core-syntax.md)

**Control Flow & Functions**: Conditionals, loops, comprehensions, `defn`/`fn`, decorators, type parameters, annotations → [Control Flow & Functions](reference/02-control-flow-functions.md)

**Macros & Metaprogramming**: Regular macros, reader macros, quasiquoting, macro scoping, pitfalls, compile-time evaluation → [Macros & Metaprogramming](reference/03-macros-metaprogramming.md)

**Classes & Modules**: `defclass`, `import`/`require`, packaging Hy libraries, one-shot imports → [Classes & Modules](reference/04-classes-modules.md)

**CLI Tools & REPL**: `hy`/`hy2py`/`hyc` commands, REPL configuration, startup files, environment variables → [CLI Tools & REPL](reference/05-cli-repl.md)

**Python Interoperability**: Mangling, `py`/`pys` macros, using Hy from Python, `py2hy` converter → [Python Interoperability](reference/06-python-interop.md)

**Semantics & Gotchas**: Implicit `import hy`, evaluation order, bytecode caching, tracebacks → [Semantics & Gotchas](reference/07-semantics-gotchas.md)

**Advanced Topics**: Model patterns, `hy.eval`/`hy.macroexpand`, `hy.gensym`, reader API, recommended libraries → [Advanced Topics](reference/08-advanced-topics.md)
