# pip Interface

`uv pip` provides a drop-in replacement for `pip`, `pip-tools`, and `virtualenv`. It operates directly on virtual environments without managing lockfiles or project state.

## Environment creation

```bash
uv venv                          # create .venv
uv venv my-env                   # custom name
uv venv --python 3.11            # specific Python
```

Activate as usual:

```bash
source .venv/bin/activate        # bash/zsh
.venv\Scripts\activate           # PowerShell
```

## Installing packages

```bash
uv pip install flask              # single package
uv pip install flask ruff         # multiple
uv pip install 'ruff>=0.2'       # with constraint
uv pip install 'flask[dotenv]'   # with extras
uv pip install -e .              # editable install
uv pip install -r reqs.txt       # from file
uv pip install -r pyproject.toml --extra dev  # from pyproject.toml
```

### Git sources

```bash
uv pip install git+https://github.com/psf/requests
uv pip install git+https://github.com/psf/requests@v2.31.0
uv pip install git+https://github.com/psf/requests@main
```

## Compiling (pip-compile replacement)

Lock dependencies to exact versions:

```bash
uv pip compile requirements.in -o requirements.txt
uv pip compile pyproject.toml -o requirements.txt
uv pip compile setup.py -o requirements.txt          # legacy
uv pip compile - -o requirements.txt                  # from stdin
uv pip compile reqs.in -o reqs.txt --upgrade         # upgrade all
uv pip compile reqs.in -o reqs.txt --upgrade-package ruff  # upgrade one
```

## Syncing

`uv pip sync` makes the environment match the file exactly (removes extraneous packages):

```bash
uv pip sync requirements.txt
uv pip sync pylock.toml                 # PEP 751 format
```

Unlike `uv pip install`, `sync` removes packages not in the file.

## Constraints and overrides

**Constraints** — additive version bounds (don't trigger installation):

```bash
# constraints.txt
pydantic<2.0

uv pip compile reqs.in --constraint constraints.txt
uv pip install -r reqs.txt -c constraints.txt
```

**Overrides** — absolute version replacement (ignores package requirements):

```bash
# overrides.txt
requests>=2.31.0

uv pip compile reqs.in --override overrides.txt
```

Use overrides to remove upper bounds from transitive dependencies that conflict.

## Build constraints

Control build-time dependency versions:

```bash
# build-constraints.txt
setuptools==75.0.0

uv pip compile reqs.in --build-constraint build-constraints.txt
```

## Inspecting environments

```bash
uv pip freeze                       # list installed packages
uv pip list                         # formatted list
uv pip show requests                # package details
```

## System installs

For CI/containers where virtualenvs aren't needed:

```bash
uv pip install --system flask       # install into system Python
```

Requires explicit `--system` flag — uv refuses to modify system Python by default.

## Key differences from pip

- uv requires a virtual environment by default (no bare `pip install`)
- `uv pip compile` replaces `pip-tools`
- 10–100× faster resolution and installation
- Supports features pip lacks: universal resolutions, overrides, build constraints
- Not exact behavioral clone — edge cases may differ; see [compatibility docs](https://docs.astral.sh/uv/pip/compatibility/)
