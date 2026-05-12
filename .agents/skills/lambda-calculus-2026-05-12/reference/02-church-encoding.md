# Church Encoding

## Contents
- Church Numerals
- Arithmetic Operations
- Church Booleans and Logic
- Predicates
- Pairs and Lists
- Recursion and Fixed-Point Combinators

## Church Numerals

Church numerals encode natural numbers as higher-order functions. The numeral `n` represents "apply function f, n times":

```
0  = λfx.x
1  = λfx.f x
2  = λfx.f (f x)
3  = λfx.f (f (f x))
n  = λfx.f applied n times to x
```

Think of Church numeral `n` as the instruction "repeat n times." Given a function `f` and starting value `x`, it produces `f(f(...f(x)...))` with `n` applications.

## Arithmetic Operations

### Successor

Adds one more application of `f`:

```
SUCC = λnfx.f (n f x)
```

Verify: `SUCC 0 = λfx.f ((λfx.x) f x) = λfx.f x = 1`

### Addition

Two definitions, both equivalent:

```
PLUS  = λmnfx.m f (n f x)
PLUS' = λmn.m SUCC n
```

The first applies `f` exactly `m + n` times. The second applies `SUCC`, `m` times to `n`.

Example: `PLUS 2 3 →β 5`

### Multiplication

Function composition of Church numerals:

```
MULT  = λmnf.m (n f)
MULT' = λmn.m (PLUS n) 0
```

The first composes `n` applications of `f`, then repeats that `m` times = `m × n` total. The second adds `n`, `m` times starting from 0.

### Exponentiation

Church numerals *are* repeated composition, so exponentiation is direct application:

```
POW = λbn.n b
```

The numeral `n` applied to base `b` composes `b` with itself `n` times, giving `b^n`.

Example: `POW 2 3 = 3 2 = (λfx.f (f (f x))) 2`, which applies the function "multiply by 2" three times = 8.

### Predecessor

The predecessor is more involved. One definition using pairs:

```
PRED = λnfx.n (λg.h.h (g f)) (λu.x) (λu.u)
```

Intuition: track a running pair `(previous, current)` through `n` iterations, then extract the previous value.

### Subtraction

```
SUB = λmn.m PRED n    -- applies PRED m times to n
```

Yields `m - n` when `m > n`, and 0 otherwise.

## Church Booleans and Logic

Booleans are encoded as choice functions:

```
TRUE  = λxy.x     -- selects first argument
FALSE = λxy.y     -- selects second argument
```

A boolean applied to two values picks one — `TRUE a b → a`, `FALSE a b → b`.

### Logical Operators

```
AND = λp.q.p q p    -- if p is TRUE, result is q; if FALSE, result is FALSE (p)
OR  = λp.q.p p q    -- if p is TRUE, result is TRUE (p); if FALSE, result is q
NOT = λp.p FALSE TRUE  -- swaps the selection
```

### If-Then-Else

Booleans *are* conditionals:

```
IFTHENELSE = λpab.p a b
```

Usage: `TRUE A B → A`, `FALSE A B → B`. In practice, just apply the boolean directly to the two branches.

## Predicates

A **predicate** returns a Church Boolean.

### ISZERO

Returns TRUE if its argument is 0, FALSE otherwise:

```
ISZERO = λn.n (λx.FALSE) TRUE
```

How it works: numeral `n` applies `(λx.FALSE)` exactly `n` times to `TRUE`. For `n = 0`, nothing is applied, result is `TRUE`. For any `n > 0`, the first application yields `FALSE`, and subsequent applications keep it `FALSE`.

### Less Than or Equal

```
LEQ = λmn.ISZERO (SUB m n)
```

`m ≤ n` iff `m - n = 0` (since SUB floors at 0).

### Equality

```
EQ = λmn.(AND (LEQ m n) (LEQ n m))
```

`m = n` iff `m ≤ n` and `n ≤ m`.

## Pairs and Lists

### Pairs

A pair encapsulates two values by accepting a handler function:

```
PAIR   = λxyf.f x y
FIRST  = λp.p (λxy.x)
SECOND = λp.p (λxy.y)
```

`PAIR a b` produces `λf.f a b`. Applying `FIRST` feeds it the selector `λxy.x`, which picks `a`.

### Linked Lists

A list is either empty (`NIL`) or a pair of head and tail:

```
NIL  = λf.TRUE
NULL = λp.p (λxy.FALSE)
```

`NULL NIL → TRUE`, `NULL (PAIR h t) → FALSE`.

Alternatively, using `NIL = FALSE`:

```
NIL = λxy.y
```

Then `(list handler on_nil)` dispatches directly without an explicit `NULL` test.

### Building Lists with Numerals

Church numerals naturally construct lists by repetition:

```
λnx.n (PAIR x) NIL
```

Given numeral `n` and element `x`, this produces a list of `n` copies of `x`.

## Recursion and Fixed-Point Combinators

Lambda calculus has no named functions — a term cannot refer to itself by name. **Fixed-point combinators** provide the mechanism for recursion in this anonymous setting.

### The Problem

In ordinary programming, recursion is straightforward:

```
fact(n) = if n == 0 then 1 else n * fact(n-1)
```

The function `fact` appears in its own definition. Lambda calculus forbids this: abstractions have no names and cannot reference themselves. We need a way for a function to obtain a handle to itself.

### The Solution: Fixed Points

A **fixed point** of function `f` is a value `x` such that `f x = x`. A **fixed-point combinator** is a closed lambda term (combinator) that, given any function `f`, returns one of its fixed points:

```
Y f →β f (Y f)
```

This equation is the key: `Y f` reduces to `f` applied to `Y f` itself. So `f` receives, as its argument, something that behaves exactly like `f` applied to that same thing — effectively giving `f` a way to call itself.

### The Y Combinator (Curry)

Discovered by Haskell Curry:

```
Y = λf.(λx.f (x x)) (λx.f (x x))
```

**Verification** that `Y f =β f (Y f)`:

```
Y f
= (λf.(λx.f (x x)) (λx.f (x x))) f
→β (λx.f (x x)) (λx.f (x x))          -- substitute f for the outer parameter
→β f ((λx.f (x x)) (λx.f (x x)))      -- apply inner function to itself
= f (Y f)                               -- recognize Y f again
```

**Evaluation strategy matters**: Y works correctly in **call-by-name** (lazy/normal-order) evaluation. In **call-by-value** (strict/eager) evaluation, Y loops immediately because the argument `(λx.f (x x)) (λx.f (x x))` is evaluated before `f` gets a chance to inspect its input.

### The Z Combinator (Strict/Lazy)

For call-by-value languages, the **Z combinator** adds an η-expansion to delay the self-application:

```
Z = λf.(λx.f (λv.x x v)) (λx.f (λv.x x v))
```

The extra `λv.` wrapper prevents the inner `(x x)` from being eagerly evaluated. Z is an η-expansion of Y and satisfies the same fixed-point property:

```
Z f →β f (Z f)
```

Z works in both call-by-name and call-by-value evaluation strategies.

### The Turing Fixed-Point Combinator

Discovered by Alan Turing, this combinator has a stronger reduction property than Y:

```
Θ = (λx.λf.f (x x f)) (λx.λf.f (x x f))
```

Unlike Y, where `Y f` and `f (Y f)` only share a common reduct, Turing's combinator satisfies:

```
Θ f →β f (Θ f)
```

That is, `Θ f` directly β-reduces to `f (Θ f)` in one step, rather than requiring multiple reduction paths to converge.

### Factorial Example

Define factorial using the Y combinator. First, write a non-recursive "step" function that takes the recursive function as a parameter:

```
FACT_STEP = λfact.λn.ISZERO n 1 (MULT n (fact (PRED n)))
```

Then apply Y to get the recursive version:

```
FACT = Y FACT_STEP
```

Reduction of `FACT 2` (abbreviated):

```
FACT 2
= (Y FACT_STEP) 2
→β (FACT_STEP (Y FACT_STEP)) 2          -- Y f → f (Y f)
= (FACT_STEP FACT) 2                     -- Y FACT_STEP = FACT
→β ISZERO 2 1 (MULT 2 (FACT (PRED 2)))   -- apply FACT_STEP
→β MULT 2 (FACT 1)                       -- ISZERO 2 = FALSE, so second branch
→β MULT 2 (ISZERO 1 1 (MULT 1 (FACT 0)))
→β MULT 2 (MULT 1 (FACT 0))
→β MULT 2 (MULT 1 1)                     -- FACT 0 → ISZERO 0 1 ... → 1
→β 2
```

### Why Fixed-Point Combinators Cannot Be Typed

In simply typed lambda calculus, no fixed-point combinator can be assigned a type. The reason: if `Y : A`, then from `Y f →β f (Y f)`, the type of `Y` would need to satisfy `A = (A → B) → B` for some `B`, which implies an infinitely deep type. This is why typed systems that support recursion use an explicit `fix` operator with a special typing rule, rather than encoding recursion as a pure lambda term.

### Other Combinators

There are infinitely many fixed-point combinators in untyped lambda calculus. Some notable ones:

- **Y** (Curry): the most common, works in call-by-name
- **Z**: η-expansion of Y, works in both call-by-name and call-by-value
- **Θ** (Turing): stronger reduction property (`Θ f →β f (Θ f)` directly)
- In SKI combinator calculus: `Y = S (λx.f (x x)) (λx.f (x x))` expressed via S, K, I combinators

### The Omega Term

The simplest non-terminating term, related to fixed-point self-application:

```
Ω = (λx.x x)(λx.x x)
```

This reduces to itself forever: `Ω →β Ω →β Ω ...`. It is essentially the self-application at the heart of fixed-point combinators, without any function `f` to give the recursion a productive direction.
