---
name: rsync-3-4-1
description: Complete toolkit for rsync 3.4.1, the fast and versatile file-copying tool using delta-transfer algorithm. Use when backing up files, mirroring directories, syncing data across hosts via SSH or rsync daemon, implementing incremental backups with --link-dest or --backup-dir, creating batch updates for bulk deployments, configuring rsyncd.conf daemons, or managing complex include/exclude filter rules.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.4.1"
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

Rsync is a fast and extraordinarily versatile file-copying tool for Unix systems. It can copy locally, to/from another host over any remote shell (typically SSH), or to/from a remote rsync daemon. It is famous for its delta-transfer algorithm, which reduces the amount of data sent over the network by sending only the differences between the source files and the existing files in the destination.

Rsync finds files that need to be transferred using a "quick check" algorithm (by default) that looks for files changed in size or last-modified time. Changes in other preserved attributes are made on the destination file directly when quick check indicates the file's data does not need updating.

Key features:

- Delta-transfer algorithm sends only differences between files
- Supports copying links, devices, owners, groups, permissions, ACLs, and extended attributes
- Exclude and exclude-from options similar to GNU tar
- CVS exclude mode for ignoring build artifacts
- Can use any transparent remote shell (SSH, rsh) or direct rsync daemon connection
- Does not require super-user privileges
- Pipelining of file transfers to minimize latency costs
- Anonymous or authenticated rsync daemons ideal for mirroring
- Batch mode for applying same updates to many identical systems
- Compression support with zstd, lz4, zlib algorithms

## When to Use

- Backing up files locally or across hosts
- Mirroring directory trees and filesystems
- Incremental backups with rotating history (using `--backup-dir` or `--link-dest`)
- Syncing data between servers via SSH or rsync daemon
- Configuring rsync daemons for anonymous or authenticated access
- Creating batch update files for deploying changes to multiple identical systems
- Implementing complex file filtering with include/exclude rules
- Moving files (using `--remove-source-files`)
- Bandwidth-limited transfers (`--bwlimit`)
- Transfers with time limits (`--stop-after`, `--stop-at`)

## Core Concepts

### Transfer Modes

Rsync supports three access modes:

**Local copy** — both source and destination are local paths:

```bash
rsync -av /src/dir/ /dest/dir/
```

**Remote shell (SSH by default)** — uses a colon (`:`) separator after the host specification:

```bash
# Pull from remote
rsync -av user@host:/remote/src/ /local/dest/

# Push to remote
rsync -av /local/src/ user@host:/remote/dest/
```

**Rsync daemon** — uses double colon (`::`) or `rsync://` URL syntax:

```bash
# Pull from daemon
rsync -av host::module/path /local/dest/
rsync -av rsync://host/module/path /local/dest/

# Push to daemon (requires read_only = no)
rsync -av /local/src/ host::module/path
```

### The Trailing Slash Rule

A trailing slash on the source changes behavior:

- `rsync -av /src/foo /dest` — copies the directory `foo` into `/dest/foo`
- `rsync -av /src/foo/ /dest` — copies the *contents* of `foo` into `/dest`
- `rsync -av /src/foo/ /dest/foo` — equivalent to the above

### Archive Mode (`-a`)

The `-a` flag is shorthand for `-rlptgoD`:

- `-r` — recurse into directories
- `-l` — copy symlinks as symlinks
- `-p` — preserve permissions
- `-t` — preserve modification times
- `-g` — preserve group
- `-o` — preserve owner (requires root)
- `-D` — preserve devices and special files

Note: `-a` does NOT include ACLs (`-A`), xattrs (`-X`), atimes (`-U`), crtimes (`-N`), or hardlinks (`-H`). Add these explicitly when needed.

### Quick Check Algorithm

By default, rsync skips files that match in both size and modification time. Alternatives:

- `--checksum` (`-c`) — compares 128-bit checksums instead (slower, more I/O)
- `--size-only` — skips files matching only in size
- `--modify-window=NUM` — treats timestamps as equal if they differ by at most NUM seconds (useful for FAT filesystems: `--modify-window=1`)

## Usage Examples

### Basic local copy with archive mode and verbose output

```bash
rsync -av /source/dir/ /destination/dir/
```

### Remote sync over SSH with compression

```bash
rsync -avz /local/data/ user@remote:/backup/data/
```

### Incremental backup with rotating weekly history

```bash
DAY=$(date +%A)
rsync -a --delete --backup --backup-dir=/backup/$USER/$DAY \
  /home/$USER/ /backup/$USER/current/
```

### Mirror with hard-linked unchanged files (space-efficient snapshots)

```bash
rsync -av --link-dest=$PWD/prior_backup host:src_dir/ new_backup/
```

### Dry run to preview changes before actual transfer

```bash
rsync -ain /source/ /destination/
```

### Exclude patterns with delete

```bash
rsync -av --delete \
  --exclude='*.tmp' \
  --exclude='.git/' \
  --exclude='node_modules/' \
  /src/ user@host:/dest/
```

### Bandwidth-limited transfer with progress

```bash
rsync -avP --bwlimit=1000 /large/files/ remote:/backup/
```

### Transfer with time limit

```bash
rsync -aiv --stop-after=60 /src/ /dest/
rsync -aiv --stop-at=23:59 /src/ /dest/
```

## Advanced Topics

**Command-Line Options**: Complete reference of all rsync options including delete modes, compression, checksums, filtering, and daemon options → See [Command-Line Options](reference/01-command-line-options.md)

**Filter Rules**: Include/exclude patterns, merge files, per-directory filters, pattern matching with wildcards, and filter rule modifiers → See [Filter Rules](reference/02-filter-rules.md)

**Rsync Daemon (rsyncd.conf)**: Daemon configuration, modules, authentication, access control, logging, SSL/TLS setup, and config directives → See [Rsync Daemon Configuration](reference/03-rsync-daemon.md)

**Batch Mode and Advanced Workflows**: Batch updates for multiple hosts, batch file creation and application, advanced backup strategies, and transfer rules → See [Batch Mode and Advanced Workflows](reference/04-batch-and-advanced.md)
