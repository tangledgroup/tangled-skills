---
name: git
description: >
  Complete Git v2.x toolkit covering version control workflows, Conventional Commits v1.0.0,
  Keep a Changelog message bodies, and Semantic Versioning 2.0.0. Use when managing repositories,
  writing structured commit messages with conventional types and changelog-style bodies,
  bumping versions, or analyzing codebase health through git history.
version: "0.4.0"
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
---

# Git Toolkit

## Overview

Practical reference for Git version control, structured commit conventions (Conventional Commits), semantic versioning rules, and changelog formatting. Covers the most common daily workflows — no plumbing commands or obscure edge cases.

## When to Use

- Setting up a new repository or cloning an existing one
- Staging, committing, branching, merging, or rebasing changes
- Writing commit messages that follow Conventional Commits format
- Determining whether a change warrants a major/minor/patch version bump
- Creating or updating a CHANGELOG following Keep a Changelog format
- Diagnosing a new codebase by analyzing its git history

## Core Concepts

Git tracks snapshots of your project through a directed acyclic graph of commits. Understanding these four areas is essential:

**Staging area (index)** — An intermediate layer between working directory and the repository. You explicitly choose which changes to include in the next commit using `git add`. This gives you fine-grained control over commit granularity.

**Branches** — Lightweight movable pointers to commits. The default branch is usually `main` or `master`. Branches let you develop features, fix bugs, or experiment without affecting the main codebase.

**Commits** — Snapshots of your project at a point in time, each with a unique 40-character SHA-1 hash. A commit records what changed, who made the change, when, and why (via the commit message).

**Remotes** — Named references to other repositories (e.g., `origin`). Remotes enable collaboration: you push your commits to share them and fetch/pull others' commits to stay in sync.

## Essential Commands

### Initialize and Clone

```bash
git init                          # Start a new repository
git clone <url>                   # Clone an existing remote repository
```

### Stage and Commit

```bash
git add <file>                    # Stage a specific file or changes
git add .                         # Stage all untracked and modified files
git add -p                        # Interactively choose which hunks to stage
git mv <old> <new>                # Move/rename a file (updates index)
git rm <file>                     # Remove a file from working dir and index
git rm --cached <file>            # Stop tracking a file without deleting it
git status                        # Show staged, unstaged, and untracked files
```

### Make Commits

```bash
git commit                        # Open editor to write commit message
git commit -m 'message'           # Commit with inline message
git commit -am 'message'          # Stage all tracked changes and commit
git commit --amend                # Modify the most recent commit (message or contents)
```

### Branch and Switch

```bash
git switch <name>                 # Switch to branch <name>
git switch -c <name>              # Create and switch to a new branch
git checkout <name>               # Alternative: switch branches
git checkout -b <name>            # Alternative: create and switch branch
git branch                        # List local branches
git branch --sort=-committerdate  # Sort by most recent commit
git branch -d <name>              # Delete a merged branch
git branch -D <name>              # Force delete (even if unmerged)
```

### Diff and Show

```bash
git diff                          # Unstaged changes (working dir vs index)
git diff --staged                 # Staged changes (index vs HEAD)
git diff HEAD                     # All changes vs latest commit
git show <commit>                 # Changes in a specific commit
git show <commit> --stat          # Summary of a commit's changes
git diff <commit1> <commit2>      # Diff between two commits
```

### Ways to Refer to Commits

| Reference | Meaning |
|-----------|---------|
| `main` | A branch name |
| `v0.1` | A tag name |
| `3e887ab` | Commit ID (short hash) |
| `origin/main` | Remote branch |
| `HEAD` | Current commit |
| `HEAD~3` | Three commits before HEAD |
| `HEAD^^^` | Alternative syntax for three parents back |

### Discard Changes

```bash
git restore <file>                # Undo unstaged changes to a file
git checkout <file>               # Alternative: discard working dir changes
git restore --staged --worktree <file>  # Unstage and discard
git reset <file>                  # Unstage a specific file
git reset                         # Unstage everything
git reset --hard                  # Discard all staged and unstaged changes
git clean                         # Remove untracked files
git stash                         # Temporarily save all working changes
```

### Edit History

```bash
git reset HEAD^                   # Undo the most recent commit (keep changes)
git rebase -i HEAD~6              # Interactive rebase of last 5 commits
                                  # Change "pick" to "fixup" to squash commits
git reflog BRANCHNAME             # Find lost commits after a failed rebase
```

### Merge and Rebase

```bash
git switch main                   # Switch to target branch
git merge banana                  # Merge branch into current branch
git switch banana                 # Switch to feature branch
git rebase main                   # Rebase feature onto main (linear history)
```

### Remotes, Push, Pull

```bash
git remote -v                     # List remotes and their URLs
git fetch origin                  # Download commits without merging
git pull origin main              # Fetch and merge remote changes
git push origin main              # Upload local commits to remote
```

### Log and Blame

```bash
git log main                      # Show commit history for a branch
git log --graph main              # Graph-shaped history view
git log --oneline                 # Compact one-line-per-commit
git log <file>                    # Commits that modified a file
git log --follow <file>           # Track renames across history
git log -G banana                 # Commits adding/removing "banana" text
git blame <file>                  # Show who last changed each line
```

## Commit Conventions

### Conventional Commits Format

Structure your commit messages as:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- **`fix:`** — Bug fix (corresponds to PATCH version bump)
- **`feat:`** — New feature (corresponds to MINOR version bump)
- **`BREAKING CHANGE:`** in footer or `!` before colon — Breaking API change (MAJOR version bump)

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

- **MAJOR** — Incompatible API changes (use `BREAKING CHANGE` in commit)
- **MINOR** — Backward-compatible functionality added (use `feat:` type)
- **PATCH** — Backward-compatible bug fixes (use `fix:` type)
- Pre-release versions use a hyphen: `1.0.0-alpha`, `1.0.0-beta.2`
- Build metadata uses a plus: `1.0.0+20130313144700` (ignored in precedence)

## Changelog Format

Follow [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/) structure:

```markdown
# Changelog

All notable changes to this project will be documented in this file.
The format is based on Keep a Changelog, and this project adheres to SemVer.

## [Unreleased]

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

Use these section names in this order: **Added, Changed, Deprecated, Removed, Fixed, Security**. Leave out sections with no changes. Include an `[Unreleased]` section for work not yet shipped.

## Codebase Diagnostics

Before reading code in a new project, run these five commands from `app/` or `src/` (not the repo root) to understand the codebase:

```bash
# 1. What changes the most (code churn hotspots)
git log --format=format: --name-only --since="1 year ago" \
  | sort | uniq -c | sort -nr | head -20

# 2. Who built this (bus factor)
git shortlog -sn --no-merges

# 3. Where do bugs cluster
git log -i -E --grep="fix|bug|broken" --name-only \
  --format='' | sort | uniq -c | sort -nr | head -20

# 4. Project velocity over time
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c

# 5. How often is the team firefighting
git log --oneline --since="1 year ago" \
  | grep -iE 'revert|hotfix|emergency|rollback'
```

Cross-reference churn hotspots with bug clusters: files appearing on both lists are highest-risk code.
