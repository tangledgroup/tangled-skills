# History Manipulation

This reference covers modifying Git history: reset, revert, cherry-pick, reflog, and other history manipulation commands.

## Reset Commands

### Understanding Reset Modes

```bash
# Soft: Keep changes staged
git reset --soft HEAD~1

# Mixed (default): Unstage changes, keep in working directory
git reset HEAD~1

# Hard: Discard all changes (dangerous!)
git reset --hard HEAD~1
```

### Reset Visual Diagram

```
Before: A---B---C (HEAD, main)
        Working dir has changes

After 'reset --soft HEAD~1':
A---B (HEAD, main)
C is staged

After 'reset HEAD~1' (mixed):
A---B (HEAD, main)
C is in working directory (unstaged)

After 'reset --hard HEAD~1':
A---B (HEAD, main)
C is gone!
```

### Common Reset Scenarios

```bash
# Undo last commit, keep changes staged
git reset --soft HEAD~1

# Undo last commit, keep changes unstaged
git reset HEAD~1

# Undo last commit, discard changes
git reset --hard HEAD~1

# Undo last N commits
git reset --hard HEAD~3

# Reset to specific commit
git reset --hard abc123

# Reset branch to match remote (dangerous!)
git reset --hard origin/main
```

### Reset Without Moving Branch

```bash
# Reset index to match commit (unstage files)
git reset abc123

# Reset specific file only
git reset HEAD src/app.js

# With --mixed (default), changes remain in working directory
```

## Revert Commands

### What is Revert?

`git revert` creates a **new commit** that undoes changes from a previous commit. Safe for shared branches.

### Basic Revert

```bash
# Revert last commit
git revert HEAD

# Revert specific commit
git revert abc123

# Revert without auto-commit (edit first)
git revert --no-commit abc123
git commit -m "Custom revert message"

# Revert range of commits
git revert abc123..def456

# Revert merge commit
git revert -m 1 <merge-commit>
```

### Revert vs Reset

| Aspect | Revert | Reset |
|--------|--------|-------|
| Creates new commit | ✅ Yes | ❌ No |
| Rewrites history | ❌ No | ✅ Yes |
| Safe for shared branches | ✅ Yes | ❌ No |
| Can be reverted again | ✅ Yes | N/A |

### When to Use Each

- **Use `revert`**: For public/shared branches, when you need to undo a commit that's already pushed
- **Use `reset`**: For local branches, when you haven't pushed yet or can force-push

## Cherry-Pick

### What is Cherry-Pick?

Apply specific commits from one branch to another without merging the entire branch.

### Basic Cherry-Pick

```bash
# Pick single commit
git cherry-pick abc123

# Pick multiple commits
git cherry-pick abc123 def456 fed789

# Pick range of commits
git cherry-pick abc123..def456

# Pick with edit (amend before applying)
git cherry-pick -n abc123
# Make edits
git commit
```

### Cherry-Pick Options

```bash
# Don't auto-commit (edit first)
git cherry-pick --no-commit abc123

# Use different author
git cherry-pick --author="Name <email>" abc123

# Keep original commit date
git cherry-pick --keep-date abc123

# Stop at merge commits
git cherry-pick --no-stat abc123
```

### Cherry-Pick Conflicts

```bash
# When conflict occurs:
git cherry-pick abc123
# ... resolve conflicts ...
git add <resolved-files>
git cherry-pick --continue

# Skip this commit
git cherry-pick --skip

# Abort cherry-pick
git cherry-pick --abort
```

### Find Commits to Cherry-Pick

```bash
# See which commits are in one branch but not another
git log main..feature-branch --oneline

# Search for specific changes
git log --grep="fix" --oneline feature-branch

# Once you have the hash:
git cherry-pick abc123
```

## Reflog (Reference Log)

### What is Reflog?

The reflog records where `HEAD` and branch references have pointed. It's your **safety net** for recovering lost commits.

### View Reflog

```bash
# Show reflog
git reflog

# Show reflog for specific branch
git reflog show main

# Show reflog in short format
git reflog --date=short

# Limit output
git reflog -5
```

### Reflog Output Example

```
abc123 HEAD@{0}: commit: Add new feature
def456 HEAD@{1}: checkout: moving from feature to main
fed789 HEAD@{2}: commit: WIP on feature
123abc HEAD@{3}: checkout: moving from main to feature
```

### Recover Lost Commits

```bash
# Find lost commit in reflog
git reflog

# Reset to that point
git reset --hard HEAD@{5}

# Or create branch at that point
git branch recovered-branch abc123

# Recover specific commit (not entire state)
git cherry-pick abc123
```

### Reflog Retention

- Default: 90 days for `HEAD`, 90 days for branches
- View expiration: `git config gc.pruneExpire`
- Expired entries are removed by `git gc`

## Amend Commits

### Modify Last Commit

```bash
# Change commit message only
git commit --amend -m "New message"

# Add forgotten files
git add forgotten-file.js
git commit --amend --no-edit

# Change both message and files
git add .
git commit --amend -m "Updated message"

# Open editor for message
git commit --amend
```

### Amend Author

```bash
# Change author of last commit
git commit --amend --author="New Name <new@email.com>"

# Change committer (usually not needed)
git commit --amend --committer="Name <email>"
```

### Amend Multiple Commits

Use interactive rebase:

```bash
# Rebase last 3 commits interactively
git rebase -i HEAD~3

# In editor, change 'pick' to 'edit' for commits to amend
edit abc123 First commit
edit def456 Second commit
pick  fed789 Third commit

# After each edit:
git commit --amend -m "New message"
git rebase --continue
```

## Rewriting History

### Interactive Rebase

```bash
# Rebase last N commits
git rebase -i HEAD~5

# Rebase since specific branch
git rebase -i main

# Available commands:
# pick    - keep commit as-is
# reword  - change commit message
# edit    - stop to amend commit
# squash  - combine with previous commit
# fixup   - combine, discard message
# drop    - remove commit
# reverse - reverse changes
```

### Squash Commits

```bash
# Interactive squash
git rebase -i HEAD~5
# Change 'pick' to 'squash' for commits to combine

# Auto-squash (commits starting with "squash!" or "fixup!")
git rebase -i --autosquash HEAD~5

# Squash all into one commit
git reset --soft HEAD~5
git commit -m "Combined commit message"
```

### Fixup Commits

```bash
# Create fixup commit (will be squashed into previous)
git commit --fixup=abc123

# Or reference HEAD
git commit --fixup HEAD

# Then run interactive rebase with autosquash
git rebase -i --autosquash HEAD~10
```

### Rewrite Commit Messages

```bash
# Interactive rebase, change 'pick' to 'reword'
git rebase -i HEAD~3

# Or use commit-tree (advanced)
NEW_MSG=$(echo "New message")
git commit-tree HEAD^{tree} -p HEAD -m "$NEW_MSG"
```

## Clean Up History

### Remove Sensitive Data

⚠️ **Warning:** Rewriting history requires force-push and coordination with all collaborators.

```bash
# Using BFG Repo-Cleaner (recommended)
java -jar bfg.jar --delete-files secret.key repo.git

# Using git filter-repo (modern replacement for filter-branch)
git filter-repo --path secret.key --invert-path

# Remove file from entire history
git filter-repo --path sensitive-file.txt --invert-path
```

### Change Email in History

```bash
# Replace email address in all commits
git filter-repo --replace-email old@email.com new@email.com

# Or with filter-branch (older method)
git filter-branch --env-filter '
OLD_EMAIL="old@email.com"
NEW_EMAIL="new@email.com"
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
fi
' --tag-name-filter cat -- --all
```

## Safe History Practices

### When NOT to Rewrite History

❌ **Never rewrite:**
- Public/shared branches (`main`, `develop`)
- Branches others are working on
- Tags (use delete and recreate instead)

✅ **Safe to rewrite:**
- Local feature branches
- Your own WIP branches
- Private repositories

### Force Push Safely

```bash
# Always prefer --force-with-lease over --force
git push --force-with-lease origin main

# This fails if remote has commits you don't have
# Prevents accidentally overwriting others' work
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Accidentally ran `reset --hard` | Check `git reflog`, then `git reset --hard HEAD@{n}` |
| Lost branch after rebase | `git reflog` shows all branch positions |
| Rebase in progress | `git rebase --abort` to stop, `--continue` to proceed |
| Cherry-pick conflict | Resolve conflicts, `git add`, then `git cherry-pick --continue` |
| Need to undo revert | `git revert <revert-commit-hash>` |

## Recovery Examples

### Recover Deleted Branch

```bash
# Find branch in reflog
git reflog | grep deleted-branch-name

# Recreate at last known position
git branch deleted-branch abc123
```

### Recover Amended Commit

```bash
# Original commit is still in reflog
git reflog

# Cherry-pick original changes
git cherry-pick HEAD@{5}
```

### Undo Force Push

```bash
# If you force-pushed and need to restore
git fetch origin

# Find the commit before force-push in reflog
git reflog

# Reset to that point
git reset --hard abc123

# Re-push (coordinate with team!)
git push --force-with-lease origin main
```

## Best Practices

1. **Use `reset --soft` first** - Safer, keeps changes staged
2. **Always check reflog** before destructive operations
3. **Prefer `revert` for public branches** - Never rewrites history
4. **Use `--force-with-lease`** instead of `--force` when pushing
5. **Communicate before rewriting shared history**
6. **Keep backups** of important branches before major rewrites
7. **Document rewritten history** in commit messages
