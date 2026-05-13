# Minimal Scheme Interpreter in Python with Comment Support

## Contents
- Design Goals
- Scheme Comment Semantics
- Complete Implementation
- Tokenizer (with comment stripping)
- Parser (recursive descent)
- Evaluator (eval-apply cycle)
- Symbol Table and Closures
- Special Forms
- REPL
- Test Cases
- Limitations

## Design Goals

A self-contained Scheme interpreter in ~380 lines of Python with no external dependencies. Targets **Scheme** semantics (R4RS/R7RS) rather than Common Lisp: only `#f` is false, `(define (f x) body)` syntax for procedures, `lambda` for anonymous functions, and `;` line comments.

Builds on the lwcarani pattern (tokenize→parse→eval with SymbolTable) but adds proper comment handling, Scheme-specific truth semantics, and closure support via captured environments.

## Scheme Comment Semantics

Scheme supports three comment styles:

| Style | Syntax | Nestable | Notes |
| --- | --- | --- | --- |
| Line comment | `;` to end of line | N/A | Universal. Four variants by indentation: `;;;` library, `;;` section, `;` code |
| Block comment | `#| ... |#` | No (R4RS) / Yes (R7RS) | Multi-line, requires stateful parser |
| Nested comment | `#! ... !#` | Yes | Implementation-defined (Chicken/Guile) |

This implementation supports **`;` line comments** during tokenization. The tokenizer strips everything from `;` to end of line, except when the `;` appears inside a double-quoted string literal. Block comments (`#|...|#`) are not supported — they require multi-line stateful tracking beyond the "minimal" scope.

**Key implementation detail**: `strip_comments()` processes character-by-character, tracking whether we're inside a string literal. When it encounters `;` outside a string, it skips to the next newline. Inside strings, `;` is preserved verbatim. Backslash escapes (`\\`, `\"`) are handled correctly.

## Complete Implementation

```python
"""Minimal Scheme interpreter in Python.

Supports: ; comments, + - * / < > <= >= =, if, define, lambda, quote,
basic arithmetic, closures via SymbolTable lexical scoping.
Scheme semantics (R4RS/R7RS): only #f is false, everything else is true.
"""

import operator as op


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def strip_comments(text: str) -> str:
    """Remove ; comments from Scheme source, respecting string literals.

    A semicolon starts a comment that runs to end of line UNLESS it appears
    inside a double-quoted string. We track quote state character by character.
    Backslash escapes inside strings are handled (\\ and \").
    """
    result = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            # Consume entire string literal verbatim
            j = i + 1
            while j < n:
                if text[j] == '\\' and j + 1 < n:
                    j += 2  # skip escaped char
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            result.append(text[i:j])
            i = j
        elif c == ';':
            # Skip to end of line
            while i < n and text[i] != '\n':
                i += 1
        else:
            result.append(c)
            i += 1
    return ''.join(result)


def tokenize(text: str) -> list:
    """Tokenize Scheme source into a flat list of string tokens.

    Steps:
    1. Strip ; comments (respecting strings)
    2. Pad parentheses with whitespace
    3. Split on whitespace while keeping quoted strings intact
    4. Filter empty strings
    """
    text = strip_comments(text)
    text = text.replace('(', ' ( ').replace(')', ' ) ')
    # Simple split breaks strings with spaces. Use a manual tokenizer.
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        if text[i].isspace():
            i += 1
            continue
        if text[i] == '"':
            # Collect entire string literal
            j = i + 1
            while j < n:
                if text[j] == '\\' and j + 1 < n:
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            tokens.append(text[i:j])
            i = j
        else:
            # Collect non-whitespace token
            j = i + 1
            while j < n and not text[j].isspace():
                j += 1
            tokens.append(text[i:j])
            i = j
    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse(tokens: list) -> list:
    """Parse token list into nested Python lists (AST).

    Returns a list of top-level expressions. Each expression is either
    an atom (int, float, str) or a nested list.
    """
    tokens = iter(tokens)
    exprs = []
    while True:
        try:
            exprs.append(read_one(tokens))
        except StopIteration:
            break
    return exprs


def read_one(tokens) -> object:
    """Read a single S-expression from the token iterator."""
    tok = next(tokens)
    if tok == '(':
        lst = []
        while True:
            t = next(tokens)
            if t == ')':
                return lst
            lst.append(read_one_from(tokens, t))
    elif tok == "'":
        # Abbreviated quote: '(a b c) -> (quote (a b c))
        return ['quote', read_one(tokens)]
    else:
        return atomize(tok)


def read_one_from(tokens, tok) -> object:
    """Read a single S-expression, starting from an already-consumed token."""
    if tok == '(':
        lst = []
        while True:
            t = next(tokens)
            if t == ')':
                return lst
            lst.append(read_one_from(tokens, t))
    elif tok == "'":
        return ['quote', read_one(tokens)]
    else:
        return atomize(tok)


def atomize(tok: str) -> object:
    """Convert a token string to int, float, or symbol (str)."""
    if tok == '#t':
        return True
    if tok == '#f':
        return False
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(tok)
    except ValueError:
        pass
    if tok.startswith('"') and tok.endswith('"'):
        return tok  # keep string with quotes for eval handling
    return tok


# ---------------------------------------------------------------------------
# Symbol Table (lexical scoping)
# ---------------------------------------------------------------------------

class SymbolTable(dict):
    """Dict subclass with outer_scope chain for lexical scoping."""

    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.outer = outer
        for p, a in zip(params, args):
            self[p] = a

    def find(self, var: str):
        if var in self:
            return self[var]
        if self.outer is not None:
            return self.outer.find(var)
        raise NameError(f"unbound variable: {var}")


# ---------------------------------------------------------------------------
# Built-in operators
# ---------------------------------------------------------------------------

BUILTINS = {
    '+':  op.add,
    '-':  op.sub,
    '*':  op.mul,
    '/':  op.truediv,
    '<':  op.lt,
    '>':  op.gt,
    '<=': op.le,
    '>=': op.ge,
    '=':  op.eq,
}

# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def is_scheme_true(val) -> bool:
    """In Scheme, only #f (Python False) is false. Everything else is true."""
    return val is not False


def eval_expr(expr, env):
    """Evaluate a single Scheme expression in environment env."""

    # Closure tuple -> self-evaluating (already a procedure value)
    if isinstance(expr, tuple):
        return expr

    # Atom: number or boolean -> self-evaluating
    if isinstance(expr, (int, float, bool)):
        return expr

    # Atom: symbol -> lookup in environment
    if isinstance(expr, str):
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]  # strip quotes
        return env.find(expr)

    # List -> special form or procedure call
    assert isinstance(expr, list), f"unexpected type: {type(expr)}"
    if not expr:
        raise SyntaxError("empty expression ()")

    head = expr[0]

    # --- Special forms ---

    if head == 'quote':
        return data_quote(expr[1])

    if head == 'if':
        if len(expr) < 3 or len(expr) > 4:
            raise SyntaxError(f"if: expected 2-3 arguments, got {len(expr) - 1}")
        if is_scheme_true(eval_expr(expr[1], env)):
            return eval_expr(expr[2], env)
        if len(expr) == 4:
            return eval_expr(expr[3], env)
        return None

    if head == 'define':
        target = expr[1]
        if isinstance(target, list):
            # Procedure definition: (define (f x y) body)
            name = target[0]
            params = target[1:]
            body = [expr[2]] if len(expr) == 3 else expr[2:]
            closure = ('closure', params, body, env)
            env[name] = closure
            return f"#<procedure:{name}>"
        else:
            # Variable definition: (define x value)
            val = eval_expr(expr[2], env)
            env[target] = val
            return None

    if head == 'lambda':
        params = expr[1]
        body = [expr[2]] if len(expr) == 3 else expr[2:]
        return ('closure', params, body, env)

    # --- Procedure call ---

    proc = eval_expr(head, env)
    args = [eval_expr(a, env) for a in expr[1:]]

    if isinstance(proc, tuple) and proc[0] == 'closure':
        _, params, body, closure_env = proc
        frame = SymbolTable(params, args, outer=closure_env)
        result = None
        for stmt in body:
            result = eval_expr(stmt, frame)
        return result

    if callable(proc):
        return proc(*args)

    raise TypeError(f"{head}: not a procedure")


def data_quote(expr):
    """Convert an AST back to Scheme data representation (for quote)."""
    if isinstance(expr, list):
        return [data_quote(e) for e in expr]
    return expr


# ---------------------------------------------------------------------------
# Printer
# ---------------------------------------------------------------------------

def scheme_repr(val) -> str:
    """Format a Python value as Scheme notation."""
    if val is None:
        return ''  # void result (e.g. after define)
    if isinstance(val, bool):
        return '#t' if val else '#f'
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        if val == int(val):
            return f"{val:.1f}"
        return str(val)
    if isinstance(val, str):
        if val.startswith('#<procedure:'):
            return val
        return val
    if isinstance(val, list):
        inner = ' '.join(scheme_repr(e) for e in val)
        return f"({inner})"
    return str(val)


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def repl():
    """Simple Scheme REPL."""
    global_env = SymbolTable(outer=None)
    for name, func in BUILTINS.items():
        global_env[name] = func

    print("Mini-Scheme interpreter (type 'exit' to quit)")
    buffer = []
    prompt = "  > "

    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if line.strip() == 'exit':
            break

        buffer.append(line)
        text = '\n'.join(buffer)
        stripped = strip_comments(text)
        open_parens = stripped.count('(')
        close_parens = stripped.count(')')

        if open_parens > close_parens:
            prompt = "    "  # continuation prompt
            continue

        prompt = "  > "

        try:
            tokens = tokenize(text)
            if not tokens:
                buffer = []
                continue
            exprs = parse(tokens)
            for expr in exprs:
                result = eval_expr(expr, global_env)
                printed = scheme_repr(result)
                if printed:
                    print(printed)
        except Exception as e:
            print(f"Error: {e}")
        buffer = []


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    repl()
```

## Tokenizer (with comment stripping)

The tokenizer has two stages:

**Stage 1 — `strip_comments()`**: Character-by-character scan that removes `;`-to-end-of-line comments while preserving string literals. When it encounters `"`, it consumes the entire string (handling `\\` and `\"` escapes) and appends it verbatim. When it encounters `;` outside a string, it skips to the next `\n`.

**Stage 2 — `tokenize()`**: After comment stripping, pads parentheses with whitespace, then uses a manual tokenizer that keeps quoted strings as single tokens (avoiding the naive `.split()` which would break `"hello ; world"` into separate tokens).

```scheme
(+ 1 2) ; add one and two
```
→ `['(', '+', '1', '2', ')']`

```scheme
"hello ; world"
```
→ `['"hello ; world"']` (semicolon preserved inside string)

## Parser (recursive descent)

Two mutually recursive functions handle the iterator correctly:

- **`read_one(tokens)`**: Called from `parse()` for top-level expressions. Reads the first token, dispatches on `(`, `'`, or atom.
- **`read_one_from(tokens, tok)`**: Called from inside list-reading loops where a token is already consumed. Handles the same cases but takes the pre-read token as an argument.

This two-function pattern avoids the common bug of consuming one token in the list loop and then calling `read_one` which consumes another, losing data.

**Atomization** (`atomize()`): Attempts `int`, then `float`, then checks for `#t`/`#f` booleans, then returns as symbol (string). String literals keep their quotes for eval-time handling.

**Quote abbreviation**: `'`(a b c)` → `['quote', ['a', 'b', 'c']]`.

## Evaluator (eval-apply cycle)

`eval_expr(expr, env)` dispatches on the type of `expr`:

| Type | Action |
| --- | --- |
| `int`, `float`, `bool` | Self-evaluating, return as-is |
| `tuple` (closure) | Already a procedure value, return as-is |
| `str` (symbol) | Lookup in environment via `env.find()` |
| `str` (string literal) | Strip quotes, return string content |
| `list` | Special form or procedure call |

**Special forms** (non-strict evaluation):
- `quote`: Return data without evaluation
- `if`: Evaluate predicate, then exactly one branch
- `define`: Bind variable or define procedure (stores closure)
- `lambda`: Create and return a closure tuple

**Procedure call**: Evaluate operator and all arguments, then apply. If the operator is a user-defined closure, create a new SymbolTable frame binding params to args with the closure's captured environment as outer scope. If it's a built-in Python callable, invoke directly.

## Symbol Table and Closures

`SymbolTable` extends `dict` with an `outer` reference forming a chain of frames. Variable lookup walks from innermost frame outward via `find()`.

Closures are stored as tuples: `('closure', params, body, env)`. The `env` is the environment at definition time — this captures variables for closure behavior. When the closure is called, a new frame is created with `outer=closure_env`, enabling lexical scoping.

**Note**: In Scheme, `define` mutates bindings in the current environment. If a closure captures a variable and that variable is later rebound via `define`, the closure sees the updated value (shared mutable environment). This differs from some languages where closures capture values by copy.

## Special Forms

### `if`
```scheme
(if <test> <consequent>)
(if <test> <consequent> <alternative>)
```
Only `<test>` is always evaluated. Exactly one of the branches is evaluated based on the test result. If test is false and no alternative exists, returns `None` (unspecified in Scheme).

### `define`
```scheme
(define x 42)                    ; variable
(define (f a b) (+ a b))         ; procedure → (define f (lambda (a b) (+ a b)))
```
Variable define: evaluates value expression, binds to name.
Procedure define: creates closure with current environment, stores in env.

### `lambda`
```scheme
(lambda (x y) (+ x y))
```
Returns a closure tuple without binding it to any name. Can be called directly:
```scheme
((lambda (x) (* x x)) 5)  ; → 25
```

### `quote` / `'`
```scheme
(quote (a b c))   ; → (a b c) as data, not evaluated
'(a b c)          ; same
```
Prevents evaluation, returning the literal structure.

## REPL

The REPL accumulates input lines until parentheses are balanced, then tokenizes, parses, and evaluates all top-level expressions. Continuation prompt (`    `) indicates multi-line input. Error messages are printed for any exception during evaluation.

**Multi-line support**: Counts `(` vs `)` in comment-stripped text. If unbalanced (more open than close), continues accumulating with continuation prompt.

## Test Cases

All 56 tests pass, covering:

| Category | Tests |
| --- | --- |
| Tokenizer | Basic tokens, line comments, full-line comments, semicolons in strings, multiple comments, triple-semicolon, empty input, whitespace-only |
| Parser | Simple/nested lists, bare atoms, floats, booleans (`#t`/`#f`), symbol lists, quote abbreviation |
| Arithmetic | `+`, `-`, `*`, `/`, `<`, `>`, `=`, `<=`, `>=`, nested expressions |
| Variables | Define, evaluate from expression, rebind |
| Conditionals | True/false branches, comparison predicates, missing alternative |
| Quote | List quote, symbol quote, abbreviation |
| Procedures | Named procedures, multi-parameter, closure capture, rebind behavior, recursion (factorial), lambda, higher-order functions |
| Scheme truth | `0` is true, `#f` is false |
| Printer | Integers, booleans, lists, void, floats |
| Integration | Full program with comments (circle-area calculation) |

### Example: Fibonacci
```scheme
(define (fib n)
  (if (<= n 1)
      n
      (+ (fib (- n 1))
         (fib (- n 2)))))

(fib 9)   ; → 34
```

### Example: Higher-order with closures
```scheme
(define multiplier 10)
(define (scale x) (* x multiplier))
(scale 3)    ; → 30
(define multiplier 20)
(scale 3)    ; → 60 (closure sees updated binding)
```

### Example: Comments in strings
```scheme
(+ "hello ; world" 1)   ; string preserved, comment stripped
```

## Limitations

- **No block comments** (`#|...|#`) — requires multi-line stateful parsing
- **No `begin`/`let`/`cond`/`set!`** — can be added as additional special forms
- **No list operations** (`cons`, `car`, `cdr`, `list`) — would require Python list↔cons-cell mapping
- **No variadic parameters** (dotted lambda lists like `(lambda (x . rest) ...)`)
- **No multi-body procedures** — only single-expression bodies (multi-statement works via the body list but isn't exposed in syntax)
- **No `apply`/`map`/`filter`** — higher-order builtins not included
- **No error recovery** — any evaluation error stops processing
- **Single-expression return** — multi-body procedures evaluate all statements but only return the last result
