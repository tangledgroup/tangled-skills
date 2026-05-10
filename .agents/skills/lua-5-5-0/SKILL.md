---
name: lua-5-5-0
description: Lightweight embeddable scripting language with a small C footprint, dynamic typing via tables, coroutines, and a powerful C API for embedding. Use when writing Lua scripts, embedding Lua in C/C++ applications, creating DSLs or configuration languages, building game scripting systems, or working with Lua-based ecosystems (Neovim, OpenResty, LÖVE2D).
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - lua
  - scripting
  - embeddable
  - c-api
  - dynamic-language
category: language-runtime
external_references:
  - https://www.lua.org/manual/5.5/
  - https://www.lua.org/source/5.5/
  - https://github.com/lua/lua
---

# Lua 5.5.0

## Overview

Lua is a powerful, efficient, lightweight, embeddable scripting language developed by PUC-Rio. It uses garbage-collected dynamic typing, first-class functions with lexical scoping and closures, and provides coroutines for cooperative multitasking. Lua is implemented in clean ISO C and compiles unmodified on all platforms with an ISO C compiler (also as C++).

The single core data structure is the **table** — an associative array supporting both array-like (integer keys) and map-like (arbitrary keys) access, with metatables for operator overloading and behavior customization.

## When to Use

- Writing Lua scripts or modules for existing Lua-based systems
- Embedding Lua as a scripting engine in C/C++ applications
- Creating domain-specific languages or configuration formats
- Building game scripting, plugin systems, or runtime extensibility
- Working with Neovim plugins, OpenResty/Nginx scripting, or LÖVE2D games
- Understanding Lua 5.5 incompatibilities when migrating from 5.4

## Core Concepts

**Types:** nil, boolean, number (doubles by default), integer (64-bit by default), string (immutable, multi-byte), table, function (first-class closures), thread (coroutines), userdata (full and light).

**Tables as the sole data structure:** Arrays (`t[1]`), maps (`t["key"]`), objects (with metatables), modules (returned tables), records. Use `table.create(nseq, nrec)` to pre-allocate slots.

**Metatables and metamethods:** Customize behavior via `__index`, `__newindex`, `__add`, `__call`, `__gc`, `__close`, etc. Lua uses raw access (`rawget`) when querying metatables, so the metatable's own `__index` is not triggered during lookup.

**Garbage collection:** Two modes — incremental (default, marks and sweeps in small steps) and generational (collects young objects more frequently). Tune via `collectgarbage("param", value)` or `collectgarbage("setpause"`/`"setstepmul")`. Weak tables (`__mode` = "k", "v", or "kv") allow keys or values to be collected.

**Coroutines:** Independent threads of execution that yield explicitly via `coroutine.yield()`. Create with `coroutine.create(f)`, run with `coroutine.resume(co, ...)`, wrap into callable with `coroutine.wrap(f)`. Check status with `coroutine.status(co)`.

**To-be-closed variables:** Declare with `<·*close*>` annotation. The value's `__close` metamethod is called when the variable goes out of scope (normal exit, break, return, or error). Equivalent to try/finally for resource cleanup.

## Usage Examples

**Running a script:**

```bash
lua script.lua arg1 arg2
```

**Minimal Lua program:**

```lua
-- hello.lua
local name = arg[1] or "world"
print("Hello, " .. name .. "!")
```

**Table as object with metatable:**

```lua
local Vector = {}
Vector.__index = Vector

function Vector.new(x, y)
    return setmetatable({x = x, y = y}, Vector)
end

function Vector:__add(other)
    return Vector.new(self.x + other.x, self.y + other.y)
end

local a = Vector.new(1, 2)
local b = Vector.new(3, 4)
print(a.x + b.x) -- via __add: 4
```

**Pattern matching (Lua uses its own pattern syntax, not regex):**

```lua
local str = "price: $42.50"
local price = string.match(str, "%$(%d+%.?%d*)")
print(price) -- "42.50"
```

**To-be-closed variable for resource management:**

```lua
local f = io.open("data.txt", "<·*close*>")
-- f is automatically closed when it goes out of scope
for line in f:lines() do
    print(line)
end
```

**Embedding Lua in C (minimal):**

```c
#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

int main(void) {
    lua_State *L = luaL_newstate();
    luaL_openlibs(L);
    luaL_dostring(L, "print('Hello from C!')");
    lua_close(L);
    return 0;
}
```

Compile: `gcc -o embed embed.c -llua -lm`

## Advanced Topics

**Language Reference**: Types, syntax, statements, expressions, operators, metamethods, garbage collection, coroutines → [Language Reference](reference/01-language-reference.md)

**C API**: Virtual stack, C closures, registry, error handling, yielding from C, all lua_* functions → [C API](reference/02-c-api.md)

**Auxiliary Library**: luaL_* helper functions for argument checking, library registration, chunk loading, string buffers, references → [Auxiliary Library](reference/03-auxiliary-library.md)

**Standard Libraries**: Basic, coroutine, string (with patterns), utf8, table, math, io, os, debug, package → [Standard Libraries](reference/04-standard-libraries.md)

**Build and Embedding**: Building from source, installation, luaconf.h customization, embedding patterns, precompiled chunks → [Build and Embedding](reference/05-build-and-embedding.md)
