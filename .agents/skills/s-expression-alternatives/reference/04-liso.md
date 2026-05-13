# Liso

**Author:** Olivier Breuleux  
**Source:** https://github.com/breuleux/liso  
**Year:** 2013–present  
**Language:** Racket  
**Stars:** 33  
**Description:** Operator syntax for the Lisp family of languages (Racket implementation)

## Overview

Liso is a Racket implementation of o-expressions as an alternative syntax for Lisp-like languages. It translates o-expressions into s-expressions while maintaining maximal compatibility with Racket's macro system. The syntax cannot be customized from within itself — operator priority is predetermined, even for custom operators.

## Usage

### First Version (Planet)

Put this at the beginning of a source file:

```racket
#lang planet breuleux/liso
```

### Bleeding Edge Version

Download the code and put this at the beginning:

```racket
#lang reader "/path/to/liso/lang/reader.rkt"
```

Then execute:

```bash
racket file.liso
```

## Syntax Rules

Liso implements a specific subset of o-expressions with predetermined operator priority. The following table maps Liso syntax to s-expressions:

| Rule | O-Expression | S-Expression |
|------|-------------|--------------|
| **Operator** | `x <operator> y` | `(<operator> x y)` |
| | `x <op> y <op> z` | `(<op> x y z)` |
| | `x <op1> y <op2> z` | `(<op1>_<op2> x y z)` (op1 != op2) |
| **Apply** | `x y` | `(apply x y)` |
| | `x y z` | `(apply (apply x y) z)` |
| **List** | `[]` | `(list)` |
| | `[x, ...]` | `(list x ...)` |
| **Apply+List** | `x[y, ...]` | `(x y ...)` |
| **Group** | `{x}` | `x` |
| | `{x, y, ...}` | `(begin x y ...)` |
| **Arrow** | `x => y` | `(x y)` (for all x) |
| **Control** | `@K : x` | `(K x)` |
| | `@K x : y` | `(K x y)` |
| | `@K x, y : {a, b, c}` | `(K (begin x y) a b c)` |
| **Sexp** | `(...)` | `(...)` |

### Operator Priority Table

Liso uses a fixed operator priority table. Custom operators cannot change their priority — it is predetermined by the implementation.

## Aliases

Liso provides syntactic aliases for common operations:

| Usual Syntax | Equivalent Operator |
|-------------|-------------------|
| `@define spec: body` | `spec = body` |
| `@lambda args: body` | `args -> body` |
| `@set! var: value` | `var := value` |
| `@quote: expr` | `..expr` |
| `@quasiquote: expr` | `.expr` |
| `@unquote: expr` | `^expr` |
| `expt[x, y]` | `x ** y` |
| `cons[x, y]` | `x :: y` |
| `string-append[x, y]` | `x ++ y` |
| `not[x == y]` | `x /= y` |
| `or[a, b, c]` | `a \|\| b \|\| c` |
| `and[a, b, c]` | `a && b && c` |
| `not[x]` | `! x` |

## Examples

### Fibonacci

```liso
; Liso (o-expression syntax):
fib[n] =
   @if n <= 1:
      n
      fib[n - 1] + fib[n - 2]

fib[30]

; Equivalent s-expression:
(= (fib n)
   (if (<= n 1)
       n
       (+ (fib (- n 1))
          (fib (- n 2)))))
(fib 30)
```

## Macros

Liso supports Racket's macro system without changes to their underlying logic. Macros see the translated s-expressions, so existing Racket macros work transparently.

Example macro usage is available in the repository at `liso/examples/macros.liso`.

## Key Properties

| Property | Description |
|----------|-------------|
| **Homoiconic** | All syntactic elements behave the same in all contexts |
| **No associated semantics** | Syntax elements have no built-in meaning beyond structure |
| **Regular structures** | Reduces to extremely regular AST nodes |
| **Macro compatible** | Works with Racket's full macro system |
| **Fixed priority** | Operator priority is predetermined, not customizable |
| **Racket-native** | Translates to s-expressions for the Racket compiler |

## Relationship to Pure O-Expressions

Liso's syntax is more complex than pure o-expressions would be for a new language. This is because it must shoehorn o-expressions into Racket's existing s-expression-based system. Key compromises:

- **`(...)` passthrough** — Raw s-expressions are allowed directly
- **`(apply x y)`** — Juxtaposition translates to `(apply ...)` rather than native application
- **Fixed priority** — Pure o-expressions allow user-defined priority; Liso uses a predetermined table
- **Control keyword `@K`** — Needed for macro-like constructs that don't fit the operator model

## Directory Structure

```
liso/
├── lang/
│   └── reader.rkt          ; Main reader implementation
├── examples/
│   ├── macros.liso         ; Macro usage examples
│   └── ...                 ; More examples
└── doc/
    └── liso_priority.png   ; Operator priority table image
```

## Related Projects

- **Liso** — Racket implementation (this project)
- **Earl Grey** — Compile-to-JS language based on o-expressions
- **O-expressions blog post** — Theoretical foundation: https://breuleux.net/blog/oexprs.html
