# Git Remote Operations

## Understanding Remotes

A remote is a reference to a repository on another machine (or different location).

```bash
# List configured remotes
git remote -v

# Typical output:
origin  https://github.com/user/repo.git (fetch)
origin  https://github.com/user/repo.git (push)
upstream  https://github.com/original/repo.git (fetch)
upstream  https://original/repo.git (push)
```

## Adding and Managing Remotes

### Add Remote

```bash
# Add remote with name
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git

# Add with SSH URL
git remote add origin git@github.com:user/repo.git

# Add read-only remote
git remote add mirror https://github.com/readonly/repo.git
```

### View Remote Configuration

```bash
# List all remotes with URLs
git remote -v

# Show detailed configuration
git config --get-all remote.origin.url
git config --get-all remote.origin.fetch
```

### Rename Remote

```bash
# Rename remote
git remote rename origin upstream

# Update references in tracking branches
git branch --list --format='%(refname:short)' | grep origin/
```

### Remove Remote

```bash
# Remove remote reference
git remote remove origin

# Also delete remote-tracking branches
git for-each-ref --format='delete %(refname)' refs/remotes/origin/ | git update-ref --stdin
```

## Fetching from Remotes

### Basic Fetch

```bash
# Fetch all remotes
git fetch

# Fetch specific remote
git fetch origin

# Fetch specific branch
git fetch origin main

# Fetch with pruning (remove deleted branches)
git fetch --prune
```

### Fetch Options

```bash
# Fetch all tags too
git fetch --tags

# Fetch without merging (default behavior)
git fetch origin

# Dry run (see what would be fetched)
git fetch --dry-run origin

# Force fetch even if not fast-forward
git fetch --force origin
```

### Understanding Remote Tracking Branches

```bash
# After fetch, remote branches are stored locally as:
refs/remotes/origin/main
refs/remotes/origin/feature-branch

# View all remote-tracking branches
git branch -r

# Compare local and remote branches
git switch main
git log main..origin/main --oneline  # Commits on remote not in local
```

## Pulling Changes

### Basic Pull

```bash
# Fetch and merge into current branch
git pull origin main

# Default: fetch from tracking remote and merge
git pull

# Show what will be pulled without doing it
git pull --dry-run
```

### Pull with Rebase (Recommended)

```bash
# Fetch and rebase instead of merge
git pull --rebase

# Configure globally
git config --global pull.rebase true

# Benefits: Linear history, cleaner commit graph
```

### Pull Specific Branch

```bash
# Pull specific branch into current
git pull origin feature-branch

# Pull and create new local branch
git pull origin main:my-main-branch
```

## Pushing Changes

### Basic Push

```bash
# Push current branch to tracking remote
git push

# Push to specific remote and branch
git push origin feature-branch

# Push all branches
git push --all origin

# Push all tags
git push --tags origin
```

### Set Up Tracking

```bash
# Push and set upstream tracking
git push -u origin feature-branch

# After setup, simple commands work:
git push    # Pushes to tracked remote/branch
git pull    # Pulls from tracked remote/branch

# Check tracking configuration
git branch -vv
```

### Push Multiple Branches

```bash
# Push multiple branches at once
git push origin main develop feature-1

# Push with refspec (advanced)
git push origin refs/heads/feature:refs/heads/experimental
```

## Force Pushing (Use Carefully!)

### Regular Force Push

```bash
# DANGEROUS: Overwrites remote history
git push --force origin main

# Can lose others' work if they pushed after you
```

### Safer Force Push (Recommended)

```bash
# Fails if remote has new commits you don't have
git push --force-with-lease origin feature-branch

# Safe for rebased branches you own
# Still protects against accidental overwrites
```

### When to Force Push

✅ Safe:
- Your own feature branches
- After interactive rebase of local work
- Fixing mistakes before anyone else pulls

❌ Never:
- Shared branches (`main`, `master`)
- Branches others are working on
- Public repository branches

## Remote Workflows

### Fork-Based Workflow (GitHub/GitLab)

```bash
# 1. Clone your fork
git clone https://github.com/your-user/repo.git
cd repo

# 2. Add upstream remote
git remote add upstream https://github.com/original/repo.git
git remote -v  # Verify both remotes exist

# 3. Create feature branch
git switch -c feature-branch

# 4. Make changes and push to your fork
git add . && git commit -m "Add feature"
git push -u origin feature-branch

# 5. Keep in sync with upstream
git fetch upstream
git rebase upstream/main

# 6. Create pull request on web interface
```

### Shared Repository Workflow

```bash
# 1. Clone shared repository
git clone git@server.com:team/shared-repo.git
cd shared-repo

# 2. Create feature branch
git switch -c feature-branch

# 3. Work and commit
git add . && git commit -m "Implement feature"

# 4. Fetch latest changes before pushing
git fetch origin
git rebase origin/main

# 5. Push for review
git push -u origin feature-branch

# 6. After review, merge into main
git switch main
git pull origin main
git merge feature-branch
git push origin main
```

## Configuring Remote Defaults

### Set Default Remote

```bash
# Push to specific remote by default
git config --global push.default current

# Options:
# current  = Push current branch to remote with same name
# upstream = Push to upstream tracking branch
# matching = Push all branches with matching names
```

### Configure Fetch Behavior

```bash
# Fetch all refs by default
git config --global fetch.prune false

# Download tags automatically
git config --remote.*.fetch '+refs/tags/*:refs/tags/*'
```

## SSH vs HTTPS Authentication

### SSH Setup

```bash
# Generate SSH key (if needed)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Test connection
ssh -T git@github.com

# Use SSH URL for remote
git remote set-url origin git@github.com:user/repo.git
```

### HTTPS with Credential Helper

```bash
# Cache credentials for 15 minutes
git config --global credential.helper cache

# Store permanently (not recommended for shared machines)
git config --global credential.helper store

# Use OS keychain (macOS)
git config --global credential.helper osxkeychain

# Use OS keychain (Windows)
git config --global credential.helper wincred
```

## Best Practices

1. **Use descriptive remote names** - `origin`, `upstream`, `fork`
2. **Fetch before pushing** - Avoid conflicts with `git fetch` first
3. **Prefer --force-with-lease** - Safer than --force
4. **Set upstream tracking** - Use `-u` flag when pushing new branches
5. **Pull with rebase** - Keep history linear with `git pull --rebase`

## Troubleshooting

### Remote: Repository Not Found

```bash
# Check remote URL
git remote -v

# Update if changed
git remote set-url origin https://new-url/repo.git

# Test connection
git ls-remote origin
```

### Push Rejected (Not Fast-Forward)

```bash
# Someone else pushed first - fetch and integrate
git fetch origin
git rebase origin/main  # Or git merge origin/main
git push
```

### Permission Denied

```bash
# Check authentication method
git remote -v  # SSH vs HTTPS

# For HTTPS, credentials may be needed
# For SSH, ensure key is added to ssh-agent:
ssh-add ~/.ssh/id_rsa

# Verify SSH key on GitHub/GitLab settings
```
