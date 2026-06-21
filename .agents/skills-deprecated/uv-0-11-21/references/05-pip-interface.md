# pip Interface Reference

The `uv pip` interface provides drop-in replacements for `pip`, `pip-tools`, and `virtualenv`. These commands work directly with virtual environments (unlike the project interface which manages environments automatically).

## Virtual Environments

### Creating environments
```bash
uv venv                                    # .venv with default Python
uv venv my-env                             # Named environment
uv venv --python 3.12                      # Specific Python version
uv venv --python pypy                      # PyPy
```

### Environment discovery order
1. `VIRTUAL_ENV` environment variable
2. `CONDA_PREFIX` (conda environments)
3. `.venv` in current or parent directories

If no environment found, uv prompts to create one with `uv venv`.

### Using arbitrary environments
```bash
VIRTUAL_ENV=/path/to/venv uv pip install flask
uv pip install --python /path/to/python flask
uv pip install --system flask              # System Python (CI/containers)
```

## Installing Packages

```bash
uv pip install flask                        # Basic install
uv pip install "flask[dotenv]"             # With extras
uv pip install flask ruff                   # Multiple packages
uv pip install 'ruff>=0.2.0'               # Version constraint
uv pip install 'ruff==0.3.0'               # Exact version
uv pip install "ruff @ ./projects/ruff"    # Local path
uv pip install "git+https://github.com/astral-sh/ruff"  # Git
uv pip install "git+https://github.com/astral-sh/ruff@v0.2.0"  # Git tag
uv pip install -e .                        # Editable (current dir)
uv pip install -e "ruff @ ./project/ruff"  # Editable (path)
```

### Installing from files
```bash
uv pip install -r requirements.txt          # Requirements file
uv pip install -r pyproject.toml            # pyproject.toml
uv pip install -r pyproject.toml --extra foo    # With extra
uv pip install -r pyproject.toml --all-extras   # All extras
uv pip install --group foo                  # Dependency group
uv pip install --project some/path/ --group foo  # From specific project
```

## Uninstalling Packages

```bash
uv pip uninstall flask
uv pip uninstall flask ruff                 # Multiple
```

## Compiling Requirements (Locking)

Replace `pip-compile` with `uv pip compile`:

```bash
uv pip compile requirements.in -o requirements.txt
uv pip compile pyproject.toml -o requirements.txt
uv pip compile setup.py -o requirements.txt
uv pip compile -                            # From stdin
echo "ruff" | uv pip compile -
uv pip compile requirements.in --extra foo
uv pip compile requirements.in --all-extras
uv pip compile requirements.in --group foo
```

### Upgrading compiled requirements
```bash
uv pip compile requirements.in -o requirements.txt --upgrade
uv pip compile requirements.in -o requirements.txt --upgrade-package ruff
```

### Universal resolution
```bash
uv pip compile requirements.in -o requirements.txt --universal
```

### Platform-specific resolution
```bash
uv pip compile requirements.in -o requirements.txt \
  --python-platform linux --python-version 3.10
```

## Syncing Environments

`uv pip sync` ensures the environment *exactly* matches the requirements file (removes extras):

```bash
uv pip sync requirements.txt                # From compiled file
uv pip sync pylock.toml                     # PEP 751 lockfile
```

Unlike `uv pip install`, `uv pip sync` removes packages not in the file. Use `uv pip install` when you want to add without removing.

## Constraints and Overrides

### Constraints (narrow versions, don't force inclusion)
```bash
# constraints.txt
pydantic<2.0
numpy>=1.24

uv pip compile requirements.in --constraint constraints.txt
uv pip install -r requirements.txt --constraint constraints.txt
```

### Build constraints (for build-time deps only)
```bash
# build-constraints.txt
setuptools==75.0.0

uv pip compile requirements.in --build-constraint build-constraints.txt
```

### Overrides (force versions, replace all declared requirements)
```bash
# overrides.txt
pydantic>=2.0        # Overrides any pydantic<2.0 from transitive deps

uv pip compile requirements.in --override overrides.txt
```

Overrides are absolute — they completely replace a package's requirements. Use when you know a dependency is compatible despite metadata saying otherwise.

## Inspecting Environments

```bash
uv pip list                              # List installed packages
uv pip list --find-links /path/to/wheels # With find-links source
uv pip freeze                            # Freeze (pip-compatible output)
uv pip show flask                        # Show package details
uv pip check                             # Check compatibility
uv pip tree                              # Dependency tree
```

## Key Differences from pip

| Feature | pip | uv pip |
|---------|-----|--------|
| Requires venv | Optional (`--target`) | Required by default |
| System install | `pip install --break-system-packages` | `uv pip install --system` |
| Compile speed | Slow | Very fast |
| Lock file format | `requirements.txt` only | `requirements.txt`, `pylock.toml` |
| Universal resolution | Not supported | `--universal` flag |
| Build isolation | Default | Default (PEP 517) |

## When to Use pip Interface vs Project Interface

| Use pip interface when: | Use project interface when: |
|------------------------|----------------------------|
| Legacy workflows with requirements.txt | Managing a full Python project |
| CI pipelines not ready for pyproject.toml | Need lockfile portability (uv.lock) |
| Ad-hoc package installation | Automatic environment management |
| Fine-grained control over env mutations | `uv run`, `uv add`, `uv sync` workflow |
| Migrating from pip/pip-tools gradually | Workspaces, dependency groups |
