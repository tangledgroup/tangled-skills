# Sweet-Expressions

**Author:** David Wheeler  
**Source:** https://readable.sourceforge.net/  
**Year:** 2009–present  
**Dialects:** Common Lisp, Scheme, Emacs Lisp, ACL2, Clojure, Arc

## Overview

Sweet-expressions are a set of *abbreviations* that can be added to any existing Lisp reader. They do not replace s-expressions — they sit on top of them, translating readable syntax back into standard s-expressions before the Lisp compiler or interpreter sees them. This means sweet-expressions work with **any** Lisp dialect without requiring changes to the language itself.

The approach has three layers that can be used independently or together:

1. **Curly-infix-expressions** — infix notation inside curly braces
2. **Neoteric-expressions** (modern/neo) — traditional function-call syntax `f(...)`
3. **Sweet-expressions** — indentation-based automatic parentheses

You can choose any subset. For example, you might use only curly-infix without indentation sensitivity.

## Layer 1: Curly-Infix-Expressions

Curly braces `{ ... }` enclose an infix expression that maps to a standard s-expression with the operator first.

### Rules

- `{a op b}` maps to `(op a b)`
- `{a op b op c}` maps to `(op a b c)` (n-ary)
- The first operator encountered becomes the function position
- Multiple different operators in one expression are not allowed

### Examples

```lisp
; S-expression          ; Sweet-expression        ; Meaning
(+ 1 2)                 {1 + 2}                   ; addition
(* n (factorial n))     {n * factorial(n)}        ; multiplication
(<= n 1)                {n <= 1}                  ; comparison
(- n 1)                 {n - 1}                   ; subtraction
```

### Key Properties

- The operator is syntactically in the middle but semantically first
- Works with any operator, not just arithmetic: `{x := y}`, `{a => b}`
- Curly braces are explicit grouping — no indentation required
- Can be nested: `{n * factorial{n - 1}}`

## Layer 2: Neoteric-Expressions

Neoteric-expressions add traditional function-call notation using parentheses.

### Rules

- `f(...)` maps to `(f ...)`
- Arguments inside the parentheses are space or comma separated
- This is purely syntactic sugar — the reader translates it to an s-expression

### Examples

```lisp
; S-expression              ; Neoteric-expression
(print "hello")             print("hello")
(factorial (- n 1))         factorial(n - 1)
(define (foo x y) ...)      define(foo(x, y) ...)
```

## Layer 3: Sweet-Expressions (Full)

The full sweet-expression syntax adds **indentation-based automatic parentheses**. When code is indented, the reader deduces where parentheses should be without requiring explicit `(` or `)`.

### Rules

- Indentation implies a nested form
- Dedent closes the implied form
- Line breaks can act as implicit grouping
- Explicit parentheses still work alongside indentation

### Complete Example

```lisp
; Traditional s-expression:
(define (factorial n)
  (if (<= n 1)
    1
    (* n (factorial (- n 1)))))

; Sweet-expression equivalent:
define factorial(n)
  if {n <= 1}
    1
    {n * factorial{n - 1}}
```

### How It Works

1. `define factorial(n)` — the `neoteric` form `(define (factorial n) ...)`
2. `if {n <= 1}` — body of `define`, using curly-infix for comparison
3. `1` — first branch of `if` (indented under `if`)
4. `{n * factorial{n - 1}}` — second branch, with nested curly-infix

### Compatibility Guarantees

- **All sweet-expressions translate to valid s-expressions** before reaching the compiler
- **No semantic changes** — the Lisp sees exactly what it would see with parentheses
- **Mix freely** — you can use sweet, neoteric, curly-infix, and raw s-expressions in the same file
- **Works with any reader** — implemented as a reader macro extension, not a language change

## Implementation

Sweet-expressions are implemented as a Lisp reader extension. The project provides:

- A Common Lisp implementation (ASDF system)
- An ACL2 book
- Plans for Scheme, Emacs Lisp, and other dialects

The reader processes input character by character, recognizing `{`, `}`, indentation changes, and `f(...)` patterns, then outputs standard s-expressions.

## Design Philosophy

The project is guided by Paul Graham's principle: *"A language that makes source code ugly is maddening to an exacting programmer."*

Key design decisions:

1. **Abbreviations, not replacements** — Sweet-expressions are syntactic sugar on top of s-expressions, not a new syntax from scratch
2. **Opt-in layers** — Each layer can be used independently
3. **Universal compatibility** — Works with any Lisp dialect that supports reader extensions
4. **No semantic ambiguity** — Every sweet-expression has exactly one s-expression translation

## Comparison Points

| Aspect | Sweet-Expressions | Notes |
|--------|-------------------|-------|
| Parentheses | Reduced but not eliminated | Curly braces and indentation replace many `()` |
| Homoiconicity | Preserved | Translates back to s-expressions |
| Dialect support | Universal | Any Lisp with reader extension support |
| Indentation | Optional (layer 3 only) | Layers 1–2 work without it |
| Macros | Fully compatible | Macros see the translated s-expression |
| Learning curve | Incremental | Adopt layers as needed |
