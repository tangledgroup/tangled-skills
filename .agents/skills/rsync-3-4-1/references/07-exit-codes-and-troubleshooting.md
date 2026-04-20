# Exit Codes and Troubleshooting

## Exit Codes

| Code | Meaning |
|------|---------|
| **0** | Success |
| **1** | Syntax or usage error |
| **2** | Protocol incompatibility |
| **3** | Errors selecting input/output files, dirs |
| **4** | Requested action not supported (e.g., 64-bit files on unsupported platform) |
| **5** | Error starting client-server protocol |
| **6** | Daemon unable to append to log-file |
| **10** | Error in socket I/O |
| **11** | Error in file I/O |
| **12** | Error in rsync protocol data stream (connection broken) |
| **13** | Errors with program diagnostics |
| **14** | Error in IPC code |
| **20** | Received SIGUSR1 or SIGINT (interrupted) |
| **21** | Some error returned by waitpid() |
| **22** | Error allocating core memory buffers |
| **23** | Partial transfer due to error |
| **24** | Partial transfer due to vanished source files |
| **25** | The `--max-delete` limit stopped deletions |
| **30** | Timeout in data send/receive |
| **35** | Timeout waiting for daemon connection |

## Common Errors and Fixes

### "protocol version mismatch -- is your shell clean?"

**Cause:** Remote shell startup scripts (`.bashrc`, `.profile`, `.cshrc`) are outputting text that corrupts the rsync data stream.

**Diagnosis:**
```bash
ssh remotehost /bin/true > out.dat
cat out.dat   # Should be empty
```

**Fix:** Remove or guard output statements in shell startup scripts:
```bash
# In ~/.bashrc — only output when interactive
if [ -z "$PS1" ]; then return; fi
```

### "error writing X unbuffered bytes — exiting: Broken pipe" / code 12

**Cause:** The connection to the remote rsync was lost during transfer.

**Common causes:**
- Destination disk is full
- Idle connection closed by router/firewall
- Network error
- Remote rsync not found
- Shell not clean (see above)

**Debugging:**
```bash
# Get more detail from the remote side
rsync -av --msgs2stderr /src/ user@host:/dest/

# Test connectivity
echo hi | ssh HOST cat
ssh HOST rsync --version

# Check remote daemon logs
tail -f /var/log/rsyncd.log
```

**Fixes:**
- Ensure destination has enough free space (need space for largest file)
- Use `--timeout` to handle idle connections:
  ```bash
  rsync -avz --timeout=300 /src/ user@host:/dest/
  ```
- Switch from `--delete` to `--delete-during` or `--delete-delay`
- Configure SSH keep-alives in `~/.ssh/config`:
  ```
  Host backup-server
      ServerAliveInterval 60
      ServerAliveCountMax 3
  ```

### "rsync: Command not found"

**Cause:** rsync is not in the PATH on the remote system.

**Fixes:**
```bash
# Option 1: Install rsync in a standard location
ssh host 'which rsync'   # Find current path
ssh host 'echo $PATH'    # Check remote PATH

# Option 2: Specify explicit remote path
rsync -av --rsync-path=/usr/local/bin/rsync /src/ user@host:/dest/

# Option 3: Modify remote PATH in .bashrc or .profile
```

### "out of memory"

**Cause:** Transferring a very large number of files.

**Fixes:**
- Upgrade both sides to rsync 3.0.0+ (enables incremental recursion)
- Use `--delete-delay` instead of `--delete-before`
- Break into smaller chunks using `--relative` or exclude rules
```bash
# Process subdirectories individually
for dir in /src/*/; do
    rsync -av "$dir" /dest/
done
```

### "Read-only file system" (daemon)

**Cause:** Module has `read only = yes` (the default).

**Fix:** Set `read only = no` in the module's rsyncd.conf entry.

### "vanished files" warning (exit code 24)

**Cause:** Source files were deleted during transfer.

**Suppress:**
```bash
#!/bin/bash
# Wrapper script to suppress exit code 24
rsync "$@"
e=$?
if test $e = 24; then exit 0; fi
exit $e
```

### "inflate (token) returned -5"

**Cause:** Compression error on a file transferred with block size of 32816 bytes.

**Fix:**
```bash
# Set custom block size
rsync -av --block-size=33000 /src/ /dest/

# Or upgrade the receiving side to rsync 3.0.7+
```

### "multiplexing overflow 101:7104843" or "invalid message 101:..."

**Cause:** An rsync process was killed, and a "Kill" message was inserted into the protocol stream.

**Fix:** Investigate why rsync is being killed (OOM killer, signal, etc.).

### "is your shell clean" via daemon (no remote shell)

**Cause:** Error on the server side in the daemon.

**Fix:** Check the daemon log file and ensure `log file` is configured correctly in rsyncd.conf.

## Debugging Techniques

### Increase Verbosity
```bash
# Normal verbose
rsync -av /src/ /dest/

# Extra verbose (shows skipped files)
rsycn -avv /src/ /dest/

# Fine-grained info control
rsync -a --info=progress2,stats2 /src/ /dest/

# Debug filter rules
rsync -avv --debug=FILTER /src/ /dest/
```

### Itemized Output
```bash
# Show what would change (without making changes)
rsync -avn /src/ /dest/

# Itemize changes with verbose
rsync -avi /src/ /dest/
```

The itemized output shows a code for each file:
- `.` = unchanged
- `f` = regular file being transferred
- `dF` = directory + files
- `>f` = local file being updated
- `<f` = remote file being received
- `*.x..` = excluded

### strace Debugging (Daemon)
```bash
# Run daemon under strace for debugging
ulimit -c unlimited
strace -f -t -s 1024 -o /tmp/rsync-debug.out rsync --daemon --no-detach
# Then run the failing transfer in another window
kill %1    # Stop the debug daemon
cat /tmp/rsync-debug.out
```

### Debug Script for Remote Side
Create `/usr/local/bin/rsync-debug` on the remote host:
```bash
#!/bin/sh
ulimit -c unlimited
strace -f -t -s 1024 -o /tmp/rsync-strace.out.$$ rsync --server "$@"
```

Usage:
```bash
rsync -av --rsync-path=/usr/local/bin/rsync-debug host:/src/ /dest/
```

### Checksum Verification
```bash
# Use checksums instead of mod-time (slower, more thorough)
rsync -ac /src/ /dest/

# Verify transferred files have correct checksums
# (rsync always verifies whole-file checksums after transfer by default)
```

## Performance Tips

### Reduce Network Transfer
```bash
# Compress data during transfer
rsync -avz /src/ user@host:/dest/

# Use faster compression
rsync -avz --compress-choice=zstd --compress-level=3 /src/ /dest/

# Skip compressing already-compressed files
rsync -avz --skip-compress='.jpg .png .mp4 .zip .gz' /src/ /dest/
```

### Reduce Disk I/O
```bash
# Use inplace mode (writes directly to destination file)
rsync -a --inplace /src/ /dest/

# Use sparse files for files with lots of null bytes
rsync -aS /src/ /dest/

# Use temp directory for faster writes
rsync -a -T /tmp/fast-disk/ /src/ /dest/
```

### Bandwidth Limiting
```bash
# Limit to 1 MB/s
rsync -av --bwlimit=1000 /src/ /dest/

# Limit to 100 KB/s
rsync -av --bwlimit=100 /src/ /dest/
```
