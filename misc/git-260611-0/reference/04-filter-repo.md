# git filter-repo — History Rewriting

## Contents
- Overview
- Prerequisites and Installation
- Safety Model
- Workflow
- Path Filtering
- Content Filtering
- Ref and Tag Renaming
- Name/Email Rewriting
- Commit Message Rewriting
- Parent Rewriting and Grafts
- Callbacks (Python Snippets)
- Sensitive Data Removal
- Analysis Mode
- Partial History Rewrites
- Output Files
- Limitations

## Overview

`git filter-repo` is the recommended replacement for `git filter-branch`. It rewrites entire repository history by filtering commits, trees, tags, and blobs, then deletes the original history. Recommended by the git project itself — `git filter-branch` is deprecated due to performance issues (orders of magnitude slower) and silent corruption risks.

Key advantages over alternatives:
- **Speed**: Multiple orders of magnitude faster than `filter-branch`
- **Safety**: Detects non-fresh clones and aborts (use `--force` to override)
- **Auto-shrink**: Removes old objects and repacks after filtering
- **Commit hash rewriting**: Updates abbreviated hashes referenced in commit messages
- **Empty commit pruning**: Removes commits that become empty from filtering (preserves intentionally empty commits)
- **Degenerate merge pruning**: Handles merges that lose parents during filtering

## Prerequisites and Installation

Requires git >= 2.36.0 and python3 >= 3.6.

Single-file Python script. Install by placing `git-filter-repo` in `$PATH`, or use pip:

```bash
pip install git-filter-repo
```

On many systems, available via package managers. The core logic is a single file — no dependencies beyond Python 3 standard library and git.

## Safety Model

filter-repo refuses to run unless the repository appears to be a **fresh clone**. This prevents accidental data loss from rewriting local-only history. The check verifies ~12 conditions that are true of brand new clones.

Override with `--force`, but only when you understand the irreversible consequences. Never habitually add `--force`.

After filtering, `origin` remote is removed to prevent accidentally pushing rewritten history back over the original. To push to a new location:

```bash
git remote add origin <new-url>
git push --force --branches --tags --prune
```

## Workflow

Standard workflow for history rewriting:

1. **Clone** the repository (use `--no-local` for local filesystem clones)
2. **(Optional)** Run `git filter-repo --analyze` to inspect repo before filtering
3. **Determine target** — push to a new repo URL (recommended) or back to original (sensitive data only)
4. **Run filter-repo** with desired options
5. **Push** rewritten history to new location
6. **(Optional)** Verify with `git filter-repo --analyze` again

If anything goes wrong, delete the clone and restart. Multiple sequential filter-repo invocations are supported for complex rewrites.

## Path Filtering

### Select paths to keep

```bash
# Keep specific files and directories
git filter-repo --path README.md --path src/ --path docs/guides/

# Keep by glob pattern (quotes prevent shell expansion)
git filter-repo --path-glob '*.py'

# Keep by regex (Python re syntax)
git filter-repo --path-regex '^.*/.*/[0-9]{4}-[0-9]{2}-[0-9]{2}\.txt$'

# Keep by basename only (any directory)
git filter-repo --use-base-name --path README.md --path Makefile
```

### Invert selection (remove specific paths)

```bash
# Remove specific files from all history
git filter-repo --invert-paths --path .env --path secrets/

# Remove all .DS_Store files
git filter-repo --invert-paths --path '.DS_Store' --use-base-name
```

### Rename paths

```bash
# Rename a directory
git filter-repo --path-rename olddir/:newdir/

# Merge two directories into one
git filter-repo --path-rename cmds/:tools/ --path-rename src/scripts/:tools/

# Handle collisions — rename conflicting file first, then directories
git filter-repo --path-rename cmds/run.sh:tools/do_run.sh \
                --path-rename cmds/:tools/ \
                --path-rename src/scripts/:tools/
```

Note: `--path-rename` does not filter — it only renames paths already selected by `--path`. If you rename and want to keep the renamed path, also include it in `--path`.

### Directory shortcuts

```bash
# Extract a subdirectory as new root (module/ becomes ./)
git filter-repo --subdirectory-filter module/

# Move everything into a subdirectory
git filter-repo --to-subdirectory-filter my-module/
```

### Many paths from file

Use `--paths-from-file` for long lists. File format:

```
# Comments and blank lines ignored
README.md
src/
glob:*.py
regex:^.*/config\.yaml$
tools/==>scripts/
regex:(.*)/([^/]*)\.text$==>\2/\1.txt
```

```bash
git filter-repo --paths-from-file paths.txt
```

## Content Filtering

### Strip large files

```bash
# Remove all blobs bigger than 10MB
git filter-repo --strip-blobs-bigger-than 10M
```

Suffixes: K, M, G.

### Strip specific blob IDs

```bash
# List one git object hash per line in a file
git filter-repo --strip-blobs-with-ids blob-ids.txt
```

### Replace text in file contents

Create an expressions file (one rule per line):

```
# Literal — replace with ***REMOVED*** by default
p455w0rd

# Literal with custom replacement
foo==>bar

# Glob match — blank replacement removes the line
glob:*666*==>

# Regex with word boundaries
regex:\bdriver\b==>pilot

# Explicit literal prefix
literal:MM/DD/YYYY==>YYYY-MM-DD

# Regex with capture groups
regex:([0-9]{2})/([0-9]{2})/([0-9]{4})==>\3-\1-\2
```

```bash
git filter-repo --replace-text expressions.txt
```

Without `==>`, default replacement is `***REMOVED***`. Multiple matches per file are all replaced. Regex uses Python `re` syntax — add `(?m)` for MULTILINE mode where `^`/`$` match line boundaries.

## Ref and Tag Renaming

```bash
# Prefix all tags
git filter-repo --tag-rename '':'my-module-'

# Rename tag prefix
git filter-repo --tag-rename foo:bar
# foo-1.2.3 → bar-1.2.3
```

Either side of the colon can be empty.

## Name/Email Rewriting

Use a mailmap file (git-shortlog format):

```
# Map old name/email to new
New Name <new@email.com> Old Name <old@email.com>
<new@email.com> <old@email.com>
New Name <new@email.com> <old@email.com>
```

```bash
git filter-repo --mailmap my-mailmap

# Or use existing .mailmap file in repo root
git filter-repo --use-mailmap
```

If the mailmap file is tracked in git, only the current version is used (not historical versions).

## Commit Message Rewriting

Same syntax as `--replace-text`:

```bash
git filter-repo --replace-message expressions.txt
```

By default, abbreviated commit hashes in messages are rewritten to point to new post-rewrite hashes. Use `--preserve-commit-hashes` to disable this. By default, non-UTF-8 commit messages are re-encoded to UTF-8. Use `--preserve-commit-encoding` to preserve original encoding.

## Parent Rewriting and Grafts

Replace one commit with another in the parent chain:

```bash
# Make all children of $commit_A use $commit_B as parent instead
git replace $commit_A $commit_B
git filter-repo --proceed
```

Graft a commit onto different parent(s):

```bash
git replace --graft $commit_A $new_parent_or_parents
git filter-repo --proceed
```

`--proceed` is required since no filtering arguments are specified. Existing `refs/replace/` refs are automatically baked into permanent history during the rewrite.

Control replace-ref behavior with `--replace-refs`:
- `update-no-add` (default): update existing replace refs, don't add new ones
- `update-and-add`: also create replace refs for all rewritten commits

## Callbacks (Python Snippets)

For advanced filtering, specify Python code bodies on the command line. All values are **bytestrings** (prefix with `b""`), not strings.

### Convenience callbacks (return a value)

```bash
# Fix name typos
git filter-repo --name-callback 'return name.replace(b"Wiliam", b"William")'

# Fix email domains
git filter-repo --email-callback 'return email.replace(b".cm", b".com")'

# Prefix all branch names
git filter-repo --refname-callback '
  rdir, rpath = os.path.split(refname)
  return rdir + b"/prefix-" + rpath'

# Add Signed-off-by to commits missing it
git filter-repo --message-callback '
  if b"Signed-off-by:" not in message:
    message += b"\nSigned-off-by: Me <me@self.com>"
  return re.sub(b"[Ee]-?[Mm][Aa][Ii][Ll]", b"email", message)'

# Remove files in nested src/ dirs, rename tools/ → scripts/misc/
git filter-repo --filename-callback '
  if b"/src/" in filename:
    return None
  elif filename.startswith(b"tools/"):
    return b"scripts/misc/" + filename[6:]
  else:
    return filename'
```

### Raw object callbacks (modify in place, no return)

```bash
# Remove blobs bigger than 25 bytes, or replace text in small ones
git filter-repo --blob-callback '
  if len(blob.data) > 25:
    blob.skip()
  else:
    blob.data = blob.data.replace(b"Hello", b"Goodbye")
  '

# Filter file changes in commits
git filter-repo --commit-callback '
  commit.file_changes = [
      change for change in commit.file_changes
      if not (change.mode == b"100755" and
              change.filename.count(b"6") == 3)]
  for change in commit.file_changes:
    if change.filename.endswith(b".sh"):
      change.mode = b"100755"
  '

# Omit tags by specific tagger
git filter-repo --tag-callback '
  if tag.tagger_name == b"Jim Williams":
    tag.skip()
  else:
    tag.message += b"\n\nTagged by %s" % tag.tagger_email'
```

### file-info callback (filename + mode + contents)

For filtering that depends on both filename and content:

```bash
# Only apply --replace-text rules to .config files, rename to .cfg
git filter-repo --file-info-callback '
  if not filename.endswith(b".config"):
    return (filename, mode, blob_id)
  new_filename = filename[0:-7] + b".cfg"
  contents = value.get_contents_by_identifier(blob_id)
  new_contents = value.apply_replace_text(contents)
  new_blob_id = value.insert_file_with_contents(new_contents)
  return (new_filename, mode, new_blob_id)'
```

Available helpers on `value`:
- `get_contents_by_identifier(blob_id)` → bytestring
- `get_size_by_identifier(blob_id)` → int
- `insert_file_with_contents(contents)` → blob_id
- `is_binary(contents)` → bool
- `apply_replace_text(contents)` → new_contents (applies --replace-text rules)
- `data` — dict for caching results across calls

File modes: `b"100644"` (regular), `b"100755"` (executable), `b"120000"` (symlink), `b"160000"` (submodule).

## Sensitive Data Removal

When removing credentials, tokens, or secrets from history:

1. **Revoke the credential first** — history rewriting won't prevent use of already-exposed secrets
2. Tell collaborators to stop working during cleanup
3. Use `--sensitive-data-removal` flag for extra tracking

```bash
# Clone fresh, then filter
git clone --no-local <repo-url> clean-repo
cd clean-repo
git filter-repo --sensitive-data-removal --invert-paths --path .env --path secrets/
```

Verify removal:
```bash
git log --all --name-status -- ${PROBLEMATIC_FILE}
git log -S"${SECRET_STRING}" --all -p --
```

Push back to origin (replaces all refs):
```bash
git remote add origin <original-url>
git push --force --mirror origin
```

Note: Some forges block force-pushing certain refs (`refs/changes/*`, `refs/pull/*`). Follow forge-specific docs for full cleanup.

For colleagues with existing clones, easiest option is delete and reclone. If not possible, they must:
1. Delete all tags, then `git fetch --prune --tags`
2. Rebase their branches on new history
3. `git reflog expire --expire=now --all`
4. `git gc --prune=now`
5. Verify with `git cat-file -t ${HASH_OF_FIRST_CHANGED_COMMIT}` (should return fatal error)

Do not have colleagues run the same filter-repo commands — they'll get different hashes and create duplicate history.

## Analysis Mode

Run `--analyze` to generate reports in `.git/filter-repo/analysis/`:

- `path-deleted-sizes.txt` — paths sorted by total size across history
- `directory-deleted-sizes.txt` — same, aggregated by directory
- `extension-deleted-sizes.txt` — same, by file extension
- `blob-sizes-by-path.txt` — blob sizes per path
- `renames.txt` — detected renames in history

Useful for identifying what to filter, or verifying a previous filter worked:

```bash
git filter-repo --analyze
# Review .git/filter-repo/analysis/path-deleted-sizes.txt
# Then run actual filter
git filter-repo --strip-blobs-bigger-than 10M
# Re-analyze to verify
git filter-repo --analyze
```

## Partial History Rewrites

Limit rewriting to specific branches or commit ranges using `--refs`. Implies `--partial`, which disables auto-shrink and origin removal:

```bash
# Only rewrite master branch
git filter-repo --invert-paths --path extraneous.txt --refs master

# Only rewrite last 3 commits on master
git filter-repo --invert-paths --path extraneous.txt --refs master~3..master
```

Use `--source` and `--target` to read from one repo and write to another (also implies `--partial`, but avoids mixing old/new history since they're in different repos):

```bash
git filter-repo --source /path/to/source.git --target /path/to/target.git --path src/
```

## Output Files

After each run, `.git/filter-repo/` contains:

- `commit-map` — old and new commit hash mappings (header: "old" → "new")
- `ref-map` — old and new ref mappings with ref names
- `changed-refs` — subset of refs where old ≠ new
- `first-changed-commits` — first commit(s) affected by the rewrite
- `already_ran` — marker that filter-repo has been used (bypasses fresh clone check on subsequent runs)
- `suboptimal-issues` — notes about hash rewriting failures or merge-to-non-merge conversions
- `original_lfs_objects` / `orphaned_lfs_objects` — LFS object lists (with `--sensitive-data-removal`)

## Limitations

### Inherited from fast-export/fast-import
- Extended commit headers are stripped
- Commit/tag signatures are removed (signed tags become annotated)
- Tags of trees are not supported
- Annotated/signed tags outside `refs/tags/` namespace are mangled
- Commits without authors get committer as author
- Tags without taggers get fake taggers
- Works with exact file contents, not patches (can't undo a single commit's changes)

### Commit hash rewriting
- Hashes in messages may not update if: hash doesn't exist in old repo, commit was pruned, or abbreviated hash is ambiguous
- Failures are noted in `.git/filter-repo/suboptimal-issues`

### Empty/degenerate pruning
- Pruning empty commits can convert merges to non-merges (kept if they have file changes)
- Intentionally empty commits (e.g., for versioning) are preserved
- Only commits that **become** empty are pruned, not those that **started** empty

### Not reversible
filter-repo is designed for one-shot conversions. Most rewrites throw away information and cannot be undone. If you need reversibility, consider other approaches.
