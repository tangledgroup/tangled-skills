# Usage Examples

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
