# Tools

`uvx` is an alias for `uv tool run`. It executes Python CLI tools in ephemeral, isolated environments — no persistent installation needed.

## uvx (ephemeral execution)

```bash
uvx ruff check .                       # resolve, install, run, discard
uvx pycowsay hello                      # one-off invocation
uvx ruff@0.8.0 check                    # exact version
uvx ruff@latest check                   # latest version
uvx --python 3.11 ruff                  # specific Python
```

### Package name differs from command

When the package name and executable differ, use `--from`:

```bash
uvx --from httpie http                 # http command from httpie package
uvx --from 'mypy[reports]==1.13.0' mypy  # version + extras
uvx --from git+https://github.com/httpie/cli httpie  # git source
uvx --lfs --from git+https://... lfs-tool       # Git LFS support
```

### Adding extra dependencies

```bash
uvx --with mkdocs-material mkdocs      # include plugin
uvx --with black --with isort mypy     # multiple extras
```

## Persistent tool installation

For frequently used tools, install persistently (executables added to PATH):

```bash
uv tool install ruff                   # install + add to PATH
uv tool install 'httpie>=3.2'          # with version constraint
uv tool install --python 3.11 ruff     # specific Python
uv tool install mkdocs --with mkdocs-material  # with extras
```

Installed tools are isolated from projects and scripts — importing their modules in regular Python won't work by design.

### Managing installed tools

```bash
uv tool list                           # show installed tools
uv tool upgrade ruff                   # upgrade one tool
uv tool upgrade --all                  # upgrade all tools
uv tool uninstall ruff                 # remove
uv tool update-shell                   # add tool bin dir to PATH (if missing)
```

## uvx vs uv run

| Aspect | `uvx` | `uv run` |
|---|---|---|
| Environment | Isolated, ephemeral | Project environment |
| Project access | None | Full (project is installed) |
| Use case | One-off CLI tools | Scripts + project tools |
| Example | `uvx ruff check .` | `uv run pytest` |

Use `uv run` when the tool needs your project's code or dependencies (e.g., `pytest`, `mypy`, `ruff` checking project files). Use `uvx` for standalone tools that operate independently.

## Windows legacy scripts

On Windows, `uvx` auto-discovers `.ps1`, `.cmd`, and `.bat` scripts:

```bash
uvx --from nuitka==2.6.7 nuitka --version
```

No need to specify the extension — uv checks in order: `.ps1`, `.cmd`, `.bat`.
