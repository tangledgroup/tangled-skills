# Workspaces

## Overview

Inspired by Cargo, a workspace is "a collection of one or more packages, called workspace members, that are managed together."

Workspaces organize large codebases into multiple packages with common dependencies. Each package defines its own `pyproject.toml`, but the workspace shares a single lockfile for consistent dependency resolution.

`uv lock` operates on the entire workspace at once. `uv run` and `uv sync` operate on the workspace root by default, though both accept `--package` to target specific members.

## Creating a Workspace

Add a `tool.uv.workspace` table to a `pyproject.toml`:

```toml
[project]
name = "albatross"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["bird-feeder", "tqdm>=4,<5"]

[tool.uv.sources]
bird-feeder = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/seeds"]
```

Running `uv init` inside an existing package automatically adds the new member to the workspace.

Every directory matched by `members` globs must contain a `pyproject.toml`. Members can be either applications or libraries.

## Workspace Sources

Dependencies on workspace members use `workspace = true`:

```toml
[tool.uv.sources]
bird-feeder = { workspace = true }
```

Dependencies between workspace members are editable.

Root-level `tool.uv.sources` apply to all members unless overridden in a specific member's `tool.uv.sources`:

```toml
[tool.uv.sources]
bird-feeder = { workspace = true }
tqdm = { git = "https://github.com/tqdm/tqdm" }
```

Every member installs `tqdm` from GitHub unless it overrides the source in its own `pyproject.toml`.

## Workspace Layouts

Common layout — root project with accompanying libraries:

```
albatross/
├── packages/
│   ├── bird-feeder/
│   │   ├── pyproject.toml
│   │   └── src/bird_feeder/
│   └── seeds/
│       ├── pyproject.toml
│       └── src/seeds/
├── pyproject.toml
├── uv.lock
└── src/albatross/
```

## Running in Workspaces

```bash
# Run in workspace root (default)
uv run

# Run in specific member from any workspace directory
uv run --package bird-feeder python -c "import bird_feeder"

# Sync specific member
uv sync --package bird-feeder
```

## When (Not) to Use Workspaces

**Use workspaces when:**
- Developing multiple interconnected packages in a single repository
- A library has a performance-critical subroutine in an extension module
- A library has a plugin system with each plugin as a separate package
- You want to test core library independently of CLI

**Do not use workspaces when:**
- Members have conflicting requirements
- Each member needs a separate virtual environment
- Members need different Python versions

In these cases, use path dependencies instead:

```toml
[tool.uv.sources]
bird-feeder = { path = "packages/bird-feeder" }
```

## Limitations

- uv enforces a single `requires-python` for the entire workspace (intersection of all members)
- uv cannot ensure packages don't import dependencies declared by another workspace member
- For testing on unsupported Python versions, use `uv pip` in a separate environment
