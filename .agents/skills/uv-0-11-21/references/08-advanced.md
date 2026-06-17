# Advanced Reference

## Caching

### Cache behavior by dependency type
- **Registry deps** — HTTP caching headers respected
- **Direct URL deps** — Cached by URL
- **Git deps** — Cached by resolved commit hash
- **Local deps** — Cached by last-modified time of `pyproject.toml`/`setup.py`/`setup.cfg`
- **Flat indexes** — Assumed immutable; cached by filename

### Cache management
```bash
uv cache clean                     # Clear all cache
uv cache clean ruff                # Clear specific package
uv cache prune                     # Remove unused entries
uv cache prune --ci                # CI: keep source-built wheels, remove pre-built
uv cache dir                       # Show cache directory
```

### Refresh and reinstall flags
```bash
uv sync --refresh                  # Revalidate all cached data
uv sync --refresh-package ruff     # Revalidate specific package
uv sync --reinstall                # Ignore installed versions
uv pip install --reinstall .       # Force rebuild of local project
```

### Cache directory
Determined by: `--no-cache` (temp dir) → `UV_CACHE_DIR` / `--cache-dir` → system default (`$XDG_CACHE_HOME/uv`, `%LOCALAPPDATA%\uv\cache`)

Keep the cache on the same filesystem as the target environment for hard-linking performance.

### Cache keys for dynamic metadata
```toml
[tool.uv]
cache-keys = [
  { file = "pyproject.toml" },
  { git = { commit = true, tags = true } },
  { env = "MY_ENV_VAR" },
  { dir = "src" },
]
```

Globs supported: `{ file = "**/*.toml" }` (expensive — walks filesystem).

### Force always-rebuild
```toml
[tool.uv]
reinstall-package = ["my-package"]
```

## Configuration Files

### Hierarchy (highest to lowest precedence)
1. Command-line flags
2. Environment variables
3. Project-level (`pyproject.toml` → `[tool.uv]` or `uv.toml`)
4. User-level (`~/.config/uv/uv.toml`)
5. System-level (`/etc/uv/uv.toml`)

### File formats
```toml
# pyproject.toml
[tool.uv]
index-url = "https://test.pypi.org/simple"

# uv.toml (same directory, takes precedence over pyproject.toml)
[index]
url = "https://test.pypi.org/simple"
```

`uv.toml` omits the `[tool.uv]` prefix. User/system config must use `uv.toml` format.

### Disabling configuration
```bash
uv <command> --no-config              # Disable all persistent config
uv <command> --config-file path/to/uv.toml  # Use specific file only
```

### Merging behavior
- Scalars: higher precedence wins
- Arrays: concatenated (higher precedence first)

## Building Packages

### Basic build
```bash
uv build                             # sdist + wheel from sdist
uv build --wheel                     # Wheel only
uv build --sdist                     # Sdist only
uv build path/to/project             # Build different directory
uv build --package my-member         # Build workspace member
```

Artifacts go to `dist/`.

### Build with constraints
```bash
uv build --build-constraint constraints.txt --require-hashes
```

### uv_build backend
```toml
[build-system]
requires = ["uv_build>=0.11.21,<0.12"]
build-backend = "uv_build"
```

The uv build backend supports pure Python only. For extension modules, use `maturin` (Rust) or `scikit-build-core` (C/C++).

### Module configuration
```toml
[tool.uv.build-backend]
module-name = "FOO"          # Override normalized name
module-root = ""              # Root directory instead of src/
namespace = true              # Auto-discover namespace packages
data = ["data", "assets"]    # Extra data directories
source-include = ["**/*.json"]
source-exclude = ["**/__pycache__"]
wheel-exclude = ["tests/**"]
```

### Stub packages
Package name ending in `-stubs` (e.g., `foo-stubs`). uv looks for `__init__.pyi` instead of `__init__.py`.

### Preventing accidental PyPI upload
```toml
[project]
classifiers = ["Private :: Do Not Upload"]
```

## Publishing Packages

### Basic publish
```bash
uv publish                                    # To PyPI (default)
uv publish --token $PYPI_TOKEN               # With token
uv publish --index testpypi                   # Custom index
UV_PUBLISH_TOKEN=... uv publish               # Via env var
```

### Publishing to custom indexes
```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

```bash
uv publish --index testpypi
```

### Attestations
uv auto-discovers `.publish.attestation` files in `dist/`:
```
dist/
├── package-1.0.0-py3-none-any.whl
├── package-1.0.0-py3-none-any.whl.publish.attestation
└── package-1.0.0.tar.gz
```

Disable with `--no-attestations` or `UV_PUBLISH_NO_ATTESTATIONS`.

### Retry behavior
uv retries failed uploads. For PyPI, identical files are ignored on retry. For other registries:
```bash
uv publish --check-url https://my-index.com/simple/
```

## Export Formats

### requirements.txt
```bash
uv export --format requirements.txt
uv export --format requirements.txt --output-file requirements.txt
```

### pylock.toml (PEP 751)
```bash
uv export --format pylock.toml
uv export --format pylock.toml --output-file pylock.toml
```

Install from pylock.toml:
```bash
uv pip sync pylock.toml
uv pip install -r pylock.toml
```

### CycloneDX SBOM (preview)
```bash
uv export --format cyclonedx1.5
uv export --format cyclonedx1.5 --output-file sbom.json
```

## Environment Variables

Key environment variables:
| Variable | Purpose |
|----------|---------|
| `UV_CACHE_DIR` | Override cache directory |
| `UV_NO_CACHE` | Disable cache (use temp dir) |
| `UV_PYTHON_INSTALL_DIR` | Override managed Python install dir |
| `UV_PROJECT_ENVIRONMENT` | Override project venv path |
| `UV_INDEX_<NAME>_USERNAME` | Index credentials |
| `UV_INDEX_<NAME>_PASSWORD` | Index credentials |
| `UV_PUBLISH_TOKEN` | Publish token |
| `UV_NO_MODIFY_PATH` | Don't modify shell profiles on self-update |
| `UV_ENV_FILE` | Default .env file for `uv run` |
| `UV_NO_ENV_FILE` | Disable dotenv loading |
| `UV_GIT_LFS` | Default Git LFS behavior for all sources |
| `UV_LOCK_TIMEOUT` | Cache lock timeout (default: 5 min) |
| `UV_NO_INSTALL_PROJECT` | Skip installing the project itself |
| `UV_NO_INSTALL_WORKSPACE` | Skip installing workspace members |
| `UV_NO_INSTALL_LOCAL` | Skip installing local path dependencies |
| `UV_NO_SYSTEM_CONFIG` | Disable reading system config file |

## Partial Installations

For Docker layer caching:
```bash
uv sync --no-install-project              # Skip project, install deps only
uv sync --no-install-workspace            # Skip all workspace members
uv sync --no-install-package <name>       # Skip specific package
```

Dependencies of skipped packages are still installed. Use carefully to avoid broken environments.

## Malware Checks (Preview)

```bash
UV_MALWARE_CHECK=1 uv sync
```

Scans lockfile against OSV/OpenSSF malicious packages database. Terminates sync on match.

## Running Type Checks (Preview)

`uv check` runs the `ty` type checker from within uv:
```bash
uv check                              # Run ty on current project
uv check --isolated                   # Ignore project config
```
This integrates Astral's `ty` type checker with uv's workspace and environment management.

## Lockfile Versioning

`uv.lock` uses a versioned schema. Schema changes only in minor releases. All patch versions within a minor release share lockfile compatibility. The `revision` field tracks backwards-compatible changes.
