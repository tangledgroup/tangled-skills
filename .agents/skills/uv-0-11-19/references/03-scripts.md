# Scripts

uv supports running Python scripts with automatic dependency management via PEP 723 inline metadata.

## Inline metadata (PEP 723)

Dependencies are declared in a TOML block at the top of the script:

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

resp = requests.get("https://api.example.com/data")
pprint(resp.json())
```

## Managing script dependencies

```bash
uv init --script task.py              # scaffold with metadata block
uv add --script task.py requests      # add dependency
uv add --script task.py 'rich>=13'    # with constraint
uv run task.py                        # auto-resolves from inline metadata
```

## Running without inline metadata

For quick scripts without declared dependencies, use `--with`:

```bash
uv run --with rich example.py         # one-off dependency
uv run --with 'rich>12,<13' example.py  # versioned
uv run --no-project example.py        # skip project installation
```

Read from stdin:

```bash
echo 'print("hello")' | uv run -
```

## Shebang scripts

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
chmod +x greet
./greet
```

## Locking script dependencies

Scripts can have lockfiles for reproducibility:

```bash
uv lock --script task.py              # creates task.py.lock
uv run task.py                        # uses lockfile if present
```

Add `exclude-newer` to prevent future version drift:

```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2024-10-16T00:00:00Z"
# ///
```

## Python version per script

```bash
uv run --python 3.10 task.py          # run with specific Python
```

The script's `requires-python` field is respected automatically.

## GUI scripts (Windows)

`.pyw` files run via `pythonw` (no console window):

```bash
uv run example.pyw                    # GUI script
uv run --with PyQt5 app.pyw           # with dependencies
```

## Key behaviors

- Inline metadata scripts **ignore** surrounding project dependencies entirely
- `--no-project` is not needed when script has inline metadata
- uv creates ephemeral environments per script — no manual venv management
- Scripts can be locked independently from projects
