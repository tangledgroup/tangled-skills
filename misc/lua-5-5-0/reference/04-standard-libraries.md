# Standard Libraries

## Contents
- Basic Functions
- Coroutine Library
- String Library and Patterns
- UTF-8 Library
- Table Library
- Math Library
- I/O Library
- OS Library
- Debug Library
- Package Library

## Basic Functions

Global functions available without requiring a module.

**`assert(v [, message])`** — Raise an error if `v` is falsy. Message defaults to `"assertion failed!"`.

**`collectgarbage([opt [, arg]])`** — Control the garbage collector.
- `"collect"` — Full GC cycle (default).
- `"count"` — Current memory in KB (and bytes as second result).
- `"stop"` / `"restart"` — Pause/resume GC.
- `"setpause", p` / `"setstepmul", m` — Tune incremental mode.
- `"param", value` — Unified parameter setting.
- `"generational", limit` — Switch to generational mode.
- `"incremental"` — Switch back to incremental.
- `"isrunning"` — Returns true if GC is running.

**`dofile([filename])`** — Load and run a file as a chunk. Returns all results. Propagates errors.

**`error(message [, level])`** — Terminate the protected function. `level` controls error location reporting (1 = error call, 2 = caller).

**`getmetatable(object)`** — Return the metatable of the value.

**`ipairs(t)`** — Iterator for array part of table: `1, t[1]`, `2, t[2]`, ... until first nil.

**`load(chunk [, chunkname [, mode [, env]]])`** — Load a chunk from a string without executing it. Returns the compiled function or `(nil, error)`. `mode`: `"b"` (binary), `"t"` (text), `"bt"` (both). `env` sets the environment table.

**`loadfile([filename [, mode [, env]]])`** — Load a chunk from a file. Same semantics as `load`.

**`next(table [, index])`** — Traverse table fields. Returns key-value pairs in arbitrary order. Passing nil as index returns the first pair. Modifying the table during traversal produces undefined behavior.

**`pairs(t)`** — Iterator for all keys: `next, t, nil`.

**`pcall(f [, arg1, ...])`** — Protected call. Returns `(true, results...)` or `(false, error_object)`.

**`print(...)`** — Print arguments to stdout using `tostring`.

**`rawequal(v1, v2)`** — Compare without `__eq` metamethod.

**`rawget(table, index)`** — Access without `__index` metamethod.

**`rawlen(v)`** — Get length without `__len` metamethod.

**`rawset(table, index, value)`** — Set without `__newindex` metamethod.

**`require(modname)`** — Load a module. Searches `package.path` (Lua) and `package.cpath` (C). Caches in `package.loaded`. Returns the module table.

**`select(index, ...)`** — If `index` is number, returns arguments from that position. If `index` is `"#"`, returns total argument count.

**`setmetatable(table, metatable)`** — Set the metatable of a table.

**`tonumber(e [, base])`** — Convert to number. Base defaults to 10. Returns nil on failure.

**`tostring(v)`** — Convert to string. Calls `__tostring` metamethod if available.

**`type(v)`** — Return type name as string: `"nil"`, `"boolean"`, `"number"`, `"string"`, `"table"`, `"function"`, `"thread"`, `"userdata"`.

**`_VERSION`** — String `"Lua 5.5"`.

**`warn(msg1, ...)`** — Print warning messages to stderr. Does not stop execution. Can be replaced via `debug.setwarningf`.

**`xpcall(f, msgh [, arg1, ...])`** — Protected call with error handler `msgh`.

**`_G`** — The global environment table.

## Coroutine Library

Accessible as `coroutine.*`.

**`coroutine.close([co])`** — Close a suspended or dead coroutine. Runs pending close metamethods. Returns `(true)` or `(false, error)`.

**`coroutine.create(f)`** — Create a new coroutine with main function `f`. Returns thread object (status: `"suspended"`).

**`coroutine.isyieldable([co])`** — Returns true if the coroutine can yield. Main thread is not yieldable unless running inside a runnable thread.

**`coroutine.resume(co [, val1, ...])`** — Resume coroutine execution. First call passes arguments to `f`. Subsequent calls pass values as results of `yield`. Returns `(true, results...)` on success or `(false, error)` on failure.

**`coroutine.running()`** — Returns the running thread and a boolean indicating if it is the main thread.

**`coroutine.status(co)`** — Returns `"suspended"`, `"running"`, `"normal"` (main thread), or `"dead"`.

**`coroutine.wrap(f)`** — Like `create`, but returns a callable function. Errors propagate instead of being caught.

**`coroutine.yield(...)`** — Suspend the running coroutine. Arguments become extra return values of `resume`.

## String Library and Patterns

Accessible as `string.*` (also available as metamethods on string userdata).

**`string.byte(s [, i [, j]])`** — Return numeric codes of characters s[i] through s[j]. Defaults to s[1] through s[#s].

**`string.char(...)`** — Create string from numeric codes.

**`string.dump(function [, strip])`** — Return a binary chunk string. If `strip` is true, debug info is omitted (smaller file).

**`string.find(s, pattern [, init [, plain]])`** — Find first match. Returns start and end indices, plus captures. If `plain` is true, treat pattern as literal string.

**`string.format(formatstring, ...)`** — Format string (like printf). Supports `%s`, `%d`, `%f`, `%x`, `%o`, `%c`, `%q`, `%p`, `%%`.

**`string.gmatch(s, pattern [, init])`** — Return an iterator that yields successive captures. If pattern has no captures, yields the whole match.

**`string.gsub(s, pattern, repl [, n])`** — Global substitution. Returns new string and number of substitutions. `repl` can be a string, table, or function.

**`string.len(s)`** — Length in bytes.

**`string.lower(s)` / `string.upper(s)`** — Case conversion (ASCII only).

**`string.match(s, pattern [, init])`** — Return captures from first match. If no captures, returns the whole match.

**`string.rep(s, n [, sep])`** — Return s repeated n times, optionally separated by `sep`.

**`string.reverse(s)`** — Reverse string byte-by-byte.

**`string.sub(s, i [, j])`** — Extract substring. Negative indices count from end.

### Patterns

Lua uses its own pattern syntax (not POSIX regex). Key elements:

**Character classes:**
- `.` — Any character
- `%a` — Letters | `%c` — Control | `%d` — Digits | `%g` — Printable (not space)
- `%l` — Lowercase | `%p` — Punctuation | `%s` — Space | `%u` — Uppercase
- `%w` — Alphanumeric | `%x` — Hex digit
- `%z` — Zero byte
- `%x` (any non-alphanumeric) — The character itself (escape magic chars)
- `[set]` — Union of classes. Ranges with `-`. Negate with `^`: `[^0-7]`
- `[^set]` — Complement of set

**Pattern items:**
- `c` — Single character class (matches one instance)
- `c-` — Optional (0 or 1)
- `c*` — Repetition (0 or more, maximal match)
- `c+` — One or more (maximal)
- `c.` — One or more (minimal/possessive)
- `cn` — Exactly n times
- `c[m-n]` — Between m and n times
- `%bxy` — Balanced chunks (matches text between x and y, properly nested)
- `(e)` — Capture
- `(e)` with `#` prefix: `#(e)` — Length of capture (5.4+)

**Captures:**
- `()` — Capture the matched substring
- `%1`, `%2`, ... — In replacement strings, refer to captures
- `%0` — Entire match
- Nested captures numbered by opening parenthesis order
- `(?` — Non-capturing group

### Pack/Unpack Binary Data

**`string.pack(fmt, v1, v2, ...)`** — Pack values into binary string.

**`string.unpack(fmt, s [, pos])`** — Unpack binary string. Returns values plus next position.

**`string.packsize(fmt)`** — Size of the packed string without actually packing.

**Format strings:**
- `<` — Little-endian (default) | `>` — Big-endian | `=` — Native
- Space — Padding | `x` — Zero byte
- `b`, `B` — Signed/unsigned char
- `h`, `H` — Signed/unsigned short
- `i`, `I` — Signed/unsigned int (with optional size: `i4`)
- `l`, `L` — Signed/unsigned long
- `j`, `J` — Signed/unsigned lua_Integer
- `n`, `N` — Signed/unsigned lua_Number
- `T` — Size of a type
- `z` — Zero-terminated string

## UTF-8 Library

Accessible as `utf8.*`.

**`utf8.char(...)`** — Create UTF-8 string from codepoints.

**`utf8.charpattern`** — Pattern `%C` matching a single UTF-8 character.

**`utf8.codes(s [, lax])`** — Iterator yielding byte positions and codepoints of successive characters.

**`utf8.codepoint(s [, i [, j [, lax]]])`** — Return codepoints of characters s[i] through s[j].

**`utf8.len(s [, i [, j]])`** — Number of UTF-8 characters (not bytes).

**`utf8.offset(s, n [, i])`** — Byte position of the nth character counting from position i. Negative n counts backward.

## Table Library

Accessible as `table.*`.

**`table.concat(list [, sep [, i [, j]]])`** — Concatenate elements list[i] through list[j] with separator. Defaults to 1 through #list.

**`table.create(nseq [, nrec])`** — Create a table with space for nseq sequential elements and nrec non-sequential fields. Pre-allocation optimization.

**`table.insert(list, [pos,] value)`** — Insert value at pos (default: end). Shifts elements. O(n) without pre-allocation.

**`table.move(a1, f, e, t [, a2])`** — Move elements from a1[f..e] to a2[t]. Default a2 = a1. Handles overlap correctly.

**`table.pack(...)`** — Pack all arguments into a table with `n` field holding the count. Preserves nils (unlike `{...}`).

**`table.remove(list [, pos])`** — Remove element at pos (default: last). Returns removed value. Shifts elements.

**`table.sort(list [, comp])`** — Sort in-place. `comp(a, b)` returns true if a should come before b. Not stable.

**`table.unpack(list [, i [, j]])`** — Unpack table elements as multiple return values. Default 1 through #list.

## Math Library

Accessible as `math.*`.

**Constants:**
- `math.pi` — π
- `math.huge` — Positive infinity
- `math.maxinteger` — Maximum integer value
- `math.mininteger` — Minimum integer value

**Basic functions:**
- `math.abs(x)` | `math.ceil(x)` | `math.floor(x)` | `math.modf(x)` (returns int, frac)
- `math.sqrt(x)` | `math.exp(x)` | `math.log(x [, base])`
- `math.min(x, ...)` | `math.max(x, ...)`
- `math.fmod(x, y)` — Remainder (sign follows x)

**Trigonometric:**
- `math.sin(x)` | `math.cos(x)` | `math.tan(x)`
- `math.asin(x)` | `math.acos(x)` | `math.atan(y [, x])`
- `math.deg(x)` | `math.rad(x)`

**Integer operations:**
- `math.tointeger(x)` — Convert to integer (nil if not representable).
- `math.type(x)` — Returns `"integer"`, `"float"`, or nil.
- `math.ult(m, n)` — Unsigned less-than comparison.

**Random numbers:**
- `math.random([m [, n]])` — No args: 0..1 float. One arg: 1..m integer. Two args: m..n integer range.
- `math.randomseed([x [, y]])` — Seed the random generator. Two seeds for better distribution.

**Floating-point decomposition:**
- `math.frexp(x)` — Returns mantissa and exponent (x = m × 2^e).
- `math.ldexp(m, e)` — Returns m × 2^e.

## I/O Library

Two models: simple (default input/output files) and explicit (file handles).

### Simple model

- `io.input([file])` — Set/get default input file. Accepts filename string or file handle.
- `io.output([file])` — Set/get default output file.
- `io.close([file])` — Close file (default output if no arg).
- `io.flush()` — Flush default output.
- `io.read(...)` — Read from default input. Formats: `"*n"` (number), `"*l"` (line, default), `"*L"` (line with possible empty), `"*a"` (whole file), `n` (n bytes).
- `io.write(...)` — Write to default output.
- `io.lines([filename, ...])` — Return iterator that reads lines. Closes file on completion.
- `io.tmpfile()` — Return a temporary file (auto-deleted on close).
- `io.type(obj)` — Returns `"file"` (open), `"closed file"`, or nil.
- `io.popen(prog [, mode])` — Execute program, return file handle for reading/writing its output/input.

### File methods

- `file:close()` — Close the file.
- `file:flush()` — Flush output.
- `file:lines(...)` — Iterator for lines from this file (does not close it).
- `file:read(...)` — Same formats as `io.read`.
- `file:write(...)` — Write to this file.
- `file:seek([whence [, offset]])` — Set/get file position. Whence: `"set"` (start), `"cur"` (current, default), `"end"` (end). Returns final position or nil on error.
- `file:setvbuf(mode [, size])` — Set buffering: `"full"`, `"line"`, `"no"`.

### Opening files

- `io.open(filename [, mode])` — Open file. Modes: `"r"` (read, default), `"w"` (write, truncate), `"a"` (append), `"r+"` (update), `"w+"` (update, truncate), `"a+"` (append update). Returns file handle on success, or `(nil, error_message, code)` on failure.

## OS Library

Accessible as `os.*`.

**`os.clock()`** — Return approximate CPU time used by the program in seconds.

**`os.date([format [, time]])`** — Format time. With `"!"` prefix: UTC. `%c` with no args → human-readable local time. Numeric formats (`%Y`, `%m`, `%d`, etc.) return numbers. Returns table with fields `year`, `month`, `day`, `hour`, `min`, `sec`, `isdst`, `wday`, `yday`, `time` when format is `"*t"` or `"!*t"`.

**`os.difftime(t2, t1)`** — Difference in seconds.

**`os.execute([command])`** — Execute shell command. Returns `(success, type, code)`.

**`os.exit([code [, close]])`** — Exit program. If `close` is true (default), close Lua state first.

**`os.getenv(varname)`** — Get environment variable.

**`os.remove(filename)`** — Delete file. Returns `(true)` or `(nil, error, code)`.

**`os.rename(old, new)`** — Rename file. Returns `(true)` or `(nil, error, code)`.

**`os.setlocale(locale [, category])`** — Set/get locale. Categories: `"all"`, `"collate"`, `"ctype"`, `"monetary"`, `"numeric"`, `"time"`.

**`os.time([table])`** — Return time in seconds. Table has fields `year`, `month`, `day`, `hour`, `min`, `sec`, `isdst`.

**`os.tmpname()`** — Return a temporary filename (caller responsible for cleanup and deletion).

## Debug Library

Accessible as `debug.*`. Most functions accept an optional `thread` parameter to operate on other coroutines.

**`debug.debug()`** — Enter interactive debug mode (runs input via `load`).

**`debug.gethook([thread])`** — Return current hook function, mask, and count.

**`debug.getinfo([thread,] f [, what])`** — Return info about a function or call frame. `f` can be a function or call level number. `what` string selects fields: `"S"` (source), `"l"` (line), `"u"` (upvalues), `"t"` (tail call), `"L"` (lines), `"f"` (function), `"r"` (registered lines), `"n"` (name).

**`debug.getlocal([thread,] f, local)`** — Get local variable by index. Returns `(name, value)`.

**`debug.getmetatable(value)`** — Get metatable of any value (not just tables).

**`debug.getregistry()`** — Return the registry table.

**`debug.getupvalue(f, up)`** — Get upvalue by index. Returns `(name, value)`.

**`debug.getuservalue(u, n)`** — Get nth uservalue of a full userdata.

**`debug.sethook([thread,] hook, mask [, count])`** — Set debug hook. Mask: `"c"` (calls), `"r"` (returns), `"l"` (lines). With count, hook fires every count instructions.

**`debug.setlocal([thread,] level, local, value)`** — Set local variable. Returns name or nil if out of range.

**`debug.setmetatable(value, table)`** — Set metatable of any value.

**`debug.setupvalue(f, up, value)`** — Set upvalue by index. Returns name or nil.

**`debug.setuservalue(udata, value, n)`** — Set nth uservalue of a full userdata.

**`debug.traceback([thread,] [message [, level]])`** — Generate a traceback string.

**`debug.upvalueid(f, n)`** — Get unique identifier for an upvalue (for comparison).

**`debug.upvaluejoin(f1, n1, f2, n2)`** — Make two upvalues share the same storage.

## Package Library

Accessible as `package.*`. Controls module loading.

- `package.config` — Directory separator (first char, usually `"\"`), path separator (`";"`), and Lua suffix.
- `package.path` — Search path for Lua modules (default from `LUA_PATH`). Uses `"?"` as placeholder for module name.
- `package.cpath` — Search path for C libraries. Uses `"?"` placeholder.
- `package.loaded[modname]` — Table of loaded modules. Set to `false` to prevent loading, or remove to force reload.
- `package.preload[modname]` — Table for predefining loaders before `require` searches paths.
- `package.searchers` — List of loader functions used by `require`.
- `package.loadlib(libname, funcname)` — Load a C library function. `funcname` is typically `"luaopen_<modulename>"`.
- `package.searchpath(name, path [, sep [, rep]])` — Search for name in path, replacing separators. Returns found path or nil.
