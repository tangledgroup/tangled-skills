# Minimal Scheme Interpreter with Comments in Python

## Contents
- Design Goals
- Complete Implementation
- Comment Handling
- Tokenizer
- Parser
- Evaluator
- Usage Examples
- Limitations

## Design Goals

A minimal Scheme-style interpreter in ~25 lines of Python. Based on the bytegoblin 16-line Lisp pattern (tokenize→parse→eval) but adds **`;` line comment support** during tokenization, matching Scheme's standard comment syntax.

Fills the gap between the ultra-minimal 16-line PoC (`02-bytegoblin-minimal-lisp-python.md`) and the full Scheme interpreter with closures (`12-full-scheme-interpreter-python.md`). No SymbolTable, no closures, no special forms — just arithmetic operations that ignore comments.

## Complete Implementation

```python
import re

def scheme(input):
    def parse(tokens):
        if not tokens:
            return None
        if tokens[0] == '(':
            tokens.pop(0)
            expr = []
            while tokens and tokens[0] != ')':
                expr.append(parse(tokens))
            tokens.pop(0)  # discard ')'
            return expr
        return tokens.pop(0)

    def eval_ast(ast):
        if isinstance(ast, str):
            return float(ast) if re.match(r'^-?\d+(\.\d+)?$', ast) else ast
        op = ast[0]
        if op == 'add':
            return eval_ast(ast[1]) + eval_ast(ast[2])
        elif op == 'sub':
            return eval_ast(ast[1]) - eval_ast(ast[2])
        elif op == 'mul':
            return eval_ast(ast[1]) * eval_ast(ast[2])
        elif op == 'div':
            return eval_ast(ast[1]) / eval_ast(ast[2])
        raise ValueError(f"Unknown operator: {op}")

    cleaned = re.sub(r';[^\n]*', '', input)
    tokens = cleaned.replace('(', ' ( ').replace(')', ' ) ').split()
    return eval_ast(parse(tokens))
```

## Comment Handling

Scheme uses `;` for line comments. This implementation strips them before tokenization using a single regex:

```python
cleaned = re.sub(r';[^\n]*', '', input)
```

The pattern `;[^\n]*` matches a semicolon followed by any characters up to (but not including) the newline. This correctly handles:

- **Inline comments**: `(add 1 2) ; sum of one and two`
- **Full-line comments**: `; this is a comment\n(add 3 4)`
- **Triple-semicolons** (Scheme convention for library-level): `;;; header comment`
- **Multiple comments**: Each line's comment is stripped independently

**Limitation**: Does not handle `;` inside quoted strings. For a fully correct Scheme tokenizer, string-aware comment stripping is needed (see the full implementation in `12-full-scheme-interpreter-python.md`).

## Tokenizer

Two-step process:
1. **Comment stripping**: `re.sub(r';[^\n]*', '', input)` removes all `;`-to-end-of-line text
2. **Paren padding + split**: Same as the bytegoblin pattern — `replace('(', ' ( ').replace(')', ' ) ').split()`

Input: `(add 1 ; one\n(sub 5 2))`
After comment strip: `(add 1 \n(sub 5 2))`
After tokenization: `['(', 'add', '1', '(', 'sub', '5', '2', ')', ')']`

## Parser

Recursive descent parser that builds a nested list AST from the token stream. Unlike the bytegoblin original (which only stripped outer parens), this properly handles arbitrary nesting by consuming `(` and `)` tokens:

```python
def parse(tokens):
    if not tokens:
        return None
    if tokens[0] == '(':
        tokens.pop(0)
        expr = []
        while tokens and tokens[0] != ')':
            expr.append(parse(tokens))
        tokens.pop(0)
        return expr
    return tokens.pop(0)
```

Result for `(add 1 (sub 5 2))`: `['add', '1', ['sub', '5', '2']]`

## Evaluator

Recursive `eval_ast` dispatches on the first element of each list node:
- **String**: parse as float if numeric (supports negatives and decimals), otherwise return as symbol
- **`add`/`sub`/`mul`/`div`**: evaluate both operands recursively, apply operator
- **Unknown operator**: raises `ValueError` with the operator name

```python
def eval_ast(ast):
    if isinstance(ast, str):
        return float(ast) if re.match(r'^-?\d+(\.\d+)?$', ast) else ast
    op = ast[0]
    if op == 'add':
        return eval_ast(ast[1]) + eval_ast(ast[2])
    # ... other ops
```

## Usage Examples

```python
# Basic arithmetic
print(scheme("(add 1 2)"))           # 3.0
print(scheme("(sub 10 3)"))          # 7.0
print(scheme("(mul 4 5)"))           # 20.0
print(scheme("(div 10 3)"))          # 3.333...

# Nested expressions
print(scheme("(add 1 (sub 5 2))"))   # 4.0

# With comments
print(scheme("(add 1 ; one\n2)"))    # 3.0
print(scheme(";;; calculate total\n(add 10 20)"))  # 30.0
print(scheme("(mul (add 2 3) ; sum=5\n(sub 4 1))"))  # 15.0
```

## Limitations

- Only `add`, `sub`, `mul`, `div` operators — no comparison, boolean, or list operations
- No variables, bindings, or environment
- No functions (`lambda`/`define`) or closures
- No special forms (`if`, `quote`, etc.)
- Comment stripping does not respect string literals (`"hello; world"` would lose text after `;`)
- No error handling for malformed input (missing parens, wrong arity)

For a complete Scheme interpreter with variables, closures, and proper comment handling, see `12-full-scheme-interpreter-python.md`.
