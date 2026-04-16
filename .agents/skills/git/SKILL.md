---
name: git
description: >
  Complete Git v2.53 toolkit covering version control workflows, Conventional Commits v1.0.0,
  and Semantic Versioning 2.0.0. Use when managing repositories, writing structured commit messages,
  bumping versions, or analyzing codebase health through git history.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - git
  - version-control
  - conventional-commits
  - semver
  - devops
category: development
external_references:
  - https://git-scm.com/cheat-sheet
  - https://git-scm.com/docs/user-manual.html
  - https://raw.githubusercontent.com/conventional-commits/conventionalcommits.org/refs/heads/master/content/v1.0.0/index.md
  - https://raw.githubusercontent.com/semver/semver/refs/heads/master/semver.md
  - https://keepachangelog.com/en/1.1.0/
  - https://piechowski.io/post/git-commands-before-reading-code/
---

# Git v2.53 — Version Control, Conventional Commits & SemVer

A comprehensive toolkit for Git version control covering core workflows, the Conventional Commits specification (v1.0.0), and Semantic Versioning (v2.0.0). Provides practical command references, branching strategies, commit message conventions, and codebase analysis patterns.

## When to Use

- Setting up a new repository or cloning an existing one
- Writing structured, machine-readable commit messages following Conventional Commits
- Determining MAJOR/MINOR/PATCH version bumps using SemVer rules
- Analyzing codebase health through git history (churn, bug clusters, bus factor)
- Rewriting history interactively with rebase, cherry-pick, or reset
- Resolving merge conflicts and recovering from failed operations

## Quick Reference

### Common Git Commands

| Task | Command |
|------|---------|
| Initialize repo | `git init` |
| Clone repo | `git clone <url>` |
| Check status | `git status` |
| Stage changes | `git add <file>` / `git add -p` |
| Commit | `git commit -m "message"` |
| Amend last commit | `git commit --amend` |
| View history | `git log --oneline --graph` |
| Create branch | `git switch -c <name>` |
| Switch branch | `git switch <name>` |
| List branches | `git branch --sort=-committerdate` |
| Diff unstaged | `git diff` |
| Diff staged | `git diff --staged` |
| Show commit diff | `git show <commit>` |
| Stash changes | `git stash` |
| Merge branch | `git merge <branch>` |
| Rebase onto main | `git rebase main` |
| Fetch remotes | `git fetch` |
| Pull + merge | `git pull` |
| Push to remote | `git push` |
| Blame a file | `git blame <file>` |

### Conventional Commits — Type Quick Reference

| Type | SemVer Impact | Description |
|------|--------------|-------------|
| `feat:` | MINOR | New feature |
| `fix:` | PATCH | Bug fix |
| `docs:` | — | Documentation only |
| `style:` | — | Code style (formatting, semicolons) |
| `refactor:` | — | Code change that fixes neither bug nor adds feature |
| `perf:` | PATCH | Performance improvement |
| `test:` | — | Adding or correcting tests |
| `build:` | — | Build system or dependency changes |
| `ci:` | — | CI configuration changes |
| `chore:` | — | Other changes (no production code) |

Breaking changes: append `!` before `:` or add `BREAKING CHANGE:` footer.

### SemVer Bump Rules

| Commit Type | Version Bump | Example |
|-------------|-------------|---------|
| `fix` / `perf` | PATCH | 1.2.3 → 1.2.4 |
| `feat` | MINOR | 1.2.3 → 1.3.0 |
| `BREAKING CHANGE` | MAJOR | 1.2.3 → 2.0.0 |

## Reference Files

- [`references/01-core-git-commands.md`](references/01-core-git-commands.md) — Core Git workflows: init, clone, status, add, commit, diff, stash, restore, reset, log, blame
- [`references/02-version-control-workflows.md`](references/02-version-control-workflows.md) — Branching strategies, merging vs rebasing, remote operations, tags, worktrees
- [`references/03-conventional-commits.md`](references/03-conventional-commits.md) — Conventional Commits v1.0.0: structure, types, scopes, breaking changes, examples, FAQ
- [`references/04-semver-2-0-0.md`](references/04-semver-2-0-0.md) — SemVer 2.0.0: versioning rules, pre-release/build metadata, precedence comparison, validation regex
- [`references/05-codebase-analysis.md`](references/05-codebase-analysis.md) — Git archaeology: churn hotspots, bug clusters, bus factor, velocity tracking, piechowski diagnostic commands
- [`references/06-history-rewriting.md`](references/06-history-rewriting.md) — History rewriting: rebase -i, amend, reset, cherry-pick, conflict resolution, reflog recovery

## Troubleshooting

### Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Accidentally committed wrong file | `git restore --staged <file>` then commit again |
| Need to edit last commit message | `git commit --amend -m "new message"` |
| Messed up rebase | `git reflog` to find original commit, then `git reset --hard <commit>` |
| Merge conflict not resolving | Use `git status` to see conflicted files, edit them, then `git add` + `git continue` |
| Committed to wrong branch | Switch to correct branch and cherry-pick: `git cherry-pick <commit>` |

For detailed guidance on any topic, see the relevant reference file above.
