# I-Expressions

**Author:** Egil Möller (SRFI-49), Felix Springer (Haskell implementation)  
**Source:** https://srfi.schemers.org/srfi-49/srfi-49.html  
**Year:** 2003–2004 (SRFI-49), 2022 (Felix Springer's haskeme)  
**Dialects:** Scheme (R6RS), Guile

## Overview

I-expressions (indentation-sensitive expressions) use **indentation to group expressions** instead of parentheses. They provide equal descriptive power to s-expressions while eliminating the need for explicit parenthesization. I-expressions can be mixed freely with s-expressions, giving programmers the ability to lay out code for maximum readability.

Unlike Python's indentation syntax, I-expressions have **no special constructs** for semantic language features — they work purely at the syntactic level, making them applicable to both code and data input.

## Specification (SRFI-49)

### Core Mechanism: INDENT and DEDENT

Each line in a file is either empty (whitespace/comments only) or contains code preceded by spaces/tabs. Before parsing, the leading whitespace of each line is compared to the last non-empty line:

- **INDENT** — if the current line has more leading whitespace than the previous, an implicit `INDENT` token is prepended
- **DEDENT** — if the current line has less leading whitespace, one or more `DEDENT` tokens are prepended (one for each level of dedent)
- **Error** — if neither whitespace sequence is a prefix of the other (e.g., mixing tabs and spaces inconsistently)

### Grammar

```
expr -> QUOTE expr                        => (list 'quote $2)
expr -> QUASIQUOTE expr                   => (list 'quasiquote $2)
expr -> UNQUOTE expr                      => (list 'unquote $2)
expr -> head INDENT body DEDENT           => (append $1 $3)
expr -> GROUP head INDENT body DEDENT     => (append $2 $4)
expr -> GROUP INDENT body DEDENT          => $3
expr -> head                              => (if (= (length $1) 1) (car $1) $1)
expr -> GROUP head                        => (if (= (length $2) 1) (car $2) $2)
head   -> expr head                       => (append $1 $2)
head   -> expr                            => (list $1)
body   -> expr body                       => (cons $1 $2)
body   ->                                 => '()
```

### The `group` Keyword

The special terminal `GROUP` (written as the word `group`) allows lists whose first element is also a list. It is needed because indentation of an empty line is not accounted for.

## Examples

### Pure I-Expression

```
define
 fac x
 if
  = x 0
  1
  * x
    fac
     - x 1
```

This translates to the s-expression:

```scheme
(define (fac x)
  (if (= x 0)
      1
      (* x (fac (- x 1)))))
```

### Mixed I- and S-Expressions

```
define (fac x)
 if (= x 0) 1
  * x
   fac (- x 1)
```

Mixing gives the best of both worlds: s-expressions for dense data/structure, i-expressions for readable layout.

### Using `group`

When you need a list whose first element is itself a list (e.g., in `let` bindings):

```
let
 group
  foo (+ 1 2)
  bar (+ 3 4)
 + foo bar
```

The `group` keyword ensures that `foo` and `bar` bindings are collected as a proper list of pairs, rather than being flattened into the `let` form.

## Felix Springer's Haskell Implementation (haskeme)

Felix Springer implemented an I-expression to S-expression compiler in Haskell, available at:

- **GitHub:** https://github.com/jumper149/haskeme
- **Hackage:** https://hackage.haskell.org/package/haskeme
- **AUR:** https://aur.archlinux.org/packages/haskeme

### Example from the Implementation

```
; I-Expression:
define
 f
  lambda
   x
    let
     y
      * x x
     + y 1

; S-Expression equivalent:
(define f
  (lambda (x)
    (let ((y (* x x)))
      (+ y 1))))

; Mixed I/S-Expression:
define f
 lambda (x)
  let y (* x x)
   + y 1
```

### Design Goals

The implementation translates I-expressions into S-expressions, allowing any Scheme interpreter to process the output. It supports:

- Pure I-expression input
- Mixed I/S-expression input
- Translation in one direction (I → S)
- Shebang and comment handling (planned)

## Key Properties

| Property | Description |
|----------|-------------|
| **Homoiconicity** | Preserved — translates to valid s-expressions |
| **No semantic constructs** | Indentation is purely syntactic, unlike Python |
| **Free mixing** | S-expressions and I-expressions coexist in the same file |
| **Data and code** | Works for both program input and data input |
| **Error on mismatch** | Inconsistent indentation (non-prefix whitespace) is an error |
| **Quote support** | `'`, `` ` ``, and `,` work as in standard Scheme |

## Comparison with Python

Python's indentation syntax differs from I-expressions in key ways:

- Python has special syntactic constructs for `if`, `for`, `def`, etc.
- Python's file input and interactive input have slightly different syntax
- Python's indentation only covers statements, not expressions or data
- I-expressions work at the expression level and apply to both code and data

## Limitations

- **Indentation-only grouping** can make it harder to see structure in dense code
- **Pure I-expressions** use many lines with little information per line
- **`group` keyword** is needed for nested list structures, which breaks pure indentation
- **Translation only one direction** — most implementations go I → S, not S → I
