---
name: lambda-calculus-and-lisp-2026-05-12
description: Covers the relationship between lambda calculus and Lisp, including McCarthy's EVAL, Church encodings in Scheme, the Y combinator for nameless recursion, and Lisp's hardware origins vs pure lambda theory. Use when implementing lambda calculus in Lisp/Scheme, enabling recursion without named functions via fixed-point combinators, encoding data types as pure functions with Church encodings, or studying the historical divergence between Lisp and lambda calculus.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - lambda-calculus
  - lisp
  - scheme
  - y-combinator
  - church-encoding
  - recursion
  - eval
category: language-runtime
external_references:
  - https://babbagefiles.xyz/lambda-calculus-and-lisp-01/
  - https://babbagefiles.xyz/lambda-calculus-and-lisp-02-recursion/
  - https://wal.sh/research/lambda-calculus-in-scheme.html
  - https://8dcc.github.io/programming/understanding-y-combinator.html
---

# Lambda Calculus and Lisp

## Overview

This skill covers the practical and theoretical intersection of lambda calculus and Lisp. While lambda calculus is a minimal formal system with only variables, abstractions, and applications, Lisp was designed for list processing on the IBM 704 with hardware-specific operations like `car` and `cdr`. McCarthy borrowed `LAMBDA` notation from Church but did not intend Lisp as a direct implementation of lambda calculus — as he himself acknowledged, he "didn't understand the lambda calculus, really."

Despite this divergence, Lisp and lambda calculus share deep connections: `lambda` expressions bind variables and substitute arguments, `eval` provides self-interpretation (homoiconicity), and the Y combinator enables recursion in systems without named self-reference. This skill covers how to implement lambda calculus concepts in Scheme, encode data types as pure functions using Church encodings, and understand the historical relationship between these two foundational systems.

## When to Use

- Implementing a lambda calculus interpreter or evaluator in Lisp/Scheme
- Understanding how recursion works without named functions (Y combinator, fixed-point combinators)
- Encoding data types (numbers, booleans, lists) as pure lambda terms in Scheme
- Studying McCarthy's original `eval` and the `LAMBDA`/`LABEL` mechanism
- Building recursive functions in Emacs Lisp or Scheme with tail-call optimization
- Understanding why Lisp is not a direct realization of lambda calculus

## Core Concepts

### LAMBDA in Lisp vs Lambda Calculus

In McCarthy's 1958 Lisp, `LAMBDA` was borrowed from Church's lambda calculus as a notation for anonymous functions that bind variables:

```lisp
(LAMBDA (x y z) (+ (* y x) (* z x)))
;; Applied to 5, 2, 3:
;; (+ (* 2 5) (* 3 5)) = 25
```

In pure lambda calculus, the equivalent is `λx.λy.λz.body` — functions take exactly one argument (curried). Lisp's `LAMBDA` accepts multiple parameters simultaneously, already a departure from pure lambda calculus.

### EVAL: The Lisp Interpreter in Lisp

McCarthy's 1960 paper defined `eval` as a recursive function that interprets Lisp expressions. This is the foundation of homoiconicity — code as data:

```lisp
(label eval
       (lambda (e a)
         (cond
           ((atom e) (assoc e a))
           ((atom (car e))
            (cond
              ((eq (car e) 'quote) (cadr e))
              ((eq (car e) 'atom)  (atom  (eval (cadr e) a)))
              ((eq (car e) 'eq)    (eq    (eval (cadr e) a)
                                          (eval (caddr e) a)))
              ((eq (car e) 'car)   (car   (eval (cadr e) a)))
              ((eq (car e) 'cdr)   (cdr   (eval (cadr e) a)))
              ((eq (car e) 'cons)  (cons  (eval (cadr e) a)
                                          (eval (caddr e) a)))
              ((eq (car e) 'cond)  (evcon (cdr e) a))
              ('t                  (eval (cons (assoc (car e) a)
                                               (cdr e))
                                         a))))
           ((eq (caar e) 'label)   (eval (cons (caddar e) (cdr e))
                                         (cons (list (cadar e) (car e)) a)))
           ((eq (caar e) 'lambda)  (eval (caddar e)
                                         (append (pair (cadar e)
                                                       (evlis (cdr e) a))
                                                 a))))))
```

This `eval`, combined with helper functions (`evcon`, `evlis`, `assoc`, `pair`), forms a complete Lisp interpreter. Steve Russell compiled this theoretical code into IBM 704 machine code, creating the first Lisp interpreter.

### car/cdr: Hardware Origins, Not Pure Theory

`car` and `cdr` come from the IBM 704's memory architecture, not lambda calculus:
- **CAR** = Contents of the Address part of the Register
- **CDR** = Contents of the Decrement part of the Register

Lists are singly-linked structures where each node has a value field (`car`) and a next field (`cdr`). The list `(a b c)` is `(cons a (cons b (cons c nil)))`. Pure lambda calculus has no `car`, `cdr`, `cons`, or `eq` — these must be encoded from the three basic constructs.

### Recursion Without Names: The Y Combinator

Pure lambda calculus has no named functions, so a term cannot call itself by name. The Y combinator solves this by finding a fixed point of any function `f`:

```
Y f = f (Y f)
```

In Scheme (with beta-abstraction for strict evaluation):

```scheme
(define Y
  (lambda (f)
    ((lambda (x) (f (lambda (n) ((x x) n))))
     (lambda (x) (f (lambda (n) ((x x) n)))))))
```

This enables recursion in systems without `define` or named self-reference.

## Usage Examples

### Church Numerals in Scheme

Encode natural numbers as function application counts:

```scheme
(define lc-zero (lambda (f) (lambda (x) x)))
(define lc-succ (lambda (n) (lambda (f) (lambda (x) (f ((n f) x))))))

(define (church-to-int n)
  ((n (lambda (x) (+ x 1))) 0))

(define lc-one (lc-succ lc-zero))
(define lc-two (lc-succ lc-one))

(church-to-int lc-zero) ; 0
(church-to-int lc-two)  ; 2
```

### Factorial with the Y Combinator

Define factorial without naming the recursive function:

```scheme
(define fact-generator
  (lambda (self)
    (lambda (n)
      (if (= n 0)
          1
          (* n (self (- n 1)))))))

(define fact (Y fact-generator))
(fact 5) ; 120
```

### Church Booleans and Conditionals

Encode logic as selection functions:

```scheme
(define lc-true (lambda (x) (lambda (y) x)))
(define lc-false (lambda (x) (lambda (y) y)))

(define lc-if
  (lambda (condition)
    (lambda (then-val)
      (lambda (else-val)
        ((condition then-val) else-val)))))

(((lc-if lc-true) "yes") "no") ; "yes"
```

### Tail-Recursive Fibonacci in Emacs Lisp

Using `cl-labels` with accumulator for tail-call optimization:

```lisp
(defun fib (n)
  (cl-labels ((fib* (a b accum)
                (let* ((accum (cons a accum))
                       (accum-lng (length accum)))
                  (if (< n accum-lng)
                      (nreverse accum)
                    (fib* b (+ b a) accum)))))
    (fib* 0 1 nil)))

(fib 10) ; (0 1 1 2 3 5 8 13 21 34)
```

## Advanced Topics

**History and Origins**: McCarthy's EVAL, the IBM 704 hardware origins of car/cdr, "Lisp ≠ Lambda Calculus" — why Lisp diverged from pure theory → [History and Lisp Origins](reference/01-history-and-lisp.md)

**Recursion in Lisp**: Tail-call optimization, `cl-labels`, accumulator patterns, streams, and the `excessive-lisp-nesting` limits in Emacs Lisp → [Recursion in Lisp](reference/02-recursion-in-lisp.md)

**Y Combinator and Fixed-Points**: Derivation of Y g = g(Y g), beta-abstraction for strict evaluation, Z combinator variant, complete factorial examples → [Y Combinator and Fixed-Points](reference/03-y-combinator-and-fixed-points.md)

**Church Encodings in Scheme**: Booleans, numerals with arithmetic, pairs, lists with map/filter/fold, comparison operations, and recursion on Church terms → [Church Encodings in Scheme](reference/04-church-encodings-in-scheme.md)
