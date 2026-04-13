# Nuitka Core Concepts

This reference covers fundamental Nuitka concepts, compilation modes, output formats, and how Nuitka transforms Python code.

## How Nuitka Works

Nuitka translates Python modules into C-level programs that:
- Use `libpython` (the CPython implementation library)
- Include static C files for execution infrastructure
- Execute in the same way as CPython does
- Maintain full compatibility with uncompiled Python code

### Compilation Pipeline

1. **Tree Building** (`nuitka.tree.Building`) - Parses Python source into AST
2. **Optimization** (`nuitka.optimization`) - Applies optimizations to AST
3. **Finalization** (`nuitka.finalization`) - Prepares tree for code generation
4. **Code Generation** (`nuitka.code_generation`) - Creates C code from AST
5. **C Compilation** - Compiles generated C to native binary

### Optimization Goals

- **Avoid overhead** where unnecessary
- **Maintain compatibility** - not aimed at removing Python semantics
- **Constant propagation** - determine values at compile time
- **Type inference** - detect and specialize string/int/list handling (in progress)

## Compilation Modes

### Acceleration Mode (Default)

```bash
python -m nuitka program.py
```

**Output**: `program.bin` (or `program.exe` on Windows)

**Characteristics**:
- Binary depends on Python installation
- Depends on C extension modules being installed
- Fast compilation, small output
- Use for personal use on development machine
- Not suitable for distribution to other machines

### Standalone Mode

```bash
python -m nuitka --standalone program.py
```

**Output**: `program.dist/` directory containing:
- Main executable (`program` or `program.exe`)
- Python shared library
- All imported modules (compiled and uncompiled)
- Required DLLs/shared libraries
- Data files (if specified)

**Characteristics**:
- Fully self-contained distribution
- Can be copied to other machines
- No Python installation required on target
- Larger output size
- Use for application distribution

### Onefile Mode

```bash
python -m nuitka --onefile program.py
```

**Output**: Single executable file `program.bin` (or `program.exe`)

**Characteristics**:
- All files packed into single executable
- Unpacks to temporary directory on execution
- Easy distribution (single file)
- Slightly slower startup (unpacking overhead)
- Temp directory location customizable with `--onefile-tempdir-spec`

**Important**: Test with `--standalone` first to ensure all dependencies are included, then switch to `--onefile`.

### Module Mode

```bash
python -m nuitka --module some_module.py
```

**Output**: Extension module (`some_module.so`, `.pyd`, or `.dll`)

**Characteristics**:
- Creates importable extension module
- Filename cannot be changed (Python requires specific entry point names)
- Can replace `some_module.py` with compiled version
- Cannot include other extension modules
- Must match Python version used for compilation

### App Mode (macOS only)

```bash
python -m nuitka --enable-plugin=tk-inter --onefile=app program.py
```

**Output**: `program.app` bundle

**Characteristics**:
- Creates macOS application bundle
- Double-click to run from Finder
- Supports app icons with `--macos-app-icon`
- Supports entitlements with `--macos-app-protected-resource`

## Output File Naming

### Windows
- Acceleration mode: `program.exe`
- Standalone mode: `program.dist/program.exe`
- Onefile mode: `program.exe`
- Module mode: `program.pyd`

### Linux/macOS/FreeBSD
- Acceleration mode: `program.bin`
- Standalone mode: `program.dist/program`
- Onefile mode: `program.bin`
- Module mode: `program.so`

**Custom naming**: Use `-o output_name` or `--output-filename=output_name`

## Import Control

### Follow Imports (Recursive Compilation)

```bash
# Follow all imports recursively
python -m nuitka --follow-imports program.py

# Follow specific modules only
python -m nuitka --follow-import-to=module1,module2 program.py

# Exclude specific modules from following
python -m nuitka --nofollow-import-to=tests,docs program.py
```

### Include Modules/Package

```bash
# Force include module (for dynamic imports)
python -m nuitka --include-module=pandas program.py

# Force include entire package
python -m nuitka --include-package=numpy program.py

# Include plugin directory (dynamic loading)
python -m nuitka --include-plugin-directory=plugins program.py
```

### Demotion (Uncompiled Modules)

Nuitka can "demote" modules to remain as Python files:
- Faster compilation time
- Useful for large third-party libraries
- Still works with standalone mode

```bash
# Demote specific module
python -m nuitka --demote=pandas program.py

# Demote pattern
python -m nuitka --demote='*tests*' program.py
```

## Data File Handling

### Finding Data Files in Compiled Code

**Standalone mode**:
```python
# Files near the executable
import os
data_path = os.path.join(__compiled__.containing_dir, "data.txt")

# Fallback for non-compiled execution
try:
    data_path = os.path.join(__compiled__.containing_dir, "data.txt")
except NameError:
    data_path = os.path.join(os.path.dirname(sys.argv[0]), "data.txt")
```

**Onefile mode**:
```python
# File near original executable (outside onefile)
external_file = os.path.join(os.path.dirname(sys.argv[0]), "config.ini")

# File inside onefile (unpacked to temp dir)
internal_file = os.path.join(os.path.dirname(__file__), "data.txt")

# Works for both standalone and onefile
try:
    data_file = os.path.join(__compiled__.containing_dir, "data.txt")
except NameError:
    data_file = os.path.join(os.path.dirname(sys.argv[0]), "data.txt")
```

**Important**: Never use `os.getcwd()` to find data files - working directory is unpredictable.

### Including Data Files

```bash
# Include package data (preferred)
python -m nuitka --include-package-data=package_name program.py

# Include data directory
python -m nuitka --include-data-dir=/path/to/resources=resources program.py

# Include individual files
python -m nuitka --include-data-files=config.ini=config.ini,logo.png=logo.png program.py
```

## Python Version Support

### Supported Versions
- **Python 2**: 2.6, 2.7 (feature parity reached)
- **Python 3**: 3.4 - 3.14 (feature parity for up to 3.13)

### Special Cases

**Python 3.4**: Requires another Python version (2.x or 3.5+) installed for Scons during compilation.

**Python 3.13+ on Windows**: MinGW64 does not work - must use MSVC.

**CPython only**: Nuitka requires CPython implementation details. PyPy, Jython, IronPython are not supported.

## Detecting Compiled Code

Nuitka does not set `sys.frozen` (unlike PyInstaller/cx_Freeze). Use these instead:

```python
# Check if current module was compiled
if hasattr(__compiled__, '__name__'):
    print("This module was compiled by Nuitka")

# Check if function was compiled
def my_function():
    pass

if hasattr(my_function, '__compiled__'):
    print("This function was compiled")

# Access original argv[0] in onefile mode
original_argv0 = getattr(__compiled__, 'original_argv0', None)
```

## Deployment Mode

Deployment mode adds safeguards and helpers for debugging:

```bash
# Default (deployment helpers enabled)
python -m nuitka program.py

# Disable all deployment helpers
python -m nuitka --deployment program.py

# Disable specific protection
python -m nuitka --no-deployment-flag=self-execution program.py
```

**Deployment features**:
- Prevents fork bombs from self-execution
- Improves error messages for missing imports
- Detects common misconfigurations
- Can be disabled selectively or entirely

## Compilation Reports

Generate detailed compilation analysis:

```bash
# XML report (recommended for bug reports)
python -m nuitka --report=compilation-report.xml program.py

# Custom template report
python -m nuitka --report-template=my_template.rst.j2:output.rst program.py

# Built-in license report
python -m nuitka --report=LicenseReport program.py
```

Reports include:
- Module inclusion/exclusion reasons
- Import attempts and failures
- Plugin influences
- Compilation timings
- Data file paths
- DLL dependencies

## Platform Compatibility

### Windows
- **Supported**: x86, x86_64, ARM
- **Compilers**: MSVC 2022+, MinGW64, clang-cl
- **Runtime**: Requires Visual C++ Redistributable on target (unless bundled)
- **Icons**: PNG or ICO files with `--windows-icon-from-ico`

### Linux
- **Supported**: x86, x86_64, ARM, RISC-V
- **Compilers**: gcc 5.1+, clang
- **Compatibility**: Build on oldest target OS (glibc version matters)
- **Static linking**: Possible with some Python builds

### macOS
- **Supported**: x86_64, arm64
- **Compiler**: clang (Xcode command line tools)
- **Python source**: Homebrew recommended, pyenv not supported
- **App bundles**: Full support with `--onefile=app`

### FreeBSD/NetBSD/OpenBSD
- **Supported**: x86, x86_64, ARM
- **Compiler**: clang
- **Status**: Generally good portability

## Architecture Matching

Nuitka automatically targets the architecture of the Python interpreter used:
- 64-bit Python → 64-bit binary
- 32-bit Python → 32-bit binary

Check architecture with:
```bash
python -m nuitka --version
# Output includes: Arch: x86_64 (or x86 for 32-bit)
```

**Important**: Match Python and C compiler architecture, or compilation will fail with cryptic errors.
