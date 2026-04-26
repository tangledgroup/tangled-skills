# Command-Line Reference

## Usage

```
tcc [options] [infile1 infile2...] [-run infile args...]
```

TCC options are very similar to GCC. The main difference is that TCC can execute the resulting program directly and pass runtime arguments.

## General Options

**`-c`** — Generate an object file (`.o`).

**`-o outfile`** — Put object file, executable, or DLL into output file `outfile`.

**`-run source [args...]`** — Compile `source` and run it with the given command-line arguments. Multiple TCC options can be given after `-run`, separated by spaces:

```bash
tcc "-run -L/usr/X11R6/lib -lX11" ex4.c
```

In a script shebang:

```c
#!/usr/local/bin/tcc -run -L/usr/X11R6/lib -lX11
```

**`-v`** — Display TCC version.

**`-vv`** — Show included files. As sole argument, print search directories. `-vvv` shows tries too.

**`-bench`** — Display compilation statistics.

## Preprocessor Options

**`-Idir`** — Specify an additional include path. Paths are searched in the order specified. System include paths (`/usr/local/include`, `/usr/include`, `PREFIX/lib/tcc/include`) are always searched after.

**`-Dsym[=val]`** — Define preprocessor symbol `sym` to `val`. If `val` is not present, its value is `1`. Function-like macros: `-DF(a)=a+1`.

**`-Usym`** — Undefine preprocessor symbol `sym`.

**`-E`** — Preprocess only, output to stdout or file (with `-o`).

**`-P[1]`** — Preprocessor option (0.9.27).

**`-dD`** — Emit macro definitions in preprocessed output (0.9.27).

**`-dM`** — Emit only macro definitions in preprocessed output (0.9.27).

**`-include <file>`** — Include a file before processing (0.9.27).

## Compilation Flags

Each option has a negative form beginning with `-fno-`.

**`-funsigned-char`** — Let the `char` type be unsigned.

**`-fsigned-char`** — Let the `char` type be signed.

**`-fno-common`** — Do not generate common symbols for uninitialized data.

**`-fleading-underscore`** — Add a leading underscore at the beginning of each C symbol.

**`-fms-extensions`** — Allow MS C compiler extensions. Nested named structure declaration without an identifier behaves like an unnamed one.

**`-fdollars-in-identifiers`** — Allow dollar signs in identifiers.

## Warning Options

Each option has a negative form beginning with `-Wno-`.

**`-w`** — Disable all warnings.

**`-Wimplicit-function-declaration`** — Warn about implicit function declaration.

**`-Wunsupported`** — Warn about unsupported GCC features that are ignored by TCC.

**`-Wwrite-strings`** — Make string constants `const char *` instead of `char *`.

**`-Werror`** — Abort compilation if warnings are issued.

**`-Wall`** — Activate all warnings except `-Werror`, `-Wunsupported`, and `-Wwrite-strings`.

## Linker Options

**`-Ldir`** — Specify an additional static library path for the `-l` option. Default paths: `/usr/local/lib`, `/usr/lib`, `/lib`.

**`-lxxx`** — Link with dynamic library `libxxx.so` or static library `libxxx.a`. Searched in `-L` paths and `LIBRARY_PATH`.

**`-Bdir`** — Set the path where TCC internal libraries and include files are found (default: `PREFIX/lib/tcc`).

**`-shared`** — Generate a shared library instead of an executable.

**`-soname name`** — Set name for shared library to be used at runtime.

**`-static`** — Generate a statically linked executable (default is dynamically linked).

**`-rdynamic`** — Export global symbols to the dynamic linker. Useful when a library opened with `dlopen()` needs to access executable symbols.

**`-r`** — Generate an object file combining all input files.

**`-Wl,-rpath=path`** — Put custom search path for dynamic libraries into executable.

**`-Wl,--enable-new-dtags`** — Create DT_RUNPATH instead of legacy DT_RPATH when setting rpath.

**`-Wl,--oformat=fmt`** — Use `fmt` as output format:
- `elf32-i386` — ELF output format (default)
- `binary` — Binary image (only for executable output)
- `coff` — COFF output format (TMS320C67xx target only)

**`-Wl,-subsystem=console/gui/wince/...`** — Set type for PE (Windows) executables.

**`-Wl,-[Ttext=# | section-alignment=# | file-alignment=# | image-base=# | stack=#]`** — Modify executable layout.

**`-Wl,-Bsymbolic`** — Set DT_SYMBOLIC tag.

**`-Wl,-(no-)whole-archive`** — Turn on/off linking of all objects in archives (0.9.27).

**`-x[c|a|n]`** — Force filetype: c (C source), a (assembly), n (none) (0.9.27).

**`-pthread`** — Equivalent to `-D_REENTRANT -lpthread`.

## Debugger Options

**`-g`** — Generate runtime debug information for clear error messages. Instead of "Segmentation fault" you get: `test.c:68: in function 'test5()': dereferencing invalid pointer`.

**`-b`** — Generate additional support code to check memory allocations and array/pointer bounds. `-g` is implied. Generated code is slower and bigger. Note: `-b` is only available on i386 when using libtcc.

**`-bt N`** — Display N callers in stack traces. Useful with `-g` or `-b`.

## Miscellaneous Options

**`-MD`** — Generate makefile fragment with dependencies.

**`-MF depfile`** — Use `depfile` as output for `-MD`.

**`-print-search-dirs`** — Print configured installation directory and list of library and include directories.

**`-dumpversion`** — Print version.

**`@listfile`** — Read options from `listfile` (0.9.27).

## Target-Specific Options

**`-mms-bitfields`** — Use MSVC-compatible bitfield alignment algorithm (default is GCC's) (0.9.27).

**`-mfloat-abi`** — Select float ABI for ARM. Values: `softfp`, `hard`.

**`-mno-sse`** — Do not use SSE registers on x86_64 (0.9.27).

**`-m32, -m64`** — Pass command line to the i386/x86_64 cross compiler.

## Environment Variables

**`CPATH`** / **`C_INCLUDE_PATH`** — Colon-separated list of directories searched for include files. Directories given with `-I` are searched first (0.9.27).

**`LIBRARY_PATH`** — Colon-separated list of directories searched for libraries for the `-l` option. Directories given with `-L` are searched first (0.9.27).

## Notes

- GCC options `-Ox`, `-fx`, and `-mx` are ignored by TCC.
- TCC includes its own `ar`/`impdef` tools integrated into the main binary (0.9.27): `tcc -ar` and `tcc -impdef`.
