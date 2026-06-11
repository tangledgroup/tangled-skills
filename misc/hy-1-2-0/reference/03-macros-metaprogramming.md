# Macros & Metaprogramming

## Contents
- Regular macros
- Quasiquoting
- Reader macros
- Macro scoping and namespaces
- Compile-time evaluation
- Macro pitfalls
- Best practices

## Regular Macros

Macros are functions called at compile-time that return code to be executed at run-time. Defined with `defmacro`:

```hy
(defmacro do-while [condition #* body]
  `(do
     ~@body
     (while ~condition
       ~@body)))
```

Macros receive **models** as arguments (not evaluated values). They return models or anything convertible via `hy.as-model`.

**Parameter list**: `symbol`, `[symbol default]`, `/`, `#* args` allowed. No `#** kwargs` or `*` — keywords are passed as literal keyword objects.

Macros from other modules use `require` (not `import`), since macros expand at compile-time:

```hy
(require mymodule)          ; full module
(require mymodule [foo])    ; specific macro
(require mymodule *)        ; all exported macros
(require mymodule :as M)    ; aliased
```

Reader macros are in a separate namespace, require explicit `:readers`:

```hy
(require mymodule :readers [spiff])
(require mymodule :macros [foo] :readers [spiff])
```

## Quasiquoting

**`quasiquote`** (`` ` ``): Like `quote` but treats the form as a template with evaluation holes.

**`unquote`** (`~`): Evaluate and substitute a value into the template.

**`unquote-splice`** (`~@`): Splice an iterable into the parent sequence.

```hy
(setv x 2)
`(setv foo ~x)        ; => '(setv foo 2)
`(a b ~X c d ~@X e)   ; X=[1 2 3] => '[a b [1 2 3] c d 1 2 3 e]
```

`~@None` treated as empty list. `~` and `@` need whitespace if referring to symbol starting with `@`: `~ @foo`.

## Reader Macros

Reader macros hook into the parser to customize how text is parsed. Defined with `defreader`:

```hy
(defreader hi
  '(print "Hello."))
#hi  ; prints "Hello." at parse-time
```

Access to `&reader` (a `hy.HyReader` object) for parsing subsequent source:

```hy
(defreader do-twice
  (setv x (.parse-one-form &reader))
  `(do ~x ~x))
#do-twice (print "twice")
```

**Key `&reader` methods:**
- `.parse-one-form()` — parse one form from source
- `.getc()` / `.peekc()` — consume/peek single character
- `.slurp-space()` — consume whitespace
- `.read-ident()` — read identifier characters
- `.peek-and-getc TARGET` — peek and consume if matches
- `.saving-chars()` — context manager to save consumed chars
- `.end-identifier CHAR` — temporarily add char to end-of-ident set

Reader macros are evaluated at parse-time. Can't use a reader macro in the same top-level form that defines it.

## Macro Scoping and Namespaces

Three scopes for regular macros:

1. **Core macros**: Built-in, available everywhere (e.g., `if`, `setv`, `defn`). Inspectable via `builtins._hy_macros`.

2. **Global macros**: Module-level, stored in `_hy_macros` dict per module. Defined by `defmacro` or `require` at module scope.

3. **Local macros**: Function/class/comprehension scope. Viewed via `(local-macros)`. Beware: local macro definitions apply to results of expanding other macros in context — may not be as local as expected.

**Reader macros**: Module-level only (like global regular macros), stored in `_hy_reader_macros` (keys not mangled). No core or local reader macros.

Macros don't share namespaces with Python objects: `(defmacro m []) (print m)` → `NameError`.

## Compile-Time Evaluation

**`eval-when-compile`**: Execute at compile-time only, contribute nothing to final program:

```hy
(eval-when-compile
  (defn helper [x] (+ x 1)))
; helper available to macros but not at runtime
```

**`eval-and-compile`**: Execute at both compile-time and run-time. Same code, potentially different scoping:

```hy
(eval-and-compile
  (defn add [x y] (+ x y)))
(defmacro m [x] (add x 2))  ; macro can call add
(print (add 3 6))            ; runtime can also call add
```

**`do-mac`**: Evaluate arguments at compile-time, leave result as code:

```hy
(do-mac `(setv ~(hy.models.Symbol (* "x" 5)) "foo"))
; Expands to: (setv xxxxx "foo")
```

## Macro Pitfalls

**Name shadowing**: Macros using bare names in expansions can accidentally capture variables:

```hy
; BAD — shadows outer x
(defmacro upper-twice [arg]
  `(do
     (setv x (.upper ~arg))
     (+ x x)))

; GOOD — use gensym
(defmacro upper-twice [arg]
  (setv g (hy.gensym))
  `(do
     (setv ~g (.upper ~arg))
     (+ ~g ~g)))
```

**Multiple evaluation**: Using an argument multiple times without assignment:

```hy
; BAD — .pop called twice
(defmacro upper-twice [arg]
  `(+ (.upper ~arg) (.upper ~arg)))
```

**Macro subroutines**: Functions used inside macros must be available at compile-time:

```hy
; Use hy.I for one-shot imports in macro expansions
(defmacro hypotenuse [a b]
  `(hy.I.math.sqrt (+ (** ~a 2) (** ~b 2))))

; Use eval-and-compile for helper functions
(eval-and-compile
  (defn subroutine [x] ...))
```

**Golden rule**: A typical macro should use only these names in expansions:
- Gensyms
- Core macros
- Python built-ins
- `hy` and its attributes

## Best Practices

- Use `hy.gensym` for all temporary variable names
- Use `hy.I` or `hy.R` for imports/requires inside macro expansions
- Extract complex logic into functions (wrapped in `eval-and-compile`)
- Don't shadow core macros (`pragma :warn-on-core-shadow True` is default)
- Set `_hy_export_macros` (or use `(export :macros [...])`) to control `require *` behavior
- Prefer the least powerful option: Python dynamic features → regular macro → reader macro
