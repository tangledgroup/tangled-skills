# History Rewriting and Recovery

This reference covers Git history manipulation: interactive rebasing, cherry-picking, reset operations, merge conflict resolution, and recovery from failed operations using the reflog.

## Undoing Commits

### Soft Reset — Keep Changes Staged

```bash
git reset HEAD^                               # Undo last commit, keep changes staged
git reset --soft HEAD~3                       # Undo last 3 commits, keep all changes staged
```

The working tree and index remain unchanged. Use this when you want to restructure a commit before pushing.

### Mixed Reset — Keep Changes Unstaged (Default)

```bash
git reset HEAD^                               # Same as above but unstages the changes
git reset --mixed HEAD~2                      # Undo last 2 commits, keep changes in working tree
```

This is the default mode when no flag is specified. The index is updated to match HEAD, but the working tree is untouched.

### Hard Reset — Discard All Changes

```bash
git reset --hard HEAD^                        # Undo last commit AND discard all changes
git reset --hard origin/main                  # Reset to match remote exactly (DANGEROUS)
git reset --hard <commit>                     # Reset to any specific commit
```

**WARNING:** `--hard` discards uncommitted changes permanently. Only use when you're sure the changes are not needed.

### Amend Last Commit

```bash
git commit --amend                            # Edit the most recent commit message
git commit --amend -m "new message"           # Change message and/or staged files
git commit --amend --no-edit                  # Add/modify staged files without changing message
```

**Use case:** You forgot to add a file, or made a typo in the commit message. Only amend **local, unpushed** commits.

## Squashing Commits with Interactive Rebase

### Basic Squash

```bash
git rebase -i HEAD~5                          # Interactively rebase last 5 commits
```

An editor opens with each commit prefixed by `pick`. Change the command for commits you want to squash:

| Command | Effect |
|---------|--------|
| `pick` (or `p`) | Keep this commit as-is |
| `reword` (or `r`) | Keep commit but edit its message |
| `edit` (or `e`) | Stop at this commit for amending (add/remove files) |
| `squash` (or `s`) | Merge into previous commit, combine messages |
| `fixup` (or `f`) | Merge into previous commit, discard this message |
| `drop` (or `d`) | Remove this commit entirely |

**Example — squash last 3 commits into one:**
```
pick abc123 First commit
squash def456 Second commit
squash ghi789 Third commit
```

This combines all three into a single commit. The editor will open with all three messages combined, which you can edit down to a clean summary.

### Advanced Rebase Patterns

**Reorder commits:**
```
pick abc123 Third commit    # Move this line first
pick def456 First commit
pick ghi789 Second commit
```

**Edit a specific commit (e.g., to fix a typo):**
```
pick abc123 First commit
edit def456 Fix typo in function name
pick ghi789 Third commit
```

Git stops at the `edit` line. Make your changes, then:
```bash
git add <file>
git commit --amend --no-edit    # Replace the stopped commit
git rebase --continue           # Continue to next commits
```

**Drop (delete) a commit:**
```
pick abc123 First commit
drop def456 Unnecessary commit
pick ghi789 Third commit
```

## Cherry-Picking

Apply specific commits from one branch to another without merging the entire branch.

```bash
git cherry-pick <commit>                    # Apply single commit on top of current branch
git cherry-pick <sha1>..<sha2>              # Apply range of commits (exclusive start)
git cherry-pick <sha1>^..<sha2>             # Apply range of commits (inclusive start)
git cherry-pick -n <commit>                 # Cherry-pick without auto-committing
git cherry-pick --continue                  # Continue after resolving conflicts
git cherry-pick --abort                     # Abort cherry-pick, return to original state
```

**Use case:** A critical bug fix was committed to `main` and you need it on a feature branch. Or you want to apply a specific commit from another developer's branch.

## Merge Conflict Resolution

### Identifying Conflicts

```bash
git status                                  # Shows files with conflicts (both in merge and cherry-pick)
```

Conflicted files contain markers:
```
<<<<<<< HEAD
your version of the code
=======
incoming version of the code
>>>>>>> feature-branch
```

### Resolving Conflicts

1. **Open each conflicted file** and resolve the conflict markers manually
2. **Stage the resolved files:** `git add <file>` (or `git add .`)
3. **Continue the operation:**
   - For merge: `git commit` (creates merge commit) or `git merge --continue`
   - For rebase: `git rebase --continue`
   - For cherry-pick: `git cherry-pick --continue`

### Using a Merge Tool

```bash
git mergetool                                 # Open configured merge tool
git mergetool -t vimdiff                      # Use vimdiff as the merge tool
```

Configure your preferred tool in `.git/config`:
```ini
[mergetool "vscode"]
    cmd = code --wait --merge $REMOTE $LOCAL $BASE $MERGED
[merge]
    tool = vscode
```

### Rebase Conflicts

When a conflict occurs during `git rebase`:

1. Resolve conflicts in the files
2. Stage resolved files: `git add <file>`
3. Continue: `git rebase --continue`

**Abort a problematic rebase:**
```bash
git rebase --abort                            # Return to state before rebase started
```

## Recovering from Failed Operations

### The Reflog — Git's Safety Net

The reflog records every position HEAD has pointed to, including commits that are no longer reachable from any branch. It is your safety net for recovering from `git reset --hard`, failed rebases, and accidental deletions.

```bash
git reflog                                    # Show all HEAD movements
git reflog main                               # Reflog for a specific branch
git reflog show --all                         # All reflogs
```

**Recovery workflow after a failed rebase:**
```bash
git reflog BRANCHNAME                         # Find the commit before the rebase started
git reset --hard <commit>                     # Restore to that commit
```

**Recovery after `git reset --hard` mistake:**
```bash
git reflog                                    # Find the commit you lost
git reset --hard <commit>                     # Restore it
```

### Recovering Deleted Branches

```bash
git reflog                                    # Find the tip of the deleted branch
git branch recovered-branch <commit-sha>      # Recreate the branch at that point
```

## Safe vs Unsafe History Rewriting

### Safe (Local Only)

These operations are safe because they only affect local, unpushed history:

- `git commit --amend` on last local commit
- `git rebase -i` on local commits not yet pushed
- `git reset --hard` on working tree with unpushed changes
- `git cherry-pick` (adds commits, never removes)

### Unsafe (Shared/Remote)

**Never rewrite history that has been pushed to a shared remote.** Other developers will have divergent histories and force-pushing will cause their local repos to break.

Exceptions (with team coordination):
- Force-pushing after a successful interactive rebase on a **feature branch only you use**
- Amending your own commits before anyone else has pulled them

### Golden Rule

> If it has been pushed to a shared branch, do not rewrite it. Create new commits instead.

## Practical Recovery Scenarios

### Scenario 1: Accidentally Committed to Wrong Branch

```bash
# On wrong branch — undo the commit but keep changes
git reset HEAD^

# Switch to correct branch and apply
git switch correct-branch
git cherry-pick <commit-sha-from-reflog>
# Or simply: git stash, git switch, git stash pop
```

### Scenario 2: Need to Undo a Merge

```bash
# Find the parent commit before the merge
git reflog | grep "merge"
# Reset back to the pre-merge state
git reset --hard <pre-merge-commit>
```

### Scenario 3: Squash Recent Commits Before Pushing

```bash
git rebase -i HEAD~N                          # Where N = number of commits to squash
# Mark all but the first as 'squash' or 'fixup'
# Resolve any conflicts that arise
git rebase --continue
```

See [Version Control Workflows](../02-version-control-workflows.md) for merge and rebase basics.
See [Core Git Commands](../01-core-git-commands.md) for the `reset`, `restore`, and `log` command reference.
