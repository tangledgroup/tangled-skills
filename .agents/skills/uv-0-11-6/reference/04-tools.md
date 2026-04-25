# Using Tools

uv provides seamless tool management for Python packages that provide command-line executables, replacing pipx with faster performance and better integration.

## Running Tools Without Installation

### Using uvx (Recommended)

`uvx` is a convenient alias for `uv tool run`:

```bash
# Run tool in temporary environment
uvx ruff check .
uvx black --check .
uvx pycowsay "hello from uv"
```

### Using uv tool run

```bash
# Equivalent to uvx
uv tool run ruff check .

# With arguments
uv tool run mkdocs serve
```

### How It Works

- Tool is installed in isolated temporary environment
- Dependencies are cached for future runs
- No persistent installation required
- Automatic cleanup after execution

## Specifying Tool Versions

### Exact Version

```bash
# Using @ syntax
uvx ruff@0.3.0 check
uvx black@24.1.0 .

# Using --from flag
uvx --from 'ruff==0.3.0' ruff check
```

### Version Ranges

```bash
# Constrain to version range
uvx --from 'ruff>=0.2.0,<0.4.0' ruff check

# Latest version
uvx ruff@latest check
```

## Tools with Different Package Names

Some tools have executables with different names than their package:

```bash
# http command from httpie package
uvx --from httpie http

# Multiple examples
uvx --from awscli aws
uvx --from google-cloud-cli gcloud
```

## Installing Extras

Tools can include optional dependencies (extras):

```bash
# Install with single extra
uvx --from 'mypy[faster-cache]' mypy .

# Install with multiple extras
uvx --from 'mypy[faster-cache,reports]' mypy --xml-report report.xml

# Combine with version
uvx --from 'mypy[faster-cache]==1.13.0' mypy .
```

## Adding Additional Dependencies

Include plugin packages or additional tools:

```bash
# Add plugin to mkdocs
uvx --with mkdocs-material mkdocs serve

# Multiple additional dependencies
uvx --with sphinx --with sphinx-rtd-theme sphinx-build . _build

# Version-constrained plugins
uvx --with 'ruff>=0.3' ruff check .
```

## Installing from Alternative Sources

### Git Repositories

```bash
# Install from git repository
uvx --from git+https://github.com/httpie/cli httpie

# Specific branch
uvx --from git+https://github.com/httpie/cli@master httpie

# Specific tag
uvx --from git+https://github.com/httpie/cli@3.2.4 httpie

# Specific commit
uvx --from git+https://github.com/httpie/cli@2843b87 httpie
```

### Git LFS Support

```bash
uvx --lfs --from git+https://github.com/astral-sh/lfs-cowsay lfs-cowsay
```

### Local Paths

```bash
# Install from local directory
uvx --from ./local-tool tool-command
```

## Persistently Installing Tools

### Install Tool

```bash
# Install tool to persistent location
uv tool install ruff

# Install with version constraint
uv tool install 'black>=24.0'

# Install multiple executables from same package
uv tool install httpie  # Installs: http, https, httpie

# Install with extras
uv tool install 'mypy[faster-cache]'

# Install with additional dependencies
uv tool install mkdocs --with mkdocs-material
```

### Tool Installation Location

Tools are installed to a user-level directory and added to PATH:

**macOS and Linux:** `~/.local/bin`
**Windows:** `%LOCALAPPDATA%\uv\bin`

### Update Shell PATH

If tools are not found after installation:

```bash
# Update shell configuration
uv tool update-shell

# Manually add to PATH (macOS/Linux)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Manually add to PATH (Windows PowerShell)
$env:PATH += ";$HOME\.local\bin"
```

### Managing Installed Tools

```bash
# List installed tools
uv tool list

# Show installation directory
uv tool dir

# Uninstall tool
uv tool uninstall ruff

# Reinstall tool
uv tool install --reinstall ruff
```

## Upgrading Tools

```bash
# Upgrade specific tool
uv tool upgrade ruff

# Upgrade all tools
uv tool upgrade

# Upgrade with version constraint
uv tool install 'ruff>=0.4'  # Re-install to replace constraints
```

Tool upgrades respect original version constraints:

```bash
# Install with constraint
uv tool install 'ruff>=0.3,<0.4'

# Upgrade will stay within 0.3.x range
uv tool upgrade ruff
```

## Multiple Executables from One Package

Some packages provide multiple executables:

```bash
# httpie provides: http, https, httpie
uv tool install httpie

# All three commands are now available
http get https://httpbin.org/get
https post https://httpbin.org/post
httpie --version
```

### Installing Related Executables

Install executables from multiple related packages:

```bash
# Install ansible with related tools
uv tool install --with-executables-from ansible-core,ansible-lint ansible
```

## Common Tools and Usage

### Code Quality Tools

```bash
# Ruff (linter)
uvx ruff check .
uvx ruff format .

# Black (formatter)
uvx black .

# MyPy (type checker)
uvx --from 'mypy[faster-cache]' mypy .

# PyLint
uvx pylint my_package/
```

### Documentation Tools

```bash
# MkDocs
uvx --with mkdocs-material mkdocs serve

# Sphinx
uvx --with sphinx-rtd-theme sphinx-build . _build

# pdoc
uvx pdoc my_package
```

### Development Tools

```bash
# HTTPie (HTTP client)
uvx http get https://httpbin.org/get

# HTTPX (alternative)
uvx httpx https://httpbin.org/get

# Bandit (security audit)
uvx bandit -r .

# Vulture (dead code detection)
uvx vulture .
```

### Database Tools

```bash
# SQLite CLI
uvx sqlite3 database.db

# pgcli (PostgreSQL CLI)
uvx --from pgcli pgcli

# mysqlcli
uvx --from mycli mysqlcli
```

## Troubleshooting

### Tool Not Found After Installation

```bash
# Update shell PATH
uv tool update-shell

# Check installation directory
uv tool dir

# Verify tool is installed
uv tool list

# Reinstall if necessary
uv tool install --reinstall tool-name
```

### Version Mismatch

```bash
# Specify exact version
uvx ruff@0.3.0 check

# Or reinstall with version
uv tool install 'ruff==0.3.0'
```

### Dependencies Not Installing

```bash
# Clear cache
uv cache clean

# Force reinstall
uv tool install --reinstall tool-name

# Check Python version compatibility
uvx --from 'tool-name>=1.0' tool-name --version
```

## Best Practices

1. **Use `uvx` for one-off tools** - No persistent installation needed
2. **Install frequently-used tools** - Avoid repeated downloads
3. **Pin versions in CI/CD** - Ensure reproducible builds
4. **Use `--with` for plugins** - Keep tool and plugin versions aligned
5. **Update shell PATH once** - Run `uv tool update-shell` after first installation

## Comparison: uvx vs pipx

| Feature | uvx | pipx |
|---------|-----|------|
| Performance | 10-100x faster | Standard pip speed |
| Installation | Not required | Required |
| Dependency caching | Automatic | Manual |
| Version management | Built-in | Separate command |
| Python version management | Integrated | External (pyenv) |
