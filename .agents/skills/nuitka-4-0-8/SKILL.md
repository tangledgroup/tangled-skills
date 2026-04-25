---
name: nuitka-4-0-8
description: Python compiler that translates Python code to C and native executables. Use when compiling Python applications for distribution, creating extension modules, optimizing performance, or building standalone binaries across Windows, Linux, macOS, and FreeBSD.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - python-compiler
  - native-code
  - c-generation
  - standalone-executables
  - performance-optimization
  - cross-platform
  - extension-modules
category: compilation
required_environment_variables:
  - name: C compiler (gcc, clang, MSVC, or MinGW64)
    prompt: "Nuitka requires a C compiler. Which compiler should be used?"
    help: "Install gcc/clang on Linux/macOS, or Visual Studio/MinGW64 on Windows"
    required_for: "compilation"

external_references:
  - https://nuitka.net/doc/
  - https://github.com/Nuitka/Nuitka
---
## Overview
Python compiler that translates Python code to C and native executables. Use when compiling Python applications for distribution, creating extension modules, optimizing performance, or building standalone binaries across Windows, Linux, macOS, and FreeBSD.

Nuitka is **the** Python compiler. It translates Python modules into C-level programs that use `libpython` and static C files to execute in the same way as CPython does. Nuitka compiles every construct that Python 2 (2.6, 2.7) and Python 3 (3.4 - 3.14) have, when itself run with that Python version.

## When to Use
- **Distributing Python applications** without requiring Python installation
- **Creating extension modules** for performance-critical code paths
- **Optimizing application startup time** and runtime performance (up to 3.7x faster)
- **Building standalone executables** that bundle all dependencies
- **Creating onefile executables** - single file distributions
- **Protecting source code** by compiling to native code
- **Cross-platform deployment** (Windows, Linux, macOS, FreeBSD)
- **Reducing runtime overhead** through constant propagation and type inference

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### Prerequisites

1. **Python**: 2.6, 2.7 or 3.4 - 3.14 (CPython only, not PyPy/Jython)
2. **C Compiler** (one of):
   - `gcc` 5.1+ or `g++` 4.4+ (Linux/FreeBSD)
   - `clang` (macOS/FreeBSD)
   - Visual Studio 2022+ (Windows, recommended)
   - MinGW64 C11 compiler (Windows, auto-downloaded by Nuitka)
   - `zig` compiler with `--zig` flag (all platforms)

3. **Install Nuitka**:
   ```bash
   python -m pip install Nuitka
   python -m nuitka --version  # Verify installation
   ```

### Platform-Specific Notes

- **Windows**: Use MinGW64 (auto-downloaded) or Visual Studio 2022+. Avoid Windows App Store Python.
- **macOS**: Use Homebrew Python. Avoid pyenv (known incompatibility).
- **Linux**: Build on oldest target OS for maximum compatibility (glibc version matters).

## Usage Examples
### Basic Compilation

```bash
# Compile a single script to native code
python -m nuitka hello.py
# Creates: hello.bin (or hello.exe on Windows)

# Run the compiled binary
./hello.bin
```

### Standalone Mode (Distribution Ready)

```bash
# Create standalone application with all dependencies
python -m nuitka --standalone --follow-imports program.py
# Creates: program.dist/ folder containing executable and all dependencies

# Copy the entire .dist folder to target machine
```

See [Core Concepts](reference/01-core-concepts.md) for detailed compilation modes.

### Onefile Mode (Single Executable)

```bash
# Create single executable file (includes bootstrap unpacker)
python -m nuitka --onefile --follow-imports program.py
# Creates: program.bin (or program.exe on Windows)

# Distribute the single file - it unpacks to temp directory on execution
```

Refer to [Advanced Workflows](reference/02-advanced-workflows.md) for platform-specific deployment.

## Common Operations
### Extension Module Compilation

```bash
# Compile a module as importable extension
python -m nuitka --module some_module.py
# Creates: some_module.so (Linux/macOS) or some_module.pyd (Windows)

# Use instead of some_module.py - drop-in replacement
```

See [Module and Package Compilation](reference/03-module-compilation.md).

### Package Compilation

```bash
# Compile entire package recursively
python -m nuitka --standalone --follow-imports my_package

# Exclude test modules from compilation
python -m nuitka --standalone --follow-imports \
  --nofollow-import-to='*.tests' my_package
```

### Using Third-Party Library Plugins

```bash
# NumPy, SciPy, Pandas, Matplotlib
python -m nuitka --standalone --enable-plugin=numpy program.py

# PyQt5 applications
python -m nuitka --standalone --enable-plugin=pyqt5 \
  --include-qt-plugins=sensible gui_app.py

# PySide6 applications  
python -m nuitka --standalone --enable-plugin=pyside6 app.py

# TensorFlow
python -m nuitka --standalone --enable-plugin=tensorflow model.py

# ZeroMQ
python -m nuitka --standalone --enable-plugin=pyzmq zmq_app.py
```

Refer to [Plugin System](reference/04-plugins.md) for complete plugin list.

### Performance Optimization

```bash
# Enable Link-Time Optimization (LTO) for faster executables
python -m nuitka --lto=yes --standalone program.py

# Profile-Guided Optimization (requires two passes)
python -m nuitka --pgo-c --standalone program.py  # First pass: instrument
./program.dist/program                            # Run with typical workload
python -m nuitka --pgo-c=yes --standalone program.py  # Second pass: optimize
```

See [Performance Guide](reference/05-performance.md) for optimization strategies.

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Advanced Workflows](reference/02-advanced-workflows.md)
- [Module Compilation](reference/03-module-compilation.md)
- [Plugins](reference/04-plugins.md)
- [Performance](reference/05-performance.md)
- [Command Reference](reference/06-command-reference.md)
- [Troubleshooting](reference/07-troubleshooting.md)

## Troubleshooting
### Missing Data Files in Standalone Mode

```bash
# Include package data files
python -m nuitka --standalone --include-package-data=package_name program.py

# Include specific data directories
python -m nuitka --standalone --include-data-dir=/path/to/data=data program.py

# Include individual files
python -m nuitka --standalone --include-data-files=file.txt=file.txt program.py
```

### Missing DLLs on Windows

Use appropriate plugins for libraries that ship DLLs (numpy, pyzmq, etc.). Don't manually copy DLLs.

### Fork Bombs with Multiprocessing

Some packages relaunch via `sys.executable`, causing fork bombs:

```bash
# Disable self-execution protection if your app handles sys.argv properly
python -m nuitka --no-deployment-flag=self-execution program.py
```

Or add at program start:
```python
import os, sys
if "NUITKA_LAUNCH_TOKEN" not in os.environ:
    sys.exit("Fork bomb suspected")
del os.environ["NUITKA_LAUNCH_TOKEN"]
```

### Memory Issues During Compilation

```bash
# Use less memory (slower compilation)
python -m nuitka --low-memory program.py

# Limit parallel compilation jobs
python -m nuitka --jobs=1 program.py

# Disable LTO if assembler runs out of memory
python -m nuitka --lto=no program.py
```

See [Troubleshooting Guide](reference/07-troubleshooting.md) for comprehensive solutions.

## Important Notes
1. **Use `python -m nuitka`** to ensure correct Python interpreter is used
2. **Test with `--standalone` first** before using `--onefile` (easier debugging)
3. **Enable appropriate plugins** for third-party libraries in standalone mode
4. **Don't use `os.getcwd()`** for finding data files - use `__file__` or `__compiled__.containing_dir`
5. **Compilation reports** (`--report=compilation-report.xml`) help diagnose missing modules
6. **Deployment mode** provides helpful error messages - disable selectively with `--deployment`
7. **Static linking** is faster than dynamic - use `--static-libpython=yes` when possible
8. **Nuitka does not set `sys.frozen`** - use `__compiled__` attribute to detect compiled code

## Limitations (Non-Commercial)
This skill covers Nuitka's open-source features. Commercial-only features include:
- File embedding for data protection
- Traceback encryption (de-Jong-Stacks)
- Windows service creation
- Ethereum package support
- Container-based Linux builds
- Advanced anti-virus signature mitigation

For commercial features, see https://nuitka.net/doc/commercial.html

