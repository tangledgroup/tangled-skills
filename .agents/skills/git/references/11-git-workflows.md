# Git Workflows

## Understanding Workflows

A workflow defines how branches are created, managed, and merged. Choose based on team size, project type, and deployment needs.

## Centralized Workflow (Simple)

Best for: Small teams, simple projects, beginners

```
Everyone works from central repository:
  origin/main ←→ Developer A
       ↑
  origin/main ←→ Developer B
       ↑
  origin/main ←→ Developer C
```

### Process

```bash
# 1. Clone central repository
git clone https://github.com/team/project.git
cd project

# 2. Create feature branch
git switch -c feature/login-page

# 3. Work and commit
git add . && git commit -m "Add login form"

# 4. Push to central repo
git push -u origin feature/login-page

# 5. Team creates pull request / reviews

# 6. Merge to main (via PR or direct)
git switch main
git pull origin main
git merge feature/login-page
git push origin main
```

### Pros and Cons

**Pros:**
- Simple to understand
- Single source of truth
- Easy onboarding

**Cons:**
- Requires constant synchronization
- Merge conflicts common
- No integration branch buffer

## Feature Branch Workflow (GitHub Flow)

Best for: Web apps, continuous deployment, modern teams

```
main (always deployable)
  ↑
  ├── feature-1 → merged → deleted
  ├── feature-2 → merged → deleted
  └── feature-3 → merged → deleted
```

### Process

```bash
# 1. Fork repository (if using GitHub)
# Click "Fork" on GitHub, then:
git clone https://github.com/your-username/project.git
cd project
git remote add upstream https://github.com/original/project.git

# 2. Keep main up-to-date
git switch main
git fetch upstream
git merge upstream/main
git push origin main

# 3. Create feature branch from main
git switch -c feature/user-authentication

# 4. Develop with multiple commits
git add . && git commit -m "Add user model"
git add . && git commit -m "Add authentication logic"
git add . && git commit -m "Add login UI"

# 5. Push and create PR
git push -u origin feature/user-authentication
# Create PR on GitHub/GitLab interface

# 6. Address review feedback
git add . && git commit -m "Address review: fix validation"
git push  # Automatically updates PR

# 7. Squash and merge via UI (recommended)
# Or rebase before merging:
git switch main
git pull upstream main
git switch feature/user-authentication
git rebase main
git push --force-with-lease

# 8. After merge, clean up
git switch main
git pull
git branch -d feature/user-authentication
git push origin --delete feature/user-authentication
```

### Best Practices

1. **Short-lived branches** - Complete features in days, not weeks
2. **One PR per feature** - Keep changes focused and reviewable
3. **Squash on merge** - Clean linear history on main
4. **Always up-to-date with main** - Rebase frequently to avoid conflicts
5. **Delete merged branches** - Keep repository clean

## Git Flow (Traditional)

Best for: Projects with formal releases, versioned software

```
main (production) ←──← release/*
  ↑                    ↑
  └────── develop ─────┘
           ↑
    feature/* → merge here
    bugfix/* → merge here
    hotfix/* → merge to main & develop
```

### Branch Types

- **main**: Production-ready code only
- **develop**: Integration branch for next release
- **feature/**: New features (branch from develop, merge to develop)
- **release/**: Release preparation (branch from develop, merge to main & develop)
- **hotfix/**: Production fixes (branch from main, merge to main & develop)

### Process

```bash
# Start new feature
git switch -c feature/payment-gateway develop
# ... work ...
git switch develop
git merge feature/payment-gateway
git branch -d feature/payment-gateway

# Prepare release
git switch -c release/1.2.0 develop
# Final testing, version bumps, docs
git switch main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release 1.2.0"
git switch develop
git merge --no-ff release/1.2.0
git branch -d release/1.2.0

# Hotfix for production
git switch -c hotfix/critical-bug main
# ... fix ...
git switch main
git merge --no-ff hotfix/critical-bug
git tag -a v1.2.1 -m "Hotfix 1.2.1"
git switch develop
git merge --no-ff hotfix/critical-bug
git branch -d hotfix/critical-bug
```

### Pros and Cons

**Pros:**
- Clear structure for releases
- Production branch protected
- Good for versioned software

**Cons:**
- More complex than GitHub Flow
- develop branch can fall behind
- Overhead for simple projects

## Forking Workflow (Open Source)

Best for: Public projects, many external contributors

```
  upstream (official repo)
       ↑
  fork A ← contributor A
  fork B ← contributor B
  fork C ← contributor C
```

### Process (As Contributor)

```bash
# 1. Fork on GitHub (click button)
# 2. Clone YOUR fork
git clone https://github.com/your-username/project.git
cd project

# 3. Add upstream remote
git remote add upstream https://github.com/original/project.git
git remote -v  # Verify both remotes

# 4. Create feature branch
git switch -c feature/improvement

# 5. Develop
git add . && git commit -m "Implement improvement"

# 6. Keep in sync with upstream
git fetch upstream
git rebase upstream/main

# 7. Push to YOUR fork
git push -u origin feature/improvement

# 8. Create Pull Request on GitHub
# Point from your fork/branch to upstream/main

# 9. Update after review comments
git add . && git commit -m "Address feedback"
git push  # Updates PR automatically

# 10. After merge, clean up
git switch main
git fetch upstream
git merge upstream/main
git branch -d feature/improvement
git push origin --delete feature/improvement
```

### Process (As Maintainer)

```bash
# 1. Review PR on GitHub

# 2. Test locally if needed
git fetch origin  # Contributor's fork is now 'origin'
git switch -c test-pr origin/feature/improvement
# Test the changes

# 3. Merge via GitHub UI (recommended)
# Or locally:
git switch main
git merge test-pr
git push upstream main

# 4. Delete contributor's branch (if you have permission)
# Or ask them to delete it
```

## GitHub Flow Variations

### Trunk-Based Development

Best for: High-velocity teams, continuous integration

```
main (everyone merges here frequently)
  ↑
  Small features merged within hours/days
  Feature flags hide incomplete work
```

```bash
# Short-lived branches (hours, not days)
git switch -c tiny-feature
# ... small change ...
git commit -m "Add tiny feature"

# Merge immediately
git switch main
git merge --no-ff tiny-feature
git branch -d tiny-feature

# Use feature flags for incomplete work
# if (featureFlags.newDashboard) { ... }
```

### Release Branch Workflow

Best for: Projects needing stable release channels

```
main (latest stable)
  ↑
release/v1.x ←── stable 1.x updates
release/v2.x ←── stable 2.x updates
  ↑
develop (next version)
```

```bash
# Create release branch from develop
git switch -c release/v2.0 develop

# Freeze features, only bug fixes
# ... testing and fixes ...

# Tag and merge to main
git switch main
git merge --no-ff release/v2.0
git tag -a v2.0.0 -m "Release 2.0.0"

# Backport critical fixes to older releases
git switch -c hotfix/v1.9 release/v1.x
# ... fix ...
git switch release/v1.x
git merge hotfix/v1.9
git tag -a v1.9.1 -m "Patch release"
```

## Comparison Table

| Workflow | Best For | Complexity | Release Process |
|----------|----------|------------|-----------------|
| Centralized | Small teams, simple projects | Low | Direct to main |
| Feature Branch (GitHub Flow) | Web apps, CD | Low-Medium | PR → main |
| Git Flow | Versioned software | High | release/* branches |
| Forking | Open source, many contributors | Medium | PR from forks |
| Trunk-Based | CI/CD, high velocity | Low | Direct to trunk |

## Branch Naming by Workflow

### GitHub Flow

```bash
feature/user-authentication
bugfix/login-error
chore/update-dependencies
docs/api-documentation
refactor/authentication-module
```

### Git Flow

```bash
feature/payment-gateway
release/1.2.0
hotfix/critical-security-patch
support/customer-request-123
```

### Trunk-Based

```bash
# Very short names, short-lived
add-validation
fix-typo
small-improvement
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test
      - run: npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run deploy
```

### Protected Branches

Configure on GitHub/GitLab:
- Require pull request reviews
- Require status checks to pass
- Require linear history (no merge commits)
- Prevent force pushes
- Require signed commits

## Best Practices by Workflow

### All Workflows

1. **Descriptive branch names** - `feature/user-auth` not `feat-123`
2. **Frequent synchronization** - Pull/rebase often to avoid conflicts
3. **Small, focused changes** - Easier to review and debug
4. **Test before merging** - Automated tests + manual verification
5. **Document decisions** - Commit messages explain why, not just what

### Team Coordination

```bash
# Check who's working on what
git branch -r | grep feature/

# See unmerged branches
git branch --no-merged main

# Find conflicting changes early
git fetch
git rebase origin/main  # Do this frequently!
```

## Troubleshooting

### Workflow Confusion

```bash
# Where am I?
git branch          # Current local branch
git log --graph --oneline -10  # Recent history

# What should I do?
# GitHub Flow: Branch from main, PR to main
# Git Flow: Branch from develop, merge to develop (or release/)
```

### Wrong Base Branch

```bash
# Feature branched from wrong place
git switch feature-branch
git rebase --onto main old-base feature-branch
git push --force-with-lease
```

### Merge vs Rebase Decision

```bash
# Before merging feature branch:
# Use merge if: Multiple people on branch, need full history
git merge feature-branch

# Use rebase if: Solo work, want clean history
git rebase main
git switch main
git merge feature-branch
```
