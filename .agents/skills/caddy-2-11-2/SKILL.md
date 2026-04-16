---
name: caddy-2-11-2
description: Complete Caddy 2.11.2 web server toolkit covering Caddyfile configuration, JSON API, CLI commands, automatic HTTPS with Let's Encrypt and ZeroSSL, reverse proxy, TLS/SSL setup, PKI, modules, and extensions. Use when configuring Caddy as a web server or reverse proxy, setting up automatic HTTPS, creating Caddyfile configurations, managing certificates, building Go applications on Caddy platform, or implementing production-ready HTTP/HTTPS servers with zero downtime reloads.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.11.2"
tags:
  - web server
  - reverse proxy
  - HTTPS
  - Caddyfile
  - automatic SSL
  - ACME
  - HTTP/3
  - TLS
  - PKI
category: infrastructure
external_references:
  - https://github.com/caddyserver/caddy/tree/v2.11.2
  - https://github.com/caddyserver/website
---

# Caddy 2.11.2

A powerful, enterprise-ready, open source web server with automatic HTTPS written in Go. Every site on HTTPS by default.

## Overview

Caddy is an extensible server platform that uses TLS by default. It supports:

- **Easy configuration** with the [Caddyfile](https://caddyserver.com/docs/caddyfile)
- **Powerful configuration** with native [JSON config](https://caddyserver.com/docs/json/)
- **Dynamic configuration** via the [JSON API](https://caddyserver.com/docs/api)
- **[Config adapters](https://caddyserver.com/docs/config-adapters)** for non-JSON formats (Caddyfile, JSON5, YAML, TOML, NGINX)
- **Automatic HTTPS** with Let's Encrypt, ZeroSSL, or fully-managed local CA for internal names & IPs
- **HTTP/1.1, HTTP/2, and HTTP/3** all supported by default
- **Zero-downtime config reloads** via API or `caddy reload`
- **Modular architecture** — only include what you need
- **Runs anywhere** with no external dependencies (not even libc)

Caddy is a project of [ZeroSSL](https://zerossl.com).

## When to Use

Use this skill when:
- Configuring Caddy as a web server or reverse proxy
- Setting up automatic HTTPS with Let's Encrypt or ZeroSSL
- Writing Caddyfile configurations for single or multiple sites
- Working with Caddy's JSON configuration and API
- Implementing TLS/SSL with custom certificates, client auth, or ECH
- Building Go applications that run on the Caddy platform
- Setting up static file serving, template rendering, or basic authentication
- Configuring load balancing, health checks, or circuit breakers for upstreams
- Managing PKI (Certificate Authority) operations
- Deploying Caddy via systemd, Docker, or cloud platforms

## Core Concepts

### Configuration Formats

Caddy's native configuration is a **JSON document**. However, you can use config adapters to write in other formats:

| Format | Description | Best For |
|--------|-------------|----------|
| JSON (native) | Caddy's native format | Programmatic config, API usage |
| Caddyfile | Human-friendly config file | Manual editing, quick setup |
| JSON5, YAML, TOML | Alternative structured formats | Preferences/team conventions |
| NGINX | NGINX config adapter | Migration from NGINX |

### The Caddyfile Structure

A Caddyfile consists of one or more **site blocks**, each starting with an address:

```caddyfile
# Global options block (optional, must be first)
{
    email you@example.com
    admin localhost:2019
}

# Snippet (optional, reusable config block)
(snippet) {
    header X-Frame-Options DENY
}

# Site block 1
example.com {
    # Matchers can be defined here
    @post method POST
    
    # Directives execute in a specific order
    reverse_proxy @post localhost:9001
    file_server /static
    
    # Import reusable snippets
    import snippet
}

# Site block 2
www.example.com {
    redir https://example.com{uri}
}
```

**Key syntax rules:**
- Opening `{` must be at end of line, preceded by a space
- Closing `}` must be on its own line
- Single site block: braces are optional
- Directives execute in a defined order (unless inside `route` blocks)
- Whitespace separates tokens; quote multi-word values

### Addresses

Addresses define what hostnames and ports Caddy listens on:

```caddyfile
# Listen on port 443 for example.com (HTTPS auto-enabled)
example.com { ... }

# Listen on specific port, no HTTPS
:8080 { ... }

# Multiple addresses
example.com www.example.com { ... }

# Bind to specific interfaces
bind 192.168.1.1 :443 {
    protocols h2 h3
}
```

### Directives

Directives are functional keywords that customize how the site is served:

```caddyfile
site.example.com {
    # Handler directives (process requests)
    respond "Hello" 200
    file_server /public
    reverse_proxy localhost:8080
    
    # Container directives (group other directives)
    route /api/* {
        reverse_proxy backend1:8080
        reverse_proxy backend2:8080
    }
    
    handle /graphql {
        reverse_proxy graphql:4000
    }
}
```

**Directive types:**
- **Handler directives**: Process requests (e.g., `respond`, `file_server`, `reverse_proxy`)
- **Container directives**: Group other directives (`route`, `handle`, `handle_path`)
- **Config directives**: Set server-level options (`tls`, `log`, `bind`)

### Matchers

Match requests by various criteria:

```caddyfile
# Built-in matchers
@get method GET
@static path /static*
@json header Content-Type application/json
@ip remote 10.0.0.0/8

# Combined matchers
@api method {GET POST} path /api/*

# Custom matchers using other modules
@secure tls {}
```

### Placeholders

Caddy supports template-style placeholders throughout config:

```caddyfile
{http.request.host}
{http.request.method}
{http.request.header.X-Forwarded-For}
{host}
{scheme}
{path}
{query}
{remote_host}
{timestamp:2006-01-02 15:04:05}
```

### Snippets

Reusable configuration blocks:

```caddyfile
(snippet_security) {
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Strict-Transport-Security "max-age=63072000"
    }
}

example.com {
    import snippet_security
    file_server
}
```

### Global Options

Top-level configuration:

```caddyfile
{
    # ACME CA settings
    email admin@example.com
    
    # Admin API
    admin {
        disabled false
        address :2019
    }
    
    # Default server settings
    servers {
        listen :443
        protocols h1 h2 h3
        trusted_proxies static private_ranges
    }
    
    # Auto-HTTPS
    auto_https off|strict|ignore_invalid_hsts|disable_redirects|enforce_enforce
    
    # Logging
    log {
        output file /var/log/caddy/access.log {
            roll_size 10MiB
            roll_keep 10
        }
    }
    
    # Storage
    storage filesystem {
        path /var/lib/caddy
    }
    
    # DNS providers for ACME
    dns cloudflare {env.CLOUDFLARE_API_KEY}
}
```

### PKI (Certificate Management)

Caddy includes a built-in PKI app:

```caddyfile
# Use Let's Encrypt (default)
example.com { tls }

# Use ZeroSSL
example.com { tls { issuer acme zerossl } }

# Custom certificate files
example.com {
    tls /path/to/cert.pem /path/to/key.pem
}

# Internal CA for local domains
internal.example.com {
    tls internal
}

# ACME with custom CA endpoint
example.com {
    tls {
        ca https://acme.example.com/dir
        key_type ed25519
    }
}
```

## Installation

### Package Managers

```bash
# macOS
brew install caddy

# Debian/Ubuntu (official repo)
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install caddy

# Arch Linux
pacman -S caddy

# NixOS
nix-env -iA nixpkgs.caddy

# Snap
snap install caddy
```

### Download Pre-built Binaries

```bash
# Install with DNS plugins and other extras
curl https://caddyserver.com/api/download?os=linux&arch=amd64&tag=v2.11.2&include=cloudflare,dns.providers.cloudflare | tar xz -C /usr/local/bin caddy

# Minimal download (no plugins)
curl -O https://github.com/caddyserver/caddy/releases/download/v2.11.2/caddy_2.11.2_linux_amd64.tar.gz
tar xzf caddy_2.11.2_linux_amd64.tar.gz
sudo mv caddy /usr/local/bin/
```

### Build from Source (Go 1.25+)

```bash
git clone https://github.com/caddyserver/caddy.git
cd caddy/cmd/caddy/
go build

# Grant port binding capability on Linux
sudo setcap cap_net_bind_service=+ep ./caddy
```

### Build with xcaddy (Custom Plugins)

```bash
xcaddy build \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/caddy-custom/module
```

## Usage Examples

### Basic Static File Server

```caddyfile
example.com {
    root * /var/www/html
    file_server
}
```

### Reverse Proxy

```caddyfile
api.example.com {
    reverse_proxy localhost:3000
}

# With load balancing
lb.example.com {
    reverse_proxy {
        to backend1:8080 backend2:8080 backend3:8080
        lb_policy round_robin
        health_uri /health
        health_interval 10s
        health_timeout 5s
    }
}

# With headers
proxy.example.com {
    reverse_proxy localhost:8080 {
        header_up Host {upstream_hostport}
        header_up X-Real-IP {remote_host}
        header_down X-Caddy-Proxy "true"
    }
}
```

### HTTPS Redirect

```caddyfile
# Auto HTTP→HTTPS redirect (default)
example.com { ... }

# Disable auto redirect
example.com {
    auto_https off
}
```

### TLS Configuration

```caddyfile
secure.example.com {
    tls admin@example.com {
        protocols tls1.3
        ciphers TLS_AES_256_GCM_SHA384
        curves x25519 secp384r1
        
        client_auth {
            mode verify_if_given
            trusted_leaf_cert_file /etc/caddy/client-ca.pem
        }
        
        key_type ed25519
    }
}
```

### Basic Authentication

```caddyfile
protected.example.com {
    basicauth {
        # Use: caddy hash-password --plaintext mypassword
        admin $2a$14$...hash...
        user $2a$14$...hash...
    }
    file_server
}
```

### Template Rendering

```caddyfile
# With Go templates
blog.example.com {
    root * /var/www/blog
    templates
    file_server
}

# With frontmatter (YAML, JSON, TOML) in markdown files
{{ define "title" }}My Blog{{ end }}
---
title: "Welcome"
date: 2024-01-01
---
Hello, world!
```

### HTTP/3 Support

```caddyfile
# HTTP/3 enabled by default when HTTPS is on
example.com {
    reverse_proxy localhost:8080
}

# Specify protocols explicitly
example.com {
    bind example.com
    protocols h1 h2 h3
    reverse_proxy localhost:8080
}
```

### Admin API Usage

```bash
# Get current config
curl localhost:2019/config/ | jq

# Load new config
curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @caddy.json

# Partial config update (add a route)
curl -X POST localhost:2019/config/apps/http/servers/myserver/routes/... \
    -H "Content-Type: application/json" \
    -d '{
        "handle": [{"handler": "static_response", "body": "Updated!"}]
    }'

# Reload config file
caddy reload --config Caddyfile

# Validate config without running
caddy validate --config Caddyfile

# Adapt Caddyfile to JSON
caddy adapt --config Caddyfile --pretty > caddy.json
```

### Systemd Service

```ini
# /etc/systemd/system/caddy.service
[Unit]
Description=Caddy Web Server
Documentation=https://caddyserver.com/docs/
After=network-online.target

[Service]
User=caddy
Group=caddy
ExecReload=/usr/bin/caddy reload --config /etc/caddy/Caddyfile --force
TimeoutStopSec=5s
LimitNOFILE=1048576
PrivateTmp=true
ProtectSystem=full
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
```

### Docker

```bash
docker run -d --name caddy \
    -p 80:80 -p 443:443 \
    -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile \
    -v caddy_data:/data \
    -v caddy_config:/config \
    caddy:latest
```

## Caddyfile Directives Reference

### Core HTTP Directives

| Directive | Type | Description |
|-----------|------|-------------|
| `respond` | Handler | Return a fixed response |
| `redir` | Handler | Redirect requests |
| `file_server` | Handler | Serve static files |
| `reverse_proxy` | Handler | Proxy to upstream servers |
| `abort` | Handler | Abort the request immediately |
| `error` | Handler | Generate an error response |
| `route` | Container | Group directives with custom order |
| `handle` | Container | Match and group directives |
| `handle_path` | Container | Strip prefix and match |
| `vars` | Handler | Set variables/placeholders |
| `log` | Config | Configure access logging |
| `skip_log` | Handler | Skip logging for matched requests |

### TLS Directives

| Directive | Type | Description |
|-----------|------|-------------|
| `tls` | Config | Configure TLS certificates and settings |
| `bind` | Config | Specify network interfaces and protocols |

### Authentication & Security

| Directive | Type | Description |
|-----------|------|-------------|
| `basicauth` | Handler | HTTP Basic Authentication |
| `forward_auth` | Handler | Forward authentication to external service |

### Advanced Directives

| Directive | Type | Description |
|-----------|------|-------------|
| `handle_errors` | Config | Configure error page handling |
| `invoke` | Handler | Invoke another named route |
| `templates` | Handler | Render Go templates and markdown with frontmatter |
| `request_body` | Handler | Read request body into variable |

## CLI Commands Reference

### Server Management

| Command | Description |
|---------|-------------|
| `caddy run` | Start Caddy in foreground (daemon mode) |
| `caddy start` | Start Caddy in background |
| `caddy stop` | Stop running Caddy process |
| `caddy reload` | Gracefully reload config without downtime |

### Configuration

| Command | Description |
|---------|-------------|
| `caddy adapt` | Convert Caddyfile to JSON |
| `caddy validate` | Validate a configuration file |
| `caddy fmt` | Format/pretty-print a Caddyfile |

### Diagnostics & Utilities

| Command | Description |
|---------|-------------|
| `caddy version` | Print version |
| `caddy build-info` | Print build information |
| `caddy list-modules` | List installed modules |
| `caddy environ` | Print environment variables |
| `caddy hash-password` | Hash a password for basicauth |
| `caddy completion` | Generate shell completions |

### Server Utilities

| Command | Description |
|---------|-------------|
| `caddy file-server` | Quick static file server |
| `caddy respond` | Quick hard-coded HTTP server |
| `caddy reverse-proxy` | Quick reverse proxy |

### Storage & Certificates

| Command | Description |
|---------|-------------|
| `caddy trust` | Install CA cert into system trust store |
| `caddy untrust` | Remove CA cert from trust store |
| `caddy storage export` | Export storage contents |
| `caddy storage import` | Import storage contents |

### Upgrade (Experimental)

| Command | Description |
|---------|-------------|
| `caddy upgrade` | Replace binary with latest version |
| `caddy add-package` | Add plugins to current binary |
| `caddy remove-package` | Remove plugins from current binary |

## Signal Handling

| Signal | Behavior |
|--------|----------|
| `SIGINT` | Graceful exit (send again for immediate) |
| `SIGQUIT` | Immediate quit, cleans up storage locks |
| `SIGTERM` | Graceful exit |
| `SIGUSR1` | Reload config (if running with Caddyfile, no API changes) |

## JSON Configuration Structure

Caddy's native config is a JSON document:

```json
{
  "admin": {
    "listen": ":2019"
  },
  "logging": {
    "logs": {
      "default": {
        "writer": {
          "output": "file",
          "filename": "/var/log/caddy/access.log"
        }
      }
    }
  },
  "apps": {
    "http": {
      "servers": {
        "example": {
          "listen": [":443"],
          "routes": [
            {
              "handle": [
                {
                  "handler": "subroute",
                  "routes": [
                    {
                      "handle": [
                        {
                          "handler": "static_response",
                          "body": "Hello, world!"
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ],
          "tls_connection_policies": [...],
          "listeners": [...]
        }
      }
    },
    "tls": {
      "automation": {
        "policies": [...]
      }
    },
    "pki": {
      "cas": {
        "local": {}
      }
    }
  }
}
```

## Reference Files

- [`references/01-caddyfile-directives.md`](references/01-caddyfile-directives.md) - Complete directive reference with syntax, options, and examples
- [`references/02-tls-ssl-guide.md`](references/02-tls-ssl-guide.md) - TLS configuration, certificates, client auth, ECH, ALPN
- [`references/03-reverse-proxy.md`](references/03-reverse-proxy.md) - Reverse proxy patterns, load balancing, health checks, circuit breakers
- [`references/04-json-config.md`](references/04-json-config.md) - JSON configuration structure, API operations, traversal with @id
- [`references/05-pki-certificates.md`](references/05-pki-certificates.md) - PKI app, CA management, certificate lifecycle, ACME settings

## References

- Official documentation: https://caddyserver.com/docs/
- GitHub repository (v2.11.2): https://github.com/caddyserver/caddy/tree/v2.11.2
- Website source: https://github.com/caddyserver/website
- API tutorial: https://caddyserver.com/docs/api-tutorial
- Caddyfile tutorial: https://caddyserver.com/docs/caddyfile-tutorial
- Community forum: https://caddy.community
