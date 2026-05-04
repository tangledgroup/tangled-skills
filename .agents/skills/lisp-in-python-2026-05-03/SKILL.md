---
name: lisp-in-python-2026-05-03
description: "Complete guide to building a minimal Lisp interpreter in Python, synthesized from six independent implementations (Norvig's lispy, ByteGoblin's 16-line proof, Spatters' typed approach, Zstix's tutorial, AlJamal's homoiconic Python, Misfra.me's mini-lisp with tail-call/call/cc). Covers the eval-apply cycle, recursive descent parsing, lexical scoping via environment chains, user-defined closures, special forms (quote, if, define, set!, lambda, begin, cond), built-in procedures, and a REPL. Includes extension patterns: tail-call optimization, call/cc continuations, macros with quasiquote, strings, derived forms (let, when, unless, do). Use when building a Lisp interpreter from scratch in Python, understanding how programming language interpreters work, learning the eval-apply cycle, implementing lexical scoping and closures, or studying homoiconicity where code and data share the same representation."
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026-05-03"
tags:
  - lisp
  - interpreter
  - python
  - eval-apply
  - homoiconicity
  - lexical-scoping
category: language-runtime
external_references:
  - https://norvig.com/lispy.html
  - https://bytegoblin.io/blog/write-a-lisp-in-16-lines-of-python.mdx
  - https://gist.github.com/spatters/bdd0c6ce2863bda0de61e8c0ae097e84
  - https://zstix.io/posts/make-a-lisp-in-python/
  - https://aljamal.substack.com/p/homoiconic-python
  - https://misfra.me/2019/03/mini-lisp/
---

# Lisp in Python — Minimal Interpreter Guide

## Overview

Build a complete Scheme-like Lisp interpreter in ~200 lines of pure Python. The interpreter supports arithmetic, comparison, variables, user-defined functions with lexical scoping, conditionals, list operations, and a REPL — all using the eval-apply cycle that powers every Lisp implementation.

The design synthesizes six independent implementations studied across different approaches: Norvig's gold-standard Scheme subset, ByteGoblin's ultra-minimal 16-line proof of concept, Spatters' class-based type system, Zstix's step-by-step tutorial build, AlJamal's direct translation of McCarthy's original "Lisp in Lisp", and Misfra.me's Go implementation with tail-call optimization and call/cc.

## When to Use

- Building a Lisp interpreter from scratch in Python
- Understanding how programming language interpreters work (parsing, evaluation, scoping)
- Learning the eval-apply cycle — the core mechanism of all Lisp implementations
- Implementing lexical scoping and closures
- Studying homoiconicity (code-as-data property of Lisp)
- Extending a minimal interpreter with advanced features (macros, continuations, tail-call optimization)

## Core Concepts

**Homoiconicity**: In Lisp, code is data. Programs are represented as lists — the same data structure used for everything else. This means the interpreter can manipulate programs as data structures, enabling macros and metaprogramming. A program `(+ 1 2)` is just the list `['+', 1, 2]`.

**S-expressions**: The fundamental notation. Atoms (numbers, symbols) evaluate to values. Lists `(proc arg1 arg2)` represent function calls. Parentheses are not grouping — they denote list structure.

**Eval-apply cycle**: The interpreter has two operations. `eval` takes an expression and environment, returns a value. `apply` takes a procedure and argument values, returns a result. Eval dispatches on expression type; for procedure calls, it evals the operator and all arguments, then applies the result. Apply creates a new environment frame and calls eval on the body. This cycle is recursive until expressions reduce to atoms.

**Lexical scoping**: A function captures the environment where it was defined, not where it's called. Environments form a chain: each has an `outer` reference. Variable lookup walks from innermost outward. This enables proper closures — functions that remember their defining context.

**Special forms vs procedures**: Most expressions evaluate all sub-expressions before applying (applicative order). Special forms break this rule: `quote` returns its argument without evaluation, `if` evaluates only one branch, `define` doesn't evaluate the variable name. The eval function handles special forms explicitly before falling through to the general procedure-call case.

## Usage Examples

Start the REPL:

```bash
python lispy.py
```

Run a file:

```bash
python lispy.py program.lisp
```

Basic expressions in the REPL:

```
lispy> (+ 1 2 3)
6

lispy> (define x 10)
x

lispy> (* x x)
100

lispy> (if (> x 5) "big" "small")
big
```

Define and call recursive functions:

```
lispy> (define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
fact

lispy> (fact 10)
3628800

lispy> (define fib (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2))))))
fib

lispy> (fib 10)
55
```

Higher-order functions and closures:

```
lispy> (define double (lambda (f) (lambda (x) (f (f x)))))
double

lispy> ((double (lambda (x) (* 2 x))) 5)
20
```

List operations:

```
lispy> (cons 0 (list 1 2 3))
(0 1 2 3)

lispy> (car (list 1 2 3))
1

lispy> (cdr (list 1 2 3))
(2 3)

lispy> (length (list 1 2 3 4))
4

lispy> (null? '())
#t
```

Multi-way conditionals and sequencing:

```
lispy> (cond ((= 1 2) "no") ((> 1 0) "yes") ("else" "default"))
yes

lispy> (begin (define a 1) (define b 2) (+ a b))
3
```

## Advanced Topics

**Interpreter Architecture**: Eval-apply cycle, type system, parsing pipeline, environment model, procedure closures, special forms → [Architecture](reference/01-architecture.md)

**Source Comparisons**: How each of the six implementations differs — Norvig's Scheme subset, ByteGoblin's 16-line proof, Spatters' typed approach, Zstix's tutorial, AlJamal's homoiconic Python, Misfra.me's Go with tail-call → [Source Comparisons](reference/02-source-comparisons.md)

**The Complete Interpreter**: Full ~200-line Python source with inline documentation, section-by-section breakdown, and running examples → [Complete Interpreter](reference/03-the-complete-interpreter.md)

**Extensions**: Tail-call optimization, call/cc continuations, macros with quasiquote, strings, derived forms (let, when, unless, do), additional builtins → [Extensions](reference/04-extensions.md)
