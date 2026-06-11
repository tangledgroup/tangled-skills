# Common Lisp Functions Guide (lisp-lang.org)

## Contents
- Named Functions (defun)
- Anonymous Functions
- Indirect Calling (funcall/apply)
- Multiple Return Values

## Named Functions (defun)

```lisp
(defun fib (n)
  "Return the nth Fibonacci number."
  (if (< n 2)
      n
      (+ (fib (- n 1))
         (fib (- n 2)))))

(fib 30)  ; → 832040
```

`defun` defines a named function with optional documentation string.

## Anonymous Functions

Created with `lambda`:

```lisp
(lambda (x) (+ x 1))
```

Equivalent to `(defun name (params) body)` without binding to a symbol.

## Indirect Calling

**`funcall`** — call a function with explicit arguments:
```lisp
(funcall #'fib 30)  ; → 832040
```

**`apply`** — call a function with a list of arguments:
```lisp
(apply #'fib (list 30))  ; → 832040
```

Use `apply` when arguments are collected in a list at runtime.

## Multiple Return Values

Functions can return multiple values using `values`:

```lisp
(defun many (n)
  (values n (* n 2) (* n 3)))

(multiple-value-list (many 2))     ; → (2 4 6)
(nth-value 1 (many 2))             ; → 4
```

Bind individual values with `multiple-value-bind`:

```lisp
(multiple-value-bind (first second third)
    (many 2)
  (list first second third))  ; → (2 4 6)
```
