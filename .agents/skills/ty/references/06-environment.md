# Environment Variables

## ty-defined variables

### `TY_CONFIG_FILE`

Path to a `ty.toml` configuration file. Equivalent to `--config-file`. When set, automatic config discovery is skipped.

### `TY_LOG`

Log level filter for verbose output. Uses `tracing_subscriber` crate syntax:

```bash
TY_LOG=ty=debug ty check    # Equivalent to -vv
TY_LOG=trace ty check       # All trace-level logging
```

### `TY_LOG_PROFILE`

Set to `"1"` or `"true"` to enable flamegraph profiling. Creates a `tracing.folded` file for performance analysis.

### `TY_MAX_PARALLELISM`

Upper limit on parallel tasks (e.g., files checked in parallel). Not the same as thread count — ty may spawn additional threads for file watching or UI.

### `TY_OUTPUT_FORMAT`

Default output format for diagnostics. Same values as `--output-format`: `full`, `concise`, `github`, `gitlab`, `junit`.

## Externally-defined variables

### `VIRTUAL_ENV`

Primary method for detecting an activated virtual environment. Preferred over `CONDA_PREFIX` when both are set.

### `CONDA_PREFIX` / `CONDA_DEFAULT_ENV` / `_CONDA_ROOT`

Conda environment detection. `CONDA_PREFIX` provides the path; `CONDA_DEFAULT_ENV` gives the name.

### `PYTHONPATH`

Additional directories added to ty's module search paths. Colon-separated on Unix, semicolon-separated on Windows (same format as shell PATH).

### `RAYON_NUM_THREADS`

Upper limit on parallel threads. Standard Rayon variable; equivalent to `TY_MAX_PARALLELISM`.

### `XDG_CONFIG_HOME`

Path to user-level configuration directory on Unix. User config is read from `$XDG_CONFIG_HOME/ty/ty.toml` (or `~/.config/ty/ty.toml` if unset).
