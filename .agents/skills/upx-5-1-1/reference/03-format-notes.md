# UPX Format-Specific Notes

This reference covers platform-specific considerations, options, and limitations for each supported executable format.

## Windows PE Formats (win32/pe, win64/pe)

### Overview
Windows Portable Executable format includes EXE, DLL, and EFI files for both 32-bit and 64-bit Windows.

### Features
- Full support for PE32 and PE32+ formats
- TLS (Thread Local Storage) callback support
- Icon and resource compression
- Load configuration section handling
- Correct SizeOfHeaders in PE header (v4.0.0+)

### Special Options

```bash
# Compress icons and version resources
upx --compress-icons=1 program.exe   # Compress some icons
upx --compress-icons=2 program.exe   # Compress more icons
upx --compress-icons=3 program.exe   # Compress all icons

# Keep specific resources uncompressed
upx --keep-resource=RT_VERSION program.exe
upx --keep-resource=RT_ICON program.exe
upx --keep-resource=RT_MANIFEST program.exe

# Disable relocation stripping (improves compatibility)
upx --strip-relocs=0 program.exe

# Preserve hard links (Unix only, use with care)
upx --link program.exe
```

### Known Issues and Workarounds

**Go binaries:** Go compiler creates bad PT_LOAD segments. Use hemfix.c tool before compression:
```bash
# See: https://github.com/pwaller/goupx
hemfix program.exe
upx --best program.exe
```

**.NET assemblies:** UPX can detect but does not support .NET files (win32/net). These will be rejected.

**Regressions in 3.92:** Internal changes reunited diverged source files. If problems occur, try UPX 3.91.

### Best Practices

```bash
# Recommended workflow for Windows executables
strip program.exe  # If symbols present
upx --best --compress-icons=2 program.exe
upx -t program.exe  # Verify integrity
```

## Linux ELF Formats

### Overview
Linux support includes three main formats:
- **linux/elf386**: ELF executables (direct-to-memory decompression)
- **linux/sh386**: Shell scripts (decompress to memory, pass to shell)
- **linux/386**: Generic format (decompresses to /tmp)

### linux/elf386 - ELF Executables

**How it works:** UPX decompresses directly to memory, simulating the mapping that the OS kernel uses during exec(). Uses only one exec, no /tmp space, no /proc.

**Features:**
- About 1700 bytes stub written in assembler
- Only uses kernel syscalls, not linked against libc
- Should run under any Linux configuration that can run ELF binaries
- Byte-identical after uncompression

**Supported architectures:** i386, amd64, arm64, ppc32, mipsel, riscv64 (v5.1.0+)

**Shared libraries:** Supported since v3.05 with restrictions:
- DT_INIT must exist
- All info needed by runtime loader must be first in .text
- v5.1.1: MIPS r3000 (32-bit) shared libraries supported

### linux/sh386 - Shell Scripts

**How it works:** UPX decompresses the script into low memory, maps the shell, and passes control with the entire decompressed file as argument after "-c".

**Supported shells:** sh, ash, bash, bsh, csh, ksh, tcsh, pdksh

**Restrictions:**
- Cannot handle scripts with optional string argument after shell name
  Example that won't work: `#!/bin/sh option3`

**Features:**
- No /tmp space used
- No /proc required
- Byte-identical after uncompression

### linux/386 - Generic Format

**How it works:** Uses execve() syscall, requiring decompression to temporary file in /tmp.

**When selected:** Only when elf386 and sh386 don't recognize the file.

**Requirements:**
- Free disk space in /tmp for uncompressed program
- /proc filesystem support (/proc/<pid>/exe and /proc/<pid>/fd/X)
- Cannot compress programs used before /proc is mounted (boot sequence)

**Drawbacks:**
- Utilities like `top` show numerical values in process name
- Slower decompression due to temporary disk I/O
- Need additional free space in /tmp

### Linux-Specific Options

```bash
# Force generic execve format (SELinux compatibility)
upx --force-execve program

# Unmap all pages (avoid /proc/self/exe entirely)
upx --unmap-all-pages program

# Preserve build ID (GNU ELF)
upx --preserve-build-id program

# Work around bad Android shared library design
upx --android-shlib library.so

# Force PIE when ET_DYN not marked as DF_1_PIE
upx --force-pie program
```

### SELinux Support (v5.0.0+)

```bash
# Use memfd_create for SELinux Enforcing mode
upx program  # Automatically uses memfd_create in v5.0.0+

# If issues persist, force execve format
upx --force-execve program
```

### General Linux Notes

**Benefits:**
- Compress all executables: AOUT, ELF, libc4/5/6, scripts, Java .class
- Completely self-contained compressed programs
- Original program untouched (byte-identical after decompression)
- Stub only uses syscalls, runs under any Linux configuration

**Drawbacks:**
- Not advisable for programs with many concurrent instances (sh, make)
- Compressed programs won't be shared between processes
- `ldd` and `size` won't show useful information
- Platform independence lost for scripts (NFS issues)

**Security restrictions:**
- SUID, GUID, and sticky-bit programs are rejected
- No sense in making compressed programs SUID

**Recommendations:**
```bash
# Strip before compression
strip program
upx --best program

# Check swap space usage for elf386/sh386 formats
top  # Monitor RAM and swap usage
```

## macOS Mach-O Formats

### Status: Disabled (v4.2.0+)

**Important:** macOS support is disabled in UPX v4.2.0+ until compatibility with macOS 13+ is fixed.

**Historical formats (pre-4.2.0):**
- Mach/i386 (32-bit)
- Mach/amd64 (64-bit)
- Mach/ppc32 (PowerPC)
- Mach/fat (Universal binaries)
- Dylib/i386 and Dylib/ppc32 (shared libraries)

### Requirements (when supported)

**Shared libraries:** Required -init function (LC_ROUTINES command).

**Code signing:** Supported with LC_UUID.

## DOS Formats

### DOS/COM

**Characteristics:**
- Maximum uncompressed size: ~65100 bytes
- Compressed programs work on 286+
- Byte-identical after uncompression

**Options:**
```bash
# Create 8086-compatible executable
upx --8086 program.com

# Try all compression methods
upx --all-methods program.com

# Try all filters
upx --all-filters program.com
```

**Limitations:** Won't work with executables that read data from themselves (some Win95/98/ME utilities).

### DOS/EXE

**Characteristics:**
- "Normal" 16-bit DOS executables
- Works on 286+
- LZMA supported since v2.93 (use --lzma explicitly, even for --ultra-brute)

**Options:**
```bash
upx --8086 program.exe
upx --no-reloc program.exe      # No relocation records in header
upx --all-methods program.exe
```

### DOS/SYS

**Characteristics:**
- Device driver format
- Maximum uncompressed size: ~65350 bytes
- Works on 286+
- Byte-identical after uncompression

**Options:** Same as DOS/COM

## DJGPP2/COFF Format

### Overview
DJGPP2 COFF format for DOS development environment.

### Features
- UPX recommended **instead of strip** (strip replaces stub with outdated version)
- Fixes 4 KiB alignment bug in strip v2.8.x
- Full stubify functionality included
- Automatic Allegro packfile handling
- DLM format not supported

### Behavior
- Byte-identical after uncompression
- Debug information and trailing garbage stripped

### Options

```bash
# Produce COFF output instead of EXE
upx --coff program.exe

# Try all methods/filters
upx --all-methods program.exe
upx --all-filters program.exe
```

## Atari/TOS Format

### Overview
Motorola 68000 based Atari ST/TT executable format.

**Note:** Support is nostalgic only, no practical purpose. See https://freemint.github.io

### Characteristics
- Byte-identical after uncompression
- Debug information stripped

### Options

```bash
upx --all-methods program.tos
```

## PlayStation 1 Format (ps1/exe)

### Overview
MIPS R3000 based Sony PlayStation (PSone) executable format.

**Compatibility:** Reported to work with PS2 and PSP in PSone emulation mode.

### Characteristics
- Maximum uncompressed size: ~1.89 / ~7.60 MiB
- Byte-identical after uncompression (until further notice)
- Default creates CD-Mastering and console transfer compatible executable

### Memory Handling
Normally uses same memory areas as uncompressed version. If not possible, UPX aborts with "packed data overlap" error. Use `--force` to relocate loading address.

### Options

```bash
# Try all compression methods
upx --all-methods game.exe

# Use 8-bit size compression (default: 32-bit)
upx --8-bit game.exe

# PSone has 8 MiB RAM available (default: 2 MiB)
upx --8mib-ram game.exe

# CD-Mastering only (faster, better ratio, cannot console transfer)
upx --boot-only main.exe

# Disable CD mode 2 sector alignment (console transfer only)
upx --no-align game.exe
```

## ARM Formats

### ARM/PE and RTM32/PE

Same as win32/pe. Supports:
- Windows CE executables
- Thumb mode
- DLL support
- Filter support

### Linux ARM

- **armel-eabi:** Extended ABI version 4 supported
- **arm64-linux (aarch64):** Supported since v3.94
- **riscv64:** Supported since v5.1.0

## Bootable Kernel Formats

### vmlinuz/386 and bvmlinuz/386

**Features:**
- Support for bootable Linux kernels
- BVMLINUZ supports boot protocol 2.08
- x86_64 kernel support

**Use case:** Compressing kernels for embedded systems or distribution media.

## EFI Format

### Overview
Support for EFI (Extensible Firmware Interface) files added in v4.0.0.

**Format:** PE x86

**Contributor:** Kornel Pal

## Unsupported Formats

UPX explicitly does not support:
- **.NET assemblies** (win32/net) - Can detect but will reject
- **Shared libraries on Darwin/macOS** - Withdrawn in v3.05
- **DLM format** (DJGPP shared library extension)

## Format Detection

UPX automatically detects executable format. To verify detection:

```bash
# Check file type
file program.exe
# Output: PE32 executable (console) x86, for MS Windows

# UPX will show format in verbose output
upx -v program.exe
```

## Related Reference Files

- [Common Operations](01-common-operations.md) - Basic commands and workflows
- [Compression Strategies](02-compression-strategies.md) - Tuning and optimization
- [Linux Executables](04-linux-executables.md) - Detailed Linux format documentation
