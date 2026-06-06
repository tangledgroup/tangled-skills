# CLI Reference

## Command Summary

### Project Commands

- `uv init` — Create a new project
- `uv add` — Add dependencies to the project
- `uv remove` — Remove dependencies from the project
- `uv version` — Read or update the project's version
- `uv sync` — Update the project's environment
- `uv lock` — Update the project's lockfile
- `uv export` — Export the lockfile to an alternate format
- `uv tree` — Display the dependency tree
- `uv audit` — Audit dependencies for security vulnerabilities
- `uv format` — Format Python code in the project

### Execution Commands

- `uv run` — Run a command or script in the project environment

### Tool Commands

- `uv tool install` — Install a Python CLI tool
- `uv tool run` / `uvx` — Run a Python CLI tool (without persistent install)
- `uv tool upgrade` — Upgrade an installed tool
- `uv tool list` — List installed tools
- `uv tool uninstall` — Uninstall a tool
- `uv tool dir` — Show the tools directory

### Python Version Commands

- `uv python install` — Install a Python version
- `uv python list` — List installed Python versions
- `uv python uninstall` — Uninstall a managed Python
- `uv python pin` — Pin a Python version (creates `.python-version`)
- `uv python upgrade` — Upgrade to latest patch release

### pip Interface Commands

- `uv pip install` — Install packages
- `uv pip uninstall` — Uninstall packages
- `uv pip freeze` — Freeze installed packages
- `uv pip list` — List installed packages
- `uv pip show` — Show package details
- `uv pip check` — Check for broken packages
- `uv pip compile` — Compile requirements (pip-compile equivalent)
- `uv pip sync` — Sync environment from requirements file

### Other Commands

- `uv venv` — Create a virtual environment
- `uv build` — Build Python packages into distributions
- `uv publish` — Upload distributions to an index
- `uv cache clean` — Clear the cache
- `uv cache prune` — Remove unused cache entries
- `uv cache dir` — Show the cache directory
- `uv self update` — Update uv itself
- `uv auth login` — Login to a service
- `uv auth logout` — Logout from a service
- `uv auth token` — Show authentication token
- `uv help` — Display documentation

## Common Global Options

- `--directory <dir>` / `-C` — Change working directory before running
- `--project <dir>` — Discover project in given directory
- `--no-cache` / `-n` — Disable cache (use temp directory)
- `--no-config` — Disable configuration file discovery
- `--offline` — Disable network access
- `--verbose` / `-v` — Verbose output (repeat for more)
- `--quiet` / `-q` — Quiet output
- `--color <choice>` — Control color output (`auto`, `always`, `never`)
- `--no-progress` — Hide progress bars
- `--python <version>` — Request specific Python version
- `--python-preference` — Prefer managed or system Python
- `--managed-python` — Require uv-managed Python
- `--no-managed-python` — Disable uv-managed Python
- `--no-python-downloads` — Disable automatic Python downloads
- `--config-file <path>` — Use specific config file

## Key Environment Variables

- `UV_CACHE_DIR` — Override cache directory
- `UV_NO_CACHE` — Disable cache
- `UV_CONFIG_FILE` — Specific config file path
- `UV_NO_CONFIG` — Disable config discovery
- `UV_OFFLINE` — Disable network access
- `UV_PYTHON_DOWNLOADS` — Control automatic Python downloads (`automatic`, `never`)
- `UV_MANAGED_PYTHON` — Require managed Python
- `UV_NO_MANAGED_PYTHON` — Disable managed Python
- `UV_PROJECT_ENVIRONMENT` — Override project venv path
- `UV_INDEX` / `UV_DEFAULT_INDEX` — Command-line index URLs
- `UV_INDEX_STRATEGY` — Index resolution strategy
- `UV_ENV_FILE` — Default dotenv file path
- `UV_NO_ENV_FILE` — Disable dotenv loading
- `UV_LOCK_TIMEOUT` — Cache lock timeout (default: 5 min)
- `UV_SYSTEM_CERTS` — Use platform certificate store
- `UV_KEYRING_PROVIDER` — Keyring provider (`disabled`, `native`, `subprocess`)
