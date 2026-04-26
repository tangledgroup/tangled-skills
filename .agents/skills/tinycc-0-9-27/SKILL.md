---
name: tinycc-0-9-27
description: Complete toolkit for TinyCC 0.9.27, a small hyper-fast C compiler that generates native x86/x86_64/ARM code directly without an external assembler or linker. Use when compiling C code extremely fast, creating C scripts with shebangs, using libtcc for dynamic code generation at runtime, performing memory/bounds checking during development, building rescue disk toolchains, or cross-compiling for ARM and TMS320C67xx targets.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.9.27"
tags:
  - c-compiler
  - code-generation
  - dynamic-compilation
  - x86
  - arm
  - embedded
category: compiler
external_references:
  - https://www.bellard.org/tcc/
  - https://www.bellard.org/tcc/tcc-doc.html
  - https://github.com/TinyCC/tinycc/tree/release_0_9_27
---

# TinyCC 0.9.27

## Overview

TinyCC (TCC) is a small but hyper-fast C compiler created by Fabrice Bellard. Unlike GCC or Clang, TCC is self-relying: it includes a full C preprocessor, compiler, assembler, and linker in a single executable of about 100KB for x86. It generates native machine code directly — no bytecode, no intermediate assembly files.

TCC compiles roughly 7-9 times faster than `gcc -O0`. For large projects this speed can make Makefiles unnecessary, as recompilation is nearly instant. It supports ANSI C, most ISO C99 features, many GNU C extensions including inline assembly, and optional memory/bounds checking.

Key capabilities:

- **C scripting** — add `#!/usr/local/bin/tcc -run` as a shebang and execute C code directly like a Python or Perl script
- **libtcc** — use TCC as a backend for dynamic code generation at runtime from C strings
- **Bounds checking** — optional `-b` flag catches out-of-bounds array access, freed memory access, double-free, and buffer overflows
- **Cross-compilation** — supports i386, x86_64, ARM (arm-tcc), ARM64 (aarch64), and TMS320C67xx targets
- **Self-hosting** — TCC can compile itself

## When to Use

- Compiling C code where build speed matters (rapid iteration, scripting)
- Creating C scripts that run directly from the command line with `tcc -run`
- Dynamic code generation at runtime via libtcc (embedding a C compiler in an application)
- Building rescue disks or minimal environments where a ~100KB compiler is needed
- Debugging memory issues with built-in bounds checking (`-b` flag)
- Cross-compiling to ARM or TMS320C67xx from x86 hosts
- Generating standalone executables without needing gcc, as, or ld installed

## Core Concepts

**Single-pass compilation:** TCC generates linked binary code in one pass. It is register-based with expression-level optimization only — no intermediate representation beyond the value stack. On x86, three temporary registers are used; additional values spill to the stack.

**Self-contained toolchain:** No external assembler or linker needed. TCC produces ELF object files, executables, and shared libraries directly. On Windows it generates PE-i386 EXE and DLL files.

**C scripts:** By placing `#!/usr/local/bin/tcc -run` at the top of a `.c` file and making it executable, C code runs like any shell script. Compilation is fast enough that the overhead is negligible.

**libtcc API:** The `libtcc` library exposes TCC as a programmable backend. You create a `TCCState`, compile C source strings or files, relocate the code, and call generated functions by symbol name — all at runtime.

**Bounds checking:** With `-b`, TCC inserts runtime checks for array bounds, pointer validity, freed memory access, and double-free. Checked and unchecked code can be mixed freely. Pointer size is unchanged.

## Installation / Setup

Build from source using the standard autotools workflow:

```bash
./configure
make
make test
sudo make install
```

For macOS and FreeBSD, use `gmake` instead of `make`. The default install prefix is `/usr/local/bin`. Use `./configure --help` for configuration options.

`makeinfo` must be installed to build the documentation. For Windows, see the `tcc-win32.txt` file in the distribution.

## Usage Examples

**Compile and run directly:**

```bash
tcc -run hello.c
```

**Compile with arguments passed to main():**

```bash
tcc -run fib.c 10
```

**Generate an executable:**

```bash
tcc -o myprog a.c b.c
```

**Compile to object file only:**

```bash
tcc -c a.c
```

**C script with shebang:**

```c
#!/usr/local/bin/tcc -run
#include <stdio.h>

int main()
{
    printf("Hello World\n");
    return 0;
}
```

Make executable with `chmod +x script.c` and run directly: `./script.c`.

**C script with library links:**

```c
#!/usr/local/bin/tcc -run -L/usr/X11R6/lib -lX11
#include <X11/Xlib.h>
int main() { /* X11 code */ }
```

**Read from stdin:**

```bash
echo 'main(){puts("hello");}' | tcc -run -
```

**Compile with bounds checking:**

```bash
tcc -b -run test.c
```

**libtcc — dynamic compilation at runtime:**

```c
#include <stdlib.h>
#include <stdio.h>
#include "libtcc.h"

char program[] =
    "#include <tcclib.h>\n"
    "int fib(int n) {\n"
    "    if (n <= 2) return 1;\n"
    "    return fib(n-1) + fib(n-2);\n"
    "}\n"
    "int main() {\n"
    "    printf(\"fib(10) = %d\\n\", fib(10));\n"
    "    return 0;\n"
    "}\n";

int main(int argc, char **argv)
{
    TCCState *s = tcc_new();
    if (!s) { fprintf(stderr, "Could not create tcc state\n"); exit(1); }

    tcc_set_output_type(s, TCC_OUTPUT_MEMORY);

    if (tcc_compile_string(s, program) == -1)
        return 1;

    if (tcc_relocate(s, TCC_RELOCATE_AUTO) < 0)
        return 1;

    int (*entry)(int, char **) = tcc_get_symbol(s, "main");
    if (entry)
        entry(argc, argv);

    tcc_delete(s);
    return 0;
}
```

**libtcc — inject symbols into compiled code:**

```c
#include "libtcc.h"

int add(int a, int b) { return a + b; }

char program[] =
    "#include <tcclib.h>\n"
    "extern int add(int, int);\n"
    "int main() {\n"
    "    printf(\"add(3,4) = %d\\n\", add(3, 4));\n"
    "    return 0;\n"
    "}\n";

int main()
{
    TCCState *s = tcc_new();
    tcc_set_output_type(s, TCC_OUTPUT_MEMORY);
    tcc_compile_string(s, program);
    tcc_add_symbol(s, "add", add);
    tcc_relocate(s, TCC_RELOCATE_AUTO);

    int (*fn)(void) = tcc_get_symbol(s, "main");
    fn();

    tcc_delete(s);
    return 0;
}
```

## Advanced Topics

**Command-Line Reference**: All TCC options including preprocessor, compilation flags, linker options, debugger options, and target-specific flags → See [Command-Line Reference](reference/01-command-line-reference.md)

**C Language Support**: ANSI C, ISO C99 extensions, GNU C extensions, inline assembly, and TCC-specific features → See [C Language Support](reference/02-c-language-support.md)

**Assembler and Linker**: Built-in gas-like assembler, ELF/PE output formats, GNU linker script support → See [Assembler and Linker](reference/03-assembler-linker.md)

**libtcc API Reference**: Complete API for dynamic code generation including context management, compilation, linking, symbol resolution, and output types → See [libtcc API Reference](reference/04-libtcc-api.md)

**Memory and Bounds Checking**: Using `-b` flag to catch buffer overflows, out-of-bounds access, use-after-free, and double-free at runtime → See [Memory and Bounds Checking](reference/05-memory-bounds-checking.md)
