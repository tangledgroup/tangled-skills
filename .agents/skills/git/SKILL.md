---
name: git
description: Manage version-controlled projects with Git - essential commands for daily development workflows including staging, committing, branching, merging, and remote synchronization
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - version-control
  - git
  - source-code-management
  - collaboration
category: version-control
required_environment_variables: []
---

# Git Basic

Essential Git commands for daily version control workflows. Use this skill for common operations like staging changes, committing, branching, merging, and syncing with remote repositories.

## When to Use

- Initialize new repositories or clone existing ones
- Stage and commit code changes
- Create and switch between branches
- Merge or rebase branches
- Push/pull changes to/from remote repositories
- View commit history and diffs
- Reset or revert unwanted changes

## Setup

```bash
# Configure your identity (required once)
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Optional: Set default editor
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "nvim"         # Neovim
```

## Usage

### Initialize or Clone Repository

```bash
# Create new repository in current directory
git init

# Clone existing repository
git clone https://github.com/user/repo.git
git clone git@github.com:user/repo.git  # SSH
```

### Stage and Commit Changes

```bash
# See what changed
git status

# Stage specific files
git add file1.txt src/module.js

# Stage all changes in tracked files
git add .

# Commit staged changes
git commit -m "Add feature X"

# Or skip staging (tracked files only)
git commit -am "Fix bug Y"
```

### View History and Diffs

```bash
# Recent commits
git log --oneline -10

# With file changes
git log -p -5

# Changes since last commit
git diff

# Staged changes (ready to commit)
git diff --staged
```

### Branch Operations

```bash
# List branches (* = current)
git branch

# Create and switch to new branch
git switch -c feature-branch

# Switch to existing branch
git switch main

# Create branch without switching
git branch bugfix-123

# Delete merged branch
git branch -d old-feature
```

### Merge Changes

```bash
# Merge branch into current
git merge feature-branch

# Fast-forward only (no merge commit)
git merge --ff-only feature-branch

# Abort merge in progress
git merge --abort
```

### Rebase Branches

```bash
# Rebase current branch onto main
git switch feature-branch
git rebase main

# Interactive rebase (last 5 commits)
git rebase -i HEAD~5

# Abort if conflicts occur
git rebase --abort

# Continue after resolving conflicts
git add <resolved-files>
git rebase --continue
```

### Sync with Remote

```bash
# Fetch latest changes (doesn't modify working directory)
git fetch origin

# Pull and merge remote changes
git pull origin main

# Push current branch to remote
git push origin feature-branch

# Push all branches
git push --all origin

# Force push (use carefully!)
git push --force-with-lease origin main
```

### Reset and Restore

```bash
# Unstage file but keep changes
git restore --staged file.txt

# Discard unstaged changes
git restore file.txt

# Soft reset (keep changes staged)
git reset --soft HEAD~1

# Mixed reset (keep changes unstaged)
git reset HEAD~1

# Hard reset (discard all changes - dangerous!)
git reset --hard HEAD~1
```

### Checkout Files or Commits

```bash
# Checkout file from another branch
git checkout main -- path/to/file.txt

# View commit without switching
git show commit-hash

# Create branch at specific commit
git switch -c new-branch commit-hash
```

## Reference Files

- `{baseDir}/references/01-git-setup-and-init.md` - Initial configuration and repository setup
- `{baseDir}/references/02-git-staging-and-committing.md` - Staging area, commits, and messages
- `{baseDir}/references/03-git-branching.md` - Branch creation, switching, and management
- `{baseDir}/references/04-git-merging.md` - Merge strategies and conflict resolution
- `{baseDir}/references/05-git-rebase.md` - Interactive rebasing and history rewriting
- `{baseDir}/references/06-git-remote-operations.md` - Clone, fetch, pull, push workflows
- `{baseDir}/references/07-git-reset-and-restore.md` - Undoing changes safely
- `{baseDir}/references/08-git-log-and-diff.md` - Viewing history and comparing changes
- `{baseDir}/references/09-git-stash.md` - Temporarily saving work in progress
- `{baseDir}/references/10-git-tags.md` - Version tagging and releases
- `{baseDir}/references/11-git-workflows.md` - Common branching workflows (Git Flow, GitHub Flow)
- `{baseDir}/references/12-git-troubleshooting.md` - Common issues and solutions

## Troubleshooting

- **Merge conflicts**: Edit conflicted files, remove markers, `git add`, then `git commit`
- **Wrong branch**: Switch with `git switch correct-branch` before committing
- **Need to undo commit**: Use `git reset --soft HEAD~1` to keep changes staged
- **Messy history**: Interactive rebase with `git rebase -i HEAD~n` to squash/amend
- **Lost work**: Check reflog: `git reflog` to find lost commits
