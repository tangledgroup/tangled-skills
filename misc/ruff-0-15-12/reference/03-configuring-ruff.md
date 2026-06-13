# Configuring Ruff

## Configuration Files

Ruff can be configured through three file types:

- `pyproject.toml` — Settings under `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]`.
- `ruff.toml` — Settings at top level, `[lint]`, `[format]` (no `tool.ruff` prefix).
- `.ruff.toml` — Same schema as `ruff.toml`, but takes precedence over it.

If multiple config files exist in the same directory: `.ruff.toml` > `ruff.toml` > `pyproject.toml`.

## Default Configuration

If no config file is found, Ruff uses these defaults (equivalent to this `ruff.toml`):

```toml
exclude = [
    ".bzr", ".direnv", ".eggs", ".git", ".git-rewrite", ".hg",
    ".ipynb_checkpoints", ".mypy_cache", ".nox", ".pants.d", ".pyenv",
    ".pytest_cache", ".pytype", ".ruff_cache", ".svn", ".tox", ".venv",
    ".vscode", "__pypackages__", "_build", "buck-out", "build", "dist",
    "node_modules", "site-packages", "venv",
]

line-length = 88
indent-width = 4
target-version = "py310"

[lint]
select = ["E4", "E7", "E9", "F"]
ignore = []
fixable = ["ALL"]
unfixable = []
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = false
docstring-code-line-length = "dynamic"
```

## Config File Discovery

Ruff supports hierarchical configuration: the closest config file in the directory hierarchy is used for each individual file, with paths resolved relative to that config file's directory.

Key rules:

1. Ruff ignores `pyproject.toml` files that lack a `[tool.ruff]` section.
2. If `--config path/to/ruff.toml` is passed directly, those settings apply to all analyzed files, with relative paths resolved from the current working directory.
3. If no config file is found, Ruff falls back to default configuration (or user-level config at `${config_dir}/ruff/pyproject.toml`).
4. CLI options override every resolved configuration file.

Unlike ESLint, Ruff does **not** merge settings across config files — the closest one wins. Use `extend` to inherit from another config:

```toml
# Extend parent config but override line length.
extend = "../ruff.toml"
line-length = 100
```

## Python Version Inference

When no config specifies `target-version`, Ruff attempts to infer it from the `requires-python` field in a nearby `pyproject.toml`. The inference rules depend on how configuration was discovered (direct path, filesystem hierarchy, user-level, or no config).

## Python File Discovery

When passed a path, Ruff automatically discovers all Python files, respecting `exclude` and `extend-exclude` settings. By default, it also skips files omitted via `.gitignore`, `.ignore`, and `.git/info/exclude`.

### Default Inclusions

Ruff discovers files matching: `*.py`, `*.pyi`, `*.ipynb`, or `pyproject.toml`.

To add custom extensions:

```toml
extend-include = ["*.myext"]
```

Or override defaults entirely:

```toml
include = ["pyproject.toml", "src/**/*.py", "scripts/**/*.py"]
```

### Extension Mapping (0.15.2+)

Map custom file extensions to language types:

```toml
# ruff.toml
extension = { qmd = "markdown" }

# pyproject.toml
[tool.ruff]
extension = { qmd = "markdown" }
```

Configured extensions are included in file discovery (0.15.3+).

### Tool-Specific Exclusion

Scope `exclude` to specific tools:

```toml
[format]
exclude = ["*.pyi"]   # Don't format stub files, but still lint them.
```

## Jupyter Notebook Support

Ruff has built-in support for linting and formatting Jupyter Notebooks (`.ipynb`). To control notebook handling:

```toml
# Only lint notebooks, don't format them.
[format]
exclude = ["*.ipynb"]

# Only format notebooks, don't lint them.
[lint]
exclude = ["*.ipynb"]

# Disable notebook support entirely.
extend-exclude = ["*.ipynb"]

# Ignore specific rules for notebooks.
[lint.per-file-ignores]
"*.ipynb" = ["T20"]
```

Some rules behave differently for notebooks — e.g., `E402` detects imports at the top of a **cell** rather than the top of a file.

## Command-Line Interface

### Top-Level Commands

```
ruff check    # Run the linter.
ruff format   # Run the formatter.
ruff rule     # Explain a rule (or all rules).
ruff config   # List available configuration options.
ruff linter   # List all supported upstream linters.
ruff clean    # Clear cache.
ruff server   # Run the language server.
ruff version  # Display version.
```

### The `--config` Flag

Two uses:

1. Point to a configuration file:
   ```bash
   ruff check path/to/directory --config path/to/ruff.toml
   ```

2. Override specific settings inline:
   ```bash
   ruff check --config "lint.dummy-variable-rgx = '__.*'"
   ruff check --config "lint.per-file-ignores = {'some_file.py' = ['F841']}"
   ```

Linter-specific options need `lint.` prefix, formatter-specific need `format.` prefix.

### Key CLI Flags for `ruff check`

- `--select RULE_CODE` — Enable specific rules.
- `--ignore RULE_CODE` — Disable specific rules.
- `--extend-select RULE_CODE` — Add rules on top of existing selection.
- `--fix` — Apply fixes.
- `--unsafe-fixes` — Include unsafe fixes.
- `--diff` — Show diff instead of writing files.
- `--watch` — Re-run on file changes.
- `--add-noqa` — Auto-add noqa directives to violating lines.
- `--output-format FORMAT` — Output format: `concise`, `full`, `json`, `json-lines`, `junit`, `grouped`, `github`, `gitlab`, `pylint`, `rdjson`, `azure`, `sarif`.
- `--statistics` — Show counts per rule.
- `--no-cache` — Disable cache reads.
- `--isolated` — Ignore all configuration files.
- `-n, --no-cache` — Same as `--no-cache`.

### Key CLI Flags for `ruff format`

- `--check` — Check without writing (CI-friendly).
- `--diff` — Show diff of changes.
- `--line-length N` — Override line length.
- `--exit-non-zero-on-format` — Exit non-zero if files were formatted.

### Global Options

- `--config CONFIG_OPTION` — Config file path or TOML key-value pair.
- `--isolated` — Ignore all configuration files.
- `--color WHEN` — Control colored output: `auto`, `always`, `never` (0.15.0+).
- `-v, --verbose` / `-q, --quiet` / `-s, --silent` — Log levels.

## Shell Autocompletion

```bash
# Bash
echo 'eval "$(ruff generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(ruff generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
echo 'ruff generate-shell-completion fish | source' > ~/.config/fish/completions/ruff.fish
```

Supported shells: `bash`, `zsh`, `fish`, `elvish`, `powershell`, `fig`.
