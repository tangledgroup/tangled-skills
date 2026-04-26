---
name: nuitka-4-0-8
description: Python compiler that translates Python code to C and native executables. Use when compiling Python applications for distribution, creating extension modules, optimizing performance, or building standalone binaries across Windows, Linux, macOS, and FreeBSD.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.0.8"
tags:
  - python
  - compiler
  - c-extension
  - standalone
  - onefile
  - performance
  - distribution
category: tooling
external_references:
  - https://nuitka.net/doc/
  - https://github.com/Nuitka/Nuitka
---

# Nuitka 4.0.8

## Overview

Nuitka is the optimizing Python compiler written in Python that creates executables that run without a separate installer. It compiles Python source code to C, then to native machine code, producing standalone binaries, extension modules, or accelerated programs. Data files can be included alongside or embedded within the output.

Nuitka 4.0.8 is the current stable release. It is fully compatible with Python 3 (3.4 through 3.13) and Python 2 (2.6, 2.7), and works on Windows, macOS, Linux, FreeBSD, NetBSD, OpenBSD, and Android.

## When to Use

- Compiling Python applications into standalone executables for distribution without requiring Python installation
- Creating Python extension modules (`.so`/`.pyd`) for performance-critical code
- Accelerating Python programs by compiling them to native C code
- Building single-file executables with `--mode=onefile` for easy deployment
- Protecting intellectual property by converting source code to compiled binaries
- Producing Setuptools-compatible wheels from Python packages
- Compiling programs for multiple platforms via GitHub Actions with Nuitka-Action

## Core Concepts

### Compilation Modes

Nuitka supports several compilation modes that determine the output and its portability:

- **Accelerated mode** (default) — compiles Python to C and links as a native binary. Still depends on CPython being installed on the target system.
- **`--mode=standalone`** — produces a distribution folder (`.dist`) containing the compiled binary, embedded Python interpreter, and all dependencies. Copy the entire folder to another machine.
- **`--mode=onefile`** — creates a single executable that self-extracts at runtime. Includes standalone behavior automatically.
- **`--mode=app`** — macOS-specific mode for creating `.app` bundles.

### Import Following

By default, Nuitka compiles only the entry-point file. Use `--follow-imports` to recursively compile all imported modules into the binary. Fine-grained controls include:

- `--include-module=modname` — force-include a specific module
- `--include-package=pkgname` — include an entire package
- `--nofollow-import-to=pattern` — exclude matching modules from compilation
- `--include-plugin-directory=path` — include a directory for dynamically loaded plugins

### C Compiler Requirements

Nuitka generates C code that must be compiled by a native C compiler:

- **Windows:** Visual Studio 2022+ (default, use `--msvc=latest`), MinGW64 (`--mingw64`, not for Python 3.13+), Zig (`--zig`), or Clang-cl
- **Linux:** GCC or Clang from the system, or Zig
- **macOS:** System Clang (install Xcode command-line tools)
- **FreeBSD/other:** Clang or GCC 5.1+

The compiler must support C11 (or C++03 for Python 3.10 and older with MSVC).

### Supported Architectures

x86, x86_64 (AMD64), and ARM are officially supported. Nuitka generates portable C code, so other architectures such as RISC-V typically work out of the box.

## Installation / Setup

Nuitka is installed via pip from PyPI:

```bash
# Standard version with minimal dependencies
python -m pip install -U Nuitka

# With onefile/app support dependencies
python -m pip install -U "Nuitka[app]"

# With all optional dependencies
python -m pip install -U "Nuitka[all]"
```

Alternatively, use `uv`:

```bash
uv add Nuitka
uv add "Nuitka[all]"
```

All Nuitka dependencies are optional — it detects what is available and works with whatever is installed.

## Usage Examples

### Basic Compilation

```bash
# Recommended way — ensures correct Python interpreter
python -m nuitka --follow-imports myprogram.py
```

This produces `myprogram.exe` (Windows) or `myprogram.bin` (other platforms).

### Standalone Distribution

```bash
python -m nuitka --mode=standalone myprogram.py
```

Produces a `myprogram.dist/` folder. Copy the entire folder to distribute.

### Single-File Executable

```bash
python -m nuitka --mode=onefile myprogram.py
```

Creates a single self-extracting binary. Test with standalone mode first for easier debugging.

### Extension Module

```bash
python -m nuitka --module some_module.py
```

Produces `some_module.so` (Linux/macOS) or `some_module.pyd` (Windows). The filename must match the module name.

### Package Compilation

```bash
python -m nuitka --module some_package --include-package=some_package
```

Compiles an entire package with all its modules embedded.

### Including Data Files

```bash
# Single file
python -m nuitka --follow-imports --include-data-files=icon.png=icon.png program.py

# Directory of files
python -m nuitka --follow-imports --include-data-dir=/path/to/images=images program.py

# With shell glob patterns
python -m nuitka --follow-imports --include-data-files=/etc/*.txt=etc/ program.py

# Package data (auto-detects non-code files)
python -m nuitka --follow-imports --include-package-data program.py
```

### Performance Optimization

```bash
# With Link-Time Optimization
python -m nuitka --follow-imports --lto=yes program.py

# With Profile-Guided Optimization
python -m nuitka --follow-imports --pgo program.py

# Both LTO and PGO for maximum performance
python -m nuitka --follow-imports --lto=yes --pgo program.py
```

## Advanced Topics

**Requirements and System Setup**: C compilers, Python versions, operating systems, and architectures → [Requirements](reference/01-requirements.md)

**Compilation Options Reference**: Python flags, project options in code, data files, tweaks, and compilation reports → [Compilation Options](reference/02-compilation-options.md)

**Deployment Modes and Use Cases**: Standalone distribution, onefile mode, extension modules, package compilation, Setuptools wheels, and multidist → [Deployment Modes](reference/03-deployment-modes.md)

**Common Issues and Solutions**: Deployment mode helpers, fork bombs, missing data files, dynamic sys.path, virus scanners, and debugging tips → [Common Issues](reference/04-common-issues.md)

**Nuitka Package Configuration**: YAML-based package configuration for data files, DLLs, implicit imports, anti-bloat, and compatibility hacks → [Package Configuration](reference/05-package-configuration.md)

**Performance Guide**: Benchmark expectations, LTO and PGO results, optimization tips, and compiler selection → [Performance](reference/06-performance.md)
