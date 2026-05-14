# Projects

## Project Structure and Files

### pyproject.toml

Python project metadata is defined in a `pyproject.toml` file. uv requires this file to identify the root directory of a project.

A minimal project definition includes a name and version:

```toml
[project]
name = "example"
version = "0.1.0"
```

Additional metadata and configuration includes Python version requirement, dependencies, build system, and entry points (commands).

### The Project Environment

When working on a project with uv, uv creates a virtual environment as needed. It manages a persistent environment in a `.venv` directory next to the `pyproject.toml`. The `.venv` is stored inside the project for editor discovery — it is automatically excluded from git with an internal `.gitignore`.

To run a command in the project environment, use `uv run`. Alternatively, the environment can be activated as normal.

It is **not** recommended to modify the project environment manually (e.g., with `uv pip install`). For project dependencies, use `uv add`. For one-off requirements, use `uvx` or `uv run --with`.

To disable automatic environment management:

```toml
[tool.uv]
managed = false
```

### The Lockfile

uv creates a `uv.lock` file next to the `pyproject.toml`. This is a universal (cross-platform) lockfile capturing packages across all possible Python markers (OS, architecture, Python version).

The lockfile should be checked into version control for reproducible installations. It is automatically created and updated during `uv sync` and `uv run`. It can also be explicitly updated with `uv lock`.

`uv.lock` is a human-readable TOML file managed by uv — it should not be edited manually.

### Relationship to pylock.toml

PEP 751 standardized `pylock.toml` as a resolution output format. uv supports `pylock.toml` as an export target:

```bash
# Export uv.lock to pylock.toml
uv export -o pylock.toml

# Generate pylock.toml from requirements
uv pip compile requirements.in -o pylock.toml

# Install from pylock.toml
uv pip sync pylock.toml
uv pip install -r pylock.toml
```

## Creating Projects

### Applications (Default)

Application projects are suitable for web servers, scripts, and CLIs:

```bash
uv init example-app
```

Creates:
- `pyproject.toml` — basic metadata, no build system
- `main.py` — sample file with a `main()` function
- `README.md`
- `.python-version` — Python version pin

The pyproject.toml for an application does not include a build system — it is not a package and will not be installed into the environment:

```toml
[project]
name = "example-app"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []
```

### Packaged Applications

For CLIs published to PyPI or projects needing a `src` layout, use `--package`:

```bash
uv init --package example-pkg
```

This creates a `src/` layout with a build system and command entry point:

```toml
[project]
name = "example-pkg"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
example-pkg = "example_pkg:main"

[build-system]
requires = ["uv_build>=0.11.7,<0.12"]
build-backend = "uv_build"
```

Run the command with `uv run example-pkg`.

### Libraries

Libraries are intended to be built and distributed (e.g., uploaded to PyPI):

```bash
uv init --lib example-lib
```

Using `--lib` implies `--package`. A `py.typed` marker is included to indicate types can be read from the library.

## Project Configuration

### Python Version Requirement

Set supported Python versions in `requires-python`:

```toml
[project]
name = "example"
version = "0.1.0"
requires-python = ">=3.12"
```

This determines allowed Python syntax and affects dependency version selection.

### Entry Points

Command-line interfaces:

```toml
[project.scripts]
hello = "example:hello"
```

Run with `uv run hello`.

GUI scripts (Windows-only difference — no console window):

```toml
[project.gui-scripts]
hello = "example:app"
```

Plugin entry points:

```toml
[project.entry-points.'example.plugins']
a = "example_plugin_a"
```

### Build Systems

A build system determines how the project is packaged and installed. uv uses the presence of a `[build-system]` table to determine if the project should be installed in the environment.

Without a build system, uv installs only dependencies. With one, it builds and installs the project itself.

Override packaging behavior:

```toml
[tool.uv]
package = true   # Force build/install even without build-system
package = false  # Skip build/install even with build-system
```

### Project Environment Path

Customize the virtual environment path:

```bash
UV_PROJECT_ENVIRONMENT=/path/to/venv uv sync
```

### Build Isolation

By default, uv builds packages in isolated environments per PEP 517. For packages needing the project environment (e.g., `flash-attn` needing matching PyTorch), use `extra-build-dependencies`:

```toml
[tool.uv]
extra-build-dependencies = ["torch"]
```

Or disable build isolation for specific packages with `no-build-isolation-package`.
