---
name: git
description: A skill for using Git version control system to track changes, collaborate, and manage code repositories. Use when working with Git repositories, managing branches, or collaborating on code projects.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - version-control
  - collaboration
  - repository
  - branching
category: version-control
---

# Git Version Control Skill

A comprehensive skill for using Git, the distributed version control system. This skill covers basic to advanced Git operations including branching, merging, rebasing, and collaboration workflows.

## When to Use

- Initialize a new Git repository or clone an existing one
- Track changes to files with commits
- Create and manage branches for features or fixes
- Merge or rebase branches to integrate changes
- Collaborate with teams using remote repositories
- Resolve merge conflicts
- Undo or modify previous commits
- Share changes with `push` and update with `pull`

## Quick Start

### Initialize or Clone a Repository

```bash
# Create new repository
git init my-project
cd my-project

# Clone existing repository
git clone https://github.com/user/repo.git
```

See [Repository Basics](references/01-repository-basics.md) for detailed setup instructions.

### Basic Workflow

```bash
# Check status
git status

# Add files to staging
git add <file>
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin main
```

See [Basic Operations](references/02-basic-operations.md) for detailed commands.

### Branching and Merging

```bash
# Create and switch to new branch
git checkout -b feature-name

# Or use git switch (Git 2.23+)
git switch -c feature-name

# Merge branch into current
git merge feature-name

# Rebase instead of merge
git rebase main
```

See [Branching and Merging](references/03-branching-merging.md) for workflows and conflict resolution.

### Remote Collaboration

```bash
# Fetch updates without merging
git fetch origin

# Pull and merge in one step
git pull origin main

# Push branch to remote
git push origin feature-name
```

See [Remote Operations](references/04-remote-operations.md) for collaboration patterns.

## Reference Files

- [`references/01-repository-basics.md`](references/01-repository-basics.md) - Initialize, clone, and configure repositories
- [`references/02-basic-operations.md`](references/02-basic-operations.md) - Add, commit, status, diff, log commands
- [`references/03-branching-merging.md`](references/03-branching-merging.md) - Branch management, merge, rebase, and conflict resolution
- [`references/04-remote-operations.md`](references/04-remote-operations.md) - Clone, fetch, pull, push, and remote management
- [`references/05-history-manipulation.md`](references/05-history-manipulation.md) - Reset, revert, cherry-pick, and reflog
- [`references/06-advanced-topics.md`](references/06-advanced-topics.md) - Stash, tags, blame, bisect, and submodules

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/git/`). All paths are relative to this directory.

## Common Patterns

### Feature Branch Workflow
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/my-feature

# Work on feature, commit changes
git add .
git commit -m "Add feature"

# Push and create pull request
git push origin feature/my-feature
```

### Quick Fix Workflow
```bash
# Save work in progress
git stash

# Switch to main, pull latest
git checkout main
git pull origin main

# Make fix, commit, push
git checkout -b fix/quick-fix
# ... make changes ...
git add . && git commit -m "Fix issue"
git push origin fix/quick-fix
```

See [Branching and Merging](references/03-branching-merging.md) for more workflows.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Wrong commit message | `git commit --amend -m "New message"` |
| Accidentally committed wrong files | `git reset HEAD^` or see [History Manipulation](references/05-history-manipulation.md) |
| Merge conflicts | Edit conflicted files, `git add <file>`, then `git merge --continue` |
| Need to undo last commit | `git reset --soft HEAD~1` (keeps changes) or `git reset --hard HEAD~1` (discards) |
| Lost a branch | Check `git reflog` for recovery |

For detailed troubleshooting, see [History Manipulation](references/05-history-manipulation.md).
