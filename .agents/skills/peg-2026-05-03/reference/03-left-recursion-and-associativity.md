# Left Recursion and Associativity

## Contents
- The Left Recursion Problem
- Idiomatic Workaround
- Left Recursion Support Techniques
- Associativity Control

## The Left Recursion Problem

Traditional PEGs are defined as **well-formed** only when they contain no left-recursive rules. Left recursion causes infinite loops in naive recursive descent parsers.

### Direct left recursion

A rule where the leftmost symbol in an alternative is the rule itself:

```
# DIRECT left recursion — infinite loop
Sum ← Sum '+' Term
    / Term
```

When parsing `Sum`, the parser immediately calls `Sum` again, which calls `Sum` again, ad infinitum. No input is consumed before the recursive call.

### Indirect left recursion

Circular dependency through multiple rules:

```
# INDIRECT left recursion
Expr ← Sum
Sum  ← Expr '+' Term   # Expr → Sum → Expr → ... infinite
```

### Hidden left recursion

Left recursion that may or may not occur depending on an optional sub-expression:

```
# HIDDEN left recursion — if Y? matches empty, this is left-recursive
X ← Y? X
   / Base
```

If `Y?` succeeds consuming zero characters, the parser calls `X` from the same position with no progress, creating infinite recursion.

### Practical significance

In CFGs, left recursion is the natural way to express left-associative operators:

```
# Natural CFG form for left-associative addition
Sum → Sum '+' Term | Term
```

PEG practitioners often expect to use this idiom but cannot with traditional packrat parsers. However, PEG repetition operators handle most repetition cases without recursion:

```
# Idiomatic PEG — no left recursion needed
Sum ← Term (('+' / '-') Term)*
```

This works for simple operator chains. It does not work when the recursive structure is about more than repetition (e.g., complex precedence with mixed associativity).

## Idiomatic Workaround

Rewrite left-recursive rules to use right recursion with repetition:

| Left-recursive (CFG style) | Right-recursive (PEG idiomatic) |
|---|---|
| `Sum ← Sum '+' Term / Term` | `Sum ← Term ('+' Term)*` |
| `Args ← Arg ',' Args / Arg` | `Args ← Arg (',' Arg)*` |

**Tradeoff:** The repetition form produces a flat list in the parse tree, not a binary tree. Left-associativity must be imposed during AST construction:

```
# Parse tree for "a + b + c" using Term ('+' Term)*
# Result: [Term(a), Term(b), Term(c)] — flat list
# AST construction must fold left: ((a + b) + c)
```

For right-associative operators (e.g., exponentiation), use direct right recursion:

```
# Right-recursive — naturally produces right-associative tree
Power ← Value ('^' Power)?
# Parse tree for "a ^ b ^ c": a ^ (b ^ c)
```

## Left Recursion Support Techniques

### Ford/Warth iterative fixed-point

Warth et al. (2008) extended packrat parsing to support direct left recursion using an iterative fixed-point algorithm:

1. On first call to left-recursive rule at position p, store "in progress" marker
2. On recursive call to same rule at same position, return best result so far
3. After each alternative completes, update memo if it consumed more input
4. Repeat until no improvement (fixed point reached)

**Properties:**
- Supports direct left recursion
- Loses guaranteed linear-time parsing (may iterate multiple times per position)
- Does not handle indirect or hidden left recursion
- Used by CPython pegen

### OMeta algorithm

OMeta supports full direct and indirect left recursion without additional complexity, but again at the cost of linear-time guarantees.

### Autumn expression clusters

Autumn introduces **expression clusters** — a grouping construct where alternatives are parsed together with explicit precedence and associativity annotations:

```
# Expression cluster with explicit precedence
E = expr
  → E '+' E @+ @left recur
  → E '-' E
  → E '*' E @+ @left recur
  → E '/' E
  → [0-9]   @+
```

- `@+` increments precedence level
- `@left recur` marks the rule as left-recursive (enables fixed-point iteration)
- Right associativity is default (no annotation needed)
- Performance: O(P × L) without full memoization

### Pika parsing (bottom-up)

Pika parsing applies PEG rules bottom-up and right-to-left, the inverse of recursive descent order. This naturally handles left recursion without rewriting or fixed-point iteration, and provides optimal error recovery.

## Associativity Control

Associativity determines how chains of same-precedence operators group:

### Left-associative
`a - b - c` → `(a - b) - c`
- Addition, subtraction, multiplication, division
- With idiomatic PEG `Term ('+' Term)*`, the parse tree is flat — fold left during AST construction

### Right-associative
`a ^ b ^ c` → `a ^ (b ^ c)`
- Exponentiation, assignment
- Use right-recursive form: `Power ← Value ('^' Power)?`

### Without left recursion support

When using the idiomatic repetition form, all operators produce flat lists. Associativity is a post-parse concern:

```python
# Post-parse: fold flat list into left-associative tree
def build_left_assoc(operands, op):
    result = operands[0]
    for i in range(1, len(operands)):
        result = Tree(op, result, operands[i])
    return result
```

### With expression clusters

Associativity is explicit per-operator:

```
# Left-associative + and -, right-associative ^
Expr ← expr
  → Expr '+' Expr @+ @left recur   # left-associative
  → Expr '-' Expr                  # inherits left-recursive
  → Expr '^' Expr @+               # right-associative (default, no @left recur)
  → Number @+
```
