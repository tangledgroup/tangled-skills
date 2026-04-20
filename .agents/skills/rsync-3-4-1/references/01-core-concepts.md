# Core Concepts

## The rsync Algorithm

Rsync uses a delta-transfer algorithm that reduces the amount of data sent over the network by sending only the differences between source and destination files. This makes it extraordinarily efficient for:

- **Incremental backups**: Only changed blocks are transferred
- **Mirroring**: Keep remote directories in sync efficiently
- **Everyday copying**: Improved `cp` command with delta support

### How It Works

1. **File List Generation**: The sender creates a file list including pathnames, ownership, mode, permissions, size, and modtime
2. **Pipeline Architecture**: Three processes communicate unidirectionally:
   - `generator → sender → receiver`
3. **Block Checksums**: For each file needing update, the generator creates block checksums for the "basis file" (existing version on receiver)
4. **Remote Matching**: The sender reads file indices and block checksums, then computes matching checksums against the source file to find which blocks already exist at the destination

### Key Terminology

| Term | Meaning |
|------|---------|
| **Client** | The side that initiates synchronization |
| **Server** | The remote rsync process (not necessarily a daemon) |
| **Daemon** | A persistent rsync process awaiting connections on TCP port 873 |
| **Sender** | Process with access to source files being synchronized |
| **Receiver** | Process that receives update data and writes to disk |
| **Generator** | Process that identifies changed files and manages file-level logic |
| **Basis File** | Existing version on the receiving side used as reference for delta computation |

## Connection Types

### 1. Local Copy
```bash
rsync [OPTION...] SRC... [DEST]
```
Both source and destination are local paths. Behaves like an improved `cp`.

### 2. Remote Shell (SSH)
```bash
# Pull (from remote to local)
rsync [OPTION...] [USER@]HOST:SRC... [DEST]

# Push (from local to remote)
rsync [OPTION...] SRC... [USER@]HOST:DEST
```
Uses any transparent remote shell (ssh, rsh). The `:` separator after a hostname triggers remote mode.

### 3. Rsync Daemon
```bash
# Pull
rsync [OPTION...] [USER@]HOST::SRC... [DEST]
rsync [OPTION...] rsync://[USER@]HOST[:PORT]/SRC... [DEST]

# Push
rsync [OPTION...] SRC... [USER@]HOST::DEST
rsync [OPTION...] SRC... rsync://[USER@]HOST[:PORT]/DEST
```
Connects directly to an rsync daemon via TCP (default port 873). The `::` separator or `rsync://` URL triggers daemon mode.

### Trailing Slash Behavior
A trailing slash on the **source** changes behavior:
- `rsync -av /src/foo /dest` → copies the `foo` directory INTO `/dest/` (creates `/dest/foo/`)
- `rsync -av /src/foo/ /dest` → copies the **contents** of `foo/` INTO `/dest/` (creates `/dest/file1`, `/dest/file2`, ...)

### Single Source + No Destination = List
```bash
rsync somehost::
# Lists all available modules from the daemon

rsync -av srcdir/
# Lists files in srcdir with ls -l style output
```

## The Archive Mode (`-a`)

`-a` is equivalent to `-rlptgoD` (no `-A,-X,-U,-N,-H`):
- `-r`: recurse into directories
- `-l`: copy symlinks as symlinks
- `-p`: preserve permissions
- `-t`: preserve modification times
- `-g`: preserve group
- `-o`: preserve owner (super-user only)
- `-D`: same as `--devices --specials`

**Note**: Archive mode does NOT preserve ACLs (`-A`), extended attributes (`-X`), or hard links (`-H`) by default. Add these explicitly when needed.

## The Quick Check Algorithm

By default, rsync uses a "quick check" to decide if a file needs updating:
- Compares **size** and **last-modified time**
- If both match, the file is considered unchanged
- Other preserved attributes (permissions, ownership) are still updated on destination if needed

If `--checksum` (`-c`) is used, rsync compares full checksums instead of mod-time+size (more accurate but slower and I/O intensive).

## Delete Options

Rsync offers multiple strategies for handling deletions:

| Option | When Deletions Happen |
|--------|----------------------|
| `--delete` | Default: same as `--delete-during` |
| `--delete-before` | Before transfer, on receiver side |
| `--delete-during` / `--del` | During transfer, on sender side |
| `--delete-delay` | During transfer, but collects files to delete and deletes after transfer |
| `--delete-after` | After transfer, on receiver side |
| `--delete-excluded` | Also exclude matching files from deletion |

## Memory Considerations

- rsync 3.0.0+ uses **incremental recursion** by default, building file lists in chunks
- Each file entry consumes ~100 bytes of memory
- `-H` (hard links) and `--delete` increase memory usage
- For very large file counts with memory issues: use `--delete-delay`, break into smaller subdirectory transfers, or use exclude rules
