# Delete Modes Reference

## Overview

Rsync provides several delete modes that control when and how files are removed from the destination during a sync operation. Choosing the right mode is critical for data safety.

## Delete Mode Comparison

| Mode | When Deletions Happen | Memory Usage | Safety |
|------|----------------------|--------------|--------|
| `--delete-before` | Before transfer begins | Higher (needs full file list) | Safe |
| `--delete-during` (default for `--delete`) | During transfer | Lower (incremental) | Moderate |
| `--delete-delay` | Find during, delete after | Lower (incremental) | Safe |
| `--delete-after` | After transfer completes | Higher (needs full file list) | Safest |

## Detailed Options

### `--delete`

Alias for `--delete-during`. Deletes extraneous files from the destination. This is the **default delete mode** when `--delete` is used with incremental recursion (rsync 3.0.0+).

```bash
# Mirror source to destination, removing extra files at dest
rsync -av --delete /source/ /dest/
```

### `--delete-before`

Receiver deletes files **before** the transfer begins. Requires scanning the full file list upfront (disables incremental recursion).

```bash
# Safe: all deletions happen before any data is sent
rsync -av --delete-before /source/ /dest/
```

### `--delete-during`

Receiver deletes files **during** the transfer. This is the default when using `--delete` with modern rsync and incremental recursion enabled.

```bash
# Default behavior of --delete
rsync -av --delete /source/ /dest/
```

### `--delete-delay`

Finds files to delete during transfer, but deletes them **after** the transfer completes. Best balance of memory efficiency and safety.

```bash
# Find deletions during transfer, apply after
rsync -av --delete-delay /source/ /dest/
```

### `--delete-after`

Receiver deletes files **after** the transfer completes. Safest mode — if the transfer fails, no files are deleted.

```bash
# Safest: nothing is deleted until transfer succeeds
rsync -av --delete-after /source/ /dest/
```

## Delete-Related Safety Options

### `--max-delete=NUM`

Don't delete more than NUM files. Useful for testing with safety limits.

```bash
# Don't delete more than 100 files
rsync -av --max-delete=100 /source/ /dest/
```

### `--force`

Force deletion of directories even if not empty. Required when removing non-empty directories during a transfer.

```bash
rsync -av --force --delete /source/ /dest/
```

### `--delete-excluded`

Also delete excluded files from the destination. Without this, excluded files are simply skipped.

```bash
# Remove .tmp files from dest even though they're excluded from transfer
rsync -av --exclude='*.tmp' --delete-excluded /source/ /dest/
```

### `--ignore-errors`

Delete even if there are I/O errors during the transfer. Without this, deletions are skipped if any I/O error occurs.

```bash
# Continue with deletions even after I/O errors
rsync -av --delete --ignore-errors /source/ /dest/
```

### `--partial`

Keep partially transferred files. Useful for interrupted transfers — you can resume later.

```bash
rsync -av --partial /source/ /dest/
```

### `--partial-dir=DIR`

Put a partially transferred file into a separate directory instead of leaving it in the destination with an unusual name.

```bash
# Partial files go to .partial/ instead of filename.<random>
rsync -av --partial-dir=.partial /source/ /dest/
```

### `--delay-updates`

Put all updated files into place at the end of the transfer. Provides atomicity — partial updates don't leave the destination in an inconsistent state.

```bash
rsync -av --delay-updates /source/ /dest/
```

## Deleting New Files on Receiver

### `--delete-missing-args`

Delete missing source arguments from the destination. Useful when a file is removed from the source argument list but still exists at the destination.

```bash
# Remove files from dest that aren't in the source arg list
rsync -av --delete-missing-args /source/file1 /source/file2 /dest/
```

### `--ignore-missing-args`

Ignore missing source arguments without error. Opposite of delete-missing-args.

## Best Practices

1. **Always test with `--dry-run` first:**
   ```bash
   rsync -avn --delete /source/ /dest/
   ```

2. **Use `--itemize-changes` to see what will change:**
   ```bash
   rsync -avni --delete /source/ /dest/
   ```

3. **For production backups, prefer `--delete-after`:**
   ```bash
   rsync -av --delete-after /source/ /dest/
   ```

4. **Use `--max-delete` for safety during initial testing:**
   ```bash
   rsync -av --delete --max-delete=10 /source/ /dest/
   ```

5. **Combine with `--backup` for extra safety:**
   ```bash
   rsync -avb --delete /source/ /dest/
   # Pre-existing files are backed up with ~ suffix before deletion
   ```

6. **Use `--backup-dir` for incremental backup rotation:**
   ```bash
   rsync -avb --delete --backup-dir="/backups/$(date +%A)" /source/ /dest/
   ```
