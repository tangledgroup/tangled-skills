# Configuration Syntax & Core Directives

## Measurement Units

Nginx configuration supports various time and size units:

**Time:** `ms` (milliseconds), `s` (seconds), `m` (minutes), `h` (hours), `d` (days)
- Examples: `500ms`, `30s`, `5m`, `1h`, `1d`

**Size:** `k` (kilobytes), `m` (megabytes), `g` (gigabytes)
- Examples: `4k`, `64k`, `256m`, `1g`

## Main Context Directives

### `accept_mutex [ on | off ]`
If enabled, worker processes accept new connections by turn. Otherwise, all workers are notified and may compete. No need to enable on systems with `EPOLLEXCLUSIVE` flag (Linux 4.5+) or when using `reuseport`.

**Default:** `off`  
**Context:** `events`

### `accept_mutex_delay [ time ]`
Maximum time a worker waits to accept connections if another worker is currently accepting.

**Default:** `500ms`  
**Context:** `events`

### `daemon [ on | off ]`
Whether nginx should become a daemon process. Mainly used during development.

**Default:** `on`  
**Context:** `main`

### `debug_connection [ address | CIDR | unix: ]`
Enables debugging log for selected client connections. Other connections use the level set by `error_log`.

```nginx
events {
    debug_connection 127.0.0.1;
    debug_connection ::1;
    debug_connection 192.0.2.0/24;
}
```
Requires `--with-debug` compilation flag.  
**Context:** `events`

### `debug_points [ abort | stop ]`
For debugging internal errors. `abort` creates a core file, `stop` halts the process for debugger attachment.

**Context:** `main`

### `env [ variable [= value] ]`
By default, nginx removes all inherited environment variables except `TZ`. This directive preserves or sets specific variables.

```nginx
env MALLOC_OPTIONS;
env PERL5LIB=/data/site/modules;
```
**Default:** `env TZ;`  
**Context:** `main`

### `error_log [ file [ level ] ]`
Configures logging. Multiple log files can be specified at the same level.

**Log levels** (in order of increasing severity): `debug`, `info`, `notice`, `warn`, `error`, `crit`, `alert`, `emerg`

```nginx
error_log /var/log/nginx-error.log info;
error_log syslog:server=127.0.0.1,facility=local7;  # syslog
error_log memory:32m error;  # cyclic memory buffer (debugging)
```
**Default:** `logs/error.log error`  
**Context:** `main`, `http`, `mail`, `stream`, `server`, `location`

### `events { ... }`
Provides the configuration context for connection processing directives.

**Context:** `main`

### `include [ file | mask ]`
Includes another file or files matching a glob pattern.

```nginx
include mime.types;
include vhosts/*.conf;
```
**Context:** any

### `load_module [ file ]`
Loads a dynamic module (introduced in 1.9.11).

```nginx
load_module modules/ngx_mail_module.so;
```
**Context:** `main`

### `lock_file [ file ]`
Prefix for lock file names used by `accept_mutex` and shared memory serialization. Ignored on systems using atomic operations.

**Default:** `logs/nginx.lock`  
**Context:** `main`

### `master_process [ on | off ]`
Whether worker processes are started. Intended for nginx developers.

**Default:** `on`  
**Context:** `main`

### `multi_accept [ on | off ]`
If disabled, a worker accepts one connection at a time. If enabled, all new connections are accepted at once. Ignored with kqueue (which reports count of pending connections).

**Default:** `off`  
**Context:** `events`

### `pcre_jit [ on | off ]`
Enables PCRE JIT compilation for known regular expressions during configuration parsing. Requires PCRE 8.20+ built with `--enable-jit`.

**Default:** `off`  
**Context:** `main`

### `pid [ file ]`
File storing the master process ID.

**Default:** `logs/nginx.pid`  
**Context:** `main`

### `ssl_engine [ device ]`
Name of hardware SSL accelerator device.

**Context:** `main`

### `stall_threshold [ time ]`
Time threshold for event loop iteration before a stall is reported. Default: 1000ms. Ignored if `timer_resolution` is enabled.

**Default:** `1000ms`  
**Context:** `events`  
*Available as part of commercial subscription.*

### `thread_pool [ name ] threads=number [ max_queue=number ]`
Defines a thread pool for multi-threaded file I/O without blocking workers.

```nginx
thread_pool mypool threads=16 max_queue=32768;
```
**Default:** `default threads=32 max_queue=65536`  
**Context:** `main`

### `timer_resolution [ interval ]`
Reduces timer resolution, decreasing `gettimeofday()` system calls. Called once per specified interval instead of on every kernel event.

```nginx
timer_resolution 100ms;
```
Implementation depends on method: `EVFILT_TIMER` (kqueue), `timer_create()` (eventport), `setitimer()` (others).  
**Context:** `main`

### `use [ method ]`
Specifies the connection processing method. Usually auto-detected as most efficient.

Supported methods: `select`, `poll`, `kqueue`, `epoll`, `/dev/poll`, `eventport`

**Context:** `events`

### `user [ user [ group ]]`
User/group credentials for worker processes.

**Default:** `nobody nobody`  
**Context:** `main`

### `worker_aio_requests [ number ]`
Max outstanding async I/O operations per worker when using `aio` with `epoll`.

**Default:** `32`  
**Context:** `events`

### `worker_connections [ number ]`
Max simultaneous connections opened by a single worker process. Includes all connections (clients + proxied servers). Must not exceed the OS limit on open files (`worker_rlimit_nofile`).

**Default:** `512`  
**Context:** `events`

### `worker_cpu_affinity [ cpumask ... ]`
Binds worker processes to specific CPUs using bitmasks.

```nginx
worker_processes    4;
worker_cpu_affinity 0001 0010 0100 1000;  # one CPU per worker

worker_processes    2;
worker_cpu_affinity 0101 1010;  # hyper-threading friendly
```

Auto-binding:
```nginx
worker_processes auto;
worker_cpu_affinity auto;
```
Limited to specific CPUs: `worker_cpu_affinity auto 01010101;`  
**Context:** `main` (FreeBSD, Linux only)

### `worker_priority [ number ]`
Scheduling priority for worker processes (like `nice`). Negative = higher priority. Range typically -20 to 20.

**Default:** `0`  
**Context:** `main`

### `worker_processes [ number | auto ]`
Number of worker processes. Optimal value depends on CPU cores, disk configuration, and load pattern. Use `auto` to autodetect.

**Default:** `1`  
**Context:** `main`

### `worker_rlimit_core [ size ]`
Changes `RLIMIT_CORE` (core file size limit) for worker processes.

**Context:** `main`

### `worker_rlimit_nofile [ number ]`
Changes the maximum open files (`RLIMIT_NOFILE`) limit for worker processes. Useful to increase without restarting the master process.

**Context:** `main`

### `worker_shutdown_timeout [ time ]`
Timeout for graceful shutdown of worker processes. After timeout, nginx closes all connections open.

**Default:** unlimited  
**Context:** `main`

### `working_directory [ directory ]`
Working directory for worker processes. Primarily used for core file output location. Worker must have write permission.

**Context:** `main`

## Connection Processing Methods

| Method | Platform | Notes |
|--------|----------|-------|
| `select` | All | Standard, built-in fallback. Limited by `FD_SETSIZE`. |
| `poll` | All | Standard, built-in fallback. |
| `kqueue` | FreeBSD 4.1+, OpenBSD 2.9+, NetBSD 2.0, macOS | Efficient |
| `epoll` | Linux 2.6+ | Efficient. Supports `EPOLLRDHUP` (Linux 2.6.17) and `EPOLLEXCLUSIVE` (Linux 4.5). |
| `/dev/poll` | Solaris 7 11/99+, HP/UX 11.22+, IRIX 6.5.15+ | Efficient |
| `eventport` | Solaris 10+ | Known issues; prefer `/dev/poll` instead |

## Example Minimal Configuration

```nginx
user www www;
worker_processes auto;
error_log /var/log/nginx-error.log info;

events {
    use epoll;
    worker_connections 2048;
    multi_accept on;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;

    keepalive_timeout 65;

    server {
        listen 80;
        server_name example.com;

        location / {
            root /var/www/html;
            index index.html;
        }
    }
}
```
