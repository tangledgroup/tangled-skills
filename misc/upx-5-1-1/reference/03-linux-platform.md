# Linux Platform Guide

## Overview

Linux support in UPX consists of three different executable formats:

- **linux/elf386** — Optimized for ELF executables, decompresses directly into
  RAM
- **linux/sh386** — Optimized for shell scripts, uses the shell's -c argument
- **linux/386** — Generic format, decompresses to /tmp then execve

UPX automatically selects the best format. ELF binaries prefer linux/elf386,
shell scripts use linux/sh386, and everything else falls back to linux/386.

## How Decompression Works

### linux/elf386 (default for ELF binaries)

UPX decompresses directly to memory, simulating the mapping that the kernel
uses during exec(), including the PT_INTERP program interpreter. The brk() is
set by a special PT_LOAD segment in the compressed executable itself. UPX then
wipes the stack clean except for arguments, environment variables, and
Elf_auxv entries, and transfers control to the program interpreter or the
e_entry address.

The stub is about 1700 bytes, partly written in assembler, uses only kernel
syscalls, and is not linked against any libc.

Benefits:
- Uses only one exec
- Does not use space in /tmp
- Does not use /proc
- Packed programs are byte-identical after uncompression

### linux/sh386 (for shell scripts)

For scripts beginning with "#!/" or "#! /" where the shell accepts "-c
<command>", UPX decompresses into low memory, maps the shell, and passes the
entire decompressed file as an argument after "-c". Known shells: sh, ash,
bash, bsh, csh, ksh, tcsh, pdksh.

Restriction: Cannot handle scripts with optional string arguments after the
shell name (e.g., "#! /bin/sh option3").

### linux/386 (generic fallback)

Decompresses to a temporary file in /tmp, then starts via execve(). Requires
/proc filesystem support.

Steps at runtime:
1. Decompress overlay to /tmp
2. Open the temporary file for reading
3. Try to delete it and start via /proc/<pid>/fd/X
4. If that fails, fork a subprocess to clean up

Drawbacks:
- Needs free disk space in /tmp
- Requires /proc filesystem
- Utilities like `top` show numerical values in process name field
- Slower decompression due to temporary file

Use `--force-execve` to force this format.

## SELinux Support

Starting with UPX 5.0.0, ELF uses memfd_create which supports Enforcing mode
of SELinux. The two-step de-compression enables future per-PT_LOAD work. The
`--unmap-all-pages` option completely avoids /proc/self/exe.

For older UPX versions (pre-5.0), use `--force-execve` for SELinux
compatibility, but note that /tmp must support execve() — it cannot be mounted
with 'noexec'.

## Shared Libraries

ELF shared libraries are supported for i386 and amd64 (and other architectures
as listed in the Supported Formats reference). Requirements:

- DT_INIT must exist
- All info needed by the runtime loader must be first in .text
- ELF executables with more than 2 PT_LOAD segments are handled since UPX 4.1.0

## Kernel Support

- **vmlinuz/386** — Takes a gzip-compressed bootable Linux kernel,
  gzip-decompresses it, and re-compresses with UPX method
- **bvmlinuz/386** — Same as vmlinuz/386
- **vmlinux/386** — Directly supports building Linux kernels

Example compression savings for a 2.2.16 kernel:

```
1589708  vmlinux
 641073  bzImage        [original]
 560755  bzImage.upx    [compressed by "upx -9"]
```

## General Benefits on Linux

- Compresses all executables: AOUT, ELF, libc4/5/6, shell scripts, Perl,
  Python, standalone Java .class binaries
- Completely self-contained — no external program needed
- Byte-identical after decompression
- Stub uses only syscalls (no libc dependency)
- Should run under any Linux configuration that can run ELF binaries
- Compressed executables should run under FreeBSD and other systems that run
  Linux binaries

## General Drawbacks on Linux

- Not advisable to compress programs with many simultaneous instances (like
  `sh` or `make`) because common segments won't be shared between processes
- `ldd` and `size` won't show useful output — they see only the statically
  linked stub
- Compression of suid, guid, and sticky-bit programs is rejected for security
- Executables that read data from themselves will not work
- In case of internal errors, the stub aborts with exit code 127. Run
  `strace -o strace.log compressed_file` for diagnostics

## Recommendations

- Strip executables before compression (UPX leaves the original untouched)
- Compressing scripts loses platform independence — be careful with NFS
- Medium-sized programs accessing about 1/3 to 1/2 of their stored bytes
  benefit most from compression
- Small programs save little absolute space
- Large programs where each invocation uses only a small fraction don't
  benefit proportionally since UPX decompresses the entire program
