---
name: rsync-3-4-1
description: Complete toolkit for rsync 3.4.1, the fast and versatile file-copying tool using delta-transfer algorithm for remote and local file synchronization. Use when backing up files, mirroring directories, syncing data across hosts via SSH or rsync daemon, configuring rsync daemon servers, implementing incremental backups with --link-dest, creating batch updates for bulk deployments, or managing complex include/exclude filter rules.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.4.1"
tags:
  - file synchronization
  - backup
  - mirroring
  - delta transfer
  - remote copy
category: systems
external_references:
  - https://rsync.samba.org/
  - https://github.com/rsyncproject/rsync
---

# rsync 3.4.1

## Overview

Rsync is a fast, extraordinarily versatile file-copying tool for both remote and local file synchronization. It uses the **delta-transfer algorithm** which reduces network data by sending only the differences between source and destination files, without requiring both sets of files to exist at one end beforehand.

Rsync is widely used for backups, mirroring, and as an improved `cp` command for everyday use. Both sender and receiver can be run on the same or different hosts.

## When to Use

- **Incremental backups** — sync only changed files between source and destination
- **Remote file synchronization** — copy files across SSH or rsync daemon
- **Mirroring** — maintain exact copies of directory trees across systems
- **Selective file transfers** — use include/exclude filters for fine-grained control
- **Bandwidth-constrained transfers** — use compression and delta-transfer
- **Bulk deployments** — use batch mode to update many identical systems
- **Daemon configuration** — set up authenticated rsync servers for public/private file distribution

## Core Concepts

### Transfer Modes

Rsync supports three transfer modes:

1. **Local copy**: `rsync [OPTION...] SRC... DEST`
2. **Remote shell (SSH)**: `rsync [OPTION...] [USER@]HOST:SRC... DEST` (pull) or `rsync [OPTION...] SRC... [USER@]HOST:DEST` (push)
3. **Rsync daemon**: `rsync [OPTION...] [USER@]HOST::SRC... DEST` or `rsync [OPTION...] rsync://[USER@]HOST[:PORT]/SRC.../DEST`

### Archive Mode (`-a`)

The `-a` flag is equivalent to `-rlptgoD`:
- `-r` recursive
- `-l` copy symlinks as symlinks
- `-p` preserve permissions
- `-t` preserve modification times
- `-g` preserve group
- `-o` preserve owner (super-user only)
- `-D` preserve device files and special files (same as `--devices --specials`)

**Note:** Archive mode does NOT include ACLs (`-A`), extended attributes (`-X`), atimes (`-U`), crtimes (`-N`), or hard link preservation (`-H`).

### The Delta-Transfer Algorithm

Rsync works by:
1. The sender scans source files and sends a list of file names and sizes to the receiver
2. The receiver generates checksums for blocks of each file
3. The sender finds the best-matching blocks and sends delta corrections
4. The receiver reconstructs the updated files

Key options controlling this:
- `--checksum` (`-c`): skip based on checksum, not mod-time & size (slower, more thorough)
- `--block-size=SIZE` (`-B`): force a fixed block size for the algorithm
- `--whole-file` (`-W`): copy files whole without delta algorithm

### Trailing Slash Behavior

A trailing slash on the **source** changes behavior:
- `rsync -av /src/foo /dest` → copies the `foo` directory into `/dest/foo`
- `rsync -av /src/foo/ /dest` → copies the *contents* of `foo` into `/dest`

### Incremental Recursion

Since rsync 3.0.0, recursive scanning uses **incremental recursion** by default, which builds the file list in chunks and holds each chunk in memory only as needed. This dramatically reduces memory usage for large transfers. Some options (like `--delete-before`, `--delete-after`, `--prune-empty-dirs`) disable this mode.

## Installation / Setup

### From Package Manager (Recommended)

```bash
# Debian/Ubuntu
sudo apt install rsync

# RHEL/CentOS/Fedora
sudo dnf install rsync
# or: sudo yum install rsync

# macOS
brew install rsync

# Arch Linux
pacman -S rsync
```

### Build from Source

```bash
git clone https://github.com/rsyncproject/rsync.git
cd rsync
./configure --prefix=/usr/local
make
sudo make install
```

**Optional build dependencies for maximum features:**
- `libxxhash-dev` — fast xxHash checksums (default in modern builds)
- `libzstd-dev` — zstd compression (more efficient than zlib)
- `liblz4-dev` — lz4 compression (fastest, lower ratio)
- `libssl-dev` — hardware-accelerated MD4/MD5 checksums
- `libacl1-dev` — ACL support
- `libattr1-dev` — extended attribute support

See [references/01-installation-and-building.md](references/01-installation-and-building.md) for detailed build instructions.

## Usage Examples

### Basic Local Copy

```bash
# Simple local copy (like cp but with progress)
rsync -av /source/dir/ /dest/dir/

# With progress indicator
rsync -av --progress /source/file.txt /dest/

# Dry run — see what would be transferred
rsync -avn /source/dir/ /dest/dir/
```

### Remote Copy via SSH (Default)

```bash
# Push local files to remote host
rsync -avz /local/path/ user@remote:/remote/path/

# Pull remote files to local
rsync -avz user@remote:/remote/path/ /local/path/

# Use custom SSH key and port
rsync -avz -e "ssh -i ~/.ssh/custom_key -p 2222" /local/path/ user@remote:/remote/path/

# Preserve additional attributes with compression
rsync -avzHAX --delete /source/ user@remote:/dest/
```

### Backup with Rotation (7-Day Incremental)

```bash
#!/bin/bash
# 7-day rotating incremental backup
BACKUP_DIR="/backup/current"
DATE=$(date +%A)  # Day of week: Monday, Tuesday, ...
RSYNC_OPTS="-a --delete --backup --backup-dir=/$DATE"

rsync $RSYNC_OPTS /home/ user@backup-server:/backups/home/
```

### Incremental Backup with Hard Links (Space-Efficient)

```bash
#!/bin/bash
# Create a new backup directory, hard-linking unchanged files from prior backup
PRIOR="/backups/previous"
NEW="/backups/$(date +%Y-%m-%d)"

mkdir -p "$NEW"
rsync -a --link-dest="$PRIOR" /source/ "$NEW/"
```

### Mirroring with Exclusions

```bash
# Mirror a website, excluding build artifacts and version control
rsync -avz \
  --exclude={'*.o','*.swp','.git','node_modules','__pycache__'} \
  --delete \
  /src/webapp/ user@webserver:/var/www/html/
```

### Using Filter Rules (Advanced)

```bash
# Include only specific file types, exclude everything else
rsync -av \
  -f'+ *.txt' -f'+ *.pdf' -f'- *' \
  /source/ dest/

# Per-directory filters using .rsync-filter files
rsync -av -F /source/ dest/
# This reads .rsync-filter files from each directory in the transfer tree
```

### Rsync Daemon (Server Setup)

**`/etc/rsyncd.conf`:**
```ini
pid file = /var/run/rsyncd.pid
port = 873
address = 0.0.0.0
log file = /var/log/rsyncd.log
max connections = 5
timeout = 600

[public]
    path = /srv/rsync/public
    comment = Public mirror
    read only = yes
    list = yes

[private]
    path = /srv/rsync/private
    comment = Private storage
    read only = no
    auth users = admin,backup-user
    secrets file = /etc/rsyncd.secrets
    hosts allow = 192.168.1.0/24
```

**`/etc/rsyncd.secrets`:**
```
admin:securepassword123
backup-user:backuppass456
```

**Start the daemon:**
```bash
sudo rsync --daemon --config=/etc/rsyncd.conf
```

**Connect to a daemon:**
```bash
# Pull from public module (no auth)
rsync -av rsync://backup-server/public/ /local/mirror/

# Push to private module (with auth)
export RSYNC_PASSWORD=securepassword123
rsync -av /local/data/ admin@backup-server::private/
```

### Batch Mode (Bulk Deployments)

```bash
# Write batch file on source
rsync --write-batch=updates -a /source/dir/ /dest/dir/

# Apply to multiple target machines
for host in server1 server2 server3; do
    scp updates* "$host:"
    ssh "$host" ./updates.sh /new-dest/dir/
done
```

### Bandwidth-Limited Transfer

```bash
# Limit transfer rate to 1 MB/s
rsync -av --bwlimit=1000 /source/ user@remote:/dest/
```

## Advanced Topics

For detailed coverage of advanced topics, see the reference files:

- **[references/02-filter-rules.md](references/02-filter-rules.md)** — Comprehensive filter rule syntax, include/exclude patterns, per-directory filters, and CVS ignore mode
- **[references/03-delete-modes.md](references/03-delete-modes.md)** — Delete modes (--delete, --delete-before/after/during/delay), partial transfer handling, and safety options
- **[references/04-dest-options.md](references/04-dest-options.md)** — compare-dest, copy-dest, link-dest for sparse backups and flash cutover
- **[references/05-daemon-config.md](references/05-daemon-config.md)** — Complete rsyncd.conf reference, authentication, access control, logging, and security
- **[references/06-symlink-and-security.md](references/06-symlink-and-security.md)** — Symlink handling options, CVE-2024 vulnerabilities, and safe transfer practices
- **[references/07-exit-codes-and-troubleshooting.md](references/07-exit-codes-and-troubleshooting.md)** — All exit codes, common errors, and debugging techniques

## Key Options Quick Reference

| Option | Short | Description |
|--------|-------|-------------|
| `--archive` | `-a` | Archive mode (-rlptgoD) |
| `--recursive` | `-r` | Recurse into directories |
| `--links` | `-l` | Preserve symlinks |
| `--perms` | `-p` | Preserve permissions |
| `--times` | `-t` | Preserve modification times |
| `--delete` | — | Delete extraneous files from dest |
| `--compress` | `-z` | Compress file data during transfer |
| `--progress` | — | Show transfer progress |
| `--dry-run` | `-n` | Trial run, no changes made |
| `--backup` | `-b` | Make backups of existing files |
| `--update` | `-u` | Skip files newer on receiver |
| `--itemize-changes` | `-i` | Output change summary for all updates |
| `--human-readable` | `-h` | Output sizes in human-readable format |
| `--exclude=PATTERN` | — | Exclude files matching PATTERN |
| `--filter=RULE` | `-f` | Add a file-filtering rule |
| `--bwlimit=RATE` | — | Limit I/O bandwidth |
| `--timeout=SECS` | — | Set I/O timeout in seconds |
| `--partial` | — | Keep partially transferred files |
| `--sparse` | `-S` | Turn sequences of nulls into sparse blocks |
| `--xattrs` | `-X` | Preserve extended attributes |
| `--acls` | `-A` | Preserve ACLs |
| `--hard-links` | `-H` | Preserve hard links |
| `--one-file-system` | `-x` | Don't cross filesystem boundaries |
| `--copy-devices` | — | Copy device contents as regular file |
| `--iconv=SPEC` | — | Convert filename character sets |

## Statistics

- **Protocol number**: 32 (rsync 3.4.x)
- **Original authors**: Andrew Tridgell and Paul Mackerras
- **Current maintainer**: Wayne Davison (until 3.3.0), then Andrew Tridgell (from 3.4.0)
- **License**: GNU GPL
- **Latest CVE fixes**: 3.4.0 fixed 6 security vulnerabilities (CVE-2024-12084 through CVE-2024-12747)

## References

- Official website: https://rsync.samba.org/
- GitHub repository: https://github.com/rsyncproject/rsync
- Man page (HTML): https://download.samba.org/pub/rsync/rsync.1
- rsyncd.conf man page: https://download.samba.org/pub/rsync/rsyncd.conf.5
- FAQ: https://rsync.samba.org/FAQ.html
- Examples: https://rsync.samba.org/examples.html
- Bug tracking: https://rsync.samba.org/bug-tracking.html
- Mailing list: rsync@lists.samba.org
