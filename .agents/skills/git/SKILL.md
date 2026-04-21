---
name: git
description: >
  Complete Git v2.53 toolkit covering version control workflows, Conventional Commits v1.0.0,
  Keep a Changelog message bodies, and Semantic Versioning 2.0.0. Use when managing repositories,
  writing structured commit messages with conventional types and changelog-style bodies,
  bumping versions, or analyzing codebase health through git history.
version: "0.3.0"
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
---

# Git v2.53 — Version Control, Conventional Commits & SemVer

A comprehensive toolkit for Git version control covering core workflows, the Conventional Commits specification (v1.0.0), and Semantic Versioning (v2.0.0). Provides practical command references, branching strategies, commit message conventions, and codebase analysis patterns.

## When to Use

- Setting up a new repository or cloning an existing one
- Writing structured commit messages: Conventional Commits type on line 1 + Keep a Changelog categories in body
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
| Check status | `git status` / `git status -s` |
| Stage all changes | `git add -A` |
| Stage selectively | `git add -p <file>` |
| Commit (one-liner) | `git commit -m "type: description"` |
| Commit (detailed, editor) | `git commit` |
| Amend last commit | `git commit --amend [--no-edit]` |
| View history | `git log --oneline --graph` |
| Create branch | `git switch -c <name>` |
| Switch branch | `git switch <name>` |
| List branches | `git branch --sort=-committerdate` |
| Diff unstaged | `git diff` |
| Diff staged | `git diff --staged` |
| Show commit diff | `git show <commit>` |
| Stash changes | `git stash` / `git stash push -u` |
| Merge branch | `git merge <branch>` |
| Rebase onto main | `git rebase main` |
| Fetch remotes | `git fetch` |
| Pull + merge | `git pull` |
| Push to remote | `git push` |
| Safe force push | `git push --force-with-lease` |
| Blame a file | `git blame <file>` |

### Conventional Commits — Type Quick Reference

| Type | SemVer Impact | Description |
|------|--------------|-------------|
| `feat` | MINOR | New feature |
| `fix` | PATCH | Bug fix |
| `docs` | — | Documentation only |
| `style` | — | Code style (formatting, semicolons) |
| `refactor` | — | Code change that fixes neither bug nor adds feature |
| `perf` | PATCH | Performance improvement |
| `test` | — | Adding or correcting tests |
| `build` | — | Build system or dependency changes |
| `ci` | — | CI configuration changes |
| `chore` | — | Other changes (no production code) |

Breaking changes: append `!` before `:` or add `BREAKING CHANGE:` footer.

## Commit Message Format

Every commit message combines **Conventional Commits** (first line) with **Keep a Changelog** categories (body).

### Structure

```
<type>[optional scope]: <description>

[optional body with Keep a Changelog categories]

[optional footer(s)]
```

- **Line 1 (subject):** Conventional Commits — `<type>[scope]!: <description>`
- **Body paragraphs:** Keep a Changelog change categories — `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
- **Footers:** References, breaking changes, related issues

### Subject Line (Line 1)

The subject line follows the Conventional Commits spec:

```
type[scope]!: description
```

| Element | Required | Example |
|---------|----------|---------|
| `type` | Yes | `feat`, `fix`, `docs`, `refactor`, etc. |
| `[scope]` | No | `(auth)`, `(api)`, `(cli)` |
| `!` | Optional (breaking) | `feat!:`, `feat(api)!:` |
| `: ` | Yes | Always colon + space after type/scope/! |
| `description` | Yes | Short imperative summary, lowercase |

### Body Paragraphs (Keep a Changelog Categories)

The body organizes changes using Keep a Changelog categories. Each category is a heading followed by bullet points:

```
Added: for new features.
Changed: for changes in existing functionality.
Deprecated: for soon-to-be removed features.
Removed: for now removed features.
Fixed: for any bug fixes.
Security: in case of vulnerabilities.
```

**Rules:**
- One blank line separates the subject from the body
- Each category heading is a paragraph starting with the category name followed by a colon
- Bullet points under each category describe specific changes
- Only include categories that have relevant changes (omit empty sections)
- Group related changes together under the same category

### Complete Example

```
feat(auth): add OAuth2 social login

Added:
- Google and GitHub OAuth2 login providers
- Social login button on authentication page
- Session creation via OAuth callback handler

Changed:
- Refactored user registration flow to support multiple auth methods
- Updated database migration for provider foreign keys

Fixed:
- Race condition in session token generation
```

### Breaking Change Example

```
feat(api)!: drop v1 endpoints, require v2 requests

BREAKING CHANGE: All /api/v1/ routes removed. Clients must migrate to /api/v2/.
The response format has changed from snake_case to camelCase.

Changed:
- Migrated all route handlers to v2 namespace
- Updated response serialization to use camelCase
- Added v2 middleware for request transformation

Deprecated:
- /api/v1/users endpoint — removed in v3
- /api/v1/products endpoint — removed in v3
```

### Reference Files

- [`references/03-conventional-commits.md`](references/03-conventional-commits.md) — Conventional Commits v1.0.0: structure, types, scopes, breaking changes, examples

## Stage, Commit & Push — Detailed Workflow

This section covers the complete workflow from staging changes to pushing, with emphasis on writing detailed, structured commit messages.

### Staging Changes

Git has three states: working tree (your files), index/staging area (what will be committed), and history (committed snapshots).

```bash
git add <file>                    # Stage a specific file
git add .                         # Stage all modified + new files in current dir (not deleted)
git add -A                        # Stage ALL changes: modified, new, and deleted
git add -u                        # Stage only modified + deleted tracked files (ignores untracked)
```

**Key differences:**
- `git add .` — does NOT stage deleted files or untracked files outside current directory tree
- `git add -A` — stages everything: new, modified, deleted, everywhere under the repo root
- `git add -u` — stages only tracked files that have been modified or deleted (ignores new/untracked)

### Selective Staging (Interactive Mode)

When you've changed multiple things but want to commit them separately:

```bash
git add -p                        # Interactive: accept/reject changes hunk by hunk
git add -p <file>                 # Interactive for a specific file
```

In interactive mode, Git shows hunks (contiguous changed blocks). Press:
- `y` — accept this hunk
- `n` — skip this hunk
- `e` — manually edit which lines to stage
- `s` — split hunk into smaller pieces
- `q` — quit, accepting none of the remaining hunks
- `a` — accept all remaining hunks in this file

### Viewing What Will Be Committed

```bash
git diff                          # Unstaged changes (working tree vs index)
git diff --staged                 # Staged changes (index vs HEAD)
git diff HEAD                     # Everything (staged + unstaged) vs last commit
git diff --stat                   # Summary: files changed, insertions, deletions
```

### Committing with a Detailed Message

#### Simple One-Liner Commit

```bash
git commit -m "feat(auth): add OAuth2 login"
```

#### Structured Commit (Inline)

For multi-line messages, use a here-doc or escaped newlines:

```bash
git commit -m "feat(auth): add OAuth2 social login" \
  -m "Added: Google and GitHub OAuth2 providers. Changed: refactored registration flow."
```

#### Structured Commit (Editor)

The recommended approach for detailed commits — opens your `$EDITOR`:

```bash
git commit                        # Opens editor with template
```

This writes a commit combining **Conventional Commits** (line 1) and **Keep a Changelog categories** (body):

```
feat(auth): add OAuth2 social login

Added:
- Google and GitHub OAuth2 login providers
- Social login button on authentication page
- Session creation via OAuth callback handler

Changed:
- Refactored user registration flow to support multiple auth methods
- Updated database migration for provider foreign keys

Fixed:
- Race condition in session token generation
```

#### Amending After Adding More Files

If you committed but forgot a file or want to refine the message:

```bash
git add forgotten_file.py         # Stage the missed file
git commit --amend                # Opens editor to edit the message
git commit --amend --no-edit      # Amend without changing the message
```

> **Rule:** Only amend commits that have NOT been pushed. Once pushed, amending rewrites history and breaks collaborators' clones.

### Pushing to Remote

```bash
git push                          # Push to configured upstream branch
git push origin main              # Push 'main' to 'origin'
git push --set-upstream origin main  # Set upstream tracking for a new branch
git push -u origin main           # Shorthand for --set-upstream
```

#### Force-Pushing (Rewritten History)

When you've rebased or amended commits and need to update a remote branch:

```bash
git push --force-with-lease       # Safe: fails if someone pushed in the meantime
git push -f                       # Dangerous: overwrites remote regardless
git push --force                  # Same as -f
```

**Always prefer `--force-with-lease` over `-f`.** It checks that the remote branch hasn't been updated by someone else since your last fetch. A plain `-f` will silently overwrite a collaborator's commits.

#### Push Tags

```bash
git push origin v1.0              # Push a single tag
git push origin --tags            # Push all tags
```

### Complete Workflow Examples

#### Workflow 1: Clean Commit of All Changes

```bash
git status                        # Review what changed
git add -A                        # Stage everything
git diff --staged                 # Verify staged changes look correct
git commit -m "feat(api): add user search endpoint"
                                   # (or: git commit to open editor for detailed message)
git push                          # Push to remote
```

#### Workflow 2: Selective Commit with Detailed Message

```bash
git status                        # See all changes
git add -p                         # Stage only relevant hunks
git diff --staged                 # Verify staged changes
git commit                        # Opens editor for detailed message
# Write Conventional Commit subject + Keep a Changelog body
git push                          # Push to remote
```

#### Workflow 3: Fix a Mistake After Committing

```bash
git commit -m "feat: add user login"
git add forgotten_file.py         # Add missed file
git commit --amend --no-edit      # Fold it into previous commit
git push --force-with-lease       # Update remote (safe force-push)
```

#### Workflow 4: Squash Before Pushing

```bash
git rebase -i HEAD~3              # Interactively rebase last 3 commits
# Change 'pick' to 'squash' or 'fixup' for commits to merge
# Resolve any conflicts, then:
git rebase --continue             # Continue until done
git push --force-with-lease       # Push the clean history
```

### SemVer Bump Rules

| Commit Type | Version Bump | Example |
|-------------|-------------|---------|
| `fix` / `perf` | PATCH | 1.2.3 → 1.2.4 |
| `feat` | MINOR | 1.2.3 → 1.3.0 |
| `BREAKING CHANGE` | MAJOR | 1.2.3 → 2.0.0 |

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
