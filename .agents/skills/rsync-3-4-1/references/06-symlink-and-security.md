# Symlink Handling and Security

## Symlink Options

Rsync supports multiple symlink handling modes. The options are listed in order of precedence (first complete subset wins):

| Combination | Behavior |
|-------------|----------|
| `--copy-links` (`-L`) | Turn ALL symlinks into normal files/directories (collapse the chain) |
| `--links --copy-unsafe-links` | Create safe symlinks; copy unsafe ones as files |
| `--copy-unsafe-links` | Copy only unsafe symlinks as files; skip safe ones |
| `--links --safe-links` | Skip creating unsafe symlinks; create safe ones |
| `--copy-dirlinks` (`-k`) | Treat symlink-to-directory as real directory (on sender) |
| `--keep-dirlinks` (`-K`) | Treat existing symlink-to-dir on receiver as a directory |
| `--munge-links` | Prefix symlink values with `/rsyncd-munged/` to make them unusable |
| `--links` (`-l`) | Copy all symlinks as-is (default when `-a` is used) |

## Safe vs Unsafe Symlinks

A symlink is considered **unsafe** if:
- It is an absolute path (starts with `/`)
- It is empty
- It contains enough `..` components to ascend from the top of the transfer

```bash
# Example: only copy unsafe symlinks as files
rsync -a --copy-unsafe-links /src/ /dest/

# Example: ignore all unsafe symlinks
rsync -aL --safe-links /src/ /dest/
```

## Daemon Symlink Protection

In writable daemon modules, symlinks are munged by default (unless `use chroot = true` with inside-chroot path of `/`, or `daemon chroot` is set). This prevents users from creating symlinks that escape the module directory.

Munging prefixes each symlink value with `/rsyncd-munged/`. The daemon will refuse to start if this path already exists as a directory or symlink.

## CVE-2024 Security Fixes (rsync 3.4.0)

Rsync 3.4.0 is a critical security release fixing 6 vulnerabilities:

| CVE | Description | Severity |
|-----|-------------|----------|
| CVE-2024-12084 | Heap Buffer Overflow in Checksum Parsing | High |
| CVE-2024-12085 | Info Leak via uninitialized Stack contents (defeats ASLR) | High |
| CVE-2024-12086 | Server leaks arbitrary client files | Critical |
| CVE-2024-12087 | Server can make client write files outside destination using symlinks | Critical |
| CVE-2024-12088 | `--safe-links` Bypass | High |
| CVE-2024-12747 | Symlink race condition | High |

**Protocol number changed to 32** to help administrators identify updated servers.

### Mitigations

1. **Upgrade immediately** to rsync 3.4.0 or later
2. Use `--safe-links` with caution (now bypassed in older versions)
3. For daemon modules, ensure `munge symlinks` is enabled on writable shares
4. Consider using SSH as transport instead of direct daemon connections for untrusted sources
5. When copying from untrusted hosts, use a dedicated destination directory

## Security Best Practices

### Copying from Untrusted Hosts

```bash
# Always copy into a dedicated directory
rsync -aiv host1:dir1 ~/host1-files/

# Use --trust-sender only when you trust the remote sender
rsync -aiv --trust-sender host::module /dest/

# For case-insensitive filesystems, disable symlinks
rsync -a --no-links /src/ /dest/
```

### Daemon Security Checklist

1. Set `read only = yes` for public modules
2. Use `auth users` + `secrets file` for private modules
3. Restrict with `hosts allow` / `hosts deny`
4. Enable `munge symlinks` on writable modules
5. Set `max connections` to prevent resource exhaustion
6. Configure `timeout` to prevent idle connection abuse
7. Use `refuse options` to disable dangerous options:
   ```ini
   refuse options = delete delete-during delete-before
   ```

### SSH Transport Security

```bash
# Use SSH key authentication (no password prompts)
rsync -avz -e "ssh -i ~/.ssh/id_rsa" /src/ user@host:/dest/

# Disable host key checking (use with caution!)
rsync -avz -e "ssh -o StrictHostKeyChecking=no" /src/ user@host:/dest/

# Use SSH config for complex setups
# In ~/.ssh/config:
# Host backup-server
#     HostName 10.0.0.5
#     User backup
#     IdentityFile ~/.ssh/backup_key
#     Port 2222

rsync -avz /src/ backup-server:/dest/
```

## Case-Sensitivity Issues

When copying between case-preserving and case-insensitive filesystems:

```bash
# Disable symlinks to prevent dangerous behavior
rsync -a --no-links /src/ /dest/

# Or munge symlinks
rsync -aL --munge-links /src/ /dest/

# Best: list all source files explicitly
find /src -type f | rsync --files-from=- -a / /dest/
```

## Filesystem Timestamp Issues

### FAT/Windows Filesystems

FAT stores times with 2-second resolution. Files with odd millisecond timestamps will be re-copied:

```bash
# Allow 1-second tolerance for FAT filesystems
rsync -a --modify-window=1 /src/ /dest/
```

### Daylight Saving Time

If the OS saves file times in local time instead of UTC, DST changes can cause files to appear modified:

```bash
# Use checksum-based comparison (slower but accurate)
rsync -ac /src/ /dest/
```

### HFS+ Character Encoding

Mac OS X may decompose UTF-8 characters differently:

```bash
# Specify character set conversion
rsync -a --iconv=UTF-8,UTF8-MAC /src/ /dest/
```
