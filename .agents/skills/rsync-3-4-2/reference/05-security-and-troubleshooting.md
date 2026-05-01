# Symbolic Links, Security, and Troubleshooting

## Symbolic Link Handling

Rsync provides several modes for handling symbolic links:

### Default Behavior

Without any link options, symlinks are skipped with a "skipping non-regular file" message.

### Common Modes

- `--links` (`-l`) — recreate symlinks with the same target on destination (implied by `-a`)
- `--copy-links` (`-L`) — collapse all symlinks by copying their referent files
- `--copy-unsafe-links` — copy only "unsafe" symlinks as regular files
- `--safe-links` — receiver skips creating unsafe symlinks, creates safe ones
  - Requires `--links` to be specified or implied
- `--munge-links` — modify symlink targets to make them unusable (prefixes with `/rsyncd-munged/`)

### Safe vs. Unsafe Symlinks

Symlinks are considered **unsafe** if they:
- Are absolute (start with `/`)
- Are empty
- Contain enough `..` components to ascend from the top of the transfer

### Option Precedence

Options are evaluated in this order (first matching subset wins):

1. `--copy-links` — all symlinks become regular files/dirs
2. `--copy-dirlinks` — only directory symlinks become real directories
3. `--links --copy-unsafe-links` — unsafe symlinks become files, safe ones stay as links
4. `--copy-unsafe-links` — unsafe symlinks become files, safe ones are skipped
5. `--links --safe-links` — receiver creates safe symlinks, skips unsafe
6. `--links` — create all symlinks

### Dirlink Options

- `--copy-dirlinks` (`-k`) — on the sender: transform symlinks to directories into real directories
  - To follow only specific symlinks: `rsync -r --relative src/./ src/./follow-me/ dest/`
- `--keep-dirlinks` (`-K`) — on the receiver: treat an existing symlink-to-directory as a real directory
  - **Warning**: trust all symlinks in the copy or enable `--munge-links` on the receiving side
  - An untrusted user could create symlinks to arbitrary directories

## Multi-Host Security

### Trusting Remote Senders

As of version 3.2.5, rsync performs two extra validation checks when pulling from a remote host:

1. Verifies that no extra top-level items were added to the file list
2. Verifies that excluded items don't appear in the file list

Use `--trust-sender` to disable these checks (only for trusted senders).

### Safe Copy Practices

When copying from an untrusted remote host, use a dedicated destination directory:

```bash
# Instead of copying directly into your home directory:
rsync -aiv host1:dir1 ~/host1-files/
```

### Case-Insensitive Filesystem Warnings

Copying from case-preserving to case-ignoring filesystems is unsafe. If necessary:
- Disable symlinks with `--no-links`, or
- Enable `--munge-links`
- Or list source files and create a safe list for `--files-from`

### Copy-as Option

The `--copy-as=USER[:GROUP]` option drops privileges during the copy phase:

```bash
# Run rsync as root for SSH access, but copy as user "joe"
sudo rsync -aiv --copy-as=joe host1:backups/joe/ /home/joe/
```

This limits the risk of a modified path inducing changes to files the copy user cannot modify.

### Restricted Rsync

The `rrsync` script in rsync's support directory provides a restricted shell that only allows rsync commands. Use it with SSH's `authorized_keys` forced command:

```
command="/path/to/rrsync /protected/dir" ssh-ed25519 AAAA...
```

## Common Troubleshooting

### "Protocol version mismatch — is your shell clean?"

This error means the remote shell is outputting garbage before rsync starts. Diagnose with:

```bash
ssh remotehost /bin/true > test.dat
# test.dat should be zero bytes
```

Check `.cshrc`, `.profile`, `.bashrc`, or other startup scripts for non-interactive output statements. Wrap output in interactive-only checks:

```bash
# In .bashrc
if [[ $- == *i* ]]; then
    echo "Welcome!"  # Only shows on interactive shells
fi
```

### Transfer Fails to Finish

Errors like "Broken pipe" or "connection unexpectedly closed":

```
rsync: error writing 4 unbuffered bytes - exiting: Broken pipe
rsync error: error in rsync protocol data stream (code 12)
```

Common causes:
- Firewall or NAT timeout interrupting the connection
- Use `--timeout=SECONDS` to detect dead connections
- Use `--contimeout=SECONDS` for daemon connection timeout
- Check for SSH key prompts or other interactive output
- Try increasing verbosity: `rsync -vvv`

### Rsync Recopies the Same Files

Most common causes:

1. **Missing `-t` in original copy** — without modification times, rsync must transfer every file to check for changes
2. **FAT filesystem odd/even time rounding** — use `--modify-window=1`
3. **Daylight savings time changes** — if OS stores times in local time instead of UTC
4. **Filename charset changes** — e.g., HFS+ decomposing UTF-8 characters
   - Fix with `--iconv=UTF-8,UTF8-MAC` on Mac OS X

Debug with itemized output:

```bash
rsync -ai /source/ /dest/
# 't' flag = time differs, '+' = file doesn't exist
```

### "rsync: Command not found"

The remote shell cannot find rsync in the PATH. Solutions:

1. Install rsync in a standard location
2. Use `--rsync-path=/usr/local/bin/rsync`
3. Check remote PATH: `ssh host 'echo $PATH'`

### Out of Memory

Rsync needs ~100 bytes per file in memory. For 800,000 files, expect ~80MB. Solutions:

1. Upgrade both sides to rsync 3.0.0+ for incremental recursion
2. Use `--delete-delay` instead of `--delete-after`
3. Break transfer into smaller chunks by subdirectory
4. Increase `--max-alloc=SIZE`

### Spaces in Filenames

Rsync handles spaces fine — the issue is shell argument parsing on the remote side:

```bash
# These work:
rsync -av host:'"a long filename"' /tmp/
rsync -av host:'a\ long\ filename' /tmp/
rsync -av host:a\\\ long\\\ filename /tmp/

# Use ? as wildcard for a single character:
rsync -av host:a?long?filename /tmp/
```

Starting with 3.2.4, filenames are passed to preserve special characters. Use `--old-args` for legacy scripts that need old behavior.

### "Read-only file system" Error

When pushing to an rsync daemon, ensure `read only = no` is set for the module.

### "Multiplexing overflow 101:7104843"

This error occurs when an rsync process is killed (often by OOM killer) and "Kill" characters are inserted into the protocol stream. Investigate why rsync is being killed.

### "Inflate (token) returned -5"

Compression code error for files with block size 32816 bytes. Work around with `--block-size=33000` or upgrade to rsync 3.0.7+.

### Ignoring "Vanished Files" Warning (Exit Code 24)

Create a wrapper script:

```bash
#!/bin/sh
rsync "$@"
e=$?
if test $e = 24; then
    exit 0
fi
exit $e
```

### Debugging Filter Patterns

Use `-vv` to see why each file is included or excluded:

```bash
rsync -avv --exclude='*.o' src/ dest/
```

### Rsync and Cron

On some systems (notably SunOS4), cron provides a socket-like stdin that makes rsync think it was started from inetd. Fix by redirecting stdin:

```cron
0 2 * * * rsync --daemon < /dev/null
```

### Rsync Through a Firewall

When direct connection is impossible, options include:

1. **SSH tunnel**: `ssh -L 8730:targethost:873 firewall` then `rsync -av rsync://localhost:8730/module/ /dest/`
2. **RSYNC_CONNECT_PROG**: `export RSYNC_CONNECT_PROG='ssh proxyhost nc %H 873'`
3. **RSYNC_PROXY**: Set to `proxyhost:port` for web proxy support

## Exit Code Reference

| Code | Meaning | Notes |
|------|---------|-------|
| 0 | Success | |
| 1 | Syntax/usage error | Check command-line options |
| 2 | Protocol incompatibility | Version mismatch between client/server |
| 3 | I/O file/directory errors | Check paths and permissions |
| 4 | Action not supported | 64-bit files on 32-bit platform, or unsupported option |
| 5 | Client-server protocol error | Connection setup failure |
| 6 | Daemon log append error | Check log file permissions |
| 10 | Socket I/O error | Network issue |
| 11 | File I/O error | Disk or permission problem |
| 12 | Protocol data stream error | "Broken pipe", dirty shell, killed process |
| 13 | Program diagnostics error | Internal diagnostic failure |
| 14 | IPC code error | Inter-process communication failure |
| 20 | SIGUSR1 or SIGINT received | User interrupted |
| 21 | waitpid() error | Child process issue |
| 22 | Memory allocation error | Out of memory |
| 23 | Partial transfer (error) | Some files transferred, some failed |
| 24 | Vanished source files | Files disappeared during transfer |
| 25 | --max-delete limit reached | Too many extraneous files to delete |
| 30 | Data send/receive timeout | Use --timeout to adjust |
| 35 | Daemon connection timeout | Use --contimeout to adjust |

## Version Information

Check compiled-in capabilities:

```bash
rsync --version
# Shows: checksum algorithms, compression algorithms, optimizations

rsync --version --version
# JSON output format
```
