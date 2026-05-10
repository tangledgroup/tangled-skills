---
name: rsync-3-4-1
description: Complete toolkit for rsync 3.4.1, the fast and versatile file-copying tool using delta-transfer algorithm. Use when backing up files, mirroring directories, syncing data across hosts via SSH or rsync daemon, implementing incremental backups with --link-dest or --backup-dir, creating batch updates for bulk deployments, configuring rsyncd.conf daemons, or managing complex include/exclude filter rules.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - file-transfer
  - backup
  - mirroring
  - sync
  - daemon
  - incremental
category: system-tool
external_references:
  - https://rsync.samba.org/
  - https://download.samba.org/pub/rsync/rsync.1
  - https://download.samba.org/pub/rsync/rsyncd.conf.5
  - https://rsync.samba.org/FAQ.html
  - https://rsync.samba.org/examples.html
  - https://github.com/rsyncproject/rsync
---

# rsync 3.4.1

## Overview

Rsync is a fast and extraordinarily versatile file-copying tool. It can copy locally, to/from another host over any remote shell (typically SSH), or to/from a remote rsync daemon. It is famous for its delta-transfer algorithm, which reduces the amount of data sent over the network by sending only the differences between the source files and the existing files in the destination. Rsync is widely used for backups, mirroring, and as an improved copy command for everyday use.

Rsync finds files that need to be transferred using a "quick check" algorithm (by default) that looks for files that have changed in size or in last-modified time. Any changes in other preserved attributes are made on the destination file directly when the quick check indicates that the file's data does not need to be updated.

Key features include:

- Delta-transfer algorithm for efficient network usage
- Support for copying links, devices, owners, groups, and permissions
- Exclude and exclude-from options similar to GNU tar
- CVS exclude mode for ignoring common build artifacts
- Transparent remote shell support (SSH, rsh)
- No super-user privileges required
- Pipelining of file transfers to minimize latency
- Anonymous or authenticated rsync daemons for mirroring
- Incremental recursion for large file trees (reduced memory usage)
- Batch mode for applying the same updates to many identical systems
- Compression during transfer with configurable algorithms
- ACL and extended attribute preservation

## When to Use

- Backing up files locally or across hosts
- Mirroring directories (keeping source and destination in sync)
- Syncing data over SSH between servers
- Implementing incremental rotating backups with `--link-dest` or `--backup-dir`
- Creating batch update files for bulk deployment to multiple identical systems
- Setting up rsync daemons for anonymous or authenticated file distribution
- Managing complex include/exclude filter rules for selective transfers
- Moving files (using `--remove-source-files`)
- Performing dry runs to preview what changes rsync would make

## Core Concepts

### Transfer Modes

Rsync operates in three modes:

**Local copy** — both source and destination are on the same machine:

```bash
rsync -av /src/dir/ /dest/dir/
```

**Remote shell (pull)** — pulling files from a remote host via SSH:

```bash
rsync -av user@remote:/src/dir/ /local/dest/
```

**Remote shell (push)** — pushing files to a remote host via SSH:

```bash
rsync -av /local/src/ user@remote:/dest/dir/
```

**Rsync daemon (pull)** — connecting directly to an rsync daemon:

```bash
rsync -av user@host::module/path /local/dest/
rsync -av rsync://user@host:873/module/path /local/dest/
```

**Rsync daemon (push)** — pushing to a daemon module:

```bash
rsync -av /local/src/ user@host::module/path
```

### The Trailing Slash Rule

A trailing slash on the source changes behavior significantly:

- `rsync -av /src/foo /dest` — copies the directory `foo` into `/dest`, creating `/dest/foo`
- `rsync -av /src/foo/ /dest` — copies the *contents* of `foo` into `/dest`
- Both set the attributes of the containing directory on the destination

For daemon connections, no trailing slash is needed to copy module contents:

```bash
rsync -av host::module /dest
```

### Archive Mode (`-a`)

The `-a` (archive) flag is shorthand for `-rlptgoD`:

- `-r` — recurse into directories
- `-l` — copy symlinks as symlinks
- `-p` — preserve permissions
- `-t` — preserve modification times
- `-g` — preserve group
- `-o` — preserve owner (requires root on receiver)
- `-D` — preserve devices and specials

Note: `-a` does not include `-A` (ACLs), `-X` (xattrs), `-U` (atimes), `-N` (crtimes), or `-H` (hard links). Add these explicitly when needed: `rsync -aAXHN`.

### Delta-Transfer Algorithm

By default, rsync sends only the changed portions of files. This is controlled by the quick check algorithm, which compares file size and modification time. If both match, the file is skipped entirely. If they differ, rsync computes checksums on data blocks to identify exactly which portions need transferring.

Use `--whole-file` (`-W`) to disable delta-transfer and send files whole (faster for local copies or high-bandwidth connections where disk I/O is the bottleneck).

### Quick Check vs. Checksum

- **Quick check** (default): compares size and modification time — fast
- **Checksum** (`-c`): computes full-file checksums — thorough but slow, uses lots of disk I/O

Always use `-t` (preserve times) or `-a` (archive mode) in your initial copy, otherwise rsync cannot effectively skip unchanged files on subsequent runs.

## Usage Examples

### Basic local copy

```bash
rsync -av /source/ /destination/
```

### Remote sync over SSH

```bash
rsync -avz /local/data/ user@remote:/backup/data/
```

### Mirror with deletions (use `--dry-run` first!)

```bash
rsync -av --delete /source/ /mirror/
```

### Incremental rotating backup with hard links

```bash
DAY=$(date +%A)
rsync -a --link-dest=../current /source/ /backup/$DAY/
# Rotate:
mv /backup/current /backup/previous
ln -sfn "$DAY" /backup/current
```

### 7-day rotating incremental backup (from official examples)

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

### Dry run to preview changes

```bash
rsync -ain /source/ /dest/
```

### Bandwidth-limited transfer

```bash
rsync -avz --bwlimit=1000 /source/ user@remote:/dest/
```

### Progress display with partial file resume

```bash
rsync -aP /large/source/ /dest/
```

### Skip already-compressed files during compression

```bash
rsync -avz --skip-compress=gz/jpg/mp[34]/zip/bz2 /src/ /dst/
```

## Advanced Topics

**Command-Line Options**: Complete reference of all rsync options including transfer rules, delete modes, compression, and checksum algorithms → [Command-Line Options](reference/01-command-line-options.md)

**Filter Rules and Pattern Matching**: Include/exclude patterns, merge files, per-directory filters, modifiers, anchoring, and interaction with deletions → [Filter Rules](reference/02-filter-rules.md)

**Rsync Daemon Configuration**: rsyncd.conf parameters, module setup, authentication, access control, logging, SSL/TLS proxy, and daemon launch methods → [Daemon Configuration](reference/03-daemon-configuration.md)

**Batch Mode and Incremental Backups**: Write-batch/read-batch for bulk deployment, `--link-dest`, `--compare-dest`, `--copy-dest`, `--backup-dir`, and atomic update patterns → [Batch Mode and Backups](reference/04-batch-and-backups.md)

**Symbolic Links, Security, and Troubleshooting**: Symlink handling modes, multi-host security considerations, common error diagnostics, exit codes, and FAQ solutions → [Security and Troubleshooting](reference/05-security-and-troubleshooting.md)
