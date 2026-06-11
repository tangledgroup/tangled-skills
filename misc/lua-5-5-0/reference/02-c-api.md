# C API

## Contents
- The Stack
- C Closures
- Registry
- Error Handling in C
- Handling Yields in C
- Core API Functions
- Debug Interface

## The Stack

Lua uses a virtual stack to pass values between C and Lua. Each element represents a Lua value (nil, number, string, etc.). Every C callback receives its own independent stack.

**Indexing:**
- Positive: absolute position from bottom (1 = first pushed).
- Negative: offset from top (-1 = top, -2 = second from top).
- `lua_gettop(L)` returns the stack size (also the index of the top element).

**Pseudo-indices:** Special indices that do not represent actual stack elements but access specific Lua values:
- `LUA_REGISTRYINDEX` — Access to the registry table.
- `lua_upvalueindex(i)` — Access to the i-th upvalue of a C closure (1 = first).

**Stack size:** You are responsible for preventing overflow. Use `lua_checkstack(L, n)` to ensure room. The guaranteed minimum stack size is `LUA_MINSTACK` (20).

### Pushing values

| Function | Description |
|----------|-------------|
| `lua_pushnil(L)` | Push nil |
| `lua_pushboolean(L, b)` | Push boolean |
| `lua_pushinteger(L, n)` | Push integer |
| `lua_pushnumber(L, n)` | Push number (double) |
| `lua_pushstring(L, s)` | Push zero-terminated string (copies) |
| `lua_pushlstring(L, s, len)` | Push string with explicit length (allows embedded zeros) |
| `lua_pushvfstring(L, fmt, va)` | Push formatted string (like printf) |
| `lua_pushcclosure(L, fn, n)` | Push C function with n upvalues from stack |
| `lua_pushcfunction(L, fn)` | Push C function with no upvalues |
| `lua_pushlightuserdata(L, p)` | Push light userdata (C pointer) |
| `lua_pushthread(L)` | Push the thread as a value |
| `lua_pushvalue(L, idx)` | Copy stack element at idx |

### Converting values

| Function | Description |
|----------|-------------|
| `lua_toboolean(L, idx)` | Convert to boolean (nil = false) |
| `lua_tointeger(L, idx)` / `lua_tointegerx(L, idx, isnum)` | Convert to integer |
| `lua_tonumber(L, idx)` / `lua_tonumberx(L, idx, isnum)` | Convert to number |
| `lua_tolstring(L, idx, len)` | Convert to string (may coerce) |
| `lua_tocfunction(L, idx)` | Get C function pointer |
| `lua_touserdata(L, idx)` | Get userdata pointer (or NULL) |
| `lua_tothread(L, idx)` | Get thread state |
| `lua_topointer(L, idx)` | Get unique pointer for table/userdata/thread/function |

### Type checking

| Function | Description |
|----------|-------------|
| `lua_type(L, idx)` | Return type constant (LUA_TNIL, LUA_TBOOLEAN, etc.) |
| `lua_typename(L, t)` | Return type name string |
| `lua_is*` family | `lua_isnil`, `lua_isboolean`, `lua_isnumber`, `lua_isinteger`, `lua_isstring`, `lua_istable`, `lua_isfunction`, `lua_iscfunction`, `lua_isthread`, `lua_isuserdata`, `lua_islightuserdata` |
| `lua_isnone(L, idx)` / `lua_isnoneornil(L, idx)` | Check for out-of-range or nil |

### Stack manipulation

- `lua_settop(L, idx)` — Set stack top (positive = set size, negative = remove n elements)
- `lua_pushvalue(L, idx)` — Copy element
- `lua_rotate(L, idx, n)` — Rotate top n elements
- `lua_remove(L, idx)` — Remove element at idx
- `lua_insert(L, idx)` — Move top element to idx
- `lua_replace(L, idx)` — Pop top and set as element at idx
- `lua_copy(L, fromidx, toidx)` — Copy without popping
- `lua_pop(L, n)` — Convenience: `lua_settop(L, -(n+1))`
- `lua_checkstack(L, n)` — Ensure stack has room for n more elements

### Comparison and concatenation

- `lua_compare(L, idx1, idx2, op)` — Compare with `<`, `<=`, or `==`. Returns 1 if true, 0 otherwise.
- `lua_concat(L, n)` — Concatenate n values from stack, push result.
- `lua_len(L, idx)` — Push length of value (uses `__len` metamethod).

## C Closures

C functions can have upvalues (shared state) just like Lua closures. When pushing a C closure with `lua_pushcclosure(L, fn, n)`, the top n stack elements become the closure's upvalues.

Access upvalues from within the C function using `lua_upvalueindex(i)` (1-based). Upvalues are shared among all copies of the same closure.

```c
static int counter(lua_State *L) {
    lua_pushinteger(L, lua_tointeger(L, lua_upvalueindex(1)) + 1);
    lua_replace(L, lua_upvalueindex(1));  /* update upvalue */
    return 1;
}

/* Setup: push initial value, then create closure */
lua_pushinteger(L, 0);
lua_pushcclosure(L, counter, 1);
```

## Registry

The registry is a predefined table accessible at `LUA_REGISTRYINDEX`. Use it to store C-side data that needs global Lua accessibility.

- Integer keys: Reserved for Lua internal use.
- String keys: Available for user programs (use unique prefixes to avoid collisions).
- Pointer keys: Use `lua_rawgetp` / `lua_rawsetp` with pointer values. Ideal for associating data with C objects.

```c
void *key = &my_unique_key;
lua_rawgetp(L, LUA_REGISTRYINDEX, key);  /* retrieve */
lua_pushinteger(L, 42);
lua_rawsetp(L, LUA_REGISTRYINDEX, key);  /* store */
```

## Error Handling in C

When a C function calls Lua (via `lua_call`, `lua_load`, etc.), errors in Lua code propagate as C longjmp. Use protected calls to catch them.

**Unprotected:** `lua_call(L, nargs, nresults)` — Errors unwind the stack via longjmp.

**Protected:** `lua_pcall(L, nargs, nresults, errfunc)` — Catches errors. Returns a status code:
- `LUA_OK` (0) — Success
- `LUA_ERRRUN` — Runtime error
- `LUA_ERRSYNTAX` — Syntax error during lua_load
- `LUA_ERRMEM` — Memory allocation error
- `LUA_ERRERR` — Error while running the error handler

The `errfunc` index points to an error handler function on the stack. If 0, no handler (error message is the original error object). Use `lua_sethook` or push `debug.traceback` as the handler for stack traces.

**`lua_error(L)`** — Generates a Lua error. The error object must be on the stack top. Does not return.

**`lua_atpanic(L, panicfunc)`** — Set a panic function for unrecoverable errors (when no protected call is active).

## Handling Yields in C

C functions cannot yield directly unless called from a protected call context that allows yielding.

- `lua_yieldk(L, nresults, nkwargs, kont)` — Yield from C. `kont` is a continuation function called when the coroutine resumes.
- `lua_callk(L, nargs, nresults, ctx, kont)` — Call with continuation for yield recovery.
- `lua_pcallk(L, nargs, nresults, errfunc, ctx, kont)` — Protected call with continuation.

The continuation function receives the original `ctx` (C context) as an upvalue at `lua_upvalueindex(1)`, followed by any values passed to `coroutine.resume` after the yield results.

```c
static int cont(lua_State *L) {
    /* called when coroutine resumes after yield */
    void *ctx = lua_touserdata(L, lua_upvalueindex(1));
    /* resume processing */
    return nresults;
}

static int my_func(lua_State *L) {
    /* ... some work ... */
    lua_yieldk(L, 0, 0, &cont, ctx);
    return 0;  /* never reached directly */
}
```

Check `lua_isyieldable(L)` before attempting to yield.

## Core API Functions

### State management

- `lua_newstate(allocf, ud, seed)` — Create a new Lua state with custom allocator. Third parameter is hash seed for string hashing (new in 5.5, use `luaL_makeseed()` for a random seed).
- `lua_close(L)` — Close state, call GC metamethods, free memory.
- `lua_closethread(L, from)` — Close thread, run pending close metamethods. Returns status.
- `lua_newthread(L)` — Create a new coroutine (thread). Pushes it onto the stack.
- `lua_status(L)` — Get state/thread status.
- `lua_resetthread(L)` — Deprecated since 5.5; use `lua_closethread(L, NULL)`.
- `lua_setcstacklimit(L)` — Deprecated since 5.5; calls can be removed.

### Table operations

- `lua_createtable(L, narr, nrec)` — Create table with pre-allocated space for narr array slots and nrec record slots.
- `lua_newtable(L)` — Create empty table (shorthand for createtable with 0,0).
- `lua_geti(L, idx, i)` — Push `t[i]` where t is at idx.
- `lua_getfield(L, idx, k)` — Push `t[k]` (string key).
- `lua_gettable(L, idx)` — Pop key, push `t[key]` where t is at idx.
- `lua_seti(L, idx, n, v)` — Set `t[n] = v` (pop value from stack).
- `lua_setfield(L, idx, k)` — Pop value, set `t[k]`.
- `lua_settable(L, idx)` — Pop value then key, set `t[key] = value`.
- `lua_next(L, idx)` — Iterate table. Pushes key-value pair. Use with `lua_pushnil(L)` to start.

### Function calls

- `lua_call(L, nargs, nresults)` — Call function. Results replace function + args on stack.
- `lua_pcall(L, nargs, nresults, errfunc)` — Protected call.
- `lua_callk` / `lua_pcallk` — With continuation for yield recovery.
- `lua_load(L, reader, dt, name, mode)` — Load a chunk without running it. Pushes the resulting function.

### Arithmetic

- `lua_arith(L, op)` — Perform arithmetic: `LUA_OPADD`, `LUA_OPSUB`, `LUA_OPMUL`, `LUA_OPMOD`, `LUA_OPPOW`, `LUA_OPUNM`, `LUA_OPBAND`, `LUA_OPBOR`, `LUA_OPBXOR`, `LUA_OPSHL`, `LUA_OPSHR`.

### GC control from C

- `lua_gc(L, what, data)` — Control GC. Options: `LUA_GCSTOP`, `LUA_GCRESTART`, `LUA_GCCOUNT`, `LUA_GCCOUNTB`, `LUA_GCSTEP`, `LUA_SETPAUSE`, `LUA_SETSTEPMUL`, `LUA_GCINCREMENTAL`, `LUA_GCGENERATIONAL`.

### Userdata

- `lua_newuserdatauv(L, size, nuvalues)` — Allocate userdata of given size with nuvalues unnamed upvalues.
- `lua_getiuservalue(L, idx, n)` / `lua_setiuservalue(L, idx, n)` — Access numbered userdata values.

### String handling

- `lua_pushexternalstring(L, s, reserve)` — Push a string that Lua reserves memory for (for zero-copy patterns).
- `lua_stringtonumber(L, s)` — Convert string to number using current locale. Pushes result and returns new pointer.

## Debug Interface

The debug library provides hooks and introspection into running code.

### Hooks

`lua_sethook(L, hook, mask, count)` installs a C hook function called at specific events:
- `LUA_MASKCALL` / `LUA_MASKRET` — On function call/return.
- `LUA_MASKLINE` — On new line.
- `LUA_MASKCOUNT` — Every `count` instructions.

Hook receives `lua_Debug*` with event info. Use `lua_gethook(L)`, `lua_gethookcount(L)`, `lua_gethookmask(L)` to query current hook.

### lua_Debug structure

Fields available via `lua_getinfo(L, "what", &ar)`:
- `event` — Current hook event ('c', 'r', 'l', 't')
- `name`, `namewhat` — Function name and how it was found ("global", "local", "method", "field")
- `what` — "Lua", "C", "main", "tail"
- `src`, `short_src` — Source name
- `linedefined`, `lastlinedefined` — Definition line range
- `currentline` — Current execution line
- `nups`, `nparams` — Number of upvalues and parameters
- `isvararg` — Whether function accepts variable arguments
- `transfer` / `ntransfer` — For tail calls: values transferred

### Local variable access

- `lua_getlocal(L, ar, n)` — Get nth local variable. Pushes value, returns name.
- `lua_setlocal(L, ar, n)` — Set nth local variable. Pops value, returns name.

### Upvalue manipulation

- `lua_getupvalue(L, funcindex, n)` — Get nth upvalue of a closure.
- `lua_setupvalue(L, funcindex, n)` — Set nth upvalue.
- `lua_upvalueid(L, funcindex, n)` — Get unique identifier for an upvalue.
- `lua_upvaluejoin(L, func1, n1, func2, n2)` — Make two upvalues share the same storage.
