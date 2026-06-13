# Supported Executable Formats

UPX 5.1.1 supports the following executable formats. All UPX binaries are
functionally equivalent — each version can handle all formats, so you only need
the build that runs on your host OS.

## Windows PE Formats

- **win32/pe** — 32-bit Windows PE executables and DLLs (i386)
- **win64/pe** — 64-bit Windows PE executables and DLLs (amd64, arm64)
- **arm/pe** — ARM Windows CE / mobile PE executables
- **wince/arm** — ARM executables for Windows CE

## Linux ELF Formats

- **linux/elf386** — 32-bit Linux ELF executables (i386)
- **linux/ElfAMD** — 64-bit Linux ELF executables (amd64/x86_64)
- **linux/ppc32** — 32-bit PowerPC Linux ELF
- **linux/armel** — ARM Linux ELF (little-endian, v4/v5)
- **arm64-linux** — ARM64/aarch64 Linux ELF
- **linux/mipsel** — MIPS little-endian Linux ELF (r3000, 32-bit)
- **mips-linux** — MIPS big-endian Linux ELF (r3000, 32-bit)
- **powerpc64-linux** — 64-bit PowerPC Linux ELF (big-endian)
- **powerpc64le-linux** — 64-bit PowerPC Linux ELF (little-endian)
- **linux/riscv64** — RISC-V 64-bit Linux ELF (added in 5.1.0)

### Linux Shared Libraries

ELF shared libraries are supported for i386, amd64, arm, arm64, mipsel, mips,
powerpc, powerpc64, and riscv64. The DT_INIT entry must exist and all info
needed by the runtime loader must be first in .text.

New in 5.1.1: MIPS r3000 (32-bit) shared libraries are now supported.

### Linux Kernel Formats

- **vmlinuz/386** — gzip-compressed bootable Linux kernel images
- **bvmlinuz/386** — same as vmlinuz/386 (big-endian variant)
- **vmlinux/386** — uncompressed Linux kernel build output

## BSD Formats

- **bsd/elf386** — FreeBSD, NetBSD, OpenBSD ELF executables (auto-detected via
  PT_NOTE or EI_OSABI)

## macOS / Darwin Formats

- **mach/i386** — 32-bit Mac OS X (i386)
- **mach/amd64** — 64-bit Mac OS X (x86_64)
- **mach/fat** — Universal binaries (i386 + PowerPC)
- **dylib/i386** — 32-bit shared libraries (.dylib) on Darwin
- **dylib/ppc32** — 32-bit PowerPC shared libraries on Darwin

Note: macOS support was disabled in UPX 4.2.0 pending compatibility fixes for
macOS 13+. Check the latest release notes for re-enabled support status.

## DOS Formats

- **dos/com** — 16-bit COM executables (max ~65100 bytes uncompressed)
- **dos/exe** — 16-bit EXE executables
- **dos/sys** — System files (max ~65350 bytes uncompressed)

## Other Formats

- **djgpp2/coff** — DJGPP COFF format (32-bit DOS, includes stubify functionality)
- **watcom/le** — Watcom LE format (DOS4G, DOS4GW, PMODE/W, DOS32a, CauseWay)
- **tmt/adam** — TMT Pascal compiler format
- **atari/tos** — Atari ST/TT Motorola 68000 executable format
- **ps1/exe** — Sony PlayStation (PSone) MIPS R3000 executable format

### EFI Format

- **efi** — EFI executables (PE x86, added in UPX 4.0.0)

## Format-Specific Notes

- Compressed DOS programs only work on a 286+ CPU unless --8086 is specified
- djgpp2/coff: UPX includes stubify functionality — use --coff to produce raw
  COFF output instead
- watcom/le: WDOS/X extender is partly supported; DLLs and LX format not
  supported
- ps1/exe: Maximum uncompressed size ~1.89 / ~7.60 MiB depending on options
- vmlinuz formats: Ensure "vmlinuz/386" or "bvmlinuz/386" is displayed during
  compression — otherwise a wrong format may have been used and the kernel
  won't boot
