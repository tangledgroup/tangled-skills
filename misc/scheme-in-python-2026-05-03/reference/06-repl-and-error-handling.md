# REPL and Error Handling

## Contents
- REPL Structure
- Multi-Line Input
- Pretty-Printing Scheme Values
- Error Classification
- Error Reporting
- Session Management
- Debugging Support

## REPL Structure

The read-eval-print loop is the interpreter's user-facing interface:

```python
def repl():
    """Interactive Scheme REPL."""
    env = create_global_frame()
    print("Scheme Interpreter (Python)")
    print("Type Ctrl-D or (exit) to quit.\n")

    while True:
        try:
            source = read_multiline("scm> ")
            if source is None:
                break  # EOF
            for line in source.split('\n'):
                tokens = tokenize(line.strip())
                if not tokens:
                    continue
                expr = read(tokens)
                result = eval_scheme(expr, env)
                if result is not None:
                    print(scheme_repr(result))
        except SchemeError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted.")
        except EOFError:
            break
```

### Exit Command

Register `exit` as a builtin that raises a special exception:

```python
class ExitException(Exception):
    pass

BUILTIN_PROCS["exit"] = lambda: (_ for _ in ()).throw(ExitException())

# In REPL:
except ExitException:
    break
```

## Multi-Line Input

Scheme expressions span multiple lines. Accumulate input until parentheses balance:

```python
def read_multiline(prompt="scm> "):
    """Read from stdin until parens are balanced."""
    buffer = ""
    while True:
        try:
            line = input(prompt)
        except EOFError:
            if buffer.strip():
                return buffer.strip()
            return None
        buffer += " " + line
        # Check paren balance
        depth = 0
        in_string = False
        escape = False
        for ch in buffer:
            if escape:
                escape = False
                continue
            if ch == '\\':
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch in '([':
                depth += 1
            elif ch in ')]':
                depth -= 1
        if depth == 0 and buffer.strip():
            return buffer.strip()
        prompt = "scm> "  # continuation prompt
```

Handle bracket matching: `[` pairs with `]`, `(` pairs with `)`. Some implementations treat all brackets interchangeably.

## Pretty-Printing Scheme Values

Convert Python objects back to readable Scheme notation:

```python
def scheme_repr(val):
    """Convert a Python value to its Scheme string representation."""
    if val is True:
        return "#t"
    if val is False:
        return "#f"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        # Avoid repr artifacts like 3.1400000000000001
        return f"{val:g}"
    if isinstance(val, Str):
        # String literal — include quotes
        escaped = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(val, str):
        return val  # symbol — no quotes
    if isinstance(val, Nil):
        return "()"
    if isinstance(val, Pair):
        return scheme_list_repr(val)
    if isinstance(val, (BuiltinProcedure, LambdaProcedure, MuProcedure)):
        return "#<procedure>"
    return repr(val)

def scheme_list_repr(pair):
    """Recursively format a Pair structure."""
    parts = []
    current = pair
    while is_pair(current):
        if current.rest is not nil and not is_pair(current.rest) and not is_nil(current.rest):
            # Dotted pair: (a b . c)
            parts.append(scheme_repr(current.first))
            parts.append(f". {scheme_repr(current.rest)}")
            return "(" + " ".join(parts) + ")"
        parts.append(scheme_repr(current.first))
        current = current.rest
    if is_nil(current):
        return "(" + " ".join(parts) + ")"
    # Should not reach here for proper lists
    return "(" + " ".join(parts) + f". {scheme_repr(current)})"
```

**Examples:**

| Python Value | scheme_repr Output |
|-------------|-------------------|
| `True` | `#t` |
| `False` | `#f` |
| `42` | `42` |
| `"hello"` (symbol) | `hello` |
| `Str("hello")` | `"hello"` |
| `nil` | `()` |
| `Pair(1, Pair(2, nil))` | `(1 2)` |
| `Pair(1, 2)` | `(1 . 2)` |
| `LambdaProcedure(...)` | `#<procedure>` |

## Error Classification

Scheme interpreters encounter several error categories:

### Syntax Errors

Invalid source structure:

```python
class SchemeSyntaxError(SchemeError):
    """Malformed input."""
    pass
```

Examples:
- Unmatched parentheses: `( + 1 2`
- Unexpected close paren: `) ) ( + 1`
- Invalid token in expression position

### Evaluation Errors

Runtime failures during evaluation:

```python
class SchemeEvalError(SchemeError):
    """Error during evaluation."""
    pass
```

Examples:
- Undefined variable: `(foo)` when `foo` is not bound
- Wrong number of arguments: `(+ 1)` (if `+` requires 2 args)
- Type error: `(+ "hello" 5)`
- Division by zero: `(/ 1 0)`
- Calling non-procedure: `(5 3)`

### Binding Errors

Variable-related issues:

```python
class SchemeBindingError(SchemeError):
    """Variable binding errors."""
    pass
```

Examples:
- `set!` on undefined variable: `(set! x 5)` when `x` doesn't exist
- Duplicate binding in `let`: `(let ((x 1) (x 2)) ...)`

## Error Reporting

Provide clear, actionable error messages:

```python
def report_error(error, context=None):
    """Format an error message for the user."""
    if isinstance(error, SchemeError):
        return f"Error: {error}"
    elif isinstance(error, ZeroDivisionError):
        return "Error: division by zero"
    elif isinstance(error, TypeError):
        return f"Error: type error — {error}"
    elif isinstance(error, NameError):
        return f"Error: undefined variable — {error}"
    else:
        return f"Error: {type(error).__name__}: {error}"
```

Include the offending expression in error messages when possible:

```python
raise SchemeError(f"Cannot apply {scheme_repr(operator)} to arguments")
raise SchemeError(f"{var} is not defined")
raise SchemeSyntaxError(f"Unmatched '(' in expression")
```

## Session Management

### Loading Files

```python
BUILTIN_PROCS["load"] = lambda filename: scheme_load(filename, env)

def scheme_load(filename, env):
    """Read and evaluate a Scheme file."""
    # Strip quotes if passed as symbol 'filename
    name = str(filename).strip("'\"")
    try:
        with open(name, 'r') as f:
            source = f.read()
        for line in source.split('\n'):
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            tokens = tokenize(line)
            if tokens:
                expr = read(tokens)
                eval_scheme(expr, env)
    except FileNotFoundError:
        raise SchemeError(f"File not found: {name}")
    return name
```

### Prompt Customization

```python
def make_prompt(tag="scm"):
    """Create a REPL prompt with optional continuation indicator."""
    return f"{tag}> "
```

## Debugging Support

### Step-by-Step Tracing

Add trace output to `eval_scheme` for debugging:

```python
TRACE = False

def eval_scheme(expr, env, depth=0):
    indent = "  " * depth
    if TRACE:
        print(f"{indent}Evaluating: {scheme_repr(expr)}")
    result = _eval_impl(expr, env, depth)
    if TRACE:
        print(f"{indent}  → {scheme_repr(result)}")
    return result
```

### Variable Inspection

```python
BUILTIN_PROCS["inspect"] = lambda name: scheme_inspect(name, env)

def scheme_inspect(name, env):
    """Show which frame a variable is bound in."""
    frame = env
    depth = 0
    while frame is not None:
        if name in frame.bindings:
            return f"{name} → {scheme_repr(frame.bindings[name])} (in {frame.name}, depth {depth})"
        frame = frame.parent
        depth += 1
    raise SchemeError(f"{name} is not defined")
```

### Frame Dump

```python
def dump_frame(env, depth=0):
    """Print the entire environment chain."""
    indent = "  " * depth
    frame = env
    level = 0
    while frame is not None:
        print(f"{indent}Frame {level} ({frame.name}):")
        for name, val in frame.bindings.items():
            print(f"{indent}  {name} = {scheme_repr(val)}")
        frame = frame.parent
        level += 1
```
