# Command-Line Options Reference

## Output Control

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Increase verbosity (use `-vv`, `-vvv` for more) |
| `--info=FLAGS` | | Fine-grained informational verbosity (see `rsync --info=help`) |
| `--debug=FLAGS` | | Fine-grained debug verbosity (see `rsync --debug=help`) |
| `--quiet` | `-q` | Suppress non-error messages |
| `--dry-run` | `-n` | Perform trial run, no changes made |
| `--itemize-changes` | `-i` | Output abbreviated itemized list (shows why files are transferred) |
| `--human-readable` | `-h` | Human-readable output for file sizes |
| `--progress` | | Show progress during transfer |
| `-P` | | Same as `--partial --progress` |
| `--stats` | | Give various statistics about the transfer |
| `--out-format=FORMAT` | | Output format of a list operation |
| `--log-file=FILE` | | Write messages to a file instead of stderr |
| `--log-file-format=FORMAT` | | Format for log file entries |
| `--8-bit-output` | `-8` | Don't munge 8-bit characters in output |
| `--no-motd` | | Suppress daemon-mode message-of-the-day |
| `--stderr=e\|a\|c` | | Change stderr output mode (errors, all, client) |

## File-Sync Options

| Option | Short | Description |
|--------|-------|-------------|
| `--archive` | `-a` | Archive mode: `-rlptgoD` (no `-A,-X,-U,-N,-H`) |
| `--recursive` | `-r` | Recurse into directories |
| `--inc-recursive` / `--i-r` | | Incremental recursion (default in 3.0.0+) |
| `--dirs` | `-d` | Transfer directories without recursing |
| `--relative` | `-R` | Use relative path names |
| `--no-implied-dirs` | | Don't send implied dirs with --relative |
| `--times` | `-t` | Preserve modification times |
| `--super` | | Receiver attempts super-user activities |
| `--fake-super` | | Store/recover privileged attrs using xattrs |
| `--safe-links` | | Ignore symlinks pointing outside the tree |
| `--copy-dirlinks` | `-k` | Transform symlink to dir into referent dir |
| `--keep-dirlinks` | `-K` | Treat symlinked dir on receiver as dir |
| `--delete` | | Delete extraneous files from destination dirs |
| `--delete-before` | | Receiver deletes before transfer |
| `--delete-during` / `--del` | | Receiver deletes during xfer |
| `--delete-delay` | | Delete after transfer, collecting names during |
| `--delete-after` | | Receiver deletes after transfer |
| `--delete-excluded` | | Also exclude extraneous files in excluded dirs |
| `--ignore-errors` | | Delete even if there are I/O errors |
| `--force` | | Force deletion of directories |
| `--max-delete=NUM` | | Don't delete more than NUM files |
| `--max-size=SIZE` | | Don't transfer any file larger than SIZE |
| `--min-size=SIZE` | | Don't transfer any file smaller than SIZE |
| `--partial` | | Keep partially transferred files |
| `--partial-dir=DIR` | | Put a partially transferred file in DIR |
| `--timeout=SECONDS` | | Timeout server I/O after SECONDS |
| `--contimeout=SECONDS` | | Timeout daemon connection to SECONDS |
| `--no-OPTION` | | Turn off an implied OPTION (e.g., --no-D) |

## Backup Options

| Option | Description |
|--------|-------------|
| `--backup` / `-b` | Make backups of destination files |
| `--backup-dir=DIR` | Make backups into hierarchy based in DIR |
| `--suffix=SUFFIX` | Backup suffix (default `~` without --backup-dir) |
| `--update` / `-u` | Skip files newer on receiver |
| `--inplace` | Update destination files in-place |
| `--append` | Append data onto shorter files |
| `--append-verify` | --append with old data checksum verification |
| `--remove-source-files` | Sender removes source files after transfer |
| `--mkpath` | Create destination's missing path components |
| `--fuzzy` / `-y` | Fuzzy match against existing files (finds similar names) |
| `--compare-dest=DIR` | Also compare against files in DIR |
| `--copy-dest=DIR` | Like --compare-dest but includes deletions |
| `--link-dest=DIR` | Reference to a previous transfer for hard-linking identical files |
| `--delay-updates` | Put all updated files under place at end of xfer |

## File Selection (Filter Rules)

| Option | Description |
|--------|-------------|
| `--exclude=PATTERN` | Exclude files matching PATTERN |
| `--exclude-from=FILE` | Read exclude patterns from FILE |
| `--include=PATTERN` | Include files matching PATTERN |
| `--include-from=FILE` | Read include patterns from FILE |
| `--files-from=FILE` | Read list of source-file names from FILE |
| `--from0` / `-0` | All file lists are delimited by NULs (--from0, --files-from) |
| `--cvs-exclude` / `-C` | Auto-ignore files same way CVS would (ignores all) |
| `--filter=RULE` / `-f` | Add a file-filtering RULE |
| `-F` | Pass -F option(s) to the remote side (use once or twice for -F -F) |

## Attribute Preservation

| Option | Short | Description |
|--------|-------|-------------|
| `--links` | `-l` | Copy symlinks as symlinks |
| `--copy-links` / `-L` | | Transform symlink into referent file/dir |
| `--copy-unsafe-links` | | Only "unsafe" symlinks are transformed |
| `--munge-links` | | Munge symlinks to make them safe & unusable |
| `--hard-links` / `-H` | | Preserve hard links |
| `--perms` | `-p` | Preserve permissions |
| `--executability` / `-E` | | Preserve executability |
| `--chmod=CHMOD` | | Affect file and/or directory permissions |
| `--acls` / `-A` | | Preserve ACLs (implies --perms) |
| `--xattrs` / `-X` | | Preserve extended attributes |
| `--owner` | `-o` | Preserve owner (super-user only) |
| `--group` | `-g` | Preserve group |
| `--devices` | | Preserve device files (super-user only) |
| `--copy-devices` | | Copy device contents as a regular file |
| `--write-devices` | | Write to devices as files (implies --inplace) |
| `--specials` | | Preserve special files |
| `-D` | | Same as `--devices --specials` |
| `--atimes` / `-U` | | Preserve access (use) times |
| `--open-noatime` | | Avoid changing the atime on opened files |
| `--crtimes` / `-N` | | Preserve create times (newness) |
| `--omit-dir-times` / `-O` | | Omit directories from --times |
| `--omit-link-times` / `-J` | | Omit symlinks from --times |
| `--sparse` / `-S` | | Turn sequences of nulls into sparse blocks |
| `--preallocate` | | Allocate dest files before writing them |

## Network/Transport Options

| Option | Short | Description |
|--------|-------|-------------|
| `--compress` / `-z` | | Compress file data during transfer |
| `--compress-choice=STR` / `--zc=STR` | | Choose the compression algorithm |
| `--compress-level=NUM` / `--zl=NUM` | | Set compression level (1-9) |
| `--skip-compress=LIST` | | Skip compressing listed file extensions |
| `--whole-file` / `-W` | | Copy files whole (without delta algorithm) |
| `--no-whole-file` / `--no-W` | | Turn off --whole-file |
| `--checksum-choice=STR` / `--cc=STR` | | Choose the checksum algorithm |
| `--checksum` / `-c` | | Skip based on checksum, not mod-time & size |
| `--block-size=SIZE` / `-B` | | Force a specific block size (disables auto) |
| `--rsh=COMMAND` / `-e` | | Specify the remote shell program |
| `--rsync-path=PROGRAM` | | Specify rsync path on remote side |
| `--remote-option=OPTION` / `-M` | | Pass an option to the remote side |
| `--one-file-system` / `-x` | | Don't cross filesystem boundaries |
| `--existing` | | Skip creating new files on receiver |
| `--ignore-non-existing` | | Same as --existing |
| `--ignore-existing` | | Skip updating existing files on receiver |
| `--bwlimit=RATE` | | Limit I/O bandwidth (KBytes/sec) |
| `--stop-after=MINS` / `--time-limit=MINS` | | Stop after specified minutes have elapsed |
| `--stop-at` | | Stop at a specific timestamp (y-m-dTh:m format) |
| `--address=ADDRESS` | | Bind to a specific address |
| `--port=PORT` | | Specify alternate rsync port number |
| `--sockopts=OPTIONS` | | Specify custom socket options |
| `--blocking-io` | | Use blocking I/O for the remote shell |
| `--outbuf=MODE` | | Set output buffering (None, Line, Block) |
| `--ipv4` / `-4` | | Prefer IPv4 |
| `--ipv6` / `-6` | | Prefer IPv6 |
| `--protocol=NUM` | | Force a specific protocol version |
| `--iconv=CONVERT_SPEC` | | Request charset conversion of filenames |
| `--checksum-seed=NUM` | | Set block/file checksum algorithm seed |

## Authentication & Security

| Option | Description |
|--------|-------------|
| `--password-file=FILE` | Get password from FILE |
| `--trust-sender` | Trust the sender with file list (less safe) |
| `--secluded-args` / `-s` | Seclude remote args from shell processing |
| `--usermap=STRING` / `--groupmap=STRING` | Map remote user/group to local |
| `--chown=USER:GROUP` | Change destination file ownership |
| `--numeric-ids` | Don't map numeric IDs to user/group names |
| `--ignore-times` / `-I` | Don't skip files that match in size and mod-time |
| `--size-only` | Skip based on size alone (not mod-time) |
| `--modify-window=NUM` / `-@` | Set time comparison precision window |

## Batch Mode

| Option | Description |
|--------|-------------|
| `--write-batch=FILE` | Write a batch file of all changed files |
| `--only-write-batch=FILE` | Like --write-batch but no actual transfer |
| `--read-batch=FILE` | Read and apply a batch file |
| `--fsync` | Sync files after writing them |

## Ignore/Exclude Patterns

Common `.cvsignore`-style patterns (used by `-C` or `--cvs-exclude`):
```
# Skip backup files
*.bak
*~

# Skip version control directories
CVS
.svn
.git
.hg

# Skip build artifacts
*.o
*.pyc
__pycache__/
node_modules/

# Skip editor swap files
.*.swp
.*.swo
```

## Filter Rules (Advanced)

Filter rules are processed in order. The `-f` option adds rules:

```bash
# Simple exclude
rsync -av --exclude='*.log' src/ dest/

# Include then exclude (order matters!)
rsync -av --include='PATTERN' --exclude='*' src/ dest/

# Negate a pattern
rsync -av '-f + PATTERN' '-f - *' src/ dest/

# Per-directory .rsync-filter files
rsync -av -F src/ dest/    # One -F for .rsync-filter, two for both
```

Key filter rule prefixes:
- `- PATTERN` or `exclude:PATTERN` — Exclude matching files
- `+ PATTERN` or `include:PATTERN` — Include matching files
- `-! PATTERN` — Clear the include/exclude list
- `/- PATTERN` — Per-directory exclude (from .rsync-filter)
- `/+ PATTERN` — Per-directory include
- `:C PATTERN` — C-style include/exclude
- `:R PATTERN` — Regex-based pattern
- `:W PATTERN` — Wildcard-based pattern
- `:N PATTERN` — Name-only pattern (no recursion)
- `:M PATTERN` — Match only directories
- `:T PATTERN` — Match only files

### Pattern Matching Rules
- Patterns are matched against the **basename** of each file unless anchored with `/`
- A leading `/` anchors to the source directory
- A trailing `/` matches only directories
- `*` matches everything, `?` matches single character
- `[abc]` matches any character in brackets

## Environment Variables

| Variable | Description |
|----------|-------------|
| `RSYNC_RSH` | Default remote shell program (overrides `-e`) |
| `RSYNC_PORT` | Default port number for daemon connections |
| `RSYNC_PASSWORD` | Password for authenticated daemon connections |
| `RSYNC_PROXY` | HTTP proxy host:port for daemon connections through a web proxy |
| `RSYNC_CONNECT_PROG` | Custom program to connect to remote (e.g., `ssh proxyhost nc %H 873`) |
| `RSYNC_SHELL` | Shell used by RSYNC_CONNECT_PROG |
| `RSYNC_OLD_ARGS` | Enable old-style argument splitting for scripts |
| `RSYNC_PROTECT_ARGS` | Protect arguments from shell processing (default 1) |
| `RSYNC_PARTIAL_DIR` | Default partial directory for interrupted transfers |
| `RSYNC_COMPRESS_LIST` | Space-separated list of compressible file extensions |
| `RSYNC_CHECKSUM_LIST` | Space-separated list of checksum algorithms to try |
| `RSYNC_MAX_ALLOC` | Maximum memory allocation size |
| `RSYNC_ICONV` | Default iconv conversion spec |
| `CVSIGNORE` | Patterns to add to cvs-exclude mode |
| `USER` / `LOGNAME` | Used in rsyncd.conf for per-user paths |
| `HOME` | Used for finding rsyncd.conf in non-root scenarios |

## Exit Values

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Syntax or usage error |
| 2 | Protocol compatibility error |
| 3 | Supplied by source during transfer |
| 4 | Some errors detected (e.g., --ignore-errors not set) |
| 10 | Error starting client-server protocol |
| 11 | Fatal server error |
| 12 | Bad socket connection |
| 13 | Cannot allocate memory |
| 14 | Bad file descriptor |
| 20-24 | Various I/O errors (24 = vanished files during transfer) |

## Daemon-Specific Options

Options for `rsync --daemon`:

| Option | Description |
|--------|-------------|
| `--config=FILE` | Alternate config file path |
| `--dparam=OVERRIDE` / `-M` | Override a rsyncd.conf parameter |
| `--no-detach` | Don't detach and become background process |
| `--log-file=FILE` | Alternate log file path |
| `--log-file-format=FORMAT` | Log format string |

## rsyncd.conf Global Parameters

Parameters before any `[module]` section:

| Parameter | Description |
|-----------|-------------|
| `motd file` | Message of the day file path |
| `pid file` | PID file path |
| `port` | Daemon listen port (default 873) |
| `address` | IP address to bind to |
| `socket options` | TCP socket options string |
| `listen backlog` | Connection backlog (default 5) |
