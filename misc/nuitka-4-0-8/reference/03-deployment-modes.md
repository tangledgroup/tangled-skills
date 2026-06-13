# Deployment Modes

## Program Compilation (Acceleration)

Compile a whole program recursively with all modules embedded:

```bash
python -m nuitka --follow-imports program.py
```

Output: `program.exe` (Windows) or `program.bin` (other platforms). The binary still depends on CPython and used C extension modules being installed.

For dynamically loaded files not found via normal imports, use:

```bash
python -m nuitka --follow-imports --include-plugin-directory=plugin_dir program.py
```

Use `--include-plugin-directory` only for `__import__()` calls Nuitka cannot predict. For packages in your Python installation, use `--include-module` or `--include-package`.

## Extension Module Compilation

Compile a single module as a Python C extension:

```bash
python -m nuitka --module some_module.py
```

Output: `some_module.so` (Linux/macOS) or `some_module.pyd` (Windows). This can replace the `.py` source file.

Key constraints:

- The filename must not be changed — Python requires the entry point symbol `PyInit_some_module` to match the filename.
- Extension modules can only be loaded into CPython of the same version.
- An extension module cannot include other extension modules — use a wheel for that.
- If both source and compiled module exist in the same directory, the compiled version is loaded.

Use `--follow-import-to` to include additional modules, but they become importable only after importing the main module.

## Package Compilation

Compile an entire package with all embedded modules:

```bash
python -m nuitka --module some_package --include-package=some_package
```

The inclusion of package contents must be provided manually; otherwise the package is mostly empty. Use `--nofollow-import-to='*.tests'` to exclude unused parts like test code.

Data files inside the package are not embedded automatically — copy them manually or use Nuitka Commercial's file embedding feature.

## Standalone Program Distribution

Produce a self-contained distribution folder:

```bash
python -m nuitka --mode=standalone program.py
```

Output: `program.dist/` directory containing the compiled binary, embedded Python interpreter, and all dependencies. Copy the entire folder to any machine with the same OS/architecture.

`--follow-imports` is default in standalone mode. Exclude modules with `--nofollow-import-to`, but this raises `ImportError` at runtime if those modules are imported.

### Data Files in Standalone

- Use `--include-data-files=<source>=<target>` for individual files
- Use `--include-data-dir=<source>=<target>` for directories
- Use `--include-package-data` for automatic package data detection
- Manual copying into the `.dist` folder is also possible

## Onefile Mode

Create a single self-extracting executable:

```bash
python -m nuitka --mode=onefile program.py
```

This automatically includes standalone behavior. The binary extracts itself to a temporary directory at runtime before executing. Note that accessing files relative to the program path is impacted — see the Common Issues reference for details.

**Recommended workflow:** Always test with `--mode=standalone` first, then switch to onefile once everything works correctly.

## Setuptools Wheels

Nuitka can produce distribution wheels compatible with pip:

```bash
python -m nuitka --module --output-dir=dist some_package
```

This creates a wheel that can be distributed via PyPI or private package indexes. Extension modules and compiled packages are packaged as binary distributions.

## Multidist

For building multiple programs from the same source tree, Nuitka supports multidist mode to share common dependencies across outputs, reducing compilation time and output size.

## Building with GitHub Workflows

Use the [Nuitka-Action](https://github.com/Nuitka/Nuitka-Action) for CI/CD integration:

```yaml
- uses: Nuitka/Nuitka-Action@latest
  with:
    script-name: main.py
    onefile: true
```

This makes cross-platform compilation easy. Start with local compilation to iron out issues, then use Nuitka-Action for deployment to multiple platforms.

## Windows-Specific Distribution

For redistributing Windows standalone programs:

- The `program.dist/` folder contains everything needed
- On Windows, the executable is inside the `.dist` folder
- Use `--windows-icon-from-ico=icon.ico` to set a custom icon
- Use `--file-version=1.0.0` and related flags for Windows metadata
- Virus scanners may flag compiled binaries — add to whitelist or use code signing
