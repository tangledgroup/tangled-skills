# Build and Embedding

## Contents
- Building Lua
- Installation
- Source File Layout
- Customization via luaconf.h
- Embedding Lua in C
- Precompiled Chunks
- Lua Standalone

## Building Lua

Lua is distributed as source. It compiles with any ISO C compiler (also as C++).

**Unix-like platforms (Linux, macOS, BSD):**

```bash
cd lua-5.5.0
make           # auto-detect platform and build
make test      # verify build (prints version)
```

If auto-detection fails:

```bash
make help      # list supported platforms
make linux     # or: macosx, freebsd, solaris, posix, generic, c89, ios, mingw
```

**Build outputs** (in `src/`):
- `lua` — The interpreter
- `luac` — The compiler (produces precompiled chunks)
- `liblua.a` — The static library

## Installation

**System-wide:**

```bash
make install        # default prefix (usually /usr/local)
sudo make install   # if permissions required
make install INSTALL_TOP=/opt/lua  # custom prefix
```

**Local installation** (no root needed):

```bash
make local          # creates install/{bin,include,lib,man,share}
```

**Build and install in one step:**

```bash
make all install
make linux install
```

**Installed files:**
- `bin/`: `lua`, `luac`
- `include/`: `lua.h`, `luaconf.h`, `lualib.h`, `lauxlib.h`, `lua.hpp`
- `lib/`: `liblua.a`
- `man/man1/`: `lua.1`, `luac.1`

For running scripts only, you need just `bin/` and `man/`. For embedding in C/C++, you also need `include/` and `lib/`.

## Source File Layout

**Public headers:**
- `lua.h` — Core API (lua_State, stack operations, types)
- `lualib.h` — Standard library open functions
- `lauxlib.h` — Auxiliary library helpers
- `luaconf.h` — Configuration options
- `lua.hpp` — C++ wrapper with automatic state cleanup

**Core VM sources (liblua.a):**
- `lapi.c` — Core API implementation
- `lcode.c` — Code generator (bytecode)
- `lctype.c` — Character classification
- `ldebug.c` — Debug facilities
- `ldo.c` — Stack execution / doseq
- `ldump.c` — Binary chunk dumper
- `lfunc.c` — Function objects
- `lgc.c` — Garbage collector
- `llex.c` — Lexical analyzer
- `lmem.c` — Memory allocation
- `lobject.c` — Lua object operations
- `lopcodes.c` — Bytecode opcode definitions
- `lparser.c` — Parser
- `lstate.c` — State management
- `lstring.c` — String objects
- `ltable.c` — Table implementation
- `ltm.c` — Tag methods (metamethods)
- `lundump.c` — Binary chunk loader
- `lvm.c` — Virtual machine
- `lzio.c` — Stream I/O

**Standard library sources:**
- `lauxlib.c` — Auxiliary library
- `lbaselib.c` — Basic functions
- `lcorolib.c` — Coroutine library
- `ldblib.c` — Debug library
- `liolib.c` — I/O library
- `lmathlib.c` — Math library
- `loadlib.c` — Module loading (package)
- `loslib.c` — OS library
- `lstrlib.c` — String library
- `ltablib.c` — Table library
- `lutf8lib.c` — UTF-8 library
- `linit.c` — Library registration

**Stand-alone programs:**
- `lua.c` — Interpreter
- `luac.c` — Compiler

**To build a custom library subset**, create your project with only the needed `.c` files instead of using `liblua.a`.

## Customization via luaconf.h

Edit `src/luaconf.h` before building. Key options:

**Number types:**
- `LUA_32BITS` — Use 32-bit integers (default is 64-bit on capable platforms).
- `LUA_C89_NUMBERS` — Fall back to C89 number handling.

**Integer support:**
- `LUA_NO_INT64` — Disable 64-bit integer support (numbers are always double).

**GC tuning:**
- `LUAI_GCPAUSE` — Default GC pause (200 = 2x memory before restarting).
- `LUAI_GCMUL` — Default GC speed multiplier (200 = twice allocation speed).

**String interning:**
- `LUA_USE_LONG LONG` — Use long long for string hashing seed.

**I/O:**
- `LUA_32BITS` affects file I/O types.
- `luaconf.h` controls whether `os.remove`, `os.rename`, etc. are available.

**Other:**
- `LUA_MAXCAPTURES` — Maximum pattern captures (default 32).
- `LUAI_MAXSTACK` — Maximum Lua stack size per thread.
- `LUA_IDSIZE` — Size of buffer for function/source names in debug info.

## Embedding Lua in C

**Minimal embedding:**

```c
#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

int main(void) {
    /* Create state */
    lua_State *L = luaL_newstate();

    /* Load standard libraries */
    luaL_openlibs(L);

    /* Run Lua code */
    if (luaL_dostring(L, "print('Hello from embedded Lua!')") != LUA_OK) {
        fprintf(stderr, "Error: %s\n", lua_tostring(L, -1));
        lua_pop(L, 1);
    }

    /* Clean up */
    lua_close(L);
    return 0;
}
```

Compile: `gcc -o app app.c -llua -lm`

**Selective library loading:**

Instead of `luaL_openlibs()`, load only what you need:

```c
luaL_requiref(L, LUA_GNAME, luaopen_base, 1);           /* _G */
luaL_requiref(L, LUA_TABLIBNAME, luaopen_table, 1);     /* table */
luaL_requiref(L, LUA_STRLIBNAME, luaopen_string, 1);    /* string */
/* omit io, os, debug, etc. for sandboxing */
```

Or use `luaL_openselectedlibs()` (new in 5.5) with bitmasks:

```c
int libs = LUA_BASELIB | LUA_STRLIB | LUA_TABLIB;
luaL_openselectedlibs(L, libs, 0);  /* load libs, no preloads */
```

**Calling Lua from C:**

```c
/* Call a Lua function by name */
lua_getglobal(L, "myFunction");
lua_pushinteger(L, 42);
lua_pushstring(L, "hello");
if (lua_pcall(L, 2, 1, 0) != LUA_OK) {
    fprintf(stderr, "Error: %s\n", lua_tostring(L, -1));
}
/* Result is on stack top */
int result = (int)lua_tointeger(L, -1);
lua_pop(L, 1);
```

**Registering C functions:**

```c
static int lua_add(lua_State *L) {
    double a = luaL_checknumber(L, 1);
    double b = luaL_checknumber(L, 2);
    lua_pushnumber(L, a + b);
    return 1;  /* number of results */
}

/* Register it */
lua_pushcfunction(L, lua_add);
lua_setglobal(L, "add");
```

**C++ embedding with lua.hpp:**

```cpp
#include <lua.hpp>

int main() {
    {
        lua_State* L = luaL_newstate();
        luaL_openlibs(L);
        // ... use Lua ...
        /* lua_close called automatically by LuaState destructor */
    }
    return 0;
}
```

## Precompiled Chunks

Compile Lua source to binary for faster loading:

```bash
luac -o script.lc script.lua
```

Load in Lua: `loadfile("script.lc")` or `dofile("script.lc")`.

From C, use `luaL_loadfilex` with mode `"b"` (binary) or `"bt"` (both).

**Dump from C:**

```c
/* Function must be on stack top */
lua_dump(L, writer, data, 0);  /* strip_debug = 0 */
```

Precompiled chunks are **not** compatible across Lua versions. Always recompile when changing Lua versions.

## Lua Standalone

The `lua` interpreter runs scripts and provides an interactive shell.

```bash
lua                    # Interactive mode
lua script.lua         # Run a file
lua -e "print('hi')"  # Execute code string
lua -i script.lua     # Run file, then interactive
```

**Options:**
- `-e stat` — Execute statement `stat`
- `-l name` — Require library `name` before running
- `-v` / `-V` — Version / version + copyright
- `-E` — Ignore environment variables (LUA_INIT, LUA_PATH, etc.)
- `-W` — Warnings on
- `--` — Stop processing options
- `-` — Read from stdin, stop processing options

**Environment variables:**
- `LUA_INIT_5_5` — Code to run at startup (or `@filename` for a file)
- `LUA_PATH_5_5` — Search path for Lua modules
- `LUA_CPATH_5_5` — Search path for C libraries
