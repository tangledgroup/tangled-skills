# Advanced Topics

## Contents
- Model patterns (parser combinators)
- Runtime code evaluation
- Macro expansion utilities
- Symbol generation
- Model conversion
- Custom repr registration
- Reader API
- Recommended libraries

## Model Patterns

`hy.model-patterns` provides parser combinators for pattern-matching trees of Hy models. Built on `funcparserlib`, primarily for compiler internals but useful in macros too.

**Usage:**

```hy
(import
  funcparserlib.parser [maybe many]
  hy.model-patterns *)

(setv parser (whole [
  (sym "try")
  (many (notpexpr "except" "else" "finally"))
  (many (pexpr
    (sym "except")
    (| (brackets) (brackets FORM) (brackets SYM FORM))
    (many FORM)))
  (maybe (dolike "else"))
  (maybe (dolike "finally"))]))

(setv result (.parse parser form))
```

**Key parsers:**

| Parser | Description |
|--------|-------------|
| `FORM` | Match any model |
| `SYM` | Match a symbol |
| `KEYWORD` | Match a keyword |
| `STR` | Match a string |
| `LITERAL` | Match any literal model |
| `sym NAME` | Match and skip named symbol/keyword |
| `brackets PARSERS` | Match args in square brackets |
| `pexpr PARSERS` | Match args in parentheses |
| `braces PARSERS` | Match args in curly braces |
| `in_tuple PARSERS` | Match args in tuple `#()` |
| `dolike HEAD` | Parse do-like expression |
| `whole PARSERS` | Match parsers then expect end of input |
| `times LO HI parser` | Repeat parser LO to HI times |
| `tag NAME parser` | Tag parse result with name |
| `unpack KIND` | Parse unpacking form (`#*`/`#**`) |
| `parse_if PRED parser` | Conditional parsing |
| `notpexpr *DISALLOWED` | Match anything except expressions headed by listed symbols |

funcparserlib built-ins: `(+)` sequence, `(|)` alternation, `(>> parser fn)` transform, `(skip parser)`, `(maybe parser)`, `(some pred)`.

Failed parse raises `funcparserlib.parser.NoParseError`.

## Runtime Code Evaluation

**`hy.eval`**: Evaluate Hy models as code (like Python's `eval()` but for models):

```hy
(hy.eval '(+ 1 1))                              ; → 2
(hy.eval (hy.read "(+ 1 1)"))                   ; → 2
(hy.eval '(my-macro) :module mymodule)           ; look up macros in module
(hy.eval '(local-mac) :macros (local-macros))   ; include local macros
```

Optional args: `globals`, `locals` (like Python `eval`), `module` (controls macro lookup), `macros` (dict of mangled name → function).

**`hy.read` / `hy.read-many`**: Parse source text to models:

```hy
(hy.eval (hy.read "(+ 1 1)"))                   ; single form
(hy.eval (hy.read-many "(setv x 1) (+ x 1)"))   ; multiple forms
```

Warning: Reading can execute arbitrary code via reader macros. Don't read untrusted input.

## Macro Expansion Utilities

**`hy.macroexpand-1`**: Expand one level of macro:

```hy
(defmacro m [x] `(do ~x ~x ~x))
(hy.repr (hy.macroexpand-1 '(m (+ n 1))))
; → '(do (+ n 1) (+ n 1) (+ n 1))
```

**`hy.macroexpand`**: Expand fully until no more expansion:

```hy
(defmacro m [x] (and (int x) `(m ~(- x 1))))
(hy.repr (hy.macroexpand '(m 5)))   ; → '0
```

Core macros that return internal compiler objects won't expand — you get the original back. Local macros invisible unless provided via `:macros`.

## Symbol Generation

**`hy.gensym`**: Generate unique symbol names, essential for macro hygiene:

```hy
(defmacro selfadd [x]
  (setv g (hy.gensym))
  `(do
     (setv ~g ~x)
     (+ ~g ~g)))

; Optional debug hint:
(hy.gensym "temp")  ; → symbol like #:temp_G12345
```

## Model Conversion

**`hy.as-model`**: Recursively convert Python values to Hy models:

```hy
(= 7 '7)                        ; → False (int vs model)
(= (hy.as-model 7) '7)          ; → True
```

Called implicitly by compiler when inserting macro expansions. Error on self-referential or non-literal objects (e.g., functions).

## Custom repr Registration

**`hy.repr`**: Hy's equivalent of Python's `repr()`, outputs in Hy syntax:

```hy
(hy.repr [1 2 3])   ; → "[1 2 3]"
(repr [1 2 3])      ; → "[1, 2, 3]"
```

**`hy.repr-register`**: Register custom conversion for types:

```hy
(defclass C)
(hy.repr-register C (fn [x] "cuddles"))
(hy.repr [1 (C) 2])  ; → "[1 cuddles 2]"
```

Auto-detects self-references and outputs `"..."` (or custom placeholder via `:placeholder`).

## Reader API

**`hy.HyReader`**: Modular reader for Hy source. Key methods:

| Method | Description |
|--------|-------------|
| `.parse(stream, filename, skip_shebang)` | Yield all models in stream |
| `.parse-one-form()` | Parse next form, return model |
| `.parse-forms-until(closer)` | Yield models until closer char |
| `.getc()` / `.peekc()` | Consume/peek character |
| `.getn(n)` | Consume n characters |
| `.read-ident()` | Read identifier characters |
| `.slurp-space()` | Consume whitespace |
| `.dispatch(tag)` | Call reader macro handler |
| `.fill_pos(model, start)` | Set position info on model |

**`hy.Reader`**: Abstract base class with `reader_table` (dict mapping macro key → dispatch function), `ends_ident` (char set), and `pos` (read-only line/column tuple).

**`hy.PrematureEndOfInput`**: Raised when input ends unexpectedly during parsing.

## Recommended Libraries

**hyrule**: Hy's standard utility library providing functions and macros not in core:
- `(import hyrule [inc])` — increment
- `(require hyrule [case])` — case/switch macro
- `(require hyrule [unless])` — negated when
- `(require hyrule [block])` — labeled blocks with `block-ret`
- `(require hyrule [defmacro!])` — macro def with automatic gensyms
- `(require hyrule [of])` — generic type annotation helper
- `(require hyrule [macroexpand-all])` — expand all macros in a form

**toolz / cytoolz**: Functional programming utilities:
```hy
(import toolz [partition])
(list (partition 2 [1 2 3 4 5 6]))  ; → [#(1 2) #(3 4) #(5 6)]
```

**metadict**: Attribute-style dictionary access:
```hy
(import metadict [MetaDict])
(setv d (MetaDict))
(setv d.foo 1)
d.foo  ; → 1
```
