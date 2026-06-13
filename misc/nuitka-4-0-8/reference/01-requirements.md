# Requirements

## C Compiler

Nuitka generates C code that must be compiled by a native C compiler. The generated code requires **C11** support (or **C++03** for Python 3.10 and older with MSVC as a workaround).

### Windows Compilers

- **Visual Studio 2022 or higher** — the default on Windows. Use English language pack for best results. Enforce with `--msvc=latest`.
- **MinGW64** — used with `--mingw64`. Must be the version Nuitka downloads itself to avoid toolchain breakage. Does not work with Python 3.13+.
- **Zig** — used with `--zig`. On Windows, currently limited to x64 (AMD64) Python. On other platforms, supports all architectures Zig covers.
- **Clang-cl** — provided by the Visual Studio installer. Enforce with `--clang` on Windows.
- **Clang from MinGW64** — use `--mingw64 --clang` to enforce this Clang.

### Linux Compilers

Use either GCC from the system, an installed Clang, or Zig.

### macOS Compilers

Use the system Clang compiler. Install Xcode via the Apple Store to ensure tools are available.

### FreeBSD and Other Platforms

Use Clang or GCC, ideally matching the system compiler. For other platforms, GCC 5.1+ is sufficient. Use back-ports such as EPEL or SCL on older distributions.

## Python

Nuitka supports **Python 3** (3.4 through 3.13) and **Python 2** (2.6, 2.7). It must be a standard CPython implementation — Nuitka is closely tied to CPython internals. Use the official Python from python.org when possible.

### Special Cases Requiring Two Python Installations

- **Python 3.4**: Additionally install Python 2 or Python 3.5+ for compile-time use, because SCons (which orchestrates C compilation) does not support Python 3.4.
- **Windows with Python 2**: clcache doesn't work with Python 2 on Windows. Install Python 3.5+ instead. Nuitka finds needed Python versions automatically (e.g., via Windows registry).
- **Onefile compression with Python 2.x**: Requires another Python 3 installation with the `zstandard` package available.

### Important Considerations

- **Moving binaries to other machines**: Only standalone, onefile, and app modes produce portable output. Accelerated mode (default) requires CPython on the target.
- **Binary filename suffix**: `.exe` on Windows. No suffix in standalone mode on other platforms, or `.bin` for onefile/accelerated mode. Change with `--output-filename`.
- **Module mode filenames**: Extension modules cannot be renamed — the filename and module name must match.
- **Homebrew Python (macOS)**: Supported but resulting binaries are not backward-portable.
- **Anaconda Python**: Supported, but some conda packages may need special handling. Report issues for fixes.
- **Microsoft Store Python**: Do not use — it doesn't work properly with Nuitka.
- **Pyenv on macOS**: Known not to work. Use Homebrew instead.

## Operating System

Nuitka supports: Android, Linux, FreeBSD, NetBSD, OpenBSD, macOS, and Windows (32-bit, 64-bit, ARM). The generated C code is highly portable, so other operating systems may work with minor adjustments.

Ensure the Python version matches the architecture of the C compiler — mismatched architectures produce cryptic errors.

## Architecture

Officially supported: **x86**, **x86_64 (AMD64)**, and **ARM**.

Nuitka generates portable C code without hardware-specific assumptions. Architectures supported by Debian or RHEL can be considered well-tested, including RISC-V.
