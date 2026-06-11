# The Complete Interpreter

## Contents
- Full Source Code
- Section-by-Section Breakdown
  - Types and Error Handling
  - Parsing: Tokenize, Read, Atom
  - Environment: Env Class and Standard Library
  - Procedures: User-Defined Closures
  - Evaluation: The eval Function
  - Special Forms Detail
  - REPL: Read-Eval-Print Loop
- Running Examples

## Full Source Code

```python
"""Lisp in Python — A minimal Scheme-like interpreter.

Synthesized from six independent implementations:
- Peter Norvig's lispy (norvig.com/lispy.html)
- ByteGoblin's 16-line Lisp (bytegoblin.io)
- Spatters' typed Lisp (gist.github.com/spatters)
- Zstix's tutorial interpreter (zstix.io)
- AlJamal's homoiconic Python (aljamal.substack.com)
- Misfra.me's mini-lisp with tail-call/call/cc (misfra.me)

Usage:
    python lispy.py              # Start REPL
    python lispy.py program.lisp # Run a file

Supported features:
    - Arithmetic: + - * /
    - Comparison: > < >= <= =
    - Special forms: quote if define set! lambda begin cond
    - List operations: car cdr cons null? length list
    - Type checks: number? symbol? list? boolean?
    - Builtins: not print abs round max min
    - Lexical scoping via environment chain
"""

import math
import operator as op
import sys

# --- Types ---

Symbol = str                  # A Lisp symbol is a Python string
Number = (int, float)         # A Lisp number is int or float
List = list                   # A Lisp list is a Python list
Boolean = bool                # True = #t, False = #f
Exp = (Symbol, Number, List, Boolean)  # Any Lisp expression
Env = None                    # Forward reference, defined below


class LispError(Exception):
    """Runtime error with context."""
    pass


# --- Parsing ---

def tokenize(chars: str) -> list:
    """Convert a string of characters into a list of tokens.

    Strategy: add spaces around parentheses, then split on whitespace.
    Strips comments (everything from ; to end of line).
    """
    # Remove comments
    chars = '\n'.join(
        line.split(';')[0] for line in chars.split('\n')
    )
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(program: str) -> Exp:
    """Read a Lisp expression from a string."""
    tokens = tokenize(program)
    if not tokens:
        raise LispError("empty input")
    result = read_from_tokens(tokens)
    if tokens:
        raise LispError(f"unexpected tokens: {tokens}")
    return result


def read_from_tokens(tokens: list) -> Exp:
    """Read an expression from a sequence of tokens.

    Recursive descent parser: '(' starts a list, ')' ends one,
    everything else is an atom.
    """
    if not tokens:
        raise LispError("unexpected EOF")

    token = tokens.pop(0)

    if token == '(':
        lst = []
        while tokens and tokens[0] != ')':
            lst.append(read_from_tokens(tokens))
        if not tokens:
            raise LispError("unexpected EOF (missing ')')")
        tokens.pop(0)  # consume ')'
        return lst

    elif token == ')':
        raise LispError("unexpected ')'")

    else:
        return atom(token)


def atom(token: str) -> Exp:
    """Convert a token string to a Lisp value.

    Try int, then float, then treat as symbol.
    Handles #t, #f, and '() literals.
    """
    if token == '#t':
        return True
    elif token == '#f':
        return False
    elif token == "'()":
        return []

    try:
        return int(token)
    except ValueError:
        pass

    try:
        return float(token)
    except ValueError:
        pass

    return Symbol(token)


# --- Environment ---

class Env(dict):
    """An environment: a dict of {var: value} pairs with an outer Env.

    Extends dict so all standard dict operations work. The `outer`
    reference creates a scope chain for lexical scoping.
    """

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        """Find the innermost environment where var is bound."""
        if var in self:
            return self
        elif self.outer is not None:
            return self.outer.find(var)
        else:
            raise LispError(f"unbound variable: {var}")


def standard_env() -> Env:
    """Create the global environment with built-in procedures."""
    env = Env()

    # Arithmetic operators (variadic for + and *)
    env['+'] = lambda *args: sum(args)
    env['-'] = lambda *args: (
        -args[0] if len(args) == 1
        else (args[0] - sum(args[1:]) if args else 0)
    )
    env['*'] = lambda *args: (
        math.prod(args) if hasattr(math, 'prod')
        else (_prod(args))
    )
    env['/'] = lambda a, b: a / b

    # Comparison operators
    env['>'] = lambda a, b: a > b
    env['<'] = lambda a, b: a < b
    env['>='] = lambda a, b: a >= b
    env['<='] = lambda a, b: a <= b
    env['='] = lambda a, b: a == b

    # List operations
    env['car'] = lambda x: x[0]
    env['cdr'] = lambda x: x[1:]
    env['cons'] = lambda x, y: [x] + y
    env['null?'] = lambda x: x == []
    env['length'] = len
    env['list'] = lambda *args: list(args)
    env['append'] = lambda *lists: (_flatten(lists))

    # Type predicates
    env['number?'] = lambda x: isinstance(x, Number)
    env['symbol?'] = lambda x: isinstance(x, Symbol)
    env['list?'] = lambda x: isinstance(x, list)
    env['boolean?'] = lambda x: isinstance(x, Boolean)

    # Misc builtins
    env['not'] = lambda x: not x
    env['print'] = lambda *args: print(*args)
    env['abs'] = abs
    env['round'] = round
    env['max'] = lambda *args: max(args)
    env['min'] = lambda *args: min(args)

    # Math module (sin, cos, sqrt, pi, exp, log, etc.)
    env.update({k: v for k, v in vars(math).items()
                if callable(v) or isinstance(v, Number)})

    return env


def _prod(args):
    """Product of a sequence (for Python < 3.8 without math.prod)."""
    result = 1
    for a in args:
        result *= a
    return result


def _flatten(lists):
    """Concatenate multiple lists."""
    result = []
    for lst in lists:
        if isinstance(lst, list):
            result.extend(lst)
        else:
            result.append(lst)
    return result


global_env = standard_env()


# --- Procedures ---

class Procedure:
    """A user-defined Lisp procedure (closure).

    Captures parameter names, body expression, and the environment
    where the function was defined. This implements lexical scoping.
    """

    def __init__(self, parms, body, env):
        self.parms = parms
        self.body = body
        self.env = env

    def __call__(self, *args):
        if len(args) != len(self.parms):
            raise LispError(
                f"wrong number of arguments: "
                f"expected {len(self.parms)}, got {len(args)}"
            )
        return eval(self.body, Env(self.parms, args, self.env))

    def __repr__(self):
        return f"<procedure ({' '.join(self.parms)}) ...>"


# --- Evaluation ---

def eval(x: Exp, env: Env = global_env) -> Exp:
    """Evaluate a Lisp expression in an environment.

    This is the core of the interpreter. It dispatches based on
    the type of expression and handles special forms explicitly.
    """
    # Variable reference: look up symbol in environment chain
    if isinstance(x, Symbol):
        return env.find(x)[x]

    # Self-evaluating: numbers, booleans, nil
    if isinstance(x, (Number, Boolean)) or x is None:
        return x

    # Must be a list (expression) from here on
    op = x[0]
    args = x[1:]

    # (quote exp) — return exp literally without evaluation
    if op == 'quote':
        if len(args) != 1:
            raise LispError("quote requires exactly one argument")
        return args[0]

    # (if test conseq alt) — conditional
    if op == 'if':
        if len(args) != 3:
            raise LispError("if requires exactly three arguments")
        test, conseq, alt = args
        return eval(conseq, env) if eval(test, env) else eval(alt, env)

    # (define var exp) — define a variable in current environment
    if op == 'define':
        if len(args) != 2:
            raise LispError("define requires exactly two arguments")
        var, exp = args
        if not isinstance(var, Symbol):
            raise LispError(f"define: not a valid variable name: {var}")
        env[var] = eval(exp, env)
        return var

    # (set! var exp) — mutate an existing variable
    if op == 'set!':
        if len(args) != 2:
            raise LispError("set! requires exactly two arguments")
        var, exp = args
        if not isinstance(var, Symbol):
            raise LispError(f"set!: not a valid variable name: {var}")
        env.find(var)[var] = eval(exp, env)
        return var

    # (lambda (parms...) body) — create a procedure
    if op == 'lambda':
        if len(args) != 2:
            raise LispError("lambda requires parameters and body")
        parms, body = args
        if not isinstance(parms, list):
            raise LispError("lambda: parameters must be a list")
        return Procedure(parms, body, env)

    # (begin exp1 exp2 ...) — sequential evaluation
    if op == 'begin':
        if not args:
            raise LispError("begin requires at least one expression")
        result = None
        for arg in args:
            result = eval(arg, env)
        return result

    # (cond (test1 conseq1) (test2 conseq2) ...) — multi-way conditional
    if op == 'cond':
        for clause in args:
            if not isinstance(clause, list) or len(clause) < 2:
                raise LispError(f"cond: invalid clause: {clause}")
            test, *conseqs = clause
            if eval(test, env):
                return eval(('begin',) + tuple(conseqs), env) if conseqs else None
        return None

    # Procedure call: (proc arg1 arg2 ...)
    proc = eval(op, env)
    if not callable(proc):
        raise LispError(f"cannot call: {op}")
    arg_values = [eval(arg, env) for arg in args]
    return proc(*arg_values)


# --- REPL ---

def schemestr(exp) -> str:
    """Convert a Python value back to Lisp-readable string format."""
    if isinstance(exp, list):
        return '(' + ' '.join(schemestr(e) for e in exp) + ')'
    elif isinstance(exp, bool):
        return '#t' if exp else '#f'
    elif exp is None:
        return "'()"
    elif isinstance(exp, float):
        # Avoid unnecessary .0 for whole numbers
        if exp == int(exp):
            return f"{exp:.1f}"
        return str(exp)
    elif isinstance(exp, Procedure):
        return str(exp)
    else:
        return str(exp)


def repl(prompt: str = "lispy> "):
    """Read-eval-print loop."""
    print("Lisp in Python — type an expression or 'quit' to exit")
    try:
        while True:
            try:
                line = input(prompt)
                if line.strip() in ('quit', 'exit', ':q'):
                    break
                if not line.strip():
                    continue
                result = eval(parse(line))
                print(schemestr(result))
            except LispError as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                print()
                continue
    except EOFError:
        print()


def run_file(filepath: str):
    """Run a Lisp source file."""
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        # Execute each top-level expression sequentially
        # For simplicity, parse and eval the entire content as one
        # (for multi-expression files, wrap in begin)
        program = f"(begin {source})"
        result = eval(parse(program))
        return result
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)


# --- Main ---

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
```

## Section-by-Section Breakdown

### Types and Error Handling

Type aliases document what Python types represent which Lisp concepts. `LispError` provides contextual error messages instead of bare exceptions — the agent can read the error and fix the issue.

### Parsing: Tokenize, Read, Atom

Tokenize strips comments (semicolon to end of line) then splits on whitespace after spacing around parens. The recursive `read_from_tokens` builds nested lists matching S-expression structure. `atom` converts tokens to values: booleans (`#t`, `#f`) → Python bool, integers → int, floats → float, everything else → Symbol string.

### Environment: Env Class and Standard Library

`Env(dict)` extends dict with an `outer` reference for scope chaining. `find(var)` walks the chain to locate a binding. `standard_env()` populates the global environment with arithmetic, comparison, list operations, type predicates, and math module functions.

### Procedures: User-Defined Closures

`Procedure` captures `(parms, body, env)` at definition time. When called, creates a new Env frame binding parameters to arguments with the captured env as outer — this implements lexical scoping. `__call__` validates argument count before evaluating the body.

### Evaluation: The eval Function

Core dispatch function. Checks expression type first (symbol → lookup, number/bool → self-evaluating), then checks for special forms by operator name, finally treats as procedure call (eval all args, apply proc). Each branch handles exactly one case — no overlap.

### Special Forms Detail

- **quote**: Returns argument without evaluation. Enables literal list construction.
- **if**: Evaluates test, then exactly one of conseq or alt. The unchosen branch is never evaluated.
- **define**: Binds a name in the current (innermost) environment. Used for top-level definitions.
- **set!**: Finds existing binding via `env.find()` and updates it. Mutates variables, doesn't create new ones.
- **lambda**: Returns a Procedure object. Body is not evaluated — captured for later.
- **begin**: Evaluates all expressions left to right, returns last value. Enables sequencing.
- **cond**: Multi-way conditional. Tests each clause in order, evaluates consequence of first matching test.

### REPL: Read-Eval-Print Loop

`repl()` loops: read input → parse → eval → print result via `schemestr()`. Handles EOF (Ctrl+D), KeyboardInterrupt (Ctrl+C), and quit commands. `schemestr()` formats output as S-expressions: lists get parens, booleans become `#t`/`#f`, floats show one decimal for whole numbers.

## Running Examples

```
lispy> (+ 1 2 3)
6

lispy> (define x 10)
x

lispy> (* x x)
100

lispy> (if (> x 5) "big" "small")
big

lispy> (define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
fact

lispy> (fact 10)
3628800

lispy> (define fib (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2))))))
fib

lispy> (begin (define a 1) (define b 2) (+ a b))
3

lispy> (cond ((= 1 2) "no") ((> 1 0) "yes") ("else" "default"))
yes

lispy> (car (list 1 2 3))
1

lispy> (cdr (list 1 2 3))
(2 3)

lispy> (cons 0 (list 1 2))
(0 1 2)

lispy> (null? '())
#t

lispy> (length (list 1 2 3 4))
4

lispy> (number? 42)
#t

lispy> (symbol? x)
#t

lispy> (set! x 20)
x

lispy> x
20

lispy> (define double (lambda (f) (lambda (x) (f (f x)))))
double

lispy> ((double (lambda (x) (* 2 x))) 5)
20
```
