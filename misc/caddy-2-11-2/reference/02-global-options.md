# Global Options

Global options apply server-wide and are configured in a block at the very top of the Caddyfile with no keys:

```caddy
{
    # global options here
}
```

There can only be one global options block, and it must be first.

## General Options

**`debug`** — Enables debug-level logging for the default logger. Use when troubleshooting.

**`http_port <port>`** — Internal HTTP port (default: `80`). Used for ACME HTTP challenge; does not change the client-facing port.

**`https_port <port>`** — Internal HTTPS port (default: `443`).

**`default_bind <hosts...>`** — Default bind address(es) for all sites without explicit `bind` directive.

**`order <dir1> first|last|[before|after <dir2>]`** — Assign execution order to HTTP handler directives. Required for third-party modules that lack default ordering.

```caddy
{
    order replace after encode
}
```

**`storage <module_name> { ... }`** — Configures Caddy's storage mechanism. Default is `file_system`. Used to sync certificates across Caddy instances.

**`storage_clean_interval <duration>`** — How often to scan for old/expired assets (default: `24h`).

**`admin off|<addr> { ... }`** — Customizes the admin API endpoint. Default: `localhost:2019`. Can use unix socket for file-permission access control:

```caddy
{
    admin unix//run/caddy-admin.sock
}
```

Sub-options:
- `origins <origins...>` — Allowed origins for CORS
- `enforce_origin` — Force Origin header validation

Setting `admin off` disables config reloads without process restart.

**`persist_config off`** — Disables persisting JSON config to disk (default: enabled).

**`log [name] { ... }`** — Configures named loggers. Multiple loggers can be defined:

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

Sub-options: `output`, `format`, `level`, `include`, `exclude`.

**`grace_period <duration>`** — Grace period for shutting down HTTP servers during config changes. Default: eternal (connections never forcefully closed).

**`shutdown_delay <duration>`** — Delay before grace period begins, useful for health checkers to detect impending shutdown:

```caddy
{
    shutdown_delay 30s
}

example.com {
    handle /health-check {
        @goingDown vars {http.shutting_down} true
        respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
        respond 200
    }
}
```

**`metrics { ... }`** — Enables Prometheus metrics:

```caddy
{
    metrics {
        per_host
        observe_catchall_hosts
    }
}
```

## TLS Options

**`auto_https off|disable_redirects|ignore_loaded_certs|disable_certs`** — Controls automatic HTTPS behavior. `off` disables both cert automation and HTTP-to-HTTPS redirects but does not change the default protocol (still HTTPS when hostname present).

**`email <yours>`** — Email for ACME account creation, recommended for certificate problem notifications.

**`default_sni <name>`** — Default TLS ServerName for clients without SNI.

**`fallback_sni <name>`** — Fallback ServerName when original doesn't match any cached certificate (experimental).

**`local_certs`** — Issue all certificates internally instead of through ACME CAs. Useful for development.

**`skip_install_trust`** — Skip installing local CA root into system trust store.

**`acme_ca <directory_url>`** — ACME CA directory URL. Use Let's Encrypt staging for testing:

```caddy
{
    acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

**`acme_ca_root <pem_file>`** — PEM file with trusted root cert for ACME CA.

**`acme_eab { ... }`** — External Account Binding for ACME transactions:

```caddy
{
    acme_eab {
        key_id GD-VvWydSVFuss_GhBwYQQ
        mac_key MjXU3MH-Z0WQ...
    }
}
```

**`acme_dns <provider> ...`** — ACME DNS challenge provider for all transactions.

**`dns <provider> ...`** — Default DNS provider (for ACME and ECH publication).

**`key_type ed25519|p256|p384|rsa2048|rsa4096`** — Key type for new certificates.

**`cert_issuer <name> ...`** — Certificate issuer to use.

**`renew_interval <duration>`** — How often to attempt certificate renewal.

**`ocsp_stapling off`** — Disable OCSP stapling.

**`preferred_chains { ... }`** — Control certificate chain selection:

```caddy
{
    preferred_chains smallest {
        root_common_name "ISRG Root X1"
    }
}
```

## Server Options

**`servers [<listener_address>] { ... }`** — Configure HTTP server behavior:

```caddy
{
    servers {
        timeouts {
            read_body   10s
            read_header 10s
            write       30s
            idle        3m
        }
        keepalive_interval 30s
        keepalive_idle     30s
        keepalive_count    100
        max_header_size    2MB
        protocols h1 h2 h3

        trusted_proxies static private_ranges
        trusted_proxies_strict
        client_ip_headers X-Real-IP X-Forwarded-For

        strict_sni_host on
    }
}
```

**`0rtt off`** — Disable TLS 1.3 0-RTT (pre-play).

**`enable_full_duplex`** — Enable full-duplex HTTP/2.

**`log_credentials`** — Include credentials in access logs.

**`trace`** — Enable request tracing.

## File Systems

**`filesystem <name> <module> { ... }`** — Register named file systems for reuse:

```caddy
{
    filesystem myfs file_system {
        root /var/www
    }
}
```

## PKI Options

**`pki { ... }`** — Configure Caddy's built-in PKI for local certificate authorities:

```caddy
{
    pki {
        ca local {
            name "My Local CA"
            root_cn "My Root"
            intermediate_cn "My Intermediate"
            intermediate_lifetime 180d
            maintenance_interval 24h
        }
    }
}
```

## On-Demand TLS

**`on_demand_tls { ... }`** — Enable dynamic certificate issuance during TLS handshakes:

```caddy
{
    on_demand_tls {
        ask http://localhost:8080/ask
        rate_limit 10 1m
    }
}
```

Must be restricted with `ask` endpoint or `permission` module to prevent abuse.

## ECH (Encrypted ClientHello)

**`ech <public_names...> { ... }`** — Enable ECH for hiding SNI in TLS handshakes:

```caddy
{
    dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    ech example.com
}
```

Requires a caddy-dns module for your DNS provider to publish HTTPS DNS records.

## Events

**`events { ... }`** — Handle Caddy lifecycle events:

```caddy
{
    events {
        on caddy.start exec /usr/bin/my-script.sh
    }
}
```
