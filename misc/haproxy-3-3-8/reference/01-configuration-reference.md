# Configuration Reference

## Global Section

Process-wide settings. Only one global section per configuration.

### Process Management and Security

**daemon**
  Start as a daemon, detaching from the terminal. Equivalent to `-D` on the command line. Recommended in init scripts.

**master-worker**
  Deprecated keyword (use `-W` or `-Ws` on command line). Launches a master process that monitors worker processes. Reload via SIGUSR2 to the master.

**maxconn <number>**
  Maximum total simultaneous connections per process. Affects file descriptor allocation. Rough FD estimate: maxconn * 2 + overhead.

**nbthread <number>**
  Number of threads to run. Defaults to number of CPUs the process is bound to. Each thread runs its own event loop. Connections are sticky to a single thread.

**chroot <directory>**
  Change root after startup. HAProxy cannot access the filesystem after chroot, so configuration changes require a reload (new process).

**uid <number> / user <name>**
  Drop privileges to specified UID or user name after binding sockets.

**gid <number> / group <name>**
  Change group to specified GID or group name.

**pidfile <file>**
  Write PID(s) to file. Equivalent to `-p`.

**log <target> [len <length>] [format <format>] <facility> [max level [min level]]**
  Add a global syslog server. Multiple servers can be defined. Proxies with `log global` inherit these loggers.

**ssl-default-bind-options [<option>]...**
  Default SSL options for all bind lines. Common options:
  - `ssl-min-ver <version>` / `ssl-max-ver <version>` — minimum/maximum TLS version
  - `no-tls-tickets` — disable TLS session tickets
  - `no-sslv3`, `no-tlsv10`, `no-tlsv11`, `no-tlsv12`, `no-tlsv13`
  - `force-sslv3`, `force-tlsv10`, etc. — force specific versions
  - `prefer-server-ciphers` — server cipher preference
  - `no-client-opt-curves` / `client-opt-curves`

**ssl-default-bind-ciphers <ciphers>**
  Default cipher suite string for TLS up to v1.2. Format per OpenSSL `man 1 ciphers`.

**ssl-default-bind-ciphersuites <ciphersuites>**
  Default cipher suites for TLS v1.3.

**ssl-default-server-options / ssl-default-server-ciphers / ssl-default-server-ciphersuites**
  Same as bind equivalents but for server-side (outgoing) SSL connections.

**ssl-dh-param-file <file>**
  Custom DH parameters file for DHE key exchange. Generate with `openssl dhparam <size>` (minimum 2048).

**ssl-server-verify <mode>**
  Default verification mode for backend server certificates:
  - `required` — verify and fail if invalid
  - `optional` — attempt verification but accept regardless
  - `none` — no verification (default)

**cluster-secret <secret>**
  Shared secret for QUIC retry tokens. Required when using QUIC with retry protection.

**setcap <capabilities>**
  Preserve Linux capabilities after privilege drop. Common: `cap_net_bind_service` (bind privileged ports), `cap_net_raw` (transparent proxy).

### Performance Tuning

**maxconnrate <number>**
  Maximum connection rate per second across all frontends.

**maxsessrate <number>**
  Maximum new sessions per second.

**maxsslrate / maxsslconn**
  Maximum SSL session rate and concurrent SSL connections.

**tune.bufsize <size>**
  I/O buffer size per connection side (default ~16KB). Affects memory usage: bufsize * 2 per connection.

**tune.maxrewrite <size>**
  Reserved buffer space for header rewriting (default ~1024).

**tune.maxaccept <number>**
  Maximum consecutive connections accepted before switching to other work (default 4).

**tune.idle-pool.shared { on | off }**
  Share idle connection pools between threads for the same server (default on).

**prealloc-fd**
  Pre-allocate kernel file descriptor data structures to prevent short pauses under load.

### SSL Tuning

**tune.ssl.cachesize <number>**
  Size of the SSL session cache in entries. Larger caches improve TLS session resumption rate.

**tune.ssl.lifetime <timeout>**
  Lifetime of SSL session cache entries (default 3600s).

**tune.ssl.maxrecord <size>**
  Maximum SSL record size for dynamic record sizing (default tune.bufsize).

**tune.ssl.default-dh-param <bits>**
  Default DH parameter size when no custom parameters are provided.

### HTTP/2 Tuning

**tune.h2.initial-window-size <number>**
  Default HTTP/2 initial window size (default 16384). Controls bytes per stream before ACK required.

**tune.h2.max-concurrent-streams <number>**
  Default max concurrent streams per connection (default 100).

**tune.h2.fe.rxbuf / tune.h2.be.rxbuf <size>**
  HTTP/2 receive buffer for frontend/backend connections (default ~1600k).

### QUIC Tuning

**tune.quic.fe.sock-per-conn { default-on | force-off }**
  Allocate dedicated socket per QUIC connection (default-on) or share listener socket (force-off). Dedicated sockets give best performance.

**tune.quic.fe.max-idle-timeout / tune.quic.be.max-idle-timeout <timeout>**
  QUIC max idle timeout (default 30s). Connection silently closed after this inactivity period.

**tune.quic.fe.cc.max-win-size / tune.quic.be.cc.max-win-size <size>**
  Maximum congestion window size for QUIC (default 480k).

### Memory Management

**tune.vars.proc-max-size / tune.vars.sess-max-size / tune.vars.txn-max-size**
  Maximum memory per variable scope. Prevents memory exhaustion from variable abuse.

**-m <limit>**
  Limit allocatable memory in megabytes (command line). Causes connection refusals under extreme load.

## Defaults Section

Inherited by all subsequent proxy sections. Multiple defaults sections allowed, each applies to proxies declared after it.

**mode { http | tcp | health }**
  Operating mode. `http` enables HTTP protocol processing and features. `tcp` is raw TCP/UDP passthrough. `health` is for monitoring-only proxies.

**timeout connect <delay>**
  Maximum time to wait for a connection attempt to a server to be accepted (default 5000ms).

**timeout client <delay>**
  Maximum inactivity time on the client side (default 50000ms).

**timeout server <delay>**
  Maximum inactivity time on the server side (default 50000ms).

**timeout tunnel <delay>**
  Maximum inactivity time for tunnels such as WebSocket or PROXY protocol (default 1h).

**timeout http-keep-alive <delay>**
  Maximum time to wait for a new HTTP request on keep-alive connections (default idle).

**timeout http-request <delay>**
  Maximum time to receive the whole HTTP request including headers (default 30s in HAProxy 3.x, was unlimited before).

**option httplog / log global**
  Enable HTTP-format logging or inherit global loggers.

**retries <number>**
  Number of retries before marking a server as down (default 3).

**default-server**
  Default parameters for all server lines in this proxy's backends. Options include `check`, `inter`, `fall`, `rise`, `weight`, `maxconn`, `ssl`, etc.

## Frontend Section

Client-facing proxy definition. Accepts connections and routes to backends.

### Bind Options

**bind <address>[:port] [param]* **
  Define a listening address. Multiple bind lines per frontend. Address formats:
  - `*:80` — all interfaces, port 80
  - `0.0.0.0:80` — all IPv4
  - `[::]:80` — all IPv6
  - `/path/to/socket` — UNIX socket
  - `fd@<n>` — inherited file descriptor
  - `ip@<addr>:<port>` — specific IP
  - `tcp@`, `udp@`, `quic4@`, `quic6@` — protocol-specific prefixes

Common bind options:
- `ssl crt <file>` — SSL certificate(s). Multiple certs for SNI.
- `alpn h2,http/1.1` — ALPN protocol negotiation
- `accept-proxy` — accept PROXY protocol v1
- `accept-proxy-v2` — accept PROXY protocol v2
- `name <name>` — named bind line (for runtime SSL updates)
- `shards <number>` — number of listening sockets for SO_REUSEPORT
- `process <pattern>` — which threads process this listener
- `expose-fd listeners` — expose file descriptors for seamless reload

### Routing

**default_backend <backend>**
  Default backend for connections not matching any use_backend rule.

**use_backend <backend> [if|unless <condition>]**
  Route to specific backend when condition matches. Evaluated in order, first match wins.

**use_service <service> [if|unless <condition>]**
  Route to an internal service (stats, errorfiles, lua services).

### HTTP Request/Response Rules

**http-request <action> [if|unless <condition>]**
  Actions applied during request processing. Common actions:
  - `deny [denied_status] [type <content-type>] [lf <log-format>]` — reject request
  - `allow` — explicitly allow (stops rule evaluation)
  - `redirect prefix|location|code <url> [code <status>]` — redirect
  - `return <status> [content-type <ct>] [lf <fmt>] [data <body>]` — return response
  - `set-header <name> <value>` — set/replace request header
  - `add-header <name> <value>` — append request header
  - `del-header <name>` — delete request header
  - `set-path %[converters]` — rewrite URL path
  - `set-var(<var>) <expr>` — set variable
  - `track-sc0 [src|dst] [table <table>]` — track source in stick-table

**http-response <action> [if|unless <condition>]**
  Same action types but applied during response processing.

### TCP Rules

**tcp-request connection <action> [if|unless <cond>]**
  Actions during connection establishment (before any data).

**tcp-request content <action> [if|unless <cond>]**
  Actions during request payload inspection.

**tcp-response content <action> [if|unless <cond>]**
  Actions during response payload inspection.

### Monitoring

**monitor-uri <uri>**
  Return 200 OK for the specified URI, or 503 if too many servers are down. Used by external health monitors.

**monitor fail if { <condition> }**
  Override monitor status based on conditions.

## Backend Section

Server farm definition with load balancing and health checks.

### Load Balancing Algorithms

**balance <algorithm>**
  - `roundrobin` — each server weighted by weight. Default for HTTP mode.
  - `static-rr` — round-robin without dynamic weight adjustment.
  - `leastconn` — fewest active connections wins. Default for TCP mode.
  - `first` — fill first server before using next. Good for VM power management.
  - `source` — source IP hash. Deterministic, no stickiness needed.
  - `uri [<hash-type>] [url_param <param>]` — URI-based hashing. For cache farms.
  - `url_param <param>` — hash on specific URL parameter value.
  - `hdr(<name>) [sha1|ldap_dn]` — hash on HTTP header value.
  - `rdp-cookie` — RDP cookie hashing for terminal server farms.
  - `random [map-dynamic|map-size <n>]` — random selection with optional consistent hashing.

### Server Definition

**server <name> <address>[:port] [param]* **
  Define a backend server. Common options:
  - `check` — enable health checking
  - `inter <delay>` — health check interval (default 2000ms)
  - `fall <count>` — consecutive failures before marking down (default 3)
  - `rise <count>` — consecutive successes before marking up (default 2)
  - `weight <1-256>` — server weight for load distribution
  - `maxconn <number>` — per-server connection limit
  - `backup` — only used when all non-backup servers are down
  - `disabled` — start in disabled state
  - `ssl [verify required|optional|none]` — SSL to backend
  - `crt <file>` — client certificate for mutual TLS
  - `ca-file <file>` — CA for server verification
  - `send-proxy` / `send-proxy-v2` — send PROXY protocol
  - `resolvers <name>` — use DNS resolver for address resolution
  - `resolve-prefer { ipv4 | ipv6 }` — preferred address family
  - `observe { layer4 | layer7 } [defer-on-demand]` — passive health monitoring
  - `slowstart <delay>` — progressive weight ramp-up after becoming available
  - `agent-inter <delay> addr <addr> port <port> send "<string>"` — agent check
  - `track <backend>/<server>` — inherit state from another server
  - `pool-max-conns <n> pool-max-queue <n>` — idle connection pool limits
  - `http-reuse { safe | always | disabled | connection }` — connection reuse mode

### Health Check Types

**tcp-check**
  TCP connect check (default). Verifies port is accepting connections.

**http-check method OPTIONS / GET / HEAD**
  HTTP-based health check. Sends request and validates response.
  - `http-check expect status <range>` — expected status codes
  - `http-check send meth <method> uri <uri> ver <version> host <host>`
  - `http-check expect string "<pattern>"` — match response body
  - `http-check expect rstring "<regex>"` — regex match on response

**smtp-check hello <name>**
  SMTP EHLO/HELO check.

**ssl-hello-check**
  SSL/TLS handshake verification.

**ldap-check**
  LDAP bind check.

**mysql-check / pgsql-check / redis-check**
  Database-specific checks (MySQL ping, PostgreSQL query, Redis PING).

**external-check**
  External program-based health checking (requires `insecure-fork-wanted`).
  - `external-check command <cmd> [args]`
  - `external-check cmd-options accept-invalid-certificate`

### Connection Reuse

**http-reuse { safe | always | disabled | connection }**
  Controls how backend connections are reused:
  - `safe` — reuse only for same server, no mixing clients
  - `always` — maximum reuse, multiple clients per connection (HTTP/2 recommended)
  - `disabled` — new connection per request
  - `connection` — one client per connection

**http-pretend-keepalive**
  Pretend the server supports keep-alive even if it closes connections. Useful for servers that don't send Connection: keep-alive but actually support it.

## Peers Section

Stick-table replication between HAProxy nodes.

```
peers mycluster
    peer node1 10.0.0.1:10000
    peer node2 10.0.0.2:10000
    peer node3 10.0.0.3:10000
```

- Symmetrical protocol — any peer can connect to any other
- Single TCP session per peer pair (last connected wins)
- Heartbeat every 3s, considered dead after 5s of silence
- Replicates stick-table entries in real-time

## Resolvers Section

Built-in DNS resolver for runtime address resolution.

```
resolvers mydns
    nameserver dns1 10.0.0.2:53
    nameserver dns2 10.0.0.3:53
    hold valid 5s
    hold other 1s
    hold nx 1s
    hold refused 1s
    hold timeout 1s
    accepted_payload_size 8192
    resolve-prefer ipv4
```

- `hold valid <time>` — cache TTL for valid responses
- `hold other/nx/refused/timeout <time>` — cache TTL for error responses
- Supports round-robin DNS (multiple A/AAAA records)
- Server lines with `resolvers <name>` use this resolver
- Address changes propagate to running servers at runtime

## Cache Section

HTTP response caching in memory.

```
cache mycache
    total-max-size 1024m
    max-age 3600s
    queue-size 5
    data-only
```

- `total-max-size` — maximum cache size
- `max-age / max-fresh / max-stale` — age controls
- `data-only` — store only response body (no headers)
- Enable in proxy with `enable-cache <cache-name>`
- Cache is RAM-only, no persistence across restarts
