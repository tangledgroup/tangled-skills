# Common Use Cases & Patterns

## Basic Copy Operations

```bash
# Local copy (like cp -a)
rsync -av source/ destination/

# Remote pull (download from server)
rsync -avz user@server:/path/to/data/ /local/dest/

# Remote push (upload to server)
rsync -avz /local/source/ user@server:/remote/dest/

# Using SSH with custom key
rsync -avz -e 'ssh -i ~/.ssh/custom_key' user@host:/data/ /local/

# Verbose listing of remote files
rsync -avz user@host::module/
```

## Backup Scenarios

### Incremental Backup with Rotating Snapshots

```bash
#!/bin/bash
# Daily rotating incremental backup
BACKUP_HOST="backup-server"
MODULE="backups"
DATE=$(date +%Y-%m-%d)
DAY_NAME=$(date +%A)  # Monday, Tuesday, etc.

# Create timestamped snapshot
rsync -av --delete \
    --backup --backup-dir="/$DAY_NAME" \
    --exclude='*.tmp' --exclude='.cache/' \
    /home/user/ "${BACKUP_HOST}:${MODULE}/user/current/"

# Clean old snapshots (keep last 7 days)
find /backups -maxdepth 1 -type d -mtime +7 -exec rm -rf {} +
```

### Hard-Linked Snapshots (Space-Efficient)

```bash
#!/bin/bash
# Create space-efficient daily snapshots using hard links
SNAPSHOTS="/backups/snapshots"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d 'yesterday' +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

# First snapshot: full copy
if [ ! -d "$SNAPSHOTS/$TODAY" ]; then
    rsync -a /data/ "$SNAPSHOTS/$TODAY/"
else
    # Subsequent snapshots: hard-link unchanged files
    rsync -a --link-dest="../$YESTERDAY" /data/ "$SNAPSHOTS/$TODAY/"
fi
```

### Mirror to Remote Server

```bash
#!/bin/bash
# Mirroring with change detection (saves server bandwidth)
REMOTE="mirror.example.com"
MODULE="pub"

# Check if anything changed first
rsync -az --itemize-changes "$REMOTE::$MODULE/ChangeLog" /tmp/ChangeLog.local 2>/dev/null

if [ ! -f /tmp/ChangeLog.local ]; then
    rsync -az "$REMOTE::$MODULE/ChangeLog" /tmp/
fi

# Only sync if changed
sum1=$(md5sum /tmp/ChangeLog.local | awk '{print $1}')
sum2=$(ssh "$REMOTE" "md5sum /srv/mirror/$MODULE/ChangeLog" | awk '{print $1}')

if [ "$sum1" != "$sum2" ]; then
    rsync -az --delete --force \
        --exclude='*.tmp' --exclude='.svn/' \
        "$REMOTE::$MODULE/" /local/mirror/
fi
```

### 7-Day Rotating Incremental Backup

```bash
#!/bin/sh
# From the official rsync examples page
BDIR=/home/$USER
EXCLUDES=$HOME/cron/excludes
BSERVER=backup-server

export RSYNC_PASSWORD=yourpassword

BACKUPDIR=$(date +%A)  # Day of week
OPTS="--force --ignore-errors --delete-excluded \
      --exclude-from=$EXCLUDES --delete \
      --backup --backup-dir=/$BACKUPDIR -a"

# Clear last week's incremental directory
[ -d $HOME/emptydir ] || mkdir $HOME/emptydir
rsync --delete -a $HOME/emptydir/ $BSERVER::$USER/$BACKUPDIR/
rmdir $HOME/emptydir

# Do the actual transfer
rsync $OPTS $BDIR $BSERVER::$USER/current
```

## Synchronization Patterns

### Keep Two Directories in Sync (Bidirectional Concept)

```bash
# rsync is fundamentally one-way. For bidirectional sync, run twice:
rsync -av --delete source/ dest/
rsync -av --delete dest/ source/
# Or use third-party tools like syncthing or unison for true bidirectional
```

### Selective Sync with Include/Exclude

```bash
# Only sync specific file types
rsync -avz --include='*.py' --include='*/' --exclude='*' src/ dest/

# Exclude common patterns
rsync -avz \
    --exclude='*.pyc' --exclude='__pycache__/' \
    --exclude='.git/' --exclude='node_modules/' \
    --exclude='*.swp' --exclude='.DS_Store' \
    src/ dest/

# Include everything except large files
rsync -avz --max-size='100M' src/ dest/

# Exclude from a file
rsync -avz --exclude-from=.gitignore src/ dest/
```

### Partial Transfer Recovery

```bash
# Continue interrupted transfers
rsync -avz --partial --progress user@host:/data/ /local/dest/

# Store partial files in a dedicated directory
rsync -avz --partial-dir=.rsync-partial /src/ /dest/
```

### Bandwidth-Limited Transfer

```bash
# Limit to 500 KB/s
rsync -avz --bwlimit=500 src/ dest/

# Schedule during off-hours with rate limit
rsync -avz --bwlimit=1000 --stop-after=480 /data/ user@remote:/backup/
# Runs for max 8 hours (480 minutes)
```

### Dry Run & Preview

```bash
# See what would be transferred without doing it
rsync -avn src/ dest/

# See detailed reasons why files would be updated
rsync -avni src/ dest/

# Show itemized changes (first char = reason)
# . = unchanged
# f = file being transferred
# s = file size changed
# t = file time changed
# D = directory created/updated
# L = symlink updated
```

### Transfer Only Newer Files

```bash
# Skip files that are newer on the destination
rsync -avzu src/ dest/

# Only update files that exist on destination (skip new files)
rsync -av --existing src/ dest/

# Only create new files, don't update existing ones
rsync -av --ignore-existing src/ dest/
```

## Advanced Patterns

### rsync Over SSH with Compression

```bash
# Compress and transfer over SSH
rsync -avz -e ssh /data/ user@server:/backup/

# With specific SSH options
rsync -avz -e 'ssh -o StrictHostKeyChecking=no -c aes128-ctr' \
    /data/ user@server:/backup/
```

### Using `--compare-dest` for Selective Updates

```bash
# Copy only files that differ from a reference directory
rsync -av --compare-dest=/reference/ src/ dest/

# Useful for: updating only changed projects in a multi-project workspace
rsync -av --compare-dest=/old-versions/projectA/ projectA/ new-version/
```

### Using `--copy-dest` (Includes Deletions)

```bash
# Like --compare-dest but also deletes files not in the reference
rsync -av --copy-dest=/reference/ src/ dest/
```

### Hard-Link Based Incremental Backups

```bash
#!/bin/bash
# Space-efficient incremental backups with hard links
LATEST="/backups/latest"
PREV="/backups/previous"

mkdir -p /backups
rsync -a --link-dest="$PREV" /data/ "$LATEST/"
mv "$PREV" "/backups/$(date -d '7 days ago' +%Y-%m-%d)" 2>/dev/null
ln -s "$LATEST" "$PREV"
```

### Batch Mode for Offline Transfer

```bash
# Create a batch file (for transfer on removable media)
rsync -av --write-batch=/tmp/backup.batch /data/ /media/usb/

# Apply the batch file later
rsync -av --read-batch=/tmp/backup.batch /data/ /other/dest/

# Also write/reflection to keep batch files consistent
rsync -av --only-write-batch=/tmp/update.batch /data/
```

### Using `--files-from` for Custom File Lists

```bash
# Generate file list and sync only those files
find /data -name '*.conf' -print > /tmp/conf-files.txt
rsync -av --files-from=/tmp/conf-files.txt / /backup/configs/

# With NUL delimiter (handles spaces/special chars)
find /data -name '*.log' -print0 | \
    rsync -av --files-from=- --from0 / /backup/logs/

# From remote host
rsync -av user@remote:'`find /var/log -name "*.log"`' /local/
```

### Copying to Different Name

```bash
# Copy a single file with different name
rsync -ai src/foo.c dest/bar.c

# Copy directory contents to different name (trailing slash on source)
rsync -ai src/ dest/new-name/
```

## Cron Automation

```cron
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/rsync-backup.sh >> /var/log/rsync-cron.log 2>&1

# Hourly sync during business hours
0 8-17 * * 1-5 rsync -az --bwlimit=1000 /data/ user@remote::module/ >> /var/log/rsync-hourly.log 2>&1
```

## Docker/Container Scenarios

```bash
# Backup container data volumes
docker run --rm -v mydata:/data -v $(pwd):/backup alpine \
    rsync -av /data/ /backup/mydata-backup/

# Restore from backup
docker run --rm -v mydata:/data -v $(pwd):/backup alpine \
    rsync -av /backup/mydata-backup/ /data/
```

## Windows (WSL/Cygwin)

```bash
# WSL: Copy between Windows and Linux filesystem
rsync -av /mnt/c/Users/username/Documents/ /home/user/win-docs/

# Cygwin: Use native rsync
rsync -av /cygdrive/c/data/ /cygdrive/d/backup/
```

## Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| "is your shell clean" error | Remove echo/print statements from `.bashrc`/`.profile` on remote host |
| rsync recopies same files | Add `-t` (or use `-a` which includes `-t`), or `--modify-window=1` for FAT filesystems |
| Protocol mismatch | Ensure matching rsync versions on both sides |
| "Connection refused" | Check if daemon is running, port 873 is open, firewall allows connection |
| Permission denied on destination | Use appropriate `--chown` or run as correct user |
| Spaces in filenames | Quote remote paths: `host:'a file with spaces'` |
| Memory issues with large trees | Use `--delete-delay`, break into subdirectory transfers |
| "vanished files" exit code 24 | Wrap in script that ignores exit 24, or use `--ignore-errors` |
