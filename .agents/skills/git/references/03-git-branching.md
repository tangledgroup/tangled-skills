# Git Branching

## Understanding Branches

A branch is a movable pointer to a commit. The default branch is typically `main` or `master`.

```
Branch structure:
  main ──C1──C2──C3* (current HEAD)
           \
            feature ──F1──F2* (current HEAD when on feature)
```

## Listing Branches

```bash
# List local branches (* = current)
git branch

# List all branches (local and remote)
git branch -a

# Show which commits each branch points to
git branch -v

# Show upstream tracking info
git branch -vv

# List branches with commit count from common ancestor
git branch --contains HEAD
```

## Creating Branches

### Create Without Switching

```bash
# Create new branch from current commit
git branch feature-login

# Create branch from specific commit
git branch hotfix-123 abc1234

# Create branch from tag
git branch release-v1.0 v1.0.0
```

### Create and Switch (Recommended)

```bash
# Create new branch and switch to it
git switch -c feature-login

# Alternative (older Git versions)
git checkout -b feature-login

# Create from specific commit and switch
git switch -c hotfix abc1234
```

## Switching Branches

```bash
# Switch to existing branch
git switch main

# Alternative (older Git)
git checkout main

# Switch with force (discards uncommitted changes)
git switch --discard-changes feature

# List recent branches for quick switching
git reflog show HEAD
```

### Handle Uncommitted Changes When Switching

```bash
# Option 1: Commit changes first
git add .
git commit -m "WIP before switching"
git switch other-branch

# Option 2: Stash changes temporarily
git stash push -m "work in progress"
git switch other-branch
git stash pop

# Option 3: Force switch (loses changes!)
git switch --discard-changes other-branch
```

## Branch Operations

### Delete Branches

```bash
# Delete merged branch (safe)
git branch -d feature-completed

# Force delete unmerged branch (dangerous!)
git branch -D feature-incomplete

# Delete multiple branches
git branch -d feature1 feature2 feature3

# Delete remote branch
git push origin --delete feature-branch
```

### Rename Branches

```bash
# Rename current branch
git branch -m new-name

# Rename specific branch
git branch -m old-name new-name

# Rename and update remote tracking
git branch -m main master
git push origin -u master
git push origin --delete main
```

### Merge Branches into Current

```bash
# See which branches are merged into current
git branch --merged

# See which branches have unique commits
git branch --no-merged
```

## Working with Remote Branches

### List Remote Branches

```bash
# List remote-tracking branches
git branch -r

# List all branches (local and remote)
git branch -a

# Show remote configuration
git remote -v
```

### Track Remote Branches

```bash
# Create local branch tracking remote
git switch -c feature --track origin/feature

# Alternative syntax
git checkout -b feature origin/feature

# Set upstream for existing branch
git switch feature
git push -u origin feature
```

### Fetch and Update Remote Tracking

```bash
# Fetch all remotes
git fetch --all

# Prune deleted remote branches
git fetch --prune

# Update local tracking branches
git fetch origin
```

## Branch Naming Conventions

### Common Patterns

```bash
# Feature branches
feature/user-authentication
feature/add-search-functionality

# Bug fixes
bugfix/login-crash
hotfix/security-patch

# Release branches
release/v1.0.0
release/candidate-2.1

# Experiment branches
experiment/new-ui
wip/refactoring
```

### Scoped Naming (Team/Component)

```bash
# Team-based
backend/api-improvements
frontend/dashboard-redesign
devops/deployment-pipeline

# Component-based
feat/auth-module
fix/payment-processing
chore/dependency-updates
```

## Branch Protection Strategies

### Local Protection

```bash
# Never delete main/master
git config branch.main.protected true

# Create backup branches before major changes
git branch backup-before-major-change
```

### Remote Protection (GitHub/GitLab)

Configure on hosting platform:
- Require pull requests before merging
- Require status checks to pass
- Require review approvals
- Prevent force pushes
- Require linear history (no merge commits)

## Common Branching Workflows

### Simple Workflow

```bash
# 1. Create feature branch
git switch -c feature/my-feature

# 2. Make changes and commit
git add . && git commit -m "Add feature"

# 3. Push to remote
git push -u origin feature/my-feature

# 4. Switch back to main
git switch main

# 5. Update main with latest changes
git pull origin main

# 6. Merge feature branch
git merge feature/my-feature

# 7. Push main and delete feature branch
git push origin main
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

### Fork-Based Workflow (GitHub)

```bash
# 1. Clone your fork
git clone https://github.com/your-username/repo.git
cd repo

# 2. Add upstream remote
git remote add upstream https://github.com/original-owner/repo.git

# 3. Keep in sync
git fetch upstream
git switch main
git merge upstream/main

# 4. Create feature branch
git switch -c feature/my-feature

# 5. Push to your fork
git push -u origin feature/my-feature

# 6. Create pull request on GitHub
```

## Best Practices

1. **One feature per branch** - Keeps changes isolated and reviewable
2. **Descriptive names** - `feature/user-authentication` not `feat-123`
3. **Delete merged branches** - Clean up after merging
4. **Rebase before merging** - Keep history linear (for feature branches)
5. **Update main frequently** - Avoid large merge conflicts
6. **Use branch protection** - Prevent accidental pushes to protected branches

## Troubleshooting

### Lost Work After Switching

```bash
# Find lost commits in reflog
git reflog

# Recover specific commit
git switch -c recovered-branch abc1234
```

### Can't Delete Branch (Merge Conflicts)

```bash
# Force delete (if you're sure)
git branch -D stubborn-branch

# Or merge first then delete
git merge stubborn-branch
git branch -d stubborn-branch
```

### Remote Branch Shows as Deleted Locally

```bash
# Prune stale remote-tracking branches
git fetch --prune

# Manually delete stale reference
git update-ref -d refs/remotes/origin/deleted-branch
```
