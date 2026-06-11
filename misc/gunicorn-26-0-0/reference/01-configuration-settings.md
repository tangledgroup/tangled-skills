# Configuration Settings Reference

## Contents
- Server Socket
- Worker Processes
- Config File
- Control
- Debugging
- Dirty Arbiters
- HTTP/2
- Logging
- Process Naming
- SSL
- Security
- Server Hooks
- Server Mechanics
- ASGI Settings

---

## Server Socket

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `bind` | `-b`, `--bind` | `['127.0.0.1:8000']` | Socket to bind: `HOST`, `HOST:PORT`, `unix:PATH`, `fd://FD`. Multiple allowed. If `$PORT` env is set, defaults to `['0.0.0.0:$PORT']`. |
| `backlog` | `--backlog` | `2048` | Max pending connections. Range 64-2048 typical. |

## Worker Processes

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `workers` | `-w`, `--workers` | `1` | Number of worker processes. Formula: `(2 * CPU_CORES) + 1`. `$WEB_CONCURRENCY` env var takes priority if set (e.g., Heroku). |
| `worker_class` | `-k`, `--worker-class` | `'sync'` | Worker type: `sync`, `gevent`, `tornado`, `gthread`, `asgi`. Or Python path to custom subclass. |
| `threads` | `--threads` | `1` | Threads per worker (gthread only). Setting threads > 1 with sync worker auto-switches to gthread. |
| `worker_connections` | `--worker-connections` | `1000` | Max simultaneous clients (gthread/gevent/asgi only). |
| `max_requests` | `--max-requests` | `0` | Restart worker after N requests (mitigates memory leaks). 0 = disabled. |
| `max_requests_jitter` | `--max-requests-jitter` | `0` | Random jitter added to max_requests to stagger restarts. |
| `timeout` | `-t`, `--timeout` | `30` | Kill workers silent for N seconds. 0 = infinite (not recommended for sync). |
| `graceful_timeout` | `--graceful-timeout` | `30` | Time for workers to finish requests during graceful restart. |
| `keepalive` | `--keep-alive` | `2` | Seconds to wait on Keep-Alive connections. 1-5 range typical. Ignored by sync worker. |

## Config File

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `config` | `-c`, `--config` | `'./gunicorn.conf.py'` | Config file path. Formats: `PATH`, `file:PATH`, `python:MODULE_NAME`. Auto-loaded from working directory. |
| `wsgi_app` | — | `None` | WSGI app path `MODULE:VARIABLE`. Allows omitting positional APP argument. |

## Control

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `control_socket` | `--control-socket` | `$XDG_RUNTIME_DIR/gunicorn.ctl` | Unix socket for `gunicornc` runtime control. Parent dir auto-created. |
| `control_socket_mode` | `--control-socket-mode` | `384` (`0600`) | Socket permissions. `0660` for group access. |
| `control_socket_disable` | `--no-control-socket` | `False` | Disable control socket entirely. |

## Debugging

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `reload` | `--reload` | `False` | Restart workers on code changes (development only). Incompatible with `preload_app`. |
| `reload_engine` | `--reload-engine` | `'auto'` | Reload implementation: `auto`, `poll`, `inotify` (requires inotify package). |
| `reload_extra_files` | `--reload-extra-file` | `[]` | Extra files to watch for reload (templates, configs). |
| `spew` | `--spew` | `False` | Trace every line executed (nuclear debugging option). |
| `check_config` | `--check-config` | `False` | Validate config and exit (0 = valid, 1 = invalid). |
| `print_config` | `--print-config` | `False` | Print fully resolved config. Implies check_config. |

## Dirty Arbiters

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `dirty_apps` | `--dirty-app` | `[]` | List of dirty app paths: `module:Class` or `module:Class:N` (N = worker count limit). |
| `dirty_workers` | `--dirty-workers` | `0` | Number of dirty workers. 0 = disabled. |
| `dirty_timeout` | `--dirty-timeout` | `300` | Task timeout in seconds. 0 = disabled. |
| `dirty_threads` | `--dirty-threads` | `1` | Threads per dirty worker. |
| `dirty_graceful_timeout` | `--dirty-graceful-timeout` | `30` | Graceful shutdown timeout for dirty workers. |

## Dirty Arbiter Hooks

| Setting | Default | Description |
|---------|---------|-------------|
| `on_dirty_starting` | `pass` | Called before dirty arbiter initializes. Receives DirtyArbiter. |
| `dirty_post_fork` | `pass` | Called after dirty worker forked. Receives DirtyArbiter, DirtyWorker. |
| `dirty_worker_init` | `pass` | Called after dirty worker initializes all apps. Receives DirtyWorker. |
| `dirty_worker_exit` | `pass` | Called when dirty worker exits. Receives DirtyArbiter, DirtyWorker. |

## HTTP/2

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `http_protocols` | `--http-protocols` | `'h1'` | Protocols: `h1`, `h2` (requires TLS + h2 library), comma-separated. |
| `http2_max_concurrent_streams` | `--http2-max-concurrent-streams` | `100` | Max concurrent streams per connection. |
| `http2_initial_window_size` | `--http2-initial-window-size` | `65535` | Initial flow control window (bytes). |
| `http2_max_frame_size` | `--http2-max-frame-size` | `16384` | Max frame payload size (16384-16777215). |
| `http2_max_header_list_size` | `--http2-max-header-list-size` | `65536` | Max decompressed header list size (HPACK protection). |

## Logging

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `accesslog` | `--access-logfile` | `None` | Access log file. `'-'` = stdout. |
| `access_log_format` | `--access-logformat` | CLF format | Format string with identifiers: `h`, `l`, `u`, `t`, `r`, `m`, `U`, `q`, `H`, `s`, `B`, `b`, `f`, `a`, `T`, `M`, `D`, `L`, `p`, `{header}i`, `{header}o`, `{variable}e`. |
| `errorlog` | `--error-logfile`, `--log-file` | `'-'` | Error log file. `'-'` = stderr. |
| `loglevel` | `--log-level` | `'info'` | Log granularity: `debug`, `info`, `warning`, `error`, `critical`. |
| `capture_output` | `--capture-output` | `False` | Redirect stdout/stderr to errorlog. |
| `logger_class` | `--logger-class` | `'gunicorn.glogging.Logger'` | Custom logger class Python path. |
| `logconfig` | `--log-config` | `None` | Python logging config file path. |
| `logconfig_dict` | — | `{}` | Python logging dict config (takes precedence over logconfig/logconfig_json). |
| `logconfig_json` | `--log-config-json` | `None` | JSON logging config file path. |
| `syslog` | `--log-syslog` | `False` | Send logs to syslog. |
| `syslog_addr` | `--log-syslog-to` | Platform-specific | Syslog address: `unix://PATH`, `udp://HOST:PORT`, `tcp://HOST:PORT`. |
| `syslog_prefix` | `--log-syslog-prefix` | `None` | Prefix for syslog entries (`gunicorn.<prefix>`). |
| `syslog_facility` | `--log-syslog-facility` | `'user'` | Syslog facility name. |
| `statsd_host` | `--statsd-host` | `None` | StatsD server: `HOST:PORT` or `unix://PATH`. |
| `statsd_prefix` | `--statsd-prefix` | `''` | Prefix for statsd metrics (trailing `.` auto-added). |
| `dogstatsd_tags` | `--dogstatsd-tags` | `''` | Datadog tags: `'tag1:value1,tag2:value2'`. |
| `enable_backlog_metric` | `--enable-backlog-metric` | `False` | Emit `gunicorn.backlog` histogram (Linux only). |
| `disable_redirect_access_to_syslog` | `--disable-redirect-access-to-syslog` | `False` | Disable redirecting access logs to syslog. |
| `enable_stdio_inheritance` | `-R`, `--enable-stdio-inheritance` | `False` | Enable stdio fd inheritance in daemon mode. |

## Process Naming

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `proc_name` | `-n`, `--name` | `None` | Base name for `ps`/`top`. Requires `setproctitle` package. |
| `default_proc_name` | — | `'gunicorn'` | Internal default process name. |

## SSL

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `certfile` | `--certfile` | `None` | SSL certificate file path. |
| `keyfile` | `--keyfile` | `None` | SSL private key file path. |
| `cert_reqs` | `--cert-reqs` | `0` (none) | Client cert verification: `0` = none, `1` = optional, `2` = required. |
| `ca_certs` | `--ca-certs` | `None` | CA certificates file for client verification. |
| `ciphers` | `--ciphers` | `None` | OpenSSL cipher list string. |
| `ssl_context` | — | default factory | Custom SSLContext hook. Receives `(config, default_factory)`, returns SSLContext. |

## Security

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `limit_request_line` | `--limit-request-line` | `4094` | Max HTTP request-line size (0-8190). 0 = unlimited. |
| `limit_request_fields` | `--limit-request-fields` | `100` | Max HTTP header fields (max 32768). |
| `limit_request_field_size` | `--limit-request-field_size` | `8190` | Max header field size. 0 = unlimited. |
| `forwarded_allow_ips` | `--forwarded-allow-ips` | `'127.0.0.1,::1'` | Trusted proxy IPs for `X-Forwarded-*` headers. `*` = disable checking. |
| `secure_scheme_headers` | — | see below | Dict mapping headers to values that indicate HTTPS. Default: `{'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}`. |
| `proxy_protocol` | `--proxy-protocol` | `'off'` | PROXY protocol: `off`, `v1`, `v2`, `auto`. |
| `proxy_allow_ips` | `--proxy-allow-from` | `'127.0.0.1,::1'` | IPs allowed to send PROXY headers. |
| `header_map` | `--header-map` | `'drop'` | Header name mapping: `drop` (silent drop of ambiguous), `refuse` (error on ambiguous), `dangerous` (merge). |
| `forwarder_headers` | `--forwarder-headers` | `'SCRIPT_NAME,PATH_INFO'` | Headers from proxy used for WSGI environ. |

## Server Hooks

All hooks are callable functions defined in the config file. Each receives the specified parameters.

| Hook | Signature | Called When |
|------|-----------|-------------|
| `on_starting` | `(server)` | Before master process initializes |
| `on_reload` | `(server)` | During SIGHUP reload (recycle workers) |
| `when_ready` | `(server)` | After server starts |
| `pre_fork` | `(server, worker)` | Before worker is forked |
| `post_fork` | `(server, worker)` | After worker is forked |
| `post_worker_init` | `(worker)` | After worker initializes app |
| `worker_int` | `(worker)` | After worker exits on SIGINT/SIGQUIT |
| `worker_abort` | `(worker)` | Worker receives SIGABRT (timeout) |
| `pre_exec` | `(server)` | Before new master forked (binary upgrade) |
| `pre_request` | `(worker, req)` | Before request processed |
| `post_request` | `(worker, req, environ, resp)` | After request processed |
| `child_exit` | `(server, worker)` | After worker exited (in master) |
| `worker_exit` | `(server, worker)` | After worker exited (in worker) |
| `nworkers_changed` | `(server, new_value, old_value)` | After worker count changed |
| `on_exit` | `(server)` | Before Gunicorn exits |

## Server Mechanics

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `preload_app` | `--preload` | `False` | Load app before forking workers (saves RAM, faster boot). Incompatible with `reload`. |
| `sendfile` | `--no-sendfile` | `None` | Disable `sendfile()`. Falls back to `$SENDFILE` env. |
| `reuse_port` | `--reuse-port` | `False` | Set `SO_REUSEPORT` on listening socket. |
| `chdir` | `--chdir` | `'.'` | Change directory before loading apps. |
| `daemon` | `-D`, `--daemon` | `False` | Daemonize (detach from terminal). |
| `raw_env` | `-e`, `--env` | `[]` | Environment variables: `KEY=VALUE`. |
| `pidfile` | `-p`, `--pid` | `None` | PID file path. |
| `worker_tmp_dir` | `--worker-tmp-dir` | `None` | Directory for worker heartbeat file. Use tmpfs to avoid blocking. |
| `user` | `-u`, `--user` | current euid | Run workers as this user (uid or name). |
| `group` | `-g`, `--group` | current egid | Run workers as this group (gid or name). |
| `umask` | `-m`, `--umask` | `0` | File mode mask (affects unix sockets). |
| `initgroups` | `--initgroups` | `False` | Include all user groups in worker's group list. |
| `tmp_upload_dir` | — | `None` | Directory for temporary request data uploads. |
| `pythonpath` | `--pythonpath` | `None` | Directories to add to Python path (comma-separated). |
| `paste` | `--paste`, `--paster` | `None` | PasteDeploy config file (optionally `#section`). |
| `protocol` | `--protocol` | `'http'` | Protocol: `http` or `uwsgi`. |
| `uwsgi_allow_ips` | `--uwsgi-allow-from` | `'127.0.0.1,::1'` | IPs allowed to send uWSGI protocol requests. |
| `raw_paste_global_conf` | `--paste-global` | `[]` | PasteDeploy global config `KEY=VALUE`. |
| `root_path` | `--root-path` | `''` | Root path for ASGI apps (mount point behind proxy). |

### HTTP Parsing Options

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `permit_obsolete_folding` | `--permit-obsolete-folding` | `False` | Allow deprecated HTTP line folding (diagnostic only). |
| `strip_header_spaces` | `--strip-header-spaces` | `False` | Strip spaces between header name and `:`. Deprecated. |
| `permit_unconventional_http_method` | `--permit-unconventional-http-method` | `False` | Allow nonstandard HTTP methods (diagnostic only). |
| `permit_unconventional_http_version` | `--permit-unconventional-http-version` | `False` | Allow nonstandard HTTP versions. |
| `casefold_http_method` | `--casefold-http-method` | `False` | Uppercase HTTP methods (legacy behavior). Deprecated. |

## ASGI Settings

| Setting | CLI Flag | Default | Description |
|---------|----------|---------|-------------|
| `asgi_loop` | `--asgi-loop` | `'auto'` | Event loop: `auto` (uvloop if available), `asyncio`, `uvloop`. |
| `asgi_lifespan` | `--asgi-lifespan` | `'auto'` | Lifespan protocol: `auto`, `on`, `off`. |
| `asgi_disconnect_grace_period` | `--asgi-disconnect-grace-period` | `3` | Seconds for ASGI apps to handle client disconnects. |
| `http_parser` | `--http-parser` | `'auto'` | HTTP parser: `auto`, `fast` (gunicorn_h1c C extension), `python`. |
