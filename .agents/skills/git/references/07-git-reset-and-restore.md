# Git Reset and Restore

## Understanding Undo Operations

Git provides several ways to undo changes at different stages:

```
Working Directory  <-(restore)->  Staging Area  <-(reset)->  Repository (HEAD)
```

## The restore Command (Git 2.23+)

### Discard Unstaged Changes

```bash
# Discard changes to specific file in working directory
git restore filename.js

# Discard all unstaged changes
git restore .

# From specific commit/branch
git restore --source=main filename.js
```

### Unstage Files (Keep Working Directory Changes)

```bash
# Remove from staging but keep changes
git restore --staged filename.js

# Unstage all files
git restore --staged .

# Equivalent older command:
git reset HEAD filename.js
```

### Restore Deleted File

```bash
# File was deleted but not committed
git restore deleted-file.js

# From specific commit
git restore --source=HEAD~3 deleted-file.js
```

## The reset Command

### Soft Reset (Keep Changes Staged)

```bash
# Undo last commit, keep changes staged
git reset --soft HEAD~1

# Undo multiple commits
git reset --soft HEAD~3

# Result: Commit removed, changes ready to re-commit
```

### Mixed Reset (Default - Keep Changes Unstaged)

```bash
# Undo last commit, changes unstaged
git reset HEAD~1

# Same as --mixed (default behavior)
git reset --mixed HEAD~1

# Result: Commit removed, changes in working directory
```

### Hard Reset (Discard All Changes - DANGEROUS!)

```bash
# Undo last commit and ALL changes
git reset --hard HEAD~1

# Reset to specific commit
git reset --hard abc1234

# WARNING: All unstaged changes are lost permanently!
```

### Reset Without Moving HEAD

```bash
# Update staging area to match commit
git reset --abc1234

# Update working directory to match staging
git reset -abc1234

# Update both (like --hard but specific commit)
git reset --abc1234
```

## The revert Command

### Revert Commit (Safe for Shared History)

```bash
# Create new commit that undoes specified commit
git revert abc1234

# Revert multiple commits
git revert abc1234 def5678

# Revert range of commits (newest first)
git revert abc1234..def5678

# No-edit mode (use existing message)
git revert --no-edit abc1234
```

### Revert Merge Commit

```bash
# Revert merge, keeping other parent's changes
git revert -m 1 MERGE_COMMIT_HASH

# -m 1 = keep first parent (main branch)
# -m 2 = keep second parent (feature branch)
```

## Comparing Reset vs Revert

### Use reset When:
- Working on local/private branches
- Want to completely remove commits from history
- No one else has pulled the commits
- Need to rewrite history before pushing

### Use revert When:
- Commits are already pushed/shared
- Want to preserve history (audit trail)
- Working on public branches (`main`, `master`)
- Need safe undo that others can pull

## Practical Undo Scenarios

### Scenario 1: Wrong Commit Message

```bash
# Just changed your mind about message
git commit --amend -m "Correct commit message"

# Or open editor to edit
git commit --amend
```

### Scenario 2: Forgot to Add File

```bash
# File should have been in last commit
git add forgotten-file.js
git commit --amend --no-edit
```

### Scenario 3: Bad Commit Before Pushing

```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Fix issues, then re-commit
git add .
git commit -m "Fixed commit message"
```

### Scenario 4: Bad Commit Already Pushed

```bash
# Create revert commit (safe for shared history)
git revert HEAD

# Push the revert
git push origin main

# Alternative: If you own the branch and no one pulled
git reset --hard HEAD~1
git push --force-with-lease origin main
```

### Scenario 5: Messy Working Directory

```bash
# See what's changed
git status

# Option A: Keep some changes, discard others
git restore file-to-discard.js
git add files-to-keep.js

# Option B: Stash everything temporarily
git stash push -m "save work"
# Later: git stash pop

# Option C: Start over (dangerous!)
git reset --hard HEAD
```

### Scenario 6: Accidental File Deletion

```bash
# File deleted but not committed
git restore deleted-file.js

# Or from specific commit
git checkout HEAD~1 -- deleted-file.js

# If already committed, find in history
git log -- deleted-file.js
git checkout COMMIT_HASH -- deleted-file.js
```

## The reflog - Your Safety Net

### Find Lost Commits

```bash
# View reference log (last 10 entries)
git reflog

# See all reflog entries
git reflog show HEAD

# Find specific point in time
git reflog | grep "before bad reset"
```

### Recover from Disasters

```bash
# After accidental reset --hard
git reflog  # Find the commit before disaster

# Create branch at lost commit
git switch -c recovery-branch HEAD@{1}

# Or reset to that point
git reset --hard HEAD@{1}
```

### Understanding Reflog Notation

```bash
HEAD@{0}  = Current HEAD
HEAD@{1}  = Previous position
HEAD@{2}  = Two positions ago
HEAD@{1.hour.ago}  = Position 1 hour ago
HEAD@{yesterday}   = Position yesterday
HEAD@{1.week.ago}  = Position 1 week ago
```

## Advanced Reset Techniques

### Partial Reset (Specific Files)

```bash
# Reset specific files to last commit
git reset HEAD filename.js
git checkout -- filename.js

# Or with restore (Git 2.23+)
git restore --source=HEAD filename.js
```

### Interactive Reset

```bash
# See what will be reset
git diff HEAD~1

# Choose which changes to keep
git add -p  # Select hunks to stage
git commit -m "Keep only important changes"
```

## Best Practices

1. **Use --soft first** - Safest reset, keeps changes staged
2. **Check reflog before hard reset** - Can recover if needed
3. **Prefer revert for shared commits** - Safe for everyone
4. **Test in branch first** - Try reset on feature branch before main
5. **Communicate force pushes** - Let team know before rewriting history

## Command Cheat Sheet

```bash
# Staging area operations
git restore --staged file      # Unstage file
git reset HEAD file           # Old way to unstage

# Working directory operations  
git restore file              # Discard unstaged changes
git checkout -- file          # Old way to discard

# Commit operations
git reset --soft HEAD~1       # Undo commit, keep staged
git reset HEAD~1              # Undo commit, keep unstaged
git reset --hard HEAD~1       # Undo commit, lose all (dangerous!)
git revert HEAD               # Create undo commit (safe)

# Recovery
git reflog                    # Find lost commits
git reset --hard HEAD@{1}     # Recover from reflog
```

## Troubleshooting

### Can't Reset (Clean Working Directory Required)

```bash
# Git won't reset if you have uncommitted changes
git status  # Check what's changed

# Option 1: Commit changes first
git add . && git commit -m "Save before reset"

# Option 2: Stash changes
git stash push -m "temp save"

# Option 3: Force (loses changes!)
git reset --hard HEAD
```

### Reset Wrong Commit

```bash
# Check reflog immediately
git reflog

# Reset to correct position
git reset --hard HEAD@{1}  # Or appropriate number
```

### Lost Work After Hard Reset

```bash
# Reflog saves HEAD positions for 90 days
git reflog

# Find commit before reset
git reflog | head -20

# Recover with new branch
git switch -c recovered HEAD@{n}
```
