---
name: tinycc-0-9-27
description: Complete toolkit for TinyCC 0.9.27, a small hyper-fast C compiler that generates x86 code directly without external assembler or linker. Use when compiling C code extremely fast, creating C scripts with shebangs, using libtcc for dynamic code generation at runtime, performing memory/bounds checking, building rescue disks, or cross-compiling for ARM and TMS320C67xx targets.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.9.27"
tags:
  - C compiler
  - x86
  - libtcc
  - dynamic code generation
  - C scripting
category: compilers
external_references:
  - https://www.bellard.org/tcc/
  - https://www.bellard.org/tcc/tcc-doc.html
  - https://github.com/TinyCC/tinycc/tree/release_0_9_27
---
## Overview
TinyCC (TCC) is a small (~100KB), hyper-fast C compiler that generates optimized x86 code directly without byte code overhead. Unlike GCC, TCC is self-relying — it includes its own preprocessor, assembler, and linker, so no external tools are needed. It compiles about 7-9 times faster than GCC at -O0.

TCC targets i386 on Linux, Windows, macOS, and FreeBSD, with alpha ports for ARM (arm-tcc) and TMS320C67xx (c67-tcc). It aims for full ISO C99 compliance and supports many GNU C extensions.

## When to Use
- **Fast compilation**: When build speed matters more than optimization quality (e.g., during development, scripting, or embedded/rescue environments)
- **C scripting**: When you want to write C programs that execute like shell/Perl scripts via `#!/usr/local/bin/tcc -run`
- **Dynamic code generation**: When embedding a C compiler into your application using `libtcc` for runtime code compilation
- **Memory safety**: When you need optional bounds and memory checking mixed with normal C code (`-b` flag)
- **Small footprint**: When you need a complete C toolchain in ~100KB (rescue disks, minimal environments)
- **Inline assembly**: When writing x86 inline assembly with GNU assembler (gas)-like syntax

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### From Source (Linux/macOS/FreeBSD)

```bash
git clone https://github.com/TinyCC/tinycc.git
cd tinycc
git checkout release_0_9_27
./configure
make
sudo make install   # Installs to /usr/local/bin by default
```

**Notes**: Use `gmake` instead of `make` on macOS and FreeBSD. `makeinfo` is required to build documentation. Configure options: `./configure --help`.

### From Package Managers

```bash
# Debian/Ubuntu
apt install tcc

# Arch Linux
pacman -S tinycc

# macOS
brew install tcc

# NixOS
nix-shell -p tcc
```

## Quick Start Examples
### Compile and Run Directly

```bash
# Compile and execute C source (no linking/assembly needed)
tcc -run hello.c

# Pass arguments to the program
tcc -run hello.c arg1 arg2

# Read from stdin
echo 'main(){puts("hello");}' | tcc -run -
```

### C Scripts (Shebang)

Create `myscript.c`:

```c
#!/usr/local/bin/tcc -run
#include <stdio.h>

int main(int argc, char **argv)
{
    printf("Hello from C script! Args: %d\n", argc);
    return 0;
}
```

Make executable and run: `chmod +x myscript.c && ./myscript.c hello world`

### Compile to Executable

```bash
tcc -o myprog source.c                    # dynamically linked (default)
tcc -static -o myprog source.c            # statically linked
tcc -o myprog main.c utils.c -lm -lpthread  # with libraries
```

### Object Files and Libraries

```bash
tcc -c source.c                           # produces source.o
tcc -r -o combined.o file1.c file2.c      # combine objects (no linking)
tcc -shared -o libmylib.so source.c       # shared library
```

## Command-Line Options Summary
| Option | Description |
|--------|-------------|
| `-c` | Generate object file |
| `-o outfile` | Output file name |
| `-run source [args...]` | Compile and execute with arguments |
| `-v` / `-vv` / `-vvv` | Version / included files / all search tries |
| `-bench` | Compilation statistics |
| `-E` | Preprocess only |
| `-Idir` | Add include path |
| `-Dsym[=val]` | Define preprocessor symbol |
| `-Usym` | Undefine symbol |
| `-g` | Debug info for clear error messages |
| `-b` | Memory/bounds checking (implies -g) |
| `-bt N` | Show N callers in stack traces |
| `-Wall` | All warnings |
| `-Werror` | Warnings as errors |
| `-w` | Disable all warnings |
| `-funsigned-char` / `-fsigned-char` | char signedness |
| `-fno-common` | No common symbols |
| `-fleading-underscore` | Leading underscore on C symbols |
| `-fms-extensions` | MS C compiler extensions |
| `-fdollars-in-identifiers` | Allow $ in identifiers |
| `-Ldir` | Library search path |
| `-lxxx` | Link library |
| `-shared` | Generate shared library |
| `-static` | Static linking |
| `-rdynamic` | Export global symbols |
| `-r` | Combine files into object file |
| `-Bdir` | Set internal library path |
| `-MD` / `-MF depfile` | Dependency generation |
| `-mms-bitfields` | MSVC bitfield alignment |
| `-mno-sse` | Disable SSE on x86_64 |
| `-mfloat-abi=softfp\|hard` | ARM float ABI |

See `reference/01-command-reference.md` for full option details.
See `reference/02-c-language-support.md` for language features and extensions.
See `reference/03-libtcc-api.md` for the libtcc dynamic code generation API.
See `reference/04-assembler-and-linker.md` for assembler directives and linker options.

## Advanced Topics
## Advanced Topics

- [Command Reference](reference/01-command-reference.md)
- [C Language Support](reference/02-c-language-support.md)
- [Libtcc Api](reference/03-libtcc-api.md)
- [Assembler And Linker](reference/04-assembler-and-linker.md)

