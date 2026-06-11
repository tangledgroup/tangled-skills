"""Scheme interpreter in Python.

Supports: ; comments, + - * / < > <= >= =, if, cond, and, or, not,
define, lambda, quote, let, set!, begin, cons, car, cdr, list, null?,
eq?, equal?

Scheme semantics (R5RS): only #f is false, everything else is true.
Lists use cons-cell representation (pair nodes), not Python lists.
"""

import operator as op


# ---------------------------------------------------------------------------
# Cons Cell (pair)
# ---------------------------------------------------------------------------

class SchemeString:
    """Wrapper to distinguish Scheme string values from symbol names."""

    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, SchemeString):
            return self.value == other.value
        return False

    def __repr__(self):
        return f'"{self.value}"'


class Pair:
    """A Scheme cons cell (pair). car -> first, cdr -> second."""

    __slots__ = ('car', 'cdr')

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __eq__(self, other):
        if not isinstance(other, Pair):
            return False
        return self.car == other.car and self.cdr == other.cdr

    def __repr__(self):
        return scheme_repr(self)


# Empty list singleton
NIL = object()  # internal sentinel for '()


def is_proper_list(obj):
    """Check if obj is a proper list (chain of Pairs ending at NIL)."""
    seen = set()
    while obj is not NIL:
        if not isinstance(obj, Pair):
            return False
        if id(obj) in seen:  # cycle detection
            return False
        seen.add(id(obj))
        obj = obj.cdr
    return True


def list_to_pair(*items):
    """Build a proper Scheme list from Python items."""
    result = NIL
    for item in reversed(items):
        result = Pair(item, result)
    return result


def pair_to_list(pair_obj):
    """Convert a proper Scheme list to a Python list. Raises on improper."""
    if pair_obj is NIL:
        return []
    if not isinstance(pair_obj, Pair):
        raise TypeError("expected a list")
    result = []
    seen = set()
    current = pair_obj
    while current is not NIL:
        if not isinstance(current, Pair):
            raise TypeError("improper list")
        if id(current) in seen:
            raise TypeError("circular list")
        seen.add(id(current))
        result.append(current.car)
        current = current.cdr
    return result


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def strip_comments(text: str) -> str:
    """Remove ; comments from Scheme source, respecting string literals."""
    result = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n:
                if text[j] == '\\' and j + 1 < n:
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            result.append(text[i:j])
            i = j
        elif c == ';':
            while i < n and text[i] != '\n':
                i += 1
        else:
            result.append(c)
            i += 1
    return ''.join(result)


def tokenize(text: str) -> list:
    """Tokenize Scheme source into a flat list of string tokens."""
    text = strip_comments(text)
    text = text.replace('(', ' ( ').replace(')', ' ) ').replace("'", " ' ")
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        if text[i].isspace():
            i += 1
            continue
        if text[i] == '"':
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
    """Parse token list into nested Python lists (AST)."""
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
    """Convert a token string to int, float, bool, or symbol (str)."""
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
        return tok  # keep quotes for eval-time handling
    return tok


# ---------------------------------------------------------------------------
# Symbol Table (lexical scoping)
# ---------------------------------------------------------------------------

class Env(dict):
    """Environment: dict with outer reference for lexical scoping."""

    def __init__(self, params=(), args=(), outer=None):
        super().__init__()
        self.outer = outer
        for p, a in zip(params, args):
            self[p] = a

    def find(self, var):
        if var in self:
            return self[var]
        if self.outer is not None:
            return self.outer.find(var)
        raise NameError(f"unbound variable: {var}")


# ---------------------------------------------------------------------------
# Built-in operators
# ---------------------------------------------------------------------------

def _sub_variadic(args):
    """Handle - with 1 or more args: (- x) = -x, (- a b ...) = a - b - ..."""
    if len(args) == 0:
        raise TypeError("-: expects at least 1 argument")
    if len(args) == 1:
        return -args[0]
    result = args[0]
    for a in args[1:]:
        result = op.sub(result, a)
    return result


def _mul_variadic(args):
    """Handle * with 0 or more args: (*) = 1, (* a b ...) = a * b * ..."""
    if not args:
        return 1
    result = args[0]
    for a in args[1:]:
        result = op.mul(result, a)
    return result


def _div_variadic(args):
    """Handle / with 1 or more args: (/ x) = 1/x, (/ a b ...) = a / b / ..."""
    if len(args) == 0:
        raise TypeError("/: expects at least 1 argument")
    if len(args) == 1:
        return op.truediv(1, args[0])
    result = args[0]
    for a in args[1:]:
        result = op.truediv(result, a)
    return result


BUILTINS = {
    '+':  lambda *args: sum(args, 0),
    '-':  lambda *args: (_sub_variadic(args)),
    '*':  lambda *args: (_mul_variadic(args)),
    '/':  lambda *args: (_div_variadic(args)),
    '<':  op.lt,
    '>':  op.gt,
    '<=': op.le,
    '>=': op.ge,
    '=':  op.eq,
    'modulo': op.mod,
    'remainder': op.mod,

    # List operations
    'cons': lambda a, b: Pair(a, b),
    'car':  lambda p: p.car if isinstance(p, Pair) else (_ for _ in ()).throw(TypeError("car: expects a pair")),
    'cdr':  lambda p: p.cdr if isinstance(p, Pair) else (_ for _ in ()).throw(TypeError("cdr: expects a pair")),
    'null?': lambda x: x is NIL,
    'list?': lambda x: is_proper_list(x),
    'pair?': lambda x: isinstance(x, Pair),

    # List construction
    'list': lambda *args: (_build_list(args)),

    # Predicates
    'eq?':    lambda a, b: a is b if isinstance(a, (str, bool)) else a == b,
    'equal?': lambda a, b: _deep_eq(a, b),
    'symbol?': lambda x: isinstance(x, str) and not x.startswith('"'),
    'number?': lambda x: isinstance(x, (int, float)),
    'boolean?': lambda x: isinstance(x, bool),
    'procedure?': lambda x: callable(x) or (isinstance(x, tuple) and x[0] == 'closure'),
    'string?': lambda x: isinstance(x, SchemeString),

    # Boolean
    'not': lambda x: x is False,  # Scheme: (not #f) = #t, (not anything-else) = #f

    # I/O (no-op for testing)
    'display':  lambda x: x,
    'newline':  lambda: None,
}


def _build_list(args):
    """Build a proper Scheme list from args."""
    result = NIL
    for item in reversed(args):
        result = Pair(item, result)
    return result


def _deep_eq(a, b) -> bool:
    """Structural equality for Scheme values including pairs."""
    if type(a) is not type(b):
        # Special case: int == float comparison
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a == b
        return False
    if isinstance(a, Pair):
        return _deep_eq(a.car, b.car) and _deep_eq(a.cdr, b.cdr)
    if isinstance(a, SchemeString):
        return a.value == b.value
    if a is NIL and b is NIL:
        return True
    return a == b


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def is_true(val) -> bool:
    """In Scheme, only #f (Python False) is false."""
    return val is not False


def eval_expr(expr, env):
    """Evaluate a single Scheme expression in environment env."""

    # Closure tuple -> self-evaluating
    if isinstance(expr, tuple):
        return expr

    # NIL -> self-evaluating (empty list)
    if expr is NIL:
        return NIL

    # Numbers and booleans -> self-evaluating
    if isinstance(expr, (int, float, bool)):
        return expr

    # Symbol -> lookup in environment
    if isinstance(expr, str):
        if expr.startswith('"') and expr.endswith('"'):
            return SchemeString(expr[1:-1])  # wrap string literal
        return env.find(expr)

    # List -> special form or procedure call
    if not isinstance(expr, list):
        raise TypeError(f"unexpected type: {type(expr)}")
    if not expr:
        raise SyntaxError("empty expression ()")

    head = expr[0]

    # --- Special forms ---

    if head == 'quote':
        return data_quote(expr[1])

    if head == 'if':
        if len(expr) < 3 or len(expr) > 4:
            raise SyntaxError(f"if: expected 2-3 arguments, got {len(expr) - 1}")
        if is_true(eval_expr(expr[1], env)):
            return eval_expr(expr[2], env)
        if len(expr) == 4:
            return eval_expr(expr[3], env)
        return None

    if head == 'cond':
        for clause in expr[1:]:
            if not isinstance(clause, list) or len(clause) < 2:
                raise SyntaxError(f"cond: invalid clause {clause}")
            test = clause[0]
            if test == 'else':
                # else clause: evaluate remaining body expressions
                result = None
                for body_expr in clause[1:]:
                    result = eval_expr(body_expr, env)
                return result
            if is_true(eval_expr(test, env)):
                result = None
                for body_expr in clause[1:]:
                    result = eval_expr(body_expr, env)
                return result
        return None

    if head == 'and':
        result = True
        for arg in expr[1:]:
            result = eval_expr(arg, env)
            if result is False:
                return False
        return result

    if head == 'or':
        result = False
        for arg in expr[1:]:
            result = eval_expr(arg, env)
            if is_true(result):
                return result
        return result

    if head == 'begin':
        result = None
        for body_expr in expr[1:]:
            result = eval_expr(body_expr, env)
        return result

    if head == 'let':
        if len(expr) < 3:
            raise SyntaxError("let: expected bindings and body")
        bindings = expr[1]
        body = expr[2:]
        # Evaluate init values in current env, bind in new env
        new_env = Env(outer=env)
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) < 2:
                raise SyntaxError(f"let: invalid binding {binding}")
            var = binding[0]
            init_val = eval_expr(binding[1], env)
            new_env[var] = init_val
        result = None
        for body_expr in body:
            result = eval_expr(body_expr, new_env)
        return result

    if head == 'set!':
        if len(expr) != 3:
            raise SyntaxError("set!: expected variable and value")
        var = expr[1]
        val = eval_expr(expr[2], env)
        # Walk up environment chain to find mutable binding
        current = env
        while current is not None:
            if var in current:
                current[var] = val
                return val
            current = current.outer
        raise NameError(f"set!: unbound variable: {var}")

    if head == 'define':
        target = expr[1]
        if isinstance(target, list):
            # Procedure definition: (define (f x y) body...)
            name = target[0]
            params = target[1:]
            body = expr[2:]
            closure = ('closure', params, body, env)
            env[name] = closure
            return None
        else:
            # Variable definition: (define x value)
            val = eval_expr(expr[2], env)
            env[target] = val
            return None

    if head == 'lambda':
        if len(expr) < 3:
            raise SyntaxError("lambda: expected parameters and body")
        params = expr[1]
        body = expr[2:]
        return ('closure', params, body, env)

    # --- Procedure call ---

    proc = eval_expr(head, env)
    args = [eval_expr(a, env) for a in expr[1:]]

    if isinstance(proc, tuple) and proc[0] == 'closure':
        _, params, body, closure_env = proc
        frame = Env(params, args, outer=closure_env)
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
        items = [data_quote(e) for e in expr]
        # Build as proper list (cons cells)
        result = NIL
        for item in reversed(items):
            result = Pair(item, result)
        return result
    return expr


# ---------------------------------------------------------------------------
# Printer
# ---------------------------------------------------------------------------

def scheme_repr(val) -> str:
    """Format a Python value as Scheme notation."""
    if val is None:
        return ''  # void result
    if val is NIL:
        return '()'
    if isinstance(val, bool):
        return '#t' if val else '#f'
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        if val == int(val):
            return f"{val:.1f}"
        return str(val)
    if isinstance(val, SchemeString):
        return f'"{val.value}"'
    if isinstance(val, str):
        # Bare symbol — display without quotes
        if val.startswith('#<procedure:'):
            return val
        return val
    if isinstance(val, Pair):
        # Build representation walking the pair chain
        parts = []
        current = val
        while isinstance(current, Pair):
            parts.append(scheme_repr(current.car))
            current = current.cdr
        if current is NIL:
            # Proper list: (a b c)
            return '(' + ' '.join(parts) + ')'
        else:
            # Improper/dotted: (a b . rest)
            if not parts:
                return f"(. {scheme_repr(current)})"
            return '(' + ' '.join(parts) + ' . ' + scheme_repr(current) + ')'
    if isinstance(val, tuple) and val[0] == 'closure':
        return '#<procedure>'
    return str(val)


# ---------------------------------------------------------------------------
# Convenience: run a Scheme expression string
# ---------------------------------------------------------------------------

def make_global_env():
    """Create the global environment with builtins."""
    env = Env(outer=None)
    for name, func in BUILTINS.items():
        env[name] = func
    return env


def scheme_eval(source: str, env=None):
    """Evaluate a Scheme source string and return the result."""
    if env is None:
        env = make_global_env()
    tokens = tokenize(source)
    if not tokens:
        return None
    exprs = parse(tokens)
    result = None
    for expr in exprs:
        result = eval_expr(expr, env)
    return result


def scheme_eval_repr(source: str, env=None):
    """Evaluate a Scheme source string and return its repr."""
    result = scheme_eval(source, env)
    return scheme_repr(result)


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def repl():
    """Simple Scheme REPL."""
    global_env = make_global_env()
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
            prompt = "    "
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