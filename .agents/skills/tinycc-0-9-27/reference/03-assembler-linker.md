# Assembler and Linker

## TinyCC Assembler

Since version 0.9.16, TCC integrates its own assembler with gas-like (GNU assembler) syntax. The assembler is used for `.S` files (C-preprocessed assembler), `.s` files (raw assembler), and inline `asm` blocks.

Assembler support can be deactivated at build time for a smaller executable — the C compiler does not depend on it.

### Syntax

Tokens are the same as C:

- C and C++ comments are supported
- Identifiers follow C rules (no `.` or `$`)
- Only 32-bit integer numbers are supported

### Expressions

- Integers in decimal, octal, and hexadecimal
- Unary operators: `+`, `-`, `~`
- Binary operators by decreasing priority:
  - `*`, `/`, `%`
  - `&`, `|`, `^`
  - `+`, `-`
- Values are either absolute numbers or label plus offset
- `+` and `-` can add an offset to a label
- `-` supports two labels only if they are the same or both defined in the same section

### Labels

- All labels are local except undefined ones
- Numeric labels (gas-style) can be defined multiple times:

```asm
1:
    jmp 1b   /* jump backward to '1' */
    jmp 1f   /* jump forward to '1' */
1:
```

### Directives

All directives are preceded by `.`:

- `.align n[,value]` — Align to n bytes
- `.skip n[,value]` / `.space n[,value]` — Reserve space
- `.byte value1[,...]` — Byte values
- `.word value1[,...]` — Word values
- `.short value1[,...]` — Short values
- `.int value1[,...]` / `.long value1[,...]` — Integer values
- `.quad immediate_value1[,...]` — Quad values
- `.globl symbol` / `.global symbol` — Global symbol
- `.section section` — Switch section
- `.text` / `.data` / `.bss` — Standard sections
- `.fill repeat[,size[,value]]` — Fill with repeated value
- `.org n` — Set location counter
- `.previous` — Return to previous section
- `.string string[,...]` — String (no null terminator)
- `.asciz string[,...]` — Null-terminated string
- `.ascii string[,...]` — ASCII string

### X86 Assembler

All x86 opcodes are supported. Only AT&T syntax (source then destination). If no size suffix is given, TCC guesses from operand sizes. MMX opcodes are supported; SSE opcodes are not.

## TinyCC Linker

TCC generates output directly without an external linker.

### ELF File Generation

TCC outputs relocatable ELF files (object files), executable ELF files, and dynamic ELF libraries. The linker eliminates unreferenced object code in libraries. A single pass is done on the object and library list, so order matters (same constraint as GNU ld). No `--start-group` / `--end-group` grouping options are supported.

Dynamic ELF libraries can be output but TCC does not generate position-independent code (PIC), so dynamic library code cannot be factorized among processes yet.

### ELF File Loader

TCC can load ELF object files, archives (`.a`), and dynamic libraries (`.so`).

### PE-i386 File Generation

For Windows, TCC generates native Win32 executables: EXE files (console and GUI) and DLL files.

### GNU Linker Scripts

TCC supports a subset of GNU ld scripts to handle systems where `/usr/lib/libc.so` is actually a linker script. Supported commands: `GROUP` and `FILE`. `OUTPUT_FORMAT` and `TARGET` are ignored.

Example from `/usr/lib/libc.so`:

```
/* GNU ld script */
GROUP ( /lib/libc.so.6 /usr/lib/libc_nonshared.a )
```

### Output Formats

Controlled via `-Wl,--oformat=fmt`:

- `elf32-i386` — ELF (default on Linux)
- `binary` — Raw binary image (executable only)
- `coff` — COFF format (TMS320C67xx target only)
