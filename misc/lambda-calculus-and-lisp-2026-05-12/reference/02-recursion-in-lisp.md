# Recursion in Lisp

## Contents
- Recursive Patterns in Emacs Lisp
- The excessive-lisp-nesting Limit
- Tail Call Optimization
- cl-labels with Accumulator Pattern
- Streams for Lazy Evaluation
- Pure Lambda Calculus: No Named Self-Reference

## Recursive Patterns in Emacs Lisp

Recursive functions are idiomatic in Scheme but problematic in Emacs Lisp due to stack depth limits. A simple recursive Fibonacci generator illustrates the pattern and its limits:

```lisp
(defun fib1 (n a b)
  "Calculate the first N Fibonacci numbers, recursively."
  (if (< n 1)
      a
    (cons a
          (fib1 (1- n) b (+ a b)))))

(fib1 10 0 1) ; (0 1 1 2 3 5 8 13 21 34 . 55)
```

This builds an improper list by consing each result onto a pending recursive call. The recursion unwinds only when `n < 1`, at which point the base case returns `a` and all the pending `cons` operations resolve.

## The excessive-lisp-nesting Limit

Emacs Lisp has a hard limit on nesting depth. On Emacs 30, `fib1` works up to about 529 iterations before triggering an `excessive-lisp-nesting` error with a massive backtrace. This is because each recursive call adds a frame to the call stack, and Emacs limits stack depth to prevent crashes.

The error occurs during printing of the deeply nested result, not during computation — the calculation completes but Emacs cannot print a cons chain deeper than its nesting limit.

### Loop Alternative

For practical work in Emacs Lisp, use loops instead of recursion:

```lisp
(defun fib2 (n a b)
  "Calculate the first N Fibonacci numbers in a loop."
  (let ((result nil))
    (dotimes (c n)
      (setq result (cons a result))
      (setq tempa b)
      (setq b (+ a b))
      (setq a tempa))
    (nreverse result)))

(fib2 50000 0 1) ; works fine — 50,000 numbers
```

Loops avoid stack growth entirely by using iterative state mutation instead of recursive call frames. This can compute 50,000+ Fibonacci numbers where recursion caps at ~529.

## Tail Call Optimization

Scheme was the first Lisp to implement tail call optimization (TCO), making tail-recursive functions as memory-efficient as loops. Guy Steele's 1977 paper "LAMBDA: The Ultimate GOTO" argued that tail calls should be treated as specialized GOTO statements:

> "In general, procedure calls may be usefully thought of as GOTO statements which also pass parameters, and can be uniformly encoded as JUMP instructions."

A function call is in **tail position** when it is the last operation in the function — nothing remains to be done with its result. TCO reuses the current stack frame instead of allocating a new one.

`fib1` above is NOT tail-recursive because `cons` must execute after the recursive call returns. The recursive call is not in tail position.

## cl-labels with Accumulator Pattern

Emacs 28.1+ provides limited TCO through `cl-labels`. Combined with an accumulator pattern that places the recursive call in true tail position, this avoids stack overflow:

```lisp
(defun fib5 (n)
  "Calculate Fibonacci numbers using cl-labels and accumulator."
  (cl-labels ((fib* (a b accum)
                (let* ((accum (cons a accum))
                       (accum-lng (length accum)))
                  (if (< n accum-lng)
                      (nreverse accum)
                    (fib* b (+ b a) accum)))))
    (fib* 0 1 nil)))

(fib5 10000) ; works — tail call optimized
```

The key: `fib*` calls itself as the final operation in the `if` branch. The accumulator collects results during descent, and `nreverse` produces the proper list at the base case. No pending operations remain after the recursive call, so TCO applies.

### Why cl-labels Alone Is Not Enough

Using `cl-labels` without the accumulator pattern still overflows because the recursive call is not in tail position:

```lisp
(defun fib3 (n)
  (cl-labels ((fib* (n a b)
                (if (< n 1)
                    a
                  (cons a (fib* (1- n) b (+ a b)))))) ; cons after call — NOT tail!
    (fib* n 0 1)))

(fib3 397) ; overflows at 397 — even worse than fib1's 529
```

The `cons` wrapping the recursive call means the call is not in tail position. The overhead of `cl-labels` actually makes the limit lower than plain recursion.

## Streams for Lazy Evaluation

Emacs' `stream` package provides delayed evaluation of cons cells, enabling infinite sequences without stack overflow:

```lisp
(defun fib6 (n)
  "Return first N Fibonacci numbers as a stream."
  (cl-labels ((fibonacci-populate (a b)
                (stream-cons a (fibonacci-populate b (+ a b)))))
    (let ((fibonacci-stream (fibonacci-populate 0 1))
          (fibs nil))
      (dotimes (c n)
        (setq fibs (cons (stream-pop fibonacci-stream) fibs)))
      (nreverse fibs))))

(fib6 50000) ; works — lazy evaluation avoids stack growth
```

`fibonacci-stream` is an infinite sequence. `stream-pop` evaluates and returns the next element without building up the entire structure in memory. The stream represents the full Fibonacci sequence as a potentially infinite computation that only evaluates what is consumed.

## Pure Lambda Calculus: No Named Self-Reference

In pure lambda calculus, there are no named functions — a term cannot reference itself by name. This makes traditional recursion impossible. Consider factorial:

```
fact = λn.(iszero n) 1 (mult n (fact (prec n)))
```

This references `fact` by name, which doesn't exist in pure lambda calculus. The solution is the **Y combinator**, a fixed-point combinator that enables recursion without names:

```
Y f →β f (Y f)
```

This means applying `Y` to any function `f` produces a term equal to `f` applied to itself recursively — giving `f` a way to call itself without a name. See the Y Combinator reference for full derivation and Scheme implementation.
