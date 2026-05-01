# Management and Runtime CLI

## Starting HAProxy

### Command Line Options

```
haproxy [<options>]*
```

Key options:
- `-f <file>` or `-- <files>` — configuration file(s). Multiple files supported.
- `-D` — daemon mode (detach from terminal)
- `-W` — master-worker mode
- `-Ws` — master-worker with systemd notify support
- `-db` — disable background mode (foreground, for testing)
- `-c` — check configuration and exit (exit 0 = valid, non-zero = error)
- `-c -V` — check and print "Configuration file is valid" on success
- `-cc "<condition>"` — evaluate a conditional expression
- `-d` — debug mode (foreground, show events)
- `-dW` — zero-warning mode (refuse to start if any warnings)
- `-dr` — ignore server address resolution failures
- `-df <file>` — dump configuration after parsing
- `-L <name>` — set local peer name
- `-m <limit>` — memory limit in megabytes
- `-n <limit>` — per-process connection limit
- `-p <file>` — write PID file
- `-q` — quiet mode
- `-S <bind>` — master CLI socket (master-worker mode)
- `-sf <pid>*` — graceful stop of old processes after boot
- `-st <pid>*` — hard stop of old processes after boot
- `-x <unix_socket>` — retrieve listening sockets from old process (seamless reload)
- `-v` — version
- `-vv` — version, build options, library versions, pollers

### Safe Start Pattern

```bash
haproxy -f /etc/haproxy/haproxy.cfg \
        -D -p /var/run/haproxy.pid \
        -sf $(cat /var/run/haproxy.pid)
```

### Master-Worker Mode

```bash
# Start with master-worker
haproxy -W -f /etc/haproxy/haproxy.cfg -D

# Reload (send SIGUSR2 to master process)
kill -USR2 $(head -1 /var/run/haproxy.pid)
```

The master monitors workers and forks new ones on reload. Old workers finish existing connections before exiting.

## Stopping HAProxy

### Graceful Stop (SIGUSR1)

Process stops accepting new connections but finishes processing existing ones. Used for seamless reloads.

```bash
kill -USR1 <pid>
```

### Hard Stop (SIGTERM)

Immediately terminates all connections and exits. Used for stop/restart actions.

```bash
kill -TERM <pid>
```

### Seamless Reload

```bash
# 1. Validate new configuration
haproxy -c -f /etc/haproxy/haproxy.cfg.new

# 2. Start new process with graceful handoff
haproxy -f /etc/haproxy/haproxy.cfg.new \
        -D -p /var/run/haproxy.pid \
        -sf $(cat /var/run/haproxy.pid)
```

Two small windows of potential connection drops during reload:
1. Brief moment when old process pauses listening (SIGTTOU/SIGTTIN sequence, ~1ms)
2. When old process closes listening ports (kernel may not redistribute pending connections)

On systems with SO_REUSEPORT support (Linux 3.9+, BSD), the first window is eliminated.

## Unix Socket CLI

HAProxy exposes a management interface via Unix sockets (or TCP). Commands are sent line-by-line using `socat` or similar tools.

### Connecting to the Socket

```bash
# Interactive session
socat /var/run/haproxy.sock readline

# Single command
echo "show stat" | socat stdio /var/run/haproxy.sock
```

### Stats Socket Configuration

In configuration file:

```
global
    stats socket /var/run/haproxy-admin.sock mode 660 level admin
    stats socket /var/run/haproxy-user.sock mode 660 level user
    stats socket /var/run/haproxy-op.sock mode 660 level operator expose-fd listeners

# Or in a proxy section
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
```

Access levels:
- **user** — read-only commands (show info, show stat)
- **operator** — user + limited write (set var, show errors)
- **admin** — full access (set server weight, enable/disable servers)

### Key CLI Commands

#### Process Information

```
show info                    # HAProxy status and version
show info typed              # Typed output for monitoring
show info json               # JSON format output
show proc                   # List processes (master-worker mode)
show env [<name>]           # Show environment variables
```

#### Statistics

```
show stat [;csv]             # Proxy/server statistics
show servers state [<backend>]  # Server states (savable to file)
show backend                 # List backends
```

CSV stats format includes: `pxname,svname,qcur,qmax,scur,smax,slim,stot,bin,bout,dreq,dresp,ereq,econ,eresp,wretr,wredis,status,weight,...`

#### Server Management

```
# Enable/disable servers
enable server <backend>/<server>
disable server <backend>/<server>

# Set server state (ready/drain/maint)
set server <backend>/<server> state ready
set server <backend>/<server> state drain
set server <backend>/<server> state maint

# Change weight
set weight <backend>/<server> <weight>[%]
set server <backend>/<server> weight <weight>

# Force health state
set server <backend>/<server> health up
set server <backend>/<server> health down
set server <backend>/<server> health stopping

# Change address (runtime)
set server <backend>/<server> addr <ip> [port <port>]
set server <backend>/<server> check-addr <ip> [port <port>]

# Add/remove servers dynamically
add server <backend>/<server> <address> [options...]
del server <backend>/<server>

# Change FQDN (requires resolvers configured)
set server <backend>/<server> fqdn <FQDN>
```

#### SSL Certificate Management

```
# Show certificates
show ssl cert [<bind>]

# Update certificate (transactional)
set ssl cert <filename> <<\n<pem-data>\n
commit ssl cert <filename>
abort ssl cert <filename>

# Update OCSP response
set ssl ocsp-response <base64-encoded-der-response>

# Update TLS ticket key
set ssl tls-key <id> <base64-tls-key>

# Show TLS keys
show tls-keys [<id>]
```

Certificate rotation without downtime:
1. `set ssl cert mycert.pem <<` followed by new PEM data
2. `commit ssl cert mycert.pem` to apply
3. `abort ssl cert mycert.pem` to rollback if needed

#### Stick-Table Management

```
show table [<table>]         # Show stick-table contents
clear table <table>          # Clear all entries
set table <table> key <key> [data.<type> <value>]
del table <table> key <key>
```

Dynamic IP blocking:
```
# Block an IP by setting a flag in the stick-table
set table http-in key 192.168.1.100 data.gpc0 1

# ACL to check the flag
acl is_blocked sc_gpc0(0) -m int gt 0
http-request deny if is_blocked
```

#### Variable Management

```
get var <name>               # Read variable value
set var proc.<name> <expr>   # Set process-wide variable
unset var proc.<name>        # Unset variable
```

#### Rate Limiting

```
set rate-limit connections global <value>
set rate-limit sessions global <value>
set rate-limit ssl-sessions global <value>
```

#### Debugging and Diagnostics

```
show errors [<proxy>] [request|response]  # Last HTTP protocol errors
show acl [<acl>]                          # ACL contents
show map [<map>]                          # Map contents
show resolvers [<section>]                # DNS resolver statistics
show peers [dict|-] [<peers section>]     # Peer replication status
show sess [<options>]                     # Active sessions/streams
show fd [-!plcfbsd]* [<fd>]              # File descriptor dump
show pools [byname|bysize|byusage]        # Memory pool status
show dev                                  # Platform/process info for debugging
show quic [<format>] [<filter>]           # QUIC connection info
show ssl ech <bind>                       # ECH configuration
```

## Statistics Page

Built-in web statistics interface:

```
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
    stats auth admin:password
    stats admin if LOCALHOST
```

Options:
- `stats enable` — enable statistics page
- `stats uri <uri>` — URL path for the stats page
- `stats refresh <delay>` — auto-refresh interval
- `stats hide-version` — hide HAProxy version from page
- `stats auth <user>:<password>` — HTTP basic authentication
- `stats admin { if | unless } <condition>` — enable admin actions
- `stats scope <backend>` — limit stats to specific backend
- `stats show-legends` — show legend on graphs
- `stats show-node` — display node name
- `stats show-desc <text>` — custom description

## Server State Persistence

Save and restore server states across reloads:

```
# Save current state
echo "show servers state" | socat stdio /var/run/haproxy.sock > /tmp/haproxy.state

# In configuration, load saved state
backend web-servers
    load-server-state-from-file global

# Or via global directive
global
    server-state-file /var/lib/haproxy/stats
```

## Logging

HAProxy sends logs to syslog. Configure in rsyslog or similar:

```
# /etc/rsyslog.d/49-haproxy.conf
local0.* /var/log/haproxy.log
```

Or UDP-based logging:
```
# HAProxy config
global
    log 127.0.0.1:514 udp local0

# rsyslog
$AddUnixListenSocket /dev/log
$ModLoad imudp
$UDPServerRun 514
local0.* /var/log/haproxy.log
```

### Log Formats

**HTTP log format** (default):
```
192.168.1.1:54321 [27/Mar/2024:10:15:30.123] fe-http be-web srv1 0/0/1/2/3 200 1234 - - ---- 100/50/20/10/0 0/0 "GET /path HTTP/1.1"
```

**TCP log format** (default):
```
192.168.1.1:54321 [27/Mar/2024:10:15:30.123] fe-tcp be-tcp srv1 0/0/1/0 0 -- 1/1/0/0/0 0/0
```

Custom log format with `log-format` or `log-format clf`:
```
log-format "%ci:%cp [%tr] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Ta %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"
```

## Systemd Integration

```ini
[Unit]
Description=HAProxy Load Balancer
After=network.target network-online.target systemd-modules-load.service
Wants=network-online.target

[Service]
Environment="CONFIG=/etc/haproxy/haproxy.cfg"
EnvironmentFile=-/etc/haproxy/haproxy.env
ExecStartPre=/usr/local/bin/haproxy -f $CONFIG -c -q
ExecStart=/usr/local/bin/haproxy -Ws -f $CONFIG -p /run/haproxy.pid
ExecReload=/usr/local/bin/haproxy -f $CONFIG -c -q \
         && kill -USR2 $(head -1 /run/haproxy.pid)
KillMode=mixed
KillSignal=SIGUSR1
TimeoutStopSec=5
Restart=on-failure
LimitNOFILE=500000

[Install]
WantedBy=multi-user.target
```

## Well-Known Traps to Avoid

- **Never use `ulimit-n`** unless absolutely necessary — HAProxy computes FD needs automatically since version 1.5
- **Do not swap** — the machine running HAProxy must never swap. Set `vm.swappiness=0`
- **Do not artificially throttle CPU** — sub-CPU allocation in hypervisors causes high context-switch latency
- **Remove vestigial `tune.maxaccept`** from old configs — default of 4 is optimal with multi-queue
- **Do not try to auto-detect PROXY protocol** — always explicitly configure `accept-proxy` or `accept-proxy-v2`. Auto-detection opens security holes
- **HTTP request timeout** — HAProxy 3.x defaults `timeout http-request` to 30s (was unlimited before). Legacy clients may need adjustment
- **With `http-reuse always`**, reduce `tune.h2.be.max-concurrent-streams` to avoid head-of-line blocking (values 1-5 typically)
