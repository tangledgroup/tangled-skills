# Python Interoperability

## Contents
- Mangling and unmangling
- Keyword mincing
- Using Python from Hy
- Embedding Python code
- Using Hy from Python
- py2hy converter
- Compatibility tips

## Mangling and Unmangling

Hy's mangling converts permissive Hy symbol names to valid Python identifiers.

**`hy.mangle`**: Stringify and convert to Python-legal identifier:

```hy
(hy.mangle 'foo-bar)     ; → "foo_bar"
(hy.mangle "🦑")         ; → "hyx_XsquidX"
(hy.mangle "a.c!.d")     ; → "a.hyx_cXexclamation_markX.d"
```

Idempotent: `(= (hy.mangle (hy.mangle x)) (hy.mangle x))` → `True`.

**`hy.unmangle`**: Try to reverse mangling (may not round-trip):

```hy
(hy.unmangle "hyx_XsquidX")  ; → "🦑"
```

Not one-to-one: `foo-bar` and `foo_bar` both mangle to `foo_bar`.

**Cross-language access**: A Hy function named `valid?` is called `hyx_valid_Xquestion_markX` in Python. A Python function `str.format_map` is written `str.format-map` in Hy.

## Keyword Mincing

Python reserved words used as variable names in Hy can't be accessed directly from Python:

```hy
; In Hy:
(setv break 13)
```

```python
# In Python — this is a syntax error:
import my_module
print(my_module.break)  # ERROR
```

Workarounds:
- `getattr(my_module, "break")` — string literal access
- Use Unicode normalization: `my_module.𝐛reak` (mathematical bold letters normalize to ASCII under NFKC)

Mathematical bold small letters for all Python keywords: 𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳

## Using Python from Hy

**Import Python modules**: Just use `import`:

```hy
(import math os.path sys)
(print (math.sqrt 2))
(import os.path [exists isdir :as is-dir])
```

No additional ceremony required in most cases.

## Embedding Python Code

**`py`**: Parse a Python expression at compile-time:

```hy
(print "Result:" (py "'hello' + 'world'"))
```

Only expressions allowed (not statements). String must be literal. Implicitly wrapped in parentheses for indentation safety.

**`pys`**: Zero or more Python statements:

```hy
(pys "myvar = 5")
(print "myvar is" myvar)
```

Code is dedented with `textwrap.dedent()`. Beware: significant leading whitespace in embedded string literals will be removed.

## Using Hy from Python

**Import Hy modules**: Requires `import hy` first (in current module or earlier):

```python
import hy
import my_hy_module  # .hy file, auto-loaded via import hooks
```

**Execute Hy code from strings**:

```python
import hy
result = hy.eval(hy.read_many("(setv x 1) (+ x 1)"))  # → 2
```

No Hy equivalent of `exec()` — `hy.eval` works even for non-expression input.

**Launch REPL from Python**:

```python
import hy
hy.REPL(locals={**globals(), **locals()}).run()
```

**hy2py output**: Still imports `hy`, so Hy must be installed to run. See implicit names for workarounds.

## py2hy Converter

External tool for translating Python → Hy. Available as CLI and library.

**CLI:**

```bash
python3 -m py2hy --help
python3 -m py2hy mycode.py
python3 -m py2hy mycode.py | beautifhy -  ; autoformat output
```

**Programmatic API:**

```python
from py2hy import ast_to_models, ast_to_text
```

Output discards style info and most comments. Result is a starting point for hand translation. Useful for learning Hy syntax from Python examples.

**Unimplemented nodes**: `type_comment`, type aliases (`TypeAlias`, `TypeVar`, etc.), `TryStar`, pattern-matching AST nodes (`Match`, `MatchValue`, etc.).

## Compatibility Tips

**`sys.executable`**: When running via `hy` command, `sys.executable` points to the Hy wrapper. Restore original:

```hy
(setv sys.executable hy.sys-executable)
```

**Wrapper script**: For libraries that don't work with Hy's `sys.executable`, use a Python wrapper:

```python
import hy
import my_hy_program
```

**PyPy**: Hy runs on PyPy for faster execution.

**See also**: [Hy wiki compatibility tips](https://github.com/hylang/hy/wiki/Compatibility-tips) for package-specific guidance.
