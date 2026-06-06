# Scripts

## Contents
- Running scripts
- Inline metadata
- Adding dependencies to scripts
- Script initialization

## Running scripts

`uv run` executes Python scripts in isolated environments. For scripts without dependencies:

```bash
# Run a script
uv run example.py

# With arguments
uv run example.py arg1 arg2

# From stdin
echo 'print("hello")' | uv run -

# Here-document
uv run - <<EOF
print("hello world!")
EOF
```

In a project directory, `uv run` installs the project first. Use `--no-project` to skip:

```bash
uv run --no-project example.py
```

Request one-off dependencies with `--with`:

```bash
uv run --with rich example.py
uv run --with 'rich>12,<13' --with httpx example.py
```

## Inline metadata

Python supports [inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/) — a block comment at the top of the file declaring dependencies and Python version:

```python
# /// script
# dependencies = ["httpx", "rich>=13"]
# requires-python = ">=3.10"
# ///

import httpx
from rich import print

resp = httpx.get("https://api.example.com/data")
print(resp.json())
```

When `uv run example.py` encounters inline metadata, it runs the script in an isolated environment with only the declared dependencies — separate from any project.

### Metadata fields

| Field | Description |
|-------|-------------|
| `dependencies` | List of package requirements |
| `requires-python` | Python version constraint |
| `python-version` | Specific Python version (deprecated, use requires-python) |
| `uv.sources` | Package sources (Git, path, etc.) |

## Adding dependencies to scripts

`uv add --script` adds inline metadata to an existing script:

```bash
# Add dependency to script
uv add --script example.py requests

# Adds the # /// script block if missing, updates dependencies list
```

This modifies the script file in place, adding or updating the inline metadata block.

## Script initialization

`uv init --script` creates a new script with inline metadata:

```bash
# Create script with Python version
uv init --script example.py --python 3.12

# Produces:
# # /// script
# # requires-python = ">=3.12"
# # dependencies = []
# # ///
```

## Scripts vs projects vs tools

| Use case | Command |
|----------|---------|
| Single file with its own dependencies | `uv run script.py` (with inline metadata) |
| Multi-file project with shared dependencies | `uv init` + `uv add` + `uv run` |
| CLI tool from PyPI | `uvx <tool>` or `uv tool install <tool>` |
| One-off command with temp dependency | `uv run --with <pkg> <command>` |
