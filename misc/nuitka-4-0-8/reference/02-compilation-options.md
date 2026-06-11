# Compilation Options

## Command Line Usage

### Recommended Way

```bash
python -m nuitka [options] program.py
```

Using `python -m nuitka` ensures you know exactly which Python interpreter is being used. Replace `python` with the specific version, e.g., `python3.11 -m nuitka`.

### Direct Way

From a source checkout or archive:

```bash
python bin/nuitka [options] program.py
```

Or add the `bin/` directory to your PATH for convenience.

View available options with:

```bash
python -m nuitka --help
```

## Python Flags

The `--python-flag=flag` option changes specific Python behaviors during compilation or runtime:

- **`isolated`** — ignores `PYTHONPATH` and doesn't add user site-packages to `sys.path`. Isolates execution from the user's environment.
- **`main`** (short: `-m`) — compiles input as a Python package using `package/__main__.py` as entry point, mimicking `python -m package`.
- **`no_asserts`** (short: `-O`) — disables `assert` statements and sets `__debug__` to `False`.
- **`no_docstrings`** — discards docstrings at compile time, setting `__doc__` attributes to `None`. Reduces compiled code size.
- **`no_site`** (short: `-S`) — prevents automatic import of the `site` module. Default for standalone mode.
- **`no_warnings`** — suppresses runtime warnings from Python's `warnings` module.
- **`safe_path`** (short: `-P`) — prevents the current working directory from being added to module search path.
- **`static_hashes`** — disables hash randomization for deterministic behavior.
- **`unbuffered`** (short: `-u`) — forces `stdout` and `stderr` to be unbuffered.
- **`dont_write_bytecode`** (short: `-B`) — prevents `.pyc` file creation during execution. Not typically relevant for Nuitka as compiled modules don't use `.pyc`.

## Nuitka Project Options (Options in Code)

Embed Nuitka options directly in the source code using special comment directives. This is cleaner than maintaining a separate build script:

```python
# Compilation mode, support OS-specific options
# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin", "FreeBSD"):
#    nuitka-project: --mode=onefile
# nuitka-project-else:
#    nuitka-project: --mode=standalone

# Set variables dynamically and use them later
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project-set: MY_VERSION = __import__("mypkg").__version__
#    nuitka-project: --file-version={MY_VERSION}

# Enable plugins
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml
```

Supported directives:

- `nuitka-project:` — adds a command-line option
- `nuitka-project-if:` — conditional block (evaluated as Python expression)
- `nuitka-project-else:` — else branch for conditionals
- `nuitka-project-set: KEY = expression` — define a custom variable

Comments must be at the start of lines. Indentation inside comments marks the end of blocks, like Python.

### Pre-defined Variables

Variables available in `{variable}` expansion:

- **`{MAIN_DIRECTORY}`** — directory of the compiled file (useful for relative paths)
- **`{OS}`** — operating system name: `Linux`, `Windows`, `Darwin`, `FreeBSD`, `OpenBSD`
- **`{Version}`** — Nuitka version tuple, e.g., `(4, 0, 8)`
- **`{Commercial}`** — Nuitka Commercial version tuple
- **`{Arch}`** — architecture: `x86_64`, `arm64`, etc.
- **`{GIL}`** — boolean indicating whether Python has the GIL
- **`{Flavor}`** — Python variant, e.g., `Debian Python`, `Anaconda Python`

Example using `{MAIN_DIRECTORY}`:

```python
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/my_icon.png=my_icon.png
# nuitka-project: --user-package-configuration-file={MAIN_DIRECTORY}/user.nuitka-package.config.yml
```

## Data Files

Data files are non-code files (images, configs, text documents) that your program needs. Nuitka provides several options:

### Including Individual Files

```bash
python -m nuitka --follow-imports --include-data-files=icon.png=icon.png program.py
```

The source is a filesystem path; the target is relative within the output.

### Including Directories

```bash
# Copy a directory
python -m nuitka --follow-imports --include-data-dir=/path/to/images=images program.py

# With shell glob patterns
python -m nuitka --follow-imports --include-data-files=/etc/*.txt=etc/ program.py
```

### Package Data

```bash
python -m nuitka --follow-imports --include-package-data program.py
```

Auto-detects non-code data files of packages and copies them. Preferred over manual directory copying.

### Excluding Files

Use `--noinclude-data-files` to remove specific files from inclusion.

### Important: Code Is Not Data

Nuitka does not treat code files as data. The following are excluded from data file handling:

- `.py`, `.pyc`, `.pyo`, `.pyw` — use `--include-module` instead
- DLLs and executables — use `--include-data-files` with explicit paths if absolutely necessary (not recommended)
- Folders `site-packages`, `dist-packages`, `vendor-packages`, `__pycache__` are always ignored
- `.DS_Store` (non-macOS), `.pyi`, and `py.typed` are also ignored

## Tweaks

### Link-Time Optimization (LTO)

```bash
python -m nuitka --lto=yes program.py
```

Enables compiler-level optimizations across the entire compiled program. Significantly improves performance but increases compilation time.

### Profile-Guided Optimization (PGO)

```bash
python -m nuitka --pgo program.py
```

Uses runtime profiling to guide compiler optimizations. Requires running the program with typical workloads during the PGO training phase.

### Deployment Mode

```bash
python -m nuitka --deployment program.py
```

Disables all deployment safety helpers and guards. Use when the program is fully tested and you want maximum runtime performance without diagnostic overhead.

### Output Filename

```bash
python -m nuitka --output-filename=myapp program.py
```

Controls the output binary name. In module mode, the filename must match the module name.

## Compilation Report

Nuitka can generate a compilation report showing which modules were included and why:

```bash
python -m nuitka --report=report.html program.py
```

This produces an HTML report useful for understanding dependency inclusion and diagnosing missing modules.
