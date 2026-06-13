# Eval/Apply Loop

## Contents
- The Core Pattern
- Self-Evaluating Expressions
- Variable Lookup
- Special Form Dispatch
- Procedure Application
- Lambda vs Mu Procedures
- Tail-Call Optimization

## The Core Pattern

The eval/apply loop is the interpreter's heart. Two functions call each other recursively:

```python
def eval_scheme(expr, env):
    """Evaluate expr in environment env."""
    # 1. Self-evaluating
    if isinstance(expr, (int, float, bool, str)):
        if isinstance(expr, str) and expr.startswith('"'):
            return expr  # string literal
        return expr

    # 2. Quoted
    if is_pair(expr) and expr.first == "quote":
        return expr.rest.first

    # 3. Variable reference
    if isinstance(expr, str):
        return lookup_global(env, expr)

    # 4. Combination (list/call)
    if is_pair(expr):
        head = eval_scheme(expr.first, env)
        args = list(map(lambda e: eval_scheme(e, env), iter_rest(expr.rest)))

        # 5. Special form check BEFORE apply
        if isinstance(head, str) and head in SPECIAL_FORMS:
            return SPECIAL_FORMS[head](expr.rest, env)

        # 6. Apply the procedure
        return apply_scheme(head, args, env)

    raise SyntaxError(f"Invalid expression: {scheme_repr(expr)}")


def apply_scheme(proc, args, env):
    """Apply proc to evaluated args in env."""
    if isinstance(proc, BuiltinProcedure):
        return proc.apply(args)
    elif isinstance(proc, LambdaProcedure):
        child_env = make_child_frame(proc.formals, args, proc.env)
        return eval_all(body_of(proc.body), child_env)
    elif isinstance(proc, MuProcedure):
        child_env = make_child_frame(proc.formals, args, env)  # current env, not captured
        return eval_all(body_of(proc.body), child_env)
    else:
        raise SchemeError(f"Attempted to call non-callable: {scheme_repr(proc)}")
```

The critical insight: **special forms are detected by evaluating the operator position first**, checking if the result is a known special form name, then dispatching to custom logic that receives un-evaluated operands.

## Self-Evaluating Expressions

These types return themselves without lookup or computation:

| Type | Scheme Example | Python Representation |
|------|---------------|----------------------|
| Integer | `42` | `int` |
| Float | `3.14` | `float` |
| Boolean | `#t`, `#f` | `bool` |
| String | `"hello"` | `str` (with marker) |
| Nil | `'()` | `nil` singleton |

With Pair-based representation, distinguish string literals from symbols:

```python
class Str(str):
    """String literal — self-evaluating."""
    pass

# Reader produces Str("hello") for "hello" and "hello" (plain str) for symbol hello
def eval_scheme(expr, env):
    if isinstance(expr, (int, float, bool, Str)):
        return expr
```

## Variable Lookup

Walk the frame chain from innermost to global:

```python
def lookup_global(env, var):
    """Find var in env or its parents. Raise SchemeError if not found."""
    if not isinstance(var, str):
        raise SchemeError(f"Expected a symbol, got {scheme_repr(var)}")
    frame = env
    while frame is not None:
        if var in frame.bindings:
            return frame.bindings[var]
        frame = frame.parent
    raise SchemeError(f"{var} is not defined")
```

## Special Form Dispatch

Register special forms in a dictionary. Each handler receives the **unevaluated operand list** and the environment:

```python
SPECIAL_FORMS = {}

def special_form(name):
    """Decorator to register a special form handler."""
    def decorator(fn):
        SPECIAL_FORMS[name] = fn
        return fn
    return decorator

@special_form("if")
def eval_if(expressions, env):
    if expressions.first is nil:
        raise SchemeError("if requires at least a predicate")
    predicate = eval_scheme(expressions.first, env)
    branch = expressions.rest.first  # then clause
    else_clause = expressions.rest.rest.first if expressions.rest.rest is not nil else None

    if is_true_value(predicate):
        return eval_scheme(branch, env)
    elif else_clause is not None:
        return eval_scheme(else_clause, env)
    return None  # implicit false branch returns nothing
```

**Key rule:** Special form handlers decide which sub-expressions to evaluate and in what order. The eval/apply loop never pre-evaluates operands for special forms — the handler receives raw s-expressions.

## Procedure Application

Three procedure types exist:

### BuiltinProcedure

Python functions wrapped with argument validation:

```python
class BuiltinProcedure:
    def __init__(self, name, python_fn):
        self.name = name
        self.python_fn = python_fn

    def apply(self, args):
        return self.python_fn(*args)
```

### LambdaProcedure (Lexical Scope)

Captures the defining environment. Free variables resolve in the captured frame chain:

```python
class LambdaProcedure:
    def __init__(self, formals, body, env):
        self.formals = formals   # list of parameter names
        self.body = body         # expression(s) to evaluate
        self.env = env           # captured defining environment
```

When applied, creates a child frame whose parent is `self.env` (not the calling environment).

### MuProcedure (Dynamic Scope)

Resolves free variables in the **calling** environment. Used in SICP to contrast with lexical scoping:

```python
class MuProcedure:
    def __init__(self, formals, body):
        self.formals = formals
        self.body = body
        # No env captured — resolves at call time
```

When applied, creates a child frame whose parent is the **current** environment passed to `apply_scheme`.

## Tail-Call Optimization

Scheme requires tail-call optimization: recursive calls in tail position must not grow the stack. Two implementation strategies:

### Strategy A: Trampoline (SICP Approach)

Replace recursion with a while loop that processes "thunks" (unevaluated calls):

```python
def eval_all(expressions, env):
    """Evaluate a sequence of expressions, return last value. TCO-aware."""
    val = None
    for expr in iter_rest(expressions):
        val = eval_scheme(expr, env)
        while isinstance(val, Thunk):
            # Unwind tail call: re-eval with new expr and env
            expr, env = val.expr, val.env
            val = eval_scheme(expr, env)
    return val

class Thunk:
    """Represents a pending tail call."""
    def __init__(self, expr, env):
        self.expr = expr
        self.env = env
```

In `apply_scheme`, when the body is a single expression in tail position, return a `Thunk` instead of recursing into `eval_scheme`.

### Strategy B: System Recursion Limit

For educational interpreters where TCO is not required, rely on Python's recursion limit:

```python
import sys
sys.setrecursionlimit(10000)  # Allow deeper Scheme recursion
```

This works for most SICP exercises but fails on deeply tail-recursive programs (e.g., factorial of 10000).

**Recommendation:** Implement the trampoline pattern if following SICP closely. Otherwise, document the recursion limit and note that production interpreters use TCO or bytecode compilation.
