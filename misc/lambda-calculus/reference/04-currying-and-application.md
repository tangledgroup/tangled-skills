# Currying and Application

## Contents
- What Is Currying
- Formal Definition
- Uncurrying
- Contrast with Partial Application
- Role in Lambda Calculus
- Practical Impact on Programming Languages
- Category Theory Perspective

## What Is Currying

**Currying** is the technique of transforming a function that takes multiple arguments into a sequence of functions, each taking exactly one argument. It is named after logician Haskell Curry (though the idea originated with Moses Schönfinkel and traces back to Gottlob Frege in 1893).

In lambda calculus, all functions take exactly one argument. Currying provides the mechanism to work with multi-argument functions within this constraint.

### Intuitive Example

An uncurried function `add(x, y) = x + y` takes a pair `(x, y)` and returns a sum.

Its curried form takes `x` first, returns a function that takes `y`, then returns the sum:

```
uncurried:  add : (X × Y) → Z
curried:    add' : X → (Y → Z)

add(x, y) = x + y
add'(x)(y) = x + y
```

The curried form `add'` applied to `5` produces a new function "add 5 to whatever you give me." Applied to that result with `3`, we get `8`.

## Formal Definition

Given a function `f : X × Y → Z`, **currying** constructs:

```
curry(f) : X → (Y → Z)
curry(f)(x)(y) = f(x, y)
```

The type of the curry transformation itself:

```
curry : (X × Y → Z) → (X → Y → Z)
```

Arrow associates to the right, so `X → Y → Z` is shorthand for `X → (Y → Z)`.

**Uncurrying** is the reverse:

```
uncurry(f') : X × Y → Z
uncurry(f')(x, y) = f'(x)(y)
```

Type of uncurry:

```
uncurry : (X → Y → Z) → (X × Y → Z)
```

Curry and uncurry are inverses: `uncurry(curry(f)) = f` and `curry(uncurry(f')) = f'`.

## Uncurrying

**Uncurrying** takes a function whose return value is another function, and produces a function that takes both arguments at once. It can be seen as a form of **defunctionalization**.

### Example

Given the curried addition:

```
add' = λx.λy.x + y    -- type: nat → nat → nat
```

Uncurrying produces:

```
uncurry(add') = λ( x, y ). add'(x)(y)    -- type: (nat × nat) → nat
```

The process can be iterated for functions with more than two curried arguments.

## Contrast with Partial Application

Currying and partial application are related but **not the same**.

### Currying

Transforms a function's *type signature*. A function `f : X × Y → Z` becomes `f' : X → Y → Z`. The transformation is structural — it changes how the function accepts arguments.

### Partial Application

Fixes some arguments of a (already curried) function, producing a new function with fewer arguments. It is an *application*, not a transformation of the function itself.

```
-- Curried add:
add' = λx.λy.x + y        -- type: nat → nat → nat

-- Partial application (fix first arg to 5):
add5 = add' 5              -- type: nat → nat
add5 3                     -- = 8
```

Partial application has the signature:

```
apply_x : (X → Y → Z) × X → (Y → Z)
```

Written this way, partial application is adjoint to currying.

### Key Distinction

- **Currying**: changes the function's type (multi-arg → chain of single-arg)
- **Partial application**: applies a curried function to some but not all arguments, yielding a new function

## Role in Lambda Calculus

Lambda calculus functions accept exactly one argument. Currying is not optional — it is how multi-argument computation is expressed:

```
-- Two-argument function (curried):
λx.λy.body

-- Applied to two values:
((λx.λy.body) a) b
```

Left-associative application means `(M N P)` parses as `((M N) P)`, so chained application of a curried function reads naturally without extra parentheses.

This design choice — single-argument functions with currying — simplifies the theoretical model enormously. The entire expressive power of multi-argument computation comes from composition of single-argument functions.

## Practical Impact on Programming Languages

Languages like **Haskell** and **ML** use curried functions by default:

```haskell
-- Haskell: all functions are curried
add :: Int -> Int -> Int
add x y = x + y

-- Partial application is natural
add5 = add 5        -- type: Int -> Int
add5 3              -- = 8
```

```ocaml
(* OCaml: same convention *)
let add x y = x + y
let add5 = add 5    (* type: int -> int *)
add5 3              (* = 8 *)
```

In contrast, languages like Python, Java, and C use uncurried (multi-argument) functions. Currying in these languages requires explicit wrapper functions or library utilities.

Curried functions enable:

- **Function composition**: `f . g` is straightforward when both take one argument
- **Point-free style**: composing functions without mentioning arguments
- **Higher-order patterns**: `map`, `filter`, `fold` work naturally with curried functions
- **Automatic partial application**: passing fewer arguments than expected yields a new function

Uncurried functions are generally preferred in performance-critical code, as they avoid the overhead of closure creation for each argument.

## Category Theory Perspective

Currying finds its most general statement in category theory as a **universal property** of exponential objects.

### Cartesian Closed Categories (CCCs)

In a CCC, there is a natural isomorphism between morphisms:

```
Hom(A × B, C) ≅ Hom(A, C^B)
```

Reading this: morphisms from a product `A × B` to `C` correspond naturally to morphisms from `A` to the exponential object `C^B` (the "function space" from `B` to `C`). This is exactly currying.

The simply typed lambda calculus (with products) is the **internal language** of CCCs — types are objects, terms are morphisms.

### Closed Monoidal Categories

The result generalizes to closed monoidal categories where the product is a tensor product rather than cartesian product:

```
Hom(A ⊗ B, C) ≅ Hom(A, [B → C])
```

Here `[B → C]` is the internal hom functor. This setting underpins:

- **Linear logic** and linear type systems (where the tensor product models resource consumption)
- **Quantum computation** (Hilbert spaces with tensor products)
- Generalizations of Curry-Howard to quantum mechanics, cobordisms, and string theory

The cartesian case (standard currying) suffices for classical logic and traditional programming. The monoidal case is needed for resource-sensitive reasoning (linear types) and quantum computation.
