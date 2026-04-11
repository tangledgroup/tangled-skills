# Remote Operations

This reference covers working with remote repositories: clone, fetch, pull, push, and remote management.

## Understanding Remotes

### What is a Remote?

A **remote** is a named reference to a repository hosted elsewhere (typically on a server). Common operations synchronize your local repository with remotes.

### View Remote Configuration

```bash
# List all remotes with URLs
git remote -v

# Example output:
# origin  https://github.com/user/repo.git (fetch)
# origin  https://github.com/user/repo.git (push)
# upstream    https://github.com/original/repo.git (fetch)
# upstream    https://github.com/original/repo.git (push)

# Show detailed remote info
git remote show origin
```

### Remote Output Example

```
* remote origin
  Fetch URL: https://github.com/user/repo.git
  Push  URL: https://github.com/user/repo.git
  HEAD branch: main
  Remote branches:
    develop      tracked by local develop
    main         tracked by local main
    feature/foo  tracked by local feature/foo
  Local branches configured for 'git pull':
    develop merges with remote develop
    main merges with remote main
```

## Adding and Managing Remotes

### Add Remote

```bash
# Add remote named 'origin'
git remote add origin https://github.com/user/repo.git

# Add upstream (original repository)
git remote add upstream https://github.com/original/repo.git

# Add with different fetch/push URLs
git remote add fork git@github.com:fork/repo.git
```

### Remove Remote

```bash
# Remove remote
git remote remove origin

# Or:
git remote rm origin
```

### Rename Remote

```bash
# Rename remote
git remote rename oldname newname
```

### Modify Remote URL

```bash
# Change URL
git remote set-url origin https://github.com/user/new-repo.git

# Change push URL only
git remote set-url --push origin git@github.com:user/repo.git

# Add additional fetch URL
git remote set-url --add origin https://backup.example.com/repo.git
```

## Fetching Updates

### Basic Fetch

```bash
# Fetch from all remotes
git fetch

# Fetch from specific remote
git fetch origin

# Fetch specific branch
git fetch origin main

# Fetch and prune deleted branches
git fetch --prune

# Fetch all tags
git fetch --tags
```

### Fetch Specific References

```bash
# Fetch without updating remote-tracking branches
git fetch origin abc123:my-local-branch

# Fetch only latest commit (shallow)
git fetch --depth 1 origin main

# Fetch with depth for specific branch
git fetch --depth 50 origin feature-branch
```

### Understanding Fetch

```bash
# After fetch, remote branches are in:
origin/main        # Remote tracking branch
origin/develop     # Not automatically checked out

# To view fetched changes without merging:
git log HEAD..origin/main

# To see what will be merged:
git diff HEAD origin/main
```

## Pulling Changes

### Basic Pull

```bash
# Fetch and merge into current branch
git pull

# Pull from specific remote
git pull origin main

# Pull with rebase instead of merge
git pull --rebase

# Make rebase default for pull
git config --global pull.rebase true
```

### Pull Strategies

```bash
# Default: fetch and merge
git pull origin main

# Fetch and rebase
git pull --rebase origin main

# Fetch only (don't merge)
git fetch origin

# Squash remote commits into one
git pull --squash origin main
```

### Pull vs Fetch + Merge

```bash
# These are equivalent:
git pull origin main

git fetch origin
git merge origin/main
```

## Pushing Changes

### Basic Push

```bash
# Push current branch to its upstream
git push

# Push to origin, current branch
git push origin

# Push specific branch
git push origin main

# Push and set upstream (track remote)
git push -u origin main

# Push all branches
git push origin --all
```

### Push Specific References

```bash
# Push tag
git push origin v1.0.0

# Push all tags
git push origin --tags

# Push specific tag only
git push origin --tag v1.0.0

# Delete remote branch
git push origin --delete feature-old

# Or explicitly:
git push origin :feature-old
```

### Force Push (Use Carefully!)

```bash
# Force push (dangerous on shared branches)
git push --force origin main

# Safer: force with lease (fails if remote has new commits)
git push --force-with-lease origin main

# Force push specific branch
git push --force origin feature-rebased
```

### When to Use Force Push

| Scenario | Safe? | Command |
|----------|-------|---------|
| Rewrote local-only branch | ✅ Yes | `git push --force` |
| Rewrote shared branch | ❌ No | Use merge instead |
| Need to overwrite but check first | ⚠️ Maybe | `git push --force-with-lease` |

## Upstream Tracking

### Set Upstream

```bash
# Push and create upstream tracking
git push -u origin main

# Manually set upstream
git branch --set-upstream-to=origin/main main

# Short form:
git branch -u origin/main main

# Switch to branch with upstream
git switch --main --track origin/feature-branch
```

### View Upstream Configuration

```bash
# See which branches track which remotes
git branch -vv

# Example output:
# develop  abc123 [origin/develop] Commit message
# main     def456 [origin/main] Another commit
# feature  fedcba [origin/feature] WIP
```

### Push Current Branch

```bash
# Configure to push current branch by default
git config --global push.current true

# Then just:
git push
```

## Synchronization Patterns

### Keep Local in Sync with Remote

```bash
# Standard workflow
git fetch origin
git merge origin/main

# Or with rebase
git fetch origin
git rebase origin/main

# Or one command
git pull --rebase origin main
```

### Update All Branches

```bash
# Fetch all remotes and prune
git fetch --all --prune

# Rebase all local branches on their upstreams
for branch in $(git branch --list); do
    git checkout $branch
    git rebase origin/$branch
done
git checkout main
```

### Fork Synchronization

```bash
# Add upstream if not already added
git remote add upstream https://github.com/original/repo.git

# Fetch from both
git fetch upstream
git fetch origin

# Update your fork's main
git checkout main
git merge upstream/main
git push origin main

# Update feature branch
git checkout feature-branch
git rebase main
git push origin feature-branch
```

## Authentication

### HTTPS Authentication

```bash
# Browser-based auth (Git 2.30+)
git push
# Opens browser for authentication

# Credential helper (cache in memory for 15 min)
git config --global credential.helper cache

# Credential helper (cache for 1 hour)
git config --global credential.helper 'cache --timeout=3600'

# OS keyring (recommended)
git config --global credential.helper osxkeychain   # macOS
git config --global credential.helper manager-core  # Windows
git config --global credential.helper libsecret     # Linux
```

### SSH Authentication

```bash
# Generate SSH key (if needed)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Test connection
ssh -T git@github.com

# Use SSH URL
git remote set-url origin git@github.com:user/repo.git
```

### Personal Access Tokens (GitHub/GitLab)

For HTTPS with token authentication:

```bash
# Use token in URL (not recommended - exposes in history)
git clone https://<token>@github.com/user/repo.git

# Better: use credential helper
# Token will be cached after first entry

# Or configure directly (less secure)
git config --global credential.helper store
# Then push once to save credentials
```

## Dealing with Divergent Histories

### Remote Has Commits You Don't Have

```bash
# Fetch and see differences
git fetch origin
git log HEAD..origin/main

# Merge remote changes
git merge origin/main

# Or rebase your work on top
git rebase origin/main
```

### You Have Commits Remote Doesn't Have

```bash
# Push your commits
git push origin main

# If branch doesn't exist remotely:
git push -u origin main
```

### Both Sides Have Unique Commits

```bash
# Option 1: Merge (creates merge commit)
git fetch origin
git merge origin/main
git push origin main

# Option 2: Rebase (linear history)
git fetch origin
git rebase origin/main
git push --force-with-lease origin main

# Option 3: Pull with rebase
git pull --rebase origin main
git push origin main
```

## Best Practices

1. **Fetch regularly** - Keep up with remote changes
2. **Use `--force-with-lease`** instead of `--force` when possible
3. **Set upstream tracking** for all branches you push
4. **Pull before pushing** to avoid conflicts
5. **Rebase local branches** before pushing to keep history clean
6. **Never force-push** to shared branches like `main` or `develop`
7. **Use SSH keys** for authentication when possible

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "rejected (fetch first)" | `git fetch` then `git merge` or `git rebase` |
| "non-fast-forward" | Pull first, or use `--force-with-lease` if appropriate |
| Permission denied (SSH) | Check SSH keys: `ssh-add -l`, verify `~/.ssh/config` |
| HTTPS authentication fails | Configure credential helper or use personal access token |
| Remote branch doesn't exist | Push with `-u` to create: `git push -u origin branch-name` |
| Too many files to push | Check for large files, use Git LFS if needed |
