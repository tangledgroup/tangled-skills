# O-Expressions

**Author:** Olivier Breuleux  
**Source:** https://breuleux.net/blog/oexprs.html  
**Year:** 2014  
**Implementations:** Liso (Racket), Earl Grey (compile-to-JS)

## Overview

O-expressions (operator expressions) are an alternative to s-expressions designed for **extensible syntax**. Unlike sweet-expressions (which abbreviate s-expressions) or i-expressions (which use indentation), o-expressions define a fundamentally different AST structure based on operators, juxtaposition, and explicit list nodes.

The core insight: s-expressions conflate function application and list construction into a single data structure. O-expressions separate them into distinct node types, enabling cleaner semantics and less punctuation.

## Design Principles

O-expressions are designed to satisfy four properties:

1. **Context invariance** — All tokens have the same syntactic role everywhere. `{x}` here and `{x}` there produce the same AST.
2. **Ubiquity** — Any moderately sized source file should exhibit all syntax rules. No hidden context-specific behavior.
3. **Genericity** — Standard constructs and user-defined constructs are indistinguishable visually and structurally.
4. **AST simplicity and manipulability** — The AST must be very simple and easy to manipulate programmatically.

## AST Node Types

O-expressions use only three internal node types (plus leaves):

| Node Type | Syntax | Description |
|-----------|--------|-------------|
| `Apply[f, x]` | `f x` | Function application (left-associative) |
| `Op[op, a, b, ...]` | `a <op> b` | Operator call |
| `List[a, b, ...]` | `[a, b, ...]` | Explicit list |
| `Seq[a, b, ...]` | `a, b, ...` | Statement sequence |
| (grouping) | `(...)` | Parentheses for grouping (not in AST) |

### Priority (highest to lowest)

```
juxtaposition → operators → comma → brackets
```

## Syntax Rules

### Juxtaposition (Application)

Whitespace-separated tokens form left-associative application:

```
f x y    =>    Apply[Apply[f, x], y]
f.       =>    Apply[f] (nullary, apply f to no arguments)
```

This is **currying**, not multi-argument application. `f x y` applies `f` to `x`, then applies the result to `y`.

### Operators

```
a <op> b    =>    Op[op, a, b]
a <op> b <op> c    =>    Op[op, a, b, c]
```

Operators are defined by a set of "operator characters". Any sequence of those characters forms an operator. This creates an unbounded number of operators for extension.

### Lists

```
[]        =>    List (empty)
[x, y]    =>    List[x, y]
```

Lists are explicit and comma-separated. They do not imply function application.

### Sequencing

```
a, b, c    =>    Seq[a, b, c]
```

Sequences return the value of the last expression. Used for function bodies and control structure branches. `Seq[expr]` is semantically equivalent to `expr`.

### Grouping

```
(...)    =>    grouping (not in AST)
```

Parentheses ensure enclosed content corresponds to a single AST node but do not appear in the AST themselves.

## Iteration History

The o-expression design evolved through four iterations:

### Iteration 1: Basic Rules

Very close to s-expressions with infix operators and juxtaposition application. Still very parenthesey.

```
diag = (x y -> (((x * x) + (y * y)) ^ 0.5))
if (diag 3 4 == 5) (print "hello") (print "world")
```

### Iteration 2: Operator Priority

Added a priority graph for common operators (standard arithmetic order, right-associative declarations/lambdas). Removes most parentheses.

```
diag = x y -> (x * x + y * y) ^ 0.5
if (diag 3 4 == 5) (print "hello") (print "world")
```

### Iteration 3: Sequencing and Comma Separation

Enforced distinction between application (`f x`) and lists/sequences (`[a, b]`, `a, b`). Line breaks become normal whitespace.

```
diag = x y -> (x * x + y * y) ^ 0.5
if (diag 3 4 == 5) (print "hello", print "world")
```

### Iteration 4: Currying and Explicit Lists

Reinterpreted juxtaposition as left-associative currying. Added `[a, b, ...]` for lists. Eliminated the `x.` nullary wart.

```
diag = x -> y -> (x * x + y * y) ^ 0.5
if (diag 3 4 == 5) (print "hello", print "world")

; Or with list arguments:
diag = [x, y] -> (x * x + y * y) ^ 0.5
if (diag[3, 4] == 5) (print "hello", print "world")
```

## Aggregative Operators

A key extensibility mechanism: instead of operator precedence, **aggregate** different operators by concatenating their names:

```
x <op1> y <op2> z    =>    (<op1>_<op2>)[x, y, z]
```

This enables named multi-operator constructs without adding new syntax rules:

```
@while (x < 0): (x += 1)        =>    (@while_:)[x < 0, x += 1]
@if (x < 0) @then "-" @else "+" =>    (@if_@then_@else)[x < 0, "-", "+"]
@for x <- xs: print[x]          =>    (@for_<-_:)[x, xs, print[x]]
```

### Advantages

- **Readable** — operators visually split the parts
- **Easy to define** — every combination has a unique name
- **Namespace isolation** — macros get their own namespace via `@` prefix
- **Trivial syntax highlighting** — each aggregated operator is a distinct token
- **No new sugar** — uses existing juxtaposition and operator rules

## Comparison with S-Expressions

| Aspect | S-Expressions | O-Expressions |
|--------|--------------|---------------|
| Apply encoding | Implicit (first element of list) | Explicit `Apply` node |
| Lists | Same as application | Separate `List` node |
| Functions on lists | Forced (all apply to lists) | Not required (currying or lists) |
| Punctuation | Heavy parentheses | Operators, brackets, commas |
| Node types | 1 (list) | 3–4 (Apply, Op, List, Seq) |
| Nesting collapse incentive | High (save parens) | Low (structure is explicit) |

### Example: Decoupling Apply and List

In s-expressions, `(f (g x))` and `(f g x)` are distinguishable only by nesting. In o-expressions, `Apply[f, Apply[g, x]]` and `Apply[f, List[g, x]]` use different node types — no ambiguity.

### Example: Let Syntax

O-expressions encourage proper structure without collapsing:

```
@let (x = 1, y = 2): x + y
```

Instead of the Clojure-style flattened `(let [x 1 y 2] ...)`.

## What Won't Work (Per the Author)

The following approaches are rejected for o-expressions:

- **Template-based macros** — Not flexible enough for structural manipulation
- **Hard-coded syntax** — Creates first-class structures that extensions must compete with
- **Context-sensitive syntax** — e.g., Python's comma priority changing by context; violates context invariance

## Relationship to Other Syntaxes

O-expressions are **not** m-expressions. Key difference: o-expressions do not require functions to take lists of arguments. `f[x, y]` and `f x y` are both valid but have different semantics (list-based call vs. curried application). This means o-expressions cannot be directly translated to s-expressions — the node types carry semantic information that s-expressions erase.
