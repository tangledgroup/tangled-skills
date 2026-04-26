---
name: tinypy-1-1-0
description: A minimalist Python implementation in ~64k of code featuring a fully bootstrapped parser and bytecode compiler written in tinypy itself, a Lua-esque virtual machine with incremental garbage collection written in C, and an easy C API for embedding. Supports a decent subset of Python including classes, single inheritance, variable/keyword arguments, strings, lists, dicts, numbers, modules, list comprehensions, exceptions with full traceback, and some builtins. Cross-platform (Windows/Linux/macOS). Use when building embedded scripting engines, studying VM internals, bootstrapping toolchains, or needing a tiny Python-compatible runtime for games and constrained environments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.1.0"
tags:
  - python
  - vm
  - embedding
  - scripting
  - minimal
  - bytecode
  - garbage-collection
  - bootstrap
category: language-runtime
external_references:
  - http://www.tinypy.org/
  - http://www.philhassey.com/blog/category/tinypy/
  - http://www.tinypy.org/community.html
  - https://github.com/philhassey/tinypy/blob/wiki/Index.md
  - https://github.com/philhassey/tinypy/tree/1.1
---

# TinyPy 1.1

## Overview

TinyPy is a minimalist implementation of Python in approximately 64k of code. Created by Phil Hassey and released under the MIT license, it features:

- **Parser and bytecode compiler written in tinypy** — fully bootstrapped
- **Lua-esque virtual machine with garbage collection** written in C (stackless sans Stackless features)
- **Cross-platform** — runs under Windows, Linux, and macOS
- **A fairly decent subset of Python:**
  - Classes and single inheritance
  - Functions with variable or keyword arguments
  - Strings, lists, dicts, numbers
  - Modules, list comprehensions
  - Exceptions with full traceback
  - Some builtins
- **Easy C API** for building custom modules
- MIT licensed — static compile it and its modules

The project was originally described as "Lua for people who like Python" and "batteries not (yet) included."

## When to Use

- Embedding a tiny Python-compatible scripting engine in games or applications
- Studying virtual machine internals, bytecode compilation, and garbage collection
- Bootstrapping toolchains where the compiler is written in the language itself
- Constrained environments where minimal footprint matters
- Educational purposes — understanding tokenizer, parser, encoder, and VM architecture
- Building custom C modules with a simple C API

## Core Concepts

### Architecture

TinyPy has two main components:

1. **C runtime** — The virtual machine, garbage collector, built-in operations, and object types written in C (~64k of code)
2. **Python compiler** — The tokenizer, parser (TDOP), and bytecode encoder written in tinypy itself

### Bootstrapping Process

The build process is fully bootstrapped:

1. Python runs `setup.py` to compile the initial C VM
2. The VM loads Python source files (`tokenize.py`, `parse.py`, `encode.py`, `py2bc.py`)
3. These are compiled to bytecode (`.tpc` files) and embedded into the binary
4. The resulting binary can then run any tinypy script independently

### Object Model

Every object in tinypy is a `tp_obj` union with a type field:

- **TP_NONE** — None value
- **TP_NUMBER** — Double-precision floating point (`double tp_num`)
- **TP_STRING** — Character string with length
- **TP_DICT** — Hash map (used for dicts, classes, and objects)
- **TP_LIST** — Dynamic array
- **TP_FNC** — Function (C or tinypy)
- **TP_DATA** — Custom data pointer with magic number

In tinypy, `dict == object` — meaning `a.x == a['x']`. Classes and instantiated objects are special dictionaries with "meta" dictionaries for inheritance.

### Meta System

Instead of Python-style `__get__` descriptors, tinypy uses a Lua-like meta system:

```python
class MetaX:
    def __get__(self, k): return "OK"
class X:
    def __init__(self): setmeta(self, MetaX)
```

When dictionary attributes are accessed but not present, they are looked up in the meta dictionary. This also enables dynamic class changes at runtime (like Python's `x.__class__ = B`).

## Installation / Setup

### Dependencies

- Python (only for bootstrapping)
- GCC (or Visual Studio 2005/2008 on Windows)
- SDL (optional, for the pygame module)

### Building

```bash
# Linux with pygame support
python setup.py linux pygame
./build/tinypy examples/julia.py

# Run a script
./build/tinypy your-program-goes-here.py
```

The `setup.py` script handles the full bootstrapping process. On Windows, Visual Studio 2005/2008 support was added in version 1.1 by Krzysztof Kowalczyk.

### Size Notes

The "64k" claim is approximate. Running `python mk64k.py` compresses the source by converting 4 spaces to tabs, removing blank lines and comments, and stripping namespacing prefixes (e.g., `tp_print` becomes `print`). The compiled binary can be compressed below 64k with UPX.

## Usage Examples

### Running a Julia Fractal

The included `examples/julia.py` demonstrates tinypy's capabilities:

```python
import pygame
if '.' in str(1.0):
    import pygame.locals

SW, SH = 120, 120

def julia(s, ca, cb):
    pal = [((min(255,v)), (min(255,v*3/2)), (min(255,v*2))) for v in range(0,256)]
    for y in range(0, SH):
        for x in range(0, SW):
            i = 0
            a = ((float(x)/SW) * 4.0 - 2.0)
            b = ((float(y)/SH) * 4.0 - 2.0)
            while i < 15 and (a*a) + (b*b) < 4.0:
                na = (a*a) - (b*b) + ca
                nb = (2.0*a*b) + cb
                a = na
                b = nb
                i = i + 1
            s.set_at((x, y), pal[i*16])

def main():
    pygame.init()
    s = pygame.display.set_mode((SW, SH), 0, 32)
    _quit = False
    while not _quit:
        for e in pygame.event.get():
            if e.type in (pygame.locals.QUIT, pygame.locals.KEYDOWN):
                _quit = True
        x, y = pygame.mouse.get_pos()
        ca = ((float(x)/SW) * 2.0 - 1.0)
        cb = ((float(y)/SH) * 2.0 - 1.0)
        julia(s, ca, cb)
        pygame.display.flip()

if __name__ == '__main__':
    main()
```

### Embedding TinyPy in C

```c
#include "tinypy/tp.h"

int main(int argc, char *argv[]) {
    tp_vm *tp = tp_init(argc, argv);
    /* Call a tinypy function named "foo" with string "hello" */
    tp_call(tp,
        tp_get(tp, tp->builtins, tp_string("foo")),
        tp_params_v(tp, 1, tp_string("hello")));
    tp_deinit(tp);
    return 0;
}
```

### Writing a C Module

```c
#include "tinypy/tp.h"

tp_obj my_add(TP) {
    tp_obj a = TP_OBJ();  /* First parameter */
    tp_obj b = TP_OBJ();  /* Second parameter */
    return tp_number(a.number.val + b.number.val);
}

/* Register the function in builtins */
void init_mymodule(TP) {
    tp_set(tp, tp->builtins, tp_string("my_add"),
           tp_fnc(tp, my_add));
}
```

## Advanced Topics

**C API Reference**: Complete reference for all C functions, macros, and data structures → [C API Reference](reference/01-c-api-reference.md)

**Bytecode and VM Internals**: Instructions, frames, registers, and execution model → [Bytecode and VM Internals](reference/02-bytecode-and-vm-internals.md)

**Garbage Collection**: Incremental mark-and-sweep implementation details → [Garbage Collection](reference/03-garbage-collection.md)

**Compiler Pipeline**: Tokenizer, TDOP parser, and bytecode encoder → [Compiler Pipeline](reference/04-compiler-pipeline.md)

**Built-in Functions**: All tinypy builtins with descriptions → [Built-in Functions](reference/05-built-in-functions.md)

**Python Subset Reference**: What Python features are supported and what is not → [Python Subset Reference](reference/06-python-subset-reference.md)
