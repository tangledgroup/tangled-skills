# CLI Reference

## Commands

- `ty check` — Check a project for type errors
- `ty server` — Start the language server
- `ty version` — Display ty's version
- `ty explain` — Explain rules and other parts of ty
- `ty generate-shell-completion` — Generate shell completion scripts

## ty check

```bash
ty check [OPTIONS] [PATH]...
```

Check Python files for type errors. Without paths, checks all Python files in the current directory or project root (directory with `pyproject.toml`).

### Options

**Rule severity:**
- `--error <rule>` — Treat rule as error (repeatable, use `all` for all rules)
- `--warn <rule>` — Treat rule as warning (repeatable, use `all` for all rules)
- `--ignore <rule>` — Disable rule (repeatable, use `all` for all rules)

**Environment:**
- `--python`, `--venv <path>` — Path to Python environment or interpreter
- `--python-version`, `--target-version <version>` — Target Python version (3.7–3.15)
- `--python-platform`, `--platform <platform>` — Target platform (`win32`, `darwin`, `linux`, `android`, `ios`, `all`)
- `--extra-search-path <path>` — Additional module resolution path (repeatable)
- `--typeshed`, `--custom-typeshed-dir <path>` — Custom typeshed directory

**File selection:**
- `--exclude <pattern>` — Glob patterns to exclude (gitignore-style, repeatable)
- `--force-exclude` — Enforce exclusions even for explicit paths
- `--respect-ignore-files` — Respect `.gitignore`/`.ignore` (default: on, use `--no-respect-ignore-files` to disable)

**Output:**
- `--output-format <format>` — Output format: `full` (default), `concise`, `gitlab`, `github`, `junit`
- `--color <when>` — Color control: `auto` (default), `always`, `never`
- `--quiet`, `-q` — Quiet output (`-qq` for silent)
- `--verbose`, `-v` — Verbose output (`-vv`, `-vvv` for more)
- `--no-progress` — Hide progress indicators

**Exit behavior:**
- `--exit-zero` — Always exit 0 even with errors
- `--error-on-warning` — Exit 1 on warnings

**Other:**
- `--watch`, `-W` — Watch mode with incremental rechecking
- `--fix` — Apply fixes to resolve errors
- `--add-ignore` — Add `ty: ignore` comments to suppress all diagnostics
- `--config-file <path>` — Path to `ty.toml` config file
- `--config`, `-c <key=value>` — Inline TOML config override
- `--project <dir>` — Run within given project directory

## ty server

```bash
ty server
```

Start the language server for IDE integration. Supports the Language Server Protocol (LSP).

## ty version

```bash
ty version [--output-format text|json]
```

Display version information. Default format is text; use `--output-format json` for machine-readable output.

## ty explain rule

```bash
ty explain rule [RULE]
```

Explain a specific rule or all rules if omitted. Supports `--output-format text|json`.

## ty generate-shell-completion

```bash
ty generate-shell-completion <SHELL>
```

Generate shell completion scripts for the specified shell.
