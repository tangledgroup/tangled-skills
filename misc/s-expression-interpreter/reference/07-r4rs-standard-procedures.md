# R4RS Scheme — Standard Procedures Reference

## Contents
- Boolean Values
- Equivalence Predicates
- Discrimination Levels

## Boolean Values

Standard boolean objects: `#t` (true) and `#f` (false).

In conditional expressions (`if`, `cond`, `and`, `or`, `do`), only `#f` counts as false. Everything else is true — including the empty list `'()`, numbers, strings, symbols, and procedures.

```scheme
(not #t)                    ; → #f
(not 3)                     ; → #f
(not (list 3))              ; → #f
(not #f)                    ; → #t
(not '())                   ; → #f    ; empty list is TRUE in Scheme
(boolean? #f)               ; → #t
(boolean? 0)                ; → #f
```

Boolean constants evaluate to themselves — no quoting needed.

## Equivalence Predicates

Four levels of discrimination from finest to coarsest:

**`eqv?`** — Useful equivalence. Returns `#t` if objects should normally be regarded as the same:

- Same booleans, same symbols (by name), numerically equal numbers of same exactness
- Same characters, both empty lists
- Pairs/vectors/strings at same memory location
- Procedures with equal location tags

```scheme
(eqv? 'a 'a)                ; → #t
(eqv? 2 2)                  ; → #t
(eqv? '() '())              ; → #t
(eqv? (cons 1 2) (cons 1 2)) ; → #f  ; different locations
```

Unspecified for: distinct string objects with same content, empty vectors, equivalent lambdas.

**`eq?`** — Finest discrimination. Same as `eqv?` except for numbers (where `eq?` is unspecified for numerically equal but not identical numbers). For symbols and pairs, `eq?` and `eqv?` agree.

**`equal?`** — Coarse equivalence. Recursively compares structure:

- Pairs: `equal?` on both `car` and `cdr`
- Strings: same length and character-by-character equality
- Vectors: same length and element-wise `equal?`

```scheme
(equal? '(1 2) '(1 2))      ; → #t   ; structural comparison
(eqv? '(1 2) '(1 2))        ; → #f   ; different locations
```

**`equalp?`** — Coarsest. Like `equal?` but case-insensitive for strings/characters and type-loose for numbers (`(equalp? 3 3.0)` → `#t`).

## Discrimination Levels Summary

| Predicate | Symbols | Numbers (same value) | Pairs (same content) | Strings (same chars) |
| --- | --- | --- | --- | --- |
| `eq?` | `#t` | unspecified | `#f` | `#f` |
| `eqv?` | `#t` | same exactness: `#t` | `#f` | unspecified |
| `equal?` | `#t` | same value: `#t` | `#t` | `#t` |
| `equalp?` | `#t` | any type: `#t` | `#t` | case-insensitive: `#t` |
