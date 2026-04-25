# Nuitka Command Reference

Complete reference for Nuitka command-line options, Nuitka Project syntax, and configuration patterns.

## Basic Commands

### Compile Script

```bash
# Basic compilation (acceleration mode)
python -m nuitka program.py

# With Python module flag
python -m nuitka -m package.module

# Specify output filename
python -m nuitka -o custom_name program.py
```

### Run and Compile

```bash
# Compile and execute immediately
python -m nuitka --run program.py --arg1 --arg2

# Using nuitka-run (shorthand for --run)
nuitka-run program.py --arg1 --arg2
```

## Output Mode Options

### --mode

Control compilation output mode:

```bash
# Acceleration mode (default) - binary needs Python installed
python -m nuitka --mode=accelerate program.py

# Standalone mode - self-contained distribution folder
python -m nuitka --mode=standalone program.py

# Onefile mode - single executable file
python -m nuitka --mode=onefile program.py

# Module mode - create importable extension module
python -m nuitka --mode=module program.py

# Package mode - compile package as extension
python -m nuitka --mode=package my_package
```

**Shorthand flags**:
```bash
--standalone    # Same as --mode=standalone
--onefile       # Same as --mode=onefile
--module        # Same as --mode=module
```

## Import Control Options

### --follow-imports

Recursively follow all imports:

```bash
python -m nuitka --follow-imports program.py
```

### --follow-import-to

Follow specific modules only:

```bash
python -m nuitka --follow-import-to=module1,module2 program.py
```

### --nofollow-imports

Don't follow any imports:

```bash
python -m nuitka --nofollow-imports program.py
```

### --nofollow-import-to

Exclude specific modules from following:

```bash
python -m nuitka --nofollow-import-to=tests,docs,'*.test*' program.py
```

### --include-module

Force include module (for dynamic imports):

```bash
python -m nuitka --include-module=dynamically_loaded program.py
```

### --include-package

Force include entire package:

```bash
python -m nuitka --include-package=large_package program.py
```

### --include-plugin-directory

Include directory with dynamically loaded plugins:

```bash
python -m nuitka --include-plugin-directory=plugins program.py
```

## Data File Options

### --include-data-files

Include specific data files:

```bash
python -m nuitka --include-data-files=config.ini=config.ini,logo.png=logo.png program.py

# With different destination names
python -m nuitka --include-data-files=path/to/source.txt=data/config.txt program.py
```

### --include-data-dir

Include entire directory:

```bash
python -m nuitka --include-data-dir=/path/to/assets=assets program.py
```

### --include-package-data

Include package data files:

```bash
python -m nuitka --include-package-data=my_package program.py
```

## Plugin Options

### --enable-plugin

Enable optional standard plugin:

```bash
# Enable single plugin
python -m nuitka --enable-plugin=numpy program.py

# Enable multiple plugins
python -m nuitka --enable-plugin=numpy --enable-plugin=tk-inter program.py

# With plugin options
python -m nuitka --enable-plugin=pyqt5 --include-qt-plugins=sensible program.py
```

### --disable-plugin

Disable standard plugin:

```bash
python -m nuitka --disable-plugin=plugin_name program.py
```

### --user-plugin

Load user plugin:

```bash
# Simple user plugin
python -m nuitka --user-plugin=my_plugin.py program.py

# With options
python -m nuitka --user-plugin=my_plugin.py=option1,option2 program.py
```

### --plugin-list

List available plugins:

```bash
python -m nuitka --plugin-list
```

## Optimization Options

### --lto

Link-Time Optimization:

```bash
# Enable LTO
python -m nuitka --lto=yes program.py

# Disable LTO
python -m nuitka --lto=no program.py

# Auto-detect (default)
python -m nuitka --lto=auto program.py
```

### --pgo-c

Profile-Guided Optimization:

```bash
# First pass: instrument
python -m nuitka --pgo-c program.py

# Run application to generate profile

# Second pass: optimize using profile
python -m nuitka --pgo-c=yes program.py
```

### --static-libpython

Static link Python library:

```bash
python -m nuitka --static-libpython=yes --standalone program.py
```

## Compiler Selection Options

### --mingw64

Use MinGW64 compiler (Windows):

```bash
python -m nuitka --mingw64 program.py
```

### --msvc

Use Microsoft Visual C++ compiler:

```bash
python -m nuitka --msvc=2022 program.py
python -m nuitka --msvc=latest program.py
```

### --clang

Use Clang compiler:

```bash
python -m nuitka --clang program.py
```

### --zig

Use Zig compiler:

```bash
python -m nuitka --zig program.py
```

## Platform-Specific Options

### Windows Options

#### Icon Options

```bash
# Set executable icon from ICO file
python -m nuitka --windows-icon-from-ico=app.ico program.py

# Set icon from PNG (auto-converted)
python -m nuitka --windows-icon-from-ico=app.png program.py

# Copy icon from template executable
python -m nuitka --windows-icon-template-exe=template.exe program.py
```

#### Version Information

```bash
python -m nuitka \
  --windows-company-name="My Company" \
  --windows-product-name="My App" \
  --windows-copyright="Copyright 2024" \
  --windows-file-description="Application description" \
  --windows-internal-name=myapp \
  program.py
```

#### Console Control

```bash
# Force console window
python -m nuitka --console=force program.py

# No console (default for GUI)
python -m nuitka --console=no program.py
```

#### Onefile Splash Screen

```bash
python -m nuitka --onefile-windows-splash-screen-image=splash.png program.py
```

### macOS Options

#### App Bundle

```bash
# Create app bundle
python -m nuitka --onefile=app program.py
```

#### App Icon

```bash
python -m nuitka --macos-app-icon=icon.icns --onefile=app program.py
```

#### Protected Resources (Entitlements)

```bash
python -m nuitka \
  --macos-app-protected-resource="NSMicrophoneUsageDescription:Need microphone access" \
  --onefile=app \
  program.py
```

### Linux Options

#### Icon

```bash
python -m nuitka --linux-icon=icon.png --standalone program.py
```

## Onefile-Specific Options

### --onefile-tempdir-spec

Control temporary directory location:

```bash
# Custom temp directory pattern
python -m nuitka --onefile-tempdir-spec=C:/Temp/MyApp-* program.py

# Use current directory
python -m nuitka --onefile-tempdir-spec=. program.py
```

### --onefile-keep-tempdir

Don't delete temporary directory after execution:

```bash
python -m nuitka --onefile --onefile-keep-tempdir program.py
```

### --onefile-compression

Control compression method:

```bash
# No compression (faster startup)
python -m nuitka --onefile --onefile-compression=no program.py

# Use zstandard compression
python -m nuitka --onefile --onefile-compression=zstd program.py
```

## Debugging and Development Options

### --debug

Enable debug mode:

```bash
python -m nuitka --debug program.py
```

### --verbose

Verbose output:

```bash
python -m nuitka --verbose program.py
```

### --show-modules

Show included modules:

```bash
python -m nuitka --show-modules program.py
```

### --show-progress

Show compilation progress:

```bash
python -m nuitka --show-progress program.py
```

### --show-memory

Show memory usage:

```bash
python -m nuitka --show-memory program.py
```

### --explain-imports

Explain import decisions:

```bash
python -m nuitka --explain-imports program.py
```

## Reporting Options

### --report

Generate compilation report:

```bash
# XML report (recommended)
python -m nuitka --report=compilation-report.xml program.py

# Custom template
python -m nuitka --report-template=my_template.rst.j2:output.rst program.py

# Built-in license report
python -m nuitka --report=LicenseReport program.py
```

## Resource Control Options

### --jobs

Control parallel compilation jobs:

```bash
# Use 4 parallel jobs
python -m nuitka --jobs=4 program.py

# Shorthand
python -m nuitka -j4 program.py
```

### --low-memory

Reduce memory usage:

```bash
python -m nuitka --low-memory program.py
```

## Compatibility Options

### --full-compat

Maximum compatibility mode:

```bash
python -m nuitka --full-compat program.py
```

### --python-flag

Emulate Python command-line flags:

```bash
# Optimize (like python -O)
python -m nuitka --python-flag=O program.py

# Multiple flags
python -m nuitka --python-flag=O --python-flag=S program.py
```

### --deployment

Disable deployment helpers:

```bash
# Disable all deployment protections
python -m nuitka --deployment program.py

# Disable specific protection
python -m nuitka --no-deployment-flag=self-execution program.py
```

## Output Control Options

### --output-dir

Set output directory:

```bash
python -m nuitka --output-dir=./build program.py
```

### --output-filename

Set output filename:

```bash
python -m nuitka --output-filename=custom_name program.py

# Shorthand
python -m nuitka -o custom_name program.py
```

### --remove-output

Remove build directory after compilation:

```bash
python -m nuitka --remove-output program.py
```

## Advanced Options

### --demote

Keep module uncompiled (as Python):

```bash
python -m nuitka --demote=pandas,numpy program.py
```

### --generate-c-only

Generate C code only (don't compile):

```bash
python -m nuitka --generate-c-only program.py
```

### --recompile-c-only

Recompile C code only (skip Python parsing):

```bash
python -m nuitka --recompile-c-only program.py
```

### --unstripped

Keep debug information in binary:

```bash
python -m nuitka --unstripped program.py
```

### --profile

Enable profiling support:

```bash
python -m nuitka --profile program.py
```

## Nuitka Project Syntax

### Inline Project Options

Add options directly in source file:

```python
# nuitka-project: --standalone
# nuitka-project: --enable-plugin=numpy
# nuitka-project: --include-data-files=config.ini=config.ini

def main():
    print("Hello")

if __name__ == "__main__":
    main()
```

### Conditional Options

```python
# nuitka-project-if: {OS} == "Windows"
#    nuitka-project: --windows-icon-from-ico=app.ico
# nuitka-project-else:
#    nuitka-project: --linux-icon=app.png

# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin")
#    nuitka-project: --mode=onefile
# nuitka-project-else:
#    nuitka-project: --mode=standalone
```

### Available Variables

| Variable | Description | Example Values |
|----------|-------------|----------------|
| `{OS}` | Operating system name | Windows, Linux, Darwin, FreeBSD |
| `{Version}` | Nuitka version | (1, 8, 0) |
| `{Commercial}` | Commercial version | (2, 0, 0) |
| `{Arch}` | Architecture | x86_64, arm64, x86 |
| `{MAIN_DIRECTORY}` | Directory of main script | /path/to/script |
| `{Flavor}` | Python variant | Debian Python, Anaconda Python |
| `{GIL}` | GIL enabled | True, False |

### Using Variables

```python
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/config.ini=config.ini
# nuitka-project: --user-package-configuration-file={MAIN_DIRECTORY}/config.yml

# nuitka-project-if: {OS} == "Windows" and {Arch} == "x86_64"
#    nuitka-project: --windows-icon-from-ico=icon_64.ico
```

### Project File

Create separate `.nuitka-project` file:

```yaml
# .nuitka-project
standalone: true
enable-plugin:
  - numpy
  - tk-inter
include-data-files:
  - config.ini=config.ini
  - data/data.json=data/data.json
```

## Common Command Patterns

### Quick Development

```bash
# Fast iteration (no LTO, demote dependencies)
python -m nuitka --demote=pandas,numpy program.py
```

### Production Build

```bash
# Optimized release build
python -m nuitka --standalone --lto=yes \
  --enable-plugin=numpy \
  --include-data-files=config.ini=config.ini \
  program.py
```

### Single File Distribution

```bash
# Onefile with icon and version info
python -m nuitka --onefile \
  --windows-icon-from-ico=app.ico \
  --windows-company-name="My Company" \
  --windows-product-name="My App" \
  --enable-plugin=numpy \
  program.py
```

### Cross-Platform Build

```bash
# Windows
python -m nuitka --onefile \
  --windows-icon-from-ico=app.ico \
  --enable-plugin=numpy \
  program.py

# macOS
python -m nuitka --onefile=app \
  --macos-app-icon=app.icns \
  --enable-plugin=numpy \
  program.py

# Linux
python -m nuitka --standalone \
  --linux-icon=app.png \
  --enable-plugin=numpy \
  program.py
```

### Extension Module

```bash
# Create importable extension
python -m nuitka --module fast_module.py

# Use in other scripts
python -c "import fast_module; print(fast_module.function())"
```

## Environment Variables

### Cache Control

```bash
# Set global cache directory
export NUITKA_CACHE_DIR=/path/to/cache

# Per-cache control
export NUITKA_CACHE_DIR_CCACHE=/fast/ssd/ccache
exportNuitka_CACHE_DIR_DOWNLOADS=/path/to/downloads
export NUITKA_CACHE_DIR_BYTECODE=/path/to/bytecode
export NUITKA_CACHE_DIR_DLL_DEPENDENCIES=/path/to/dll_cache
```

### CCache Binary

```bash
# Specify ccache location
export NUITKA_CCACHE_BINARY=/custom/path/ccache
```

## Getting Help

```bash
# Full help
python -m nuitka --help

# Version information
python -m nuitka --version

# List plugins
python -m nuitka --plugin-list

# Show system information
python -m nuitka --version
# Includes: Python version, architecture, compiler availability
```

## Tips and Tricks

### 1. Always Use `python -m nuitka`

Ensures correct Python interpreter is used:

```bash
# Good
python3.11 -m nuitka program.py

# Risky (might use wrong Python)
nuitka program.py
```

### 2. Test Standalone Before Onefile

```bash
# First verify with standalone
python -m nuitka --standalone program.py
./program.dist/program  # Test works

# Then create onefile
python -m nuitka --onefile program.py
```

### 3. Use Compilation Reports for Debugging

```bash
python -m nuitka --report=compilation-report.xml program.py
grep -i "error\|fail\|not found" compilation-report.xml
```

### 4. Conditional Compilation with Project Options

```python
# nuitka-project-if: {OS} == "Windows"
#    nuitka-project: --console=no
# nuitka-project-else:
#    nuitka-project: --console=force

def main():
    pass
```

### 5. Speed Up Development with CCache

```bash
# Install ccache
sudo apt install ccache  # Linux
brew install ccache      # macOS
# Windows: auto-downloaded by Nuitka

# Nuitka uses it automatically when in PATH
```
