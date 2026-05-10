---
name: scheme-in-python-2026-05-03
description: Build a Scheme interpreter in Python covering tokenization, eval/apply loop, environment frames with lexical and dynamic scoping, special forms (define/lambda/if/let/cond), Pair-based linked lists, built-in procedures, and a REPL. Use when implementing a Scheme dialect in Python, teaching programming language concepts via SICP-style interpreters, or understanding how Lisp evaluates code as data.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - scheme
  - interpreter
  - lisp
  - python
  - eval-apply
  - sicp
category: language-runtime
external_references:
  - https://en.wikipedia.org/wiki/Scheme_(programming_language)
  - https://notebook.community/dsblank/ProgLangBook/Chapter%2005%20-%20Interpreting%20Scheme%20in%20Python
  - https://github.com/MathewMouchamel/Scheme-Interpreter-in-Python
  - https://codingwithtim.github.io/Scheme-Language-Interpreter/
  - https://github.com/CodingWithTim/Scheme-Language-Interpreter
---

# Scheme Interpreter in Python

## Overview

Scheme is a minimalist Lisp dialect founded on lambda calculus, lexical scoping, and homoiconicity (code is data). Building a Scheme interpreter in Python teaches the core mechanics of how programming languages work: tokenizing source text, parsing into nested structures, recursively evaluating expressions through an eval/apply loop, managing environment frames for variable binding, implementing special forms that control evaluation order, and wiring it all together in a read-eval-print loop.

This skill follows the SICP (Structure and Interpretation of Computer Programs) tradition where interpreters are built incrementally in pure Python with no external dependencies. The reference implementations from Berkeley CS61A and educational repositories provide the structural blueprint.

## When to Use

- Building a Scheme interpreter from scratch in Python for learning or coursework
- Understanding how programming language evaluation works (eval/apply, environments, closures)
- Implementing lexical vs dynamic scoping in an interpreter
- Adding special forms or built-in procedures to an existing interpreter
- Debugging interpreter behavior (scoping bugs, evaluation order, macro expansion)
- Teaching programming language concepts through hands-on implementation

## Core Concepts

### S-Expressions and Homoiconicity

Scheme source code consists of **s-expressions** — parenthesized prefix notation where the first element is the operator and remaining elements are operands:

```scheme
(+ 1 2)          ; arithmetic
(define x 10)    ; variable binding
(lambda (x y) (+ x y))  ; anonymous procedure
```

Because Scheme uses lists as both code and data structures, programs can manipulate their own source. This **homoiconicity** means the parser produces the same data structure used at runtime.

### The Eval/Apply Loop

Every interpreter reduces to two mutually recursive functions:

- **`eval(expr, env)`** — examines an expression and determines what to do:
  - Numbers/booleans return themselves (self-evaluating)
  - Symbols look up the value in the environment
  - Quoted expressions return their structure unevaluated
  - Special forms dispatch to custom handlers (if, define, lambda, etc.)
  - Everything else is a combination: eval the operator and operands, then apply

- **`apply(proc, args, env)`** — invokes a procedure with evaluated arguments:
  - Built-in procedures: call the underlying Python function
  - User-defined procedures: bind parameters to arguments in a new frame, eval the body

### Environments and Frames

An environment is a chain of **frames**, where each frame maps symbols to values and points to a parent frame. Variable lookup walks up the chain from the innermost frame outward:

```python
class Frame:
    def __init__(self, name, parent=None):
        self.name = name       # "global", "lambda", "let"
        self.parent = parent   # outer scope
        self.bindings = {}     # symbol -> value
```

**Lexical scoping** (lambda procedures) captures the defining environment at creation time. **Dynamic scoping** (mu procedures) resolves free variables in the calling environment at invocation time.

### Special Forms vs Procedures

Procedures evaluate all arguments before application. **Special forms** control evaluation order — some sub-expressions may never be evaluated:

| Form | Evaluates operands? |
|------|-------------------|
| `if` | Only the chosen branch |
| `define` | Only the value expression |
| `lambda` | Never (returns a procedure object) |
| `and`/`or` | Left-to-right, short-circuits |
| `let` | Only init expressions, not body until after binding |

## Usage Examples

### Minimal Working Interpreter (~80 lines)

This self-contained example handles arithmetic and variable definitions:

```python
# --- Tokenizer and Reader ---
def tokenize(text):
    """Split Scheme source into tokens."""
    return text.replace('(', ' ( ').replace(')', ' ) ').split()

def read(tokens):
    """Parse tokens into nested Python lists (s-expressions)."""
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    token = tokens.pop(0)
    if token == '(':
        exprs = []
        while tokens and tokens[0] != ')':
            exprs.append(read(tokens))
        if not tokens:
            raise SyntaxError("Unmatched parenthesis")
        tokens.pop(0)  # consume ')'
        return exprs
    elif token == ')':
        raise SyntaxError("Unexpected ')'")
    else:
        # Try numeric conversion
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return token  # symbol

# --- Environment ---
class Frame:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.bindings = {}

def make_global_frame():
    """Create global environment with arithmetic builtins."""
    frame = Frame("global")
    frame.bindings["+"] = lambda *args: sum(args)
    frame.bindings["-"] = lambda a, b=None: a - b if b is not None else -a
    frame.bindings["*"] = lambda *args: eval("*".join(map(str, args)))
    frame.bindings["/"] = lambda a, b: a / b
    return frame

# --- Evaluator ---
def eval_scheme(expr, env):
    """Evaluate a Scheme expression in the given environment."""
    # Self-evaluating: numbers
    if isinstance(expr, (int, float)):
        return expr
    # Quoted: return structure as-is
    if isinstance(expr, list) and expr and expr[0] == "quote":
        return expr[1]
    # Variable lookup
    if isinstance(expr, str):
        return lookup(env, expr)
    # Combination: (operator operand...)
    if isinstance(expr, list):
        op = eval_scheme(expr[0], env)
        args = [eval_scheme(arg, env) for arg in expr[1:]]
        return apply_scheme(op, args, env)
    raise TypeError(f"Cannot evaluate: {expr}")

def lookup(env, name):
    """Find a variable in the environment chain."""
    if name in env.bindings:
        return env.bindings[name]
    if env.parent is not None:
        return lookup(env.parent, name)
    raise NameError(f"Undefined variable: {name}")

def apply_scheme(proc, args, env):
    """Apply a procedure to arguments."""
    if callable(proc):
        return proc(*args)
    raise TypeError(f"Not a procedure: {proc}")

# --- define special form ---
def eval_define(expr, env):
    """Handle (define name value) and (define (name args...) body)."""
    if isinstance(expr[1], str):
        # (define x expr)
        name = expr[1]
        value = eval_scheme(expr[2], env)
        env.bindings[name] = value
        return name
    elif isinstance(expr[1], list):
        # (define (f x y) body) -> sugar for (define f (lambda (x y) body))
        params = expr[1][1:]
        body = expr[2]
        proc = make_lambda(params, body, env)
        env.bindings[expr[1][0]] = proc
        return expr[1][0]

def make_lambda(params, body, env):
    """Create a user-defined procedure (closure)."""
    def proc(*args):
        new_frame = Frame("lambda", env)
        for param, arg in zip(params, args):
            new_frame.bindings[param] = arg
        return eval_scheme(body, new_frame)
    return proc

# --- REPL ---
global_env = make_global_frame()

print("scm> ", end="")
while True:
    try:
        line = input()
        tokens = tokenize(line)
        expr = read(tokens)
        if isinstance(expr, list) and expr[0] == "define":
            result = eval_define(expr, global_env)
        else:
            result = eval_scheme(expr, global_env)
        print(result)
    except (EOFError, KeyboardInterrupt):
        break
    except Exception as e:
        print(f"Error: {e}")
    print("scm> ", end="")
```

**Run it:** `python3 scheme_minimal.py`

```
scm> (+ 1 2)
3
scm> (define x 10)
x
scm> (* x 3)
30
```

## Advanced Topics

**Tokenizer and Reader**: Tokenization rules, reader implementation, Pair-based linked lists, handling quoted expressions and dotted pairs → [Tokenizer and Reader](reference/01-tokenizer-and-reader.md)

**Eval/Apply Loop**: Recursive evaluation architecture, self-evaluating expressions, procedure application dispatch, tail-call optimization patterns → [Eval/Apply Loop](reference/02-eval-apply-loop.md)

**Environments and Scoping**: Frame chains, lexical vs dynamic scoping, closure creation, MuProc for SICP-style dynamic scope → [Environments and Scoping](reference/03-environments-and-scoping.md)

**Special Forms**: define, lambda/mu, if/cond/case, let/let*/letrec, quote/quasiquote, begin/and/or, set! → [Special Forms](reference/04-special-forms.md)

**Builtins and Pair**: Cons-cell linked lists, arithmetic operations, predicates, higher-order functions (map/filter/fold), I/O procedures, registration patterns → [Builtins and Pair](reference/05-builtins-and-pair.md)

**REPL and Error Handling**: Multi-line input, pretty-printing Scheme values, error classification and reporting, session management → [REPL and Error Handling](reference/06-repl-and-error-handling.md)
