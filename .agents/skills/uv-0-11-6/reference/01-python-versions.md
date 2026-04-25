# Python Versions

uv provides comprehensive Python version management, including installation, discovery, and automatic downloads.

## Installing Python

### Install Latest Version

```bash
uv python install
```

This installs the latest stable Python version and adds it to your PATH as `python3.13` (or current latest).

### Install Specific Versions

```bash
# Install specific version
uv python install 3.12

# Install multiple versions at once
uv python install 3.10 3.11 3.12

# Install PyPy
uv python install pypy@3.10

# Install with default shims (python, python3)
uv python install --default
```

### Reinstall Python

```bash
# Reinstall all managed Python versions
uv python install --reinstall

# Reinstall specific version
uv python install --reinstall 3.12
```

## Viewing Python Installations

```bash
# List all available and installed versions
uv python list

# Output shows:
# - Installed versions (marked with checkmark)
# - Available versions for installation
# - Platform compatibility
```

## Automatic Python Downloads

uv automatically downloads Python when needed:

```bash
# This will download Python 3.12 if not installed
uvx python@3.12 -c "print('hello')"

# Creating venv without Python installed will download it
uv venv
```

### Disable Automatic Downloads

```bash
# Set environment variable
export UV_PYTHON_DOWNLOADS=never

# Or use flag
uv venv --no-managed-python
```

## Python Discovery

uv discovers Python versions in this order:

1. Explicitly requested version (e.g., `--python 3.12`)
2. Pinned version in `.python-version` file
3. Activated virtual environment (`VIRTUAL_ENV`)
4. Activated Conda environment (`CONDA_PREFIX`)
5. Virtual environment at `.venv` in current or parent directory
6. Managed Python installations
7. System Python installations

### Pin Python Version for Project

```bash
# Pin to specific version
uv python pin 3.12

# Creates .python-version file with pinned version
cat .python-version
# Output: 3.12
```

## Using Existing Python

uv automatically detects and uses system Python installations:

```bash
# Force use of system Python only
uv sync --no-managed-python

# Use specific Python interpreter
uv pip install --python /usr/bin/python3.11 requests

# Use Python from virtual environment
uv pip install --python /path/to/venv requests
```

## Upgrading Python Versions

Upgrade to latest patch release (preview feature):

```bash
# Upgrade specific version
uv python upgrade 3.12

# Upgrade all managed versions
uv python upgrade
```

## Uninstalling Python

```bash
# Uninstall specific version
uv python uninstall 3.11

# Uninstall all managed versions
uv python uninstall --all
```

## Finding Python Installations

```bash
# Find Python installation path
uv python find 3.12

# Show directory where uv installs Python
uv python dir
```

## Managed Python Distributions

uv uses Python distributions from the Astral `python-build-standalone` project since Python does not publish official distributable binaries.

### Available Implementations

- CPython (3.7 through latest)
- PyPy (various versions)
- Platform-specific builds for macOS, Linux, Windows

### Installation Locations

**macOS and Linux:**
```bash
uv python dir
# Output: ~/.local/share/uv/python
```

**Windows:**
```powershell
uv python dir
# Output: %LOCALAPPDATA%\uv\python
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `UV_PYTHON_DOWNLOADS` | Control automatic downloads | `auto`, `manual`, `never` |
| `UV_MANAGED_PYTHON` | Enable/disable managed Python | `1` or `0` |
| `UV_PYTHON` | Path to Python interpreter | `/usr/bin/python3.12` |

## Common Issues

### Python Not Found After Installation

Ensure uv is in your PATH:

```bash
# macOS and Linux
export PATH="$HOME/.local/bin:$PATH"

# Windows (PowerShell)
$env:PATH += ";$HOME\.local\bin"
```

### Multiple Python Versions Conflicting

Use explicit version pinning:

```bash
# Pin project to specific version
uv python pin 3.12

# Or specify in pyproject.toml
# [project]
# requires-python = ">=3.12,<4"
```

### System Python vs Managed Python

To prefer system Python:

```bash
uv sync --no-managed-python
```

To use managed Python only:

```bash
export UV_PYTHON_DOWNLOADS=manual
uv python install 3.12
```
