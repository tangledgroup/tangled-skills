---
name: upx-5-1-1
description: A skill for using UPX (Ultimate Packer for eXecutables) v5.1.1 to compress and decompress executable files across multiple platforms including Windows, Linux, macOS, and embedded systems. Use when reducing distribution size, optimizing storage, or packing executables for deployment.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - compression
  - executable
  - packer
  - optimization
  - deployment
category: tooling

external_references:
  - https://upx.github.io
  - https://github.com/upx/upx
---
## Overview
A skill for using UPX (Ultimate Packer for eXecutables) v5.1.1 to compress and decompress executable files across multiple platforms including Windows, Linux, macOS, and embedded systems. Use when reducing distribution size, optimizing storage, or packing executables for deployment.

A comprehensive skill for using UPX, the free, secure, portable, and high-performance executable packer. UPX typically reduces file size of programs and DLLs by 50%-70%, reducing disk space, network load times, download times, and distribution costs.

## When to Use
- Compress executables before distribution to reduce file size
- Pack Windows PE files (EXE, DLL), Linux ELF binaries, or macOS Mach-O executables
- Decompress UPX-packed files for analysis or modification
- Test integrity of compressed executables
- Optimize build artifacts for deployment
- Reduce storage costs for large executable distributions
- Compress bootable kernels (vmlinuz format)
- Pack scripts and interpreters (shell, Perl, Python) on Linux

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Usage Examples
### Basic Compression

```bash
# Compress a single executable (default level -8 for files <512KB, -7 otherwise)
upx program.exe

# Compress with maximum compression (slower)
upx --best program.exe

# Compress multiple files
upx file1.exe file2.dll file3.bin
```

### Decompression

```bash
# Decompress a UPX-packed file
upx -d program.exe

# Decompress and verify integrity
upx -d -t program.exe
```

### Test and List

```bash
# Test compressed file integrity
upx -t program.exe

# List compression info
upx -l program.exe
```

See [Common Operations](reference/01-common-operations.md) for detailed command examples.

## Key Features
- **Secure**: Open source since 1996; antivirus software can verify compressed apps
- **Excellent compression ratio**: Typically better than Zip (50%-70% reduction)
- **Very fast decompression**: More than 500 MB/sec on modern machines
- **No memory overhead**: In-place decompression for most formats
- **Safe**: Can list, test, and unpack executables with checksum verification
- **Universal**: Supports Windows, Linux, macOS, DOS, PlayStation, and more
- **Portable**: Written in portable endian-neutral C++
- **Free**: GPL v2+ with special exceptions for commercial use

## Security Context
**IMPORTANT**: UPX inherits the security context of any files it handles. Packing, unpacking, testing, or listing a file requires the same security considerations as actually executing the file.

**Use UPX on trusted files only!**

Compressed programs run exactly as before with no runtime penalty for most supported formats. Programs and libraries compressed by UPX are completely self-contained.

## Compression Levels & Tuning
UPX offers ten different compression levels from -1 to -9, plus `--best`:

| Level | Speed | Ratio | Use Case |
|-------|-------|-------|----------|
| -1, -2, -3 | Fast | Lower | Quick builds, development |
| -4, -5, -6 | Medium | Good | General use, good balance |
| -7, -8, -9 | Slower | Better | Release builds |
| `--best` | Slowest | Best | Final distribution |

**Default behavior:**
- Level `-8` for files smaller than 512 KiB
- Level `-7` for larger files

### Advanced Compression Options

```bash
# Brute force compression (tries many variants)
upx --brute program.exe

# Ultra brute (even more aggressive, very slow)
upx --ultra-brute program.exe

# Use LZMA compression (better ratio, slower decompression)
upx --lzma program.exe

# Try all compression methods
upx --all-methods program.exe

# Try all preprocessing filters
upx --all-filters program.exe

# Best compression without LZMA
upx --brute --no-lzma program.exe
```

**Note:** LZMA compresses better but is *significantly slower* at decompression. Avoid for large files unless distribution size is critical.

See [Compression Strategies](reference/02-compression-strategies.md) for detailed tuning guidance.

## Supported Executable Formats
UPX supports numerous executable formats across platforms:

### Modern Systems
- **Windows**: win32/pe, win64/pe (EXE, DLL), EFI files
- **Linux**: linux/elf386, linux/elf64, linux/riscv64, shell scripts (sh386)
- **macOS**: Mach-O (i386, amd64, ppc32) - *disabled until macOS 13+ compatibility fixed*
- **ARM**: arm/pe, wince/arm, linux/arm64

### Legacy & Embedded
- **DOS**: dos/com, dos/exe, dos/sys
- **DJGPP**: djgpp2/coff
- **Atari/TOS**: Motorola 68000 based systems
- **PlayStation**: ps1/exe (MIPS R3000)
- **Boot kernels**: vmlinuz/386, bvmlinuz/386

### Special Formats
- **Shell scripts**: Linux/sh386 (bash, sh, csh, ksh, etc.)
- **Device drivers**: DOS SYS files
- **Shared libraries**: ELF shared libs (MIPS r3000 in v5.1.1)

See [Format-Specific Notes](reference/03-format-notes.md) for platform-specific details and options.

## Overlay Handling
An "overlay" is auxiliary data attached after the logical end of an executable (common practice to avoid extra data files).

```bash
# Copy overlay after compressed image [DEFAULT]
upx --overlay=copy program.exe

# Strip overlay (may make program unusable)
upx --overlay=strip program.exe

# Refuse to compress if overlay present
upx --overlay=skip program.exe
```

**Warning:** Some applications access overlaid data directly. Stripping may cause crashes. Test thoroughly after using `--overlay=strip`.

## Environment Variables
### UPX Default Options

The `UPX` environment variable holds default options:

```bash
# bash/sh/ksh/zsh
export UPX="-9 --compress-icons=0"

# csh/tcsh
setenv UPX "-9 --compress-icons=0"

# DOS/Windows (use '#' instead of '=')
set UPX=-9 --compress-icons#0
```

Command line parameters override environment variable settings. Use `--no-env` to ignore the environment variable.

### NO_COLOR Support

UPX respects the `NO_COLOR` environment variable (see https://no-color.org/):

```bash
# Disable colored output
export NO_COLOR=1
upx program.exe
```

## Common Patterns
### Distribution Build Workflow

```bash
# Strip symbols before compression (recommended)
strip myprogram
upx --best myprogram

# Keep backup of original
upx -k --best myprogram
# Creates: myprogram (compressed), myprogram.bak (original)

# Verify compression
upx -l myprogram
```

### CI/CD Integration

```bash
# Compress release artifacts
upx --brute --overlay=strip build/release/*.exe

# Quiet mode for CI logs
upx -qq --best artifact.bin

# Fail on error (default behavior)
upx --best binary.exe || exit 1
```

### Safe Compression Testing

```bash
# Test before distributing
upx --best program.exe
upx -t program.exe  # Verify integrity
upx -d program.exe  # Decompress to verify round-trip
```

See [Common Operations](reference/01-common-operations.md) for more workflows.

## Advanced Topics
## Advanced Topics

- [Common Operations](reference/01-common-operations.md)
- [Compression Strategies](reference/02-compression-strategies.md)
- [Format Notes](reference/03-format-notes.md)
- [Linux Executables](reference/04-linux-executables.md)
- [Building From Source](reference/05-building-from-source.md)

## Troubleshooting
### Common Issues

| Problem | Solution |
|---------|----------|
| "packed data overlap" | Use `--force` to relocate loading address, or reduce compression level |
| File not recognized | Check file format; UPX only supports specific executable formats |
| Compression fails on PE file | Try `--strip-relocs=0` for Windows PE files |
| Program crashes after compression | Test with `upx -t`; try different overlay handling; verify original works |
| SELinux errors on Linux | Use `--force-execve` option for SELinux-compatible format |
| Cannot compress SUID files | UPX rejects SUID/GUID/sticky-bit programs for security reasons |

### Error Exit Codes

- **0**: Success
- **1**: General error (invalid options, file not found, etc.)
- **2**: File format not supported
- **3**: Internal error during compression/decompression
- **127**: Runtime error in compressed program (file modified after compression)

### Debugging Compressed Programs

```bash
# Linux: trace system calls
strace -o strace.log compressed_program

# Check if file was modified
upx -t compressed_program

# Decompress and compare with original
upx -d compressed_program
diff original compressed_program
```

## Version Information
**UPX v5.1.1** (05 Mar 2026)
- ELF: MIPS r3000 (32-bit) shared libraries supported
- Bug fixes from milestone #22

**Recent Changes:**
- v5.1.0: Added linux/riscv64 format support
- v5.0.0: SELinux Enforcing mode support via memfd_create
- v4.2.0: Added `--link` option to preserve hard-links (Unix)

For full changelog, see https://github.com/upx/upx/blob/v5.1.1/NEWS

## License
UPX is distributed under the GNU General Public License v2+ with special exceptions granting free usage for all binaries including commercial programs. See the UPX License Agreement at https://upx.github.io/upx-license.html

**Copyright** © 1996-2026 Markus Oberhumer, László Molnar & John Reiser

## Resources
- **Homepage**: https://upx.github.io
- **GitHub**: https://github.com/upx/upx
- **Documentation**: https://upx.github.io/docs/upx.html
- **Issue Tracker**: https://github.com/upx/upx/issues
- **License**: https://upx.github.io/upx-license.html

