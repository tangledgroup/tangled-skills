---
name: rsync-3-4-1
description: Complete toolkit for rsync 3.4.1, the fast and versatile file-copying tool using delta-transfer algorithm for efficient synchronization. Use when copying files locally or remotely via SSH/rsync daemon, setting up backup scripts with incremental/hard-linked snapshots, configuring rsync daemon servers with authentication and access control, mirroring directories, implementing bandwidth-limited transfers, managing include/exclude filter rules, or performing batch-mode offline transfers.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.4.1"
tags:
  - file-transfer
  - synchronization
  - backup
  - mirroring
  - remote-copy
category: devops
external_references:
  - https://rsync.samba.org/
  - https://github.com/rsyncproject/rsync
---

# rsync 3.4.1

## Overview

Rsync is a fast, versatile file copying and synchronization tool for Unix-like systems. It uses a proprietary delta-transfer algorithm that reduces network bandwidth by sending only the differences between source and destination files. Rsync is widely used for backups, mirroring, and as an improved copy command for everyday use.

Key features:
- Delta-transfer algorithm (only sends changed blocks)
- Supports local, remote shell (SSH), and rsync daemon connections
- Preserves permissions, ownership, timestamps, symlinks, devices
- Flexible file selection with include/exclude filter rules
- Bandwidth limiting and compression
- Daemon mode for anonymous or authenticated file serving
- Batch mode for offline transfer scenarios

## When to Use

Use this skill when:
- **File synchronization**: Keeping directories in sync locally or across remote hosts
- **Backup automation**: Creating incremental backups, rotating snapshots, or hard-linked backup trees
- **Remote copying**: Efficiently transferring files over SSH with compression
- **Daemon setup**: Configuring rsync daemon servers for mirroring or shared file access
- **Selective sync**: Using include/exclude patterns to control which files are transferred
- **Bandwidth management**: Limiting transfer speeds or scheduling during off-hours
- **Mirroring**: Maintaining up-to-date copies of remote repositories or content

## Core Concepts

See [Core Concepts](references/01-core-concepts.md) for:
- The rsync algorithm and pipeline architecture (generator → sender → receiver)
- Connection types: local copy, remote shell (SSH), and rsync daemon
- Archive mode (`-a`) and its components
- Delete strategies (`--delete`, `--delete-before`, `--delete-during`, etc.)
- The quick check algorithm (size + mod-time comparison)
- Memory considerations for large file sets

## Command-Line Options Reference

See [Command Options](references/02-command-options.md) for complete option reference including:
- Output control (`-v`, `-q`, `--dry-run`, `--progress`, `-P`, `--stats`)
- File-sync options (`--archive`, `--recursive`, `--times`, `--delete*`, `--partial`)
- Backup options (`--backup`, `--backup-dir`, `--suffix`, `--update`, `--inplace`, `--append`)
- Filter rules (`--exclude`, `--include`, `--files-from`, `-f`, `-F`)
- Attribute preservation (`--links`, `--copy-links`, `--hard-links`, `--perms`, `--owner`, `--group`, `--devices`, `--acls`, `--xattrs`)
- Network/transport (`--compress`, `--whole-file`, `--block-size`, `-e ssh`, `--bwlimit`)
- Authentication (`--password-file`, `--trust-sender`, `--numeric-ids`)
- Batch mode (`--write-batch`, `--read-batch`, `--only-write-batch`)
- All environment variables (`RSYNC_RSH`, `RSYNC_PASSWORD`, `RSYNC_PORT`, etc.)
- Exit values and their meanings

## Daemon Configuration

See [Daemon Configuration](references/03-daemon-configuration.md) for:
- Starting the daemon (standalone, inetd, systemd)
- rsyncd.conf file format and syntax
- Module parameters: path, read/write access, authentication
- Authentication setup (`auth users`, `secrets file`, system users/PAM)
- Access control (`hosts allow/deny`, `deny users`)
- Logging configuration
- Security best practices
- Common daemon configurations (read-only mirror, writable backup, per-user homes)
- Rate limiting on the daemon side

## Use Cases & Examples

See [Use Cases](references/04-use-cases.md) for:
- Basic copy operations (local, remote pull/push, SSH with custom keys)
- Backup scenarios (incremental, hard-linked snapshots, rotating daily/weekly/monthly)
- Synchronization patterns (selective sync, include/exclude, partial recovery)
- Advanced patterns (`--compare-dest`, `--copy-dest`, `--link-dest`, batch mode)
- Cron automation examples
- Docker/WSL/Cygwin scenarios
- Common pitfalls and solutions

## Syntax Quick Reference

```
# Local copy
rsync [OPTION...] SRC... [DEST]

# Remote shell (SSH)
rsync [OPTION...] [USER@]HOST:SRC... [DEST]     # Pull
rsync [OPTION...] SRC... [USER@]HOST:DEST        # Push

# Rsync daemon
rsync [OPTION...] [USER@]HOST::SRC... [DEST]     # Pull (double colon)
rsync [OPTION...] SRC... [USER@]HOST::DEST       # Push
rsync [OPTION...] rsync://[USER@]HOST[:PORT]/SRC [DEST]  # URL form
```

## Essential Flags Cheat Sheet

| Flag | Meaning | Use Case |
|------|---------|----------|
| `-a` | Archive mode (`-rlptgoD`) | Most common: preserve everything |
| `-v` | Verbose | See what's happening |
| `-z` | Compress during transfer | Over slow networks |
| `-n` | Dry run | Preview without changes |
| `-P` | Progress + partial | Monitor large transfers |
| `-u` | Update only (newer) | Skip files newer on destination |
| `-r` | Recursive | Include subdirectories |
| `-t` | Preserve times | Essential for delta detection |
| `-l` | Copy symlinks | Preserve link structure |
| `-H` | Hard links | Preserve hard link relationships |
| `-A` | ACLs | Preserve access control lists |
| `-X` | Extended attrs | Preserve xattrs (SELinux, etc.) |
| `--delete` | Remove extraneous files | Exact mirror of source |
| `--exclude='*.log'` | Skip patterns | Reduce transfer size |
| `--bwlimit=500` | Bandwidth limit KB/s | Rate limiting |
| `-e ssh` | Use SSH | Secure remote transfer |

## Trailing Slash Behavior

```bash
rsync -av /src/foo /dest          # Creates /dest/foo/ (with foo's contents)
rsync -av /src/foo/ /dest         # Copies contents of foo/ into /dest/
```

A trailing slash on the source means "copy the **contents**" rather than "copy the directory itself."

## Common Patterns

### Full Mirror
```bash
rsync -avz --delete src/ dest/
```

### Backup with Backups of Old Files
```bash
rsync -avz --backup --backup-dir=/backups/$(date +%Y-%m-%d) src/ dest/
```

### Dry Run to Preview Changes
```bash
rsync -avn --itemize-changes src/ dest/
```

### Sync with SSH and Compression
```bash
rsync -avz -e ssh user@host:/data/ /local/dest/
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `RSYNC_RSH` | Default remote shell (e.g., `ssh -i ~/.ssh/key`) |
| `RSYNC_PASSWORD` | Password for daemon authentication |
| `RSYNC_PORT` | Default daemon port |
| `RSYNC_PROXY` | HTTP proxy for daemon connections |

## References

- Official website: https://rsync.samba.org/
- GitHub repository: https://github.com/rsyncproject/rsync
- rsync man page (HTML): https://download.samba.org/pub/rsync/rsync.1
- rsyncd.conf man page (HTML): https://download.samba.org/pub/rsync/rsyncd.conf.5
- FAQ: https://rsync.samba.org/FAQ.html
- Mailing list: rsync@lists.samba.org
- How rsync works: https://rsync.samba.org/how-rsync-works.html
