# Y Combinator and Fixed-Points

## Contents
- Fixed Points: Definition and Intuition
- The Self-Applying Lambda Pattern
- Deriving the Y Combinator
- Step-by-Step Beta Reduction of Y g
- The Problem with Strict Evaluation
- Beta-Abstraction: Delaying (x x)
- Complete Factorial Example in Scheme
- The Z Combinator for Call-by-Value

## Fixed Points: Definition and Intuition

A **fixed point** of function `f` is a value `x` such that `f(x) = x`. For example, if `f(x) = x!`, then 1 and 2 are fixed points because `1! = 1` and `2! = 2`.

A **fixed-point combinator** is a higher-order function that, given any function `f`, returns one of its fixed points:

```
fix(f) → some x where f(x) = x
```

Equivalently: `f (fix f) = fix f`.

In lambda calculus, every function has at least one fixed point. The Y combinator is the most famous fixed-point combinator.

## The Self-Applying Lambda Pattern

Before understanding Y, observe how a lambda term can apply to itself:

```
(λx. x x) (λx. x x)
```

Both expressions are identical. Beta-reducing the outer application replaces `x` in the body `(x x)` with the argument `(λx. x x)`, producing the exact same expression again. This creates infinite self-application — the foundation for recursion without names.

In Scheme:
```scheme
((lambda (x) (x x))
 (lambda (x) (x x)))
```

In JavaScript:
```js
((x) => x(x))((x) => x(x))
```

## Deriving the Y Combinator

The goal: find a term `Y` such that for any function `g`:

```
Y g = g (Y g)
```

This equation means: applying `Y` to `g` produces the same result as applying `g` to `(Y g)`. If `g` is a "generator" function that takes its own recursive version as input, `Y g` gives us a recursive version of `g`.

Start with the self-application pattern and wrap it with `f`:

```
Y = λf. (λx. f (x x)) (λx. f (x x))
```

The body consists of the same lambda term `(λx. f (x x))` applied to itself. The self-application provides the recursive loop, and `f` is called at each iteration.

## Step-by-Step Beta Reduction of Y g

Walk through the reduction to verify that `Y g = g (Y g)`:

```
Y g
= (λf. (λx. f (x x)) (λx. f (x x))) g
→β (λx. g (x x)) (λx. g (x x))          [substitute f → g]
→β g ((λx. g (x x)) (λx. g (x x)))      [substitute x → (λx. g (x x))]
= g (Y g)                                [recognize Y g in the argument]
```

The third step applies the outer lambda: replace `x` in `(g (x x))` with `(λx. g (x x))`. The expression `(λx. g (x x)) (λx. g (x x))` appearing as the argument to `g` is exactly `Y g` from step 2. Therefore `Y g = g (Y g)`.

An alternative, slightly simpler form:

```
X = λf. (λx. x x) (λx. f (x x))
```

This also beta-reduces to the fixed-point property.

## The Problem with Strict Evaluation

The standard Y combinator works in lambda calculus (call-by-name/lazy evaluation) but fails in Scheme and most practical languages that use **strict** (call-by-value) evaluation. In strict evaluation, arguments are fully evaluated before the function body executes.

When Scheme evaluates `(Y g)`, it tries to evaluate `(x x)` immediately. But `(x x)` contains another `(x x)`, which contains another — infinite reduction before any useful computation occurs.

```scheme
;; This loops forever in Scheme:
(define Y
  (lambda (f)
    ((lambda (x) (f (x x)))
     (lambda (x) (f (x x))))))
```

## Beta-Abstraction: Delaying (x x)

The fix is **beta-abstraction**: wrap the `(x x)` application inside a lambda so it is not evaluated until called. This acts as a thunk — a delayed computation.

```scheme
(define Y
  (lambda (f)
    ((lambda (x) (f (lambda (n) ((x x) n))))
     (lambda (x) (f (lambda (n) ((x x) n)))))))
```

The key change: `(x x)` is wrapped in `(lambda (n) ((x x) n))`. When `f` receives this wrapper, it doesn't immediately evaluate `(x x)`. Instead, `(x x)` only evaluates when the wrapper is called with an argument `n`. This delays the self-application until it is actually needed, preventing infinite loops in strict evaluation.

### How the Delayed Y Works

1. `Y` receives a generator function `f` (e.g., `fact-generator`)
2. The inner lambda `(lambda (x) (f (lambda (n) ((x x) n))))` is applied to itself
3. This calls `f` with a **proxy**: `(lambda (n) ((x x) n))`
4. The proxy receives arguments and forwards them after evaluating `(x x)`
5. When the proxy is called, `(x x)` triggers another iteration of the fixed-point loop
6. Each iteration produces a new proxy, enabling infinite recursion

## Complete Factorial Example in Scheme

The pattern for using Y with a generator function:

```scheme
;; The Y combinator (beta-abstracted for strict evaluation)
(define Y
  (lambda (f)
    ((lambda (x) (f (lambda (n) ((x x) n))))
     (lambda (x) (f (lambda (n) ((x x) n)))))))

;; A factorial generator: takes self as argument, returns the factorial function
(define fact-generator
  (lambda (self)
    (lambda (n)
      (if (= n 0)
          1
          (* n (self (- n 1)))))))

;; Apply Y to get a recursive factorial function
(define fact (Y fact-generator))

(fact 5) ; 120
(fact 10) ; 3628800
```

The `fact-generator` pattern: the outer lambda receives `self` (which will be the recursive version), and returns an inner lambda that is the actual function. The inner lambda calls `self` for recursion instead of calling itself by name.

Without Y, you might try `(define fact (fact-generator fact))`, but this fails because `fact` is not yet defined when evaluating the argument to `fact-generator`. Y solves this by producing the fixed point through self-application rather than explicit naming.

## The Z Combinator for Call-by-Value

The **Z combinator** is an alternative fixed-point combinator designed specifically for call-by-value evaluation. It uses η-expansion (adding a parameter) to delay the self-application:

```
Z = λf. (λx. f (λv. x x v)) (λx. f (λv. x x v))
```

In Scheme:
```scheme
(define Z
  (lambda (f)
    ((lambda (x) (f (lambda (v) ((x x) v))))
     (lambda (x) (f (lambda (v) ((x x) v)))))))
```

The difference from Y: instead of `(lambda (n) ((x x) n))`, Z uses `(lambda (v) ((x x) v))`. The η-expansion `λv. x x v` is extensionally equivalent to `x x` but delays evaluation differently, making it work correctly in strict languages without the extra wrapping layer that Y needs.

Both Y (with beta-abstraction) and Z achieve the same goal: enabling recursion in systems where functions cannot reference themselves by name.
