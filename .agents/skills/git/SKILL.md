---
name: git
description: A skill for using Git version control system to track changes, collaborate, and manage code repositories. Use when working with Git repositories, managing branches, or collaborating on code projects.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - version-control
  - collaboration
  - repository
  - branching
category: version-control
---

# Git Version Control Skill

A comprehensive skill for using Git, the distributed version control system. This skill covers basic to advanced Git operations including branching, merging, rebasing, and collaboration workflows.

## When to Use

- Initialize a new Git repository or clone an existing one
- Track changes to files with commits
- Create and manage branches for features or fixes
- Merge or rebase branches to integrate changes
- Collaborate with teams using remote repositories
- Resolve merge conflicts
- Undo or modify previous commits
- Share changes with `push` and update with `pull`

## Quick Start

### Initialize or Clone a Repository

```bash
# Create new repository
git init my-project
cd my-project

# Clone existing repository
git clone https://github.com/user/repo.git
```

See [Repository Basics](references/01-repository-basics.md) for detailed setup instructions.

### Basic Workflow

```bash
# Check status
git status

# Add files to staging
git add <file>
git add .

# Commit changes with semantic message
git commit -m "feat: add user authentication"

# Push to remote
git push origin main
```

See [Basic Operations](references/02-basic-operations.md) for detailed commands.

### Semantic Commit Messages (Conventional Commits)

Use [Conventional Commits](https://www.conventionalcommits.org/) for human and machine-readable commit history. This specification provides an easy set of rules for creating an explicit commit history, making it easier to write automated tools on top of.

**Format:**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types

The Conventional Commits specification **MUST** use `feat` and `fix` types. Additional types are allowed but have no implicit SemVer effect.

| Type | SemVer Impact | Description |
|------|---------------|-------------|
| `feat` | **MINOR** (0.y.z) | Adds a new feature to the codebase |
| `fix` | **PATCH** (x.y.z) | Patches a bug in your codebase |
| `docs` | None | Documentation only changes |
| `style` | None | Formatting changes, missing semicolons, etc. (no code change) |
| `refactor` | None | Code refactoring without behavior change |
| `perf` | None | Performance improvements |
| `test` | None | Adding or updating tests |
| `chore` | None | Build process, auxiliary tools changes |
| `build` | None | Changes affecting build system or external dependencies |
| `ci` | None | CI configuration files and scripts |
| `revert` | None | Reverts a previous commit |

**Note:** Types are **case-insensitive**, but consistency is recommended. Only `BREAKING CHANGE` in footers MUST be uppercase.

#### Breaking Changes

A **BREAKING CHANGE** can be part of commits of any type and correlates with a **MAJOR** version bump (x.0.0). Indicate breaking changes in one or both ways:

1. **Add `!` immediately before the colon after type/scope:**
   ```bash
   git commit -m "feat!: remove deprecated user endpoint"
   git commit -m "feat(api)!: change response format to JSON"
   ```
   When `!` is used, the description SHALL be used to describe the breaking change, and the `BREAKING CHANGE:` footer MAY be omitted.

2. **Use `BREAKING CHANGE:` footer:**
   ```bash
   git commit -m "feat: add new config option" -m "BREAKING CHANGE: old config key 'timeout' renamed to 'requestTimeout'"
   ```
   The footer MUST consist of uppercase `BREAKING CHANGE`, followed by a colon, space, and description.

3. **Both `!` and footer (for emphasis):**
   ```bash
   git commit -m "feat!: drop support for Node 6" -m "BREAKING CHANGE: use JavaScript features not available in Node 6."
   ```

**Important:** Breaking changes MUST be indicated either in the type/scope prefix with `!`, or as a `BREAKING CHANGE:` footer (or both).

#### Scope

A scope **MAY** be provided after a type to provide additional contextual information. A scope **MUST** consist of a noun describing a section of the codebase surrounded by parenthesis:

- `feat(parser): add ability to parse arrays`
- `feat(auth): add OAuth2 support`
- `fix(api): resolve timeout on slow connections`
- `docs(readme): update installation steps`
- `feat(lang): add Polish language`

#### Body and Footers

**Body:**
- A longer commit body **MAY** be provided after the short description, providing additional contextual information about the code changes.
- The body **MUST** begin one blank line after the description.
- The body is free-form and **MAY** consist of any number of newline-separated paragraphs.

**Footers:**
- One or more footers **MAY** be provided one blank line after the body.
- Each footer **MUST** consist of a word token, followed by either a `:<space>` or `<space>#` separator, followed by a string value (inspired by [git trailer format](https://git-scm.com/docs/git-interpret-trailers)).
- A footer's token **MUST** use `-` in place of whitespace characters (e.g., `Reviewed-by`, not `Reviewed by`). An exception is made for `BREAKING CHANGE`, which **MAY** also be used as a token.
- A footer's value **MAY** contain spaces and newlines.

For complex changes, use a multi-line commit:

```bash
git commit -m "fix: prevent racing of requests" \
  -m "" \
  -m "Introduce a request id and a reference to latest request. Dismiss" \
  -m "incoming responses other than from latest request." \
  -m "" \
  -m "Remove timeouts which were used to mitigate the racing issue but are" \
  -m "obsolete now." \
  -m "" \
  -m "Reviewed-by: Alice" \
  -m "Refs: #123"
```

**Common footers:**
- `BREAKING CHANGE:` or `BREAKING-CHANGE:` - Describe the breaking change (MUST be uppercase)
- `Refs: #123` or `Closes: #123` - Reference issues/PRs
- `Reviewed-by: Name` - Track code review approval
- `Co-authored-by: Name <email>` - For co-authored commits

#### Examples by Type

```bash
# New feature
git commit -m "feat: add user authentication"

# Feature with scope
git commit -m "feat(auth): add OAuth2 support"

# Bug fix
git commit -m "fix(api): resolve timeout on slow connections"

# Breaking change with ! (no footer needed)
git commit -m "feat!: remove deprecated login endpoint"

# Breaking change with scope and !
git commit -m "feat(api)!: change response format to JSON"

# Breaking change with footer only
git commit -m "chore: update dependencies" -m "BREAKING CHANGE: requires Node.js 18+"

# Breaking change with both ! and footer
git commit -m "feat!: drop support for Node 6" -m "BREAKING CHANGE: use JavaScript features not available in Node 6."

# Documentation
git commit -m "docs(readme): update installation steps"

# Performance improvement
git commit -m "perf(database): optimize query execution time"

# Refactoring
git commit -m "refactor(utils): simplify date formatting logic"

# Test addition
git commit -m "test(auth): add unit tests for login flow"

# Build changes
git commit -m "build: update webpack configuration"

# CI changes
git commit -m "ci: add GitHub Actions workflow"

# Revert a commit with refs to original commits
git commit -m "revert: let us never again speak of the noodle incident" \
  -m "Refs: 676104e, a215868"

# Multi-paragraph body with multiple footers
git commit -m "fix: prevent racing of requests" \
  -m "" \
  -m "Introduce a request id and a reference to latest request. Dismiss" \
  -m "incoming responses other than from latest request." \
  -m "" \
  -m "Remove timeouts which were used to mitigate the racing issue but are" \
  -m "obsolete now." \
  -m "" \
  -m "Reviewed-by: Alice" \
  -m "Refs: #123"
```

#### Benefits

Conventional Commits enables:
- Automatically generating CHANGELOGs
- Automatically determining a semantic version bump (based on the types of commits landed)
- Communicating the nature of changes to teammates, the public, and other stakeholders
- Triggering build and publish processes
- Making it easier for people to contribute to your projects, by allowing them to explore a more structured commit history

See [Basic Operations](references/02-basic-operations.md) for more on commits.

### Conventional Commits FAQ

**Q: How should I deal with commit messages in the initial development phase?**
A: Proceed as if you've already released the product. Someone (even fellow developers) is using your software and they'll want to know what's fixed, what breaks, etc.

**Q: Are the types in the commit title uppercase or lowercase?**
A: Any casing may be used, but it's best to be consistent. Types are case-insensitive by specification (except BREAKING CHANGE which MUST be uppercase).

**Q: What do I do if the commit conforms to more than one of the commit types?**
A: Make multiple commits whenever possible. Part of the benefit of Conventional Commits is its ability to drive you to make more organized commits and PRs.

**Q: Doesn't this discourage rapid development and fast iteration?**
A: It discourages moving fast in a disorganized way. It helps you be able to move fast long-term across multiple projects with varied contributors.

**Q: What do I do if I accidentally use the wrong commit type?**
A: 
- **Before merging/releasing:** Use `git rebase -i` to edit the commit history and correct the type.
- **After release:** The cleanup depends on your tools and processes. Consider reverting and re-committing with the correct type.

**Q: Do all my contributors need to use Conventional Commits?**
A: No! If you use a squash-based workflow, lead maintainers can clean up commit messages as they're merged. Many Git systems automatically squash commits from pull requests and present a form for entering the proper commit message.

**Q: How does this relate to SemVer?**
A: 
- `fix` type commits → PATCH releases (x.y.z)
- `feat` type commits → MINOR releases (0.y.z or x.0.0 if in pre-1.0.0)
- Commits with BREAKING CHANGE → MAJOR releases (x.0.0)

### Branching and Merging

```bash
# Create and switch to new branch
git checkout -b feature-name

# Or use git switch (Git 2.23+)
git switch -c feature-name

# Merge branch into current
git merge feature-name

# Rebase instead of merge
git rebase main
```

See [Branching and Merging](references/03-branching-merging.md) for workflows and conflict resolution.

### Remote Collaboration

```bash
# Fetch updates without merging
git fetch origin

# Pull and merge in one step
git pull origin main

# Push branch to remote
git push origin feature-name
```

See [Remote Operations](references/04-remote-operations.md) for collaboration patterns.

## Reference Files

- [`references/01-repository-basics.md`](references/01-repository-basics.md) - Initialize, clone, and configure repositories
- [`references/02-basic-operations.md`](references/02-basic-operations.md) - Add, commit, status, diff, log commands
- [`references/03-branching-merging.md`](references/03-branching-merging.md) - Branch management, merge, rebase, and conflict resolution
- [`references/04-remote-operations.md`](references/04-remote-operations.md) - Clone, fetch, pull, push, and remote management
- [`references/05-history-manipulation.md`](references/05-history-manipulation.md) - Reset, revert, cherry-pick, and reflog
- [`references/06-advanced-topics.md`](references/06-advanced-topics.md) - Stash, tags, blame, bisect, and submodules

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/git/`). All paths are relative to this directory.

## Common Patterns

### Feature Branch Workflow
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/my-feature

# Work on feature, commit changes
git add .
git commit -m "feat: implement user profile page"

# Push and create pull request
git push origin feature/my-feature
```

### Quick Fix Workflow
```bash
# Save work in progress
git stash

# Switch to main, pull latest
git checkout main
git pull origin main

# Make fix, commit, push
git checkout -b fix/quick-fix
# ... make changes ...
git add . && git commit -m "fix: resolve login timeout error"
git push origin fix/quick-fix
```

See [Branching and Merging](references/03-branching-merging.md) for more workflows.

## Troubleshooting

### Common Git Problems

| Problem | Solution |
|---------|----------|
| Wrong commit message | `git commit --amend -m "fix: correct typo in message"` |
| Accidentally committed wrong files | `git reset HEAD^` or see [History Manipulation](references/05-history-manipulation.md) |
| Merge conflicts | Edit conflicted files, `git add <file>`, then `git merge --continue` |
| Need to undo last commit | `git reset --soft HEAD~1` (keeps changes) or `git reset --hard HEAD~1` (discards) |
| Lost a branch | Check `git reflog` for recovery |

### Conventional Commits Troubleshooting

| Problem | Solution |
|---------|----------|
| Wrong commit type (before merge) | Use `git rebase -i` to edit the commit and change type |
| Wrong commit type (after release) | Depends on your tools; consider revert and re-commit with correct type |
| Need to mark as breaking change | Amend: `git commit --amend -m "feat!: breaking change description"` |
| Forgot BREAKING CHANGE footer | Amend: `git commit --amend -m "BREAKING CHANGE: description"` |
| Scope in wrong position | Should be before `!`: `feat(api)!: not feat!(api):` |
| Non-conforming commit landed | Not catastrophic; tools will simply skip that commit |

For detailed troubleshooting, see [History Manipulation](references/05-history-manipulation.md).
