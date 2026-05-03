# Environments and Scoping

## Contents
- Frame Structure
- Global Frame Initialization
- Variable Binding and Lookup
- Lexical Scoping (LambdaProcedure)
- Dynamic Scoping (MuProcedure)
- Closures
- let / let* / letrec as Environment Builders

## Frame Structure

A frame is a named scope containing symbol-to-value bindings and a reference to an outer (parent) frame:

```python
class Frame:
    """An environment frame mapping symbols to values."""
    _root = None  # The global frame singleton

    def __init__(self, name, parent=None):
        self.name = name          # "global", "lambda", "let"
        self.parent = parent      # outer scope (None for global)
        self.bindings = {}        # symbol -> value

    def __repr__(self):
        return f"<Frame {self.name} bindings={list(self.bindings.keys())}>"
```

Frames form a singly-linked list. The root frame has `parent=None`. All other frames chain back to it.

### Frame Creation Pattern

When entering a new scope (procedure call, let binding), create a child frame:

```python
def make_child_frame(formals, args, parent):
    """Create a new frame binding formals to args, with given parent."""
    frame = Frame("child", parent)
    bind_formals(frame, formals, args)
    return frame
```

## Global Frame Initialization

The global frame is created once at interpreter startup and populated with built-in procedures:

```python
def create_global_frame():
    """Create and populate the global environment."""
    if Frame._root is not None:
        return Frame._root
    global_frame = Frame("global")
    Frame._root = global_frame

    # Register all built-in procedures
    for name, fn in BUILTIN_PROCS.items():
        global_frame.bindings[name] = BuiltinProcedure(name, fn)

    # Special forms are NOT stored in the frame — they are handled
    # by the eval/apply loop's SPECIAL_FORMS dictionary

    return global_frame
```

Built-in procedure registration:

```python
BUILTIN_PROCS = {
    "+": lambda *args: sum(args),
    "-": lambda a, b=None: a - b if b is not None else -a,
    "*": lambda *args: math.prod(args) if args else 1,
    "/": lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ZeroDivisionError()),
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "=": lambda a, b: a == b,
    "boolean?": lambda x: isinstance(x, bool),
    "number?": lambda x: isinstance(x, (int, float)),
    "symbol?": lambda x: isinstance(x, str),
    "pair?": lambda x: isinstance(x, Pair),
    "null?": lambda x: x is nil,
    "procedure?": lambda x: isinstance(x, (BuiltinProcedure, LambdaProcedure, MuProcedure)),
    "cons": lambda a, b: Pair(a, b),
    "car": lambda p: p.first if isinstance(p, Pair) else (_ for _ in ()).throw(TypeError()),
    "cdr": lambda p: p.rest if isinstance(p, Pair) else (_ for _ in ()).throw(TypeError()),
}
```

## Variable Binding and Lookup

### Defining a Variable

`define` adds or updates a binding in the current frame:

```python
def define_variable(name, value, env):
    """Bind name to value in the current (innermost) frame."""
    env.bindings[name] = value
```

### Setting a Variable

`set!` updates an existing binding, searching outward:

```python
def set_variable_value(name, value, env):
    """Update name's binding. Must already exist somewhere in the chain."""
    if name in env.bindings:
        env.bindings[name] = value
    elif env.parent is not None:
        set_variable_value(name, value, env.parent)
    else:
        raise SchemeError(f"{name} is not defined")
```

### Looking Up a Variable

Walk the chain from current frame to root:

```python
def lookup_global(env, var):
    if not isinstance(var, str):
        raise SchemeError(f"Expected symbol, got {scheme_repr(var)}")
    frame = env
    while frame is not None:
        if var in frame.bindings:
            return frame.bindings[var]
        frame = frame.parent
    raise SchemeError(f"{var} is not defined")
```

## Lexical Scoping (LambdaProcedure)

A lambda procedure captures its **defining environment**. When called, the new frame's parent is the captured environment, not the calling environment:

```python
class LambdaProcedure:
    def __init__(self, formals, body, env):
        self.formals = formals
        self.body = body
        self.env = env  # captured at definition time

# In apply_scheme:
elif isinstance(proc, LambdaProcedure):
    child_env = make_child_frame(proc.formals, args, proc.env)  # ← proc.env
    return eval_all(body_of(proc.body), child_env)
```

**Example:** Closure captures `x` from defining scope:

```scheme
(define (make-adder x)
  (lambda (y) (+ x y)))

(define add5 (make-adder 5))
((add5 3))  ; → 8. x=5 is resolved in make-adder's frame, not caller's
```

Frame chain for `(+ x y)` inside the lambda:
```
lambda frame (y=3) → make-adder frame (x=5) → global frame
```

## Dynamic Scoping (MuProcedure)

A mu procedure does **not** capture an environment. Free variables resolve in the **calling** environment:

```python
class MuProcedure:
    def __init__(self, formals, body):
        self.formals = formals
        self.body = body
        # No env — resolved dynamically at call time

# In apply_scheme:
elif isinstance(proc, MuProcedure):
    child_env = make_child_frame(proc.formals, args, env)  # ← current env
    return eval_all(body_of(proc.body), child_env)
```

**Example:** Dynamic scope resolves `a` and `b` from caller:

```scheme
(define (f) (* a b))
(define g (mu () (f)))
(define a 4)
(define b 5)
(g)  ; → 20. a and b found in global frame at call time
```

Without dynamic scoping, `f` would fail because `a` and `b` are not in its defining scope.

## Closures

A closure is a procedure + captured environment. Lambda procedures in Scheme are closures by default:

```python
# Creating a closure
(define (make-counter start)
  (lambda ()
    (set! start (+ start 1))
    start))

(let ((counter (make-counter 0)))
  (list (counter) (counter) (counter)))
; → (1 2 3) — each call sees updated start in captured frame
```

The closure captures the `make-counter` frame where `start` is bound. Each invocation of the lambda creates a new child frame whose parent is that captured frame, so `set!` modifies the binding in the captured scope.

### Multiple Closures Sharing Environment

```scheme
(define (make-pair-of-counters start)
  (values
   (lambda () (set! start (+ start 1)) start)
   (lambda () (set! start (- start 1)) start)))
```

Both lambdas capture the same frame, so they share the mutable `start` variable.

## let / let* / letrec as Environment Builders

These forms create local frames by desugaring to procedure calls:

| Form | Desugars To | Frame Parent |
|------|------------|-------------|
| `(let ((x 1)) body)` | `((lambda (x) body) 1)` | Current env |
| `(let* ((x 1) (y x)) body)` | Nested lets | Each binding sees previous |
| `(letrec ((f (lambda ...))) body)` | Define-then-body in new frame | Bindings mutually visible |

Implementation of `let`:

```python
@special_form("let")
def eval_let(expressions, env):
    bindings = expressions.first  # ((var1 val1) (var2 val2) ...)
    body = expressions.rest       # body expressions

    # Create new frame
    new_frame = Frame("let", env)
    # Evaluate all init values in the OUTER frame (simultaneous binding)
    for binding in iter_rest(bindings):
        var = binding.first
        val = eval_scheme(binding.rest.first, env)  # ← env, not new_frame
        new_frame.bindings[var] = val

    return eval_all(body, new_frame)
```

Implementation of `let*` (sequential binding):

```python
@special_form("let*")
def eval_let_star(expressions, env):
    bindings = expressions.first
    body = expressions.rest

    frame = Frame("let*", env)
    for binding in iter_rest(bindings):
        var = binding.first
        val = eval_scheme(binding.rest.first, frame)  # ← frame (sees previous bindings)
        frame.bindings[var] = var
    return eval_all(body, frame)
```

Implementation of `letrec` (mutual recursion):

```python
@special_form("letrec")
def eval_letrec(expressions, env):
    bindings = expressions.first
    body = expressions.rest

    frame = Frame("letrec", env)
    # First pass: bind variables to placeholder (unassigned)
    for binding in iter_rest(bindings):
        frame.bindings[binding.first] = None  # or a sentinel
    # Second pass: evaluate init values (can reference other letrec vars)
    for binding in iter_rest(bindings):
        frame.bindings[binding.first] = eval_scheme(binding.rest.first, frame)

    return eval_all(body, frame)
```
