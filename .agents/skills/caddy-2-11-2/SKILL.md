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
  - https://caddy.community
  - https://caddyserver.com/docs/
  - https://caddyserver.com/docs/api-tutorial
  - https://caddyserver.com/docs/caddyfile-tutorial
  - https://github.com/caddyserver/website
---
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
| JSON5, YAML, TOML | Alternative structured formats | Preference/team conventions |
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

## Installation / Setup
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

## Advanced Topics
## Advanced Topics

- [Caddyfile Directives](reference/01-caddyfile-directives.md)
- [Tls Ssl Guide](reference/02-tls-ssl-guide.md)
- [Reverse Proxy](reference/03-reverse-proxy.md)
- [Json Config](reference/04-json-config.md)
- [Pki Certificates](reference/05-pki-certificates.md)
- [Usage Examples](reference/06-usage-examples.md)
- [Caddyfile Directives Reference](reference/07-caddyfile-directives-reference.md)
- [Cli Commands Reference](reference/08-cli-commands-reference.md)
- [Signal Handling](reference/09-signal-handling.md)
- [Json Configuration Structure](reference/10-json-configuration-structure.md)

