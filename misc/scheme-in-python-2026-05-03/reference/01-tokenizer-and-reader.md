# Tokenizer and Reader

## Contents
- Token Types
- Tokenizer Implementation
- Reader: Tokens to S-Expressions
- Pair-Based Linked Lists
- Quoted Expressions
- Dotted Pairs
- Multi-Line Input
- Common Pitfalls

## Token Types

Scheme has a minimal token set. Every character in source maps to exactly one token category:

| Category | Examples | Delimiter? |
|----------|----------|-----------|
| Open paren | `(` `[` | Yes — starts a list |
| Close paren | `)` `]` | Yes — ends a list |
| Symbol | `+`, `foo`, `set!`, `car` | No |
| Integer | `42`, `-7` | No |
| Float | `3.14`, `2.0` | No |
| Boolean | `#t`, `#f` | No |
| String | `"hello"`, `"\"quoted\""` | No |
| Character literal | `#\space`, `#\newline` | No |
| Comment | `;; line comment`, `;| block |;` | Consumed, not emitted |
| Quote shorthand | `'` | Expands to `(quote ...)` |
| Backtick | `` ` `` | Expands to `(quasiquote ...)` |
| Comma | `,` , `,@` | Expands to `(unquote ...)` / `(unquote-splicing ...)` |

Square brackets `[` `]` are treated as synonyms for parentheses in most implementations.

## Tokenizer Implementation

The tokenizer converts a raw string into a list of token strings. Two approaches:

### Character-by-Character Scanner

```python
def tokenize(text):
    """Split Scheme source text into a list of token strings."""
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        # Skip whitespace
        if ch in ' \t\n\r':
            i += 1
            continue
        # Skip line comments (;; or ;)
        if ch == ';':
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
        # Skip block comments (;| ... |;)
        if ch == ';' and i + 1 < len(text) and text[i + 1] == '|':
            end = text.find('|;', i + 2)
            if end == -1:
                raise SyntaxError("Unterminated block comment")
            i = end + 2
            continue
        # Parentheses are standalone tokens
        if ch in '()[]':
            tokens.append(ch)
            i += 1
            continue
        # Strings
        if ch == '"':
            j = i + 1
            while j < len(text):
                if text[j] == '\\' :
                    j += 2  # skip escaped char
                    continue
                if text[j] == '"':
                    break
                j += 1
            if j >= len(text):
                raise SyntaxError("Unterminated string")
            tokens.append(text[i:j + 1])
            i = j + 1
            continue
        # Quote, backtick, comma (standalone single-char tokens)
        if ch in "'`",":
            tokens.append(ch)
            i += 1
            continue
        # Character literals (#\x or #\\)
        if ch == '#' and i + 1 < len(text) and text[i + 1] == '\\':
            j = i + 2
            # Single-char literal vs named char
            if j < len(text) and not text[j].isspace() and text[j] not in '()[];\'"`,' :
                tokens.append(text[i:j + 1])
                i = j + 1
            else:
                # Named character like #\newline
                while j < len(text) and text[j].isalnum():
                    j += 1
                tokens.append(text[i:j])
                i = j
            continue
        # Booleans (#t, #f)
        if ch == '#' and i + 1 < len(text) and text[i + 1] in 'tf':
            tokens.append(text[i:i + 2])
            i += 2
            continue
        # Numbers (may start with - or +, but only if followed by digit)
        if ch in '-+' and i + 1 < len(text) and text[i + 1].isdigit():
            j = i + 1
            while j < len(text) and text[j].isdigit():
                j += 1
            if j < len(text) and text[j] == '.':
                j += 1
                while j < len(text) and text[j].isdigit():
                    j += 1
            tokens.append(text[i:j])
            i = j
            continue
        # Symbols (everything else: letters, digits, special chars like + * !)
        j = i
        while j < len(text) and not text[j].isspace() and text[j] not in '()[];\'"`,' :
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens
```

### Regex-Based Alternative

For simpler implementations, use `re.findall`:

```python
import re

TOKEN_RE = re.compile(
    r'''
      \s+                    |  # whitespace (skip)
      ;;[^\n]*               |  # line comment (skip)
      \(                     |  # open paren
      \)                     |  # close paren
      \[                     |  # open bracket
      \]                     |  # close bracket
      "[^"\\]*(?:\\.[^"\\]*)*" |  # string
      #[tf]                  |  # boolean
      #\\(?:\w+|.)           |  # character literal
      [+\-]?\d+(?:\.\d+)?    |  # number
      '[^()\s]               |  # quoted symbol
      `,?                    |  # backtick/comma
      \S+                     # symbol
    ''',
    re.VERBOSE
)

def tokenize_regex(text):
    return [t for t in TOKEN_RE.findall(text) if t.strip()]
```

## Reader: Tokens to S-Expressions

The reader consumes tokens and produces nested Python data structures. Two representation strategies exist:

### Strategy A: Nested Python Lists (Simple)

Tokens map directly to Python `list`, `str`, `int`, `float`, `bool`:

```python
def read(tokens):
    """Parse a token list into a nested Python structure."""
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    token = tokens.pop(0)
    if token == '(':
        result = []
        while tokens and tokens[0] != ')':
            result.append(read(tokens))
        if not tokens:
            raise SyntaxError("Unmatched '('")
        tokens.pop(0)  # consume ')'
        return result
    elif token in (')', ']', ']'):
        raise SyntaxError(f"Unexpected '{token}'")
    elif token == '[':
        result = []
        while tokens and tokens[0] not in (']', ')'):
            result.append(read(tokens))
        if not tokens:
            raise SyntaxError("Unmatched '['")
        tokens.pop(0)
        return result
    else:
        return parse_atom(token)

def parse_atom(token):
    """Convert a token string to its Python value."""
    if token == '#t':
        return True
    if token == '#f':
        return False
    # Try integer
    try:
        return int(token)
    except ValueError:
        pass
    # Try float
    try:
        return float(token)
    except ValueError:
        pass
    # String literal (with surrounding quotes)
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]  # strip quotes; real impl handles escapes
    return token  # symbol
```

### Strategy B: Pair-Based Linked Lists (SICP Style)

The reference implementations (CodingWithTim, MathewMouchamel) use `Pair` objects mirroring Scheme's cons cells:

```python
class Pair:
    """A Scheme pair (cons cell)."""
    def __init__(self, first, rest):
        self.first = first
        self.rest = rest

nil = object()  # The empty list singleton
```

The reader produces `Pair` chains instead of Python lists:

```python
def read_pair(tokens):
    """Read a parenthesized expression into a Pair-linked list."""
    if not tokens or tokens[0] != '(':
        raise SyntaxError("Expected '('")
    tokens.pop(0)
    result = read_rest(tokens)
    if not tokens:
        raise SyntaxError("Unmatched '('")
    if tokens[0] == '.':
        # Dotted pair: (a b . c) -> Pair(a, Pair(b, c))
        tokens.pop(0)
        result = handle_dotted(result, tokens)
    tokens.pop(0)  # consume ')'
    return result

def read_rest(tokens):
    """Read elements until ')' or '.'."""
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    if tokens[0] in (')', ']'):
        return nil
    if tokens[0] == '.':
        # Dotted pair terminator
        tokens.pop(0)
        return read(tokens)
    first = read(tokens)
    rest = read_rest(tokens)
    return Pair(first, rest)
```

**Choosing a strategy:** Use nested lists for quick prototypes and simple interpreters. Use `Pair` when you need to distinguish proper lists from dotted pairs, implement `cons`/`car`/`cdr` faithfully, or follow the SICP curriculum closely.

## Quoted Expressions

The `'` shorthand expands to `(quote ...)`. Handle it in the reader or tokenizer:

```python
# In the reader, after reading a token:
if token == "'":
    expr = read(tokens)
    return Pair("quote", Pair(expr, nil))
```

Similarly for backtick and comma:

| Shorthand | Expands To |
|-----------|-----------|
| `'expr` | `(quote expr)` |
| `` `expr `` | `(quasiquote expr)` |
| `,expr` | `(unquote expr)` |
| `,@expr` | `(unquote-splicing expr)` |

## Dotted Pairs

A dotted pair `(a b . c)` creates a list where the last `cdr` is not `nil` but `c`:

```
(a b . c)  →  Pair('a', Pair('b', 'c'))
(a b c)    →  Pair('a', Pair('b', Pair('c', nil)))
```

Validate dotted pairs: after `.`, exactly one more expression must appear before `)`.

## Multi-Line Input

For REPL use, accumulate input across lines until parentheses balance:

```python
def read_multiline(prompt="scm> "):
    """Read input from stdin, accumulating lines until parens balance."""
    buffer = ""
    while True:
        try:
            line = input(prompt)
        except EOFError:
            return None
        buffer += " " + line
        prompt = "  " + ("." * len(line.rsplit(None, 1)[-1] if line.split() else " ")) + " "
        # Count parens
        open_count = buffer.count('(') + buffer.count('[')
        close_count = buffer.count(')') + buffer.count(']')
        if open_count == close_count and buffer.strip():
            return buffer
```

## Common Pitfalls

- **Negative numbers**: `-` is both a unary operator and subtraction. In `(- 5)`, the reader sees tokens `['(', '-', '5', ')']`. The evaluator must distinguish based on operand count, not the reader.
- **String escaping**: Handle `\\`, `\"`, `\\n`, `\\t` inside string literals. A naive `"..."` split breaks on escaped quotes.
- **Whitespace in symbols**: Symbols like `set!`, `car`, `odd?` contain special characters. The tokenizer must not treat `!`, `?`, `*`, `+` as delimiters when part of a symbol.
- **Semicolon at start of line vs symbol prefix**: `;` always starts a comment, never a symbol. Do not treat it as part of token text.
