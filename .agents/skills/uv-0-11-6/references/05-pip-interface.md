# pip Interface

uv provides a pip-compatible interface for legacy workflows and fine-grained control over package installation.

## Creating Virtual Environments

### Basic Environment Creation

```bash
# Create .venv in current directory
uv venv

# Create with custom name
uv venv my-env

# Create at specific path
uv venv /path/to/venv

# Specify Python version
uv venv --python 3.11
uv venv --python python3.12

# Use specific Python interpreter
uv venv --python /usr/bin/python3.11
```

### Environment Activation

**macOS and Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\activate
```

**fish shell:**
```bash
source .venv/bin/activate.fish
```

**Deactivate:**
```bash
deactivate
```

### Environment Discovery

uv discovers environments in this order:
1. `VIRTUAL_ENV` environment variable
2. `CONDA_PREFIX` (Conda environments)
3. `.venv` in current or parent directory

## Installing Packages

### Basic Installation

```bash
# Install single package
uv pip install requests

# Install multiple packages
uv pip install requests flask cors

# Install with version constraint
uv pip install 'requests>=2.28,<3'

# Install specific version
uv pip install 'requests==2.31.0'

# Install with extras
uv pip install 'requests[socks]'
uv pip install 'mypy[faster-cache,reports]'
```

### Installing from Files

```bash
# From requirements.txt
uv pip install -r requirements.txt

# From pyproject.toml
uv pip install -r pyproject.toml

# From pyproject.toml with extra
uv pip install -r pyproject.toml --extra dev

# From all extras
uv pip install -r pyproject.toml --all-extras

# From setup.py (legacy)
uv pip install -r setup.py

# Multiple files
uv pip install -r requirements.txt -r requirements-dev.txt
```

### Editable Installation

```bash
# Install current project in editable mode
uv pip install -e .

# Install specific directory in editable mode
uv pip install -e ./my-package

# Install with extras
uv pip install -e './my-package[dev]'
```

### Installing from Git

```bash
# From GitHub repository
uv pip install git+https://github.com/psf/requests

# Specific branch
uv pip install git+https://github.com/psf/requests@main

# Specific tag
uv pip install git+https://github.com/psf/requests@v2.31.0

# Specific commit
uv pip install git+https://github.com/psf/requests@abc123def

# With submodules
uv pip install git+https://github.com/user/repo#subdirectory=package
```

### Installing from Local Paths

```bash
# Install from directory
uv pip install ./my-package

# Install from wheel file
uv pip install my_package-1.0.0-py3-none-any.whl

# Install from source distribution
uv pip install my_package-1.0.0.tar.gz

# Install with PEP 440 direct reference
uv pip install 'my-package @ ./my-package'
```

## Compiling Requirements

### Basic Compilation

```bash
# Compile requirements.in to requirements.txt
uv pip compile requirements.in -o requirements.txt

# Compile pyproject.toml
uv pip compile pyproject.toml -o requirements.txt

# Multiple input files
uv pip compile requirements.in constraints.in -o requirements.txt

# From stdin
echo "requests" | uv pip compile - -o requirements.txt
```

### Compilation Options

```bash
# Include extras
uv pip compile pyproject.toml --extra dev -o requirements-dev.txt

# Include all extras
uv pip compile pyproject.toml --all-extras -o requirements-all.txt

# Include dependency group
uv pip compile --group lint -o requirements-lint.txt

# Specify Python version
uv pip compile requirements.in --python-version 3.12

# Specify platform
uv pip compile requirements.in --platform linux --arch x86_64

# Generate hash for security
uv pip compile requirements.in --generate-hashes
```

### Upgrading Dependencies

```bash
# Upgrade all dependencies
uv pip compile requirements.in --upgrade -o requirements.txt

# Upgrade specific package
uv pip compile requirements.in --upgrade-package requests -o requirements.txt

# Upgrade multiple packages
uv pip compile requirements.in --upgrade-package requests --upgrade-package flask
```

## Syncing Environments

### Basic Sync

```bash
# Sync environment with requirements.txt
uv pip sync requirements.txt

# Sync with pylock.toml (PEP 751)
uv pip sync pylock.toml

# Sync multiple files
uv pip sync requirements.txt requirements-dev.txt
```

### Sync Behavior

- Removes packages not in requirements file
- Upgrades/downgrades to match exact versions
- Ensures environment matches lockfile exactly

## Constraints and Overrides

### Using Constraints

Constraints limit versions without requiring installation:

```bash
# Create constraints file
echo "requests<2.30" > constraints.txt

# Use with compile
uv pip compile requirements.in --constraint constraints.txt

# Use with install
uv pip install -r requirements.txt --constraint constraints.txt
```

### Using Overrides

Overrides force specific versions regardless of dependencies:

```bash
# Create overrides file
echo "urllib3>=2.0" > overrides.txt

# Use with compile
uv pip compile requirements.in --override overrides.txt

# Useful for resolving conflicts
# If package A requires urllib3<2.0 but B requires urllib3>=2.0
```

### Build Constraints

Control build-time dependency versions:

```bash
# Create build constraints
echo "setuptools==68.0.0" > build-constraints.txt

# Use with compile
uv pip compile requirements.in --build-constraint build-constraints.txt
```

## Package Management

### Listing Packages

```bash
# List all installed packages
uv pip list

# List in freeze format
uv pip freeze

# List outdated packages
uv pip list --outdated

# Show specific package
uv pip show requests
```

### Uninstalling Packages

```bash
# Uninstall single package
uv pip uninstall requests

# Uninstall multiple packages
uv pip uninstall requests flask

# Uninstall from requirements file
uv pip uninstall -r requirements.txt
```

### Checking Environment

```bash
# Check for compatibility issues
uv pip check

# View dependency tree
uv pip tree

# Limit tree depth
uv pip tree --depth 2

# Show specific package tree
uv pip tree -p requests
```

## System Python Installation

### Installing to System Python

```bash
# Install to system Python (use with caution)
uv pip install --system requests

# Specify system interpreter
uv pip install --python /usr/bin/python3.12 --system requests

# Common in CI/CD and containers
```

### When to Use --system

- Containerized environments
- CI/CD pipelines
- Controlled environments where virtualenvs are not feasible
- **Not recommended for development** on local machines

## Advanced Options

### Index Configuration

```bash
# Use custom index URL
uv pip install --index-url https://test.pypi.org/simple requests

# Add extra index
uv pip install --extra-index-url https://test.pypi.org/simple requests

# Disable index
uv pip install --no-index --find-links ./packages requests
```

### Build Options

```bash
# No build isolation
uv pip install --no-build-isolation requests

# Prevent building from source
uv pip install --no-build requests

# Allow only specific packages to build
uv pip install --no-build --no-binary :none: requests
```

### Platform-Specific Installation

```bash
# Install for different platform
uv pip install --platform manylinux2014_x86_64 \
  --python-version 3.12 \
  --arch x86_64 \
  requests

# Useful for pre-building environments
```

## Troubleshooting

### Environment Not Found

```bash
# Create environment if missing
uv venv

# Set VIRTUAL_ENV explicitly
export VIRTUAL_ENV=/path/to/venv

# Use --python to specify interpreter
uv pip install --python /usr/bin/python3.12 requests
```

### Permission Errors

```bash
# Don't use sudo with uv
# Instead, use virtual environment or --system flag in containers

# For system installation in controlled environments
uv pip install --system package-name
```

### Build Failures

```bash
# Install build dependencies
uv pip install setuptools wheel cython

# No build isolation
uv pip install --no-build-isolation package-name

# Allow building from source
uv pip install --no-binary package-name
```

## Compatibility Notes

uv's pip interface is compatible with most common workflows but has some differences:

| pip | uv |
|-----|-----|
| `pip install` | `uv pip install` |
| `pip freeze` | `uv pip freeze` |
| `pip-compile` | `uv pip compile` |
| `pip-sync` | `uv pip sync` |
| `pip list` | `uv pip list` |
| `pip uninstall` | `uv pip uninstall` |

### Known Differences

1. **Virtual environments required** - uv requires venv by default (use `--system` to opt-out)
2. **Stricter dependency resolution** - uv may fail where pip succeeds with broken dependencies
3. **Faster performance** - 10-100x faster than pip for most operations
4. **Better error messages** - More detailed resolution conflict reporting

## Best Practices

1. **Use virtual environments** - Avoid `--system` flag in development
2. **Pin versions in requirements.txt** - Use exact versions for reproducibility
3. **Split dev and prod dependencies** - Use separate files or groups
4. **Use constraints for shared dependencies** - Prevent version conflicts
5. **Compile before sync** - Generate lockfiles before deploying
