# Python Versions

## Contents
- Requesting Python versions
- Installing Python
- Pinning Python
- Upgrading Python
- Managed vs system Python
- Discovery logic

## Requesting Python versions

Most uv commands accept `--python` with flexible formats:

| Format | Example | Description |
|--------|---------|-------------|
| Version | `3.12`, `3.12.3` | Specific version |
| Specifier | `>=3.12,<3.13` | Version range |
| Variant suffix | `3.13t`, `3.12.0d` | Short variant (t=freethreaded, d=debug) |
| Plus variant | `3.13+freethreaded` | Named variant |
| Implementation | `cpython`, `pypy` | By implementation name |
| Impl + version | `cpython@3.12`, `cp312` | Implementation with version |
| Full triplet | `cpython-3.12.3-macos-aarch64-none` | Exact build |
| Executable path | `/opt/bin/python3` | Specific interpreter |
| Directory | `/some/venv/` | Environment root |

```bash
# Create venv with specific Python
uv venv --python 3.12

# Run with PyPy
uv run --python pypy@3.8 python --version
```

## Installing Python

uv bundles downloadable CPython and PyPy distributions for macOS, Linux, and Windows. By default, uv auto-downloads missing versions — explicit install is optional.

```bash
# Install specific version
uv python install 3.12.3

# Install latest patch of minor version
uv python install 3.12

# Install by constraint
uv python install '>=3.8,<3.10'

# Install multiple versions
uv python install 3.9 3.10 3.11

# Install specific implementation
uv python install pypy
```

### Installed executables

`uv python install 3.12` creates `python3.12` in `~/.local/bin` (on PATH). To also create `python` and `python3`:

```bash
uv python install 3.12 --default
```

Executables prefer latest patch of each minor version. Adding `3.12.8` after `3.12.7` updates the symlink; adding `3.12.6` does not downgrade.

### Listing and removing

```bash
# List installed Python versions
uv python list

# List with paths
uv python list --paths

# Remove a managed Python
uv python uninstall 3.11
```

## Pinning Python

`.python-version` file sets the default Python version for uv commands. uv searches working directory upward, then user config directory.

```bash
# Pin in current directory
uv python pin 3.12
# Creates .python-version with "3.12"

# Pin globally (user config directory)
uv python pin --global 3.12
```

For projects needing multiple Python versions, use `.python-versions` file (one version per line). `uv python install` reads it and installs all listed versions.

Disable discovery with `--no-config`. uv does not search beyond project/workspace boundaries.

## Upgrading Python

Only supported for uv-managed CPython. Not supported for PyPy, GraalPy, or Pyodide.

```bash
# Upgrade to latest patch (e.g., 3.12.4 → 3.12.5)
uv python upgrade 3.12

# Upgrade all installed versions
uv python upgrade
```

Virtual environments using that Python are automatically upgraded to the new patch version, unless created with an explicit patch version like `uv venv -p 3.10.8`.

## Managed vs system Python

- **Managed**: Python installed by uv itself. Stored in uv's Python directory.
- **System**: All other Python installations (OS-provided, pyenv, conda, etc.).

uv discovers both types. Managed versions can be upgraded and uninstalled via uv commands. System versions are used as-is.

## Discovery logic

uv searches for Python in this order:

1. Explicit `--python` argument
2. `.python-version` file (current directory upward)
3. Project `requires-python` constraint
4. Active virtual environment
5. Managed Python installations
6. System Python on PATH
7. Auto-download if available

Auto-downloads can be disabled with the `python-downloads` setting or `UV_PYTHON_DOWNLOADS=never`.
