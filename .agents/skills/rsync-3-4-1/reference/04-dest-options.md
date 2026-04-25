# Destination Options Reference

## Overview

Rsync provides three options that reference an alternate destination directory for comparison purposes. These are essential for creating sparse backups, flash cutover deployments, and space-efficient versioned snapshots.

## `--compare-dest=DIR`

Compare destination files against an additional hierarchy. If a file is found in DIR that matches the sender's file, it will NOT be transferred to the destination directory.

**Use case:** Sparse backup — only transfer files that have changed since the prior backup.

```bash
# Only transfer files that differ from the prior backup
rsync -av --compare-dest=/backups/2025-01-15/ /source/ /backups/2025-01-22/

# Multiple compare directories (searched in order)
rsync -av \
  --compare-dest=/backups/latest/ \
  --compare-dest=/backups/prior/ \
  /source/ /backups/new/
```

**Behavior:**
- If the file exists in DIR and matches, it is skipped (not transferred)
- If the file differs or is missing from DIR, it is transferred normally
- Files not in the source are still deleted from destination if `--delete` is used
- Relative paths are relative to the destination directory

## `--copy-dest=DIR`

Behaves like `--compare-dest`, but rsync also **copies** unchanged files found in DIR to the destination using a local copy (not a network transfer).

**Use case:** Flash cutover — prepare a new destination while leaving existing files intact.

```bash
# Copy changed files, locally copy unchanged ones from prior deployment
rsync -av --copy-dest=/deployments/v1/ /source/ /deployments/v2/
```

**Behavior:**
- Unchanged files are copied from DIR to destination (local operation)
- Changed files are transferred normally
- Useful for preparing a new release directory while the old one is still serving traffic

## `--link-dest=DIR`

Behaves like `--copy-dest`, but unchanged files are **hard linked** from DIR to the destination.

**Use case:** Space-efficient incremental backups — only changed files consume disk space.

```bash
# Create a new backup, hard-linking unchanged files from prior backup
PRIOR="/backups/2025-01-15"
NEW="/backups/$(date +%Y-%m-%d)"
mkdir -p "$NEW"
rsync -av --link-dest="$PRIOR" /source/ "$NEW/"
```

**Behavior:**
- Unchanged files become hard links to the files in DIR (zero additional disk space)
- Changed files are transferred normally
- Files must be identical in all preserved attributes (permissions, ownership, etc.) to link
- Best when copying into an empty destination hierarchy

## Comparison Table

| Feature | `--compare-dest` | `--copy-dest` | `--link-dest` |
|---------|-----------------|---------------|---------------|
| Unchanged files skipped | ✅ | ❌ (copied locally) | ❌ (hard linked) |
| Disk space for unchanged | 0 (skipped) | Full copy | Link (0 extra) |
| Network transfer | 0 (skipped) | 0 (local copy) | 0 (link) |
| Requires empty dest | No | Recommended | Best with empty |
| Works with --delete | Yes | Yes | Yes |
| Multiple dirs supported | ✅ (2.6.4+) | ✅ (2.6.4+) | ✅ (2.6.4+) |

## Advanced Patterns

### Daily Incremental Backup Chain

```bash
#!/bin/bash
# Create daily backups with hard-linked unchanged files
BACKUP_ROOT="/backups/daily"
SOURCE="/data/important"
DATE=$(date +%Y-%m-%d)
NEW_DIR="$BACKUP_ROOT/$DATE"

# Find the most recent prior backup
PRIOR=$(ls -1d "$BACKUP_ROOT"/[0-9]* 2>/dev/null | sort | tail -1)

mkdir -p "$NEW_DIR"

if [ -n "$PRIOR" ]; then
    echo "Linking from $PRIOR"
    rsync -a --link-dest="$PRIOR" "$SOURCE/" "$NEW_DIR/"
else
    echo "First full backup (no prior to link)"
    rsync -a "$SOURCE/" "$NEW_DIR/"
fi

# Keep only last 7 days
ls -1d "$BACKUP_ROOT"/[0-9]* 2>/dev/null | sort | head -n -7 | xargs rm -rf
```

### Flash Cutover Deployment

```bash
#!/bin/bash
# Prepare new deployment alongside current one
CURRENT="/var/www/deployments/current"
NEW="/var/www/deployments/$(date +%s)"

rsync -av --copy-dest="$CURRENT" /build/output/ "$NEW/"

# Verify the new deployment
if [ $? -eq 0 ]; then
    # Atomic swap
    ln -sfn "$NEW" /var/www/deployments/current
    echo "Deployed to $NEW"
fi
```

### Sparse Backup with Delete

```bash
#!/bin/bash
# Incremental backup that only contains changed files
# Prior backups serve as compare-dest for each run

PRIOR="/backups/prior_run"
CURRENT="/backups/current_run"

rsync -av --delete \
  --compare-dest="$PRIOR" \
  /source/ "$CURRENT/"
```

## Important Notes

1. **Relative paths** in DIR are relative to the destination directory
2. **Multiple directories** can be specified (up to 20 for `--link-dest`)
3. **Directory search order** — rsync searches the list in the order specified
4. **`--ignore-times` interaction** — when combined with `--link-dest`, no files will be linked because rsync only links identical files as a transfer substitute
5. **Non-super-user limitation** — prior to rsync 2.6.1, `--link-dest` could fail for non-root users when `-o` (preserve owner) was specified
