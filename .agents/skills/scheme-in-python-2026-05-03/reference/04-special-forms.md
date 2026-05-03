# Special Forms

## Contents
- Overview
- define
- lambda and mu
- if
- cond
- case
- let / let* / letrec
- quote / quasiquote
- begin
- and / or
- set!

## Overview

Special forms are syntactic constructs whose operands are **not** all evaluated before the form executes. They control evaluation order, create bindings, and enable non-standard control flow. Each special form handler receives unevaluated operand expressions and the current environment.

Registration pattern:

```python
SPECIAL_FORMS = {}

def special_form(name):
    def decorator(fn):
        SPECIAL_FORMS[name] = fn
        return fn
    return decorator
```

## define

Two syntaxes: variable definition and procedure definition (sugar for lambda).

```scheme
(define x 10)                    ; variable
(define (f a b) (+ a b))         ; procedure → (define f (lambda (a b) (+ a b)))
```

```python
@special_form("define")
def eval_define(expressions, env):
    target = expressions.first
    if isinstance(target, str):
        # (define name value)
        name = target
        value = eval_scheme(expressions.rest.first, env)
        env.bindings[name] = value
        return name
    elif is_pair(target):
        # (define (name args...) body...)
        name = target.first
        params = iter_rest(target.rest)
        body = expressions.rest  # remaining expressions are the body
        proc = LambdaProcedure(params, body, env)
        env.bindings[name] = proc
        return name
    else:
        raise SchemeError(f"Invalid define target: {scheme_repr(target)}")
```

## lambda and mu

Both create procedures but differ in scoping:

| Form | Scoping | Captures Env? |
|------|---------|--------------|
| `lambda` | Lexical | Yes — stores defining frame |
| `mu` | Dynamic | No — resolves at call time |

```python
@special_form("lambda")
def eval_lambda(expressions, env):
    params = expressions.first
    body = expressions.rest
    return LambdaProcedure(params, body, env)

@special_form("mu")
def eval_mu(expressions, env):
    params = expressions.first
    body = expressions.rest
    return MuProcedure(params, body)
```

**Parameter binding:** The `formals` list can include:
- Simple symbols: `(lambda (a b c) ...)`
- Dotted tail: `(lambda (a b . rest) ...)` — `rest` gets remaining args as a list
- Mutable parameters (advanced): `(lambda ((x . 0)) ...)` — local mutable binding with default

Handle dotted tail in `bind_formals`:

```python
def bind_formals(frame, formals, args):
    """Bind parameter names to argument values."""
    formal_list = to_python_list(formals)
    if len(formal_list) > len(args):
        raise SchemeError(f"Too few arguments for procedure")
    for i, formal in enumerate(formal_list):
        if isinstance(formal, str):
            frame.bindings[formal] = args[i]
        elif is_pair(formal) and formal.first == ".":
            # Mutable parameter with default — advanced, skip for basic impl
            frame.bindings[formal.first] = args[i]
    # Handle dotted tail parameter
    if is_pair(formals) and formals.rest is not nil:
        last = formals
        while last.rest is not nil and last.rest.rest is not nil:
            last = last.rest
        if is_pair(last.rest) and last.rest.first == ".":
            # Dotted tail: collect remaining args into a list
            tail_name = last.rest.rest.first
            remaining = args[len(formal_list) - 1:]
            frame.bindings[tail_name] = make_list(remaining)
```

## if

Evaluates predicate, then exactly one branch:

```scheme
(if predicate then-clause else-clause)
(if predicate then-clause)  ; else defaults to None
```

```python
@special_form("if")
def eval_if(expressions, env):
    pred = expressions.first
    then_expr = expressions.rest.first
    else_expr = (expressions.rest.rest.first
                 if expressions.rest.rest is not nil
                 else None)

    if is_true_value(eval_scheme(pred, env)):
        return eval_scheme(then_expr, env)
    elif else_expr is not None:
        return eval_scheme(else_expr, env)
    return None
```

Scheme truth: everything except `#f` is true. Zero, empty lists, and `None` are all true values.

## cond

Multi-way conditional with optional `else` clause:

```scheme
(cond
  ((= x 0) 'zero)
  ((< x 0) 'negative)
  (else 'positive))
```

```python
@special_form("cond")
def eval_cond(expressions, env):
    for clause in iter_rest(expressions):
        pred = clause.first
        if pred == "else":
            return eval_all(clause.rest, env)
        elif is_true_value(eval_scheme(pred, env)):
            # Body may have => shorthand for function application
            if clause.rest.first == "=>":
                receiver = eval_scheme(clause.rest.rest.first, env)
                return receiver(eval_scheme(pred, env))
            return eval_all(clause.rest, env)
    return None  # no clause matched
```

## case

Pattern matching on a single key:

```scheme
(case x
  ((a b c) 'vowel)
  ((d e f) 'consonant)
  (else 'other))
```

```python
@special_form("case")
def eval_case(expressions, env):
    key = eval_scheme(expressions.first, env)
    for clause in iter_rest(expressions):
        data_set = clause.first  # list of values to match
        if is_pair(data_set) or data_set == "else":
            data_list = to_python_list(data_set)
            if data_set == "else" or key in data_list:
                return eval_all(clause.rest, env)
    return None
```

## let / let* / letrec

Local binding constructs. See [Environments and Scoping](reference/03-environments-and-scoping.md) for frame creation details.

```scheme
(let ((x 1) (y 2)) (+ x y))       ; simultaneous binding
(let* ((x 1) (y (+ x 1))) (+ x y)) ; sequential (y sees x)
(letrec ((f (lambda (n) (if (= n 0) 1 (* n (f (- n 1))))))
         (g (lambda (n) (f (- n 1)))))
  (g 5))                           ; mutual recursion
```

Named `let` is syntactic sugar for a recursive procedure:

```scheme
(let loop ((i 0) (result '()))
  (if (> i 10) result
      (loop (+ i 1) (cons i result))))
```

Desugars to: `((lambda loop (i result) ...) 0 '())`

## quote / quasiquote

### quote

Returns its operand unevaluated:

```scheme
(quote (a b c))    ; → (a b c)
'(a b c)           ; shorthand, same result
'x                 ; → x (the symbol, not a variable lookup)
```

```python
@special_form("quote")
def eval_quote(expressions, env):
    return expressions.first  # return unevaluated
```

### quasiquote

Template-based quoting with selective evaluation via `,` (unquote) and `,@` (unquote-splicing):

```scheme
(let ((x 1) (y '(2 3)))
  `(a ,x b ,@y c))
; → (a 1 b 2 3 c)
```

```python
@special_form("quasiquote")
def eval_quasiquote(expressions, env):
    return quasiquote(expressions.first, env)

def quasiquote(expr, env):
    if not is_pair(expr):
        return expr
    if expr.first == "unquote":
        return eval_scheme(expr.rest.first, env)
    if expr.first == "unquote-splicing":
        raise SchemeError("unquote-splicing not in proper context")
    if expr.first == "quasiquote":
        return Pair("quasiquote", Pair(quasiquote(expr.rest.first, env), nil))
    # Recursively process the pair
    new_first = quasiquote(expr.first, env)
    new_rest = quasiquote(expr.rest, env)
    # Handle splicing: if rest contains unquote-splice result, flatten it
    if is_pair(expr.rest) and expr.rest.first == "unquote-splicing":
        spliced = eval_scheme(expr.rest.rest.first, env)
        return extend_list(new_first, spliced)
    return Pair(new_first, new_rest)
```

## begin

Sequences expressions, returns the last value:

```scheme
(begin
  (define x 1)
  (define y 2)
  (+ x y))
; → 3
```

```python
@special_form("begin")
def eval_begin(expressions, env):
    return eval_all(expressions, env)

def eval_all(expressions, env):
    """Evaluate a sequence of expressions, return last value."""
    result = None
    for expr in iter_rest(expressions):
        result = eval_scheme(expr, env)
    return result
```

## and / or

Short-circuit logical operators:

```scheme
(and #t #f (/ 1 0))  ; → #f (never divides by zero)
(or 5 2 (/ 1 0))     ; → 5 (first true value, rest skipped)
(and)                ; → #t (vacuously true)
(or)                 ; → #f (no true values found)
```

```python
@special_form("and")
def eval_and(expressions, env):
    result = True
    for expr in iter_rest(expressions):
        result = eval_scheme(expr, env)
        if result is False:
            return False
    return result

@special_form("or")
def eval_or(expressions, env):
    if expressions is nil:
        return False
    result = None
    for expr in iter_rest(expressions):
        result = eval_scheme(expr, env)
        if is_true_value(result):
            return result
    return result
```

## set!

Mutates an existing variable binding:

```scheme
(define x 10)
(set! x (+ x 5))
x  ; → 15
```

```python
@special_form("set!")
def eval_set_bang(expressions, env):
    name = expressions.first
    if not isinstance(name, str):
        raise SchemeError(f"set! target must be a symbol")
    value = eval_scheme(expressions.rest.first, env)
    set_variable_value(name, value, env)
    return None
```

`set!` searches the frame chain (unlike `define` which only modifies the current frame). The variable must already exist — `set!` cannot create new bindings.
