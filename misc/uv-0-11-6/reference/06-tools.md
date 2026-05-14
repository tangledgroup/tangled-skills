# Tools

## Overview

Tools are Python packages that provide command-line interfaces. uv includes a dedicated interface for interacting with tools.

`uvx` is an alias for `uv tool run` — the two commands are exactly equivalent.

## Execution vs Installation

In most cases, executing with `uvx` is preferred over installing:

```bash
# Execute without persistent install (recommended)
uvx ruff check .

# Install for PATH availability
uv tool install ruff
ruff check .
```

Installing is useful when other programs need the tool on PATH, or in Docker images.

## Tool Environments

- `uvx` stores environments in the uv cache — disposable, recreated on cache clean
- `uv tool install` creates environments in the uv tools directory — persistent until uninstalled

Tool environments should **not** be mutated directly (e.g., with pip).

## Tool Versions

```bash
# Run specific version
uvx ruff@0.6.0 --version

# Run latest (refresh cache)
uvx ruff@latest --version

# Install specific version
uv tool install ruff==0.5.0

# Install latest
uv tool install ruff@latest
```

After first `uvx` invocation, the cached version is used unless `@latest` or `--isolated` is specified:

```bash
# Ignore installed version, use cache
uvx --isolated ruff --version
```

## Upgrading Tools

```bash
# Upgrade all packages in tool environment
uv tool upgrade black

# Upgrade a single package
uv tool upgrade black --upgrade-package click

# Reinstall all packages
uv tool upgrade black --reinstall

# Reinstall specific package
uv tool upgrade black --reinstall-package click
```

Upgrades respect original version constraints. To change constraints, reinstall:

```bash
uv tool install black>=24
```

## Including Additional Dependencies

During execution:

```bash
uvx --with <extra-package> <tool>
uvx -w httpx ruff  # shorthand
```

During installation:

```bash
uv tool install --with <extra-package> <tool-package>
```

Multiple `--with` options are supported. Specific versions can be requested.

## Installing Executables from Additional Packages

```bash
uv tool install --with-executables-from ansible-core,ansible-lint ansible
```

This installs all executables from the specified packages into the same tool environment.

## Listing and Uninstalling Tools

```bash
# List installed tools
uv tool list

# Show tool environment path
uv tool dir

# Uninstall a tool
uv tool uninstall ruff
```
