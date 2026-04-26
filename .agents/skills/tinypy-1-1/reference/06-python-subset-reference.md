# Python Subset Reference

## Supported Features

### Data Types

- **Numbers** — All numbers are doubles (floating point). No separate int type.
- **Strings** — Single, double, or triple-quoted. Escape sequences: `\n`, `\r`, `\t`, `\0`.
- **Lists** — Dynamic arrays with indexing, slicing, and methods.
- **Dicts** — Hash maps supporting any hashable key (numbers, strings, lists, dicts).
- **None** — Singleton None value.
- **Functions** — First-class functions with closures (via globals reference).
- **Classes** — Single inheritance via meta dictionaries.

### Control Flow

- `if / elif / else`
- `for item in iterable`
- `while condition`
- `break`, `continue`, `pass`
- `try / except / else`
- `return` (with or without value)
- `raise exception`
- `del name`

### Functions

- Regular parameters: `def f(a, b): ...`
- Variable positional args: `def f(*args): ...`
- Variable keyword args: `def f(**kwargs): ...`
- Mixed: `def f(a, b, *args): ...` and `def f(a=b, **kwargs): ...`
- Default parameter values

**Limitation**: Mixing `*args` and `**kwargs` in the same call does not work. Only these patterns are valid:
```python
call_with_var_args(a, b, c, *d)
call_with_named_args(a=b, **c)
```

### Classes and Inheritance

- Class definition: `class Name: ...`
- Single inheritance via meta dictionaries
- `setmeta(obj, Class)` to set an object's class
- Dynamic class change at runtime (like Python's `obj.__class__ = NewClass`)
- Meta methods via separate meta class pattern

### Modules

- `import module_name`
- `from x import y`
- `from x import *`
- Module caching in `MODULES` dict
- `__name__` set to module name
- `if __name__ == '__main__':` pattern works

### Operators

- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`
- Bitwise: `&`, `|`, `<<`, `>>`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Boolean: `and`, `or`, `not`
- Identity: `is`, `is not`
- Membership: `in`, `not in`
- Augmented assignment: `+=`, `-=`, `*=`, `/=`
- Subscript: `obj[key]`, `obj[start:end]` (slicing)
- Attribute access: `obj.attr` (equivalent to `obj['attr']`)

### Literals

- Numbers: integers, floats, hex (`0x...`)
- Strings: `'single'`, `"double"`, `'''triple'''`, `"""triple"""`
- Lists: `[1, 2, 3]`, `[x for x in y]` (comprehensions)
- Dicts: `{key: value, ...}`
- None, True, False

### Special Syntax

- Semicolons for multiple statements on one line
- Line continuation with `\`
- `#` comments
- Python-style significant whitespace (indentation-based blocks)

## Not Supported

### Missing Data Types

- Tuples (expressions that would create tuples are treated as comma-separated expressions)
- Sets
- Complex numbers
- Byte strings
- Raw strings (`r'...'`)
- Unicode literals (`u'...'`)
- Generator expressions
- Dict comprehensions

### Missing Language Features

- Decorators (can be added at runtime via metaprogramming, but not built-in)
- Properties (`@property`)
- Multiple inheritance
- Metaclasses (Python-style `__metaclass__`)
- Descriptors (`__get__`, `__set__`, `__delete__` on class attributes)
- Context managers (`with` statement)
- Generator functions (`yield`)
- Assertions with messages (`assert x, "message"`)
- String formatting (`%` operator or `.format()`)
- f-strings
- Annotations / type hints
- `__getattr__`, `__setattr__` (tinypy uses meta system instead)
- `__new__` method
- Multiple exception types in one `except`
- Exception chaining

### Missing Builtins

- `type()`, `isinstance()` (use `istype()` instead)
- `hasattr()`, `getattr()`, `setattr()` (use dict-style access)
- `super()`
- `enumerate()`, `zip()`, `map()`, `filter()`, `reduce()`
- `sorted()`, `reversed()`
- `open()` (use `load()`/`save()` instead)
- `input()`, `raw_input()`
- `eval()` (use `tp_eval` from C API instead)
- `dir()`, `vars()`, `globals()`, `locals()`
- `callable()`, `id()`, `hash()`
- `bin()`, `hex()`, `oct()`
- `slice()`
- `list()`, `dict()`, `str()` constructors (partial support via `str()`)

### Missing Modules

Standard library modules are not included ("batteries not yet included"). Available modules in 1.1:

- **math** — Basic math functions (sin, cos, tan, sqrt, log, exp, pi, e, etc.) contributed by Rockins Chen
- **pygame** — Crude pygame module for SDL-based graphics (requires SDL library)

### Other Limitations

- All numbers are doubles — no integer overflow protection, potential floating-point precision issues
- No cyclic garbage collection — avoid circular references
- `dict == object` — attribute access and dict access are unified (`a.x == a['x']`)
- No separate namespace for class attributes vs instance attributes
- Exception messages are strings only (no exception classes)
- No stackless features despite being "stackless"
- Performance varies — sometimes as fast as CPython, sometimes half the speed
- Uses more memory than CPython

## Key Differences from Python

1. **Unified dict/object model**: In tinypy, objects and dicts are the same thing. `a.x` is equivalent to `a['x']`. This eliminates the need for `__getattr__`.

2. **Meta system instead of descriptors**: Instead of Python's descriptor protocol, tinypy uses Lua-style meta dictionaries attached via `setmeta()`.

3. **All numbers are doubles**: There is no distinction between int and float.

4. **No tuples**: Comma expressions create lists or are handled as multiple values.

5. **Simpler exception model**: Exceptions are strings, not class instances. No exception hierarchy.

6. **Limited `*args`/`**kwargs` mixing**: Only pure varargs or pure kwargs work in calls, not both together.
