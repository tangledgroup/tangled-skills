# Built-in Functions

## I/O

### print

```python
print(*args)
```

Prints all arguments separated by spaces, followed by a newline.

### system

```python
system(cmd)
```

Executes a shell command. Returns the exit code. Considered a security risk — remove before deploying applications.

## Type Conversion

### str

```python
str(v)
```

Returns string representation of any object.

### float / number

```python
float(v, base=0)
number(v, base=0)
```

Converts to float. Accepts numbers or strings. Optional base for integer parsing (default 0 = auto-detect hex/decimal).

### int

```python
int(v)
```

Truncates a number to integer.

### abs

```python
abs(v)
```

Absolute value.

### round

```python
round(v)
```

Rounds to nearest integer.

### chr

```python
chr(n)
```

Returns a single-character string from an ordinal value.

### ord

```python
ord(s)
```

Returns the ordinal (integer) value of the first character of a string. Added in 1.1 by allefant.

## Type Checking

### istype

```python
istype(v, type_name)
```

Checks if `v` is of the given type. Returns 1 (true) or 0 (false). Valid `type_name` values: `"string"`, `"list"`, `"dict"`, `"number"`.

## Collections

### len

```python
len(v)
```

Returns the number of items in a list or dict, or the length of a string.

### range

```python
range(stop)
range(start, stop)
range(start, stop, step)
```

Returns a list of numbers from start (default 0) to stop (exclusive) with given step (default 1).

### copy

```python
copy(v)
```

Creates a shallow copy of a list or dict.

## Aggregation

### min / max

```python
min(*args)
max(*args)
```

Returns the minimum or maximum of all arguments.

## Functions and Objects

### bind

```python
bind(func, self)
```

Binds a function to a self object (creates a bound method).

### import

```python
import(module_name)
```

Imports a module by name. Looks for `.tpc` (compiled) or `.py` (source) files.

### from ... import ...

```python
from x import y
from x import *
```

Import specific names or all names from a module. Added in 1.1.

### exec

```python
exec(code, globals)
```

Execute compiled bytecode in the given global namespace.

## Assertions

### assert

```python
assert(condition)
```

Raises an exception if condition is false (0).

## File Operations

### exists

```python
exists(path)
```

Returns 1 if file exists, 0 otherwise.

### mtime

```python
mtime(path)
```

Returns the modification time of a file as a number. Raises if file does not exist.

### load

```python
load(fname)
```

Reads a file and returns its contents as a string (binary mode).

### save

```python
save(fname, data)
```

Writes data (string) to a file in binary mode.

## Low-Level

### fpack

```python
fpack(v)
```

Packs a float/double into raw bytes (IEEE 754 format).

### merge

```python
merge(a, b)
```

Merges dict `b` into dict `a`, or merges attributes of object `b` into object `a`.

## Module Access

### MODULES / BUILTINS

Global dictionaries accessible from any module:

- `MODULES` — All loaded modules
- `BUILTINS` — All builtin functions and values

### TP_NONE / tp_None

The None singleton value. Used as a key for default/append operations on lists.

## List Methods (accessed via string keys)

```python
lst.append(item)    # Add item to end
lst.pop()           # Remove and return last item
lst.index(item)     # Find index of item
lst.sort()          # Sort in place
lst.extend(other)   # Extend with items from another list
lst["*"]            # Pop all items (consume the list)
```

## String Methods (accessed via string keys)

```python
s.join(list)        # Join list items with separator s
s.split(delim)      # Split string by delimiter
s.index(sub)        # Find index of substring (raises if not found)
s.strip()           # Strip whitespace from both ends
s.replace(old, new) # Replace all occurrences of old with new
```

## Special Values

- `True` — Number 1
- `False` — Number 0
- `None` — The None singleton (`tp_None`)
- `__name__` — Module name (set during import)
- `__main__` — Name of the main module
