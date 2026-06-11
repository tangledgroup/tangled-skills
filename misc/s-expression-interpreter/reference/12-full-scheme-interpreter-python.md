# Full Scheme Interpreter in Python with Cons-Cell Lists

## Contents
- Design Goals
- Scheme Comment Semantics
- Complete Implementation (script reference)
- Running the Interpreter
- Cons Cell Representation
- Tokenizer (with comment stripping)
- Parser (recursive descent)
- Evaluator (eval-apply cycle)
- Environment and Closures
- Special Forms
- Built-in Operators
- Printer (Scheme notation)
- REPL
- Test Cases
- Limitations

## Design Goals

A self-contained Scheme interpreter in ~660 lines of Python with no external dependencies. Targets **R5RS Scheme** semantics: only `#f` is false, `(define (f x) body)` syntax for procedures, `lambda` for anonymous functions, `;` line comments, and proper cons-cell list representation.

Builds on the lwcarani pattern (tokenize→parse→eval with Env scoping) but adds:
- **Cons-cell lists** (`Pair` class with `car`/`cdr`) instead of Python lists
- **Full special forms**: `if`, `cond`, `and`, `or`, `let`, `set!`, `begin`, `quote`, `define`, `lambda`
- **List operations**: `cons`, `car`, `cdr`, `list`, `null?`, `pair?`, `list?`
- **Predicates**: `eq?`, `equal?`, `symbol?`, `number?`, `boolean?`, `string?`, `procedure?`
- **Variadic arithmetic**: `+`, `-`, `*`, `/` accept any number of arguments
- **String support**: `SchemeString` wrapper distinguishes string values from symbols
- **100 passing tests** covering all features

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

The full implementation is stored as a script for deterministic execution. Paths are relative to this skill's directory.

**Script (Execute)**: `scripts/full_scheme_interpreter.py` — the complete Scheme interpreter (~660 lines).

**Run as REPL:**
```bash
python3 scripts/full_scheme_interpreter.py
```

**Programmatic API:**
```python
from full_scheme_interpreter import scheme_eval_repr, scheme_eval, make_global_env, NIL, Pair

# Evaluate and get string representation
result = scheme_eval_repr("(+ 1 2)")
print(result)  # "3"

# Evaluate and get raw Python value
env = make_global_env()
value = scheme_eval("(cons 1 (cons 2 '()))", env)
print(value)  # Pair(1, Pair(2, NIL))
```

**Run tests:**
```bash
python3 scripts/test_full_scheme_interpreter.py
# Results: 100 passed, 0 failed, 100 total
```

## Cons Cell Representation

Lists are represented as chains of `Pair` objects (cons cells), not Python lists. Each `Pair` has a `car` (first element) and `cdr` (rest). The empty list `'()` is represented by the `NIL` singleton.

```
(1 2 3)  →  Pair(1, Pair(2, Pair(3, NIL)))
(1 . 2)  →  Pair(1, 2)
(1 2 . 3) → Pair(1, Pair(2, 3))
```

**`is_proper_list(obj)`**: Walks the chain checking each node is a `Pair`, with cycle detection via `id()` tracking. Returns `True` only if the chain ends at `NIL`.

**`pair_to_list(pair_obj)`**: Converts a proper list to a Python list. Raises `TypeError` on improper lists or cycles.

**`list_to_pair(*items)` / `_build_list(args)`**: Constructs proper lists from Python iterables by building pairs in reverse order.

**`SchemeString` wrapper**: Distinguishes Scheme string values (from `"hello"` literals) from symbol names (bare identifiers). Both are conceptually strings in Scheme, but symbols display without quotes and strings display with quotes. The wrapper enables `string?` predicate and correct `scheme_repr` output.

## Tokenizer (with comment stripping)

Two-stage process:

**Stage 1 — `strip_comments()`**: Character-by-character scan that removes `;`-to-end-of-line comments while preserving string literals. When it encounters `"`, it consumes the entire string (handling `\\` and `\"` escapes) and appends it verbatim. When it encounters `;` outside a string, it skips to the next `\n`.

**Stage 2 — `tokenize()`**: After comment stripping, pads `(`, `)`, and `'` with whitespace, then uses a manual tokenizer that keeps quoted strings as single tokens. The `'` padding ensures `'hello` tokenizes as `[''', 'hello']` (not `["'hello"]`), enabling the quote abbreviation to work for bare symbols.

```scheme
(+ 1 2) ; add one and two
```
→ `['(', '+', '1', '2', ')']`

```scheme
'hello
```
→ `["'", 'hello']` → parsed as `['quote', 'hello']`

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

**Quote abbreviation**: `'`(a b c)` → `['quote', ['a', 'b', 'c']]`. Also works for bare symbols: `'hello` → `['quote', 'hello']`.

## Evaluator (eval-apply cycle)

`eval_expr(expr, env)` dispatches on the type of `expr`:

| Type | Action |
| --- | --- |
| `int`, `float`, `bool` | Self-evaluating, return as-is |
| `tuple` (closure) | Already a procedure value, return as-is |
| `NIL` | Self-evaluating (empty list) |
| `str` (symbol) | Lookup in environment via `env.find()` |
| `str` (string literal) | Strip quotes, wrap in `SchemeString` |
| `list` | Special form or procedure call |

**Special forms** (non-strict evaluation):
- `quote`: Convert AST to cons-cell data structure
- `if`: Evaluate predicate, then exactly one branch
- `cond`: Multi-way conditional with `else` clause support
- `and`: Left-to-right short-circuit, returns first false or last value
- `or`: Left-to-right short-circuit, returns first true or last value
- `begin`: Sequence expressions, return last result
- `let`: Create new environment, evaluate bindings in outer env, evaluate body in new env
- `set!`: Mutate variable by walking up environment chain
- `define`: Bind variable or define procedure (stores closure)
- `lambda`: Create and return a closure tuple

**Procedure call**: Evaluate operator and all arguments, then apply. If the operator is a user-defined closure, create a new Env frame binding params to args with the closure's captured environment as outer scope. If it's a built-in Python callable, invoke directly.

## Environment and Closures

`Env` extends `dict` with an `outer` reference forming a chain of frames. Variable lookup walks from innermost frame outward via `find()`.

Closures are stored as tuples: `('closure', params, body, env)`. The `env` is the environment at definition time — this captures variables for closure behavior. When the closure is called, a new frame is created with `outer=closure_env`, enabling lexical scoping.

**Note**: In Scheme, `set!` mutates bindings in the environment chain. If a closure captures a variable and that variable is later mutated via `set!`, the closure sees the updated value (shared mutable environment). This differs from some languages where closures capture values by copy.

## Special Forms

### `if`
```scheme
(if <test> <consequent>)
(if <test> <consequent> <alternative>)
```
Only `<test>` is always evaluated. Exactly one of the branches is evaluated based on the test result. If test is false and no alternative exists, returns `None` (unspecified in Scheme).

### `cond`
```scheme
(cond (<test1> <body1> ...)
      (<test2> <body2> ...)
      (else <fallback> ...))
```
Evaluates each test in order. When a test is true, evaluates all body expressions and returns the last result. `else` clause always matches. Returns `None` if no clause matches.

### `and` / `or`
```scheme
(and <e1> <e2> ...)  ; short-circuit: returns first false or last value
(or <e1> <e2> ...)   ; short-circuit: returns first true or last value
```
Both short-circuit — `and` stops at first false, `or` stops at first true.

### `let`
```scheme
(let ((x 1) (y 2))
  (+ x y))
```
Evaluates all binding init values in the current environment, creates a new environment with the bindings, then evaluates the body expressions in the new environment. All init values share the same outer scope (not `let*` sequential binding).

### `set!`
```scheme
(set! x (+ x 1))
```
Walks up the environment chain to find the variable's binding and mutates it in place. Returns the new value. Raises `NameError` if the variable is unbound.

### `begin`
```scheme
(begin (display "hello") (newline) 42)
```
Evaluates each expression in order, returns the last result. Used for sequencing side effects.

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
(quote (a b c))   ; → (a b c) as cons-cell data, not evaluated
'(a b c)          ; same
'hello            ; → symbol hello
```
Prevents evaluation, returning the literal structure. Lists are converted to cons-cell representation via `data_quote()`.

## Built-in Operators

**Arithmetic (variadic)**: `+`, `-`, `*`, `/` accept any number of arguments.
- `(+ 1 2 3)` → 6, `(- 10)` → -10, `(- 10 3 2)` → 5, `(/ 10)` → 0.1

**Comparisons (binary)**: `<`, `>`, `<=`, `>=`, `=`

**List operations**: `cons`, `car`, `cdr`, `list`, `null?`, `pair?`, `list?`

**Predicates**: `eq?` (identity for symbols/booleans, equality for others), `equal?` (deep structural equality including pairs and strings), `symbol?`, `number?`, `boolean?`, `string?`, `procedure?`

**Arithmetic extras**: `modulo`, `remainder`

**Boolean**: `not` — `(not #f)` → `#t`, `(not x)` → `#f` for any truthy x

**I/O**: `display`, `newline` (no-op in test mode, functional in REPL)

## Printer (Scheme notation)

`scheme_repr(val)` converts Python values back to Scheme-readable strings:

| Python | Scheme |
| --- | --- |
| `None` | `` (void, no output) |
| `NIL` | `()` |
| `True` / `False` | `#t` / `#f` |
| `42` | `42` |
| `3.0` | `3.0` |
| `SchemeString("hi")` | `"hi"` |
| `'hello'` (symbol) | `hello` |
| `Pair(1, NIL)` | `(1)` |
| `Pair(1, 2)` | `(1 . 2)` |
| `Pair(1, Pair(2, 3))` | `(1 2 . 3)` |

Proper lists (chains ending at `NIL`) display as `(a b c)`. Improper lists (chains ending at non-NIL) display with dotted notation: `(a b . rest)`.

## REPL

The REPL accumulates input lines until parentheses are balanced, then tokenizes, parses, and evaluates all top-level expressions. Continuation prompt (`    `) indicates multi-line input. Error messages are printed for any exception during evaluation.

**Multi-line support**: Counts `(` vs `)` in comment-stripped text. If unbalanced (more open than close), continues accumulating with continuation prompt.

## Test Cases

All 100 tests pass, organized by feature:

### Arithmetic (9 tests)
| Expression | Result |
| --- | --- |
| `(+ 1 2)` | `3` |
| `(+ 1 2 3 4)` | `10` |
| `(- 10 3)` | `7` |
| `(- 5)` | `-5` |
| `(* 3 4)` | `12` |
| `(/ 10 2)` | `5.0` |
| `(+ (* 3 5) (- 10 6))` | `19` |
| `(/ 7 2)` | `3.5` |

### Comparisons (7 tests)
| Expression | Result |
| --- | --- |
| `(< 1 2)` | `#t` |
| `(> 3 2)` | `#t` |
| `(= 5 5)` | `#t` |
| `(= 5 6)` | `#f` |
| `(<= 3 3)` | `#t` |
| `(>= 3 3)` | `#t` |
| `(<= 4 3)` | `#f` |

### Booleans (5 tests)
| Expression | Result |
| --- | --- |
| `#t` | `#t` |
| `#f` | `#f` |
| `(if 0 'yes 'no)` | `yes` (0 is truthy) |
| `(not #t)` | `#f` |
| `(not #f)` | `#t` |

### If (6 tests)
| Expression | Result |
| --- | --- |
| `(if #t 1 2)` | `1` |
| `(if #f 1 2)` | `2` |
| `(if #t 42)` | `42` (no alternative) |
| `(if (< 1 2) 'yes 'no)` | `yes` |
| `(abs -3)` where `abs` uses `if` | `3` |

### Cond (4 tests)
| Expression | Result |
| --- | --- |
| `(cond ((< 1 2) 'a) ((< 3 4) 'b))` | `a` (first match) |
| `(cond ((< 2 1) 'a) ((< 3 4) 'b))` | `b` (second match) |
| `(cond ((< 2 1) 'a) (else 'default))` | `default` |
| `(cond ((< 1 2) (+ 1 2) (+ 3 4)))` | `7` (multi-body, last result) |

### And/Or/Not (6 tests)
| Expression | Result |
| --- | --- |
| `(and #t #t)` | `#t` |
| `(and #t #f)` | `#f` |
| `(or #f #t)` | `#t` |
| `(or #f #f)` | `#f` |
| `(and #f (/ 1 0))` | `#f` (short-circuit, no div-by-zero) |
| `(or #t (/ 1 0))` | `#t` (short-circuit) |

### Define (3 tests)
| Expression | Result |
| --- | --- |
| `(define x 42)` then `x` | `42` |
| `(define pi 3.14)` then `(* pi 2)` | `6.28` |
| Rebind: `(define x 1) (define x 2) x` | `2` |

### Procedures (6 tests)
| Expression | Result |
| --- | --- |
| `(square 21)` where `(define (square x) (* x x))` | `441` |
| `(average 1 3)` | `2.0` |
| `(add (add 21 21) 42)` | `84` |
| `((lambda (x) (* x x)) 5)` | `25` |
| `((lambda (a b) (+ a b)) 3 4)` | `7` |

### Recursion (3 tests)
| Expression | Result |
| --- | --- |
| `(fact 5)` | `120` |
| `(fact 10)` | `3628800` |
| `(fib 9)` | `34` |

### Closures (4 tests)
| Expression | Result |
| --- | --- |
| `(add3 4)` where `add3 = (make-adder 3)` | `7` |
| `((make-adder 4) 5)` | `9` |
| `(scale 3)` with `multiplier = 10` | `30` |
| `(scale 3)` after rebind `multiplier = 20` | `60` (sees updated binding) |

### Let (5 tests)
| Expression | Result |
| --- | --- |
| `(let ((x 10)) (+ x 5))` | `15` |
| `(let ((x 3) (y 4)) (+ x y))` | `7` |
| Shadow: outer `x=1`, `(let ((x 10)) x)` | `10` |
| After let shadow, outer `x` still | `1` |
| Multi-body: `(let ((x 3)) (+ x 1) (+ x 2))` | `5` |

### Set! (3 tests)
| Expression | Result |
| --- | --- |
| `(set! x 2)` then `x` | `2` |
| Counter first call: `(counter)` | `0` |
| Counter second call: `(counter)` again | `1` |

### Begin (2 tests)
| Expression | Result |
| --- | --- |
| `(begin 1 2 3)` | `3` |
| `(begin (define x 10) (define y 20) (+ x y))` | `30` |

### Quote (6 tests)
| Expression | Result |
| --- | --- |
| `(quote (a b c))` | `(a b c)` |
| `'(a b c)` | `(a b c)` |
| `'hello` | `hello` |
| `'42` | `42` |
| `'(a (b c) d)` | `(a (b c) d)` |
| `'()` | `()` |

### Pairs (4 tests)
| Expression | Result |
| --- | --- |
| `(cons 1 2)` | `(1 . 2)` |
| `(car x)` where `x = (cons 1 2)` | `1` |
| `(cdr x)` where `x = (cons 1 2)` | `2` |
| `(cons 1 (cons 2 (cons 3 4)))` | `(1 2 3 . 4)` |

### Lists (11 tests)
| Expression | Result |
| --- | --- |
| `(cons 1 (cons 2 (cons 3 '())))` | `(1 2 3)` |
| `(list 1 2 3 4)` | `(1 2 3 4)` |
| `(null? '())` | `#t` |
| `(null? '(1))` | `#f` |
| `(car (list 1 2 3))` | `1` |
| `(cdr (list 1 2 3))` | `(2 3)` |
| `(cons 10 (list 1 2 3))` | `(10 1 2 3)` |
| `(pair? (cons 1 2))` | `#t` |
| `(pair? '())` | `#f` |
| `(list? (list 1 2))` | `#t` |
| `(list? (cons 1 2))` | `#f` |

### Predicates (7 tests)
| Expression | Result |
| --- | --- |
| `(eq? 'a 'a)` | `#t` |
| `(eq? 'a 'b)` | `#f` |
| `(equal? '(1 2) '(1 2))` | `#t` |
| `(equal? (cons 1 2) (cons 1 2))` | `#t` |
| `(number? 42)` | `#t` |
| `(symbol? 'foo)` | `#t` |
| `(boolean? #t)` | `#t` |

### Higher-Order (2 tests)
| Expression | Result |
| --- | --- |
| `(map1 (lambda (x) (+ x 1)) '(1 2 3))` | `(2 3 4)` |
| `(filter even? '(1 2 3 4))` | `(2 4)` |

### Comments (3 tests)
| Expression | Result |
| --- | --- |
| `(+ 1 2) ; add` | `3` |
| `"hello ; world"` | `"hello ; world"` |
| `; comment\n(+ 3 4)` | `7` |

### Integration (2 tests)
| Expression | Result |
| --- | --- |
| Circle area: `(circle-area 5)` with `pi = 3.14159` | `78.53975` |
| `((compose (lambda (x) (+ x 1)) (lambda (x) (* 3 x))) 5)` | `16` |

## Limitations

- **No block comments** (`#|...|#`) — requires multi-line stateful parsing
- **No `let*`/`letrec`** — only basic `let` with simultaneous binding
- **No variadic parameters** (dotted lambda lists like `(lambda (x . rest) ...)`)
- **No `apply`/`map` as builtins** — must be defined in Scheme (test shows user-defined `map1`)
- **No tail-call optimization** — deep recursion limited by Python stack
- **No `case`/`do`/`delay`/`force`** — additional special forms not included
- **No numeric tower** — all numbers are `int` or `float`, no bignums/ratios
- **No error recovery** — any evaluation error stops processing
- **No `vector`/`hash-table`** — only list data structures
- **`car`/`cdr` on non-pairs** use generator-expression trick for error raising (works but unconventional)
