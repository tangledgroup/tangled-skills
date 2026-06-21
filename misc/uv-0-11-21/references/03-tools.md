# Tools Reference

## Running Tools (Ephemeral)

`uvx` is an alias for `uv tool run`. Both create a temporary, cached environment.

```bash
uvx ruff check .                     # Run latest cached version
uvx ruff@0.6.0 check .               # Specific version
uvx ruff@latest check .              # Force latest (refresh cache)
uvx pycowsay hello                   # Simple tool invocation
```

### Commands with different package names

When the command name differs from the package name:
```bash
uvx --from httpie http               # Package: httpie, command: http
uvx --from 'mypy[faster-cache]' mypy # With extras
uvx --from 'ruff==0.3.0' ruff check  # Version constraint via --from
uvx --from 'ruff>0.2,<0.3' ruff      # Range constraint
```

### Including additional dependencies (plugins)

```bash
uvx --with mkdocs-material mkdocs serve
uvx -w httpx -w rich my-tool         # Multiple --with (-w shorthand)
uvx --with 'torch>=2.0' my-tool      # Versioned extra dependency
```

### Running from Git

```bash
uvx --from git+https://github.com/httpie/cli httpie
uvx --from git+https://github.com/httpie/cli@master httpie
uvx --from git+https://github.com/httpie/cli@3.2.4 httpie
uvx --from git+https://github.com/httpie/cli@2843b87 httpie
uvx --lfs --from git+https://github.com/repo/lfs-tool tool   # Git LFS
```

## Installing Tools (Persistent)

Installed tools place executables on `PATH` in a persistent environment.

```bash
uv tool install ruff                  # Install latest
uv tool install 'ruff>=0.3,<0.4'      # With version constraint
uv tool install ruff@0.6.0            # Specific version
uv tool install ruff@latest           # Force latest
uv tool install git+https://github.com/astral-sh/ruff  # From Git
```

After installation, the tool is available directly:
```bash
ruff --version
```

### Installing with additional executables

```bash
uv tool install --with-executables-from ansible-core,ansible-lint ansible
```

This installs executables from all three packages into the same environment.

### Upgrading tools

```bash
uv tool upgrade ruff                  # Upgrade within original constraints
uv tool upgrade --all                 # Upgrade all installed tools
uv tool upgrade ruff --upgrade-package click  # Upgrade specific dep
uv tool upgrade ruff --reinstall      # Reinstall all packages
uv tool upgrade ruff --reinstall-package click  # Reinstall specific
```

To change version constraints, reinstall:
```bash
uv tool install 'ruff>=0.4'           # Replaces old constraint
```

### Managing installed tools

```bash
uv tool list                          # List installed tools
uv tool uninstall ruff                # Remove a tool
uv tool dir                           # Show tool directory path
uv tool update-shell                  # Add tool bin dir to PATH in shell config
```

## Tool Version Behavior

- `uvx` uses the latest version on first invocation, then caches it
- Subsequent `uvx` calls use the cached version unless `@latest` is specified
- After `uv tool install`, `uvx <tool>` uses the installed version by default
- `uvx --isolated <tool>` ignores both cache and installed version
- `uvx <tool>@latest` forces latest regardless of installed version

```bash
uv tool install ruff==0.5.0           # Install specific version
uvx ruff --version                    # Shows 0.5.0 (uses installed)
uvx ruff@latest --version             # Shows latest (ignores installed)
uvx --isolated ruff --version         # Shows latest (fresh env, ignores installed)
```

## Python Versions for Tools

```bash
uvx --python 3.10 ruff                # Run with specific Python
uv tool install --python 3.10 ruff    # Install with specific Python
uv tool upgrade --python 3.10 ruff    # Upgrade with specific Python
```

Tool environments ignore `.python-version` files and project `requires-python`. Use `--python` explicitly.

## uvx vs uv run

| Scenario | Command |
|----------|---------|
| Tool isolated from project | `uvx ruff check .` |
| Tool needs project installed (pytest, mypy) | `uv run pytest` |
| One-off dependency with script | `uv run --with rich script.py` |
| Flat-layout project, no install needed | `uvx pytest` works fine |

## Legacy Windows Scripts

Tools support `.ps1`, `.cmd`, and `.bat` scripts:
```powershell
uv tool run --from nuitka==2.6.7 nuitka.cmd --version
uv tool run --from nuitka==2.6.7 nuitka --version    # Auto-finds extension
```
