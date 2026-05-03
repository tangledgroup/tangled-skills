# Core Syntax & Data Types

## Contents
- Forms and models
- Literals
- Identifiers and symbols
- Keywords
- Strings
- Sequential forms
- Syntactic sugar
- Non-form elements

## Forms and Models

Hy source code is parsed into **forms** (textual units) represented as **models** (Python objects). All models inherit from `hy.models.Object`, which stores line/column position for tracebacks. Key model classes:

| Model | Python type | Description |
|-------|-------------|-------------|
| `hy.models.Integer` | `int` | Literal integer |
| `hy.models.Float` | `float` | Literal float |
| `hy.models.Complex` | `complex` | Literal complex number |
| `hy.models.String` | `str` | Literal string |
| `hy.models.Bytes` | `bytes` | Literal bytes |
| `hy.models.Symbol` | — | Symbol (variable name, operator) |
| `hy.models.Keyword` | — | Keyword (`:foo`) |
| `hy.models.Expression` | — | Parenthesized form `(a b c)` |
| `hy.models.List` | — | List literal `[1 2 3]` |
| `hy.models.Tuple` | — | Tuple literal `#(1 2 3)` |
| `hy.models.Set` | — | Set literal `#{1 2 3}` (ordered in model) |
| `hy.models.Dict` | — | Dict literal `{k1 v1 k2 v2}` |
| `hy.models.FString` | — | Format string with embedded Hy code |

Models ≠ their Python values: `(= (hy.models.String "foo") "foo")` → `False`. Convert with `hy.as-model` (value→model) or Python constructors like `str()` (model→value).

## Literals

All Python numeric syntax supported, plus Hy extensions:

```hy
1              ; int
1.2            ; float
4j             ; complex
5+4j           ; complex (single literal in Hy)
10,000,000     ; commas as digit separators
NaN Inf -Inf   ; special floats
True False None ; bool and None
```

**Collection literals:**

```hy
#(1 2 3)       ; tuple
[1 2 3]        ; list
#{1 2 3}       ; set
{1 2 3 4}      ; dict — alternating key/value pairs → {1: 2, 3: 4}
"hello"        ; string (double quotes only, no single quotes)
b"bytes"       ; bytes
```

## Identifiers and Symbols

Identifiers are any nonempty sequence excluding ASCII whitespace and `()[]{};"'`~`. Reader tries in order: numeric literal → dotted identifier → symbol.

**Symbols** are the catch-all. Compiled to Python variable names after **mangling**:

1. Remove leading underscores (restore at end)
2. Convert `-` to `_` (`foo-bar` → `foo_bar`)
3. If still not Python-legal: prepend `hyx_`, replace illegal chars with `X<unicode-name>X`
4. Restore leading underscores, normalize Unicode

```hy
foo-bar    ; → foo_bar
green☘     ; → hyx_greenXshamrockX
valid?     ; → hyx_valid_Xquestion_markX
```

Note: `foo-bar` and `foo_bar` mangle to the same name — they refer to the same variable.

**Dotted identifiers**: `foo.bar.baz` ≡ `(. foo bar baz)`. Leading dots: `.foo` ≡ `(. None foo)`, `..foo.bar` ≡ `(.. None foo bar)`.

## Keywords

String starting with `:` and no dot: `:foo` is a `hy.models.Keyword`.

Primary use: set keyword arguments in expressions. `(f :foo 3)` calls `f(foo=3)`. Hy allows positional and keyword args to be mixed: `(f 1 :foo 2 3)` works (kw args are reordered internally).

Keywords evaluate to themselves. Empty keyword `:` is syntactically legal but can't compile in function calls due to Python limitations.

**Calling a keyword on data**: `(:foo bar)` ≡ `(get bar "foo")` — gets the `"foo"` key from `bar`. Optional default: `(:foo bar "default")`.

## Strings

Hy supports double-quoted strings only (no single-quoted or triple-quoted). All string literals can contain newlines. Backslash escapes follow Python rules; unrecognized escapes are errors. Raw strings: `r"no\nescape"`.

Prefixes: only lowercase `r`, `b`, `f` recognized. No `u` prefix.

**Bracket strings**: Custom delimiters like Lua long brackets.

```hy
#[["That's very kind of yuo [sic]" Tom wrote back.]]
#[==[1 + 1 = 2]==]
```

Always raw Unicode (no `r`/`b` prefixes). If content starts with a newline, that first newline is removed.

**F-strings**: Embedded Hy code in `{}`:

```hy
(setv foo "a")
(print f"The sum is {(+ 1 1)}.")  ; => The sum is 2.
(print f"{foo :x<5}")             ; space needed to terminate form → axxxx
```

Comments and backslashes are allowed inside replacement fields.

## Sequential Forms

**Expressions** `(...)`: Parenthesized forms. First element (head) determines behavior:
- If head symbol names a macro → macro expansion
- Otherwise → Python function call with remaining elements as arguments
- Empty expression `()` is legal at reader level but compile error

**List literals** `[...]`: Square brackets produce Python lists.

**Tuple literals** `#(...)`: Hash-paren produces tuples.

**Set literals** `#{...}`: Hash-brace produces sets (model preserves order/duplicates unlike real sets).

**Dict literals** `{...}`: Brace with even number of child forms → alternating key/value pairs. Odd number is compile error.

## Syntactic Sugar

Single-character prefixes construct two-item expressions without parentheses:

| Macro | Syntax | Equivalent |
|-------|--------|------------|
| `quote` | `'FORM` | `(quote FORM)` |
| `quasiquote` | `` `FORM `` | `(quasiquote FORM)` |
| `unquote` | `~FORM` | `(unquote FORM)` |
| `unquote-splice` | `~@FORM` | `(unquote-splice FORM)` |
| `unpack-iterable` | `#* FORM` | `(unpack-iterable FORM)` |
| `unpack-mapping` | `#** FORM` | `(unpack-mapping FORM)` |

All resolved at reader level — same model produced with or without sugar.

## Non-Form Elements

- **Shebang**: `#!` on first line is ignored by Hy (handled by OS)
- **Whitespace**: ASCII whitespace only (U+0009, 0A, 0B, 0C, 0D, 20). Non-ASCII whitespace treated as identifier characters.
- **Comments**: `;` to end of line
- **Discard prefix**: `#_` reads and discards the following form (structure-aware comment, unlike `;`)
