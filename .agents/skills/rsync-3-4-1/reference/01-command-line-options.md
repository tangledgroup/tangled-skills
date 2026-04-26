# Command-Line Options

## Option Syntax

Rsync accepts both long (`--option`) and short (`-o`) forms. Parameters can be specified as `--option=value`, `--option value`, `-ovalue`, or `-o value`. Use quotes for values with spaces.

```bash
rsync --exclude='*.tmp' src/ dest/
rsync -f'- *.tmp' src/ dest/
```

Use `--no-OPTION` to disable an implied option (e.g., `--archive --no-owner`).

## Verbose and Debug Options

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Increase verbosity. Single `-v` shows transferred files and summary; `-vv` adds skipped files; more than 2 is for debugging |
| `--info=FLAGS` | Fine-grained informational verbosity (e.g., `--info=progress2`, `--info=stats2`) |
| `--debug=FLAGS` | Fine-grained debug verbosity (e.g., `--debug=FILTER`, `--debug=del2,acl`) |
| `--stderr=e\|a\|c` | Control stderr output: `errors` (default), `all`, or `client` |
| `--quiet`, `-q` | Suppress non-error messages |

## Transfer Selection Options

### Skip/Update Controls

- `--checksum`, `-c` — skip based on checksum instead of mod-time &amp; size (expensive in I/O)
- `--update`, `-u` — skip files newer on receiver (does not affect dirs/symlinks)
- `--ignore-times`, `-I` — disable quick check, transfer all files
- `--size-only` — skip files matching only in size
- `--modify-window=NUM`, `-@` — timestamp comparison tolerance in seconds (use `1` for FAT filesystems)
- `--existing` — skip creating new files on receiver
- `--ignore-existing` — skip updating existing files on receiver

### In-Place and Append Modes

- `--inplace` — update destination files directly instead of creating temp file (useful for large files with block-based changes; conflicts with `--partial-dir` and `--delay-updates`)
- `--append` — append data onto shorter files (dangerous unless you know files are shared growing files)
- `--append-verify` — like `--append` but verifies all existing content via checksum

### Directory Handling

- `--recursive`, `-r` — recurse into directories
- `--dirs`, `-d` — transfer directories without recursing
- `--relative`, `-R` — use relative path names (preserves full path on destination)
- `--no-implied-dirs` — don't send implied dirs with `--relative`
- `--mkpath` — create destination's missing path components
- `--prune-empty-dirs`, `-m` — remove empty directory chains from file list
- `--one-file-system`, `-x` — don't cross filesystem boundaries (repeat to omit mount-point dirs)

## Symlink Options

| Option | Behavior |
|--------|----------|
| `--links`, `-l` | Copy symlinks as symlinks (default in archive mode) |
| `--copy-links`, `-L` | Transform symlink into referent file/dir |
| `--copy-unsafe-links` | Only "unsafe" symlinks are transformed to files |
| `--safe-links` | Receiver ignores symlinks pointing outside the tree |
| `--munge-links` | Munge symlinks to make them safe and unusable |
| `--copy-dirlinks`, `-k` | Transform symlink-to-dir into referent dir |
| `--keep-dirlinks`, `-K` | Treat existing symlink-to-dir on receiver as real dir |

Symlink option precedence (first matching rule applies):

1. `--copy-links` — all symlinks become normal files/dirs
2. `--copy-dirlinks` — only symlinks-to-dirs become real dirs
3. `--links --copy-unsafe-links` — unsafe symlinks become files, safe ones created as symlinks
4. `--copy-unsafe-links` — unsafe symlinks become files, safe ones skipped
5. `--links --safe-links` — receiver skips unsafe, creates safe
6. `--links` — create all symlinks

## Permission and Attribute Options

- `--perms`, `-p` — preserve permissions (part of `-a`)
- `--executability`, `-E` — preserve executability when `--perms` is off
- `--chmod=CHMOD` — affect file/directory permissions during transfer. Supports `D` prefix for dirs only, `F` prefix for files only:

```bash
rsync -av --chmod=Dg+s,ug+w,Fo-w,+X src/ dest/
rsync -av --chmod=D2775,F664 src/ dest/
```

- `--acls`, `-A` — preserve ACLs (implies `--perms`)
- `--xattrs`, `-X` — preserve extended attributes (`-XX` copies all xattrs including rsync's special ones)
- `--owner`, `-o` — preserve owner (super-user only, part of `-a`)
- `--group`, `-g` — preserve group (part of `-a`)
- `--devices` — preserve device files (super-user only, part of `-D`)
- `--specials` — preserve special files like fifos and sockets (part of `-D`)
- `--copy-devices` — copy device contents as regular file
- `--write-devices` — write to devices as files (implies `--inplace`)
- `--numeric-ids` — don't map uid/gid by name, use numeric IDs
- `--usermap=STRING` / `--groupmap=STRING` — custom username/groupname mapping
- `--chown=USER:GROUP` — simple ownership mapping

### Fake Super

`--fake-super` simulates super-user activities by storing privileged attributes (owner, group, permissions, ACLs, non-user xattrs) in extended attributes. This allows full backup without root privileges:

```bash
# Apply to remote side only via --remote-option (-M)
rsync -av -M--fake-super /src/ host:/dest/

# For local copy, affects both sides
rsync -av --fake-super /src/ /dest/
```

## Time Preservation Options

- `--times`, `-t` — preserve modification times (part of `-a`)
- `--atimes`, `-U` — preserve access times (repeat for `--open-noatime` too)
- `--open-noatime` — open files with O_NOATIME flag to avoid changing atime
- `--crtimes`, `-N` — preserve create times (requires filesystem support)
- `--omit-dir-times`, `-O` — omit directories from time preservation (good for NFS, implied by `--backup` without `--backup-dir`)
- `--omit-link-times`, `-J` — omit symlinks from time preservation

## Backup Options

- `--backup`, `-b` — make backups of preexisting destination files
- `--backup-dir=DIR` — store backups in specified directory hierarchy (implies `--backup`)
- `--suffix=SUFFIX` — backup suffix (default `~` without `--backup-dir`, empty string with it)

```bash
# Rotate weekly backups
DAY=$(date +%A)
rsync -a --delete --backup --backup-dir=/backup/$DAY /src/ /backup/current/
```

## Delete Options

`--delete` removes extraneous files from destination directories that aren't on the sending side. Must specify the whole directory (not wildcarded contents).

**Delete timing modes** (choose one, default is `--delete-during`):

- `--delete-before` — delete before transfer starts (forces non-incremental recursion)
- `--delete-during`, `--del` — delete incrementally during transfer (default for modern rsync)
- `--delete-delay` — compute deletions during, remove after (compatible with incremental recursion)
- `--delete-after` — delete after transfer completes (forces non-incremental recursion)

**Additional delete controls:**

- `--delete-excluded` — also delete excluded files from dest dirs
- `--ignore-errors` — delete even if I/O errors occur
- `--force` — force deletion of dirs even if not empty
- `--max-delete=NUM` — don't delete more than NUM files (`0` warns without deleting)

**Important:** If the sending side detects I/O errors, deletion is automatically disabled to prevent accidental mass deletion. Use `--ignore-errors` to override.

Always test with `--dry-run` first:

```bash
rsync -ain --delete /src/ /dest/
```

## Compression Options

- `--compress`, `-z` — compress file data during transfer (auto-negotiates algorithm)
- `--compress-choice=STR`, `--zc=STR` — choose compression algorithm: `zstd`, `lz4`, `zlibx`, `zlib`, `none`
- `--compress-level=NUM`, `--zl=NUM` — explicitly set compression level
- `--skip-compress=LIST` — skip compressing files with specified suffixes (e.g., `gz/jpg/mp[34]/7z/bz2`)

```bash
rsync -av --zc=zstd --zl=22 host:src/ dest/
```

Available compression algorithms depend on build. Check with `rsync --version`.

## Checksum Options

- `--checksum-choice=STR`, `--cc=STR` — choose checksum algorithm: `xxh128`, `xxh3`, `xxh64` (aka `xxhash`), `md5`, `md4`, `sha1`, `none`
- `--block-size=SIZE`, `-B` — force fixed checksum block-size

```bash
rsync -av --cc=xxh3 src/ dest/
```

## Transfer Size and Speed Controls

- `--max-size=SIZE` — don't transfer files larger than SIZE (e.g., `1.5m`, `2g+1`)
- `--min-size=SIZE` — don't transfer files smaller than SIZE
- `--bwlimit=RATE` — limit socket I/O bandwidth in KB/s (e.g., `--bwlimit=1000` = 1MB/s)
- `--stop-after=MINS` — stop after MINS minutes
- `--stop-at=y-m-dTh:m` — stop at specified time (e.g., `23:59`, `2000-12-31T23:59`)

## Progress and Output Options

- `--progress` — show per-file progress during transfer
- `-P` — equivalent to `--partial --progress`
- `--itemize-changes`, `-i` — output change-summary for all updates
- `--out-format=FORMAT` — custom per-update output format (uses same escapes as daemon log format)
- `--stats` — print verbose transfer statistics
- `--human-readable`, `-h` — output numbers in human-readable format (repeat for higher levels)
- `--8-bit-output`, `-8` — leave high-bit chars unescaped in output

The `-i` flag shows changes with a 10-character string where each position represents:

```
c = checksum changed
s = size changed
t = modification time changed
p = permissions changed
o = owner changed
g = group changed
a = ACL changed
x = xattr changed
u = access time changed
n = create time changed
D = type change (file format difference)
```

A space means unchanged, `*deleting` means file being removed.

## Remote Shell and Connection Options

- `--rsh=COMMAND`, `-e` — specify remote shell (default: ssh). Can include args in single argument:

```bash
rsync -av -e 'ssh -p 2234' src/ host:/dest/
```

- `--rsync-path=PROGRAM` — specify rsync path on remote machine
- `--remote-option=OPT`, `-M` — send option to remote side only
- `--contimeout=SECONDS` — daemon connection timeout
- `--timeout=SECONDS` — I/O timeout in seconds
- `--port=PORT` — alternate daemon port (default: 873)
- `--address=ADDRESS` — bind address for outgoing socket to daemon
- `--sockopts=OPTIONS` — custom TCP options
- `--blocking-io` — use blocking I/O for remote shell
- `--ipv4`, `-4` / `--ipv6`, `-6` — prefer IPv4/IPv6

## Partial Transfer Options

- `--partial` — keep partially transferred files on interruption
- `--partial-dir=DIR` — put partial files into specified directory (implies `--partial`)

```bash
# Use .rsync-tmp as partial directory with progress
export RSYNC_PARTIAL_DIR=.rsync-tmp
rsync -avP /src/ /dest/
```

- `--delay-updates` — put all updated files into place at end (more atomic; uses `.~tmp~` dir by default)
- `--fuzzy`, `-y` — find similar file for basis if no dest file exists

## Alternate Destination Options

- `--compare-dest=DIR` — compare against DIR on destination; skip transfer if identical found there
- `--copy-dest=DIR` — like `--compare-dest` but also copies unchanged files from DIR
- `--link-dest=DIR` — like `--copy-dest` but hard-links unchanged files (space-efficient snapshots)

```bash
rsync -av --link-dest=$PWD/prior_dir host:src_dir/ new_dir/
```

## File Selection Options

- `--files-from=FILE` — read list of source-file names from file (implies `-R` and `-d`; `-a` no longer implies `-r`)
- `--from0`, `-0` — all `*-from`/filter files delimited by null characters
- `--cvs-exclude`, `-C` — auto-ignore files CVS would ignore
- `--remove-source-files` — sender removes synchronized files after successful transfer

## Other Options

- `--whole-file`, `-W` — copy files whole (disable delta-transfer; default for local copies)
- `--sparse`, `-S` — turn sequences of nulls into sparse blocks
- `--preallocate` — allocate dest files before writing (uses fallocate)
- `--dry-run`, `-n` — trial run with no changes made
- `--super` — receiver attempts super-user activities even if not root
- `--temp-dir=DIR`, `-T` — create temporary files in directory DIR
- `--fsync` — fsync every written file
- `--iconv=CONVERT_SPEC` — charset conversion of filenames (e.g., `--iconv=utf8,iso88591`)
- `--password-file=FILE` — read daemon-access password from file
- `--early-input=FILE` — send data to daemon's early exec script stdin
- `--list-only` — list files instead of copying
- `--no-motd` — suppress daemon-mode message of the day
- `--trust-sender` — trust remote sender's file list (disables extra validation)
- `--copy-as=USER[:GROUP]` — specify user/group for copy operations
- `--secluded-args`, `-s` — send filenames via protocol instead of remote shell command line
- `--old-args` — disable modern arg-protection (for legacy scripts)
- `--protocol=NUM` — force older protocol version
- `--checksum-seed=NUM` — set block/file checksum seed
- `--version`, `-V` — print version and capabilities
- `--help`, `-h` — show help

## Daemon Options

When starting an rsync daemon with `--daemon`:

- `--daemon` — run as rsync daemon
- `--address=ADDRESS` — bind to specific address
- `--bwlimit=RATE` — limit socket I/O bandwidth
- `--config=FILE` — alternate rsyncd.conf file
- `--dparam=OVERRIDE`, `-M` — override global daemon config parameter
- `--no-detach` — don't detach from parent (useful for supervisors/debugging)
- `--port=PORT` — listen on alternate port
- `--log-file=FILE` — override log file setting
- `--log-file-format=FMT` — override log format setting
- `--sockopts=OPTIONS` — custom TCP options
- `--verbose`, `-v` — increase daemon startup verbosity
- `--ipv4`, `-4` / `--ipv6`, `-6` — prefer IPv4/