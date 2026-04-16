# TinyCC Assembler and Linker Reference

## TinyCC Assembler

Since version 0.9.16, TCC integrates its own assembler with gas-like (GNU assembler) syntax. It handles:
- `.S` files: Preprocessed with C preprocessor, then assembled
- `.s` files: Assembled without preprocessing
- Inline assembly via the `asm` keyword

### Syntax

- C and C++ comments supported
- Identifiers follow C rules (no `.` or `$`)
- Only 32-bit integer numbers supported

### Expressions

| Category | Operators |
|----------|-----------|
| Unary | `+`, `-`, `~` |
| Multiplicative | `*`, `/`, `%` |
| Bitwise | `&`, `\|`, `^` |
| Additive | `+`, `-` |

A value is either an absolute number or a label plus offset. `+` and `-` can add offsets to labels. `-` supports two labels only if they are the same or both defined in the same section.

### Labels

- All labels are local except undefined ones
- Numeric labels work as gas-like labels:

```asm
 1:
      jmp 1b    /* jump backward to label '1' */
      jmp 1f    /* jump forward to label '1' */
 1:
```

### Assembler Directives

All directives are preceded by `.`:

| Directive | Description |
|-----------|-------------|
| `.align n[,value]` | Align to n bytes |
| `.skip n[,value]` | Skip n bytes, fill with value |
| `.space n[,value]` | Same as .skip |
| `.byte value1[,...]` | Emit 1-byte values |
| `.word value1[,...]` | Emit 2-byte values |
| `.short value1[,...]` | Emit 2-byte values (same as .word) |
| `.int value1[,...]` | Emit 4-byte values |
| `.long value1[,...]` | Emit 4-byte values (same as .int) |
| `.quad immediate_value1[,...]` | Emit 8-byte values |
| `.globl symbol` / `.global symbol` | Export symbol |
| `.section section` | Switch to named section |
| `.text` | Switch to code section |
| `.data` | Switch to data section |
| `.bss` | Switch to BSS (uninitialized) section |
| `.fill repeat[,size[,value]]` | Emit repeat copies of size bytes with value |
| `.org n` | Set current position to n |
| `.previous` | Switch back to previous section |
| `.string string[,...]` | Emit string without null terminator |
| `.asciz string[,...]` | Emit string with null terminator |
| `.ascii string[,...]` | Emit ASCII bytes without null |

### X86 Assembler

- All x86 opcodes supported
- ATT syntax only (source then destination operand order)
- MMX opcodes supported; SSE not supported
- Size suffix inferred from operand sizes if omitted

## TinyCC Linker

TCC includes its own linker — no external linker is needed.

### ELF File Generation

TCC directly outputs:
- Relocatable ELF files (object files)
- Executable ELF files
- Dynamic ELF libraries (.so)

**Important**: Dynamic libraries from TCC are **not position-independent code (PIC)**. The generated code cannot be factorized among processes.

The linker eliminates unreferenced object code in libraries with a single pass. Order matters (same constraint as GNU ld). No grouping options (`--start-group` / `--end-group`) are supported.

### ELF File Loader

TCC can load:
- ELF object files
- Archives (`.a` files)
- Dynamic libraries (`.so`)

### PE-i386 File Generation

Windows builds support the native PE-i386 format:
- EXE files (console and GUI)
- DLL files

See `tcc-win32.txt` in the source distribution for Windows-specific details.

### GNU Linker Scripts

TCC supports a subset of GNU ld scripts because some system libraries (e.g., `/usr/lib/libc.so`) are actually linker scripts:

| Command | Support |
|---------|---------|
| `GROUP` | ✅ Supported |
| `FILE` | ✅ Supported |
| `OUTPUT_FORMAT` | ⚠️ Ignored |
| `TARGET` | ⚠️ Ignored |

Example from `/usr/lib/libc.so`:

```ld
/* GNU ld script */
GROUP ( /lib/libc.so.6 /usr/lib/libc_nonshared.a )
```

### Linker Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| `elf32-i386` | (default) | ELF executable/object/library on Linux |
| `binary` | `-Wl,--oformat=binary` | Raw binary image (executable only) |
| `coff` | `-Wl,--oformat=coff` | COFF format for TMS320C67xx target |

### Linker Memory Layout Options

```bash
# Modify executable layout
tcc -Wl,-Ttext=#                  # Set text segment address
tcc -Wl,-section-alignment=#      # Set section alignment
tcc -Wl,-file-alignment=#         # Set file alignment
tcc -Wl,-image-base=#             # Set image base address
tcc -Wl,-stack=#                  # Set stack size

# Windows PE options
tcc -Wl,-subsystem=console        # Console executable
tcc -Wl,-subsystem=gui            # GUI executable
```

### Symbol Export Options

```bash
# Set DT_SYMBOLIC tag (for position-independent shared libs)
tcc -Wl,-Bsymbolic -shared -o lib.so source.c
```

## Memory and Bounds Checking (`-b`)

### How It Works

Activated with the `-b` flag (implies `-g`). TCC generates additional code to check:
- Memory allocations
- Array/pointer bounds
- Invalid pointer dereferences
- Freed memory access
- Double frees

### Key Properties

1. **Pointer size is unchanged** — bound-checked code is fully compatible with unchecked code
2. When a pointer comes from unchecked code, it is assumed valid
3. Even obscure C code with casts should work correctly
4. Works even with non-patched standard libraries
5. Only available on i386 when using libtcc
6. Generated code is slower and bigger

### Example Errors Caught

```c
/* Invalid range with standard string function */
{
    char tab[10];
    memset(tab, 0, 11);  /* Error: out of bounds */
}

/* Out of bounds in global/local arrays */
{
    int tab[10];
    for (i = 0; i < 11; i++) sum += tab[i];  /* Error: index 10 out of bounds */
}

/* Out of bounds in malloc'd data */
{
    int *tab = malloc(20 * sizeof(int));
    for (i = 0; i < 21; i++) sum += tab[i];   /* Error: index 20 out of bounds */
    free(tab);
}

/* Access of freed memory */
{
    int *tab = malloc(20 * sizeof(int));
    free(tab);
    for (i = 0; i < 20; i++) sum += tab[i];   /* Error: use after free */
}

/* Double free */
{
    int *tab = malloc(20 * sizeof(int));
    free(tab);
    free(tab);  /* Error: double free */
}
```

## Developer Notes: TCC Internal Architecture

### Compilation Pipeline

TCC compiles in a single pass directly to linked binary code. There is no intermediate representation — the code generator produces x86 machine code immediately.

**Architecture**: Register-based code generator with three temporary registers on x86. When more registers are needed, spilling occurs to stack-allocated temporaries.

### Value Stack Model

The value stack (`vstack`, top at `vtop`) uses `SValue` structures:

| Flag | Meaning |
|------|---------|
| `VT_CONST` | Value is a constant (stored in `SValue.c`) |
| `VT_LOCAL` | Local variable pointer at offset `SValue.c.i` on stack |
| `VT_CMP` | Value stored in CPU flags (0 or 1) |
| `VT_JMP` / `VT_JMPI` | Result of conditional jump (for `||` and `&&`) |
| `VT_LVAL` | Value is an lvalue (pointer to wanted value) |
| `VT_LLOCAL` | Saved lvalue on stack (must have `VT_LVAL` set too) |
| `VT_MUSTCAST` | Lazy cast needed if value is used |
| `VT_SYM` | Add symbol `SValue.sym` to the constant |

### Type System

Types stored in a single `int` variable with bit flags:

| Constant | Value | Meaning |
|----------|-------|---------|
| `VT_INT` | 0 | Integer type |
| `VT_BYTE` | 1 | Signed byte |
| `VT_SHORT` | 2 | Short |
| `VT_VOID` | 3 | Void |
| `VT_PTR` | 4 | Pointer |
| `VT_ENUM` | 5 | Enum definition |
| `VT_FUNC` | 6 | Function |
| `VT_STRUCT` | 7 | Struct/union |
| `VT_FLOAT` | 8 | IEEE float |
| `VT_DOUBLE` | 9 | IEEE double |
| `VT_LDOUBLE` | 10 | IEEE long double |
| `VT_BOOL` | 11 | C99 boolean |
| `VT_LLONG` | 12 | 64-bit integer |

Modifiers (bit flags):
- `VT_UNSIGNED`, `VT_ARRAY`, `VT_VLA`, `VT_BITFIELD`, `VT_CONSTANT`, `VT_VOLATILE`
- Storage: `VT_EXTERN`, `VT_STATIC`, `VT_TYPEDEF`, `VT_INLINE`, `VT_WEAK`

### Symbol Stacks

| Stack | Purpose |
|-------|---------|
| `define_stack` | Macros (`#define`) |
| `global_stack` | Global variables, functions, types |
| `local_stack` | Local variables, functions, types |
| `global_label_stack` | Goto labels (file scope) |
| `label_stack` | Block-local labels (`__label__`) |

### Sections

| Section | Purpose |
|---------|---------|
| `text_section` | Generated code |
| `data_section` | Initialized data |
| `bss_section` | Uninitialized data |
| `bounds_section` / `lbounds_section` | Bounds checking tables (with `-b`) |
| `stab_section` / `stabstr_section` | Debug info (with `-g`) |
| `symtab_section` / `strtab_section` | Exported symbols |

### Optimizations

TCC performs limited optimizations in its single-pass approach:
- **Constant propagation** for all operations
- **Strength reduction**: Multiplications/divisions → shifts when appropriate
- **Comparison caching**: CPU flags cached to avoid redundant tests
- **Logical operator optimization**: `&&`, `||`, `!` use jump-target values

No other jump optimization is performed (would require more abstract code storage).
