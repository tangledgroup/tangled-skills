# Python Versions

## Managed vs System Python

uv distinguishes between:

- **Managed Python** — Versions installed by uv itself
- **System Python** — All other installations (OS-provided, pyenv, etc.)

uv does not differentiate between OS-managed and tool-managed Pythons — a pyenv installation is still considered "system" in uv.

## Requesting a Version

Use `--python` flag in most commands:

```bash
uv venv --python 3.11.6
uv run --python 3.12 python script.py
```

Supported version request formats:

- `<version>` — `3`, `3.12`, `3.12.3`
- `<version-specifier>` — `>=3.12,<3.13`
- `<version><short-variant>` — `3.13t` (freethreaded), `3.12.0d` (debug)
- `<version>+<variant>` — `3.13+freethreaded`, `3.12.0+debug`
- `<implementation>` — `cpython`, `cp`
- `<implementation>@<version>` — `cpython@3.12`
- `<implementation><version>` — `cpython3.12`, `cp312`
- Full triplet — `cpython-3.12.3-macos-aarch64-none`
- Executable path — `/opt/homebrew/bin/python3`
- Executable name — `mypython3`
- Install directory — `/some/environment/`

By default, uv automatically downloads Python versions if not found on the system. Disable with `UV_PYTHON_DOWNLOADS=never`.

## Python Version Files

The `.python-version` file sets a default Python version request. uv searches from the working directory upward through parent directories, then checks the user configuration directory.

```bash
# Pin version in current directory
uv python pin 3.12

# Pin globally (user config directory)
uv python pin --global 3.12
```

Discovery can be disabled with `--no-config`. uv does not search beyond project/workspace boundaries (except user config).

## Installing Python Versions

uv bundles downloadable CPython and PyPy distributions for macOS, Linux, and Windows:

```bash
# Install specific version
uv python install 3.12.3

# Install latest patch
uv python install 3.12

# Install by constraint
uv python install '>=3.8,<3.10'

# Install multiple versions
uv python install 3.9 3.10 3.11

# Install PyPy
uv python install pypy
```

If a `.python-version` file is present, `uv python install` installs that version by default. A `.python-versions` file (plural) can list multiple versions for projects requiring several.

Available Python versions are frozen per uv release — upgrade uv to access newer Pythons.

### Python Executables

uv installs executables into PATH by default (e.g., `~/.local/bin/python3.12` on Unix):

```bash
# Add ~/.local/bin to PATH if needed
uv python update-shell

# Install generic python/python3 executables (experimental)
uv python install 3.12 --default
```

uv prefers the latest patch version of each minor version:

```bash
uv python install 3.12.7   # Adds python3.12
uv python install 3.12.6   # Does not update (older)
uv python install 3.12.8   # Updates python3.12
```

## Upgrading Python Versions

Transparent patch upgrades for managed Python:

```bash
# Upgrade specific version
uv python upgrade 3.12

# Upgrade all installed versions
uv python upgrade
```

Virtual environments are automatically upgraded to new patch versions. Explicitly pinned patch versions (e.g., `uv venv -p 3.10.8`) are not transparently upgraded.

Upgrades are implemented via minor-version symlinks/junctions pointing to specific patch directories.

## Listing and Uninstalling

```bash
# List installed Python versions
uv python list

# Uninstall a managed Python
uv python uninstall 3.11
```

## Project Python Versions

uv respects `requires-python` in `pyproject.toml` during project command invocations. The first compatible Python version is selected from available installations.
