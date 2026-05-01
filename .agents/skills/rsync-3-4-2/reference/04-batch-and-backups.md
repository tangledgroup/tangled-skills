# Batch Mode and Incremental Backups

## Batch Mode

Batch mode records all the information needed to apply the same set of updates to multiple identical destination systems. This avoids repeating file status checks, checksums, and data block generation for each target.

### Creating a Batch File

```bash
rsync --write-batch=foo -a host:/source/dir/ /adest/dir/
```

This syncs `/source/dir/` to `/adest/dir/` and records the update information in files named `foo` (the batch data) and `foo.sh` (a helper shell script).

The `--only-write-batch=FILE` option creates the batch without updating the destination, allowing you to transport changes via other means:

```bash
rsync --only-write-batch=foo -a /source/dir/ /adest/dir/
```

### Applying a Batch File

Using the generated shell script:

```bash
scp foo* remote:
ssh remote ./foo.sh /bdest/dir/
```

Or reading from stdin:

```bash
ssh remote rsync --read-batch=- -a /bdest/dir/ <foo
```

### Batch Mode Caveats

- The destination tree must be **identical** to the one used when creating the batch
- If a difference is encountered, the update may be discarded with a warning or error
- Safe to re-run if interrupted
- Use `--ignore-times` (`-I`) when reading to force batch updates regardless of file size/date
- The rsync version on all destinations must be at least as new as the creating version
- Use `--protocol=NUM` to create batches compatible with older rsync
- Batch files changed format in version 2.6.3 (incompatible across that boundary)
- When reading a batch, certain options are forced to match the batch file
- Filter/exclude options are not needed unless `--delete` is specified

### Multicast Deployment

Batch mode is designed for multicast transport — the same batch data can be sent to many hosts simultaneously instead of individually, saving bandwidth.

## Incremental Backups with `--link-dest`

The `--link-dest=DIR` option hardlinks to files in DIR when they are unchanged. This creates space-efficient incremental backups where unchanged files share disk blocks via hard links.

```bash
# Create today's backup, hard-linking unchanged files from yesterday
rsync -a --link-dest=/backup/yesterday /source/ /backup/today/

# Rotate
mv /backup/today /backup/yesterday
```

**Important:** The `--link-dest` directory must be specified as an absolute path or a path relative to the destination directory.

### Continuing Interrupted Backups

When resuming a `--link-dest` backup that was interrupted, use `--ignore-existing` to avoid breaking hard links on already-transferred files:

```bash
rsync -a --link-dest=../current --ignore-existing /source/ /backup/new-day/
```

## Sparse Backups with `--compare-dest`

The `--compare-dest=DIR` option compares destination files against DIR. If an identical file is found in DIR, the file is **not** transferred to the destination. This creates a sparse backup containing only changed files:

```bash
# Create sparse backup — only files that differ from last week
rsync -a --compare-dest=/backup/last-week /source/ /backup/this-week/
```

Multiple `--compare-dest` directories are searched in order. If a match differs only in attributes, a local copy is made and attributes updated.

## Full Rotation with `--copy-dest`

The `--copy-dest=DIR` option behaves like `--compare-dest` but also copies unchanged files from DIR to the destination using local copies:

```bash
# Create full backup, copying unchanged files from previous backup
rsync -a --copy-dest=/backup/previous /source/ /backup/current/
```

This is useful for flash-cutover strategies where you build a new backup alongside the old one.

## Backup with `--backup` and `--backup-dir`

The `--backup` option creates backup copies of files that would otherwise be overwritten:

```bash
# Back up modified files to a dated directory
rsync -a --backup --backup-dir=/backup/$(date +%Y%m%d) /source/ /dest/
```

Without `--backup-dir`, backups use the suffix specified by `--suffix` (default: `~`).

### 7-Day Rotating Incremental Backup

From the official rsync examples, a complete rotating backup script:

```bash
#!/bin/sh
BDIR=/home/$USER
EXCLUDES=$HOME/cron/excludes
BSERVER=backup-host
export RSYNC_PASSWORD=XXXXXX

BACKUPDIR=$(date +%A)
OPTS="--force --ignore-errors --delete-excluded --exclude-from=$EXCLUDES \
      --delete --backup --backup-dir=/$BACKUPDIR -a"

# Clear last week's incremental directory
mkdir -p $HOME/emptydir
rsync --delete -a $HOME/emptydir/ $BSERVER::$USER/$BACKUPDIR/
rmdir $HOME/emptydir

# Actual transfer
rsync $OPTS $BDIR $BSERVER::$USER/current
```

This creates:
- `current/` — full current backup
- `Monday/`, `Tuesday/`, etc. — incremental changes for each day

## Atomic Updates with `--delay-updates`

The `--delay-updates` option places temporary files in a holding directory (`.~tmp~` by default) until the end of the transfer, then renames all files into place in rapid succession:

```bash
rsync -a --delay-updates /source/ /dest/
```

This makes file updating more atomic. All updated files appear simultaneously at the end rather than one at a time.

- Conflicts with `--inplace` and `--append`
- Uses more memory on the receiver (one bit per file)
- Requires enough free disk space for an additional copy of all updated files
- If `--partial-dir` is specified, that directory is used instead of `.~tmp~`

The "atomic-rsync" Python script in rsync's support directory provides an even more atomic algorithm using `--link-dest` and a parallel hierarchy.

## Fuzzy Basis Files

The `--fuzzy` (`-y`) option looks for a basis file when the destination file is missing:

```bash
rsync -a --fuzzy /source/ /dest/
```

It searches the same directory for files with identical size and modification time, or similarly-named files. This is useful when files have been renamed or moved within the destination.

Repeating `--fuzzy` also scans alternate destination directories (`--compare-dest`, `--copy-dest`, `--link-dest`).

Note: `--delete` might remove potential fuzzy-match files. Use `--delete-after` or filename exclusions to prevent this.

## Partial Transfer Recovery

For large transfers that may be interrupted, use partial file recovery:

```bash
# Keep partial files in place
rsync -a --partial /large/source/ /dest/

# Better: use a staging directory
rsync -a --partial-dir=.rsync-tmp /large/source/ /dest/

# Shorthand with progress
rsync -aP /large/source/ /dest/
```

The `--partial-dir` with a relative path auto-creates the directory and excludes it from the transfer. On resume, rsync uses the partial file as data to speed up transfer completion.

## Moving Files

The `--remove-source-files` option removes source files after successful transfer:

```bash
rsync -aiv --remove-source-files rhost:/tmp/{file1,file2}.c ~/src/
```

Only use on quiescent files. Ensure files are fully written before rsync sees them — write to a staging directory first, then rename into the source directory. Use naming conventions like `*.new` with `--exclude='*.new'` if direct writing is unavoidable.

Starting with 3.1.0, rsync skips removal if the file's size or modify time changed during transfer. Starting with 3.2.6, local copies prevent self-deletion when source and destination are the same path.

## Memory Management for Large Transfers

For millions of files:

- Use rsync 3.0.0+ for incremental recursion (builds file list in chunks)
- Use `--delete-delay` instead of `--delete-after` (the latter forces full file list in memory)
- Increase `--max-alloc=SIZE` if needed (default ~1GB per allocation)
- Break transfers into smaller chunks by subdirectory using `--relative` or exclude rules
