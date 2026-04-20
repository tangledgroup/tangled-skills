# Daemon Configuration (rsyncd.conf)

## Starting the Daemon

```bash
# Standalone daemon
rsync --daemon

# With custom config and port
rsync --daemon --config=/etc/rsyncd.conf --port=8730

# Via inetd
# /etc/services:
# rsync    873/tcp
# /etc/inetd.conf:
# rsync   stream  tcp     nowait  root   /usr/bin/rsync rsyncd --daemon
```

The daemon **must run as root** if you want to use `chroot`, bind to port < 1024, or set file ownership. Otherwise it just needs read/write access to the data directories.

The config file is re-read on each client connection — no need to send HUP signals.

## rsyncd.conf File Format

```ini
# Global parameters (before any [module])
pid file = /var/run/rsyncd.pid
port = 873
socket options = TCP_NODELAY

# Module definitions
[modulename]
    path = /path/to/data
    comment = Description shown to clients

[global]
    # Switches back to global context for shared defaults
```

- Lines starting with `#` are comments
- Each module starts with `[name]` on its own line
- Parameters use `name = value` syntax
- Leading/trailing whitespace in values is discarded
- Internal whitespace in values is preserved
- Line continuation with trailing `\`
- Boolean values: `yes/no`, `0/1`, `true/false` (case-insensitive)
- Environment variables expanded as `%VAR%`

## Module Parameters

### Path & Access

| Parameter | Default | Description |
|-----------|---------|-------------|
| `path` | *(required)* | Directory path to serve. Use `/./` syntax for chroot: `path = /var/rsync/./module1` |
| `comment` | — | Description shown in module listing |
| `read only` | `yes` | Whether clients can upload files |
| `write only` | `no` | Whether clients can download files |
| `list` | `yes` | Whether module appears in directory listing |
| `uid` | `nobody` (if root) / no change | User to run transfers as |
| `gid` | `nogroup` (if root) / no change | Group to run transfers as |
| `use chroot` | `unset` | Whether to chroot before transfer. Requires root if true |
| `daemon chroot` | — | Path for daemon-level chroot (all modules share this) |
| `max connections` | `0` (no limit) | Max simultaneous connections. Negative value disables module |
| `lock file` | `/var/run/rsyncd.lock` | File for connection locking |
| `max verbosity` | `1` | Maximum verbosity clients can request |

### Authentication & Access Control

| Parameter | Description |
|-----------|-------------|
| `auth users` | Space-separated list of authorized usernames (separate from system users) |
| `secrets file` | File containing `username:password` pairs (mode 0600 recommended) |
| `hosts allow` | Space-separated list of allowed hosts/IPs/CIDR ranges |
| `hosts deny` | Space-separated list of denied hosts/IPs/CIDR ranges |
| `deny users` | List of usernames explicitly denied access |
| `refuse options` | Comma-separated list of client options to refuse (e.g., `delete, compress`) |

### Logging

| Parameter | Description |
|-----------|-------------|
| `log file` | Path to log file (instead of syslog) |
| `syslog facility` | Syslog facility name (default: `daemon`) |
| `syslog tag` | Syslog tag (default: `rsyncd`) |
| `log format` | Custom log format string |

### Transfer Behavior

| Parameter | Description |
|-----------|-------------|
| `timeout` | Network timeout in seconds |
| `transfer logging` | Enable transfer-specific logging |
| `ignore errors` | Ignore I/O errors during deletion |
| `ignore non-read errors` | Ignore non-read errors during deletion |
| `numeric ids` | Disable user/group name lookup (default: true for chroot) |
| `include` / `exclude` | Default include/exclude patterns for this module |
| `charset` | Character set for filenames (enables --iconv support in chroot) |
| `name converter` | Program for user/group name-to-ID conversion in chroot |
| `munge symlinks` | Prefix symlinks with `/rsyncd-munged/` to prevent escapes |
| `proxy protocol` | Require V1/V2 proxy protocol header (for proper source IP logging) |
| `open noatime` | Avoid changing atime on transferred files (`true`/`false`/`unset`) |

## Authentication Setup

### Using `auth users` + `secrets file`:

```ini
[backup]
    path = /data/backup
    read only = no
    auth users = alice bob
    secrets file = /etc/rsyncd.secrets
```

Create `/etc/rsyncd.secrets` (mode 0600):
```
alice:secret123
bob:password456
```

Client connects with password:
```bash
# Method 1: Interactive prompt
rsync -avz alice@host::backup /local/dest/

# Method 2: Password file
rsync -avz --password-file=/etc/rsync.pass alice@host::backup /local/dest/

# Method 3: Environment variable
export RSYNC_PASSWORD=secret123
rsync -avz alice@host::backup /local/dest/
```

### Using System Users (PAM):

When `auth users` is not set, rsync falls back to system authentication. The client's SSH identity becomes the transfer user.

## Common Daemon Configurations

### Read-Only Mirror (Anonymous)

```ini
[projects]
    path = /srv/mirror/projects
    comment = Public project mirrors
    read only = yes
    list = yes
    exclude = *.tmp *.swp
```

### Writable Backup Server

```ini
[backups]
    path = /data/backups
    comment = Internal backup server
    read only = no
    auth users = backup-admin
    secrets file = /etc/rsyncd.secrets
    hosts allow = 192.168.1.0/24
    max connections = 5
    log file = /var/log/rsyncd-backups.log
```

### Per-User Home Directories

```ini
[home]
    path = /home/%RSYNC_USER_NAME%
    read only = no
    auth users = %RSYNC_USER_NAME%
    secrets file = /etc/rsyncd.secrets
```

## Security Best Practices

1. **Use `auth users`** — Never rely on system authentication alone for writable modules
2. **Set restrictive `hosts allow`** — Limit access to trusted networks
3. **Use `refuse options = delete`** on read-only mirrors
4. **Set `secrets file` mode to 0600** — Prevent other users from reading passwords
5. **Use `munge symlinks`** on writable modules
6. **Consider `max connections`** — Prevent resource exhaustion
7. **Run as non-root when possible** — Only need root for chroot or privileged ports
8. **Use `fake super`** if you can't run as root but need to preserve ownership

## Rate Limiting (Daemon Side)

```bash
# Set rate limit at daemon startup
rsync --daemon --bwlimit=500

# Or in config (affects data the daemon sends; client can still use smaller value)
# Use --dparam from command line
rsync --daemon -M bwlimit=500
```

## Health Check & Management

```bash
# List running rsync processes
ps aux | grep rsync

# Check if daemon is listening
nc -zv localhost 873

# List available modules
rsync somehost::

# Get module details
rsync somehost::modulename/
```
