# Core Git Commands

This reference covers the foundational Git commands used in daily development workflows: repository creation, snapshotting, diffing, stashing, restoring, resetting, and viewing history.

## Repository Creation

### Initialize a New Repository

```bash
git init                    # Create .git directory in current folder
git init --bare             # Create bare repo (server-side only, no working tree)
git init -b main            # Set default branch name to 'main' (Git 2.28+)
```

### Clone an Existing Repository

```bash
git clone <url>                          # Full clone with all history
git clone --branch <name> <url>          # Clone a specific branch
git clone --depth 1 <url>                # Shallow clone (only latest commit)
git clone --single-branch <url>           # Clone single branch only
git clone --sparse <url>                  # Sparse checkout (clone without subdirectories)
```

## Daily Snapshotting Workflow

### Check Working Tree Status

```bash
git status                            # Show working tree status
git status -s                         # Short format (one line per file)
git status -sb                        # Short format with branch info
git status --untracked-files=no       # Hide untracked files from output
```

Output columns:
- `??` — Untracked (new, not yet added)
- `A ` — Added to staging (green in color output)
- ` M` — Modified in working tree (not staged)
- `MM` — Modified in both working tree and staging

### Stage Changes for Commit

```bash
git add <file>                        # Stage a specific file
git add .                             # Stage all modified + new files in current dir tree (not deleted)
git add -p                            # Interactive staging (hunk by hunk)
git add -A                            # Stage ALL changes: modified, new, and deleted (entire repo)
git add -u                            # Stage only modified/deleted tracked files (ignores untracked)
```

**Key differences between `add .`, `add -A`, and `add -u`:**

| Command | New files | Modified files | Deleted files | Untracked files |
|---------|-----------|---------------|---------------|----------------|
| `git add .` | ✅ (in dir tree) | ✅ | ❌ | ❌ |
| `git add -A` | ✅ | ✅ | ✅ | ❌ |
| `git add -u` | ❌ | ✅ | ✅ | ❌ |

> **Rule of thumb:** Use `git add -A` when committing all changes. Use `git add .` when you only want to stage files in the current directory tree. Use `git add -u` when working with a clean repo (no new files).

### Interactive Staging (`-p`)

When you've changed multiple things but want to commit them separately:

```bash
git add -p                        # Interactive: accept/reject hunks
git add -p <file>                 # Interactive for a specific file
```

In interactive mode, Git shows **hunks** (contiguous changed blocks). Press:
- `y` — accept this hunk
- `n` — skip this hunk
- `e` — manually edit which lines to stage
- `s` — split hunk into smaller pieces
- `q` — quit, accepting none of the remaining hunks
- `a` — accept all remaining hunks in this file

### View Differences

```bash
git diff                              # Unstaged changes (working tree vs index)
git diff --staged                     # Staged changes (index vs HEAD)
git diff HEAD                         # All changes (staged + unstaged vs HEAD)
git diff <file>                       # Changes in specific file
git diff <commit1> <commit2>          # Diff between two commits
git diff <commit> -- <file>           # Diff one file since a commit
git diff --stat                       # Summary of changes (files changed, insertions/deletions)
```

### Commit Changes

```bash
git commit -m "feat: add user authentication"   # Commit with one-line message
git commit -a -m "message"                      # Auto-stage modified+deleted + commit (skips add)
git commit                                      # Open editor for detailed message (recommended)
git commit --amend                              # Modify the most recent commit
git commit --amend --no-edit                    # Amend without changing message
git commit --verbose                            # Show diff in commit editor
```

**Amending commits:** Use `--amend` to fix mistakes in the last commit (add forgotten files, fix typo in message). Only amend **local, unpushed** commits.

```bash
# Workflow: commit, then realize you forgot a file
git commit -m "feat: add user authentication"
git add forgotten_file.py                       # Stage the missed file
git commit --amend --no-edit                    # Fold it into previous commit
git push --force-with-lease                     # Update remote (safe force-push)
```

**`git commit -a` vs `git add + git commit`:** `-a` auto-stages all modified and deleted tracked files before committing, but ignores untracked (new) files. Use it for quick commits when you know there are no new files to stage.

## Stashing Changes

Stash temporarily saves uncommitted changes without committing them.

```bash
git stash                             # Stash all staged and unstaged changes
git stash save "description"          # Stash with a label (deprecated, use 'git stash push')
git stash push -m "description"       # Stash working tree changes only
git stash push -u                     # Include untracked files
git stash push --staged               # Include staged changes only
git stash list                        # List all stashes
git stash show                        # Show changes in most recent stash
git stash show -p                     # Show patch format diff
git stash apply                       # Apply most recent stash (keeps it)
git stash apply stash@{2}             # Apply specific stash
git stash pop                         # Apply and remove most recent stash
git stash drop stash@{1}              # Delete a specific stash
git stash clear                       # Remove all stashes
git stash branch <name> <stash>       # Create branch from stash and apply it
```

**Stash reference syntax:** `stash@{0}` is the most recent, incrementing numbers go back in time.

## Restoring and Resetting

### Restore (Git 2.23+) — Modern Approach

```bash
git restore <file>                    # Discard unstaged changes to one file
git restore --staged <file>           # Unstage a file (move from index to working tree)
git restore --staged --worktree <file> # Unstage AND discard working tree changes
git restore .                         # Discard all unstaged changes in current dir
```

### Reset — Legacy but Powerful

```bash
git reset HEAD <file>                 # Unstage a file (same as 'restore --staged')
git reset --soft HEAD^                # Undo last commit, keep changes staged
git reset --mixed HEAD^               # Undo last commit, keep changes unstaged (default)
git reset --hard HEAD^                # Undo last commit, discard all changes
git reset --hard                      # Discard ALL staged and unstaged changes
```

**Reset modes:**
- `--soft` — Moves HEAD back, keeps index and working tree intact
- `--mixed` (default) — Moves HEAD back, resets index to new HEAD, keeps working tree
- `--hard` — Moves HEAD back, resets index AND working tree to match

### Remove and Rename Files

```bash
git rm <file>                         # Remove file from index and working tree
git rm --cached <file>                # Remove from index only (keep on disk)
git mv <old> <new>                    # Move/rename file and update index
```

## Viewing History

### Log Commands

```bash
git log                               # Full history with diffs
git log --oneline                     # One line per commit
git log --graph                       # ASCII graph of branch structure
git log --oneline --graph             # Combined compact view
git log <branch>                      # Show commits reachable from a branch
git log --follow <file>               # Track file across renames
git log -G "banana"                   # Find commits that added/removed text matching pattern
git log --since="2 weeks ago"         # Limit by date
git log --until="2024-01-01"          # Limit by date
git log --author="John"               # Filter by author
git log --grep="feat"                 # Filter by commit message
```

### Show Specific Commits

```bash
git show <commit>                     # Show a commit and its diff
git show <commit> --stat              # Show commit with file change summary
git show HEAD                         # Show the most recent commit
git show HEAD~3                       # Show 3 commits before HEAD
```

### Blame — Line-by-Line Attribution

```bash
git blame <file>                      # Show who last modified each line
git blame -L 10,20 <file>             # Blame specific line range
git blame -C <file>                   # Detect code moves and copies
```

## Ways to Refer to a Commit

Every time a command says `<commit>`, you can use any of these references:

| Reference | Example | Meaning |
|-----------|---------|---------|
| Branch name | `main` | Tip of the branch |
| Tag | `v0.1` | A named point in history |
| Commit ID | `3e887ab` | Full or abbreviated SHA-1 hash |
| Remote branch | `origin/main` | Tip of a remote-tracking branch |
| Current commit | `HEAD` | Currently checked-out commit |
| N commits ago | `HEAD~3` or `HEAD^^^` | Three parents back from HEAD |

## Discarding Changes Summary

| Goal | Command |
|------|---------|
| Delete unstaged changes to one file | `git restore <file>` |
| Delete all staged and unstaged changes to one file | `git restore --staged --worktree <file>` |
| Delete ALL staged and unstaged changes (entire repo) | `git reset --hard` |
| Delete untracked files | `git clean -fd` |
| Stash all changes temporarily | `git stash` |

See [Version Control Workflows](../02-version-control-workflows.md) for branching, merging, and remote operations.
