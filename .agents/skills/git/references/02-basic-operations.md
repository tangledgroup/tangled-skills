# Basic Operations

This reference covers the fundamental Git commands for tracking changes: `add`, `commit`, `status`, `diff`, and `log`.

## Checking Status

### View Repository Status

```bash
# Standard status
git status

# Short format (machine-readable)
git status -s

# Show all files including ignored
git status --ignored

# Show untracked files as per-directory summaries
git status -u
```

### Status Output Explanation

```
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>" to unstage)
        modified:   src/app.js
        new file:   src/utils.js

Changes not staged for commit:
  (use "git add <file>" to update what will be committed)
  (use "git restore <file>" to discard changes in working directory)
        modified:   README.md

Untracked files:
  (use "git add <file>" to include in what will be committed)
        tests/
```

## Adding Files (Staging)

### Basic Add Commands

```bash
# Add specific file
git add src/app.js

# Add all files in directory
git add src/

# Add all changes (new, modified, deleted)
git add .

# Add only modified and deleted files
git add -u

# Add with verbose output
git add -v .
```

### Interactive Staging

```bash
# Interactive mode (line-by-line selection)
git add -i

# Patch mode (choose hunks interactively)
git add -p

# Edit the patch before staging
git add -e

# Refresh staged files without changing index
git add --refresh
```

### Intent to Add

```bash
# Mark file for addition without actually adding content
# Useful when file doesn't exist yet
git add -N newfile.txt

# Later, when file is created, finalize with:
git add newfile.txt
```

## Viewing Differences

### Diff Working Directory

```bash
# See changes not staged
git diff

# See changes in specific file
git diff src/app.js

# Show only filename and change type
git diff --name-status

# Show only filenames
git diff --name-only

# Show stat summary
git diff --stat
```

### Diff Staged Changes

```bash
# See what's staged for commit
git diff --staged

# Also works with:
git diff --cached
git diff HEAD
```

### Diff Between Commits

```bash
# Compare two commits
git diff abc123 def456

# Compare branch to current
git diff main..feature-branch

# Compare specific ranges
git diff v1.0..v2.0
```

### Diff Options

```bash
# Ignore whitespace changes
git diff -w

# Ignore all whitespace
git diff -B

# Show word-level differences
git diff --word-diff

# Colored output (usually default)
git diff --color

# Unified context (number of lines)
git diff -U5
```

## Committing Changes

### Basic Commits

```bash
# Commit staged changes with message
git commit -m "Add new feature"

# Open editor for commit message
git commit

# Amend last commit
git commit --amend

# Amend without changing message
git commit --amend --no-edit
```

### Commit Message Best Practices

```
feat: Add user authentication system

- Implement login with email/password
- Add JWT token generation
- Create session management
- Add logout functionality

Closes #123
```

**Format:**
- **Header**: 50 chars max, imperative mood ("Add" not "Added")
- **Body**: Wrap at 72 chars, explain what and why (not how)
- **Footer**: Reference issues (Closes #123), breaking changes

### Commit Options

```bash
# Commit all files (skip staging)
git commit -a -m "Quick fix"

# Commit specific file
git commit src/app.js -m "Fix bug in app"

# Allow empty commit (rarely needed)
git commit --allow-empty -m "Trigger CI"

# Add sign-off (certification of origin)
git commit -s

# GPG sign commit
git commit -S

# Use different author
git commit --author="John Doe <john@example.com>"
```

### Interactive Commit

```bash
# Choose which staged files to commit
git commit --patch

# Edit list of files being committed
git commit --edit
```

## Viewing History

### Basic Log

```bash
# Show all commits
git log

# One line per commit
git log --oneline

# Show graph of branches
git log --graph

# Combine graph and oneline
git log --graph --oneline --all
```

### Log with More Info

```bash
# Show all changes in each commit
git log -p

# Show stats only
git log --stat

# Show author and committer dates
git log --format=fuller

# Custom format
git log --format="%h %an %ad %s"
```

### Log Filters

```bash
# Commits by specific author
git log --author="John"

# Commits in date range
git log --since="2 weeks ago"
git log --until="2024-01-01"

# Commits matching message pattern
git log --grep="fix"
git log --grep="^feat:"

# Files changed in commit
git log --name-only
git log --name-status

# Specific file history
git log src/app.js

# Specific path history (including renames)
git log --follow src/old-name.js
```

### Log Graphs

```bash
# All branches in graph
git log --graph --all --oneline

# Current branch and merges
git log --graph --decorate --oneline

# First parent only (linear view)
git log --graph --first-parent --oneline
```

## Undoing Changes

### Discard Working Directory Changes

```bash
# Discard changes in specific file
git restore src/app.js

# Or with checkout (older Git)
git checkout -- src/app.js

# Discard all working directory changes
git restore .

# Reset to last commit (dangerous!)
git reset --hard HEAD
```

### Unstage Files

```bash
# Unstage specific file
git restore --staged src/app.js

# Or with reset (older Git)
git reset HEAD src/app.js

# Unstage all files
git restore --staged .
```

## Useful Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    df = diff
    dg = log --graph --oneline --all
    last = log -1 HEAD
    unstage = restore --staged
```

## Common Workflows

### Single File Change

```bash
# Edit file, then:
git add src/app.js
git commit -m "Fix bug in app"
```

### Multiple Related Changes

```bash
# Make several edits across files
git add .
git commit -m "Implement feature X"
```

### WIP Commits

```bash
# Save progress with temporary commit
git add .
git commit -m "WIP: working on feature"

# Later, amend with proper message
git commit --amend -m "Proper commit message"
```
