# Python Versions Reference

## Requesting Python Versions

The `--python` flag accepts many formats:

```bash
uv venv --python 3.12                 # Major.minor
uv venv --python 3.12.3               # Exact version
uv venv --python '>=3.12,<3.13'       # Version range
uv venv --python cpython@3.12         # Implementation + version
uv venv --python cpython3.12          # Shorthand
uv venv --python cp312                # Shortest shorthand
uv venv --python pypy                 # PyPy (latest)
uv venv --python 3.13t                # Free-threaded Python 3.13
uv venv --python 3.13+freethreaded    # Free-threaded (explicit)
uv venv --python 3.12d                # Debug build
uv venv --python 3.12.0+debug         # Debug build (explicit)
uv venv --python /usr/bin/python3.12  # Specific executable
uv venv --python /path/to/venv/       # Directory of venv
```

Implementation names: `cpython`/`cp`, `pypy`/`pp`, `graalpy`/`gp`, `pyodide`, `pyemscripten`

## Installing Python Versions

uv bundles downloadable CPython and PyPy distributions. By default, uv auto-downloads Python when needed.

```bash
uv python install 3.12                # Latest patch of 3.12
uv python install 3.12.3              # Exact version
uv python install '>=3.8,<3.10'       # Range
uv python install 3.9 3.10 3.11      # Multiple versions
uv python install pypy                # PyPy
```

### Python executables on PATH

By default, `uv python install` creates executables in `~/.local/bin`:
```bash
uv python install 3.12                # Creates python3.12
uv python install 3.12 --default      # Also creates python, python3 (experimental)
uv python update-shell                # Add ~/.local/bin to PATH in shell config
```

### Upgrading Python versions

```bash
uv python upgrade 3.12                # Upgrade to latest patch
uv python upgrade                     # Upgrade all installed versions
```

Virtual environments are automatically upgraded to new patch versions (unless created with explicit patch version like `--python 3.10.8`).

## Managing Python Versions

```bash
uv python list                        # Show available + installed
uv python list 3.13                   # Filter by version
uv python list pypy                   # Filter by implementation
uv python list --all-versions         # Show all (incl. old patches)
uv python list --all-platforms        # Show other platforms
uv python list --only-installed       # Installed only
uv python find                        # Find first available Python
uv python find '>=3.11'               # Find matching version
uv python find --system               # Ignore venvs
uv python uninstall 3.9               # Remove a managed Python
```

## Python Version Files

`.python-version` sets the default Python for a project:
```bash
uv python pin 3.12                    # Create .python-version in current dir
uv python pin 3.12 --global           # Create in user config directory
```

uv searches for `.python-version` in the working directory and parent directories (not beyond project/workspace boundaries). A `.python-versions` file can list multiple versions for projects needing several interpreters.

Discovery is disabled with `--no-config`.

## Managed vs System Python

uv distinguishes between:
- **Managed Python** — Installed by uv itself
- **System Python** — Everything else (OS, pyenv, conda, etc.)

### Discovery order
1. Managed Python installations
2. `python`, `python3`, `python3.x` on PATH
3. Windows registry and Microsoft Store interpreters

### Preference settings

```toml
# pyproject.toml or uv.toml
[tool.uv]
python-preference = "managed"     # Default: prefer managed, but use system if available
python-preference = "only-managed"  # Only managed Python
python-preference = "system"      # Prefer system Python
python-preference = "only-system" # Only system Python
```

Command-line equivalents:
```bash
uv python list --managed-python     # Only managed
uv python list --no-managed-python  # Only system
```

### Disabling auto-downloads

By default, uv downloads Python automatically. Disable with:
```toml
[tool.uv]
python-downloads = "manual"    # Only during `uv python install`
```
Or: `uv <command> --no-python-downloads`

## Free-Threaded Python

For CPython 3.13+, free-threaded builds are available:
```bash
uv venv --python 3.13t                    # Short form
uv venv --python 3.13+freethreaded        # Explicit
uv venv --python 3.13+gil                 # Force GIL-enabled (for 3.14+)
```

- Python 3.13: free-threaded only when explicitly requested
- Python 3.14+: free-threaded available but GIL-enabled preferred by default

## Debug Builds

```bash
uv venv --python 3.13d                    # Short form
uv venv --python 3.13+debug               # Explicit
```

Debug builds are slower with assertions enabled. Useful for C-level debugging. Not appropriate for general use.

## Platform Support

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| CPython installs | ✅ | ✅ | ✅ |
| PyPy installs | ✅ | ✅ | ✅ |
| Free-threaded | ✅ | ✅ | ✅ |
| Debug builds | ✅ | ✅ | ✅ |
| Rosetta 2 (x86_64 on ARM) | ✅ | — | — |
| Windows on ARM emulation | — | — | ✅ |
| Windows registry registration | — | — | ✅ |
| PyEmscripten (PEP 783) | ✅ | ✅ | ✅ |
| Pyodide 2025 | ✅ | ✅ | ✅ |
