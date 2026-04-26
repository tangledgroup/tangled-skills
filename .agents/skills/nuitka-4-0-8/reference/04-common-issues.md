# Common Issues

## Deployment Mode

By default, Nuitka compiles in non-deployment mode with safety guards and helpers. Disable all helpers with `--deployment` or disable individually:

```bash
python -m nuitka --no-deployment-flag=flag-name program.py
```

### Fork Bombs (Self-execution)

After compilation, `sys.executable` points to the compiled binary. Packages like `multiprocessing`, `joblib`, or `loky` may attempt to re-execute the program with `-c` or `-m` arguments, causing recursive forking (fork bomb).

Error example:

```
./hello.dist/hello.bin -l fooL -m fooM
Error, the program tried to call itself with '-m' argument. Disable with '--no-deployment-flag=self-execution'.
```

Solutions:

- Ensure correct command line parsing in your program
- Use `--no-deployment-flag=self-execution` at compile time to disable the guard
- Consider using `--deployment` for production builds

## Windows Virus Scanners

Antivirus software may flag Nuitka-compiled binaries as suspicious. This is a common false positive for any tool that produces native executables from scripts. Solutions include:

- Add the binary to your antivirus whitelist
- Use code signing certificates
- Report false positives to the antivirus vendor

## Linux Standalone

On Linux, standalone mode bundles the Python interpreter and shared libraries. Ensure the target system has compatible glibc version. For maximum portability, compile on the oldest target system or use manylinux-compatible builds.

## Dynamic sys.path at Runtime

If your program modifies `sys.path` at runtime to load modules from non-standard locations, Nuitka won't see these imports at compile time. Solutions:

- Use `--include-module` or `--include-package` to explicitly include dynamically loaded modules
- Set `PYTHONPATH` at compilation time so Nuitka can discover the modules
- Use `--include-plugin-directory` for plugin directories

## Manual Python File Loading

If your code loads `.py` files manually (e.g., with `exec()` or custom importers), Nuitka cannot track these dependencies. You must explicitly include them with `--include-module`.

## Missing Data Files in Standalone

Nuitka tracks data files needed by popular packages, but coverage may be incomplete. If data files are missing:

- Use `--include-data-files` or `--include-data-dir` to add them
- Use `--include-package-data` for automatic detection
- Raise issues or PRs to improve Nuitka's built-in package configuration

## Missing DLLs/EXEs in Standalone

For dynamically loaded DLLs:

- Use `--include-data-files` with explicit paths
- Check the Nuitka Package Configuration for the relevant package
- Ensure the DLL is not being filtered as a code file

## Dependency Creep in Standalone

If your standalone build includes too many unnecessary modules:

- Use `--nofollow-import-to=pattern` to exclude specific modules
- Review the compilation report (`--report=report.html`)
- Be selective with `--include-module` rather than using broad `--follow-imports`

## Standalone: Finding Files

In standalone mode, the working directory and file paths may differ from development. Use absolute paths or paths relative to `sys.executable`:

```python
import os, sys
base_dir = os.path.dirname(sys.executable)
data_path = os.path.join(base_dir, "data", "config.json")
```

## Onefile: Finding Files

In onefile mode, the binary self-extracts to a temporary directory. `sys.executable` points to the extracted location. To find files:

```python
import os, sys
# The extracted directory (onefile temp)
base_dir = os.path.dirname(sys.executable)
```

Note that the temp directory may be cleaned up after program exit. Do not rely on it persisting.

## Windows Programs with No Console Give No Errors

When compiling GUI applications with `--disable-console`, error output is not visible. For debugging:

- Compile without `--disable-console` first
- Use `--output-filename` with a `.exe` extension
- Redirect stderr to a log file in your code

## Deep Copying Uncompiled Functions

Nuitka-compiled functions may not be compatible with `copy.deepcopy()`. If you need to deep copy functions, ensure they are included in the compilation or use alternative serialization approaches.

## Extension Modules Are Not Executable Directly

Extension modules (`.so`/`.pyd`) produced by `--module` mode cannot be executed directly. They must be imported by a Python program or another compiled binary.
