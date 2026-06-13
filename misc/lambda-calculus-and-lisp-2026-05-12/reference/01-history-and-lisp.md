# History and Lisp Origins

## Contents
- McCarthy's EVAL and the Birth of Lisp
- LAMBDA Borrowed From Church
- LABEL vs Y Combinator for Recursion
- The IBM 704 Hardware Origins of car/cdr
- "Lisp ≠ Lambda Calculus" — McCarthy's Own Words
- Discovery vs Invention: Paul Graham's Framing

## McCarthy's EVAL and the Birth of Lisp

McCarthy's 1960 paper "Recursive Functions of Symbolic Expressions and Their Computation by Machine" defined `eval[e, a]` as a mathematical function computing the value of a Lisp expression `e` in assignment list `a`. This was intended as a theoretical description — McCarthy said "this EVAL is intended for reading, not for computing."

Steve Russell disagreed. He compiled McCarthy's theoretical `eval` into IBM 704 machine code, fixing bugs along the way, creating the first working Lisp interpreter. The fact that theoretical pseudo-code translated directly to runnable programs suggested a sort of natural discovery rather than pure invention.

The original `eval` defined three core functions:

- **`eval[e, a]`** — evaluates expression `e` in environment `a`
- **`evcon[c, a]`** — evaluates conditional expressions (COND)
- **`evlis[m, a]`** — evaluates a list of arguments

Supporting utilities included `assoc` (variable lookup), `pair` (argument binding), and the standard list operations `car`, `cdr`, `cons`, `atom`, `eq`, `null`, `append`.

## LAMBDA Borrowed From Church

McCarthy needed a notation for functions that could be passed as arguments. He borrowed `LAMBDA` from Church's lambda calculus:

> "In order to describe that, one has to have a notation for functions. So one could write this function called `mapcar`. [...] That was fine for that recursive definition of applying a function to everything on the list. No new ideas were required. But then, how do you write these functions? And so, the way in which to do that was to borrow from Church's Lambda Calculus, to borrow the lambda definition."
> — McCarthy, 1978

In original Lisp, `LAMBDA` bound variables and replaced occurrences in scope with received arguments:

```lisp
(LAMBDA (x y z) (+ (* y x) (* z x)))
;; Applied to 5, 2, 3: replaces x=5, y=2, z=3
;; (+ (* 2 5) (* 3 5)) = 25
```

This mirrors lambda calculus `λx.λy.λz.body`, but Lisp's `LAMBDA` accepts multiple parameters simultaneously rather than currying them into nested single-argument functions.

## LABEL vs Y Combinator for Recursion

McCarthy's original Lisp used `LABEL` to enable recursive functions. Nathaniel Rochester invented the `LABEL` notation because pure `LAMBDA` alone couldn't express recursion — a function needed a name to call itself:

```lisp
(label factorial
       (lambda (n)
         (cond ((eq n 0) 1)
               ('t (* n (factorial (- n 1)))))))
```

D.M.R. Park pointed out that `LABEL` was logically unnecessary — the same result could be achieved using only `LAMBDA` through a construction analogous to Church's Y operator, albeit more complicated. McCarthy acknowledged he "didn't understand that you really could do conditional expressions in recursion in some sense in the pure lambda calculus."

This gap in understanding shaped early Lisp: it had `LABEL` for recursion and explicit conditionals, neither of which are needed in pure lambda calculus where the Y combinator provides recursion and Church-encoded Booleans provide conditionals.

## The IBM 704 Hardware Origins of car/cdr

`car` and `cdr` are not abstract mathematical concepts — they come directly from the IBM 704's memory architecture:

- **CAR** = Contents of the Address part of the Register
- **CDR** = Contents of the Decrement part of the Register

The IBM 704 had "address" and "decrement" fields in memory index registers. Lisp's list structure maps directly onto these hardware fields: each cons cell has a value field (car) and a next/pointer field (cdr).

Lists are singly-linked and nil-terminated:
- `(a b c)` = `(cons a (cons b (cons c nil)))`
- Dotted notation: `(a . (b . (c . ())))`

This hardware-specific design tells against the "Lisp as pure formal discovery" or "Lisp as direct implementation of lambda calculus" narratives. Pure lambda calculus has no `car`, `cdr`, `cons`, or `eq` — these are Lisp additions for list processing on real machines.

## "Lisp ≠ Lambda Calculus" — McCarthy's Own Words

McCarthy himself rejected the myth that Lisp was intended as a realization of lambda calculus:

> "One of the myths concerning LISP that people think up or invent for themselves becomes apparent, and that is that LISP is somehow a realization of the lambda calculus, or that was the intention. The truth is that I didn't understand the lambda calculus, really."
> — McCarthy, 1978

He qualified this slightly:

> "So, it wasn't an attempt to make the lambda calculus practical, although if someone had started out with that intention, he might have ended up with something like LISP."

Daniel Szmulewicz expanded on this in his 2019 talk "Lisp ≠ Lambda Calculus," pointing out additional divergences: Lisp has side effects, mutation, I/O, and special forms — none of which exist in pure lambda calculus.

## Discovery vs Invention: Paul Graham's Framing

Paul Graham's 2002 essay "The Roots of Lisp" framed McCarthy as the "discoverer" of Lisp — like Euclid of geometry — rather than its inventor:

> "In 1960, John McCarthy published a remarkable paper in which he did for programming something like what Euclid did for geometry. He showed how, given a handful of simple operators and a notation for functions, you can build a whole programming language."

Graham's key insight: Lisp's defining quality is that it can be written in itself. The `eval` function is a Lisp program that interprets Lisp programs. This self-embedding property — homoiconicity — is what makes Lisp unique among programming languages and connects it conceptually to lambda calculus's self-referential capabilities.

However, Graham's "discovery" framing contributes to the mystique around Lisp. The reality is more nuanced: McCarthy designed Lisp for list processing on the IBM 704, borrowed `LAMBDA` notation from Church without fully understanding lambda calculus's power, and the language evolved through practical implementation constraints rather than pure mathematical derivation.
