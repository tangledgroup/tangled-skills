# Nuitka Package Configuration

## Introduction

Nuitka uses YAML configuration files to handle package-specific requirements for data files, DLLs, implicit imports, anti-bloat rules, and compatibility hacks. These files ship inside Nuitka under `plugins/standard/` and follow the naming pattern `*nuitka-package.config.yml`.

Configuration files are organized as:

- **`standard`** — entries for non-stdlib packages
- **`stdlib2`** — Python 2 standard library entries (modules removed in Python 3)
- **`stdlib3`** — Python 3 standard library entries

You can provide your own configuration with `--user-package-configuration-file=path/to/config.yml`.

## The YAML Configuration File

Configuration files use the following top-level keys:

### Data Files

Specify data files that must be included for a package to work correctly.

Features:

- **`file`** — single file path (relative to package)
- **`directory`** — entire directory
- **`recursive`** — include subdirectories
- **`when`** — conditional inclusion

Example:

```yaml
data-files:
  - file: data/config.json
    when:
      os: "Linux, Windows, Darwin"
```

### DLLs

Specify DLLs that must be included in standalone mode.

Features:

- **`file`** — DLL filename or path
- **`directory`** — search directory for DLLs
- **`recursive`** — include subdirectories
- **`when`** — conditional inclusion (OS, architecture, etc.)

Example:

```yaml
dlls:
  - file: libfoo.dll
    when:
      os: "Windows"
```

### EXEs

Specify executable files needed at runtime.

Example:

```yaml
exes:
  - file: helper.exe
    when:
      os: "Windows"
```

### Anti-Bloat

Remove unnecessary modules to reduce compilation time and output size.

Features:

- **`module`** — module name to exclude
- **`when`** — conditional exclusion

Example:

```yaml
anti-bloat:
  - module: some_package.tests
    when:
      mode: "standalone, onefile"
```

### Implicit Imports

Declare imports that a package makes but are not visible through static analysis (e.g., dynamic imports, entry points).

Features:

- **`module`** — the implicitly imported module name
- **`when`** — conditional inclusion

Example:

```yaml
implicit-imports:
  - module: some_dependency
    when:
      python-version: ">=3.8"
```

### Options

Apply Nuitka command-line options automatically for specific packages.

Features:

- **`option`** — the option to apply
- **`when`** — conditional application

Example:

```yaml
options:
  - option: --enable-plugin=numpy
    when:
      module-available: "numpy"
```

### Import Hacks

Compatibility hacks for packages with unusual import patterns.

Features:

- **`from-module`** — source module
- **`to-module`** — target module to include instead
- **`when`** — conditional application

### Variables and Constants

Define reusable values in configuration expressions.

Example:

```yaml
variables:
  MY_VAR: "some_value"
constants:
  - name: IS_WINDOWS
    value: "{OS} == 'Windows'"
```

## Expression Language

Configuration conditions use an expression language with access to several built-in values:

### OS Indications

- `{OS}` — operating system: `Linux`, `Windows`, `Darwin`, `FreeBSD`, `OpenBSD`
- Check specific OS: `os: "Windows"` or `os: "Linux, Windows"`

### Compilation Modes

- Check mode: `mode: "standalone"`, `mode: "onefile"`, `mode: "standalone, onefile"`

### Python Flavors

- Detect variant: `flavor: "Debian Python"`, `flavor: "Anaconda Python"`

### Package Versions

- Check installed package version: `package-version: "numpy>=1.20"`

### Python Versions

- Check Python version: `python-version: ">=3.8"`, `python-version: "<3.10"`

### Anti-Bloat Settings

- Reference anti-bloat state in conditions

### Python Flags

- Check active Python flags: `python-flag: "no_asserts"`

### Modules Available

- Check if a module is installed: `module-available: "requests"`

### Variable/Constant Values

- Reference custom variables and constants defined in the configuration

## When Conditions

The `when` key allows conditional application of any configuration entry. Multiple conditions can be combined:

```yaml
data-files:
  - file: platform_specific.dat
    when:
      os: "Windows"
      python-version: ">=3.8"
      mode: "standalone, onefile"
```

## Where Else to Look

- Nuitka's built-in configurations are in the `plugins/standard/` directory of the Nuitka installation
- User configuration files can be placed alongside your main script and referenced with `--user-package-configuration-file`
- Raise issues or PRs to improve package configuration coverage for third-party packages
