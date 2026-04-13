# Running Scripts

uv provides seamless script execution with automatic dependency management, supporting both inline metadata and ad-hoc dependencies.

## Basic Script Execution

### Run Script Without Dependencies

```bash
# Simple script
uv run example.py

# With arguments
uv run example.py arg1 arg2

# From stdin
echo 'print("hello")' | uv run -

# Using here-document
uv run - <<EOF
import os
print(os.getcwd())
EOF
```

### Run Script with Ad-hoc Dependencies

```bash
# Single dependency
uv run --with rich example.py

# Multiple dependencies
uv run --with rich --with requests example.py

# Version constraints
uv run --with 'rich>12,<13' example.py

# Exclude project dependencies
uv run --no-project --with rich example.py
```

## Inline Script Metadata (PEP 723)

Scripts can declare dependencies inline using TOML metadata blocks.

### Creating Scripts with Metadata

```bash
# Initialize script with Python version
uv init --script example.py --python 3.12

# Add dependencies to script
uv add --script example.py 'requests<3' 'rich'
```

### Script with Inline Dependencies

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://api.github.com")
pprint(resp.json())
```

### Running Script with Inline Metadata

```bash
# Make script executable
chmod +x example.py

# Run directly
./example.py

# Or with uv run
uv run example.py
```

### Shebang for Executable Scripts

```python
#!/usr/bin/env -S uv run --script

import sys
print(f"Python {sys.version}")
```

```bash
chmod +x script
./script
```

## Dependency Management

### Adding Dependencies to Scripts

```bash
# Add single dependency
uv add --script example.py requests

# Add multiple dependencies
uv add --script example.py 'requests<3' 'rich>=13'

# Add with version constraint
uv add --script example.py 'httpx>=0.25'

# Add git dependency
uv add --script example.py git+https://github.com/encode/httpx
```

### Removing Dependencies from Scripts

```bash
uv remove --script example.py requests
```

## Script in Project Context

When running scripts within a project (directory with `pyproject.toml`):

```bash
# Script uses project dependencies
uv run script.py

# Script ignores project dependencies
uv run --no-project script.py

# Script uses both project and additional dependencies
uv run --with extra-package script.py
```

### Important Behavior

When using inline script metadata, the script's dependencies take precedence over project dependencies:

```python
# /// script
# dependencies = ["requests"]
# ///
```

This script will use only `requests`, ignoring any project dependencies.

## Platform-Specific Dependencies

Scripts can declare platform-specific dependencies using environment markers:

```python
# /// script
# dependencies = [
#   "colorama; sys_platform == 'win32'",
#   "platformdirs",
# ]
# ///
```

## Python Version Requirements

Scripts can specify Python version requirements:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["anyio"]
# ///

# Use Python 3.12+ syntax
type Point = tuple[float, float]
```

uv will automatically download and use the required Python version if not installed.

## Common Patterns

### Data Processing Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "pandas>=2.0",
#   "numpy",
# ]
# requires-python = ">=3.10"
# ///

import pandas as pd

df = pd.read_csv("data.csv")
print(df.head())
```

### API Client Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "httpx[http2]>=0.25",
#   "rich",
# ]
# ///

import httpx
from rich.progress import track

urls = ["https://api.github.com", "https://api.npms.io"]

for url in track(urls, description="Fetching"):
    resp = httpx.get(url)
    print(f"{url}: {resp.status_code}")
```

### Development Tool Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "ruff>=0.3",
#   "mypy",
# ]
# ///

import subprocess

print("Running linters...")
subprocess.run(["ruff", "check", "."])
subprocess.run(["mypy", "."])
```

## Troubleshooting

### Script Not Found

Ensure script has execute permission:

```bash
chmod +x script.py
./script.py
```

### Dependencies Not Installing

Check for syntax errors in metadata block:

```python
# Correct format
# /// script
# dependencies = ["package"]
# ///

# Incorrect (missing dependencies field)
# /// script
# requires-python = ">=3.10"
# ///
```

### Python Version Mismatch

uv will download required Python version automatically. To disable:

```bash
uv run --no-managed-python script.py
```

## Best Practices

1. **Use inline metadata** for scripts that will be shared or versioned
2. **Pin Python versions** for reproducible behavior
3. **Use `--no-project`** when running standalone scripts in project directories
4. **Make scripts executable** with shebang for convenience
5. **Keep dependencies minimal** to reduce installation time

## Comparison: Script vs Project

| Feature | Script | Project |
|---------|--------|---------|
| Dependencies | Inline metadata or `--with` | `pyproject.toml` |
| Lockfile | Automatic (per-script) | `uv.lock` |
| Virtual environment | Isolated per-script | Shared `.venv` |
| Use case | One-off tasks, utilities | Full applications, libraries |
