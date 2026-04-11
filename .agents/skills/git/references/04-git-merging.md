# Git Merging

## Understanding Merge Types

Git performs different types of merges based on the commit history:

### Fast-Forward Merge
```
Before:                    After (fast-forward):
  main ──A──B              main ──A──B──C──D
           \
            feature ──C──D
```
No merge commit created; main pointer simply moves forward.

### Three-Way Merge
```
Before:                              After (merge commit):
  main ──A──B                        main ──A──B────M
           \                          \          /
            feature ──C──D──E          \──C──D──E
```
Creates new merge commit M combining both histories.

## Basic Merge Operations

### Merge Branch into Current

```bash
# Ensure you're on target branch
git switch main

# Merge feature branch
git merge feature-login

# View merge result
git log --graph --oneline -10
```

### Fast-Forward Only

```bash
# Require fast-forward (error if merge commit needed)
git merge --ff-only feature-branch

# Useful for ensuring branch is up-to-date before deletion
```

### No-Fast-Forward (Always Create Merge Commit)

```bash
# Force merge commit even if fast-forward possible
git merge --no-ff -m "Merge feature: user authentication" feature-auth

# Good for preserving feature boundaries in history
```

## Resolving Merge Conflicts

### When Conflicts Occur

Git marks conflicts in files with conflict markers:

```javascript
<<<<<<< HEAD (current branch)
const greeting = "Hello";
=======
const greeting = "Hi there";
>>>>>>> feature-branch (incoming branch)
```

### Resolution Steps

```bash
# 1. Git stops and lists conflicted files
git merge feature-branch
# Auto-merge result in index/worktree
# Conflicts: src/app.js, README.md

# 2. Edit conflicted files to resolve
# Remove conflict markers, choose or combine changes

# 3. Stage resolved files
git add src/app.js README.md

# 4. Complete merge
git commit

# Or if --no-commit was used, just:
git commit -m "Merge with conflict resolution"
```

### Abort Merge

```bash
# Cancel merge and return to pre-merge state
git merge --abort

# Works at any point during merge process
```

## Merge Strategies

### Recursive (Default)

```bash
# Standard merge for up-to-date branches
git merge feature-branch

# Options:
git merge -s recursive -X ours feature  # Prefer current branch
git merge -s recursive -X theirs feature # Prefer incoming changes
```

### Octopus (Multiple Branches)

```bash
# Merge multiple branches at once
git merge feature1 feature2 feature3

# Only works when no conflicts between branches
```

### Squash Merge

```bash
# Combine all commits into single commit
git merge --squash feature-branch
git commit -m "Add feature X (squashed)"

# Good for cleaning up messy branch history before merging
```

## Interactive Merge Tools

### Configure Merge Tool

```bash
# List available tools
git mergetool --tool-help

# Set default merge tool
git config --global merge.tool vscode  # VS Code
git config --global merge.tool meld    # Meld (Linux/macOS)
git config --global merge.tool kdiff3  # KDiff3 (Linux)
git config --global merge.tool p4merge # P4Merge

# Run merge tool for current conflicts
git mergetool
```

### Common Merge Tools

```bash
# VS Code
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Meld (install: sudo apt install meld or brew install meld)
git config --global merge.tool meld
git config --global mergetool.meld.cmd 'meld $BASE $LOCAL $REMOTE -o $MERGED'

# KDiff3 (install: sudo apt install kdiff3)
git config --global merge.tool kdiff3
```

## Advanced Merge Techniques

### Merge Specific Commits (Cherry-Pick)

```bash
# Apply specific commit from another branch
git cherry-pick abc1234

# Cherry-pick multiple commits
git cherry-pick abc1234 def5678

# Cherry-pick range of commits
git cherry-pick feature-branch~3..feature-branch
```

### Merge Base and Diffs

```bash
# Find common ancestor
git merge-base main feature-branch

# Show changes since merge base
git diff $(git merge-base main feature-branch)..feature-branch

# Visualize merge relationship
git log --graph --oneline main feature-branch
```

### Partial Merges

```bash
# Merge specific files only
git checkout feature-branch -- path/to/file.js
# File from feature branch is now in working directory

# Or use git read-tree (advanced)
git read-tree -u -m HEAD feature-branch
```

## Merge vs Rebase Decision Guide

### Use Merge When:
- Merging public/shared branches
- Preserving complete history is important
- Working with team on same branch
- Creating release branches

### Use Rebase When:
- Cleaning up local feature branches before merging
- Wanting linear project history
- Updating feature branch with latest main changes
- No one else is working on the branch

## Common Merge Workflows

### Feature Branch Workflow

```bash
# 1. Update main with latest changes
git switch main
git pull origin main

# 2. Switch to feature and rebase (optional)
git switch feature-login
git rebase main

# 3. Switch back to main and merge
git switch main
git merge --no-ff -m "Merge: Add user login" feature-login

# 4. Push and clean up
git push origin main
git branch -d feature-login
git push origin --delete feature-login
```

### Pull Request Workflow (GitHub/GitLab)

```bash
# 1. Create PR on web interface
# 2. Resolve conflicts locally if needed
git switch feature-branch
git merge main  # Or git rebase main
# Resolve conflicts, commit
git push origin feature-branch

# 3. Merge via web UI or CLI
# GitHub: Settings > Automatic merging
# GitLab: Use MR UI merge button
```

## Best Practices

1. **Merge often** - Frequent small merges reduce conflict complexity
2. **Communicate conflicts** - Tell teammates when you resolve conflicts affecting their work
3. **Use --no-ff for features** - Preserves feature boundaries in history
4. **Test after merge** - Verify merged code works correctly
5. **Document complex merges** - Add notes about why certain decisions were made

## Troubleshooting

### Stuck in Merge State

```bash
# Check merge status
git status

# Abort if problems persist
git merge --abort

# Force clean state (last resort)
git reset --hard HEAD
```

### Accidental Merge

```bash
# Revert merge commit
git revert -m 1 MERGE_COMMIT_HASH

# Or reset to before merge (if not pushed)
git reset --hard HEAD~1
```

### Large Merge Conflicts

```bash
# Use merge tool for complex conflicts
git mergetool

# Or resolve incrementally
git checkout --theirs conflicted-file  # Accept incoming
git checkout --ours conflicted-file    # Keep current
git add conflicted-file
```
