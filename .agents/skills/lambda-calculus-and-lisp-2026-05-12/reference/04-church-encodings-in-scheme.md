# Church Encodings in Scheme

## Contents
- Church Booleans and Conditionals
- Basic Combinators (I, K, KI)
- Church Numerals
- Arithmetic Operations (Add, Multiply, Subtract)
- Church Pairs
- Church Lists with Helper Functions
- Comparison Operations
- Higher-Order List Operations (Map, Filter, Fold)
- Recursion on Church Terms via Y Combinator

## Church Booleans and Conditionals

Church booleans encode truth values as selection functions. `TRUE` selects the first argument, `FALSE` selects the second:

```scheme
(define lc-true (lambda (x) (lambda (y) x)))
(define lc-false (lambda (x) (lambda (y) y)))
```

A conditional applies the boolean to two values:

```scheme
(define lc-if
  (lambda (condition)
    (lambda (then-val)
      (lambda (else-val)
        ((condition then-val) else-val)))))

(((lc-if lc-true) "yes") "no")   ; "yes"
(((lc-if lc-false) "yes") "no")  ; "no"
```

Logical operators compose booleans:

```scheme
(define lc-and
  (lambda (x) (lambda (y) ((x y) lc-false))))

(define lc-or
  (lambda (x) (lambda (y) ((x x) y))))

(define lc-not
  (lambda (x) ((x lc-false) lc-true)))
```

## Basic Combinators (I, K, KI)

The fundamental combinators from combinatory logic:

```scheme
;; Identity: returns its argument unchanged
(define I (lambda (x) x))

;; K (constant): returns first argument, ignores second
(define K (lambda (x) (lambda (y) x)))

;; KI (reverse constant): returns second argument, ignores first
(define KI (lambda (x) (lambda (y) y)))

(I 5)       ; 5
((K 3) 4)   ; 3
((KI 3) 4)  ; 4
```

Note that `lc-true` is equivalent to `K` and `lc-false` is equivalent to `KI`.

## Church Numerals

Church numerals encode natural numbers as repeated function application. The numeral `n` applies function `f`, `n` times to `x`:

```scheme
;; Zero: applies f zero times, returns x unchanged
(define lc-zero (lambda (f) (lambda (x) x)))

;; Successor: given numeral n, returns n+1 by adding one more application of f
(define lc-succ
  (lambda (n)
    (lambda (f)
      (lambda (x)
        (f ((n f) x))))))

;; Convert Church numeral to Scheme integer for display
(define (church-to-int n)
  ((n (lambda (x) (+ x 1))) 0))

(define lc-one (lc-succ lc-zero))
(define lc-two (lc-succ lc-one))
(define lc-three (lc-succ lc-two))

(church-to-int lc-zero)  ; 0
(church-to-int lc-one)   ; 1
(church-to-int lc-three) ; 3
```

The intuition: `lc-zero` ignores `f` and returns `x`. `lc-one` applies `f` once to `x`. `lc-two` applies `f` twice. The numeral is the *count* of applications.

## Arithmetic Operations (Add, Multiply, Subtract)

### Addition

Add two Church numerals by applying `f`, `m` times then `n` times:

```scheme
(define lc-add
  (lambda (m)
    (lambda (n)
      (lambda (f)
        (lambda (x)
          ((m f) ((n f) x)))))))

(church-to-int ((lc-add lc-one) lc-two)) ; 3
```

### Multiplication

Multiply by composing: apply `(n f)` a total of `m` times:

```scheme
(define lc-mult
  (lambda (m)
    (lambda (n)
      (lambda (f)
        (m (n f))))))

(church-to-int ((lc-mult lc-two) lc-three)) ; 6
```

### Subtraction

Subtraction is more complex. It uses pair manipulation to track the difference:

```scheme
(define lc-sub
  (lambda (m)
    (lambda (n)
      ((n (lambda (p)
            (lambda (f)
              (lambda (x)
                ((p (lambda (g) (lambda (h) (h (g f))))
                   (lambda (y) x)
                   (lambda (y) y))))))
       m))))

(church-to-int ((lc-sub lc-three) lc-one)) ; 2
```

## Church Pairs

Pairs encode two values as a function that takes a selector:

```scheme
(define lc-pair
  (lambda (x)
    (lambda (y)
      (lambda (f)
        ((f x) y)))))

(define lc-first
  (lambda (p)
    (p (lambda (x) (lambda (y) x)))))

(define lc-second
  (lambda (p)
    (p (lambda (x) (lambda (y) y)))))

(define my-pair ((lc-pair 3) 4))
(lc-first my-pair)   ; 3
(lc-second my-pair)  ; 4
```

A pair is a function that, when given a selector `f`, applies `f` to both stored values. `lc-first` passes the `K` combinator (selects first), and `lc-second` passes `KI` (selects second).

## Church Lists with Helper Functions

Lists are built from pairs (cons cells) with a nil terminator:

```scheme
(define lc-nil (lambda (x) lc-true))
(define lc-cons lc-pair)
(define lc-is-nil
  (lambda (l)
    (l (lambda (h) (lambda (t) lc-false)))))

(define lc-head lc-first)
(define lc-tail lc-second)
```

Helper functions to convert between Scheme lists and Church-encoded lists:

```scheme
(define (list-to-church lst)
  (if (null? lst)
      lc-nil
      ((lc-cons (car lst)) (list-to-church (cdr lst)))))

(define (church-to-list l)
  (if ((l (lambda (h) (lambda (t) lc-false))) #t #f)
      '()
      (cons (lc-head l) (church-to-list (lc-tail l)))))

(define my-list (list-to-church '(1 2 3)))
(church-to-list my-list)       ; (1 2 3)
(lc-head my-list)              ; 1
(church-to-list (lc-tail my-list)) ; (2 3)
((lc-is-nil my-list) #t #f)    ; #f
((lc-is-nil lc-nil) #t #f)     ; #t
```

## Comparison Operations

### is-zero

A Church numeral `n` is zero if applying it to `(lambda (x) FALSE)` and `TRUE` yields `TRUE`:

```scheme
(define lc-is-zero
  (lambda (n)
    ((n (lambda (x) lc-false)) lc-true)))

((lc-is-zero lc-zero) #t #f) ; #t
((lc-is-zero lc-one) #t #f)  ; #f
```

Zero applies `f` zero times, so it returns the initial value `lc-true`. Any positive numeral applies `(lambda (x) lc-false)` at least once, producing `lc-false`.

### Less-than-or-equal and Equality

```scheme
(define lc-leq
  (lambda (m)
    (lambda (n)
      (lc-is-zero ((lc-sub m) n)))))

(define lc-eq
  (lambda (m)
    (lambda (n)
      ((lc-and (lc-leq m n)) (lc-leq n m)))))

(((lc-leq lc-one) lc-two) #t #f) ; #t  (1 <= 2)
(((lc-eq lc-one) lc-one) #t #f)  ; #t  (1 == 1)
(((lc-eq lc-one) lc-two) #t #f)  ; #f  (1 != 2)
```

## Higher-Order List Operations (Map, Filter, Fold)

### Map

Apply a function to each element of a Church list:

```scheme
(define lc-map
  (lambda (f)
    (lambda (l)
      (((lc-if (lc-is-nil l))
        lc-nil)
       (lambda ()
         ((lc-cons (f (lc-head l)))
          ((lc-map f) (lc-tail l))))))))

(define my-list (list-to-church '(1 2 3)))
(define doubled ((lc-map (lambda (x) (* x 2))) my-list))
(church-to-list doubled) ; (2 4 6)
```

### Filter

Keep elements that satisfy a predicate:

```scheme
(define lc-filter
  (lambda (p)
    (lambda (l)
      (((lc-if (lc-is-nil l))
        lc-nil)
       (lambda ()
         (((lc-if (p (lc-head l)))
           (lambda () ((lc-cons (lc-head l)) ((lc-filter p) (lc-tail l)))))
          (lambda () ((lc-filter p) (lc-tail l)))))))))

(define filtered ((lc-filter (lambda (x) (> x 1))) my-list))
(church-to-list filtered) ; (2 3)
```

### Fold (Reduce)

Accumulate a result by folding a function over the list:

```scheme
(define lc-fold
  (lambda (f)
    (lambda (acc)
      (lambda (l)
        (((lc-if (lc-is-nil l))
          acc)
         (lambda ()
           (((lc-fold f) (f acc (lc-head l))) (lc-tail l))))))))

(define sum (((lc-fold (lambda (x) (lambda (y) (+ x y)))) 0) my-list))
; sum = 6
```

## Recursion on Church Terms via Y Combinator

Combine Church-encoded arithmetic with the Y combinator for recursive computation on pure lambda terms:

```scheme
;; Y combinator (beta-abstracted for strict Scheme)
(define Y
  (lambda (f)
    ((lambda (x) (f (lambda (n) ((x x) n))))
     (lambda (x) (f (lambda (n) ((x x) n)))))))

;; Factorial using Church numerals
(define factorial
  (Y (lambda (f)
       (lambda (n)
         (((lc-if (lc-is-zero n))
           lc-one)
          (lambda ()
            ((lc-mult n) (f ((lc-sub n) lc-one)))))))))

(define lc-five (lc-succ (lc-succ (lc-succ (lc-succ lc-one)))))
(church-to-int (factorial lc-five)) ; 120
```

This demonstrates full recursion on Church-encoded data using only the Y combinator — no named self-reference, no `define` for the recursive function itself. The `factorial` generator receives its own recursive version through `f`, and uses Church-encoded arithmetic (`lc-mult`, `lc-sub`) and conditionals (`lc-if`, `lc-is-zero`) to compute the result entirely within the lambda calculus encoding.
