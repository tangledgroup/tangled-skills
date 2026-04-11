# Git Log and Diff

## Viewing Commit History

### Basic Log Commands

```bash
# Full log output
git log

# One line per commit (most common)
git log --oneline

# Last N commits
git log -10
git log --oneline -20

# With pagination disabled
git log --no-pager
```

### Log with Graph Visualization

```bash
# Simple graph
git log --graph --oneline

# All branches in graph
git log --graph --oneline --all

# Decorated (show branch names)
git log --graph --oneline --decorate --all

# Side-by-side with file changes
git log --graph --stat --oneline -20
```

### Log Formatting Options

```bash
# Custom format
git log --pretty=format:"%h - %an, %ar : %s"

# Common format options:
%H  = Full commit hash
%h  = Abbreviated hash
%T  = Tree hash
%t  = Abbreviated tree hash
%P  = Parent hashes
%p  = Abbreviated parent hashes
%an = Author name
%ae = Author email
%ad = Author date
%ar = Author date (relative)
%sn = Committer name
%sd = Committer date
%s  = Subject (commit message first line)
%b  = Body (rest of commit message)
%f  = Full diff

# Example: Detailed format
git log --pretty=format:"%h %ad | %an | %s" --date=short
```

## Filtering Commit Log

### By Author/Committer

```bash
# Commits by specific author
git log --author="john"
git log --author="johndoe" --all

# By email
git log --author="@company.com"

# By committer (may differ from author)
git log --committer="alice"
```

### By Time Range

```bash
# Since specific date
git log --since="2 weeks ago"
git log --since="2024-01-01"
git log --since="last Monday"

# Until specific date
git log --until="2024-06-01"

# Between dates
git log --since="2024-01-01" --until="2024-03-01"

# Last N days
git log --after="3.days ago"
```

### By File/Path

```bash
# Commits touching specific file
git log src/app.js
git log -- path/to/file.txt

# Multiple files
git log -- src/app.js src/helper.js

# Directory and subdirectories
git log -- src/

# Exclude paths
git log --all --no-walk -- . ':(exclude)vendor/'
```

### By Commit Message

```bash
# Grep in commit messages
git log --grep="fix"
git log --grep="bug" --all

# Case-insensitive grep
git log --grep="BUG" -i

# Extended regex
git log --grep="#[0-9]+" --all

# Grep in author field too
git log --all-match --grep="fix" --author="john"
```

### By Commit Range

```bash
# Commits in branch not in main
git log main..feature-branch

# Commits in either branch (union)
git log main...feature-branch

# Last 5 commits
git log HEAD~5..HEAD

# Between two specific commits
git log abc1234..def5678

# Exclude range
git log --not main feature-branch
```

## Viewing Differences

### Basic Diff Commands

```bash
# Changes in working directory (not staged)
git diff

# Staged changes (ready to commit)
git diff --staged
git diff --cached  # Alternative syntax

# All changes (staged + unstaged)
git diff HEAD

# Compare with specific commit
git diff abc1234
```

### Diff Between Branches/Commits

```bash
# Compare two branches
git diff main feature-branch

# Compare two commits
git diff abc1234 def5678

# Compare branch to remote
git diff main origin/main

# Stat summary only
git diff --stat main feature-branch
```

### Diff in Log Output

```bash
# Show patch for each commit
git log -p

# Last 5 commits with patches
git log -p -5

# Summary of changes per commit
git log --stat

# With file summaries
git log --summary

# Name-only (files changed)
git log --name-only
git log --name-status  # With A/M/D status
```

## Diff Options and Formatting

### Colored Output

```bash
# Force color
git diff --color

# Configure color permanently
git config --global color.diff auto
git config --global color.ui auto
```

### Ignore Whitespace Changes

```bash
# Ignore all whitespace
git diff -w
git diff --ignore-all-space

# Ignore whitespace changes only
git diff -b
git diff --ignore-blank-lines

# Ignore whitespace at EOL
git diff --ignore-space-at-eol
```

### Unified Context

```bash
# Default: 3 lines context
git diff -U3

# More context (10 lines)
git diff -U10

# No context (just changed lines)
git diff -U0
```

### Word-Diff Mode

```bash
# Show changes word-by-word
git diff --word-diff

# Colored word diff
git diff --word-diff-color

# Plain text word diff
git diff --word-diff=plain
```

## Comparing Specific Stages

### Four-Stage Comparison

```
HEAD (last commit)  vs  Index (staged)  vs  Working Directory  vs  Other Branch
     |                       |                    |                    |
     +-----------+-----------+--------------------+--------------------+
                 |           |                    |
            git diff --staged   git diff         git diff HEAD
```

```bash
# Working directory vs HEAD (all changes)
git diff HEAD

# Index vs HEAD (staged changes)
git diff --staged

# Working directory vs Index (unstaged changes)
git diff

# Working directory vs other branch
git diff feature-branch
```

## Interactive Diff Tools

### Configure External Diff Tool

```bash
# List available tools
git difftool --tool-help

# Set default tool
git config --global diff.tool vscode  # VS Code
git config --global diff.tool meld    # Meld
git config --global diff.tool kdiff3  # KDiff3

# Run diff tool
git difftool main...feature-branch
```

### Common Diff Tools Setup

```bash
# VS Code
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait $LOCAL $REMOTE'

# Meld (Linux/macOS)
git config --global diff.tool meld
git config --global difftool.meld.cmd 'meld $LOCAL $REMOTE'

# KDiff3 (Linux/Windows)
git config --global diff.tool kdiff3
git config --global difftool.kdiff3.cmd 'kdiff3 $LOCAL $REMOTE'
```

## Useful Log/Diff Workflows

### Review Changes Before Merge

```bash
# See what will change if you merge
git log main..feature-branch --oneline  # Commits to be merged
git diff main feature-branch           # All changes
git diff --stat main feature-branch    # Summary
```

### Find When Bug Was Introduced

```bash
# Binary search through history
git bisect start
git bisect bad HEAD                    # Current is bad
git bisect good v1.0.0                # Known good version
# Test at each midpoint, mark good/bad
git bisect good   # or git bisect bad
git bisect reset  # When done

# Or use blame to see line-by-line history
git blame src/app.js
```

### Track File History

```bash
# Log for specific file (with renames)
git log --follow -- src/moved-file.js

# See when file was added/renamed
git log --diff-filter=A -- src/new-file.js
git log --diff-filter=R -- src/old-name.js

# Show file content at specific commit
git show abc1234:src/app.js
```

### Compare Remote and Local

```bash
# Fetch first
git fetch origin

# See what's on remote that you don't have
git log main..origin/main --oneline

# See what you have that remote doesn't
git log origin/main..main --oneline

# Full diff
git diff main origin/main
```

## Best Practices

1. **Use --oneline for quick reviews** - Easier to scan history
2. **Filter by path when debugging** - Focus on relevant files
3. **Check --stat before full diff** - Quick overview of changes
4. **Use word-diff for text files** - Clearer than line-based
5. **Set up external diff tool** - Visual comparison for complex changes

## Command Cheat Sheet

```bash
# Log basics
git log --oneline -20              # Recent commits
git log --graph --oneline --all    # Visual history
git log --since="1 week ago"       # Time filter
git log --author="name"            # Author filter
git log -- path/to/file            # File filter

# Diff basics
git diff                           # Unstaged changes
git diff --staged                  # Staged changes
git diff HEAD                      # All changes since last commit
git diff main feature              # Between branches

# Combined
git log -p -5                      # Last 5 commits with patches
git log --stat                     # Summary of changes
git difftool                       # External diff tool
```

## Troubleshooting

### Log Output Too Long

```bash
# Limit output
git log -10
git log --oneline

# Disable pager
git --no-pager log

# Filter to relevant commits
git log --since="1 month ago" --oneline
```

### Diff Shows Binary Files

```bash
# Show binary file stats only
git diff --stat

# Configure to skip binary
git config --global diff.binary false

# Use external tool for binaries
git difftool --tool=vscode
```
