---
name: git
description: >
  Complete Git 2.54.0 toolkit covering version control workflows, Conventional Commits v1.0.0,
  Keep a Changelog message bodies, and Semantic Versioning 2.0.0. Use when managing repositories,
  writing structured commit messages with conventional types and changelog-style bodies,
  bumping versions, or analyzing codebase health through git history.
version: "2.54.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - git
  - version-control
  - conventional-commits
  - keep-a-changelog
  - semver
  - devops
category: development
external_references:
  - https://git-scm.com/cheat-sheet
  - https://git-scm.com/docs/user-manual.html
  - https://www.conventionalcommits.org/en/v1.0.0/
  - https://raw.githubusercontent.com/conventional-commits/conventionalcommits.org/refs/heads/master/content/v1.0.0/index.md
  - https://semver.org/spec/v2.0.0.html
  - https://raw.githubusercontent.com/semver/semver/refs/heads/master/semver.md
  - https://keepachangelog.com/en/1.1.0/
  - https://piechowski.io/post/git-commands-before-reading-code/
  - https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/refs/heads/main/skills/karpathy-guidelines/SKILL.md
  - https://gitcheatsheet.dev/docs/everyday-git/merging/
---

# Git Toolkit

## Overview

Git version control, structured commit conventions (Conventional Commits), semantic versioning rules, and changelog formatting. Covers common daily workflows — no plumbing commands or obscure edge cases.

## When to Use

- Setting up a new repository or cloning an existing one
- Staging, committing, branching, merging, or rebasing changes
- Writing commit messages following Conventional Commits format
- Determining whether a change warrants a major/minor/patch version bump
- Creating or updating a CHANGELOG following Keep a Changelog format
- Diagnosing a new codebase by analyzing its git history

## Core Concepts

Git tracks snapshots through a directed acyclic graph of commits. Four areas:

**Staging area (index)** — Intermediate layer between working tree and repo. Use `git add` to choose which changes enter the next commit, giving fine-grained control over commit granularity.

**Branches** — Lightweight movable pointers to commits. Default is usually `main` or `master`. Branches let you develop features or fix bugs without affecting the main codebase.

**Commits** — Snapshots with a unique 40-character SHA-1 hash. Each records what changed, who made it, when, and why (via the commit message).

**Remotes** — Named references to other repositories (e.g., `origin`). Push to share commits, fetch/pull to sync with others.

## Workflow Shorthands

When the user says "add, commit, push" (or similar shorthand), interpret as a three-step workflow operating on **all** changes by default, scoped to specific files if provided.

### Default Behavior — All Changes

"add" / "add all" → `git add .` then `git commit -m '<message>'`
"commit" / "commit all" → `git add . && git commit -m '<message>'`
"push" / "push all" → `git push origin <current-branch>`
"add, commit, push" → all three steps in order
"acp" → short for "add, commit, push"

When no files are specified, **always operate on all changes**:
```bash
git add .
git commit -m "<descriptive message following Conventional Commits>"
git push origin <current-branch>
```

### File-Specific Overrides

If the user names specific files or directories, scope only those:
```bash
git add path/to/file.py src/utils/
git commit -m "<descriptive message following Conventional Commits>"
git push origin <current-branch>
```

### When to Ask for Clarification

- User says "add" without a message → propose a Conventional Commits message from `git diff --staged` or `git status`
- User says "push" but no commits to push → suggest checking `git log origin/<branch>..HEAD`
- Dirty working directory and user says "push" → warn about pushing without committing first

## Essential Commands

### Initialize and Clone

```bash
# Start a new repository
git init
# Clone an existing remote repository
git clone <url>
```

### Stage and Commit

```bash
# Stage a specific file
git add <file>
# Stage all untracked and modified files
git add .
# Interactively choose hunks to stage
git add -p
# Move/rename a file (updates index)
git mv <old> <new>
# Remove a file from working dir and index
git rm <file>
# Stop tracking without deleting
git rm --cached <file>
# Show staged, unstaged, and untracked files
git status
```

### Make Commits

```bash
# Open editor for commit message
git commit
# Commit with inline message
git commit -m 'message'
# Stage all tracked changes and commit
git commit -am 'message'
# Modify the most recent commit (message or contents)
git commit --amend
```

### Branch and Switch

```bash
# Switch to branch <name>
git switch <name>
# Create and switch to new branch
git switch -c <name>
# Alternative: switch branches
git checkout <name>
# Alternative: create and switch branch
git checkout -b <name>
# List local branches
git branch
# Sort by most recent commit
git branch --sort=-committerdate
# Delete a merged branch
git branch -d <name>
# Force delete (even if unmerged)
git branch -D <name>
```

### Diff and Show

```bash
# Unstaged changes (working dir vs index)
git diff
# Staged changes (index vs HEAD)
git diff --staged
# All changes vs latest commit
git diff HEAD
# Changes in a specific commit
git show <commit>
# Summary of a commit's changes
git show <commit> --stat
# Diff between two commits
git diff <commit1> <commit2>
```

### Ways to Refer to Commits

`main` → branch name
`v0.1` → tag name
`3e887ab` → commit ID (short hash)
`origin/main` → remote branch
`HEAD` → current commit
`HEAD~3` → three commits before HEAD
`HEAD^^^` → three parents back (alt syntax)

### Discard Changes

```bash
# Undo unstaged changes to a file
git restore <file>
# Alternative: discard working dir changes
git checkout <file>
# Unstage and discard
git restore --staged --worktree <file>
# Unstage a specific file
git reset <file>
# Unstage everything
git reset
# Discard all staged and unstaged changes
git reset --hard
# Remove untracked files
git clean
# Temporarily save all working changes
git stash
```

### Edit History

```bash
# Undo the most recent commit (keep changes)
git reset HEAD^
# Interactive rebase of last 5 commits; change "pick" to "fixup" to squash
git rebase -i HEAD~6
# Find lost commits after a failed rebase
git reflog BRANCHNAME
```

### Merge and Rebase

```bash
# Switch to target branch
git switch main
# Merge branch into current branch
git merge banana
# Switch to feature branch
git switch banana
# Rebase feature onto main (linear history)
git rebase main
```

## Merging Patterns

Merging combines divergent branches into a unified history. Git offers three merge types depending on branch topology.

### Merge Types

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

### Merge Flags

```bash
# Default: allow fast-forward, create merge commit if diverged
git merge feature-branch

# Force a merge commit even when fast-forward is possible
git merge --no-ff feature-branch

# Only merge if fast-forward is possible (abort otherwise)
git merge --ff-only feature-branch
```

**When to use `--no-ff`**: Use when integrating feature branches to preserve the record of when and why a feature was merged. This keeps `git log --first-parent main` showing only integration points, not internal feature commits.

### Octopus Merge (Multiple Branches)

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

### Merge Strategies

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

### Merge Conflicts

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

### Conflict Resolution Process

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

### Abort a Merge

```bash
# Undo merge in progress (restores pre-merge state)
git merge --abort
```

Only works before the merge commit is created. After committing, use `git reset` to undo.

### Conflict History Analysis

```bash
# Show commits from both sides that touched a conflicted file
git log --merge auth.py

# Left/right notation: < = current branch, > = merging branch
git log --merge --left-right --oneline auth.py
# < abc123 Update auth to use ID
# > def456 Update auth to use email
```

### Rerere (Reuse Recorded Resolution)

Enable automatic replay of previously resolved conflicts:

```bash
git config --global rerere.enabled true
```

Git records conflict states and resolutions in `.git/rr-cache/`. When the same conflict pattern appears again, it auto-applies the recorded resolution. Developer verifies and commits.

### Common Merge Scenarios

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

### Merge Configuration

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

### Merge vs. Rebase Decision Guide

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

### Remotes, Push, Pull

```bash
# List remotes and their URLs
git remote -v
# Download commits without merging
git fetch origin
# Fetch and merge remote changes
git pull origin main
# Upload local commits to remote
git push origin main
```

### Log and Blame

```bash
# Show commit history for a branch
git log main
# Graph-shaped history view
git log --graph main
# Compact one-line-per-commit
git log --oneline
# Commits that modified a file
git log <file>
# Track renames across history
git log --follow <file>
# Commits adding/removing "banana" text
git log -G banana
# Show who last changed each line
git blame <file>
```

## Commit Conventions

### Conventional Commits Format

Structure commit messages as:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- `fix:` — Bug fix (→ PATCH bump)
- `feat:` — New feature (→ MINOR bump)
- `BREAKING CHANGE:` in footer or `!` before colon → MAJOR bump

Other accepted types: `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`.

### Examples

```bash
# Simple fix
git commit -m "fix: handle null pointer in user parser"
# Feature with scope
git commit -m "feat(auth): add OAuth2 token refresh flow"
# Breaking change with bang
git commit -m "feat(api)!: remove deprecated /v1 endpoints"
# With body and footer
git commit -m "fix: prevent racing of requests

Introduce a request id and reference to latest request.
Dismiss incoming responses other than from the latest.

Remove obsolete timeouts.
Reviewed-by: Z
Refs: #123"
```

### SemVer Bumping Rules

Given version `MAJOR.MINOR.PATCH`:

- **MAJOR** — Incompatible API changes (use `BREAKING CHANGE`)
- **MINOR** — Backward-compatible additions (use `feat:`)
- **PATCH** — Backward-compatible fixes (use `fix:`)
- Pre-release: `1.0.0-alpha`, `1.0.0-beta.2`
- Build metadata: `1.0.0+20130313144700` (ignored in precedence)

## Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.
The format is based on Keep a Changelog, and this project adheres to SemVer.

## v<MAJOR>.<MINOR>.<PATCH>

### Added
- New feature description

### Changed
- Modified behavior description

### Deprecated
- Soon-to-be-removed feature

### Removed
- Feature that has been removed

### Fixed
- Bug fix description

### Security
- Vulnerability fixes
```

Section order: **Added, Changed, Deprecated, Removed, Fixed, Security**.
Omit empty sections.
For unknown next `v<MAJOR>.<MINOR>.<PATCH>`, include `[Unreleased]` for work not yet shipped.

## Codebase Diagnostics

Before reading code in a new project, run these five commands:

```bash
# What changes the most (code churn hotspots)
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20
# Who built this (bus factor)
git shortlog -sn --no-merges
# Where do bugs cluster
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20
# Project velocity over time
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
# How often is the team firefighting
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback'
```

Cross-reference churn hotspots with bug clusters: files on both lists are highest-risk code.
