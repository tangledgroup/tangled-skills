# Essential Commands

## Initialize and Clone

```bash
# Start a new repository
git init
# Clone an existing remote repository
git clone <url>
```

## Stage and Commit

```bash
# Stage a specific file
git add <file>
# Stage all untracked and modified files
git add .
# Interactively choose hunks to stage
git add -p
# Move/rename a file (updates index)
git mv <old> <new>
# Remove a file from working dir and index
git rm <file>
# Stop tracking without deleting
git rm --cached <file>
# Show staged, unstaged, and untracked files
git status
```

## Make Commits

```bash
# Open editor for commit message
git commit
# Commit with inline message
git commit -m 'message'
# Stage all tracked changes and commit
git commit -am 'message'
# Modify the most recent commit (message or contents)
git commit --amend
```

## Branch and Switch

```bash
# Switch to branch <name>
git switch <name>
# Create and switch to new branch
git switch -c <name>
# Alternative: switch branches
git checkout <name>
# Alternative: create and switch branch
git checkout -b <name>
# List local branches
git branch
# Sort by most recent commit
git branch --sort=-committerdate
# Delete a merged branch
git branch -d <name>
# Force delete (even if unmerged)
git branch -D <name>
```

## Diff and Show

```bash
# Unstaged changes (working dir vs index)
git diff
# Staged changes (index vs HEAD)
git diff --staged
# All changes vs latest commit
git diff HEAD
# Changes in a specific commit
git show <commit>
# Summary of a commit's changes
git show <commit> --stat
# Diff between two commits
git diff <commit1> <commit2>
```

## Ways to Refer to Commits

`main` → branch name
`v0.1` → tag name
`3e887ab` → commit ID (short hash)
`origin/main` → remote branch
`HEAD` → current commit
`HEAD~3` → three commits before HEAD
`HEAD^^^` → three parents back (alt syntax)

## Discard Changes

```bash
# Undo unstaged changes to a file
git restore <file>
# Alternative: discard working dir changes
git checkout <file>
# Unstage and discard
git restore --staged --worktree <file>
# Unstage a specific file
git reset <file>
# Unstage everything
git reset
# Discard all staged and unstaged changes
git reset --hard
# Remove untracked files
git clean
# Temporarily save all working changes
git stash
```

## Edit History

```bash
# Undo the most recent commit (keep changes)
git reset HEAD^
# Interactive rebase of last 5 commits; change "pick" to "fixup" to squash
git rebase -i HEAD~6
# Find lost commits after a failed rebase
git reflog BRANCHNAME
```

## Merge and Rebase

```bash
# Switch to target branch
git switch main
# Merge branch into current branch
git merge banana
# Switch to feature branch
git switch banana
# Rebase feature onto main (linear history)
git rebase main
```

## Remotes, Push, Pull

```bash
# List remotes and their URLs
git remote -v
# Download commits without merging
git fetch origin
# Fetch and merge remote changes
git pull origin main
# Upload local commits to remote
git push origin main
```

## Log and Blame

```bash
# Show commit history for a branch
git log main
# Graph-shaped history view
git log --graph main
# Compact one-line-per-commit
git log --oneline
# Commits that modified a file
git log <file>
# Track renames across history
git log --follow <file>
# Commits adding/removing "banana" text
git log -G banana
# Show who last changed each line
git blame <file>
```
