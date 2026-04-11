# Git Rebase

## Understanding Rebase

Rebase rewrites commit history by moving commits to a new base, creating a linear history.

```
Before rebase:
  main ──A──B──C──D
           \
            feature ──F1──F2──F3

After rebase feature onto main:
  main ──A──B──C──D──F1'──F2'──F3' (feature)
```

## Basic Rebase Operations

### Rebase Current Branch

```bash
# Rebase current branch onto main
git switch feature-branch
git rebase main

# Alternative: rebase while on main
git rebase main feature-branch
```

### Rebase Specific Range

```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# Rebase commits after tag onto new base
git rebase v1.0.0..feature-branch main

# Rebase specific commit range
git rebase --onto main v1.0 feature
```

## Interactive Rebase

### Start Interactive Rebase

```bash
# Last 5 commits
git rebase -i HEAD~5

# Since specific commit
git rebase -i abc1234^

# All commits since branch point
git rebase -i main
```

### Available Commands

Editor opens with list of commits:

```
pick abc1234 Add user model
pick def5678 Create database schema
pick 789abcd Add authentication logic

# Commands (first letter is enough):
pick     = Keep commit as-is
reword/r = Change commit message
edit/e   = Stop to modify commit contents
squash/s = Merge with previous commit
fixup/f  = Merge with previous (discard message)
drop/d   = Remove commit
```

### Common Interactive Rebase Operations

#### Squash Commits

```bash
# Before:
pick abc1234 Add user model
pick def5678 Add email field
pick 789abcd Add password hashing

# After changing to squash:
pick abc1234 Add user model
squash def5678 Add email field
squash 789abcd Add password hashing

# Result: Single commit with combined changes
```

#### Reorder Commits

```bash
# Before:
pick abc1234 Fix bug in auth
pick def5678 Add auth feature

# After reordering:
pick def5678 Add auth feature
pick abc1234 Fix bug in auth

# Result: Logical order (feature before fix)
```

#### Edit Commit Content

```bash
# Mark commit for editing
pick abc1234 Original message
edit def5678 Stop here to modify

# After stopping:
git status  # Shows "interactive rebase in progress"
# Make changes, then:
git add .
git commit --amend
git rebase --continue
```

#### Split Commit

```bash
# Start interactive rebase
git rebase -i HEAD~1

# Mark for edit
edit abc1234 Large commit to split

# After stopping:
git reset HEAD~1  # Unstage all changes

# Stage and commit in smaller pieces
git add part1.js
git commit -m "Add part 1"
git add part2.js
git commit -m "Add part 2"

# Continue rebase with new commits
git rebase --continue
```

## Rebase vs Merge Comparison

### When to Use Rebase

- Cleaning up local feature branches before merging
- Updating feature branch with latest main changes
- Wanting linear project history
- No one else is working on the branch

### When to Use Merge

- Integrating public/shared branches
- Preserving complete historical record
- Creating release points
- Multiple people working on same branch

## Advanced Rebase Techniques

### Rebase Onto Different Branch

```bash
# Move feature from old-base to new-base
git rebase --onto new-base old-base feature

# Example: Move bugfix from v1.0 to main
git rebase --onto main v1.0 bugfix-branch
```

### Skip Commits During Rebase

```bash
# In interactive mode, delete lines for commits to skip
# Or use:
git rebase --skip  # Skip current commit during conflict resolution
```

### Abort and Continue

```bash
# Stop rebase and return to original state
git rebase --abort

# After resolving conflicts:
git add <resolved-files>
git rebase --continue

# Auto-skip conflicted commit
git rebase --skip
```

## Resolving Rebase Conflicts

### Conflict Resolution Process

```bash
# 1. Git stops at first conflict
git rebase main
# Rebasing (3/10)...
# CONFLICT (content): Merge conflict in file.js

# 2. Resolve conflicts in files
# Edit conflicted files, remove markers

# 3. Stage resolved files
git add file.js

# 4. Continue rebase
git rebase --continue

# Repeat for each conflicting commit
```

### Automated Conflict Resolution

```bash
# Always prefer our version during rebase
git config --local merge.ours.driver true
git rebase main

# Or use rerere (reuse recorded resolution)
git config --global rerere.enabled true
# Git remembers how you resolved conflicts and applies automatically next time
```

## Rewriting History Safely

### Safe Scenarios (Rewrite OK)

- Local branches not shared with others
- Your own feature branches before PR/merge
- Private repositories

### Unsafe Scenarios (Don't Rewrite)

- Public/shared branches (`main`, `master`)
- Branches others are working on
- Published release tags

### Force Push After Rebase

```bash
# DANGEROUS: Overwrites remote history
git push --force

# SAFER: Fails if remote has new commits
git push --force-with-lease

# Recommended for rebased feature branches
git push --force-with-lease origin feature-branch
```

## Common Rebase Workflows

### Clean Up Feature Branch Before Merging

```bash
# 1. Start interactive rebase
git switch feature-login
git rebase -i main

# 2. Squash related commits, reorder, fix messages
# Edit the list in your editor

# 3. Complete rebase
# Resolve any conflicts that arise

# 4. Force push updated branch
git push --force-with-lease origin feature-login
```

### Update Feature Branch with Latest Main

```bash
# Method 1: Rebase (linear history)
git switch feature-branch
git rebase main

# Method 2: Merge (preserves history)
git merge main

# Method 3: Fetch and rebase
git fetch origin
git rebase origin/main
```

### Backport Fix to Older Version

```bash
# 1. Create branch from old version tag
git switch -c backport-fix v1.0.0

# 2. Cherry-pick the fix commit
git cherry-pick abc1234

# 3. Test and push
git push origin backport-fix
```

## Best Practices

1. **Rebase local branches only** - Never rebase shared/public branches
2. **Use --force-with-lease** - Safer than --force for pushing rebased branches
3. **Enable rerere** - Saves conflict resolutions for future use
4. **Keep rebases small** - Rebase 5-10 commits, not 50
5. **Communicate with team** - Let others know before rebasing shared work

## Troubleshooting

### Stuck in Rebase

```bash
# Check rebase status
git status
git log --oneline -5

# Abort and start over
git rebase --abort

# If abort doesn't work (rare)
cat .git/rebase-merge/head-name  # Find target
git reset --hard $(cat .git/rebase-merge/head-name)
rm -rf .git/rebase-*
```

### Lost Commits After Rebase

```bash
# Find lost commits in reflog
git reflog

# Create branch at lost commit
git switch -c recovered abc1234

# Or cherry-pick the commits
git cherry-pick abc1234
```

### Rebase Created Duplicate Commits

```bash
# Check for duplicates
git log --graph --oneline --all

# Use reflog to find original state
git reflog

# Reset to before problematic rebase
git reset --hard HEAD@{1}
```
