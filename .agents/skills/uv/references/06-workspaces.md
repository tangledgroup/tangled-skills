# Workspaces

Workspaces group multiple packages into a single managed unit with one shared lockfile. Inspired by Cargo workspaces.

## Setup

Add `[tool.uv.workspace]` to the root `pyproject.toml`:

```toml
[project]
name = "my-workspace"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["bird-feeder", "tqdm>=4,<5"]

[tool.uv.sources]
bird-feeder = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/seeds"]
```

## Layout

```
my-workspace/
├── pyproject.toml          # workspace root (also a member)
├── uv.lock                 # single lockfile for all members
├── src/
│   └── my_workspace/
│       └── main.py
├── packages/
│   ├── bird-feeder/        # workspace member
│   │   ├── pyproject.toml
│   │   └── src/bird_feeder/
│   └── seeds/              # excluded (not a member)
│       └── pyproject.toml
```

## Commands

Workspace commands operate on all members by default:

```bash
uv lock                              # resolve entire workspace
uv sync                              # install all members
uv run                               # runs in workspace root context
uv run --package bird-feeder cmd     # target specific member
uv build --package bird-feeder       # build specific member
```

`uv init` inside an existing project auto-creates a workspace and adds the new member.

## Workspace sources

`workspace = true` in `tool.uv.sources` tells uv to resolve a dependency from within the workspace:

```toml
[tool.uv.sources]
bird-feeder = { workspace = true }   # resolved from workspace member
tqdm = { git = "https://..." }       # applies to ALL members unless overridden
```

Root-level sources propagate to all members. A member can override by defining its own `tool.uv.sources` entry for the same package.

## When to use workspaces

**Good fits:**
- Library + CLI split (test core independently)
- Plugin systems with shared root
- Performance-critical extension modules alongside Python code
- Multiple packages versioned together in one repo

**Not suited for:**
- Members with conflicting `requires-python` (workspace takes intersection)
- Members needing separate virtual environments
- Independent release cycles

For independent packages, use path dependencies instead:

```toml
[tool.uv.sources]
bird-feeder = { path = "packages/bird-feeder" }
```

This gives per-package environments but loses `uv run --package`.

## Key behaviors

- Single `requires-python` across workspace (intersection of all members)
- Inter-member dependencies are always editable
- Single lockfile — all members resolve together
- Root is also a workspace member
- Members can be applications or libraries
