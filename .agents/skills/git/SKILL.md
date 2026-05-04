---
name: git
description: >
  Complete Git 2.54.0 toolkit covering version control workflows, Conventional Commits v1.0.0,
  Keep a Changelog message bodies, and Semantic Versioning 2.0.0. Use when managing repositories,
  writing structured commit messages with conventional types and changelog-style bodies,
  bumping versions, or analyzing codebase health through git history.
version: "0.2.1"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - meta
  - meta-skill
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
  - https://github.com/newren/git-filter-repo
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

"add" / "add all" → `git add .`
"commit" / "commit all" → `git commit -a -m '<message>'`
"push" / "push all" → `git push origin <current-branch>`
"add, commit, push" → all three steps in order
"acp" → short for "add, commit, push"

### No File-Specific Overrides

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

[Unreleased]

...

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

## Advanced Topics

**Essential Commands**: Init, clone, add, commit, branch, diff, stash, reset, remote, log → [Essential Commands](reference/01-essential-commands.md)
**Merging Patterns**: Merge types, flags, conflicts, strategies, rebase decisions → [Merging Patterns](reference/02-merging-patterns.md)
**Codebase Diagnostics**: Churn hotspots, bus factor, bug clusters, velocity → [Codebase Diagnostics](reference/03-codebase-diagnostics.md)
**History Rewriting**: git filter-repo for stripping files, renaming paths, removing secrets, rewriting authors → [History Rewriting](reference/04-filter-repo.md)
