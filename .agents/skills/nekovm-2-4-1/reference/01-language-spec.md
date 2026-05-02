# Language Specification

## Contents
- Syntax Grammar
- Value Types
- Operations
- Execution Flow
- Arrays
- Strings
- Hashtables
- Objects
- Functions
- Exceptions
- Runtime Type Information (RTTI)

## Syntax Grammar

Neko uses a left-to-right LL(1) parser. Every statement is also an expression, enabling constructs like `return if(x) { ... } else { ... }`. The grammar is designed to be easy to generate from higher-level languages rather than hand-write.

**Program structure:**
```
program := expr program | SEMICOLON program | _
expr := value | { program } | { ident1 => expr1, ident2 => expr2 }
     | expr DOT ident | expr ( parameters ) | expr [ expr ] | expr binop expr
     | ( expr ) | var variables | while expr expr | do expr while expr
     | if expr expr [else expr] | try expr catch ident expr
     | function ( parameters-names ) expr | return [expr | SEMICOLON]
     | break [expr | SEMICOLON] | continue | ident :
     | switch expr { switch-case* } | MINUS expr
switch-case := default => expr | expr => expr
```

**Operator precedence** (least to greatest): assignments, `++=`/`%%--=%%`, `&&`/`||`, comparisons, `+`/`-`, `*`/`/`, `|`/`&`/`^`, `<<`/`>>`/`>>>`/`%`.

**Values:** `[0-9]+` (int), `0x[hex]` (hex int), `[0-9].*[0-9]` (float), `"string"`, `$ident` (builtin), `true`/`false`/`null`/`this`/`ident`.

## Value Types

| Type | Description |
|------|-------------|
| `null` | Uninitialized/default value |
| `int` | Signed 31-bit integer (decimal or hex) |
| `float` | 64-bit double-precision floating point |
| `bool` | `true` or `false` |
| `string` | Mutable byte buffer, independent of encoding |
| `array` | Fixed-size, 0-based integer-indexed table |
| `object` | Hashed-field hashtable with O(log n) access |
| `function` | First-class value, fixed or variable arity |
| `abstract` | Opaque C data pointer tagged with a *kind* |

## Operations

### Arithmetic

`+` performs numeric addition for int/float, string concatenation when either operand is a string, and calls `%%__add%%`/`%%__radd%%` on objects. Integer division `/` returns float; use `$idiv` for integer division. Overflow does not convert to float or throw — it wraps silently.

```neko
$print($isinfinite(1/0));  // true
$print($isnan(0/0));       // true
```

### Bitwise

`<<`, `>>`, `>>>`, `|`, `&`, `^` — integer only, 31-bit signed. Non-integer operands raise an exception.

### Boolean

`&&` and `||` are short-circuited. No automatic boolean conversion — only the literal `true` satisfies conditions. Use `$istrue(v)` to convert any value to boolean: `null`, `false`, and integer `0` are falsy; everything else is truthy. `$not(v)` inverts `$istrue(v)`.

### Comparisons

`==`, `!=`, `<`, `>`, `<=`, `>=` dispatch through `$compare` which returns 0/-1/1 or null (invalid). Objects use `%%__compare%%` method for comparison. Use `$pcompare` for physical (address-based) comparison, faster for integers.

### Optimized integer operations

Skip type checks for speed: `$iadd(a,b)`, `$isub(a,b)`, `$imult(a,b)`, `$idiv(a,b)`. Results unspecified if operands are not integers. `$idiv(1,0)` raises an exception.

### Conversions

- `$int(v)` — string/float to integer
- `$float(v)` — string/int to float
- `$string(v)` — any value to string (calls `%%__string%%` on objects)
- `$istrue(v)` — any value to boolean

## Execution Flow

- `{ v1; v2; ... vk }` — sequential execution, returns last value (`null` if empty)
- `{ i1 => v1, i2 => v2 }` — object literal creation
- `v DOT ident` — object field access
- `v ( args )` — function call
- `v [ idx ]` — array index access
- `var i1 = v1, i2 = v2` — variable declarations
- `while cond body` / `do body while cond` — loops; value from `break expr` or unspecified
- `if cond e1 else e2` — only literal `true` satisfies condition
- `try e1 catch ident e2` — exception handler
- `return expr` / `break expr` — exit function/loop with value
- `switch expr { case => result ... default => def }` — equality-based dispatch

## Arrays

Fixed-size, not resizable. Maximum 2^29 - 1 elements.

| Builtin | Description |
|---------|-------------|
| `$array(v1, v2, ...)` | Create array with initial values |
| `$amake(size)` | Create empty array of given size |
| `$asize(a)` | Array length |
| `$acopy(a)` | Deep copy |
| `$asub(a, pos, len)` | Subarray (returns `null` if out of bounds) |
| `$ablit(dst, dpos, src, spos, len)` | Copy elements between arrays |

Access with integer index returns value or `null` if out of bounds. Non-integer index raises exception. Write outside bounds silently does nothing.

## Strings

Mutable byte buffers, independent of encoding. Maximum 2^29 - 1 bytes. Can contain `\0`.

| Builtin | Description |
|---------|-------------|
| `$smake(size)` | Allocate string of given size |
| `$ssize(s)` | String length in bytes |
| `$scopy(s)` | Copy string |
| `$ssub(s, pos, len)` | Substring |
| `$sget(s, pos)` | Get byte at position (0-255 or `null`) |
| `$sset(s, pos, byte)` | Set byte (value mod 256) |
| `$sblit(dst, dpos, src, spos, len)` | Blit bytes between strings |
| `$sfind(s, start, needle)` | Find substring position or `null` |

Escape sequences in literals: `\"`, `\\`, `\n`, `\r`, `\t`, `\xxx` (3-digit decimal 000-255).

## Hashtables

Abstract type manipulated only through builtins. Stores (key, value) pairs with any Neko value as key.

| Builtin | Description |
|---------|-------------|
| `$hnew(size)` | Create hashtable with initial slot count |
| `$hadd(h, k, v)` | Add binding |
| `$hset(h, k, v, cmp)` | Set/replace binding (custom comparator or `null` for default) |
| `$hmem(h, k, cmp)` | Membership test |
| `$hget(h, k, cmp)` | Get value or `null` |
| `$hremove(h, k, cmp)` | Remove binding, returns success boolean |
| `$hresize(h, size)` | Resize (usually automatic) |
| `$hsize(h)` | Slot count |
| `$hcount(h)` | Number of bindings |
| `$hiter(h, f)` | Iterate: calls `f(key, value)` for each binding |

Hash function is `$hkey(k)` — cannot be overridden, but comparison function can be customized.

## Objects

Hashed-field hashtable with O(log n) access (dichotomy on sorted flat array). Field names are hashed at compile time; the global field table ensures hash uniqueness and supports reverse lookup via `$field`.

| Builtin | Description |
|---------|-------------|
| `$new(null)` / `$new(obj)` | Create empty object or copy of `obj` |
| `o.field = val` / `o.field` | Dot access (compile-time hashed) |
| `$objset(o, $hash("f"), val)` | Runtime field set |
| `$objget(o, $hash("f"))` | Runtime field get |
| `$objfield(o, $hash("f"))` | Field existence check (returns `true` even if value is `null`) |
| `$objremove(o, $hash("f"))` | Remove field |
| `$objfields(o)` | Array of all field identifiers |
| `$objgetproto(o)` / `$objsetproto(o, p)` | Get/set prototype chain |
| `$objcall(o, $hash("m"), args)` | Call method with `this` set to `o` |

**Methods:** Functions called via dot access or `$objcall` receive the object as `this`. The context is local to the call — modifications are restored on return.

**Operator overloading:** Define methods on objects to overload operators:

| Operator | Method | Reverse method |
|----------|--------|---------------|
| string conversion | `%%__string%%()` | — |
| comparison | `%%__compare%%(other)` | — |
| `+` | `%%__add%%(b)` | `%%__radd%%(a)` |
| `-` | `%%__sub%%(b)` | `%%__rsub%%(a)` |
| `*` | `%%__mult%%(b)` | `%%__rmult%%(a)` |
| `/` | `%%__div%%(b)` | `%%__rdiv%%(a)` |
| `%` | `%%__mod%%(b)` | `%%__rmod%%(a)` |
| `[i]` read | `%%__get%%(i)` | — |
| `[i] = v` write | `%%__set%%(i, v)` | — |

**Prototypes:** When a field is not found in an object, Neko searches the prototype recursively. This enables class-like inheritance:

```neko
var proto = $new(null);
proto.foo = function() { $print(this.msg) };
var o = $new(null);
o.msg = "hello";
$objsetproto(o, proto);
o.foo();  // prints "hello"
```

## Functions

Functions are values. Called by value — `foo(1)` calls whatever function is stored in `foo`. Calling a non-function or with wrong argument count raises an exception.

| Builtin | Description |
|---------|-------------|
| `$nargs(f)` | Argument count (-1 for variable arity) |
| `$call(f, context, args_array)` | Call function with array of arguments and object context |
| `$closure(f, null, arg1, ...)` | Partial application (currying); also fixes `this` context |
| `$apply(f, arg1)(arg2)` | Delayed call — if function needs more args, returns a continuation |

## Exceptions

Any value can be thrown. Use `$throw(v)` to raise and `try...catch` to handle.

```neko
try
    foo()
catch e {
    $print(e, " raised from: ", $excstack());
}
```

| Builtin | Description |
|---------|-------------|
| `$throw(v)` | Raise exception with value `v` |
| `$rethrow(v)` | Re-raise, combining current and next exception stacks |
| `$excstack()` | Current exception stack (filenames + positions) |
| `$callstack()` | Current call stack at any point |

## Runtime Type Information (RTTI)

`$typeof(v)` returns an integer type constant:

| Constant | Value | Type |
|----------|-------|------|
| `$tnull` | 0 | null |
| `$tint` | 1 | int |
| `$tfloat` | 2 | float |
| `$tbool` | 3 | bool |
| `$tstring` | 4 | string |
| `$tobject` | 5 | object |
| `$tarray` | 6 | array |
| `$tfunction` | 7 | function |
| `$tabstract` | 8 | abstract |

```neko
$typeof(3);             // 1
$typeof($array(1,2));   // 6
$typeof(null) == $tnull; // true
```
