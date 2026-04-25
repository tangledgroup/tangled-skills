# TinyCC Command-Line Reference

## General Options

### `-c`
Generate an object file.

```bash
tcc -c source.c        # produces source.o
```

### `-o outfile`
Put object file, executable, or DLL into output file `outfile`.

```bash
tcc -o myprog main.c utils.c
```

### `-run source [args...]`
Compile file and run it with command line arguments. Several TCC options can follow `-run`, separated by spaces:

```bash
tcc -run a.c arg1              # compile and execute, arg1 → main() argv[1]
tcc "-run -L/usr/X11R6/lib -lX11" ex4.c  # compile with extra options
```

In a C script shebang:
```c
#!/usr/local/bin/tcc -run -L/usr/X11R6/lib -lX11
```

### `-v` / `-vv` / `-vvv`
- `-v`: Display TCC version
- `-vv`: Show included files; as sole argument, print search dirs
- `-vvv`: Shows tries too

### `-bench`
Display compilation statistics.

## Preprocessor Options

### `-Idir`
Specify an additional include path. Include paths are searched in the order specified. System include paths (`/usr/local/include`, `/usr/include`, `PREFIX/lib/tcc/include`) are searched after.

```bash
tcc -I/usr/local/include -I./includes -run main.c
```

### `-Dsym[=val]`
Define preprocessor symbol. If val is not present, its value is `1`. Function-like macros can be defined:

```bash
tcc -DDEBUG -DVERSION="1.0" -run main.c
tcc -DMAX(a,b)=((a)>(b)?(a):(b)) -run main.c
```

### `-Usym`
Undefine preprocessor symbol.

```bash
tcc -UNDEBUG -run main.c
```

### `-E`
Preprocess only, to stdout or file (with `-o`).

```bash
tcc -E source.c > preprocessed.i
tcc -E -o output.i source.c
```

## Compilation Flags

Each option has a negative form beginning with `-fno-`.

| Option | Description |
|--------|-------------|
| `-funsigned-char` | Let `char` type be unsigned |
| `-fsigned-char` | Let `char` type be signed |
| `-fno-common` | Do not generate common symbols for uninitialized data |
| `-fleading-underscore` | Add leading underscore to each C symbol |
| `-fms-extensions` | Allow MS C compiler extensions (nested unnamed struct declarations) |
| `-fdollars-in-identifiers` | Allow dollar signs in identifiers |

## Warning Options

Each warning option has a negative form beginning with `-Wno-`.

| Option | Description |
|--------|-------------|
| `-w` | Disable all warnings |
| `-Wimplicit-function-declaration` | Warn about implicit function declaration |
| `-Wunsupported` | Warn about unsupported GCC features that are ignored by TCC |
| `-Wwrite-strings` | Make string constants `const char *` instead of `char *` |
| `-Werror` | Abort compilation if warnings are issued |
| `-Wall` | All warnings, except `-Werror`, `-Wunsupported`, and `-Wwrite-strings` |

## Linker Options

### `-Ldir`
Specify an additional static library path for the `-l` option. Default paths: `/usr/local/lib`, `/usr/lib`, `/lib`.

### `-lxxx`
Link with dynamic library `libxxx.so` or static library `libxxx.a`. Searched in `-L` paths and `LIBRARY_PATH`.

```bash
tcc -o myprog main.c -L/usr/X11R6/lib -lX11 -lm
```

### `-Bdir`
Set the path where TCC internal libraries (and include files) can be found. Default is `PREFIX/lib/tcc`.

### `-shared`
Generate a shared library instead of an executable.

### `-soname name`
Set name for shared library to be used at runtime.

```bash
tcc -shared -soname libmylib.so.1 -o libmylib.so source.c
```

### `-static`
Generate a statically linked executable (default is dynamically linked).

### `-rdynamic`
Export global symbols to the dynamic linker. Useful when a library opened with `dlopen()` needs to access executable symbols.

### `-r`
Generate an object file combining all input files.

```bash
tcc -r -o ab.o a.c b.c
```

### `-Wl,-rpath=path`
Put custom search path for dynamic libraries into executable.

### `-Wl,--enable-new-dtags`
Create DT_RUNPATH instead of legacy DT_RPATH when putting custom search paths into the executable.

### `-Wl,--oformat=fmt`
Use format as output format:

| Format | Description |
|--------|-------------|
| `elf32-i386` | ELF output format (default) |
| `binary` | Binary image (executable only) |
| `coff` | COFF format (TMS320C67xx target only) |

```bash
tcc -Wl,--oformat=binary -o firmware.bin source.c
```

### `-Wl,-subsystem=console/gui/wince/...`
Set type for PE (Windows) executables.

### `-Wl,-(no-)whole-archive`
Turn on/off linking of all objects in archives.

```bash
tcc -Wl,-whole-archive -lmyarchive -Wl,-no-whole-archive -o myprog main.c
```

## Debugger Options

### `-g`
Generate runtime debug information for clear error messages:

```bash
# Without -g: "Segmentation fault"
# With -g: "test.c:68: in function 'test5()': dereferencing invalid pointer"
tcc -g -run program.c
```

### `-b`
Generate additional support code to check memory allocations and array/pointer bounds. Implies `-g`. Generated code is slower and bigger. **Only available on i386 when using libtcc.**

### `-bt N`
Display N callers in stack traces. Useful with `-g` or `-b`.

```bash
tcc -bt 5 -b -run program.c
```

## Misc Options

### `-MD` / `-MF depfile`
Generate makefile fragment with dependencies.

```bash
tcc -MD -MF main.d -c main.c
```

### `-print-search-dirs`
Print the configured installation directory and a list of library and include directories TCC will search.

### `-dumpversion`
Print version.

## Target-Specific Options

| Option | Description |
|--------|-------------|
| `-mms-bitfields` | MSVC-compatible bitfield alignment (default is GCC's algorithm) |
| `-mfloat-abi` (ARM only) | Select float ABI: `softfp` or `hard` |
| `-mno-sse` | Do not use SSE registers on x86_64 |
| `-m32, -m64` | Pass command line to the i386/x86_64 cross compiler |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `CPATH` | Colon-separated list of directories searched for include files (after `-I` paths) |
| `C_INCLUDE_PATH` | Same as CPATH |
| `LIBRARY_PATH` | Colon-separated list of directories searched for libraries (after `-L` paths) |

## Note on Unsupported Options

GCC options `-Ox`, `-fx`, and `-mx` are **ignored** by TCC. TCC does not support optimization levels — it compiles in a single pass without intermediate representations.
