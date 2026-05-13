"""Tests for the Scheme interpreter.

Run: python3 test-scheme-interpreter.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from full_scheme_interpreter import scheme_eval_repr, scheme_eval, make_global_env, NIL, Pair


passed = 0
failed = 0
errors = []


def check(label, source, expected_repr, env=None):
    """Check that evaluating source produces expected_repr."""
    global passed, failed, errors
    try:
        result = scheme_eval_repr(source, env)
        if result == expected_repr:
            passed += 1
        else:
            failed += 1
            errors.append(f"FAIL {label}: expected {expected_repr!r}, got {result!r}")
    except Exception as e:
        failed += 1
        errors.append(f"ERROR {label}: {e}")


# =========================================================================
# Arithmetic
# =========================================================================

print("--- Arithmetic ---")
check("add two", "(+ 1 2)", "3")
check("add many", "(+ 1 2 3 4)", "10")
check("subtract", "(- 10 3)", "7")
check("negate", "(- 5)", "-5")
check("multiply", "(* 3 4)", "12")
check("divide", "(/ 10 2)", "5.0")
check("nested", "(+ (* 3 5) (- 10 6))", "19")
check("float div", "(/ 7 2)", "3.5")

# =========================================================================
# Comparisons
# =========================================================================

print("--- Comparisons ---")
check("less than", "(< 1 2)", "#t")
check("greater than", "(> 3 2)", "#t")
check("equal", "(= 5 5)", "#t")
check("not equal", "(= 5 6)", "#f")
check("leq", "(<= 3 3)", "#t")
check("geq", "(>= 3 3)", "#t")
check("leq false", "(<= 4 3)", "#f")

# =========================================================================
# Booleans
# =========================================================================

print("--- Booleans ---")
check("true literal", "#t", "#t")
check("false literal", "#f", "#f")
check("zero is true", "(if 0 'yes 'no)", "yes")
check("not true", "(not #t)", "#f")
check("not false", "(not #f)", "#t")
check("not zero", "(not 0)", "#f")

# =========================================================================
# Conditionals (if)
# =========================================================================

print("--- If ---")
check("if true branch", "(if #t 1 2)", "1")
check("if false branch", "(if #f 1 2)", "2")
check("if no alt true", "(if #t 42)", "42")
check("if comparison", "(if (< 1 2) 'yes 'no)", "yes")
check("abs positive", """(define (abs x) (if (< x 0) (- x) x))
(abs 5)""", "5")
check("abs negative", """(define (abs x) (if (< x 0) (- x) x))
(abs -3)""", "3")

# =========================================================================
# cond
# =========================================================================

print("--- Cond ---")
check("cond first", "(cond ((< 1 2) 'a) ((< 3 4) 'b))", "a")
check("cond second", "(cond ((< 2 1) 'a) ((< 3 4) 'b))", "b")
check("cond else", "(cond ((< 2 1) 'a) (else 'default))", "default")
check("cond multi-body", "(cond ((< 1 2) (+ 1 2) (+ 3 4)))", "7")

# =========================================================================
# Boolean operators (and/or/not)
# =========================================================================

print("--- And/Or/Not ---")
check("and true", "(and #t #t)", "#t")
check("and false", "(and #t #f)", "#f")
check("or true", "(or #f #t)", "#t")
check("or false", "(or #f #f)", "#f")
check("and short-circuit", "(and #f (/ 1 0))", "#f")
check("or short-circuit", "(or #t (/ 1 0))", "#t")
check("not", "(not #f)", "#t")

# =========================================================================
# Variables (define)
# =========================================================================

print("--- Define ---")
check("define var", """(define x 42)
x""", "42")
check("define use", """(define pi 3.14)
(* pi 2)""", "6.28")
check("rebind", """(define x 1)
(define x 2)
x""", "2")

# =========================================================================
# Procedures (define + lambda)
# =========================================================================

print("--- Procedures ---")
check("square", """(define (square x) (* x x))
(square 21)""", "441")
check("multi-param", """(define (average x y) (/ (+ x y) 2))
(average 1 3)""", "2.0")
check("nested call", """(define (add a b) (+ a b))
(add (add 21 21) 42)""", "84")
check("lambda direct", "((lambda (x) (* x x)) 5)", "25")
check("lambda multi", "((lambda (a b) (+ a b)) 3 4)", "7")

# =========================================================================
# Recursion
# =========================================================================

print("--- Recursion ---")
check("factorial 5", """(define (fact n)
  (if (<= n 1)
      1
      (* n (fact (- n 1)))))
(fact 5)""", "120")
check("factorial 10", """(define (fact n)
  (if (<= n 1)
      1
      (* n (fact (- n 1)))))
(fact 10)""", "3628800")
check("fibonacci 9", """(define (fib n)
  (if (<= n 1)
      n
      (+ (fib (- n 1))
         (fib (- n 2)))))
(fib 9)""", "34")

# =========================================================================
# Closures
# =========================================================================

print("--- Closures ---")
check("make-adder", """(define (make-adder n)
  (lambda (x) (+ x n)))
(define add3 (make-adder 3))
(add3 4)""", "7")
check("make-adder inline", """(define (make-adder n)
  (lambda (x) (+ x n)))
((make-adder 4) 5)""", "9")
check("closure capture mutable", """(define multiplier 10)
(define (scale x) (* x multiplier))
(scale 3)""", "30")
check("closure sees rebind", """(define multiplier 10)
(define (scale x) (* x multiplier))
(define multiplier 20)
(scale 3)""", "60")

# =========================================================================
# let
# =========================================================================

print("--- Let ---")
check("let single", "(let ((x 10)) (+ x 5))", "15")
check("let multi", "(let ((x 3) (y 4)) (+ x y))", "7")
check("let shadow", """(define x 1)
(let ((x 10)) x)""", "10")
check("let outer still", """(define x 1)
(let ((x 10)) x)
x""", "1")
check("let body multi", "(let ((x 3)) (+ x 1) (+ x 2))", "5")

# =========================================================================
# set! (mutation)
# =========================================================================

print("--- Set! ---")
check("set! basic", """(define x 1)
(set! x 2)
x""", "2")
check("set! in closure", """(define (make-counter)
  (let ((count 0))
    (lambda ()
      (set! count (+ count 1))
      (- count 1))))
(define counter (make-counter))
(counter)""", "0")
check("set! counter 2nd", """(define (make-counter)
  (let ((count 0))
    (lambda ()
      (set! count (+ count 1))
      (- count 1))))
(define counter (make-counter))
(counter)
(counter)""", "1")

# =========================================================================
# begin
# =========================================================================

print("--- Begin ---")
check("begin sequence", "(begin 1 2 3)", "3")
check("begin with define", """(begin
  (define x 10)
  (define y 20)
  (+ x y))""", "30")

# =========================================================================
# Quote / '
# =========================================================================

print("--- Quote ---")
check("quote list", "(quote (a b c))", "(a b c)")
check("quote abbrev", "'(a b c)", "(a b c)")
check("quote symbol", "'hello", "hello")
check("quote number", "'42", "42")
check("quote nested", "'(a (b c) d)", "(a (b c) d)")
check("quote empty", "'()", "()")

# =========================================================================
# cons / car / cdr (pairs)
# =========================================================================

print("--- Pairs ---")
check("cons", "(cons 1 2)", "(1 . 2)")
check("car", """(define x (cons 1 2))
(car x)""", "1")
check("cdr", """(define x (cons 1 2))
(cdr x)""", "2")
check("cons chain", "(cons 1 (cons 2 (cons 3 4)))", "(1 2 3 . 4)")

# =========================================================================
# Lists
# =========================================================================

print("--- Lists ---")
check("list cons", "(cons 1 (cons 2 (cons 3 '())))", "(1 2 3)")
check("list builtin", "(list 1 2 3 4)", "(1 2 3 4)")
check("null empty", "(null? '())", "#t")
check("null non-empty", "(null? '(1))", "#f")
check("car of list", "(car (list 1 2 3))", "1")
check("cdr of list", "(cdr (list 1 2 3))", "(2 3)")
check("cons to list", "(cons 10 (list 1 2 3))", "(10 1 2 3)")
check("pair?", "(pair? (cons 1 2))", "#t")
check("pair? nil", "(pair? '())", "#f")
check("list?", "(list? (list 1 2))", "#t")
check("list? dotted", "(list? (cons 1 2))", "#f")

# =========================================================================
# Predicates
# =========================================================================

print("--- Predicates ---")
check("eq symbols", "(eq? 'a 'a)", "#t")
check("eq diff symbols", "(eq? 'a 'b)", "#f")
check("equal lists", "(equal? '(1 2) '(1 2))", "#t")
check("equal struct pair", """(equal? (cons 1 2) (cons 1 2))""", "#t")
check("number?", "(number? 42)", "#t")
check("number? sym", "(number? 'x)", "#f")
check("symbol?", "(symbol? 'foo)", "#t")
check("boolean?", "(boolean? #t)", "#t")
check("string?", '(string? "hello")', "#t")

# =========================================================================
# Higher-order functions
# =========================================================================

print("--- Higher-Order ---")
check("map add1", """(define (map1 func lst)
  (if (null? lst)
      '()
      (cons (func (car lst))
            (map1 func (cdr lst)))))
(map1 (lambda (x) (+ x 1)) '(1 2 3))""", "(2 3 4)")
check("filter even", """(define (even? x) (= (modulo x 2) 0))
(define (filter pred lst)
  (if (null? lst)
      '()
      (if (pred (car lst))
          (cons (car lst) (filter pred (cdr lst)))
          (filter pred (cdr lst)))))
(filter even? '(1 2 3 4))""", "(2 4)")

# =========================================================================
# Comments in strings
# =========================================================================

print("--- Comments ---")
check("comment stripped", "(+ 1 2) ; add", "3")
check("semi in string", '''"hello ; world"''', '"hello ; world"')
check("full line comment", """; this is a comment
(+ 3 4)""", "7")

# =========================================================================
# Integration: full program
# =========================================================================

print("--- Integration ---")
check("circle area", """(define pi 3.14159)
(define (circle-area r)
  (* pi (* r r)))
(circle-area 5)""", "78.53975")
check("compose", """(define (compose f g)
  (lambda (x) (f (g x))))
((compose (lambda (x) (+ x 1))
          (lambda (x) (* 3 x)))
 5)""", "16")

# =========================================================================
# Summary
# =========================================================================

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
if errors:
    print("\nFailures:")
    for e in errors:
        print(f"  {e}")
else:
    print("All tests passed!")

sys.exit(1 if failed else 0)
