# Git Troubleshooting

## Common Issues and Solutions

### Merge Conflicts

#### Problem
```
Auto-merging file.js
CONFLICT (content): Merge conflict in file.js
Automatic merge failed; fix conflicts and then commit the result.
```

#### Solution
```bash
# 1. View conflicted files
git status

# 2. Open conflicted file, look for markers:
<<<<<<< HEAD
your changes
=======
incoming changes
>>>>>>> branch-name

# 3. Edit file to resolve (keep what you want, remove markers)

# 4. Stage resolved files
git add file.js

# 5. Complete merge
git commit

# Or abort entirely
git merge --abort
```

#### Prevention
```bash
# Rebase frequently to catch conflicts early
git fetch
git rebase origin/main

# Use merge tools for complex conflicts
git mergetool
```

---

### Lost Commits After Reset

#### Problem
Accidentally ran `git reset --hard` and lost work.

#### Solution
```bash
# 1. Check reflog (saves last 90 days of HEAD positions)
git reflog

# 2. Find commit before disaster
# abc1234... Work before reset  (1 hour ago)
# def5678... After reset       (0 hours ago)

# 3. Recover with new branch
git switch -c recovered-branch abc1234

# Or reset current branch
git reset --hard abc1234
```

---

### Wrong Email on Commits

#### Problem
Commits made with wrong email address.

#### Solution (Future Commits)
```bash
git config --global user.email "correct@email.com"
```

#### Solution (Past Commits - Local Only)
```bash
# Change author for last commit
git commit --amend --author="Name <correct@email.com>"

# Change multiple commits
git rebase -i HEAD~n
# Change 'pick' to 'edit' for each commit to fix
# At each stop:
git commit --amend --author="Name <correct@email.com>"
git rebase --continue

# Or use filter-branch (affects all history)
git filter-branch --env-filter '
OLD_EMAIL="wrong@email.com"
NEW_EMAIL="correct@email.com"
if [ "$COMMIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]; then
    export AUTHOR_EMAIL="$NEW_EMAIL"
fi
' HEAD
```

---

### Large File Accidentally Committed

#### Problem
Committed large binary file or sensitive data.

#### Solution (Remove from History)
```bash
# Option 1: BFG Repo-Cleaner (fast, recommended)
# Download from: https://github.com/rtyley/bfg-repo-cleaner
java -jar bfg.jar --delete-files largefile.bin .

# Option 2: git filter-branch (built-in, slower)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch largefile.bin' \
  --prune-empty --tag-name-filter cat -- --all

# Option 3: git filter-repo (modern replacement)
git filter-repo --path largefile.bin --invert-path

# After cleaning, force push
git push origin --force --all
git push origin --force --tags
```

#### Prevent Future Issues
```bash
# Add to .gitignore
echo "largefile.bin" >> .gitignore

# Or use Git LFS for large files
git lfs install
git lfs track "*.bin"
```

---

### Change Commit Message

#### Problem
Typo or unclear message in commit.

#### Solution (Last Commit)
```bash
git commit --amend -m "Correct commit message"
```

#### Solution (Older Commit)
```bash
# Interactive rebase
git rebase -i HEAD~5

# Change 'pick' to 'reword' for target commit
# Edit message when prompted

# Or use reword
git rebase -i --abort  # If mistakes made
```

---

### Split Large Commit

#### Problem
Commit has too many unrelated changes.

#### Solution
```bash
# 1. Reset to unstage changes
git reset HEAD~1  # For last commit

# 2. Stage changes in logical groups
git add -p  # Interactive hunk selection
git commit -m "First logical change"

git add remaining-files.js
git commit -m "Second logical change"
```

---

### Combine Multiple Commits

#### Problem
Too many small commits for one feature.

#### Solution (Last N Commits)
```bash
# Interactive rebase
git rebase -i HEAD~5

# Change 'pick' to 'squash' or 's' for commits to combine:
pick abc1234 Initial commit
squash def5678 Add more
squash 789abc Final tweaks

# Edit combined message when prompted
```

---

### Untracked Files Won't Delete

#### Problem
Files show as untracked but can't be removed.

#### Solution
```bash
# Check if actually ignored
git check-ignore -v filename

# Force remove from index if stuck
git rm --cached filename

# Or clean untracked files
git clean -fd  # Dry run first
git clean -fd  # Actually delete
```

---

### Remote Branch Shows as Deleted Locally

#### Problem
Remote branch deleted but still shows locally.

#### Solution
```bash
# Fetch and prune
git fetch --prune

# Or manually delete stale reference
git update-ref -d refs/remotes/origin/deleted-branch

# Clean local tracking branches
git remote prune origin
```

---

### Permission Denied on Push

#### Problem
```
remote: Permission to repository denied
fatal: unable to access repository
```

#### Solution (HTTPS)
```bash
# Check credentials
git remote -v

# Remove cached credentials
git config --global --unset credential.helper

# Re-authenticate on next push
git push

# Set up credential helper
git config --global credential.helper store
```

#### Solution (SSH)
```bash
# Check SSH key
ssh -T git@github.com

# Add key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# Verify remote uses SSH
git remote -v
git remote set-url origin git@github.com:user/repo.git
```

---

### Push Rejected (Not Fast-Forward)

#### Problem
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs
```

#### Solution
```bash
# Someone else pushed first - integrate their changes
git fetch origin

# Option 1: Merge their changes
git merge origin/main
git push

# Option 2: Rebase on top (cleaner history)
git rebase origin/main
git push

# Option 3: Force (DANGEROUS - only if you're sure)
git push --force-with-lease
```

---

### Detached HEAD State

#### Problem
```
HEAD is now at abc1234... Commit message
```

#### Understanding
You checked out a tag or commit directly, not a branch.

#### Solution (Make Changes)
```bash
# Create new branch from current position
git switch -c new-branch

# Now make changes and commit normally
```

#### Solution (Just Viewing)
```bash
# Return to main branch when done viewing
git switch main
```

---

### Wrong Branch for Commit

#### Problem
Committed to main instead of feature branch.

#### Solution (Not Pushed Yet)
```bash
# 1. Create/switch to correct branch
git switch -c feature-branch

# 2. Move the commit
git switch main
git reset --soft HEAD~1  # Undo commit, keep changes staged

# 3. Switch and re-commit
git switch feature-branch
git commit -m "Original message"

# 4. Push to correct branch
git push -u origin feature-branch
```

---

### Repository Corrupted

#### Problem
```
fatal: corrupt object file
fatal: pack has href hash collision
```

#### Solution
```bash
# Check repository integrity
git fsck --full

# Try to recover
git fsck --full --force

# If backup exists, restore from it
# Or reclone and merge local changes:
git clone url temp-repo
cp -r .git/objects temp-repo/.git/objects/
```

---

### Reflog Shows Missing Commits

#### Problem
Commits disappeared after operation.

#### Solution
```bash
# Find in reflog
git reflog show HEAD

# Create branch at lost commit
git switch -c recovery abc1234

# Cherry-pick if needed elsewhere
git cherry-pick abc1234
```

---

## Debugging Commands

### Repository Health

```bash
# Check for corruption
git fsck --full

# Count objects
git count-objects -v

# See reflog
git reflog

# List all references
git show-ref
```

### Understand Current State

```bash
# What branch am I on?
git branch

# What's the current HEAD?
git rev-parse HEAD

# What remote am I tracking?
git branch -vv

# What changes are staged/unstaged?
git status

# What's in the index?
git diff --cached
```

### Find Specific Commits

```bash
# Search by message
git log --grep="keyword" --all

# Search by author
git log --author="name" --all

# Find commit that introduced change
git log -S "function_name" --all

# Bisect to find bug introduction
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Test and mark commits good/bad
git bisect reset
```

### Compare States

```bash
# What's different from remote?
git fetch
git log main..origin/main --oneline

# What's staged vs unstaged?
git diff          # Unstaged
git diff --staged # Staged

# What changed between tags?
git diff v1.0.0..v1.1.0 --stat
```

## Prevention Best Practices

### Regular Maintenance

```bash
# Weekly: Fetch and prune
git fetch --prune

# Monthly: Garbage collect
git gc --prune=now

# Before major operations: Create backup branch
git switch -c backup-$(date +%Y%m%d)
```

### Safe Operations Checklist

Before running destructive commands:
1. ✅ `git status` - Know current state
2. ✅ `git reflog` - Can recover if needed
3. ✅ `git branch -a` - See all branches
4. ✅ Create backup branch for safety
5. ✅ Test on feature branch first

### Essential Aliases

```bash
# Add to ~/.gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    df = diff
    last = log -1 HEAD
    unpushed = "log --pretty=format:%h %s -- remotes/origin/$(git branch --show-current)"
    newer-than = "!f() { git log --since=\"$1\"; }; f"
```

## Emergency Recovery Flowchart

```
Problem occurred
    ↓
git status  # What's the state?
    ↓
git reflog  # Can we find lost work?
    ↓
Yes → Create branch at good commit
    ↓
No → Check remote: git fetch && git log origin/main
    ↓
Still lost? → Contact team, check CI/CD logs
    ↓
Recover → Document what happened, prevent recurrence
```

## When to Ask for Help

- Repository corruption you can't fix with `git fsck`
- Lost critical data not in reflog
- Complex history rewrite affecting multiple people
- Permission issues on shared repositories
- Unsure about force operations on shared branches

## Useful Resources

- **Git documentation**: `git help <command>` or https://git-scm.com/docs
- **Pro Git book**: Free at https://git-scm.com/book
- **Git Tower blog**: Practical tips and tutorials
- **GitHub Guides**: Workflow-specific guidance
- **Stack Overflow**: Search "[git]" tag for specific issues
