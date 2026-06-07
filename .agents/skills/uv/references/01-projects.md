# Projects

## Project structure

`uv init` creates:

```
my-project/
├── .git/
├── .gitignore
├── .python-version       # default Python version
├── README.md
├── main.py               # simple entry point
├── pyproject.toml        # project metadata + dependencies
├── .venv/                # auto-created on first uv run/add/sync
└── uv.lock               # resolved dependency lockfile
```

## pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["requests>=2.28"]

[dependency-groups]
dev = ["pytest", "ruff"]

[tool.uv]
cache-keys = [{ file = "pyproject.toml" }]
```

## Dependency sources

Dependencies can come from multiple sources:

```bash
uv add requests                        # PyPI (default)
uv add 'requests==2.31.0'             # exact version
uv add git+https://github.com/psf/requests  # git URL
uv add git+https://github.com/psf/requests@main  # specific branch
uv add --editable ./libs/mypackage     # local editable
```

In `pyproject.toml`, `tool.uv.sources` controls non-registry sources:

```toml
[tool.uv.sources]
mypackage = { path = "./libs/mypackage", editable = true }
requests = { git = "https://github.com/psf/requests", tag = "v2.31.0" }
```

## Lockfile (uv.lock)

- Cross-platform TOML lockfile with exact resolved versions
- Checked into version control for reproducibility
- Managed by uv — do not edit manually

```bash
uv lock                              # create/update lockfile
uv lock --upgrade                    # upgrade all dependencies
uv lock --upgrade-package requests   # upgrade specific package
uv sync                              # install from lockfile
uv sync --frozen                     # error if lockfile is out of date
```

## Running commands

`uv run` verifies the lockfile and environment before executing:

```bash
uv run python main.py                # run script
uv run flask run -p 3000             # run CLI tool
uv run --with black -- black check . # include one-off dependency
uv run --package lib-name cmd        # in workspace: target specific member
```

## Exporting lockfiles

Export `uv.lock` to other formats for compatibility:

```bash
uv export                            # requirements.txt format
uv export --format requirements-txt -o reqs.txt
uv export --no-hashes                # omit hash pins
```

## Building distributions

```bash
uv build                    # builds wheel + sdist into dist/
uv build --package lib-name # build specific workspace member
uv build --no-sources       # ignore tool.uv.sources (for publishing)
```
