# Control Flow & Functions

## Contents
- Assignment and mutation
- Conditionals
- Loops
- Comprehensions
- Function definitions
- Context managers
- Pattern matching
- Exception handling
- Miscellaneous

## Assignment and Mutation

**`setv`**: Variable assignment, returns `None`. Supports multiple pairs:

```hy
(setv x 1 y 2)           ; x=1, y=2
(setv [x y] [y x])       ; swap
(setv [a #* rest b] items) ; extended unpacking
(setv :chain [x y z] 0)  ; chained assignment (Hy 1.2+)
```

**`setx`**: Assignment expression (PEP 572), returns assigned value:

```hy
(when (> (setx x (+ 1 2)) 0)
  (print x "is greater than 0"))
```

**`let`**: Block-level scoping with mangled names. Bindings evaluated sequentially (like `let*`):

```hy
(let [x 5 y (+ x 1)]
  (print x y))  ; => 5 6
```

Note: let-bound variables persist in Python scope (not GC'd immediately). Use `del` at end or wrap in function.

**`global` / `nonlocal`**: Scope declarations compiling to Python statements.

**`del`**: Delete variables/attributes/subscripts. Returns `None`.

**Annotations** (`annotate` / `#^`): Type hints and standalone annotations:

```hy
(setv #^ int x 1)
(defn func [#^ int a #^ str [b None] #^ int [c 1]] ...)
(defn #^ int add1 [#^ int x] (+ x 1))
```

**`deftype`**: Type aliases (Python 3.12+):

```hy
(deftype IntOrStr (| int str))
(deftype :tp [T] ListOrSet (| (get list T) (get set T)))
```

## Conditionals

**`if`**: `(if CONDITION THEN ELSE)` — returns value of evaluated branch.

**`when`**: Shorthand for `(if CONDITION (do BODY...) None)`.

**`cond`**: Multi-way branching (nested `if`):

```hy
(cond
  (> x 50) (print "too big")
  (< x 10) (print "too small")
  True     (print "just right"))
```

Returns `None` if no condition matches. Use `True` as final condition for default.

## Loops

**`while`**: Condition + body forms. Returns `None`. Supports `else` clause:

```hy
(setv x 3)
(while (> x 0)
  (print x)
  (setv x (- x 1))
  (else (print "done")))
```

**`for`**: Iteration with clauses in square brackets. Returns `None`:

```hy
(for [x [1 2 3] :if (!= x 2) y [7 8]]
  (print x y))

; Async for:
(for [:async x (async-iter)] (print x))
```

Supports `:if`, `:do`, `:setv` clauses and `(else ...)` form.

**`break` / `continue`**: Apply to innermost iteration clause in multi-clause loops.

## Comprehensions

All share clause syntax: iteration (`VAR ITERABLE`), `:if COND`, `:do FORM`, `:setv VAR VAL`, `:async VAR ITERABLE`. Variables from clauses are not visible outside (except in `for`).

```hy
(lfor x (range 5) (* 2 x))           ; list → [0 2 4 6 8]
(sfor x (range 5) x)                 ; set
(dfor x (range 5) x (* x 10))        ; dict — two trailing args are key/value
(gfor x (count) :if (< x 5) x)       ; generator expression
```

## Function Definitions

**`defn`**: Named function definition:

```hy
(defn name [params]
  "docstring"   ; first string literal becomes docstring
  body...)
```

Optional modifiers before name (in order): `:async`, `[decorators]`, `:tp [type-params]`, `#^ return-annotation`.

**Lambda list features:**
- `/` — preceding params positional-only
- `*` — following params keyword-only
- `[name default]` — optional parameter
- `#* args` — varargs (tuple)
- `#** kwargs` — keyword args (dict)

```hy
(defn f [a / b [c 3] * d e #** kwargs] [a b c d e kwargs])
(f 1 2 :d 4 :e 5 :f 6)  ; => [1 2 3 4 5 {"f" 6}]
```

**`fn`**: Anonymous function (same body semantics as `defn`, no decorators/type params).

**`return`**: Exit function early. Last form is implicitly returned (except in async generators).

**`yield` / `yield :from`**: Generator support:

```hy
(defn myrange []
  (setv r (range 10))
  (while True
    (yield :from r)))
```

**`await`**: Await expression for coroutines.

## Context Managers

**`with`**: One or more context managers in bracket list:

```hy
(with [o (open "file.txt" "rt")]
  (print (.read o)))

; Multiple managers:
(with [v1 e1 v2 e2] ...)  ; → with e1 as v1, e2 as v2: ...

; Async context manager:
(with [:async v1 e1] ...)

; Anonymous (use _):
(with [_ (open "f")] ...)  ; with open("f"): ...
```

Returns value of last body form (unlike Python where `with` is statement-only).

## Pattern Matching

**`match`**: Python 3.10+ structural pattern matching:

```hy
(match subject
  pattern1 result1
  pattern2 :if guard result2
  _ default-result)
```

Patterns: literals, captures (`x`), values (`VAR`), sequences (`[a b c]`), mappings, classes `(Point 1 x)`, OR `(| p1 p2)`, AS `PATTERN :as NAME`.

## Exception Handling

**`try`**: Body forms + `except`/`except*` clauses + optional `else`/`finally`:

```hy
(try
  (risky-operation)
  (except [ZeroDivisionError]
    (print "div by zero"))
  (except [e ValueError]
    (print "ValueError:" (repr e)))
  (else (print "no errors"))
  (finally (print "done")))
```

Exception list formats: `[]` (any Exception), `[ETYPE]`, `[[E1 E2]]` (tuple), `[VAR ETYPE]`, `[VAR [E1 E2]]`.

**`raise`**: `(raise EXCEPTION)` or `(raise EX1 :from EX2)`. No args = reraise.

**`assert`**: `(assert CONDITION [MESSAGE])`.

## Miscellaneous

**`chainc`**: Heterogeneous comparison chains: `(chainc x <= y < z)`.

**`do`**: Evaluate multiple forms, return last. Essential for multi-form bodies in `if`, `cond`, etc.
