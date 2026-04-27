# Worktree Isolation

## Three Isolation Modes

autoloop isolates concurrent runs so they do not clobber each other's files:

- **shared** — project root as working directory, `.autoloop/` as state. For single runs and read-only tasks
- **run-scoped** — project root as working directory, `.autoloop/runs/<runId>/` as state. For concurrent planning runs that don't modify code
- **worktree** — `.autoloop/worktrees/<runId>/tree/` as working directory, `<worktree>/.autoloop/` as state, on a new git branch `autoloop/<runId>`. For concurrent code-modifying runs

### Resolution Order

1. `--worktree` flag → worktree
2. `--no-worktree` flag → shared
3. Config `worktree.enabled = true` → worktree
4. No other active runs → run-scoped
5. Current preset is planning category → run-scoped (no warning)
6. Other code-modifying runs active → run-scoped + warning
7. Otherwise → run-scoped

### Preset Categories

- **Code** presets (modify source): autocode, autofix, autotest, autosimplify, autoperf, autosec
- **Planning** presets (read-only): automerge, autoideas, autoresearch, autodoc, autoreview, autoqa, autospec

Detected from `<!-- category: code|planning|unknown -->` in the preset's `harness.md`, falling back to name-based heuristics.

## Worktree Lifecycle

### 1. Creation

```bash
autoloop run autocode --worktree "implement feature X"
```

Creates a git worktree at `.autoloop/worktrees/<runId>/tree/` on branch `autoloop/<runId>`. The run executes entirely inside the worktree directory.

### 2. Execution

Status in worktree metadata is `running`. All state files (journal, tasks, memory) are written inside the worktree's own `.autoloop/` directory.

### 3. Completion

Metadata status updated to `completed` (success) or `failed`.

### 4. Merge

```bash
# Manual merge
autoloop worktree merge <run-id>
autoloop worktree merge <run-id> --strategy rebase

# Auto-merge on completion
autoloop run autocode --worktree --automerge "fix the bug"
```

The merge checks out the base branch, applies changes using the configured strategy, and updates metadata to `merged`. On conflict, the merge aborts cleanly with a list of conflicting files.

### 5. Cleanup

```bash
autoloop worktree clean              # terminal (merged/failed/removed) worktrees
autoloop worktree clean <run-id>     # specific run
autoloop worktree clean --all        # include non-terminal
autoloop worktree clean --force      # force-remove with -D
```

## Merge Strategies

- **squash** (default) — `git merge --squash`: all worktree commits collapsed into one
- **merge** — `git merge --no-ff`: standard merge commit preserving full history
- **rebase** — `git rebase <branch>`: worktree commits replayed on top of base branch

### Git Author Resolution

Merge commits use the first available identity:
1. `GIT_AUTHOR_NAME` / `GIT_AUTHOR_EMAIL` environment variables
2. `git config user.name` / `user.email`
3. `AUTOLOOP_GIT_NAME` / `AUTOLOOP_GIT_EMAIL` environment variables
4. Fallback: `autoloop` / `autoloop@local`

## CLI Flags

- `--worktree` — force worktree isolation
- `--no-worktree` — force shared checkout
- `--merge-strategy <squash|merge|rebase>` — override merge strategy
- `--automerge` — automatically merge on successful completion
- `--keep-worktree` — preserve worktree directory after run ends

## Worktree Metadata

Stored at `.autoloop/worktrees/<runId>/meta.json`:

- `run_id` — unique identifier
- `branch` — git branch name (e.g., `autoloop/run-abc123`)
- `worktree_path` — absolute path to worktree directory
- `base_branch` — branch the worktree was created from
- `status` — `running`, `completed`, `failed`, `merged`, or `removed`
- `merge_strategy` — configured merge strategy
- `created_at` / `merged_at` / `removed_at` — ISO 8601 timestamps

## Chain Behavior

When a chain step runs inside a worktree, planning-category steps suppress worktree isolation (they run with `--no-worktree` internally since they don't modify code). Code-modifying steps inherit the parent's worktree settings.
