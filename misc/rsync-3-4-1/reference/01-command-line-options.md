# Command-Line Options

## Option Syntax

Rsync accepts both long (`--option`) and short (`-o`) forms. Parameters can be specified as `--option=value`, `--option value`, `-o=value`, `-o value`, or `-ovalue`. Use `--no-OPTION` to disable an implied option (e.g., `--no-D`).

## Transfer Options

### Archive and Recursion

- `--archive`, `-a` — archive mode: `-rlptgoD` (no `-A`, `-X`, `-U`, `-N`, `-H`)
- `--recursive`, `-r` — recurse into directories
- `--dirs`, `-d` — transfer directories without recursing
- `--links`, `-l` — copy symlinks as symlinks (implied by `-a`)
- `--copy-links`, `-L` — transform symlink into referent file/dir
- `--copy-unsafe-links` — only "unsafe" symlinks are transformed
- `--safe-links` — ignore symlinks that point outside the tree
- `--munge-links` — munge symlinks to make them safe & unusable
- `--copy-dirlinks`, `-k` — transform symlink to dir into referent dir
- `--keep-dirlinks`, `-K` — treat symlinked dir on receiver as dir
- `--hard-links`, `-H` — preserve hard links

### Permissions and Ownership

- `--perms`, `-p` — preserve permissions (implied by `-a`)
- `--executability`, `-E` — preserve executability when `--perms` is off
- `--chmod=CHMOD` — affect file and/or directory permissions
  - Prefix with `D` for directories only, `F` for files only
  - Example: `--chmod=Dg+s,ug+w,Fo-w,+X` or `--chmod=D2755,F644`
- `--acls`, `-A` — preserve ACLs (implies `--perms`)
- `--xattrs`, `-X` — preserve extended attributes
  - Use `-XX` to copy all xattrs including rsync's special values
  - Filter xattr names with `--filter='-x system.*'` or `--filter='-x! user.*'`
- `--owner`, `-o` — preserve owner (super-user only, implied by `-a`)
- `--group`, `-g` — preserve group (implied by `-a`)
- `--devices` — transfer character and block device files
- `--specials` — transfer named sockets and fifos
- `-D` — shorthand for `--devices --specials`
- `--copy-devices` — copy device contents as a regular file (refused by daemon by default)
- `--write-devices` — write to devices as files (implies `--inplace`)
- `--numeric-ids` — don't map uid/gid values by user/group name
- `--usermap=STRING` — custom username mapping (`FROM:TO,from2:to2`)
- `--groupmap=STRING` — custom groupname mapping
- `--chown=USER:GROUP` — force all files to be owned by USER:GROUP

### Time Preservation

- `--times`, `-t` — preserve modification times (implied by `-a`)
- `--atimes`, `-U` — preserve access (use) times; repeated also sets `--open-noatime`
- `--crtimes`, `-N` — preserve create times (newness)
- `--omit-dir-times`, `-O` — omit directories from time preservation
- `--omit-link-times`, `-J` — omit symlinks from time preservation
- `--open-noatime` — avoid changing atime on opened files
- `--modify-window=NUM`, `-@` — set accuracy for mod-time comparisons (useful for FAT filesystems)

### Super-User Activities

- `--super` — receiver attempts super-user activities even if not run as root
- `--fake-super` — store/recover privileged attrs using xattrs (allows backup without root)
  - For remote side: `rsync -av -M--fake-super /src/ host:/dest/`
  - Use `--super` to override, or `--no-super` to disable

### File Content Options

- `--sparse`, `-S` — turn sequences of nulls into sparse blocks
- `--preallocate` — allocate dest files before writing (uses fallocate)
- `--inplace` — update destination files in-place (avoids tmp file, but risks data loss on interrupt)
- `--append` — append data onto shorter files
- `--append-verify` — `--append` with old data checksum verification
- `--fsync` — fsync every written file for durability

### Transfer Algorithm

- `--whole-file`, `-W` — copy files whole (disable delta-transfer algorithm)
  - Default for local copies; useful when bandwidth > disk I/O speed
- `--checksum`, `-c` — skip based on checksum, not mod-time & size
- `--checksum-choice=STR`, `--cc=STR` — choose checksum algorithm
  - Available: `auto`, `xxh128`, `xxh3`, `xxh64` (aka `xxhash`), `md5`, `md4`, `sha1`, `none`
  - Two comma-separated names: first for transfer, second for pre-transfer (`-c`)
  - Customize default via `RSYNC_CHECKSUM_LIST` environment variable
- `--block-size=SIZE`, `-B` — force a fixed checksum block-size
- `--ignore-times`, `-I` — don't skip files that match size and time
- `--size-only` — skip files that match in size only

### Update Selection

- `--update`, `-u` — skip files that are newer on the receiver
- `--existing` / `--ignore-non-existing` — skip creating new files on receiver
- `--ignore-existing` — skip updating files that already exist on receiver
- `--remove-source-files` — sender removes synchronized files after successful transfer
  - Only use on quiescent files; ensure files are fully written before rsync sees them

## Delete Options

- `--delete` — delete extraneous files from dest dirs (only for dirs being synced)
  - **Dangerous if used incorrectly!** Always try `--dry-run` first
  - Automatically disabled if sender detects I/O errors (use `--ignore-errors` to override)
  - Requires the directory itself in the transfer (`dir` or `dir/`, not `dir/*`)
- `--delete-before` — delete before transfer starts (helpful when filesystem is tight on space)
- `--delete-during`, `--del` — delete incrementally during transfer (default for rsync 3.0.0+)
- `--delete-delay` — compute deletions during, remove after transfer completes
- `--delete-after` — delete after transfer completes (useful with per-directory merge files)
- `--delete-excluded` — also delete excluded files from dest dirs
- `--ignore-missing-args` — ignore missing source args without error
- `--delete-missing-args` — delete corresponding destination files for missing source args
- `--ignore-errors` — proceed with deletion even when I/O errors occur
- `--force` — delete a non-empty directory when replaced by a non-directory
- `--max-delete=NUM` — don't delete more than NUM files (use `0` to warn without deleting)

## Compression

- `--compress`, `-z` — compress file data during transfer
- `--compress-choice=STR`, `--zc=STR` — choose compression algorithm
  - Run `rsync --version` to see available algorithms
  - Customize default via `RSYNC_COMPRESS_LIST` environment variable
- `--compress-level=NUM`, `--zl` — explicitly set compression level
- `--skip-compress=LIST` — skip compressing files with suffix in LIST (slash-separated)
  - Default skip list includes: gz, jpg, mp3, mp4, zip, bz2, png, rar, xz, tgz, and many more

## Size Limits

- `--max-size=SIZE` — don't transfer any file larger than SIZE
  - Suffixes: `B`, `K`, `M`, `G`, `T`, `P` (or `KiB`, `MiB`, etc.)
  - Offset: `+1` or `-1` (e.g., `--max-size=1.5mb-1` = 1499999 bytes)
- `--min-size=SIZE` — don't transfer any file smaller than SIZE

## Connection Options

- `--rsh=COMMAND`, `-e` — specify the remote shell (default: ssh)
  - Examples: `-e 'ssh -p 2234'`, `-e 'ssh -o "ProxyCommand nc %h %p"'`
  - Set via `RSYNC_RSH` environment variable
- `--rsync-path=PROGRAM` — specify the rsync binary on the remote machine
- `--address=ADDRESS` — bind address for outgoing socket to daemon
- `--port=PORT` — alternate TCP port (default: 873)
- `--contimeout=SECONDS` — connection timeout for daemon connections
- `--timeout=SECONDS` — I/O timeout in seconds (0 = no timeout)
- `--ipv4`, `-4` / `--ipv6`, `-6` — prefer IPv4 or IPv6
- `--sockopts=OPTIONS` — custom TCP socket options
- `--blocking-io` — use blocking I/O for remote shell (default for rsh/remsh)

### Daemon Connection via Remote Shell

Use `--rsh` with double-colon syntax to run a daemon over SSH:

```bash
rsync -av --rsh=ssh host::module /dest
```

This encrypts the transfer while using daemon features (named modules). For different SSH and rsync users:

```bash
rsync -av -e "ssh -l ssh-user" rsync-user@host::module /dest
```

### Proxy Support

- `RSYNC_PROXY` — hostname:port for web proxy to daemon connections
- `RSYNC_CONNECT_PROG` — program to use instead of direct socket connection
  - Example: `export RSYNC_CONNECT_PROG='ssh proxyhost nc %H 873'`

## Output and Logging

- `--verbose`, `-v` — increase verbosity (1x = transferred files, 2x = skipped too)
- `--info=FLAGS` — fine-grained informational verbosity
  - `--info=progress2` — overall transfer progress (not per-file)
  - `--info=flist0 --progress` — progress without file listing
  - `--info=skip2` — show why files are skipped with detail
- `--debug=FLAGS` — fine-grained debug verbosity
- `--stderr=e|a|c` — stderr output mode: errors, all, or changes
- `--quiet`, `-q` — suppress non-error messages
- `--no-motd` — suppress daemon-mode message of the day
- `--stats` — print verbose transfer statistics (equivalent to `--info=stats2`)
- `--progress` — show per-file progress during transfer
- `-P` — shorthand for `--partial --progress`
- `--itemize-changes`, `-i` — output change-summary for all updates
  - Format: `YXcstpoguax` where Y = update type, X = file type, rest = attribute changes
- `--out-format=FORMAT` — custom per-update output format
- `--log-file=FILE` — log what rsync is doing to a file
- `--log-file-format=FMT` — customize log file format
- `--8-bit-output`, `-8` — leave high-bit chars unescaped in output
- `--human-readable`, `-h` — output numbers in human-readable format
  - 1x `-h`: digit separators, 2x: units of 1000 (K/M/G), 3x: units of 1024

### Itemize-Changes Output (`-i`)

The `%i` escape produces an 11-character string: `YXcstpoguax`

**Update types (Y):**
- `<` — sent to remote host
- `>` — received from remote host
- `c` — local change/creation
- `h` — hard link to another item
- `.` — not being updated
- `*` — message (e.g., "deleting")

**File types (X):**
- `f` — file, `d` — directory, `L` — symlink, `D` — device, `S` — special

**Attribute letters:**
- `c` — checksum differs, `s` — size changed, `t`/`T` — time changed/set
- `p` — permissions, `o` — owner, `g` — group
- `u` — atime, `n` — ctime, `b` — both atime and ctime
- `a` — ACLs, `x` — extended attributes

## Backup Options

- `--backup`, `-b` — make backups of overwritten files
- `--backup-dir=DIR` — make backups into hierarchy based in DIR
- `--suffix=SUFFIX` — backup suffix (default: `~` without `--backup-dir`)
- `--delay-updates` — put all updated files into place at end of transfer
  - Places tmp files in `.~tmp~` directory, renames all at once
  - More atomic updating; conflicts with `--inplace` and `--append`

## Partial Transfer Options

- `--partial` — keep partially transferred files on interrupt
- `--partial-dir=DIR` — put partial files into a staging directory
  - Relative path: auto-created and excluded from transfer
  - Use `--partial-dir=.rsync-tmp` with `-P` for safe resume transfers
  - Set via `RSYNC_PARTIAL_DIR` environment variable

## File Selection

- `--one-file-system`, `-x` — don't cross filesystem boundaries
  - Repeated (`-xx`) omits mount-point directories entirely
- `--prune-empty-dirs`, `-m` — prune empty directory chains from file-list
- `--fuzzy`, `-y` — find similar file for basis if no dest file (by size/time or name)
  - Repeated: also scan `--compare-dest`/`--copy-dest`/`--link-dest` dirs

## Alternate Destination Directories

- `--compare-dest=DIR` — compare against DIR; skip transfer if identical file found there
  - Multiple `--compare-dest` directories searched in order
  - Relative path is relative to destination directory
- `--copy-dest=DIR` — like `--compare-dest`, but also local-copy unchanged files to dest
- `--link-dest=DIR` — hardlink to files in DIR when unchanged (efficient rotating backups)

## Filter and Exclude Options

- `--filter=RULE`, `-f` — add a file-filtering RULE
- `-F` — first use: `--filter='dir-merge /.rsync-filter'`; repeated: `--filter='- .rsync-filter'`
- `--exclude=PATTERN` — exclude files matching PATTERN (shorthand for `-f'- PATTERN'`)
- `--exclude-from=FILE` — read exclude patterns from FILE
- `--include=PATTERN` — include files matching PATTERN (shorthand for `-f'+ PATTERN'`)
- `--include-from=FILE` — read include patterns from FILE
- `--cvs-exclude`, `-C` — auto-ignore files the same way CVS does
  - Excludes: RCS, SCCS, CVS, .svn/, .git/, .hg/, *.o, *.bak, core, and more
  - Also reads `$HOME/.cvsignore`, `$CVSIGNORE`, and per-directory `.cvsignore`
- `--files-from=FILE` — read list of source-file names from FILE (`-` for stdin)
  - Implies `--relative` and `--dirs`; `-a` does not imply `--recursive` with this option
  - Remote file: `--files-from=:remote-path` or `--files-from=host:path`
  - Sorting the input file improves efficiency

## Batch Mode Options

- `--write-batch=FILE` — write a batched update to FILE (also creates `.sh` helper script)
- `--only-write-batch=FILE` — like `--write-batch` but without updating destination
- `--read-batch=FILE` — read a batched update from FILE (`-` for stdin)

## Advanced Options

- `--relative`, `-R` — use relative path names (important with `--files-from`)
- `--no-implied-dirs` — don't send implied dirs with `--relative`
- `--mkpath` — create destination's missing path components
- `--from0`, `-0` — all *-from/filter files are delimited by nulls
- `--secluded-args`, `-s` — send args via protocol (not remote shell command line)
  - Incompatible with rsync prior to 3.0.0; refused by restricted shells
  - Set via `RSYNC_PROTECT_ARGS` environment variable
- `--old-args` — disable modern arg-protection (for legacy scripts)
  - Set via `RSYNC_OLD_ARGS` environment variable
- `--trust-sender` — trust the remote sender's file list (disables validation checks)
- `--copy-as=USER[:GROUP]` — specify user/group for copy operations (drops privileges)
- `--remote-option=OPT`, `-M` — send OPTION to the remote side only
  - Example: `rsync -av -M--fake-super src/ host:/dest/`
- `--temp-dir=DIR`, `-T` — create temporary files in directory DIR
- `--iconv=CONVERT_SPEC` — request charset conversion of filenames
  - Format: `--iconv=LOCAL,REMOTE` (e.g., `--iconv=utf8,iso88591`)
  - Set via `RSYNC_ICONV` environment variable
- `--protocol=NUM` — force an older protocol version
- `--checksum-seed=NUM` — set block/file checksum seed (advanced)
- `--password-file=FILE` — read daemon-access password from FILE
- `--early-input=FILE` — send up to 5K of data to daemon's early exec script
- `--list-only` — list files instead of copying them
- `--bwlimit=RATE` — limit socket I/O bandwidth (in KiB/s by default)
  - Suffixes: `K`, `M`, `G` etc. (e.g., `--bwlimit=1.5m`)
- `--stop-after=MINS` — stop rsync after MINS minutes have elapsed
- `--stop-at=y-m-dTh:m` — stop rsync at specified point in time
  - Abbreviated forms: `14:00` (next 2 PM), `1-30` (next Jan 30)
- `--max-alloc=SIZE` — change per-allocation memory limit (default: ~1GB)
  - Set to `0` for SIZE_MAX; set via `RSYNC_MAX_ALLOC` environment variable

## Daemon Options (when running `rsync --daemon`)

- `--daemon` — run as an rsync daemon
- `--config=FILE` — specify alternate rsyncd.conf file
- `--dparam=OVERRIDE`, `-M` — override global daemon config parameter
- `--no-detach` — do not detach from the parent (useful for debugging)

## Version and Help

- `--version`, `-V` — print version + compiled-in capabilities
  - Repeated: output in JSON format
- `--help` / `-h` (alone) — show help

## Exit Values

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Syntax or usage error |
| 2 | Protocol incompatibility |
| 3 | Errors selecting input/output files, dirs |
| 4 | Requested action not supported |
| 5 | Error starting client-server protocol |
| 6 | Daemon unable to append to log-file |
| 10 | Error in socket I/O |
| 11 | Error in file I/O |
| 12 | Error in rsync protocol data stream |
| 13 | Errors with program diagnostics |
| 14 | Error in IPC code |
| 20 | Received SIGUSR1 or SIGINT |
| 21 | Some error returned by waitpid() |
| 22 | Error allocating core memory buffers |
| 23 | Partial transfer due to error |
| 24 | Partial transfer due to vanished source files |
| 25 | The --max-delete limit stopped deletions |
| 30 | Timeout in data send/receive |
| 35 | Timeout waiting for daemon connection |

## Environment Variables

- `RSYNC_RSH` — override default remote shell program
- `RSYNC_PASSWORD` — password for daemon authentication (not for SSH)
- `RSYNC_PROXY` — hostname:port for web proxy to daemon connections
- `RSYNC_CONNECT_PROG` — program for daemon connections (uses `%H` for hostname)
- `RSYNC_SHELL` — shell to run `RSYNC_CONNECT_PROG` with
- `RSYNC_ICONV` — default `--iconv` setting
- `RSYNC_OLD_ARGS` — enable old-style arg handling (1, 2, or 0)
- `RSYNC_PROTECT_ARGS` — enable secluded-args by default (non-zero)
- `RSYNC_PARTIAL_DIR` — directory for partial transfers
- `RSYNC_COMPRESS_LIST` — customize compression algorithm negotiation
- `RSYNC_CHECKSUM_LIST` — customize checksum algorithm negotiation
- `RSYNC_MAX_ALLOC` — default per-allocation memory limit
- `USER` / `LOGNAME` — default username for daemon connections
