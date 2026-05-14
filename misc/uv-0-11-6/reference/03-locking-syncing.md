# Locking and Syncing

## Automatic Lock and Sync

Locking resolves dependencies into a lockfile. Syncing installs packages from the lockfile into the project environment. Both are automatic in uv — `uv run` locks and syncs before executing.

Disable automatic locking:

```bash
uv run --locked ...   # Error if lockfile is outdated
uv run --frozen ...   # Use lockfile without checking
uv run --no-sync ...  # Skip environment sync check
```

## Lockfile Status

The lockfile is considered outdated when:
- A dependency is added to `pyproject.toml`
- Version constraints change such that the locked version is excluded
- The lockfile format changes

The lockfile is **not** considered outdated when new package versions are released — explicit update is needed.

Check lockfile status:

```bash
uv lock --check
```

## Creating and Updating the Lockfile

```bash
# Create or update
uv lock
```

## Syncing the Environment

```bash
# Sync environment from lockfile
uv sync
```

### Editable Installation

By default, workspace members are installed as editable packages. Opt-out with `--no-editable`.

If no build system is defined, the project itself is not installed (only its dependencies).

### Exact vs Inexact Syncing

`uv sync` performs exact syncing by default — removing extraneous packages:

```bash
uv sync               # Exact (default)
uv sync --inexact     # Retain extraneous packages
```

`uv run` uses inexact syncing by default:

```bash
uv run ...            # Inexact (default for run)
uv run --exact ...    # Exact syncing
```

### Syncing Optional Dependencies

```bash
uv sync --extra foo        # Include specific extra
uv sync --all-extras       # Include all extras
```

### Syncing Development Dependencies

```bash
uv sync                     # Includes dev group by default
uv sync --no-dev            # Exclude dev group
uv sync --only-dev          # Only dev deps (not project)
uv sync --all-groups        # All dependency groups
uv sync --group lint        # Specific group
uv sync --no-group docs     # Exclude specific group
```

Group exclusions take precedence over inclusions.

## Upgrading Locked Package Versions

With an existing `uv.lock`, uv prefers previously locked versions. Upgrade explicitly:

```bash
# Upgrade all packages
uv lock --upgrade

# Upgrade a single package
uv lock --upgrade-package httpx

# Upgrade to specific version
uv lock --upgrade-package httpx==0.27.0
```

Upgrades are limited to project dependency constraints (upper bounds apply). These flags can also be provided to `uv sync` or `uv run`.

## Exporting the Lockfile

Export `uv.lock` to different formats:

```bash
uv export --format requirements.txt
uv export --format pylock.toml
uv export --format cyclonedx1.5
```

## Partial Installations

For Docker layer caching and multi-step installations:

```bash
uv sync --no-install-project          # Skip current project
uv sync --no-install-workspace        # Skip all workspace members
uv sync --no-install-package pkg-name # Skip specific package
```

Dependencies of skipped packages are still installed. Misuse can result in broken environments.
