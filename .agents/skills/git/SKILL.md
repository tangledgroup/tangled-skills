---
name: git
description: >
  Complete Git v2.x toolkit covering version control workflows, Conventional Commits v1.0.0,
  Keep a Changelog message bodies, and Semantic Versioning 2.0.0. Use when managing repositories,
  writing structured commit messages with conventional types and changelog-style bodies,
  bumping versions, or analyzing codebase health through git history.
version: "0.5.0"
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

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
