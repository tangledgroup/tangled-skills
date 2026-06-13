# Scheme Interpreter in Python with Lark Parser (John Jacobsen)

## Contents
- Approach Comparison
- Lark Grammar
- Data Model
- Evaluation and Special Forms
- Printing
- Testing

## Approach Comparison

Three parsing approaches considered:
1. **PLY** — found clumsy compared to Clojure's Instaparse
2. **Regex** — worked for simple cases but failed on nested lists in non-final positions (e.g., `(+ (* 2 3) 4)`)
3. **Lark** — EBNF grammar, returns parse tree directly; chosen approach

Norvig's `lis.py` uses simpler split-on-parens approach with nesting-level tracking, which is elegant but less extensible for complex syntax.

## Lark Grammar

```
start  : _exprs
_exprs : _e* _e
_e     : ATOM
       | _num
       | BOOL
       | list
TRUE   : "#t"
FALSE  : "#f"
BOOL   : TRUE | FALSE
list   : "(" _exprs? ")"
INT    : /[-+]?[0-9]+/
ATOM   : /[a-zA-Z]+[a-zA-Z0-9\-\?]*/
       | /[\*\/\=\>\<]/
       | /[\-\+](?![0-9])/
FLOAT  : /[-+]?[0-9]+\.[0-9]*/
_num   : INT | FLOAT
%import common.WS
%ignore WS
```

## Data Model

Tuple-based internal representation (not objects):

| Type | Example |
| --- | --- |
| Atom | `('atom', 'foo')` |
| Boolean | `('bool', True)` |
| Int | `('int', 123)` |
| Float | `('float', 3.14)` |
| List | `('list', [('atom', 'define'), ...])` |

Example conversion:

```scheme
(define (abs x)
  (if (< x 0)
      (- x)
      x))
```

Becomes:
```python
[('list', [('atom', 'define'),
           ('list', [('atom', 'abs'), ('atom', 'x')]),
           ('list', [('atom', 'if'),
                     ('list', [('atom', '<'), ('atom', 'x'), ('int', 0)]),
                     ('list', [('atom', '-'), ('atom', 'x')]),
                     ('atom', 'x')])])]
```

## Evaluation and Special Forms

Special forms handled as individual cases:
- `quote` — return data without evaluation
- `cond` / `if` — conditional branching
- `define` — variable/function binding
- `lambda` — anonymous function creation
- `or` / `and` — short-circuit boolean logic

Normal function application: evaluate all arguments first, then apply.

## Printing

```python
def printable_value(ast):
    k, v = ast
    if k == 'int' or k == 'float':
        return str(v)
    if k == 'bool':
        return {True: "#t", False: "#f"}.get(v)
    if k == 'intproc':
        return "Internal procedure '%s'" % v
    if k == 'atom':
        return v
    if k == 'list':
        return '(' + ' '.join([printable_value(x) for x in v]) + ')'
    if k == 'nop':
        return ''
    if k == 'fn':
        (fn_name, _, _) = v
        if fn_name == 'lambda':
            return "Anonymous-function"
        return "Function-'%s'" % str(fn_name)
```

`nop` type suppresses output (e.g., after `define`).

## Testing

Test-driven development workflow. Unit tests verify each expression evaluates correctly. Strict TDD cycle: write failing test, implement minimum code, verify green.
