# Build and Publish

## Building Distributions

Build Python packages into source distributions (sdist) and wheels:

```bash
# Build in current directory
uv build

# Build specific project
uv build --package my-package

# Output to specific directory
uv build --out-dir dist/

# Build only wheel
uv build --wheel

# Build only source distribution
uv build --sdist
```

Builds use the project's declared build system (e.g., `uv_build`, `hatchling`, `setuptools`).

## Publishing to PyPI

Upload distributions to a package index:

```bash
# Publish built distributions
uv publish dist/*

# Publish to test PyPI
uv publish --index-url https://test.pypi.org/legacy/ dist/*

# Dry run (check without uploading)
uv publish --dry-run dist/*

# Skip existing files
uv publish --skip-existing dist/*
```

### Authentication

Publishing requires authentication. Use environment variables or the `uv auth` CLI:

```bash
# Via environment variable
UV_PUBLISH_TOKEN=pypi-xxx uv publish dist/*

# Via uv auth
uv auth login pypi.org
uv publish dist/*
```

For TestPyPI, use `--index-url`:

```bash
UV_PUBLISH_TOKEN=pypi-xxx uv publish --index-url https://test.pypi.org/legacy/ dist/*
```

## Build Systems

Common build backends:

- **uv_build** — uv's own build backend (default for `uv init --package`)
- **hatchling** — Hatch's build system
- **setuptools** — Traditional Python build system
- **flit_core** — Flit's build backend
- **maturin** — For Rust extensions

Configure in `pyproject.toml`:

```toml
[build-system]
requires = ["uv_build>=0.11.7,<0.12"]
build-backend = "uv_build"
```

Choose build backend during project creation:

```bash
uv init --package --build-backend hatchling my-project
```
