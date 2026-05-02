# Auxiliary Library (lauxlib.h)

## Contents
- Argument Checking
- Library Registration
- Metatable Management
- Chunk Loading
- String Buffers
- Reference System
- Error Utilities
- Miscellaneous Helpers

The auxiliary library (`lauxlib.h`) provides convenience functions built on top of the core C API. It simplifies common patterns: argument validation, library registration, chunk loading, and error reporting.

## Argument Checking

When writing C functions called from Lua, use these to validate and extract arguments:

- `luaL_checkany(L, n)` — Ensure argument n exists (any type).
- `luaL_checktype(L, n, t)` — Ensure argument n has specific type.
- `luaL_checkinteger(L, n)` — Get integer from argument n. Error if missing or wrong type.
- `luaL_checknumber(L, n)` — Get number from argument n.
- `luaL_checklstring(L, n, l)` — Get string from argument n. Optionally returns length via `l`.
- `luaL_checkstring(L, n)` — Same as checklstring with no length output.
- `luaL_checkoption(L, n, def, options)` — Check argument against list of string options. Returns option index. Useful for enum-like arguments.
- `luaL_checkudata(L, n, tname)` — Get userdata of specific metatable type. Errors if wrong type or nil.

**Optional arguments:**

- `luaL_optinteger(L, n, def)` — Optional integer with default.
- `luaL_optnumber(L, n, def)` — Optional number with default.
- `luaL_optlstring(L, n, def, l)` — Optional string with default.
- `luaL_optstring(L, n, def)` — Optional string (no length).

**Error reporting:**

- `luaL_argerror(L, n, extramsg)` — Generate argument error for parameter n. Does not return.
- `luaL_argcheck(L, cond, n, extramsg)` — Assert condition; if false, calls argerror.
- `luaL_argexpected(L, n, what, tname)` — Report that argument n expected type `what`.

## Library Registration

Define libraries as arrays of `luaL_Reg` structs and register them:

```c
typedef struct luaL_Reg {
    const char *name;
    lua_CFunction func;
} luaL_Reg;
```

**`luaL_setfuncs(L, l, n)`** — Register all functions in array `l`. Pushes the library table. `n` is the number of upvalues to prepend to each function (taken from stack top). Replaces existing functions (unlike older `luaL_register`).

**`luaL_newlib(L, l)`** — Convenience: create library table with `luaL_newlibtable`, then register with `luaL_setfuncs(L, l, 0)`.

**`luaL_openselectedlibs(L, load, preload)`** — Open selected standard libraries into state `L`. `load` and `preload` are bitmasks controlling which libraries to load (e.g., `LUA_STRLIB`). New in 5.5, alternative to `luaL_openlibs()` for selective loading with finer control.

**`luaL_newlibtable(L, l)`** — Create a library table pre-sized based on the `luaL_Reg` array.

**Example:**

```c
static const luaL_Reg mylib[] = {
    {"add", mylib_add},
    {"sub", mylib_sub},
    {NULL, NULL}  /* sentinel */
};

int luaopen_mylib(lua_State *L) {
    luaL_newlib(L, mylib);
    return 1;
}
```

## Metatable Management

- `luaL_newmetatable(L, tname)` — Create a new metatable for type `tname`. Stores it in the registry under `tname`. Returns 1 if created, 0 if already exists (pushes existing).
- `luaL_getmetatable(L, tname)` — Get metatable from registry. Pushes it.
- `luaL_setmetatable(L, tname)` — Pop a table from stack and set it as the metatable for `tname` in the registry.
- `luaL_testudata(L, n, tname)` — Check that stack position n is a userdata with the correct metatable. Returns pointer or NULL.
- `luaL_checkudata(L, n, tname)` — Like testudata but generates an error if check fails.
- `luaL_tolstring(L, idx, len)` — Call `__tostring` metamethod if available, otherwise return a default description. Pushes result string.
- `luaL_callmeta(L, objidx, op)` — Call metamethod `op` (e.g., "__add") on value at `objidx`. Returns 1 if metamethod exists and was called, 0 otherwise.
- `luaL_getmetafield(L, objidx, event)` — Check if value at `objidx` has a metamethod for `event`, push it, and call it. Returns 1 if found, 0 otherwise.

## Chunk Loading

Load and optionally execute Lua code from various sources:

- `luaL_loadbufferx(L, buff, size, name, mode)` — Load a string buffer as a chunk. `mode` controls execution permissions ("b" = binary allowed, "t" = text allowed, "f" = allow loadlib). Pushes the compiled function.
- `luaL_loadfilex(L, filename, mode)` — Load and compile a file. Same mode semantics.
- `luaL_loadbuffer(L, buff, size, name)` — Deprecated alias for `loadbufferx` with "bt" mode.
- `luaL_loadfile(L, filename)` — Deprecated alias for `loadfilex` with "bt" mode.
- `luaL_loadstring(L, s)` — Load a zero-terminated string (shorthand for loadbufferx with "bt" mode).

**Execute directly:**

- `luaL_dostring(L, s)` — Load and run a string. Results left on stack.
- `luaL_dofile(L, filename)` — Load and run a file.

**Example:**

```c
if (luaL_loadfilex(L, "script.lua", "bt") != LUA_OK) {
    luaLError(L, "load error: %s", lua_tostring(L, -1));
}
lua_call(L, 0, LUA_MULTRET);
```

## String Buffers

The buffer API (`luaL_Buffer`) builds strings incrementally without repeated reallocations:

- `luaL_buffinit(L, B)` — Initialize buffer.
- `luaL_buffinitsize(L, B, size)` — Initialize with pre-allocated size hint.
- `luaL_addstring(B, s)` — Add zero-terminated string.
- `luaL_addlstring(B, s, len)` — Add string with length.
- `luaL_addvalue(B)` — Add value from stack top (pop it).
- `luaL_addgsub(B, s, p, r)` — Like `luaL_gsub` but adds result directly to buffer.
- `luaL_addchar(B, c)` — Add single character.
- `luaL_addsize(B, n)` — Mark that n bytes were added directly to the buffer area.
- `luaL_prepbuffer(B)` / `luaL_prepbuffsize(B, size)` — Get pointer to pre-allocated space.
- `luaL_pushresult(B)` / `luaL_pushresultsize(B, n)` — Push final string onto stack.
- `luaL_bufflen(B)` — Current buffer length.
- `luaL_buffsub(B, n)` — Adjust buffer size to n (trim or shrink).
- `luaL_buffaddr(B)` — Address of buffer content.

**Pattern for writing directly into the buffer:**

```c
char *b = luaL_prepbuffsize(B, needed);
int n = my_function_that_fills_buffer(b, needed);
luaL_addsize(B, n);
luaL_pushresult(B);
```

## Reference System

Persist Lua values across API calls by creating integer references in a table (typically the registry or a metatable):

- `luaL_ref(L, tindex)` — Pop value from stack, store in table at `tindex`, return unique integer reference. Returns `LUA_NOREF` (-1) if value is nil/false.
- `luaL_unref(L, tindex, ref)` — Remove reference from table. No effect if ref is `LUA_NOREF`.

**Usage:**

```c
/* Store a value */
int ref = luaL_ref(L, LUA_REGISTRYINDEX);

/* Later: retrieve it */
lua_rawgeti(L, LUA_REGISTRYINDEX, ref);

/* When done: release */
luaL_unref(L, LUA_REGISTRYINDEX, ref);
```

## Error Utilities

- `luaL_error(L, fmt, ...)` — Generate error with formatted message. Does not return. Equivalent to `lua_pushfstring` + `lua_error`.
- `luaL_where(L, lvl)` — Push a string with source location info (file:line) for error messages.
- `luaL_traceback(L, L1, msg, level)` — Build a traceback string for state `L1`. Useful as an error handler in `lua_pcall`.
- `luaL_typeerror(L, n, tname)` — Generate error saying argument n has wrong type (expected `tname`).
- `luaL_typename(L, idx)` — Push the type name of value at idx as a string.

## Miscellaneous Helpers

- `luaL_gsub(L, s, pattern, replace)` — Replace all occurrences of `pattern` in `s` with `replace`. Pushes result. Simple string replacement (not pattern-based).
- `luaL_fileresult(L, stat, filename)` — Push `(true, handle)` or `(nil, error, code)` for file operations.
- `luaL_execresult(L, stat)` — Push `(true)` or `(nil, error)` for execution results.
- `luaL_checkversion(L)` — Verify the Lua interpreter version matches the auxiliary library version (new in 5.5). Raises error on mismatch.
- `luaL_getsubtable(L, idx, name)` — Get field from table, creating it if it doesn't exist. Pushes the subtable.
- `luaL_requiref(L, libname, openfunc, isglobal)` — Load library with caching in `package.loaded`. `openfunc` creates the library.
- `luaL_len(L, idx)` — Get length of value (uses `__len`).
- `luaL_pushfail(L)` — Push the special "fail" pseudo-constant.
- `luaL_makeseed(L)` — Push a random seed for hashing (for `lua_newstate`).
- `luaL_newstate()` — Create a new Lua state using `luaL_alloc` as the allocator and `luaL_makeseed()` for the hash seed.
- `luaL_alloc(L, ud, obj, osize, nsize)` — Realloc function compatible with `lua_Alloc`.
- `luaL_checkstack(L, n, msg)` — Ensure stack has room for n more elements. Raises error with msg if not.
