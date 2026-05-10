---
name: upx-5-1-1
description: >-
  A skill for using UPX (Ultimate Packer for eXecutables) v5.1.1 to compress
  and decompress executable files across multiple platforms including Windows,
  Linux, macOS, DOS, Atari, and PlayStation. Achieves 50%-70% file size
  reduction with very fast decompression and no runtime memory penalty for most
  formats. Use when reducing distribution size of executables and DLLs,
  optimizing storage or download costs, compressing bootable Linux kernels, or
  packing executables for embedded and resource-constrained environments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - compression
  - executable-packer
  - distribution
  - size-optimization
  - cross-platform
category: tooling
external_references:
  - https://upx.github.io
  - https://github.com/upx/upx
---

# UPX 5.1.1

## Overview

UPX (the Ultimate Packer for eXecutables) is a free, secure, portable, and
high-performance executable compressor. It typically reduces file sizes of
programs and DLLs by 50%-70%, reducing disk space, network load times, download
times, and other distribution costs.

Programs compressed by UPX are completely self-contained and run exactly as
before, with no runtime or memory penalty for most supported formats due to
in-place decompression. Decompression speed exceeds 500 MB/s on modern
machines.

UPX is written in portable endian-neutral C++, distributed under the GNU
General Public License v2+ with special exceptions granting free usage for all
binaries including commercial programs.

Version 5.1.1 was released on March 5, 2026 and adds support for ELF MIPS r3000
(32-bit) shared libraries among other bug fixes.

## When to Use

- Reducing distribution size of compiled executables and DLLs
- Optimizing storage or bandwidth for software delivery
- Compressing bootable Linux kernel images (vmlinuz)
- Packing executables for embedded systems with limited flash memory
- Creating smaller release builds for Windows, Linux, macOS, or DOS targets
- Any scenario where executable file size matters and the target format is
  supported by UPX

## Core Concepts

- **Compression levels**: Levels -1 through -9 plus --best. Default is -8 for
  files under 512 KiB, -7 otherwise. Levels 1-3 are fast, 4-6 balanced, 7-9
  favor ratio, and --best may take a long time.

- **In-place decompression**: For most formats UPX decompresses directly into
  memory with no temporary files and no runtime overhead beyond the small stub.

- **Compression algorithms**: NRV (default, very fast) and LZMA (--lzma flag,
  better ratio but significantly slower decompression).

- **Overlay handling**: Auxiliary data attached after an executable's logical
  end. UPX can copy (default), strip, or skip files with overlays.

- **Security context**: UPX inherits the security context of any files it
  handles. Packing, unpacking, testing, or listing a file requires the same
  security considerations as executing it. Use only on trusted files.

- **Byte-identical round-trip**: For most formats, decompressing a packed file
  produces a byte-identical copy of the original.

## Usage Examples

Compress an executable (default operation):

```bash
upx program.exe
```

Decompress a packed executable:

```bash
upx -d program.exe
```

Test integrity of a compressed file:

```bash
upx -t program.exe
```

List information about compressed files:

```bash
upx -l program.exe
```

Best compression with brute force method selection:

```bash
upx --brute program.exe
```

Ultra brute force for maximum compression:

```bash
upx --ultra-brute program.exe
```

Compress with LZMA algorithm (better ratio, slower decompression):

```bash
upx --lzma program.exe
```

Strip overlay data from the executable:

```bash
upx --overlay=strip program.exe
```

Keep backup of original file:

```bash
upx -k program.exe
```

Write output to a specific file:

```bash
upx -o compressed.bin program.exe
```

Quiet mode (suppress warnings):

```bash
upx -q program.exe
```

Compress a Linux kernel image:

```bash
upx -9 bzImage
```

## Advanced Topics

**Supported Executable Formats**: Complete list of all supported formats with
architecture details and format-specific options → [Supported Formats](reference/01-supported-formats.md)

**Command-Line Reference**: All options, compression tuning, overlay handling,
and environment variable configuration → [Command-Line Reference](reference/02-command-line-reference.md)

**Linux-Specific Details**: ELF decompression modes, SELinux compatibility,
kernel support, and shared library considerations → [Linux Platform Guide](reference/03-linux-platform.md)

**Windows PE Details**: Resource compression, icon handling, relocation
stripping, DLL support, and Wine compatibility → [Windows PE Guide](reference/04-windows-pe.md)
