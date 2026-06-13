# Minimal 16-Line Lisp in Python (ByteGoblin)

## Contents
- Full Implementation
- Tokenization
- Parsing
- Evaluation
- Limitations

## Full Implementation

```python
def lisp(input):
    def parse(expression):
        return expression[1:] if expression[0] == '(' else expression

    def eval_ast(ast):
        if isinstance(ast, str):
            return float(ast) if ast.isdigit() else ast
        if ast[0] == 'add':
            return eval_ast(ast[1]) + eval_ast(ast[2])
        elif ast[0] == 'sub':
            return eval_ast(ast[1]) - eval_ast(ast[2])

    tokens = input.replace('(', ' ( ').replace(')', ' ) ').split()
    return eval_ast(parse(tokens))
```

## Tokenization

Same paren-padding + `split()` pattern as other Python Lisp interpreters. Input `(add 1 (sub 5 2))` becomes `['(', 'add', '1', '(', 'sub', '5', '2', ')', ')']`.

## Parsing

Strips outer parentheses by discarding first token when it is `(`:

```python
def parse(expression):
    return expression[1:] if expression[0] == '(' else expression
```

Result: `['add', '1', ['sub', '5', '2']]` — a nested list AST.

## Evaluation

Recursive `eval_ast` dispatches on first element of list:
- If string: parse as float if numeric, otherwise return as symbol
- If `add`: recursively evaluate both operands and add
- If `sub`: recursively evaluate both operands and subtract

```python
print(lisp("(add 1 (sub 5 2))"))  # Output: 4.0
```

## Limitations

Handles only `add` and `sub`. No variables, functions, conditionals, or error handling. Serves as proof-of-concept demonstrating the minimum viable eval-parse-tokenize pipeline.
