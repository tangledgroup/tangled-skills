# Introduction to Scheme — Functional Programming Notes (EECS 390)

## Contents
- Expressions and Prefix Notation
- Special Forms
- Definitions
- Compound Values (cons/car/cdr)
- Symbolic Data and Quoting
- Variadic Functions
- Parameter Passing Modes

## Expressions and Prefix Notation

Scheme programs consist of expressions — either simple literals/symbols or **combinations** (compound expressions in parentheses):

```scheme
(quotient 10 2)    ; → 5
(+ (* 3 5) (- 10 6))  ; → 19
```

Prefix notation: operator first, then operands. All within parentheses. Nested combinations allowed.

## Special Forms

Special forms have custom evaluation rules (not all sub-expressions are evaluated):

**`if`**: `(if <predicate> <consequent> <alternative>)` — predicate evaluated first; consequent or alternative based on truth value. Alternative may be omitted.

**`and`**: Left-to-right evaluation; returns first false value or last true value. Short-circuits.

**`or`**: Left-to-right evaluation; returns first true value or last false value. Short-circuits.

**`not`**: Returns `#t` if argument is false, `#f` otherwise.

Only `#f` counts as false in Scheme. Everything else (including `0`, `""`, `'()`) is true.

## Definitions

```scheme
(define pi 3.14)                    ; variable
(define (square x) (* x x))         ; procedure
;; equivalent to:
(define square (lambda (x) (* x x)))
```

General form: `(define (<name> <formal-parameters>) <body>)`.

Anonymous functions via `lambda`:
```scheme
((lambda (x y z) (+ x y (square z))) 1 2 3)  ; → 12
```

## Compound Values (cons/car/cdr)

Pairs (cons cells) are the fundamental building block:

```scheme
(define x (cons 1 2))
x           ; → (1 . 2)
(car x)     ; → 1
(cdr x)     ; → 2
```

**Proper lists**: Chain of pairs terminated by `'()` (empty list):
```scheme
(cons 1 (cons 2 (cons 3 (cons 4 '()))))  ; → (1 2 3 4)
(list 1 2 3 4)                           ; → (1 2 3 4)
```

**Improper lists**: Chain terminated by non-empty-list value:
```scheme
(cons 1 (cons 2 (cons 3 4)))  ; → (1 2 3 . 4)
```

Lists have reference semantics — `set-car!` and `set-cdr!` mutate shared objects.

## Symbolic Data and Quoting

Quoting prevents evaluation, treating symbols as data:

```scheme
(define a 1)
(list a b)       ; → (1 2)     ; values of a and b
(list 'a 'b)     ; → (a b)     ; symbols themselves
'(- 3)           ; → (- 3)     ; list containing symbol - and number 3
"(- 3)"          ; → "(- 3)"   ; string, not parsed
```

Quoted expressions are parsed but not evaluated. Strings remain raw character data.

## Variadic Functions

Scheme supports variable arguments via dotted parameter lists:

```scheme
(define (func . args) args)
(func)           ; → ()
(func 1 2 3)     ; → (1 2 3)

(define (average x . nums)
  (/ (apply + x nums)
     (+ 1 (length nums))))
(average 1 3 5 7)  ; → 4
```

`apply` takes a procedure and a list, spreading the list as arguments: `(apply + 1 2 '(3 4))` ≡ `(+ 1 2 3 4)`.

## Parameter Passing Modes

| Mode | Direction | Description |
| --- | --- | --- |
| Call by value | Input | Copy argument to new variable. Used by Scheme, Python, Java, C. |
| Call by reference | Input/Output | Parameter aliases the argument object. C++ references. |
| Call by result | Output | Uninitialized on entry, copied back on exit. |
| Call by value-result | Input/Output | Copy in on entry, copy out on exit. |
| Call by name | Lazy | Expression re-evaluated each use (via thunk). |

Scheme uses **call by value** with reference semantics for compound objects (sometimes called "call by object reference").
