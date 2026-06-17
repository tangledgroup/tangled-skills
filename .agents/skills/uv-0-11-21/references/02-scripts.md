# Scripts Reference

## Running Scripts Without Dependencies

```bash
uv run script.py                    # Simple script
uv run script.py arg1 arg2          # With arguments
echo 'print("hello")' | uv run -    # From stdin
```

Inside a project, `uv run` installs the project first. Use `--no-project` to skip:
```bash
uv run --no-project script.py       # Ignore project dependencies
```

## Inline Script Metadata (PEP 723)

Scripts can declare dependencies directly in the file:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://example.com")
pprint(resp.status_code)
```

### Managing script dependencies

```bash
uv init --script example.py --python 3.12   # Initialize with metadata block
uv add --script example.py 'requests<3'     # Add dependency
uv add --script example.py rich             # Add another
uv remove --script example.py requests      # Remove
```

### Running scripts with inline metadata

```bash
uv run example.py                           # Auto-reads metadata, creates isolated env
uv run --python 3.10 example.py             # Override Python version
```

**Important:** Scripts with inline metadata run *isolated* from any project environment. The project's dependencies are ignored even if the script is inside a project directory.

## Locking Script Dependencies

```bash
uv lock --script example.py                 # Creates example.py.lock
```

Once locked, subsequent `uv run`, `uv add --script`, `uv export --script` reuse the lockfile.

## Reproducible Scripts

Add `exclude-newer` to the inline metadata:
```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2024-01-15T00:00:00Z"
# ///
```

## Executable Scripts (Shebangs)

Make scripts executable without `uv run`:
```python
#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx
print(httpx.get("https://example.com"))
```

```bash
chmod +x my-script
./my-script
```

## GUI Scripts (Windows)

Scripts ending in `.pyw` run with `pythonw` (no console window):
```bash
uv run app.pyw
uv run --with PyQt5 gui_app.pyw
```

## Alternative Indexes for Scripts

```bash
uv add --index "https://private.pypi/simple" --script example.py 'mypackage'
```

This includes the index in the inline metadata:
```python
# /// script
# dependencies = ["mypackage"]
# [[tool.uv.index]]
# url = "https://private.pypi/simple"
# ///
```

## Script vs Project Behavior

| Aspect | Script (inline metadata) | Project |
|--------|--------------------------|---------|
| Dependencies | Declared in script header | `pyproject.toml` |
| Environment | Isolated per-script | Shared `.venv/` |
| Lockfile | `<script>.py.lock` (explicit) | `uv.lock` (auto) |
| Project deps | Ignored | Available |
| `--no-project` | Not needed | Use to ignore project |
