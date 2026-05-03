# Interpreter Architecture

## Contents
- The Eval-Apply Cycle
- Type System
- Parsing Pipeline
- Environment Model
- Procedure Model
- Special Forms vs Procedures

## The Eval-Apply Cycle

Every Lisp interpreter revolves around two operations: **eval** (evaluate an expression) and **apply** (call a procedure with arguments). Together they form the eval-apply cycle.

**Eval** takes a Lisp expression and an environment, returns a value:
- If the expression is an atom (number, symbol), return it directly or look it up
- If it's a list, check if it's a special form (quote, if, define, etc.)
- Otherwise, eval the first element to get a procedure, eval all remaining elements to get arguments, then **apply** the procedure

**Apply** takes a procedure and a list of argument values:
- If it's a built-in Python callable, call it with `proc(*args)`
- If it's a user-defined Procedure, create a new environment binding parameters to arguments, then eval the body in that environment

This cycle is recursive — eval calls apply, and apply calls eval. The recursion terminates when expressions reduce to atomic values (numbers, booleans).

## Type System

The interpreter maps Python types to Lisp values:

- **Symbol** = `str` — variable names, operators, keywords (`x`, `+`, `lambda`)
- **Number** = `(int, float)` — numeric literals
- **List** = `list` — parenthesized expressions `(a b c)`, data lists
- **Boolean** = `bool` — `True` represents `#t`, `False` represents `#f`
- **Nil** = `None` — the empty list `'()` or false value in some Lisps
- **String** = `str` with quote markers — `"hello"` (distinguished from symbols at parse time)

Python's type system handles the mapping naturally. The interpreter uses `isinstance()` checks in eval to dispatch on expression type.

## Parsing Pipeline

Parsing converts a string of characters into nested Python lists (the AST). Three stages:

**Tokenize**: Split input into tokens by adding spaces around parentheses, then calling `.split()`. This produces `['(', '+', '1', '2', ')']` from `"(+ 1 2)"`. Alternative: regex `r"[()]|[^() \n]+"` which handles whitespace more cleanly and supports comments.

**Read from tokens**: Recursive descent parser. Pop first token:
- If `(`, build a list by recursively reading sub-expressions until `)`
- If `)`, syntax error (unexpected close paren)
- Otherwise, convert to atom: try int → float → symbol

**Atom conversion**: Try `int(token)`, then `float(token)`, fallback to treating it as a Symbol string. This handles `42` → `42`, `3.14` → `3.14`, `foo` → `'foo'`.

The result is a nested Python list that mirrors the S-expression structure: `['+', 1, ['*', 2, 3]]` for `(+ 1 (* 2 3))`.

## Environment Model

An environment maps variable names to values. The key insight from Norvig's approach: environments form a chain for lexical scoping.

```python
class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        return self if (var in self) else self.outer.find(var)
```

Env extends dict, so all standard dict operations work. The `outer` reference creates a scope chain. When looking up a variable:
1. Check current environment
2. If not found, check outer environment
3. Repeat until found or no outer remains (error)

The global environment is created once with built-in procedures pre-loaded. Local environments are created when calling user-defined functions, binding parameters to arguments and pointing `outer` to the function's captured environment.

## Procedure Model

User-defined procedures are closures: they capture the environment where they were defined.

```python
class Procedure:
    def __init__(self, parms, body, env):
        self.parms = parms  # parameter names (list of symbols)
        self.body = body    # expression to evaluate
        self.env = env      # captured environment

    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))
```

When a `(lambda (x y) (+ x y))` is evaluated, it returns a Procedure with `parms=['x', 'y']`, `body=['+', 'x', 'y']`, and `env` pointing to the current environment. When called with arguments, a new Env frame is created binding `'x'` and `'y'` to the argument values, with the captured env as outer. This implements lexical scoping.

Built-in procedures are just Python callables (functions, lambdas) stored directly in the environment. The eval function checks `callable()` to distinguish between user-defined Procedure objects and built-ins.

## Special Forms vs Procedures

Special forms are expressions where arguments are **not** all evaluated before the form executes. This distinguishes them from regular procedure calls.

- **quote**: Returns its argument literally without evaluation. `(quote (+ 1 2))` → `['+', 1, 2]`, not `3`.
- **if**: Evaluates only one of two branches based on the test condition. The unchosen branch is never evaluated (enabling conditional logic).
- **define**: Evaluates only the value expression, then binds it to a variable name. The variable name itself is not evaluated.
- **set!**: Like define but for existing variables. Finds the variable in the scope chain and updates it.
- **lambda**: Returns a Procedure object without evaluating the body. The body is captured for later evaluation when the function is called.
- **begin**: Evaluates all arguments sequentially, returns the last value (for grouping expressions).
- **cond**: Multi-way conditional. Evaluates test clauses until one succeeds, then evaluates the corresponding consequence.

Regular procedure calls evaluate **all** arguments first, then apply the procedure to the resulting values. This is called "applicative-order" evaluation and is the default in Scheme.
