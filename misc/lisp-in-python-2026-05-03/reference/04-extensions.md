# Extensions

## Contents
- Tail-Call Optimization
- call/cc (Continuations)
- Macros
- Strings and Characters
- Derived Special Forms
- Additional Builtins
- Syntax Sugar

## Tail-Call Optimization

Tail-call optimization (TCO) eliminates stack growth for recursive calls in tail position. A call is in tail position when its result is directly returned — no further computation follows.

**Why it matters**: Without TCO, `(fact 10000)` causes Python's recursion limit error. With TCO, it runs with constant stack space.

**Approach: Trampoline pattern**. Instead of eval calling apply which calls eval recursively, restructure so that when a tail call is detected, return a "thunk" (a marker saying "call this procedure with these args"). The trampoline loop catches thunks and continues without adding stack frames.

Key changes to the interpreter:

1. Rename `eval` to `eval_core` — it returns either a value or a TailCall thunk
2. Create a `TailCall(proc, args)` class as the marker
3. In procedure call evaluation, detect tail position and return TailCall instead of recursing
4. Wrap everything in a trampoline loop that processes TailCall thunks iteratively

```python
class TailCall:
    def __init__(self, proc, args):
        self.proc = proc
        self.args = args

def trampoline(f, *args):
    result = f(*args)
    while isinstance(result, TailCall):
        result = result.proc(*result.args)
    return result

# In eval_core, the procedure call case becomes:
# Instead of: return proc(*arg_values)
# Use:        return TailCall(proc, arg_values)
```

For full TCO (not just top-level), the apply function needs to be separated from eval, and the tail-call detection needs to happen in apply. This is more involved but enables optimization anywhere in the call chain.

**Reference**: Norvig's lispy2 implements this pattern. See his article "An ((Even Better) Lisp) Interpreter (in Python)".

## call/cc (Continuations)

`call-with-current-continuation` captures the current execution context as a first-class value. Calling the captured continuation jumps back to that point, abandoning everything done since.

**Simplified version (catch/throw)**: Misfra.me implements this as `catch!` / `throw`, behaving like try/catch:

```
(catch! (lambda (throw)
  (+ 5 (* 10 (catch! (lambda (escape) (* 100 (throw 3)))))))
)
; Returns 3 — throw escapes both catch! frames
```

**Implementation**: Use Python exceptions as continuations. When `catch!` is evaluated, create a custom exception class. The `throw` function raises this exception with the value. The catch! handler catches it and returns the value.

```python
class Continuation(Exception):
    def __init__(self, value):
        self.value = value

# In eval for 'catch!':
try:
    throw_fn = Procedure(['v'], raise_continuation, Env())
    return eval(body, Env(['throw'], [throw_fn], env))
except Continuation as e:
    return e.value
```

**Full call/cc**: Requires capturing the entire continuation stack. In Python, this means wrapping eval in a try/except that catches a special exception and re-invokes eval with a different expression. Much more complex — requires restructuring the entire eval-apply cycle.

## Macros

Macros transform code before evaluation. Unlike functions (which operate on values), macros operate on expressions (the raw S-expressions before evaluation).

**define-macro**: Define a macro by name. When the macro name appears as an operator, expand it before evaluating arguments.

```python
# Add to environment:
global_env['macros'] = {}

# In eval, before procedure call:
if op in env.get('macros', {}):
    macro_fn = env['macros'][op]
    expanded = macro_fn(*args)  # args are unevaluated expressions
    return eval(expanded, env)

# Special form for defining macros:
if op == 'define-macro':
    (_, name, parms, body) = x
    env['macros'][name] = Procedure(parms, body, env)
```

**Example macro — `when`**:

```lisp
(define-macro when
  (lambda (test . body)
    `(if ,test (begin ,@body))))

(when (> 10 5)
  (print "yes")
  (define result "big"))
```

The macro receives unevaluated arguments and returns a new expression that eval processes. This enables defining new syntax without modifying the interpreter.

**Quasiquote**: Needed for practical macros. Allows template construction with selective evaluation:

- `` ` `` (quasiquote): Like quote, but allows escapes
- `,` (unquote): Evaluate this sub-expression within a quasiquote
- `,@` (unquote-splice): Evaluate and splice list into parent

Implementation: Walk the quoted tree, evaluate any unquoted sub-expressions, splice where `,@` appears.

## Strings and Characters

**String tokens**: Extend the tokenizer to handle double-quoted strings as single tokens:

```python
def tokenize(chars):
    result = []
    i = 0
    while i < len(chars):
        c = chars[i]
        if c == '(':
            result.append('(')
        elif c == ')':
            result.append(')')
        elif c == '"':
            # Read until closing quote
            j = i + 1
            while j < len(chars) and chars[j] != '"':
                j += 1
            result.append(chars[i:j+1])  # include quotes
            i = j
        elif not c.isspace():
            j = i
            while j < len(chars) and not chars[j].isspace() and chars[j] not in '()':
                j += 1
            result.append(chars[i:j])
        i += 1
    return result
```

**String type**: Create a `LispString` class (or use a tuple `('str', value)` marker) to distinguish from symbols. Add string builtins: `string?`, `string-length`, `string-append`, `string->symbol`, `symbol->string`.

**Character literals**: `#\space`, `#\a` → single-character strings.

## Derived Special Forms

Derived forms can be implemented as macros or as direct eval clauses:

**let**: Syntactic sugar for immediate lambda application.

```lisp
; (let ((x 1) (y 2)) (+ x y))
; Expands to:
; ((lambda (x y) (+ x y)) 1 2)
```

Direct eval implementation:

```python
if op == 'let':
    bindings, *body = args
    new_env = Env(outer=env)
    for (var, exp) in bindings:
        new_env[var] = eval(exp, env)  # eval in outer env
    return eval(('begin',) + tuple(body), new_env)
```

**let\***: Like let but each binding can reference previous ones (sequential evaluation).

**letrec**: Like let but bindings can reference each other (mutual recursion). Pre-bind variables to None, then fill in.

**when / unless**: Conditional with multiple consequence expressions.

```python
if op == 'when':
    test, *body = args
    if eval(test, env):
        return eval(('begin',) + tuple(body), env)
    return None

if op == 'unless':
    test, *body = args
    if not eval(test, env):
        return eval(('begin',) + tuple(body), env)
    return None
```

**do**: Loop construct with initialization, test, step, and body.

```lisp
(do ((i 0 (+ i 1))
     (sum 0 (+ sum i)))
    ((>= i 10) sum)
  ;; body — side effects here if needed
)
```

## Additional Builtins

**I/O operations**:
- `read`: Parse and return next expression from input
- `load`: Read and evaluate a file
- `display` / `write`: Output values with different formatting

**More math**:
- `modulo`, `remainder`, `quotient`
- `even?`, `odd?`
- `expt` (power), `sqrt`, `log`, `exp`, `sin`, `cos`, `tan`

**List operations**:
- `reverse`, `member`, `assoc`
- `map`, `filter`, `reduce` (fold)
- `list-ref`, `list-set!`

**Association lists**:
- `assoc`: Lookup key in list of (key . value) pairs
- `assq`: Like assoc but uses identity comparison

**Random**:
- `random`: Return random number
- `seed!`: Set random seed

## Syntax Sugar

**Reader macros**: Extend the parser to handle shorthand syntax:

- `'expr` → `(quote expr)` — single quote for quoting
- `` `expr `` → `(quasiquote expr)` — backtick for template quoting
- `,expr` → `(unquote expr)` — comma for escape
- `,@expr` → `(unquote-splice expr)` — comma-at for splicing

**Implementation**: Pre-process tokens before parsing, or handle in `read_from_tokens`:

```python
def read_from_tokens(tokens):
    if not tokens:
        raise LispError("unexpected EOF")

    token = tokens.pop(0)

    if token == "'":
        # 'expr → (quote expr)
        return ['quote', read_from_tokens(tokens)]

    # ... rest of parser
```

**Dot notation for pairs**: `(a . b)` represents a cons cell (not a list). Extend the parser to handle `.` in lists:

```python
# In read_from_tokens, inside the '(' case:
if tokens[0] == '.':
    tokens.pop(0)  # consume '.'
    car_part = lst
    cdr_part = read_from_tokens(tokens)
    # Return as a pair marker: ('pair', car_part, cdr_part)
```

This enables proper dotted-pair notation: `(1 . (2 . (3 . ())))` equivalent to `(1 2 3)`.
