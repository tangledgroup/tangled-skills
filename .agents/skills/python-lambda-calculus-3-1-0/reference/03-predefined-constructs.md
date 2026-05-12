# Predefined Constructs

## Contents
- Logic (Church Booleans)
- Arithmetic (Church Numerals)
- Pairs
- Combinators
- Letter Variables

## Logic (Church Booleans)

Module: `lambda_calculus.terms.logic`

Booleans are encoded as selectors that choose between two arguments:

| Constant | Lambda Form | Behavior |
|----------|------------|----------|
| `TRUE`  | `λx.λy.x` | Selects first argument |
| `FALSE` | `λx.λy.y` | Selects second argument |

### Logical Operators

| Constant | Purpose |
|----------|---------|
| `AND` | Conjunction: `AND p q` → `p q p` |
| `OR`  | Disjunction: `OR p q` → `p p q` |
| `NOT` | Negation: `NOT p` → `p FALSE TRUE` |
| `IF_THEN_ELSE` | Conditional: `IF_THEN_ELSE p a b` → `p a b` |

### Usage

```python
from lambda_calculus.terms.logic import TRUE, FALSE, AND, OR, NOT, IF_THEN_ELSE

# IF_THEN_ELSE TRUE a b → a
result = IF_THEN_ELSE.apply_to(TRUE, Variable("a"), Variable("b"))

# AND TRUE FALSE → FALSE
result = AND.apply_to(TRUE, FALSE)
```

## Arithmetic (Church Numerals)

Module: `lambda_calculus.terms.arithmetic`

Natural numbers are encoded as repeated function application: `n` applies `f` to `x`, `n` times.

### Creating Numbers

```python
from lambda_calculus.terms.arithmetic import number

zero = number(0)   # λf.λx.x
one  = number(1)   # λf.λx.f x
two  = number(2)   # λf.λx.f (f x)
```

Raises `ValueError` for negative numbers.

### Arithmetic Operators

| Constant | Purpose | Lambda Form |
|----------|---------|-------------|
| `ISZERO` | Check if zero: returns `TRUE` or `FALSE` | `λn.n (λx.FALSE) TRUE` |
| `SUCCESSOR` | Increment by one | `λn.λf.λx.f (n f x)` |
| `PREDECESSOR` | Decrement by one | Complex Church predecessor |
| `ADD` | Addition | `λm.λn.λf.λx.m f (n f x)` |
| `SUBTRACT` | Subtraction | `λm.λn.n PREDECESSOR m` |
| `MULTIPLY` | Multiplication | `λm.λn.λf.m (n f)` |
| `POWER` | Exponentiation | `λb.λe.e b` |

### Usage

```python
from lambda_calculus.terms.arithmetic import ADD, MULTIPLY, number

# 2 + 3
result = ADD.apply_to(number(2), number(3))

# 2 * 3
result = MULTIPLY.apply_to(number(2), number(3))
```

To evaluate arithmetic terms to their normal form, use `BetaNormalisingVisitor`. The resulting term will be in Church numeral form.

## Pairs

Module: `lambda_calculus.terms.pairs`

Pairs encode ordered tuples using Church booleans as selectors:

| Constant | Purpose |
|----------|---------|
| `PAIR`  | Construct pair: `PAIR x y f` → `f x y` |
| `FIRST` | Extract first: `FIRST p` → `p TRUE` |
| `SECOND` | Extract second: `SECOND p` → `p FALSE` |
| `NIL`   | Empty pair sentinel: `λx.TRUE` |
| `NULL`  | Check for NIL: returns `TRUE` if argument is `NIL` |

### Usage

```python
from lambda_calculus.terms.pairs import PAIR, FIRST, SECOND, NIL, NULL

# Create a pair
pair = PAIR.apply_to(Variable("a"), Variable("b"))

# Extract first element
first = FIRST.apply_to(pair)  # reduces to "a"

# Check if empty
is_empty = NULL.apply_to(NIL)  # reduces to TRUE
```

## Combinators

Module: `lambda_calculus.terms.combinators`

Well-known combinators expressed as closed terms (no free variables):

### SKI Combinator Calculus

| Constant | Purpose | Lambda Form |
|----------|---------|-------------|
| `I` | Identity: `I x` → `x` | `λx.x` |
| `K` | Constant: `K x y` → `x` | `λx.λy.x` |
| `S` | Substitution: `S x y z` → `x z (y z)` | `λx.λy.λz.x z (y z)` |

### BCKW Combinator Calculus

| Constant | Purpose | Lambda Form |
|----------|---------|-------------|
| `B` | Composition: `B f g x` → `f (g x)` | `λx.λy.λz.x (y z)` |
| `C` | Flip: `C f x y` → `f y x` | `λx.λy.λz.x z y` |
| `W` | Duplication: `W f x` → `f x x` | `λx.λy.x y y` |

### Fixed-Point and Self-Application

| Constant | Purpose | Lambda Form |
|----------|---------|-------------|
| `Y` | Y combinator for recursion | `λg.(λx.g (x x)) (λx.g (x x))` |
| `DELTA` | Self-application: `Δ x` → `x x` | `λx.x x` |
| `OMEGA` | No normal form: `Δ Δ` | `(λx.x x) (λx.x x)` |

### Usage

```python
from lambda_calculus.terms.combinators import Y, S, K, I, DELTA, OMEGA

# Identity applied to a variable
result = I.apply_to(Variable("x"))  # reduces to "x"

# Y combinator for recursive definitions
# Y F → F (Y F) — enables fixed-point recursion

# OMEGA has no beta normal form — evaluation diverges
omega = OMEGA
omega.is_combinator()  # True (closed term)
```

## Letter Variables

Module: `lambda_calculus.terms.abc`

Predefined `Variable` instances for all ASCII letters, convenient for constructing terms interactively:

```python
from lambda_calculus.terms.abc import x, y, z, a, b, c

# Build terms with letter variables
term = x.apply_to(y).abstract("x", "y")  # (λx.(λy.(x y)))
```

Available: `a` through `z` (lowercase) and `A` through `Z` (uppercase), each a `Variable[str]` instance.
