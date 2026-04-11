# Git Staging and Committing

## The Three Areas

Git has three main areas for file management:

1. **Working Directory** - Your actual files on disk
2. **Staging Area (Index)** - Files prepared for next commit
3. **Repository (.git)** - Permanently committed snapshots

```
Working Directory  --(git add)-->  Staging Area  --(git commit)-->  Repository
       |                                       ^
       +----------(git restore)----------------+
```

## Checking Status

```bash
# Basic status
git status

# Short format (machine-readable)
git status -s

# Include ignored files
git status --ignored

# Show untracked files as individual entries
git status --untracked-files=all
```

### Status Output Interpretation

```
On branch main
Changes to be committed:      # Staged changes (will be committed)
  (use "git restore --staged <file>..." to unstage)
        modified:   src/app.js

Changes not staged for commit: # Unstaged changes in working directory
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md

Untracked files:              # New files not yet staged
  (use "git add <file>..." to include in what will be committed)
        src/utils.js
```

## Staging Files

### Stage Specific Files

```bash
# Stage individual files
git add file1.txt
git add src/module.js src/helper.js

# Stage with glob patterns
git add *.md
git add src/**/*.js
```

### Stage All Changes

```bash
# Stage all tracked and new files
git add .

# Stage only tracked files (ignores new files)
git add -A

# Interactive staging (choose hunks)
git add -p

# Stage deletions too
git add -u
```

### Stage Specific Changes (Hunks)

```bash
# Interactive patch mode - choose which changes to stage
git add -p filename.js

# Prompts for each change block:
# y = stage this hunk
# n = skip this hunk
# a = stage all remaining
# s = split hunk into smaller pieces
# q = quit
```

### Unstage Files

```bash
# Unstage specific file (keep changes in working directory)
git restore --staged filename.js

# Alternative syntax (older Git versions)
git reset HEAD filename.js

# Unstage all files
git restore --staged .
```

## Making Commits

### Basic Commit

```bash
# Commit staged changes with message
git commit -m "Add user authentication feature"

# Open editor for commit message
git commit

# Commit all tracked files (skip staging)
git commit -am "Fix typo in README"
```

### Commit Message Best Practices

```
Subject line (max 50 chars)

Blank line

Optional body (wrap at 72 chars) explaining:
- What changed and why
- How it was tested
- Related issues or PRs

Co-authored-by: Name <email@example.com>
```

### Multi-line Commit Messages

```bash
# Interactive commit with editor
git commit

# Or provide message via stdin
git commit -m "Subject line" -m "Additional context in body"

# Amend previous commit (change message or add forgotten files)
git commit --amend
git commit --amend --no-edit  # Keep same message
```

### Signed Commits

```bash
# GPG-signed commit (requires GPG key setup)
git commit -S -m "Security fix"

# Configured globally
git config --global commit.gpgSign true
```

## Commit History

### View Recent Commits

```bash
# Basic log
git log

# One line per commit
git log --oneline

# Last 10 commits
git log -10

# With file changes (stat)
git log --stat

# Graph visualization
git log --graph --oneline --all

# Pretty format
git log --pretty=format:"%h - %an, %ar : %s"
```

### Filter Commit Log

```bash
# Commits by author
git log --author="john"

# Commits in date range
git log --since="2 weeks ago" --until="1 week ago"

# Commits touching specific files
git log src/app.js
git log -- path/to/file.txt

# Commits with specific message text
git log --grep="fix"
git log --grep="bug" --all
```

## Discarding Changes

### Unstaged Changes (Working Directory)

```bash
# Discard changes to single file
git restore filename.js

# Alternative (older Git)
git checkout -- filename.js

# Discard all unstaged changes
git restore .
```

### Staged Changes

```bash
# Unstage and discard changes
git restore --staged filename.js
git restore filename.js

# Or in one step (Git 2.23+)
git restore --source=HEAD filename.js
```

### All Changes Since Last Commit

```bash
# Reset to last commit (lose all changes - dangerous!)
git reset --hard HEAD

# Reset working directory only
git checkout .
```

## Amend Commits

### Modify Last Commit

```bash
# Change commit message
git commit --amend -m "New commit message"

# Add forgotten files to last commit
git add forgotten-file.js
git commit --amend --no-edit

# Change author of last commit
git commit --amend --author="Name <email@example.com>"
```

### Amend Multiple Commits (Interactive Rebase)

```bash
# Interactively amend last 5 commits
git rebase -i HEAD~5

# Commands in editor:
# pick = keep commit as-is
# rewrite/reword = change message
# edit/e = stop to modify commit
# squash/s = merge with previous commit
# fixup/f = merge with previous (discard message)
# drop/d = remove commit
```

## Best Practices

1. **Atomic commits** - One logical change per commit
2. **Descriptive messages** - Clear subject, detailed body when needed
3. **Stage carefully** - Review staged changes before committing
4. **Commit often** - Small commits are easier to review and revert
5. **Use amend for typos** - Fix mistakes in last commit before pushing

## Useful Commands Summary

```bash
# Quick workflow
git status              # Check what changed
git add file.js         # Stage specific files
git diff --staged       # Review staged changes
git commit -m "message" # Commit

# Common scenarios
git add -p             # Interactive staging
git commit -am "msg"   # Skip staging for tracked files
git commit --amend     # Fix last commit
git log --oneline -10  # Recent history
```
