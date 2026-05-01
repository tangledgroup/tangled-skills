# Running Commands

## Basic Usage

When working on a project, it is installed into `.venv`. Use `uv run` to execute commands in the project environment:

```bash
uv run python -c "import example"
uv run example-cli foo
uv run bash scripts/foo.sh
```

uv ensures the environment is up-to-date before running.

## Requesting Additional Dependencies

Add dependencies per-invocation with `--with`:

```bash
# Run with a specific version
uv run --with httpx==0.26.0 python -c "import httpx; print(httpx.__version__)"

# Run with multiple extra deps
uv run --with ruff --with mypy python -c "import ruff, mypy"
```

The requested version is respected regardless of project requirements.

## Running Scripts

Scripts with inline metadata (PEP 723) are automatically executed in isolated environments:

```python
# /// script
# dependencies = [
#   "httpx",
# ]
# ///

import httpx
resp = httpx.get("https://peps.python.org/api/peps.json")
print(resp.json())
```

Run with `uv run example.py` — it runs isolated from the project with only the declared dependencies.

## Legacy Scripts on Windows

Support for legacy setuptools scripts (`.ps1`, `.cmd`, `.bat`):

```bash
uv run --with nuitka==2.6.7 -- nuitka.cmd --version
# Extension auto-detected:
uv run --with nuitka==2.6.7 -- nuitka --version
```

## Signal Handling

On Unix, uv forwards most signals to the child process (except SIGKILL, SIGCHLD, SIGIO, SIGPOLL). SIGINT is forwarded only if sent more than once or the child process group differs.

On Windows, Ctrl-C events are deferred to the child process.

## Environment Variables

uv run loads `.env` files automatically:

```bash
# Auto-discover .env, .env.local, .env.development
uv run python app.py

# Specify env file
uv run --env-file .env.staging python app.py

# Disable dotenv loading
uv run --no-env-file python app.py
# Or: UV_NO_ENV_FILE=1 uv run python app.py
```

Multiple `--env-file` flags are supported, with later files overriding earlier ones. Environment variables take precedence over `.env` file values.
