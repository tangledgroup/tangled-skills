# Architecture and Operations

## Caddy Architecture

Caddy consists of three parts:

1. **Command** — CLI interface, minimal code for bootstrapping the core
2. **Core library** — Manages configuration lifecycle (`Run()` and `Stop()`)
3. **Modules** — Everything else (HTTP serving, TLS, logging, etc.)

The core knows only two methods to call on apps: `Start()` and `Stop()`. All functionality beyond that is provided by modules. Caddy's config document has top-level fields the core recognizes (`admin`, `logging`) and opaque fields for apps (`apps`).

### Module Lifecycle

Modules go through four phases:

1. **Load** — Deserialize JSON bytes into typed values
2. **Provision** — Setup work, load guest modules, validate configuration
3. **Use** — Active operation (handling requests, managing TLS, etc.)
4. **Cleanup** — Free allocated resources when config is unloaded

Modules have IDs consisting of a namespace and name (e.g., `http.handlers.reverse_proxy`). Host modules load guest modules; all modules are guests of something.

### Config Management

Caddy treats configs as immutable atomic units. During reload:

1. New config is provisioned in full
2. If provisioning succeeds, old config is cleaned up
3. Briefly, both configs operate simultaneously
4. On failure, old config remains active (automatic rollback)

This approach provides ACID-like guarantees with only one background lock and minimal global state. Each config has its own context holding module state.

### Plugging In

Modules register themselves via Go imports:

```go
import (
    _ "github.com/caddyserver/caddy/v2"
    _ "github.com/caddy-dns/cloudflare"
)
```

Use `xcaddy` to build with plugins:

```bash
xcaddy build WITH=github.com/caddy-dns/cloudflare
```

Or manually: create a folder, copy Caddy's `main.go`, add imports, run `go mod init caddy`, then `go build`.

## Logging

Caddy uses structured logging (zero-allocation via zap). Logs are JSON by default with strongly-typed fields.

### Log Pipeline

1. **Logger** — Emits messages with level, message, and typed fields
2. **Log** — Processes messages with encoder, writer, level filter, sampling
3. **Encoder** — Transforms in-memory data to bytes (JSON, console, etc.)
4. **Writer** — Outputs bytes (stdout, file, network)

### Configuring Logs

Global option for all logs:

```caddy
{
    log default {
        output stdout
        format json
        level INFO
        include http.log.access admin.api
        exclude tls.syncer
    }
}
```

Per-site access logging:

```caddy
example.com {
    log {
        output file /var/log/example.com/access.log {
            roll_size 100mb
            roll_keep 10
            roll_gzip
        }
        format json
    }
}
```

Enable debug logging for troubleshooting:

```caddy
{
    debug
}
```

## Metrics

Prometheus metrics enabled via global option:

```caddy
{
    metrics {
        per_host              # Per-host tags
        observe_catchall_hosts
    }
}
```

Or per-site with the `metrics` directive:

```caddy
example.com {
    metrics {
        listen :9184
    }
}
```

Default endpoint: `/metrics` at admin API address (`http://localhost:2019/metrics`).

Key metrics:

- `caddy_http_requests_total` — Request counter by server, handler, status, method
- `caddy_http_request_duration_seconds` — Histogram of round-trip durations
- `caddy_http_response_size_bytes` — Response body size histogram
- `caddy_http_requests_in_flight` — Active request gauge
- `caddy_http_request_errors_total` — Error counter
- `caddy_reverse_proxy_upstreams_healthy` — Upstream health gauge (0 or 1)

Sample Prometheus queries:

```
# Request rate per second (5m average)
rate(caddy_http_requests_total{handler="file_server"}[5m])

# 95th percentile request duration
histogram_quantile(0.95, sum(rate(caddy_http_request_duration_seconds_bucket{handler="reverse_proxy"}[5m])) by (le))
```

Prometheus scrape config:

```yaml
scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

## Running as a Service

### Linux (systemd)

Official packages install `caddy.service` automatically. Manual installation:

```ini
# /etc/systemd/system/caddy.service
[Unit]
Description=Caddy
Documentation=https://caddyserver.com/docs/
After=network.target network-online.target
Requires=network-online.target

[Service]
Type=notify
User=caddy
Group=www-data
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/Caddyfile
ExecReload=/usr/bin/caddy reload --config /etc/caddy/Caddyfile
TimeoutStopSec=5s
LimitNOFILE=1048576
LimitNPROC=512
Restart=always
RestartPreventExitStatus=1
RestartSec=42s

[Install]
WantedBy=multi-user.target
```

Override service settings:

```bash
sudo systemctl edit caddy
```

Add environment variables:

```ini
[Service]
Environment="CF_API_TOKEN=super-secret-token"
# Or:
EnvironmentFile=/etc/caddy/.env
```

Use JSON config instead of Caddyfile:

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

Restart on crash:

```ini
[Service]
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

### Docker Compose

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"    # HTTP/3
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

Reload in Docker:

```bash
# Via exec (all versions)
docker compose exec -w /etc/caddy caddy caddy reload

# Via SIGUSR1 (v2.11.0+)
docker compose kill -sUSR1 caddy
```

Install local CA for development:

```bash
# Linux
docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt && sudo update-ca-certificates

# macOS
docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt /tmp/root.crt \
    && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt
```

### Windows

Using sc.exe:

```powershell
sc.exe create caddy start= auto binPath= "C:\path\to\caddy.exe run"
sc.exe start caddy
sc.exe stop caddy
```

Using WinSW: create `caddy-service.xml` and run `caddy-service install`.

## Conventions

### Network Addresses

Format: `network/address` where network is optional (default: `tcp`):

- `:8080` — TCP on all interfaces, port 8080
- `127.0.0.1:8080` — TCP localhost
- `[::1]:8080` — TCP IPv6 localhost
- `unix//path/to/socket` — Unix socket
- `unix//path/to/socket|0200` — Unix socket with permissions
- `:8080-8085` — Port range (multiplied into individual addresses)

Network types: `tcp`, `tcp4`, `tcp6`, `udp`, `udp4`, `udp6`, `ip`, `ip4`, `ip6`, `unix`, `unixgram`, `unixpacket`.

### File Locations

Data directory (certificates, keys):

- Linux/BSD: `$HOME/.local/share/caddy` (or `$XDG_DATA_HOME/caddy`)
- Windows: `%AppData%\Caddy`
- macOS: `$HOME/Library/Application Support/Caddy`

Configuration directory (persisted config):

- Linux/BSD: `$HOME/.config/caddy` (or `$XDG_CONFIG_HOME/caddy`)
- Windows: `%AppData%\Caddy`
- macOS: `$HOME/Library/Application Support/Caddy`

The data directory must not be treated as a cache — it contains TLS certificates and keys.

### Durations

Go `time.ParseDuration` format plus `d` for days:

- `ns`, `us`/`µs`, `ms`, `s`, `m`, `h`, `d`
- Examples: `250ms`, `5s`, `1.5h`, `2h45m`, `90d`

In JSON, durations can also be integers representing nanoseconds.

## Troubleshooting Strategies

1. **Define expected behavior clearly** — "I expect a 301 redirect" not "it should work"
2. **Observe current behavior specifically** — "Getting 200 instead of 301, Server header shows Caddy"
3. **Check all logs** — Enable debug logging, collect more than you think you need
4. **Doubt assumptions** — Verify DNS, verify config was actually reloaded, verify binary path
5. **Reproduce minimally** — Eliminate config complexity until problem disappears
6. **Explore behaviors** — Vary one thing at a time, notice patterns

Common issues:
- Connection problems are almost always DNS
- Config not reloading — use `caddy reload`, not stop/start
- Certificate rate limits — use staging endpoint during testing
- Docker networking — `localhost` means "this container", use service names
