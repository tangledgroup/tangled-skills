# Rsync Daemon Configuration

## Overview

The rsync daemon allows anonymous or authenticated file transfers without requiring SSH. It listens on TCP port 873 by default and is configured via `rsyncd.conf`.

## Launching the Daemon

**Stand-alone daemon:**

```bash
rsync --daemon
```

Requires root privileges for chroot, binding to ports under 1024, or setting file ownership. Otherwise needs only read/write permission on data, log, and lock files.

The config file (`rsyncd.conf`) is re-read on each client connection — no need to send HUP signals.

**Via inetd:**

Add to `/etc/services`:
```
rsync   873/tcp
```

Add to `/etc/inetd.conf`:
```
rsync   stream  tcp     nowait  root  /usr/bin/rsync  rsyncd --daemon
```

Then send inetd a HUP signal.

**Via remote shell (single-use daemon):**

Run a daemon over SSH without opening new ports:

```bash
rsync -av --rsh=ssh host::module /dest
```

The daemon reads its config from the remote user's home directory. Useful for encrypted daemon-style transfers.

## Daemon Command-Line Options

- `--daemon` — run as rsync daemon
- `--config=FILE` — alternate rsyncd.conf file
- `--address=ADDRESS` — bind to specific address
- `--port=PORT` — listen on alternate port
- `--log-file=FILE` — override log file setting
- `--log-file-format=FMT` — override log format
- `--sockopts=OPTIONS` — custom TCP options
- `--no-detach` — don't detach (useful for debugging)
- `--dparam=OVERRIDE`, `-M` — override global daemon config parameter
  - Example: `rsync --daemon --dparam=motdfile=/path/motd`
- `--bwlimit=RATE` — limit socket I/O bandwidth
- `--ipv4`, `-4` / `--ipv6`, `-6` — prefer IPv4 or IPv6

## Config File Format

The `rsyncd.conf` file is line-based. Lines starting with `#` are comments. Continuation lines end with `\`. Parameters use `name = value` format (only first `=` is significant). Boolean values accept yes/no, 0/1, true/false.

Environment variables are expanded in parameter values using `%VAR%` syntax. Rsync sets connection-time variables like `RSYNC_USER_NAME`. Use `%%` for a literal `%`.

**Config directives:**

- `&include /path/dir` — reads `*.conf` files from directory (isolated defaults)
- `&merge /path/dir` — reads `*.inc` files (merged in place, affects subsequent parsing)

Example `/etc/rsyncd.conf`:
```
port = 873
log file = /var/log/rsync.log
pid file = /var/lock/rsync.lock

&merge /etc/rsyncd.d
&include /etc/rsyncd.d
```

## Global Parameters

- `motd file` — message of the day file displayed on connect
- `pid file` — file to write daemon PID to
- `port` — TCP port to listen on (default: 873)
- `address` — IP address to bind to
- `socket options` — custom setsockopt() values
- `listen backlog` — connection backlog value (default: 5)

Any module parameter can also be set globally to provide defaults.

## Module Parameters

Modules are defined with `[module_name]` headers. The special `[global]` section switches back to global context for shared defaults. Module names cannot contain `/` or `]`.

### Path and Chroot

- `path` — filesystem directory for this module (**required**)
  - `/./` element divides chroot dir from inner-chroot subdir: `path = /var/rsync/./module1`
  - Environment variables expanded: `path = /home/%RSYNC_USER_NAME%`
- `use chroot` — chroot to path before transfer
  - Default: tries chroot, continues with warning if it fails
  - If path has `/./`, unset value is treated as true
  - Prior to 3.2.7, default was always "true"
- `daemon chroot` — path for daemon-wide chroot (before module chroot)
- `numeric ids` — disable uid/gid name mapping (default: enabled in chroot modules)
- `name converter` — external program for user/group name conversions

### Access Control

- `read only` — prevent uploads (default: true)
- `write only` — prevent downloads (default: false)
  - Recommend adding `refuse options = delete` for write-only modules
- `max connections` — maximum simultaneous connections (0 = unlimited, negative = disabled)
- `lock file` — file for connection locking (default: `/var/run/rsyncd.lock`)
- `list` — show module in listing (default: true)
  - When false, daemon pretends module doesn't exist for denied clients
- `hosts allow` — comma/space-separated patterns of allowed hosts
  - Forms: exact IP, `ip/mask`, hostname wildcards, netgroups (`@name`)
- `hosts deny` — patterns of denied hosts
  - When both allow and deny are set, allow is checked first
- `reverse lookup` — perform reverse DNS on client IP (default: true)
- `forward lookup` — forward DNS on hostname in allow/deny (default: true)
- `proxy protocol` — require PROXY protocol header on connections (for use behind load balancers)

### Authentication

- `auth users` — comma/space-separated list of authorized usernames
  - Shell wildcards supported
  - Group matching with `@` prefix: `@rsync`
  - Per-rule options after colon: `user:deny`, `admin:rw`, `@group:ro`
  - Rules checked in order; first match wins
  - Example: `auth users = joe:deny @guest:deny admin:rw @rsync:ro susan sam`
- `secrets file` — file with `username:password` pairs (one per line)
  - Lines starting with `#` are comments
  - Group passwords: `@groupname:password`
- `strict modes` — check secrets file permissions (default: true)

### User/Group Execution

- `uid` — user for file transfers (default: "nobody" when root)
  - Use `%RSYNC_USER_NAME%` to run as authenticating user
- `gid` — group(s) for file transfers (default: "nobody"/"nogroup" when root)
  - `*` as first gid = all normal groups for the transfer user
  - Comma-separated list; start with comma if names contain spaces
- `daemon uid` — uid for the daemon process itself
- `daemon gid` — gid for the daemon process itself
- `fake super` — simulate super-user via xattrs (allows full backup without root)

### Permissions and Attributes

- `incoming chmod` — chmod applied to incoming files (after all other calculations)
- `outgoing chmod` — chmod applied to outgoing files (before sending)
- `open noatime` — open files with O_NOATIME flag (default: unset, user controls)

### Filtering

- `filter` — space-separated daemon filter rules (daemon-side only, not sent to client)
  - Prevents access to hidden files; excluded files appear non-existent
  - Use `***` pattern to exclude entire subtrees: `/secret/***`
- `exclude` — space-separated exclude patterns
- `include` — include patterns to override excludes
- `exclude from` — file of exclude patterns
- `include from` — file of include patterns
- `munge symlinks` — modify symlinks for safety (default: enabled when not chrooted to `/`)
  - Prefixes symlinks with `/rsyncd-munged/`
  - Add `/rsyncd-munged/` to exclude setting in chroot areas

### Transfer Behavior

- `ignore errors` — proceed with deletion despite I/O errors
- `ignore nonreadable` — completely ignore unreadable files
- `timeout` — override client's I/O timeout in seconds (default: 0 = no timeout)
  - Recommended: 600 (10 minutes) for anonymous daemons
- `refuse options` — space-separated list of refused client options
  - Wildcards supported; `!` for negation
  - `copy-devices` and `write-devices` refused by default
  - Example: `refuse options = c delete-* !delete-during`
  - Accept-only mode: `refuse options = * !a !v !compress*`
- `dont compress` — wildcard patterns for files not to compress
  - Set to `*` to disable compression entirely

### Logging

- `log file` — log to file instead of syslog
  - Opened before chroot, can be placed outside transfer area
  - Falls back to syslog if file cannot be opened
- `syslog facility` — syslog facility name (default: daemon)
- `syslog tag` — syslog tag (default: "rsyncd")
  - Supports `%RSYNC_USER_NAME%`: `syslog tag = rsyncd.%RSYNC_USER_NAME%`
- `transfer logging` — enable per-file transfer logging
- `log format` — format string for transfer log entries
  - Default: `%o %h [%a] %m (%u) %f %l`
  - Prefixed with `%t [%p] ` when using `log file`

**Log format escapes:**

- `%a` — remote IP address, `%h` — remote hostname
- `%b` — bytes transferred, `%l` — file length
- `%f` — filename (long), `%n` — filename (short)
- `%i` — itemized change list, `%L` — link target
- `%m` — module name, `%M` — last-modified time
- `%o` — operation (send/recv/del.), `%p` — process ID
- `%u` — authenticated username, `%U` — uid
- `%G` — gid, `%B` — permission bits
- `%t` — current date/time, `%P` — module path
- `%c` — block checksums received, `%C` — full-file checksum

Human-readable numbers: add apostrophes before numeric escapes (e.g., `%''l %'b`).

### Charset

- `charset` — character set for module filenames (required for `--iconv` support)

### Hook Scripts

- `early exec` — command run early in connection (before transfer request known)
  - Can receive up to 5K via client's `--early-input=FILE`
  - Use with `lock file` and `max connections` to avoid concurrency issues
- `pre-xfer exec` — command run right before transfer
  - Non-zero exit aborts transfer; stdout shown to user on abort
- `post-xfer exec` — command run after transfer (even if other scripts failed)

**Environment variables for hooks:**

- `RSYNC_MODULE_NAME` — module name
- `RSYNC_MODULE_PATH` — configured path
- `RSYNC_HOST_ADDR` — client IP address
- `RSYNC_HOST_NAME` — client hostname
- `RSYNC_USER_NAME` — authenticating username
- `RSYNC_PID` — unique transfer number
- `RSYNC_REQUEST` (pre-xfer) — module/path info from user
- `RSYNC_ARG#` (pre-xfer) — numbered request arguments
- `RSYNC_EXIT_STATUS` (post-xfer) — server exit value
- `RSYNC_RAW_STATUS` (post-xfer) — raw waitpid() exit value

Hooks run as the daemon's user without chroot restrictions. Set `RSYNC_SHELL` to control which shell runs hooks, or `RSYNC_NO_XFER_EXEC` to disable all hooks.

## SSL/TLS Daemon Setup

The rsync daemon protocol does not encrypt data. Use SSH transport for encryption, or place the daemon behind an SSL/TLS proxy:

**HAProxy configuration:**

```
frontend fe_rsync-ssl
   bind :::874 ssl crt /etc/letsencrypt/example.com/combined.pem
   mode tcp
   use_backend be_rsync

backend be_rsync
   mode tcp
   server local-rsync 127.0.0.1:873 check send-proxy
```

**Nginx stream configuration:**

```nginx
stream {
    server {
        listen 874 ssl;
        listen [::]:874 ssl;

        ssl_certificate /etc/letsencrypt/example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/example.com/privkey.pem;

        proxy_pass localhost:873;
        proxy_protocol on;
        proxy_timeout 1m;
        proxy_connect_timeout 5s;
    }
}
```

When using a proxy, enable `proxy protocol = true` in rsyncd.conf and restrict backend access to the proxy only.

## Daemon Config Examples

**Anonymous read-only module:**

```
[ftp]
    path = /home/ftp
    comment = ftp export area
```

**Multi-module with authentication:**

```
uid = nobody
gid = nobody
use chroot = yes
max connections = 4
syslog facility = local5
pid file = /var/run/rsyncd.pid

[ftp]
    path = /var/ftp/./pub
    comment = whole ftp area (approx 6.1 GB)

[sambaftp]
    path = /var/ftp/./pub/samba
    comment = Samba ftp area (approx 300 MB)

[cvs]
    path = /data/cvs
    comment = CVS repository (requires authentication)
    auth users = tridge, susan
    secrets file = /etc/rsyncd.secrets
```

**Secrets file** (`/etc/rsyncd.secrets`):

```
tridge:mypass
susan:herpass
```

## Authentication Strength

The rsync daemon uses a 128-bit MD4-based challenge-response authentication system, which is fairly weak. For strong security, use rsync over SSH instead of the daemon protocol. The daemon protocol provides authentication but no data encryption.
