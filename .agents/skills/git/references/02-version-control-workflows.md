# Version Control Workflows

This reference covers branching strategies, merging vs rebasing, remote operations, tags, and Git worktrees — the collaborative aspects of version control.

## Branch Management

### Create and List Branches

```bash
git branch                              # List all local branches
git branch --sort=-committerdate        # Sort by most recently committed
git branch -v                           # Show last commit on each branch
git branch -a                           # List all (local + remote-tracking)
git switch -c <name>                    # Create and switch to new branch
git checkout -b <name>                  # Legacy: create and switch to new branch
```

### Switch Between Branches

```bash
git switch <name>                       # Switch to existing branch
git checkout <name>                     # Legacy: switch to existing branch
git switch -                            # Switch back to previous branch
git checkout -                           # Legacy: same as above
```

### Delete Branches

```bash
git branch -d <name>                    # Delete merged branch (safe)
git branch -D <name>                    # Force delete (even if unmerged)
```

## Combining Diverged Branches

There are three primary strategies for combining work from different branches:

### Strategy 1: Rebase

Replay your branch's commits on top of another branch, creating a linear history.

```bash
git switch banana                       # Switch to the feature branch
git rebase main                         # Replay banana's commits onto main
```

**Before:**
```
A -- B -- C  (main)
      \
       D -- E  (banana)
```

**After:**
```
A -- B -- C  (main)
         \
          D' -- E'  (banana)
```

**Pros:** Clean linear history. **Cons:** Rewrites history — only use on local/unpushed branches.

### Strategy 2: Merge

Create a merge commit that combines both branch histories.

```bash
git switch main                         # Switch to target branch
git merge banana                        # Merge feature into main
```

**Before:**
```
A -- B -- C  (main)
      \
       D -- E  (banana)
```

**After:**
```
A -- B -- C
      \   / \
       D -- E  M  (main)
```

**Pros:** Preserves full history including branch point. **Cons:** Can produce merge commits; non-linear history.

### Strategy 3: Squash Merge

Combine all commits from a branch into a single new commit on the target branch.

```bash
git switch main
git merge --squash banana               # Stage all changes as one set of modifications
git commit -m "feat: integrate feature X"  # Commit them as one
```

**Result:** A single commit on `main` representing all changes from `banana`. The original branch history is not preserved in `main`.

### Fast-Forward Merge

When the target branch has no new commits since the source diverged, Git can fast-forward instead of creating a merge commit:

```bash
git switch main
git merge banana                        # Fast-forwards main to banana's tip if possible
```

**Before:**
```
A -- B -- C  (main)
      \
       D -- E  (banana)
```

**After:**
```
A -- B -- C -- D -- E  (main, banana moved here)
```

No merge commit is created. Use `git merge --no-ff` to force a merge commit even when fast-forward is possible.

## Remote Operations

### Managing Remotes

```bash
git remote -v                           # List remotes with URLs
git remote add origin <url>             # Add a new remote
git remote rename origin upstream       # Rename a remote
git remote remove origin                # Remove a remote
git remote set-url origin <new-url>     # Change remote URL
```

### Fetching — Download Remote History

```bash
git fetch                               # Download all refs from all remotes
git fetch origin                        # Download from 'origin' only
git fetch origin --prune                # Also remove stale remote-tracking branches
git fetch --all                         # Download from all configured remotes
```

**Note:** `fetch` downloads objects and refs but does NOT modify your working tree. Compare with `pull` which also merges or rebases.

### Pulling — Fetch + Merge/Rebase

```bash
git pull                                # Fetch + merge (default)
git pull --rebase                       # Fetch + rebase local commits on top
git pull origin main                    # Pull specific branch from specific remote
```

**`--rebase` vs default:** `--rebase` replays your local commits on top of fetched changes (cleaner history). Default creates a merge commit.

### Pushing — Upload Local Commits

```bash
git push                                # Push to configured upstream branch
git push origin main                    # Push 'main' to 'origin'
git push --set-upstream origin main     # Set upstream tracking for new branch
git push -f                             # Force push (rewrite remote history — DANGEROUS)
git push --force-with-lease             # Safer force push (fails if remote changed)
git push --tags                         # Push all tags
git push origin --delete <branch>       # Delete remote branch
```

**`--force-with-lease` vs `--force`:** `--force-with-lease` checks that the remote branch hasn't been updated by someone else since your last fetch. It's significantly safer for shared branches.

## Tags

### Lightweight Tags

Simple pointers to commits (no extra metadata):

```bash
git tag <name>                          # Create lightweight tag at HEAD
git tag                                 # List all tags
```

### Annotated Tags

Full objects with tagger name, date, message, and optionally GPG signature:

```bash
git tag -a v1.0 -m "Release version 1.0"   # Create annotated tag
git tag -a v1.0 -s -m "Signed release"     # Create GPG-signed tag
git show v1.0                               # Show tag object details
git push origin v1.0                        # Push single tag
git push origin --tags                      # Push all tags
```

**When to use annotated tags:** For official releases (v1.0, etc.). **Lightweight tags:** for internal bookmarks or temporary labels.

## Git Worktrees

Worktrees allow multiple branches to be checked out simultaneously in separate directories — useful when you need to work on two branches at once without stashing.

```bash
git worktree add ../project-fix main        # Create worktree in sibling directory
git worktree list                           # List all worktrees
git worktree remove ../project-fix          # Remove a worktree
git worktree move ../project-fix ./fix      # Move a worktree to new location
```

**Restrictions:** You cannot have the same branch checked out in multiple worktrees simultaneously. Worktrees share the same `.git` directory (objects, refs) so they don't duplicate disk space.

## Common Workflow Patterns

### Feature Branch Workflow

1. `git switch main && git pull` — Update from remote
2. `git switch -c feature/my-feature` — Create feature branch
3. Make commits as normal
4. `git switch main && git pull` — Update before merging
5. `git switch feature/my-feature && git rebase main` — Rebase on latest
6. `git switch main && git merge feature/my-feature` — Merge (or squash merge)
7. `git branch -d feature/my-feature` — Delete feature branch

### Hotfix Workflow

1. `git switch main && git pull` — Get latest
2. `git switch -c hotfix/issue-123` — Branch from main
3. Fix and commit
4. Merge back to main with high priority
5. Tag the release if applicable

See [Core Git Commands](../01-core-git-commands.md) for foundational command reference.
See [History Rewriting](../06-history-rewriting.md) for advanced history manipulation.
