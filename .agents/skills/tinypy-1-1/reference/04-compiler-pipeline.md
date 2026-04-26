# Compiler Pipeline

TinyPy's compiler is written in tinypy itself and consists of three stages: tokenize → parse → encode. This enables full bootstrapping — the compiler can modify itself at runtime.

## Stage 1: Tokenizer (`tokenize.py`)

The tokenizer converts source text into a stream of tokens using a hand-written lexer.

### Token Types

- **symbol** — Keywords and operators (`def`, `class`, `+`, `==`, etc.)
- **name** — Identifiers (variable names, function names)
- **number** — Numeric literals (integers, floats, hex with `0x` prefix)
- **string** — String literals (single, double, or triple-quoted)
- **nl** — Newline (outside of brackets/parens/braces)
- **indent / dedent** — Indentation level changes (Python-style significant whitespace)
- **eof** — End of file

### Key Design Decisions

- Uses a `Token` class instead of dicts for memory efficiency (saved 1064 bytes in 1.1)
- Handles Python's significant whitespace via indent/dedent tokens
- Bracket depth tracking (`T.braces`) prevents newline/indent processing inside expressions
- Supports `#` comments and line continuation with `\`
- String escape sequences: `\n`, `\r`, `\t`, `\0`

### Token Class

```python
class Token:
    def __init__(self, pos=(0,0), type='symbol', val=None, items=None):
        self.pos, self.type, self.val, self.items = pos, type, val, items
```

Each token carries its source position `(line, column)` for error reporting.

## Stage 2: Parser (`parse.py`)

The parser uses **Top-Down Operator Precedence (TDOP)** parsing, also known as Pratt parsing. This is a particularly elegant approach that makes the parser very extensible — new operators can be added by modifying dictionaries.

### TDOP Concepts

Each token type has two methods:

- **nud** ("null denotation") — Handles prefix/unary context
- **led** ("left denotation") — Handles infix/binary context
- **lbp** ("left binding power") — Determines precedence for the operator

The core parsing loop:

```python
def expression(rbp):
    t = P.token
    advance()
    left = nud(t)
    while rbp < get_lbp(P.token):
        t = P.token
        advance()
        left = led(t, left)
    return left
```

### Operator Precedence

| Precedence | Operators |
|-----------|-----------|
| 65 | `**` (power) |
| 60 | `*`, `/`, `%` |
| 50 | `+`, `-` |
| 40 | `<`, `>`, `<=`, `>=`, `==`, `!=` |
| 36 | `<<`, `>>` |
| 35 | `not` (prefix), `is`, `in` |
| 31 | `and`, `&` |
| 30 | `or`, `\|` |
| 20 | `,` (tuple) |
| 10 | `=`, `+=`, `-=`, `*=`, `/=` |

### Supported Syntax

The parser handles:

- **Statements**: `def`, `class`, `if/elif/else`, `for`, `while`, `try/except`, `return`, `raise`, `break`, `continue`, `pass`, `import`, `from x import y`, `from x import *`, `del`, `global`
- **Expressions**: arithmetic, comparison, boolean, attribute access (`.`), indexing (`[]`), function calls
- **Literals**: strings (single/double/triple-quoted), numbers (int/float/hex), lists (`[]`), dicts (`{}`)
- **List comprehensions**: `[x for x in y]`
- **Variable args**: `*args` and `**kwargs`
- **Semicolons** for multiple statements on one line
- **Block structure** via indent/dedent or semicolons

### Metaprogramming

Since the parser's grammar is stored in dictionaries (`base_dmap`, `dmap`), you can modify the language at runtime. Phil Hassey demonstrated this by adding decorator support (`@decorator`) with only 611 bytes of code — the `deco.py` module patches tokenize, parse, and encode to understand the `@` symbol.

## Stage 3: Encoder (`encode.py`)

The encoder transforms the AST into bytecode.

### Register Allocation

- Uses a simple register allocator with up to 256 registers per frame
- `alloc(n)` finds the first contiguous gap of `n` free registers
- Temporary registers are named `$0`, `$1`, etc.
- Named variables map to specific registers
- An assertion after each frame verifies no temp registers were leaked

### Code Generation

- Each instruction is exactly 4 bytes
- String literals are embedded inline with length in a 16-bit header
- Numbers (doubles) are stored as raw IEEE 754 bytes
- Jump targets use tags that are resolved in a post-processing pass (`map_tags`)
- Position information (line numbers and source text) is embedded for traceback

### Output Format

The encoder produces a binary bytecode stream (`.tpc` files) that the VM can execute directly. The format is:

```
[REGS instruction][bytecode instructions][embedded strings][embedded doubles]
```

## Stage 4: py2bc (`py2bc.py`)

The `py2bc` module orchestrates the pipeline and handles module imports:

```python
def _compile(s, fname):
    tokens = tokenize.tokenize(s)
    t = parse.parse(s, tokens)
    r = encode.encode(fname, s, t)
    return r

def _import(name):
    if name in MODULES:
        return MODULES[name]
    # Load .tpc if exists and is newer than .py
    # Otherwise compile .py to .tpc
    code = load(name + ".tpc")
    g = {'__name__': name, '__code__': code}
    g['__dict__'] = g
    MODULES[name] = g
    exec(code, g)
    return g
```

## Bootstrapping

The build process:

1. Python runs `setup.py` which compiles the C VM
2. The initial VM loads `tokenize.py`, `parse.py`, `encode.py`, `py2bc.py`
3. These are compiled to `.tpc` bytecode and embedded into the binary
4. The final binary is self-contained — no Python dependency at runtime

The `boot.py` module provides shim implementations of C functions (like `fpack`, `system`, `load`, `save`) during bootstrapping, using Python's standard library equivalents.
