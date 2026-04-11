# Branching and Merging

This reference covers branch management, merging strategies, rebasing, and conflict resolution.

## Creating and Managing Branches

### Create New Branch

```bash
# Create branch (stay on current)
git branch feature-login

# Create and switch to new branch
git checkout -b feature-login

# Or with git switch (Git 2.23+)
git switch -c feature-login

# Create from specific commit
git branch feature-login abc123

# Create from remote branch
git branch feature-login origin/develop
```

### Switch Branches

```bash
# Switch to existing branch
git checkout main

# Or with git switch (Git 2.23+)
git switch main

# Switch and create if doesn't exist
git switch -c new-feature

# Force switch (discard changes)
git switch --discard-changes main
```

### List Branches

```bash
# Local branches
git branch

# All branches (local and remote)
git branch -a

# Show recent commits per branch
git branch -v

# Show which branch is merged into current
git branch --merged

# Show branches NOT merged into current
git branch --no-merged
```

### Delete Branches

```bash
# Delete local branch (must be merged or force)
git branch -d feature-old

# Force delete (even if not merged)
git branch -D feature-old

# Delete remote branch
git push origin --delete feature-old

# Or explicitly:
git push origin :feature-old
```

### Rename Branches

```bash
# Rename current branch
git branch -m new-name

# Rename specific branch
git branch -m old-name new-name

# Rename and update remote (Git 2.30+)
git branch -M new-name
git push origin --delete old-name
git push origin -u new-name
```

## Understanding Branches

### What is a Branch?

- A **branch** is a movable pointer to a commit
- `HEAD` points to your current branch (or commit in detached state)
- Default branch is typically `main` or `master`

### Branch Types

| Type | Purpose | Examples |
|------|---------|----------|
| Main | Production-ready code | `main`, `master` |
| Develop | Integration branch | `develop`, `dev` |
| Feature | New functionality | `feature/login`, `feat/auth` |
| Bugfix | Fix issues | `fix/bug-123`, `hotfix/crash` |
| Release | Pre-production | `release/v1.0` |

## Merging Branches

### Basic Merge

```bash
# Make sure you're on target branch
git checkout main

# Merge feature branch
git merge feature-login

# Merge with commit message
git merge -m "Merge feature-login into main" feature-login

# Merge remote branch directly
git merge origin/develop
```

### Merge Strategies

```bash
# Default: recursive (handles most cases)
git merge feature-branch

# Octopus (merge multiple branches at once)
git merge octopus branch1 branch2 branch3

# Resolve only, don't commit
git merge --no-commit feature-branch

# Squash all commits into one
git merge --squash feature-branch
git commit -m "Squashed feature"
```

### Merge Commit Message

When merging without `--no-ff`, Git creates a merge commit:

```
Merge branch 'feature-login' into main

This reverts commit abc123 which was incorrectly applied.
```

### Fast-Forward vs Merge Commit

```bash
# Allow fast-forward (default)
git merge feature-branch

# Always create merge commit
git merge --no-ff feature-branch

# Fast-forward only (fail if not possible)
git merge --ff-only feature-branch
```

## Rebasing

### Basic Rebase

```bash
# Rebase current branch onto main
git checkout feature-login
git rebase main

# Rebase onto specific commit
git rebase abc123

# Interactive rebase (last 5 commits)
git rebase -i HEAD~5

# Interactive rebase from main
git rebase -i main
```

### Interactive Rebase Commands

During `git rebase -i`, you can:

| Command | Action |
|---------|--------|
| `pick` | Keep commit as-is |
| `reword` | Change commit message |
| `edit` | Pause to amend commit |
| `squash` | Combine with previous commit |
| `fixup` | Combine, discard message |
| `drop` | Remove commit |
| `reverse` | Reverse commit changes |

### Rebase Example

```bash
# Before rebase:
# A---B---C (feature)
# \
#  D---E---F (main)

# After 'git rebase main' on feature:
# D---E---F---A'---B'---C' (main and feature)
```

### Abort and Continue Rebase

```bash
# Stop rebase, return to original state
git rebase --abort

# Continue after resolving conflicts
git add <resolved-files>
git rebase --continue

# Skip current commit during rebase
git rebase --skip
```

### Merge vs Rebase

| Aspect | Merge | Rebase |
|--------|-------|--------|
| History | Preserves timeline | Linear, cleaner |
| Commits | Creates merge commit | Rewrites commit hashes |
| Shared branches | Safe | **Never rebase** |
| Use case | Public/shared branches | Local feature branches |

**Rule:** Never rebase branches pushed to shared repositories.

## Resolving Conflicts

### What Causes Conflicts?

Conflicts occur when:
- Same line modified in both branches
- File deleted in one, modified in other
- Different files renamed to same name

### Conflict Workflow

```bash
# 1. Start merge/rebase (conflict occurs)
git merge feature-branch

# 2. Git marks conflicts in files
# Look for conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> feature-branch

# 3. Edit files to resolve conflicts
# Remove markers, keep desired content

# 4. Mark as resolved
git add <resolved-file>

# 5. Complete merge/rebase
git commit        # for merge
git rebase --continue  # for rebase
```

### Conflict Resolution Tools

```bash
# List conflicted files
git status

# Use mergetool (GUI or vimdiff)
git mergetool

# Configure merge tool
git config --global merge.tool vimdiff
git config --global mergetool.vimdiff.cmd 'vimdiff \"$1\" \"$3\" -o \"$2\"'

# Accept current (our) version
git checkout --ours <file>
git add <file>

# Accept incoming (their) version
git checkout --theirs <file>
git add <file>

# Show all conflict options
git checkout --help <file>
```

### Abort Merge/Rebase

```bash
# Abort merge, return to pre-merge state
git merge --abort

# Abort rebase
git rebase --abort
```

## Common Branching Workflows

### Feature Branch Workflow

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/new-feature

# 2. Work and commit
git add . && git commit -m "Add feature"

# 3. Keep up with main (optional)
git fetch origin
git rebase origin/main

# 4. Push and create PR
git push -u origin feature/new-feature

# 5. After review, merge into main
git checkout main
git pull origin main
git merge feature/new-feature
git push origin main

# 6. Clean up
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

### Git Flow (Simplified)

```bash
# Feature development
git flow feature start myfeature
# ... work ...
git flow feature finish myfeature

# Release
git flow release start 1.0.0
# ... finalize ...
git flow release finish 1.0.0

# Hotfix
git flow hotfix start 1.0.1
# ... fix ...
git flow hotfix finish 1.0.1
```

### Forking Workflow (GitHub)

```bash
# 1. Fork on GitHub, then clone your fork
git clone https://github.com/your-username/repo.git
cd repo

# 2. Add upstream remote
git remote add upstream https://github.com/original/repo.git

# 3. Create feature branch
git checkout -b feature/fix

# 4. Keep in sync with upstream
git fetch upstream
git rebase upstream/main

# 5. Push and create PR on GitHub
git push origin feature/fix
```

## Detached HEAD State

### What is Detached HEAD?

When `HEAD` points directly to a commit instead of a branch:

```bash
# Can happen when:
git checkout abc123          # Checkout by commit hash
git checkout tags/v1.0       # Checkout tag

# Check status
git status
# "HEAD is now at abc123..."
```

### Working in Detached HEAD

```bash
# Make changes and create a branch
git checkout -b new-feature-from-old-commit

# Or just return to main branch
git checkout main

# Discard changes (dangerous!)
git reset --hard main
```

## Best Practices

1. **Use descriptive branch names**: `feature/add-login`, not `feat` or `test`
2. **Rebase local branches** before merging to keep history clean
3. **Never rebase shared branches** - use merge instead
4. **Merge often** to avoid large conflict resolutions
5. **Delete merged branches** to keep repository clean
6. **Use pull requests** for code review before merging
7. **Keep branches focused** - one feature per branch

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot merge unrelated histories" | `git merge --allow-unrelated-histories` |
| Rebase in progress | `git rebase --abort` or `--continue` |
| Lost commit after rebase | Check `git reflog` for recovery |
| Too many conflicts | Use `git mergetool` for visual resolution |
