# Merging Patterns

Merging combines divergent branches into a unified history. Git offers three merge types depending on branch topology.

## Merge Types

**Already up-to-date**: The branch being merged is already an ancestor of the current branch. No new commits, no merge commit created.

```bash
git merge feature-branch
# Already up-to-date.
```

**Fast-forward**: Current branch HEAD is a direct ancestor of the merging branch — straight-line history. Git simply advances the branch pointer forward; no merge commit is created.

```bash
# feature-branch extends main linearly
# A---B (main)
#      \
#       C---D (feature-branch)

git merge feature-branch
# Fast-forward

# Result: A---B---C---D (main, feature-branch)
```

**Three-way merge**: Both branches have independent commits since their common ancestor. Git creates a new merge commit with two parents.

```bash
# Divergent branches
#       C---D (feature-branch)
#      /
# A---B---E---F (main)

git merge feature-branch
# Merge made by the 'recursive' strategy.

# Result: merge commit M with parents F and D
#       C---D
#      /     \
# A---B---E---F---M (main)
```

## Merge Flags

```bash
# Default: allow fast-forward, create merge commit if diverged
git merge feature-branch

# Force a merge commit even when fast-forward is possible
git merge --no-ff feature-branch

# Only merge if fast-forward is possible (abort otherwise)
git merge --ff-only feature-branch
```

**When to use `--no-ff`**: Use when integrating feature branches to preserve the record of when and why a feature was merged. This keeps `git log --first-parent main` showing only integration points, not internal feature commits.

## Octopus Merge (Multiple Branches)

Merge more than two branches in a single command:

```bash
git merge feature-a feature-b feature-c
```

Creates one merge commit with three or more parents. Aborts on the first conflict — if conflicts are expected, merge sequentially instead.

```bash
# Sequential fallback when conflicts exist
git merge feature-a
# resolve conflicts
git add file.py && git commit

git merge feature-b
# resolve conflicts
git add file.py && git commit
```

## Merge Strategies

Git uses different algorithms depending on complexity. The default is **recursive** (handles criss-cross merges with multiple merge bases). Other strategies:

```bash
# Recursive (default, handles complex histories)
git merge feature-branch

# Resolve (legacy, single merge base only)
git merge -s resolve feature-branch

# Ours (record the merge but keep current branch content)
git merge -s ours experimental

# Subtree (merge into a subdirectory)
git merge -s subtree library-project/main
```

**Ours strategy**: Use when you manually integrated changes from another branch and want to mark it as merged to prevent Git from attempting future automatic merges. Creates a merge commit with multiple parents but keeps the current branch tree unchanged.

## Merge Conflicts

Conflicts occur when both branches modify the same lines in incompatible ways.

**Conflict markers in files:**

```python
def authenticate(user):
<<<<<<< HEAD
    return jwt.encode(user.id, secret_key)
=======
    return jwt.encode(user.email, secret_key)
>>>>>>> feature-branch
```

**With diff3 style** (shows the common ancestor between `HEAD` and `=======`):

```bash
git config --global merge.conflictstyle diff3
```

Produces:

```python
def authenticate(user):
<<<<<<< HEAD
    return jwt.encode(user.id, secret_key)
||||||| merged common ancestors
    return jwt.encode(user.username, secret_key)
=======
    return jwt.encode(user.email, secret_key)
>>>>>>> feature-branch
```

## Conflict Resolution Process

```bash
# 1. Identify conflicted files
git status
# both modified:   auth.py
# both modified:   config.py

# 2. Examine the conflict
git diff                          # combined diff with markers
git diff --ours                   # changes from current branch
git diff --theirs                 # changes from merging branch
git diff --base                   # changes from merge base

# 3. Inspect three versions during a conflict
git show :1:auth.py               # base (common ancestor)
git show :2:auth.py               # ours (current branch)
git show :3:auth.py               # theirs (merging branch)

# 4a. Resolve manually — edit file, remove markers, then:
git add auth.py

# 4b. Or accept one side completely
git checkout --ours auth.py       # keep current branch version
git checkout --theirs config.py   # keep merging branch version
git add auth.py config.py

# 4c. Or use a visual merge tool
git mergetool

# 5. Complete the merge
git commit
```

**Popular merge tools:** kdiff3, meld, vimdiff, p4merge, VS Code (`git config --global merge.tool vscode && git config --global mergetool.vscode.cmd 'code --wait --merge $REMOTE $LOCAL $BASE $MERGED'`).

## Abort a Merge

```bash
# Undo merge in progress (restores pre-merge state)
git merge --abort
```

Only works before the merge commit is created. After committing, use `git reset` to undo.

## Conflict History Analysis

```bash
# Show commits from both sides that touched a conflicted file
git log --merge auth.py

# Left/right notation: < = current branch, > = merging branch
git log --merge --left-right --oneline auth.py
# < abc123 Update auth to use ID
# > def456 Update auth to use email
```

## Rerere (Reuse Recorded Resolution)

Enable automatic replay of previously resolved conflicts:

```bash
git config --global rerere.enabled true
```

Git records conflict states and resolutions in `.git/rr-cache/`. When the same conflict pattern appears again, it auto-applies the recorded resolution. Developer verifies and commits.

## Common Merge Scenarios

**Update feature branch with latest main:**

```bash
git checkout feature-auth
git fetch origin
git merge main
# resolve conflicts if any, then continue development
```

**Integrate completed feature into main:**

```bash
git checkout main
git pull origin main
git merge --no-ff feature-payments -m "Merge feature-payments: Stripe integration

Complete payment processing implementation:
- Stripe API integration
- Payment webhook handlers
- Refund processing
- Comprehensive test suite

Closes #345, #367, #389"
git push origin main
```

**Emergency hotfix merge (GitFlow style):**

```bash
git checkout -b hotfix-security-1.2.1 v1.2.0
# ... implement fix ...
git commit -m "fix(security): patch authentication bypass"

git checkout main && git merge --no-ff hotfix-security-1.2.1
git tag -a v1.2.1 -m "Security hotfix release"
git checkout develop && git merge --no-ff hotfix-security-1.2.1
git push origin main develop v1.2.1
git branch -d hotfix-security-1.2.1
```

## Merge Configuration

```bash
# Better conflict markers (shows common ancestor)
git config --global merge.conflictstyle diff3

# Always create merge commits (no fast-forward by default)
git config --global merge.ff false

# Set default visual merge tool
git config --global merge.tool vimdiff
git config --global mergetool.keepBackup false
git config --global mergetool.prompt false

# Per-branch merge options
git config branch.main.mergeoptions "--no-ff"
git config branch.develop.mergeoptions "--ff-only"

# Verify settings
git config --global --get-regexp merge
```

## Merge vs. Rebase Decision Guide

**Use merge when:**
- Integrating into main/develop
- Working on a shared feature branch
- Preserving feature development context matters
- Commits have already been pushed

**Use rebase when:**
- Updating a personal (unpushed) feature branch
- Creating a clean linear history
- Preparing commits for review

**Golden rule:** Never rebase commits that have been pushed to shared branches.
