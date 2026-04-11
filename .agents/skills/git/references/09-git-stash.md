# Git Stash

## Understanding Stash

Stash temporarily saves uncommitted changes without creating a commit. Useful for switching branches or pulling updates without committing incomplete work.

```bash
# Working directory changes  --(stash)-->  Stash stack
# Later:                     --(pop/apply)-->  Back to working directory
```

## Basic Stash Operations

### Save Changes (Stash Push)

```bash
# Stash current changes with default message
git stash

# Stash with descriptive message
git stash push -m "WIP: implementing user authentication"

# Stash specific files only
git stash push -m "partial work" src/auth.js src/utils.js

# Include untracked files too
git stash push -u -m "all changes including new files"

# Keep index (staged files stay staged after pop)
git stash push -k -m "preserve staging"
```

### View Stashed Changes

```bash
# List all stashes
git stash list

# Output example:
# stash@{0}: WIP: implementing user authentication
# stash@{1}: WIP on main: abc1234 - previous work
# stash@{2}: On feature: def5678 - older changes

# See diff for specific stash
git stash show stash@{0}

# Show with patch
git stash show -p stash@{0}
```

### Apply Stashed Changes

```bash
# Apply most recent stash (keep in list)
git stash apply

# Apply specific stash
git stash apply stash@{2}

# Apply and remove from list
git stash pop

# Pop specific stash
git stash pop stash@{1}
```

### Drop (Delete) Stashes

```bash
# Drop most recent stash
git stash drop

# Drop specific stash
git stash drop stash@{2}

# Drop all stashes
git stash clear

# Drop range (keep only latest)
git stash branch old-stashes stash@{10}
git stash clear
```

## Stash Workflows

### Switch Branches Without Committing

```bash
# 1. Save work in progress
git stash push -m "incomplete feature work"

# 2. Switch to other branch
git switch main

# 3. Do urgent work, commit

# 4. Return to feature branch
git switch feature-branch

# 5. Restore stashed changes
git stash pop
```

### Pull Updates Without Conflicts

```bash
# 1. Stash local changes
git stash push -m "local modifications"

# 2. Pull latest from remote
git pull origin main

# 3. Apply your changes back
git stash pop

# 4. Resolve any conflicts that arise
```

### Work on Multiple Things Simultaneously

```bash
# Stash different work items separately
git stash push -m "bugfix: login issue" src/login.js
git stash push -m "feature: new dashboard" src/dashboard/
git stash push -m "refactor: utils cleanup" src/utils.js

# List and apply as needed
git stash list
git stash apply stash@{1}  # Work on dashboard
```

## Advanced Stash Operations

### Create Branch from Stash

```bash
# Create new branch with stashed changes
git stash branch new-feature stash@{0}

# This:
# - Applies the stash
# - Creates and switches to new branch
# - Drops the stash from list

# Continue work on the branch
git switch new-feature
git status  # Changes are now in working directory
```

### Store Stash as Commit

```bash
# View stash as commit (stashes have commit hashes)
git stash show -p stash@{0} | head -20

# Get stash commit hash
git stash list  # Shows stash@{n}: message

# Cherry-pick stash changes
git stash show -p stash@{0} | git apply

# Or use stash's internal commit
git stash reflog  # Shows internal structure
```

### Stash Clean Working Directory

```bash
# Save everything and start fresh
git add -A
git stash push -m "save all work"

# Now working directory is clean
git status  # Should show clean state

# Later restore:
git stash pop
```

## Stash with Untracked Files

### Default Behavior

```bash
# By default, untracked files are NOT stashed
git add new-file.js
git stash push
# new-file.js remains in working directory!
```

### Include Untracked Files

```bash
# Stash tracked and untracked files
git stash push -u

# Or include ALL files (even ignored)
git stash push -a  # Includes .gitignore'd files too

# With message
git stash push -u -m "complete snapshot"
```

### Partial Stash of Untracked

```bash
# Only stash specific untracked files
git stash push -u new-file.js another-untracked.txt
```

## Stash Inspection and Management

### See What's in Each Stash

```bash
# List with timestamps
git stash list

# Show file list (no diff)
git stash show stash@{0}

# Show full diff
git stash show -p stash@{0}

# Compare two stashes
git stash show -p stash@{0} stash@{1}
```

### Rename Stash Message

```bash
# Git doesn't support renaming, but you can:
# 1. Apply to branch
git stash branch temp-branch stash@{0}

# 2. Commit with proper message
git add .
git commit -m "Properly described changes"

# 3. Drop old stash
git stash drop stash@{0}
```

### Clean Up Old Stashes

```bash
# Find old stashes
git stash list

# Drop individually
git stash drop stash@{5}

# Or create branch for important ones, then clear
git stash branch save-important stash@{3}
git stash clear
```

## Common Stash Patterns

### Save Multiple WIP States

```bash
# Before starting new task
git stash push -m "before hotfix" 

# Work on hotfix, commit

# After hotfix, restore previous work
git stash pop

# If conflicts, resolve then continue
```

### Experiment Safely

```bash
# Save current state
git stash push -m "stable point"

# Make experimental changes
# ... hack around ...

# If experiment fails:
git stash drop  # Discard experiment
git stash pop   # Restore stable point

# If experiment succeeds:
git add .
git commit -m "Successful experiment"
git stash drop  # Remove save point
```

### Collaborative Stash (Not Recommended)

```bash
# WARNING: Stash is local-only!
# Each machine has separate stash list

# To share work, use branch instead:
git switch -c shared-work
git add . && git commit -m "WIP"
git push -u origin shared-work
```

## Troubleshooting

### Conflicts When Applying Stash

```bash
# 1. Stash apply fails with conflicts
git stash apply
# CONFLICT (content): Merge conflict in file.js

# 2. Resolve conflicts manually
# Edit conflicted files, remove markers

# 3. Mark as resolved
git add file.js

# 4. Complete the apply
git stash pop  # Or let it complete automatically

# If problems persist:
git stash drop  # Discard this apply attempt
```

### Stash Lost After Reset

```bash
# Stashes survive most operations, but check reflog:
git stash list  # Should still show stashes

# If truly lost, check if you created branch from it
git branch -a | grep stash

# Otherwise, stashes are local and can be lost on:
# - git clone (new clone has no stashes)
# - Manual .git manipulation
```

### Can't Stash (Clean Working Directory)

```bash
# Git won't stash if nothing to save
git status  # Check for changes

# If clean, nothing to stash
# Make some changes first, then:
git stash push -m "description"
```

### Too Many Stashes

```bash
# List all stashes
git stash list

# Review and drop old ones
git stash show stash@{10}  # Check what it is
git stash drop stash@{10}  # If not needed

# Or create branches for important ones
git stash branch feature-from-stash stash@{5}

# Clear the rest
git stash clear
```

## Best Practices

1. **Use descriptive messages** - `stash push -m "what and why"`
2. **Drop stashes regularly** - Don't let them accumulate
3. **Prefer commits for long-term saves** - Stash is temporary
4. **Include untracked files explicitly** - Use `-u` flag
5. **Create branches from important stashes** - More permanent

## Command Cheat Sheet

```bash
# Save changes
git stash push -m "message"          # Save with message
git stash push -u                    # Include untracked files
git stash                            # Quick save (default message)

# View stashes
git stash list                       # List all stashes
git stash show -p stash@{0}          # Show diff

# Restore changes
git stash pop                        # Apply and remove latest
git stash apply stash@{1}            # Apply specific (keep in list)
git stash drop stash@{2}             # Delete specific

# Cleanup
git stash clear                      # Remove all stashes
git stash branch new-branch stash@{0}  # Create branch from stash
```

## Limitations

- **Local only** - Stashes don't push/pull with remotes
- **Not for collaboration** - Use branches to share work
- **Can be lost** - On clone, fresh checkout, or manual cleanup
- **One stack per repo** - Each repository has its own stash list
