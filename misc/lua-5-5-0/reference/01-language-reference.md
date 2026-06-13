# Language Reference

## Contents
- Values and Types
- Variables and Scopes
- Error Handling
- Metatables and Metamethods
- Garbage Collection
- Coroutines
- Lexical Conventions
- Operators
- Statements
- Expressions

## Values and Types

Lua is dynamically typed. Values carry their own type. Eight value types:

- **nil** — The nil value. Tests as false. Initializing a variable sets it to nil; accessing an undefined field yields nil.
- **boolean** — Two values: `false` and `true`. Both `nil` and `false` are falsy; everything else is truthy.
- **number** — Double-precision floating-point (default). Can also hold integers natively.
- **integer** — Signed 64-bit (default on 64-bit platforms). Use `//` for integer division, `%` for integer modulus.
- **string** — Immutable sequences of bytes (not necessarily characters). Safe for embedded zeros. Concatenate with `..`. Length with `#`.
- **table** — The sole data structure. Associative arrays indexed by any value except nil and NaN. Supports array semantics (sequential integer keys starting at 1) and map semantics simultaneously.
- **function** — First-class values with lexical scoping and full closures. Can be stored in variables, passed as arguments, returned.
- **thread** — Independent coroutine of execution (see Coroutines below).
- **userdata** — Arbitrary C data stored in a Lua variable. Two kinds: *full userdata* (allocated by Lua, can have metatables, subject to GC) and *light userdata* (represent C pointers, compared by value, no metatable).

Type coercion: `tonumber(e)` converts string/number to number. `tostring(v)` converts any value to string. Automatic numeric coercion occurs in arithmetic expressions (`"10" + 4` → `14`). String coercion occurs with concatenation (`10 .. "hello"` → `"10hello"`).

## Variables and Scopes

**Local variables:** Declared with `local`. Block-scoped. Can be reassigned.

```lua
local x = 10
local a, b, c = 1, 2, 3  -- multiple assignment
```

**Global variables:** Implicitly declared on first assignment. Stored in the global environment (`_G`).

**Upvalues:** Local variables captured by nested functions. Shared across all closures that reference them.

```lua
function counter()
    local count = 0
    return function()
        count = count + 1
        return count
    end
end
```

**Environments:** In Lua 5.2+, no per-chunk `_ENV`. Functions access globals through their upvalue chain. The debug library can manipulate environments.

## Error Handling

Lua propagates errors by unwinding the stack. Three mechanisms:

- **`error(message [, level])`** — Terminates the protected function and jumps to an error handler. `level` controls where the error location is reported (1 = error call site, 2 = caller of error, etc.).
- **`pcall(f [, arg1, ...])`** — Protected call. Returns `(true, results...)` on success, `(false, error_object)` on failure. Never propagates errors.
- **`xpcall(f, msgh [, arg1, ...])`** — Protected call with custom error handler `msgh`. The handler receives the error object and can produce a traceback via `debug.traceback()`.

```lua
local ok, err = pcall(function()
    return 1 / 0
end)
if not ok then
    print("Error: " .. err)
end
```

## Metatables and Metamethods

Every value can have a metatable. Tables and full userdata have individual metatables; other types share one per type.

Query with `getmetatable(obj)`, set on tables with `setmetatable(table, metatable)`.

### Indexing events

- **`__index`** — Called when reading a non-existent key. Can be a function `(table, key)` or a table (Lua looks up the key in that table).
- **`__newindex`** — Called when writing to a non-existent key. Can be a function `(table, key, value)` or a table (Lua writes to that table instead).
- **`__pairs` / `__ipairs`** — Custom iterators for `pairs()` and `ipairs()`.

### Arithmetic events

- **`__add (+)`**, **`__sub (-)`**, **`__mul (*)`**, **`__mod (%)`**, **`__pow (^)`**, **`__idiv (//)`**, **`__unm (-)`**
- Each receives the two operands (or one for unary). Return the result.

### Bitwise events

- **`__band (&)`**, **`__bor (|)`**, **`__bxor (~)`**, **`__bnot (~)`**, **`__shl (<<)`**, **`__shr (>>)`**
- Operate on integers only.

### Order events

- **`__lt (<)`**, **`__le (<=)`** — Return boolean. `>` and `>=` use `__lt` with reversed operands; `==` always uses raw equality (no metamethod).

### Other events

- **`__concat (..)`** — String concatenation.
- **`__len (#)`** — Length operator.
- **`__call`** — Call the object as a function. Chain limit: at most 15 objects in a `__call` chain.
- **`__gc`** — Garbage collection finalizer. Called before the object is collected. Can resurrect the object by creating a new reference.
- **`__close`** — Called on to-be-closed variables going out of scope. Receives `(value, is_error)` where `is_error` is the error object if exiting via error.

### Weak tables

Set `__mode` in the metatable to `"k"` (weak keys), `"v"` (weak values), or `"kv"` (both weak). Entries are collected when no other references exist.

```lua
local cache = setmetatable({}, {__mode = "v"})
cache[obj] = expensive_result  -- collected when obj has no other refs
```

## Garbage Collection

Lua uses automatic memory management. Two modes:

### Incremental mode (default)

Mark-and-sweep in small steps. Tune with:
- `collectgarbage("setpause", p)` — When GC restarts (default 200 = 2x memory growth).
- `collectgarbage("setstepmul", m)` — GC speed relative to allocation (default 200 = twice the allocation speed).
- Unified: `collectgarbage("param", value)` sets the combined parameter.

### Generational mode

Collects young objects more frequently. Better for programs that create many short-lived objects.
- `collectgarbage("generational", limit)` — Switch to generational with memory limit.
- `collectgarbage("incremental")` — Switch back to incremental.
- Parameters: `minormul` (how often to do minor collections) and `major` (how often to do major collections).

### Common options

- `collectgarbage("collect")` — Full GC cycle.
- `collectgarbage("count")` — Current memory in KB.
- `collectgarbage("stop"` / `"restart")` — Pause/resume GC.

## Coroutines

Coroutines provide cooperative multitasking. A coroutine suspends only by explicitly calling `coroutine.yield()`.

**Lifecycle:**
- `created` → `running` → `suspended` → `dead` (or back to suspended via yield)

**Functions:**
- `coroutine.create(f)` — Create a new coroutine. Returns thread object.
- `coroutine.resume(co, val1, ...)` — Resume execution. On first call, arguments go to `f`. On subsequent calls, arguments become yield results. Returns `(true, results...)` or `(false, error)`.
- `coroutine.wrap(f)` — Like `create`, but returns a callable function that internally resumes. Errors propagate.
- `coroutine.yield(...)` — Suspend the running coroutine. Return values become resume results.
- `coroutine.status(co)` — Returns `"suspended"`, `"running"`, `"normal"` (main thread), or `"dead"`.
- `coroutine.close(co)` — Close a suspended/dead coroutine, allowing its objects to be collected.
- `coroutine.running()` — Returns the running thread.
- `coroutine.isyieldable([co])` — Check if a coroutine can yield.

```lua
local co = coroutine.create(function(a, b)
    print(coroutine.yield(a + b))  -- yields 3
    print(coroutine.yield(a * b))  -- yields 2
end)
print(coroutine.resume(co, 1, 1))  -- true, 3
print(coroutine.resume(co, "x"))   -- x\ntrue, 2
```

## Lexical Conventions

**Identifiers:** Letters, digits, underscores. Cannot start with digit. Cannot be a reserved word.

**Reserved words:** `and`, `break`, `do`, `else`, `elseif`, `end`, `false`, `for`, `function`, `global`, `goto`, `if`, `in`, `local`, `nil`, `not`, `or`, `repeat`, `return`, `then`, `true`, `until`, `while`. The `global` keyword (new in 5.5) explicitly declares variables as global, voiding the implicit `global *` declaration at chunk start.

**Comments:** `--` to end of line. `--[[ ]]` for multi-line (nestable in 5.2+).

**String literals:** Double-quoted (`"..."`), single-quoted (`'...'`), long strings (`[[...]]`). Escape sequences: `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`, `\\`, `\"`, `\'`, `\nnn` (octal).

## Operators

**Arithmetic:** `+`, `-`, `*`, `/` (float division), `//` (integer division), `%` (modulus, sign follows divisor), `^` (exponentiation, right-associative), unary `-`.

**Bitwise:** `&` (and), `|` (or), `~` (xor), `~` (not, prefix), `<<` (left shift), `>>` (right shift). Operate on integers; convert floats to integers first.

**Concatenation:** `..` — Left-associative. Higher precedence than arithmetic.

**Relational:** `<`, `>`, `<=`, `>=`, `==`, `~=`. Compare numbers numerically, strings lexicographically. Tables/userdata/threads/functions compared by identity (same object). `nil` and `boolean` compared only with same type.

**Logical:** `and`, `or`, `not`. Short-circuit evaluation. `and` returns first operand if falsy, else second. `or` returns first operand if truthy, else second. `not` always returns `true` or `false`.

**Length:** `#` — For strings: byte length. For tables: the "length" is any integer boundary n where `t[n]` is not nil and `t[n+1] is nil`. Undefined for tables with holes. Can be customized via `__len`.

**Precedence (highest to lowest):**
1. `^`
2. `not`, `#`, `~`, unary `-`
3. `*`, `/`, `%`, `//`
4. `+`, `-`
5. `..`
6. `<`, `>`, `<=`, `>=`, `==`, `~=`
7. `&`
8. `~`
9. `<<`, `>>`
10. `|`
11. `and`
12. `or`

## Statements

**Blocks:** Sequences of statements delimited by `do...end`.

**Chunks:** Top-level blocks (files or strings). Each chunk is an implicit function with variadic arguments available via `arg` table.

**Assignment:** `varlist = explist`. Multiple assignment adjusts: extra values discarded, missing values filled with nil.

**Control structures:**
- `if condition then block [elseif condition then block ...] [else block] end`
- `while condition do block end`
- `repeat block until condition` — Condition checked after execution (always runs at least once).
- `break` — Terminates the innermost loop.
- `goto label` / `::label::` — Jump to label. Cannot jump into the scope of a local variable.

**For statement:**
- **Numerical for:** `for var = exp1, exp2, exp3 do block end` — Step defaults to 1. Control variable is read-only (since 5.5; declare a local if you need to modify it).
- **Generic for:** `for varlist in explist do block end` — Uses iterator functions. Standard iterators: `pairs(t)` (all keys), `ipairs(t)` (sequential integers from 1).

**Function calls as statements:** Ignore all return values. `f(arg1, arg2)`.

**Variable declarations:** `local name [list] [= explist]`. Can declare to-be-closed variables with `<·*close*>` annotation.

**To-be-closed variables:**

```lua
local file <·*close*> = io.open("data.txt")
-- __close metamethod called when file goes out of scope
```

Multiple to-be-closed variables in the same block are closed in reverse declaration order.

## Expressions

**Table constructors:** `{}` creates a new table each time. Three forms:
- List: `{1, 2, 3}` — Indices start at 1.
- Record: `{x = 10, y = 20}` — String keys.
- General: `{[exp] = exp, ...}` — Arbitrary key-value pairs.
Mix freely: `{1, 2, x = 10, [f(1)] = "hello"}`.

**Function calls:**
- `expr(args)` — Parenthesized arguments.
- `expr string` — Single string literal argument (no parentheses needed).
- `expr table` — Single table constructor argument.

**Function definitions:**

```lua
function name(params) block end
-- Equivalent to:
name = function(params) block end

local function name(params) block end
-- Equivalent to:
local name; name = function(params) block end
```

Variable arguments via `...`. Access via `select("#", ...)` for count, `select(1, ...)` for all values. The `...` expression yields all extra arguments.

**Multiple results:** Functions can return multiple values. In a list of expressions, only the last function call contributes multiple results (all others adjusted to one value). Use `{f()}` or `return f()` to capture all results.

## Lua 5.5 Incompatibilities (Migration from 5.4)

- **`global` is reserved** — Do not use `global` as a variable or function name.
- **For-loop control variable is read-only** — Cannot assign to it directly; declare a local with the same name if modification needed.
- **`__call` chain limit** — At most 15 objects in a `__call` metamethod chain.
- **nil error object replaced** — In errors, nil as the error object is replaced by a string message.
- **GC parameters changed** — Use `collectgarbage("param", value)` instead of `"incremental"`/`"generational"` options for tuning.
