# Python Versions

uv installs and manages Python versions, eliminating the need for `pyenv` or system package managers.

## Installing Python

```bash
uv python install                    # latest stable
uv python install 3.12               # specific version
uv python install 3.11 3.12          # multiple versions
uv python install pypy@3.10          # alternative implementation
uv python install --default          # also install `python`/`python3` shims
```

Installed versions are added to PATH as `python3.X` executables.

## Version request formats

The `--python` flag accepts many formats:

```bash
uv venv --python 3.12                # major.minor
uv venv --python 3.12.3              # exact
uv venv --python '>=3.12,<3.13'      # range
uv venv --python cpython@3.12        # implementation
uv venv --python pypy@3.10           # PyPy
uv venv --python 3.13t               # freethreaded (3.13+freethreaded)
uv venv --python /opt/bin/python3    # explicit path
```

## .python-version file

Pin a default Python version per directory:

```bash
uv python pin 3.12                    # writes .python-version
uv python pin --global 3.12           # user-level config
```

uv searches for `.python-version` in current and parent directories, then the user config directory. Disable with `--no-config`.

## Automatic downloads

By default, uv downloads missing Python versions on demand:

```bash
uvx --python 3.12 python -c "print('hi')"  # downloads 3.12 if needed
uv venv                                     # downloads latest if none found
```

Disable automatic downloads:

```bash
export UV_PYTHON_DOWNLOADS=never
# or in pyproject.toml:
# [tool.uv]
# python-downloads = "never"
```

## Managed vs system Python

- **Managed Python** — installed by `uv python install`; stored in uv's internal directory
- **System Python** — any other installation (OS package, pyenv, homebrew, etc.)

uv discovers and uses system Python automatically. Force system-only:

```bash
uv run --no-managed-python script.py
```

Force managed-only (skip system interpreters):

```bash
# use explicit --python version that uv manages
```

## Upgrading Python

```bash
uv python upgrade 3.12               # latest patch for 3.12
uv python upgrade                    # all managed versions
```

## Listing and removing

```bash
uv python list                       # available + installed versions
uv python install --reinstall        # reinstall all managed versions
```

## Key behaviors

- uv does not depend on Python to run — it's a standalone Rust binary
- Multiple Python versions coexist without conflicts
- `.python-version` is compatible with `pyenv` format
- Managed Python uses [python-build-standalone](https://github.com/astral-sh/python-build-standalone) distributions
