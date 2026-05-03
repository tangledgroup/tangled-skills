# Builtins and Pair

## Contents
- Pair Class and nil
- Cons Cell Operations
- List Construction
- Arithmetic Procedures
- Comparison Procedures
- Predicates
- Higher-Order Procedures
- I/O Procedures
- Registration Patterns

## Pair Class and nil

The `Pair` class models Scheme's cons cells — the fundamental building block of all list structures:

```python
class Pair:
    """A Scheme pair (cons cell) with first and rest fields."""
    def __init__(self, first, rest):
        self.first = first
        self.rest = rest

    def __repr__(self):
        return f"Pair({self.first!r}, {self.rest!r})"

    def __eq__(self, other):
        return (isinstance(other, Pair)
                and self.first == other.first
                and self.rest == other.rest)
```

The `nil` object represents the empty list:

```python
class Nil:
    """The empty list singleton."""
    def __repr__(self):
        return "nil"

    def __eq__(self, other):
        return isinstance(other, Nil)

nil = Nil()
```

### Proper Lists vs Dotted Pairs

A **proper list** ends with `nil`:
```
(1 2 3) → Pair(1, Pair(2, Pair(3, nil)))
```

A **dotted pair** ends with a non-nil value:
```
(1 . 2) → Pair(1, 2)
(1 2 . 3) → Pair(1, Pair(2, 3))
```

### Helper Functions

```python
def is_pair(exp):
    return isinstance(exp, Pair)

def is_nil(exp):
    return isinstance(exp, Nil)

def is_scheme_list(exp):
    """Check if exp is a proper list (ends with nil)."""
    while is_pair(exp):
        exp = exp.rest
    return is_nil(exp)
```

### Iterating Over Pairs

```python
def iter_rest(pair):
    """Yield elements of a Pair-linked list (proper list only)."""
    while is_pair(pair):
        yield pair.first
        pair = pair.rest

def to_python_list(pair):
    """Convert a Pair-linked proper list to a Python list."""
    result = []
    while is_pair(pair):
        result.append(pair.first)
        pair = pair.rest
    return result

def make_list(items):
    """Build a Pair-linked proper list from a Python iterable."""
    result = nil
    for item in reversed(items):
        result = Pair(item, result)
    return result
```

## Cons Cell Operations

### cons

Construct a pair:

```python
BUILTIN_PROCS["cons"] = lambda first, rest: Pair(first, rest)
```

```scheme
(cons 1 '(2 3))    ; → (1 2 3)
(cons 1 2)         ; → (1 . 2)
(cons '(a) '(b))   ; → ((a) b)
```

### car / cdr

Access first and rest of a pair:

```python
BUILTIN_PROCS["car"] = lambda p: p.first if is_pair(p) else (_ for _ in ()).throw(TypeError("car: expected pair"))
BUILTIN_PROCS["cdr"] = lambda p: p.rest if is_pair(p) else (_ for _ in ()).throw(TypeError("cdr: expected pair"))
```

Composed operations (`cadr`, `caddr`, `cadadr`, etc.):

```python
# Generate car/cdr compositions programmatically
for chars in ["ar", "ad", "dar", "ddr", "aadar", "aadar"]:
    name = f"c{chars}"
    fn = lambda p, _chars=chars: _car_cdr(_chars, p)
    BUILTIN_PROCS[name] = fn

def _car_cdr(opcode, val):
    for ch in opcode:
        if ch == 'a':
            val = val.first
        elif ch == 'd':
            val = val.rest
    return val
```

## List Construction

### list

Create a proper list from arguments:

```python
BUILTIN_PROCS["list"] = lambda *args: make_list(args)
```

```scheme
(list 1 2 3)    ; → (1 2 3)
(list)          ; → ()
```

### append

Concatenate lists (does not mutate):

```python
BUILTIN_PROCS["append"] = lambda *lists: scheme_append(lists)

def scheme_append(lists):
    """Append Scheme lists (Pair-linked). Returns new list."""
    result = nil
    for lst in reversed(lists):
        result = extend_list(lst, result)

def extend_list(front, back):
    """Concatenate two Pair-linked structures."""
    if not is_pair(front) and not is_nil(front):
        return Pair(front, back)  # dotted pair
    current = front
    while is_pair(current) and is_pair(current.rest):
        current = current.rest
    if is_pair(current):
        current.rest = back
    else:
        # front was nil or atomic
        pass
    return front if is_pair(front) else back
```

### reverse

```python
BUILTIN_PROCS["reverse"] = lambda lst: scheme_reverse(lst)

def scheme_reverse(lst):
    result = nil
    while is_pair(lst):
        result = Pair(lst.first, result)
        lst = lst.rest
    return result
```

### length / member / assq

```python
BUILTIN_PROCS["length"] = lambda lst: sum(1 for _ in iter_rest(lst))
BUILTIN_PROCS["member"] = lambda x, lst: scheme_member(x, lst)
BUILTIN_PROCS["assq"] = lambda key, alist: scheme_assq(key, alist)

def scheme_member(x, lst):
    """Return tail of lst starting with first element equal to x, or nil."""
    while is_pair(lst):
        if lst.first == x:
            return lst
        lst = lst.rest
    return nil

def scheme_assq(key, alist):
    """Find first pair in alist whose car equals key (== comparison)."""
    while is_pair(alist):
        if alist.first.first == key:
            return alist.first
        alist = alist.rest
    return nil
```

## Arithmetic Procedures

```python
import math

BUILTIN_PROCS["+"] = lambda *args: sum(args, 0)
BUILTIN_PROCS["-"] = lambda a, b=None: a - b if b is not None else -a
BUILTIN_PROCS["*"] = lambda *args: math.prod(args) if args else 1
BUILTIN_PROCS["/"] = lambda a, b: a / b
BUILTIN_PROCS["abs"] = abs
BUILTIN_PROCS["max"] = lambda *args: max(args)
BUILTIN_PROCS["min"] = lambda *args: min(args)
BUILTIN_PROCS["modulo"] = lambda a, b: a % b
BUILTIN_PROCS["quotient"] = lambda a, b: int(a / b)
BUILTIN_PROCS["remainder"] = lambda a, b: a - int(a / b) * b
BUILTIN_PROCS["square"] = lambda x: x * x
BUILTIN_PROCS["sqrt"] = math.sqrt
```

Division by zero should raise a `ZeroDivisionError`, which the REPL catches and reports.

## Comparison Procedures

```python
BUILTIN_PROCS["="] = lambda a, b: a == b
BUILTIN_PROCS["<"] = lambda a, b: a < b
BUILTIN_PROCS[">"] = lambda a, b: a > b
BUILTIN_PROCS["<="] = lambda a, b: a <= b
BUILTIN_PROCS[">="] = lambda a, b: a >= b
BUILTIN_PROCS["zero?"] = lambda x: x == 0
BUILTIN_PROCS["positive?"] = lambda x: x > 0
BUILTIN_PROCS["negative?"] = lambda x: x < 0
BUILTIN_PROCS["even?"] = lambda x: x % 2 == 0
BUILTIN_PROCS["odd?"] = lambda x: x % 2 != 0
```

## Predicates

Type-checking procedures that return `#t` or `#f`:

```python
BUILTIN_PROCS["boolean?"] = lambda x: isinstance(x, bool)
BUILTIN_PROCS["number?"] = lambda x: isinstance(x, (int, float))
BUILTIN_PROCS["integer?"] = lambda x: isinstance(x, int)
BUILTIN_PROCS["symbol?"] = lambda x: isinstance(x, str)
BUILTIN_PROCS["pair?"] = lambda x: is_pair(x)
BUILTIN_PROCS["null?"] = lambda x: is_nil(x)
BUILTIN_PROCS["list?"] = lambda x: is_scheme_list(x)
BUILTIN_PROCS["procedure?"] = lambda x: isinstance(x, (BuiltinProcedure, LambdaProcedure, MuProcedure))
BUILTIN_PROCS["string?"] = lambda x: isinstance(x, Str)
```

## Higher-Order Procedures

### map

```python
BUILTIN_PROCS["map"] = lambda proc, lst: make_list(
    proc(item) for item in iter_rest(lst)
)
```

```scheme
(map (lambda (x) (* x x)) '(1 2 3 4))
; → (1 4 9 16)
```

### filter

```python
BUILTIN_PROCS["filter"] = lambda pred, lst: make_list(
    item for item in iter_rest(lst) if is_true_value(pred(item))
)
```

```scheme
(filter odd? '(1 2 3 4 5))
; → (1 3 5)
```

### fold (accumulate / reduce)

```python
BUILTIN_PROCS["fold"] = lambda proc, init, lst: scheme_fold(proc, init, lst)

def scheme_fold(proc, init, lst):
    result = init
    for item in iter_rest(lst):
        result = proc(result, item)
    return result
```

```scheme
(fold + 0 '(1 2 3 4))     ; → 10
(fold * 1 '(1 2 3 4))     ; → 24
(fold cons nil '(a b c))   ; → (a b c)
```

### apply

```python
BUILTIN_PROCS["apply"] = lambda proc, args_list: scheme_apply(proc, args_list)

def scheme_apply(proc, args_list):
    """Apply proc to arguments collected from a list."""
    args = list(iter_rest(args_list))
    if callable(proc):
        return proc(*args)
    raise SchemeError(f"Not a procedure: {scheme_repr(proc)}")
```

## I/O Procedures

### display / write

```python
BUILTIN_PROCS["display"] = lambda x: sys.stdout.write(scheme_str(x))
BUILTIN_PROCS["write"] = lambda x: sys.stdout.write(scheme_repr(x))
BUILTIN_PROCS["newline"] = lambda: sys.stdout.write("\n")
```

`display` outputs the raw value (strings without quotes). `write` outputs the printed representation (strings with quotes, lists with parens).

### read

```python
BUILTIN_PROCS["read"] = lambda: scheme_read()

def scheme_read():
    """Read one Scheme expression from stdin."""
    line = input()
    tokens = tokenize(line)
    return read(tokens)
```

## Registration Patterns

Two common patterns for adding builtins:

### Dictionary Registration (Simple)

```python
BUILTIN_PROCS = {}

def add_builtin(name, fn):
    BUILTIN_PROCS[name] = BuiltinProcedure(name, fn)

add_builtin("my-func", lambda x, y: x + y)
```

### Decorator Registration (Cleaner)

```python
def builtin(name):
    def decorator(fn):
        BUILTIN_PROCS[name] = BuiltinProcedure(name, fn)
        return fn
    return decorator

@builtin("my-func")
def my_func(x, y):
    return x + y
```

### Argument Validation

For robustness, wrap builtins with argument checking:

```python
def check_type(value, type_name, python_type):
    if not isinstance(value, python_type):
        raise SchemeError(f"Expected {type_name}, got {scheme_repr(value)}")

def check_non_string(value, name):
    if isinstance(value, str):
        raise SchemeError(f"{name}: argument cannot be a string")
```
