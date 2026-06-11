---
name: git
description: Git version control. Use when the user mentions git, commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules, or any version control task. Covers straightforward workflows (add/commit/push) and advanced topics.
---

# git

Git workflow shorthand — describe what you want, not exact commands.

## Overview

Map natural descriptions to git operations. Use concise shorthand patterns instead of verbose command chains. All paths are relative to the repo root unless stated otherwise.

## Commit Messages

`acp` rephrases the user's description into a structured commit message before committing.

**First line:** [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) type and summary.
**Body (below first line):** [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) categories — describe what changed descriptively, grouped under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

```
<type>[optional scope]: <description>

### Added
- ...

### Changed
- ...

### Fixed
- ...
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Single-change commit (body optional):**
```
fix(auth): handle null session on login
```

**Multi-change commit (body required, uses Keep a Changelog categories):**
```
feat(profile): add avatar upload and settings page

### Added
- profile page with avatar upload
- user settings panel for theme and notifications

### Changed
- auth middleware now returns user preferences
```

**Breaking changes:** add `!` before `:` or `BREAKING CHANGE:` in footer.
**Scoped:** use optional scope for module/area (e.g., `feat(api)`, `fix(ui)`).

## Usage

### Start / Clone

```
clone <url>                    # git clone <url>
init                           # git init
init --bare                    # git init --bare (remote/bare repo)
```

### Stage / Commit / Push

```
add <files>                    # git add <files>
add -A                         # stage everything (new, modified, deleted)
commit "msg"                   # git commit -m "msg"
commit --amend                 # rewrite last commit message or add files
acp ["msg"]                    # fetch + merge/rebase (resolve conflicts), rephrase msg → Conventional Commit, then add -A && commit && push
push                           # git push
push --force-with-lease        # safe force push (rejects if remote has new commits)
push --set-upstream origin <br> # git push -u origin <br>
```

`acp` takes an optional natural-language description. Before committing:
1. **Fetch and sync** — pull latest from remote (merge or rebase depending on config)
2. **Resolve conflicts** — if merge/rebase conflicts arise, resolve them automatically
3. **Rephrase message** — convert description to Conventional Commit format
4. **Stage, commit, push** — `add -A`, commit with rephrased message, push

If no message given, infer one from the staged changes.

### Fetch / Pull

```
fetch                          # git fetch (download, don't merge)
pull                           # git pull (fetch + merge)
pull --rebase                  # git pull --rebase (fetch + rebase onto remote)
fetch --all --prune            # clean up stale remote tracking branches
```

### Branching

```
branch <name>                  # git branch <name>
checkout <name>                # git switch <name> (or git checkout <name>)
checkout -b <name>             # create and switch to new branch
checkout -- <files>            # discard working tree changes in files
merge <branch>                 # git merge <branch>
delete <branch>                # git branch -d <branch>
delete --force <branch>        # git branch -D <branch>
branches                       # list local branches
branches -r                    # list remote tracking branches
```

### Inspect

```
status                         # git status
log                            # git log --oneline --graph --all
log <n>                        # last n commits
diff                           # unstaged changes
diff --staged                  # staged but not committed
show <commit>                  # show commit details
show :<file>                   # show file content at current tree (staged)
blame <file>                   # git blame <file> (line-by-line authorship)
who <file>                     # short: git log -1 --format='%an <%ae>' -- <file>
```

### Tags

```
tag <name>                     # lightweight tag
tag -a <name> -m "msg"         # annotated tag
push --tags                    # push tags to remote
delete-tag <name>              # git tag -d <name>
push --delete origin <name>    # delete remote tag
```

### Remote

```
remotes                        # git remote -v
remote add <name> <url>        # add remote
remote set-url <name> <url>    # change remote url
remote rename <old> <new>      # rename remote
```

### Common Workflows

**Quick fix on main:**
```
checkout main
pull
acp "fixed the login crash when token expires"
# → rephrases to: fix(auth): handle expired token gracefully
```

**Feature branch:**
```
checkout -b feat/<name>
... work ...
acp "add user profile page with avatar upload"
# → rephrases to: feat(profile): add user profile page with avatar upload
```

**Clean up after merge:**
```
checkout main
pull
delete <merged-branch>
fetch --all --prune
```

**Undo local changes:**
```
checkout -- <files>            # discard unstaged file changes
reset HEAD~1                   # uncommit last commit (keep changes staged)
reset --hard HEAD~1            # drop last commit entirely
```

## Gotchas

- **`push --force` is dangerous** — use `--force-with-lease` which rejects if others pushed new commits. Only force when you own the branch or confirmed with teammates.
- **`reset --hard` destroys uncommitted work** — stash or commit first if you might need the changes.
- **Detached HEAD** happens after checking out a commit hash or tag. Create a branch immediately: `checkout -b <name>`.
- **Merge conflicts block commits** — resolve all `<<<<<<<` markers, then `add <resolved-files>` and complete the commit.
- **`pull` defaults to merge** — use `pull --rebase` for linear history, or set globally: `git config --global pull.rebase true`.
- **Untracked files survive `reset --hard`** — they are not tracked, so reset doesn't touch them. Use `clean -fd` to remove them (irreversible).
- **Submodules need explicit init/update** — cloning a repo with submodules requires `submodule update --init --recursive`.
- **`stash pop` fails on conflicts** — stash still exists after failed pop. Resolve conflicts, then `stash drop`.

## References

Detailed topics loaded on demand:

- [Worktrees](references/01-worktrees.md) — parallel working directories on one repo
- [Request Pull](references/02-request-pull.md) — generate pull request URLs for bare repos and email workflows
- [Rebase Strategies](references/03-rebase-strategies.md) — interactive rebase, merge vs rebase, when to use each
- [Stash / Reset / Revert](references/04-undo-operations.md) — detailed undo patterns, cherry-pick, revert
- [Submodules](references/05-submodules.md) — adding, updating, migrating submodules
- [Bisect and Debugging](references/06-bisect-debugging.md) — bisect, blame, log search, finding regressions
- [Conventional Commits](references/07-conventional-commits.md) — types, scopes, breaking changes, rephrasing guide
- [Keep a Changelog](references/08-keep-a-changelog.md) — categories, commit body format, CHANGELOG.md structure
- [Semantic Versioning](references/09-semver.md) — MAJOR.MINOR.PATCH rules, pre-release, bump mapping from commit types
