# Process Control

## Starting, Stopping, and Reloading

Control nginx via the `-s` parameter:

```bash
nginx              # start
nginx -s stop      # fast shutdown
nginx -s quit      # graceful shutdown (waits for workers to finish)
nginx -s reload    # reload configuration
nginx -s reopen    # reopen log files
```

Execute commands as the same user that started nginx.

## Configuration Reload Process

On `reload` (or HUP signal), the master process:
1. Checks syntax validity of the new configuration
2. Tries to apply it (opens log files, listen sockets)
3. If successful — starts new workers, signals old workers to shut down gracefully
4. If failed — rolls back and continues with old configuration

Old workers stop accepting new connections but finish serving existing requests before exiting.

## Signal Reference

### Master Process Signals

- `TERM`, `INT` — fast shutdown
- `QUIT` — graceful shutdown
- `HUP` — reload configuration, start new workers, gracefully shut down old workers
- `USR1` — reopen log files
- `USR2` — upgrade executable on the fly
- `WINCH` — graceful shutdown of worker processes

### Worker Process Signals

- `TERM`, `INT` — fast shutdown
- `QUIT` — graceful shutdown
- `USR1` — reopen log files
- `WINCH` — abnormal termination for debugging (requires `debug_points`)

## Using kill Directly

The master process PID is written to the `nginx.pid` file (default: `/usr/local/nginx/logs/nginx.pid` or `/var/run/nginx.pid`):

```bash
# Graceful shutdown
kill -s QUIT $(cat /var/run/nginx.pid)

# Reload configuration
kill -s HUP $(cat /var/run/nginx.pid)

# Reopen logs
kill -s USR1 $(cat /var/run/nginx.pid)
```

List running processes:

```bash
ps -ax | grep nginx
```

## Rotating Log Files

1. Rename the current log file
2. Send `USR1` signal to the master process
3. Master reopens log files, workers follow
4. Old files are immediately available for compression/archiving

```bash
mv /var/log/nginx/access.log /var/log/nginx/access.log.old
nginx -s reopen
gzip /var/log/nginx/access.log.old
```

## Upgrading Executable on the Fly

Zero-downtime binary upgrade using `USR2`:

1. Replace the nginx binary with the new version
2. Send `USR2` to the old master process
3. Old master starts a new master with the new binary
4. Both old and new workers handle requests simultaneously
5. Send `WINCH` to old master — old workers begin graceful shutdown
6. When all old workers exit, send `QUIT` to old master
7. Only new processes remain

Rollback if the new version has issues:
- Send `HUP` to old master — it starts its own new workers
- Send `QUIT` or `TERM` to the new master — its workers exit
- Old master resumes full operation

## Configuration Testing

Always test configuration before reloading:

```bash
nginx -t    # test configuration syntax
nginx -T    # dump full resolved configuration
```

The `-t` flag checks syntax and reports errors without applying changes. The `-T` flag shows the complete effective configuration including all `include` directives — useful for debugging complex setups.

## pid Directive

Control where the PID file is written:

```nginx
pid /var/run/nginx.pid;
```

Can also be set at build time via `--with-pid-path`.
