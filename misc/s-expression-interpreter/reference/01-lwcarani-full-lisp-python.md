# Full Lisp Interpreter in Python (Luke Carani)

## Contents
- Type System
- Lexer
- Parser (AST Generation)
- Symbol Table and Scoping
- Evaluation
- Paren Matching

## Type System

Lisp types mapped to Python:

```python
Symbol = str            # Lisp Symbol → Python str
Number = (int, float)   # Lisp Number → Python int or float
Atom = (Symbol, Number) # Lisp Atom → Symbol or Number
List = list             # Lisp List → Python list
Exp = (Atom, List)      # Lisp Expression → Atom or List
```

## Lexer

Lisp's parenthesized syntax allows trivial tokenization via `str.split()`:

```python
def tokenize(input: str) -> List[str]:
    """Pad parens with whitespace before splitting."""
    return input.replace("(", " ( ").replace(")", " ) ").split()
```

Input `'(+ 1 2)'` tokenizes to `['(', '+', '1', '2', ')']`.

## Parser (AST Generation)

Recursive descent parser converts tokens into nested Python lists:

```python
def generate_ast(tokens: List) -> List:
    t = tokens.pop(0)
    if t == "(":
        ast = []
        while tokens[0] != ")":
            ast.append(generate_ast(tokens))
        tokens.pop(0)  # consume ')'
        return ast
    elif t == ")":
        raise SyntaxError("Mismatched parens.")
    else:
        return atomize(t)

def atomize(token: str) -> Atom:
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)
```

Token `['(', 'defun', 'doublen', '(', 'n', ')', '(', '*', 'n', '2', ')', ')']` becomes `['defun', 'doublen', ['n'], ['*', 'n', 2]]`.

## Symbol Table and Scoping

Nested `dict` subclass with outer-scope chain for lexical scoping:

```python
class SymbolTable(dict):
    def __init__(self, params, args, outer_scope=None):
        self.update(zip(params, args))
        self.outer_scope = outer_scope

    def find(self, var):
        if var in self:
            return self[var]
        elif self.outer_scope is not None:
            return self.outer_scope.find(var)
        else:
            raise NameError(f"NameError: name '{var}' is not defined")
```

Global symbol table pre-loaded with `operator` module functions (`+`, `-`, `*`, `/`, `<`, `>`, etc.) and `math` library.

## Evaluation

```python
def eval(x: Exp, st=global_symbol_table):
    if isinstance(x, Number):
        return x
    elif isinstance(x, Symbol):
        return st.find(x)
    elif x[0] == "if":
        condition, statement, alternative = x[1:4]
        expression = (statement if eval(condition, ...) else alternative)
        return eval(expression, ...)
    elif x[0] == "defun":
        func_name, params, func_body = x[1:4]
        st[func_name] = (params, func_body)
        return f"Defined function: {func_name.upper()}"
    elif x[0] == "format":
        # String interpolation with ~D~% and ~% placeholders
        ...
    else:
        func = eval(x[0], ...)
        args = [eval(arg, ...) for arg in x[1:]]
        if isinstance(func, tuple):  # user-defined function
            params, func_body = func
            st.update(zip(params, args))
            return eval(func_body, SymbolTable(st.keys(), st.values(), st))
        else:
            return func(*args)
```

Supported forms: arithmetic operators, `if`, `defun` (function definition), `format` (string interpolation).

## Paren Matching

Functional approach using map-reduce to validate balanced parentheses:

```python
def are_parens_matched_map_reduce(s: str) -> bool:
    t = tokenize(s)
    d = {"(": 1, ")": -1}
    res = reduce(lambda a, b: a + b, map(lambda x: d.get(x, 0), t))
    if res != 0:
        raise SyntaxError(f'Input string "{s}" contains mismatched parens.')
    return True
```

Maps `(` to `1`, `)` to `-1`, all other tokens to `0`. Sum of `0` means balanced.
