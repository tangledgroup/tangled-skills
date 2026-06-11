# Operations

## Contents
- Signal Handling
- Binary Upgrades (Zero-Downtime)
- Logging
- StatsD Instrumentation
- Kernel Tuning
- Troubleshooting FAQ

---

## Signal Handling

### Master Process Signals

| Signal | Action |
|--------|--------|
| `QUIT`, `INT` | Quick shutdown |
| `TERM` | Graceful shutdown (waits up to `graceful_timeout`) |
| `HUP` | Reload config, spawn new workers, gracefully stop old ones. Also reloads app code if not preloaded. |
| `TTIN` | Increase worker count by 1 |
| `TTOU` | Decrease worker count by 1 |
| `USR1` | Reopen log files (for log rotation) |
| `USR2` | Binary upgrade — start new master with new binary. Send `TERM` to old master after. |
| `WINCH` | Gracefully stop workers when daemonized |

### Worker Process Signals

| Signal | Action |
|--------|--------|
| `QUIT`, `INT` | Quick shutdown |
| `TERM` | Graceful shutdown |
| `USR1` | Reopen log files |

### Common Operations

```bash
# Reload config and app code
kill -HUP $(cat /var/run/gunicorn.pid)

# Scale workers
kill -TTIN $(cat /var/run/gunicorn.pid)   # +1 worker
kill -TTOU $(cat /var/run/gunicorn.pid)   # -1 worker

# Reopen logs (log rotation)
kill -USR1 $(cat /var/run/gunicorn.pid)

# Graceful shutdown
kill -TERM $(cat /var/run/gunicorn.pid)
```

---

## Binary Upgrades (Zero-Downtime)

Replace the Gunicorn binary without downtime. Preloaded applications reload.

### Steps

1. Replace the old binary
2. Send `USR2` to the old master — starts new master with new workers
3. Send `WINCH` to old master — gracefully stop its workers
4. Verify new workers are healthy
5. Send `TERM` to old master — complete the upgrade

### Rollback

If new workers have issues, rollback while old master keeps listen sockets:

1. Send `HUP` to old master — restart its workers (without reloading config)
2. Send `TERM` to new master — shut down new workers
3. Send `QUIT` to new master — force exit

PID files follow the pattern `<name>.pid.2` for the new master (changed in 19.6.0).

---

## Logging

### Log Levels

`debug`, `info`, `warning`, `error`, `critical` (default: `info`)

### Access Log Format Identifiers

| Identifier | Description |
|------------|-------------|
| `h` | Remote address |
| `l` | `'-'` |
| `u` | User name (HTTP Basic auth) |
| `t` | Date of request |
| `r` | Status line (`GET / HTTP/1.1`) |
| `m` | Request method |
| `U` | URL path without query |
| `q` | Query string |
| `H` | Protocol |
| `s` | Status code |
| `B` | Response length |
| `b` | Response length or `'-'` (CLF) |
| `f` | Referrer (`referer` header) |
| `a` | User agent |
| `T` | Request time (seconds) |
| `M` | Request time (milliseconds) |
| `D` | Request time (microseconds) |
| `L` | Request time (decimal seconds) |
| `p` | Process ID |
| `{header}i` | Request header |
| `{header}o` | Response header |
| `{variable}e` | Environment variable |

### Custom Log Format Example

```python
access_log_format = '%({x-forwarded-for}i)s %(L)s "%(r)s" %(s)s %(b)s'
```

### Log Rotation

```bash
kill -USR1 $(cat /var/run/gunicorn.pid)
```

With logrotate:

```
/var/log/gunicorn/*.log {
    weekly
    missingok
    rotate 52
    compress
    delaycompress
    sharedscripts
    postrotate
        kill -USR1 $(cat /var/run/gunicorn.pid) 2>/dev/null || true
    endscript
}
```

### Important Notes

- Gunicorn's error log should capture **Gunicorn messages only** — route application logs separately
- If overriding `LOGGING` dictionary, set `disable_existing_loggers: False`
- Console logging is enabled by default (changed in 19.2). Use `--log-file=-` to explicitly stream to stdout.

---

## StatsD Instrumentation

Enable statsD metrics via UDP (non-blocking):

```bash
gunicorn --statsd-host=localhost:8125 --statsd-prefix=service.app app:app
```

### Metrics Emitted

| Metric | Type | Description |
|--------|------|-------------|
| `gunicorn.requests` | Counter | Request rate per second |
| `gunicorn.request.duration` | Histogram | Request duration (ms) |
| `gunicorn.workers` | Gauge | Number of workers managed by arbiter |
| `gunicorn.log.critical` | Counter | Rate of critical log messages |
| `gunicorn.log.error` | Counter | Rate of error log messages |
| `gunicorn.log.warning` | Counter | Rate of warning log messages |
| `gunicorn.log.exception` | Counter | Rate of exceptional log messages |
| `gunicorn.backlog` | Histogram | Connections in socket backlog (Linux only, `--enable-backlog-metric`) |

### Datadog Tags

```bash
gunicorn --statsd-host=localhost:8125 \
    --statsd-prefix=service.app \
    --dogstatsd-tags='env:prod,service:web' \
    app:app
```

---

## Kernel Tuning

### File Descriptors

Raise per-process limit (sockets count as files):

```bash
# In systemd service
LimitNOFILE=65536

# Or via ulimit in init script
ulimit -n 65536
```

### Socket Backlog

```bash
sudo sysctl -w net.core.somaxconn="2048"
```

### Worker Heartbeat on tmpfs

On disk-backed `/tmp`, `os.fchmod` can block. Use tmpfs:

```bash
sudo mkdir /mem
echo 'tmpfs /mem tmpfs defaults,size=64m,mode=1777,noatime 0 0' | sudo tee -a /etc/fstab
sudo mount /mem
```

```bash
gunicorn app:app --worker-tmp-dir /mem
```

---

## Troubleshooting FAQ

### Why are workers silently killed?

Check for `SIGKILL` from OOM killer:

```bash
dmesg | grep gunicorn
```

If you see `Memory cgroup out of memory ... Killed process (gunicorn)`, raise memory limits or adjust OOM behavior. Reverse proxies may show `502` while Gunicorn only logs new worker startups.

### Why don't I see logs in the console?

Use `--log-file=-` to stream logs to stdout. Console logging is default since 19.2.

### How do I test proxy buffering?

Use [Hey](https://github.com/rakyll/hey):

```bash
hey -n 10000 -c 100 http://127.0.0.1:5000/
```

### How do I set SCRIPT_NAME?

Set via environment variable or HTTP header. For subfolder mounting, `SCRIPT_NAME` starts with `/` and has no trailing slash. Header is only accepted from trusted forwarders in `forwarded_allow_ips`.

### How do I name processes?

Install `setproctitle` and use `--name`:

```bash
pip install setproctitle
gunicorn -n myapp app:app
```

### Why is there no HTTP keep-alive with sync workers?

Sync workers target Nginx, which uses HTTP/1.0 for upstream connections. For direct internet traffic without a buffering proxy, use an async worker (gthread, gevent, or asgi).

### Does Gunicorn suffer from thundering herd?

Potentially with many sleeping handlers waking simultaneously. Monitor load if using large numbers of workers or threads.

### Django reports ImproperlyConfigured

Async workers may break `django.core.urlresolvers.reverse`. Use `reverse_lazy` instead.

### How do I avoid blocking in os.fchmod?

Point `--worker-tmp-dir` to a tmpfs mount (see Kernel Tuning section above). Check with `df /tmp`.

### How do I disable sendfile()?

```bash
gunicorn --no-sendfile app:app
# Or: SENDFILE=0 gunicorn app:app
```
