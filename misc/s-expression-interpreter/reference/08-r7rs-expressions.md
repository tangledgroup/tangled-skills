# R7RS Scheme — Expression Types Specification

## Contents
- Variable References
- Literal Expressions
- Procedure Calls
- Lambda (Procedures)
- Conditionals

## Variable References

An expression consisting of a single variable evaluates to the value stored in its bound location. Referencing an unbound variable is an error.

```scheme
(define x 28)
x    ⟹  28
```

## Literal Expressions

Three equivalent syntaxes:

```scheme
(quote <datum>)     ; full form
'<datum>            ; abbreviated
<constant>          ; self-evaluating constants
```

Self-evaluating (no quoting needed): numbers, strings, characters, vectors, bytevectors, booleans.

```scheme
'145932      ⟹  145932
"abc"        ⟹  "abc"
#\a          ⟹  #\a
#(a 10)      ⟹  #(a 10)
#t           ⟹  #t
```

It is an error to alter a constant using mutation procedures (`set-car!`, `string-set!`).

## Procedure Calls

Syntax: `(<operator> <operand1> …)`

Operator and operand expressions are evaluated in **unspecified order** (contrast with other Lisps that may specify left-to-right). The resulting procedure receives the resulting arguments.

```scheme
(+ 3 4)          ⟹  7
((if #f + *) 3 4) ⟹  12
```

Procedure calls can return any number of values (see `values`). Empty list `()` is an error as an expression in Scheme (unlike other Lisps where it evaluates to itself).

## Lambda (Procedures)

Syntax: `(lambda <formals> <body>)`

Evaluates to a procedure. The environment at evaluation time is captured (closure). When called, fresh locations are created for formal parameters.

**Formal argument list forms:**

| Form | Behavior |
| --- | --- |
| `(v1 … vn)` | Fixed n arguments |
| `v` | Any number of arguments → list bound to `v` |
| `(v1 … vn . vk)` | At least n arguments, rest as list in `vk` |

```scheme
((lambda x x) 3 4 5 6)         ⟹  (3 4 5 6)
((lambda (x y . z) z) 3 4 5 6) ⟹  (5 6)
```

Duplicate variables in `<formals>` is an error.

## Conditionals

Syntax:
```scheme
(if <test> <consequent> <alternate>)
(if <test> <consequent>)
```

`<test>` evaluated first. If true, evaluate `<consequent>`. Otherwise evaluate `<alternate>`. If test is false and no alternate specified, result is unspecified.
