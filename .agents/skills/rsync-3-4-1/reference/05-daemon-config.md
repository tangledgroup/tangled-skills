# Daemon Configuration Reference

## Starting the Daemon

```bash
# Standalone daemon (requires root for port 873)
sudo rsync --daemon --config=/etc/rsyncd.conf

# Via inetd
# /etc/inetd.conf:
# rsync  stream  tcp  nowait  root  /usr/bin/rsync  rsyncd --daemon

# Via systemd
sudo systemctl enable --now rsyncd
```

## Basic `rsyncd.conf` Structure

```ini
# Global parameters (before any [module])
pid file = /var/run/rsyncd.pid
port = 873
address = 0.0.0.0
log file = /var/log/rsyncd.log
max connections = 4
syslog facility = local5

# Module definitions
[module_name]
    path = /path/to/directory
    comment = Description shown in module list
```

## Global Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `motd file` | none | Message of the day file |
| `pid file` | none | PID file for the daemon |
| `port` | 873 | Port to listen on |
| `address` | all | IP address to bind to |
| `socket options` | default | TCP socket options (e.g., `TCP_NODELAY SO_RCVBUF=65536`) |
| `listen backlog` | 5 | Connection backlog queue size |
| `max verbosity` | 1 | Maximum verbosity for daemon logging |
| `lock file` | `/var/run/rsyncd.lock` | Lock file for max connections |

## Module Parameters

### Access Control

| Parameter | Default | Description |
|-----------|---------|-------------|
| `path` | **required** | Directory to serve |
| `comment` | none | Description shown in module listing |
| `read only` | yes | Whether clients can upload |
| `write only` | no | Whether clients can download |
| `list` | yes | Whether module appears in listing |
| `uid` | nobody (as root) | User for file transfers |
| `gid` | nobody (as root) | Group for file transfers |
| `fake super` | no | Store privileged attrs using xattrs (non-root operation) |

### Authentication

| Parameter | Default | Description |
|-----------|---------|-------------|
| `auth users` | none | Comma-separated list of allowed users |
| `secrets file` | **required** if auth_users set | File with username:password pairs |
| `strict modes` | yes | Check permissions on secrets file |

### Network Security

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hosts allow` | all hosts | Comma-separated host/IP patterns allowed |
| `hosts deny` | none | Comma-separated host/IP patterns denied |
| `reverse lookup` | yes | Perform reverse DNS on connecting clients |
| `forward lookup` | yes | Resolve hostnames in hosts allow/deny |
| `proxy protocol` | no | Require V1/V2 proxy protocol header |

### Logging

| Parameter | Default | Description |
|-----------|---------|-------------|
| `log file` | syslog | Log file path (empty = syslog) |
| `syslog facility` | daemon | Syslog facility name |
| `syslog tag` | rsyncd | Syslog tag |
| `transfer logging` | no | Per-file transfer logging (ftp-like format) |
| `log format` | `%o %h [%a] %m (%u) %f %l` | Custom log format string |
| `timeout` | 0 (none) | I/O timeout in seconds |

### File Filtering

| Parameter | Default | Description |
|-----------|---------|-------------|
| `filter` | none | Daemon-side filter rules |
| `exclude` | none | Space-separated exclude patterns |
| `include` | none | Space-separated include patterns |
| `exclude from` | none | File of daemon exclude patterns |
| `include from` | none | File of daemon include patterns |
| `ignore errors` | no | Ignore I/O errors during delete phase |
| `ignore nonreadable` | no | Skip unreadable files |
| `dont compress` | default list | Wildcard patterns to skip compression |

### Permission Control

| Parameter | Default | Description |
|-----------|---------|-------------|
| `incoming chmod` | none | Affect permissions of incoming files |
| `outgoing chmod` | none | Affect permissions of outgoing files |
| `open noatime` | unset | Avoid changing atime on transferred files |

### Command Execution

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pre-xfer exec` | none | Run before transfer (can abort) |
| `post-xfer exec` | none | Run after transfer |
| `early exec` | none | Run at connection start (before request known) |

### Other

| Parameter | Default | Description |
|-----------|---------|-------------|
| `refuse options` | none | Space-separated refused options |
| `charset` | system default | Character set for filename storage |
| `max connections` | 0 (unlimited) | Maximum simultaneous connections |
| `munge symlinks` | auto | Modify symlinks to prevent escape |
| `name converter` | none | Program for user/group name conversion |
| `daemon chroot` | none | Chroot the daemon before serving modules |
| `use chroot` | unset | Chroot to module path before transfer |
| `numeric ids` | auto (on for chroot) | Disable uid/gid name mapping |

## Secrets File Format

**`/etc/rsyncd.secrets`:**
```
username1:password1
username2:password2
@groupname:group_password
```

- One entry per line
- `#` as first character = comment
- Group passwords only used with `@groupname` auth rules
- File must not be readable by others (when `strict modes = yes`)

## Auth Users Rule Format

Per-user options can be specified after a colon:

```ini
auth users = joe:deny, @guest:deny, admin:rw, @rsync:ro, susan
```

Options: `deny`, `:ro` (read-only override), `:rw` (read/write override)

Matching stops at the first rule that matches the user.

## Log Format Escape Sequences

| Code | Description |
|------|-------------|
| `%a` | Remote IP address |
| `%b` | Bytes actually transferred |
| `%f` | Filename (long form sender; no trailing /) |
| `%h` | Remote host name |
| `%i` | Itemized list of what is being updated |
| `%l` | File length in bytes |
| `%m` | Module name |
| `%n` | Filename (short form; trailing / on dir) |
| `%o` | Operation: send, recv, or del. |
| `%p` | Process ID |
| `%t` | Current date/time |
| `%u` | Authenticated username |

## Complete Example

```ini
# Global settings
pid file = /var/run/rsyncd.pid
port = 873
address = 0.0.0.0
log file = /var/log/rsyncd.log
max connections = 10
syslog facility = local5
timeout = 600

# Module: public mirror (anonymous read)
[public]
    path = /srv/rsync/mirror
    comment = Public file mirror
    read only = yes
    list = yes
    hosts allow = 0.0.0.0/0

# Module: team backups (authenticated write)
[backups]
    path = /srv/rsync/backups
    comment = Team backup storage
    read only = no
    auth users = alice, bob, deploy-bot
    secrets file = /etc/rsyncd.secrets
    hosts allow = 192.168.1.0/24, 10.0.0.0/8
    exclude = .Trash *~ *.tmp
    log file = /var/log/rsyncd-backups.log
    transfer logging = yes

# Module: restricted (read-only for specific hosts)
[restricted]
    path = /srv/rsync/restricted
    read only = yes
    hosts allow = 192.168.1.100
    hosts deny = *
    exclude = **
    include = public_docs/**
```

## SSL/TLS Setup (via Proxy)

Rsync daemon protocol does not encrypt data. Use a proxy for TLS:

**HAProxy:**
```
frontend fe_rsync-ssl
    bind :::874 ssl crt /etc/letsencrypt/example.com/combined.pem
    mode tcp
    use_backend be_rsync

backend be_rsync
    mode tcp
    server local-rsync 127.0.0.1:873 check send-proxy
```

Then set `proxy protocol = true` in rsyncd.conf.

## Config File Includes

```ini
# Merge (inline) — parameters affect surrounding context
&merge /etc/rsyncd.d/*.inc

# Include (separate) — each file starts fresh with global defaults
&include /etc/rsyncd.d/*.conf
```

## Environment Variable Expansion

Use `%VAR%` syntax in parameter values:

```ini
path = /home/%RSYNC_USER_NAME%/files
syslog tag = rsyncd.%RSYNC_USER_NAME%
```

Variables expanded include `RSYNC_MODULE_NAME`, `RSYNC_MODULE_PATH`, `RSYNC_HOST_ADDR`, `RSYNC_HOST_NAME`, `RSYNC_USER_NAME`, `RSYNC_PID`, `RSYNC_REQUEST`.
