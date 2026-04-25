# Reverse Proxy Guide

Complete guide to reverse proxy configuration in Caddy 2.11.2.

## Basic Reverse Proxy

```caddyfile
# Simple proxy to a single backend
example.com {
    reverse_proxy localhost:8080
}

# With custom host header
example.com {
    reverse_proxy localhost:8080 {
        header_up Host {upstream_hostport}
    }
}

# Proxy with path prefix
example.com/api {
    reverse_proxy localhost:3000
}
```

---

## Load Balancing

### LB Policies

| Policy | Description |
|--------|-------------|
| `round_robin` | Distribute requests evenly (default) |
| `random` | Random selection |
| `first` | First available backend |
| `nearest` | Nearest backend (custom metric) |
| `latency` | Lowest latency backend |
| `ip_hash` | Hash-based on client IP |
| `uri_hash` | Hash-based on URI |
| `header_<name>` | Hash based on header value |
| `cookie_<name>` | Hash based on cookie value |

### Configuration

```caddyfile
example.com {
    reverse_proxy {
        # Backend addresses
        to backend1:8080 backend2:8080 backend3:8080
        
        # Load balancing policy
        lb_policy round_robin
        
        # Number of retry attempts
        lb_retries 2
        
        # Time between retries
        lb_try_interval 5s
        
        # Maximum total time for all retries
        lb_try_duration 5m
        
        # Match healthy backends by response
        lb_response_matcher status 200-299
    }
}
```

---

## Health Checks

### Active Health Checks

```caddyfile
example.com {
    reverse_proxy {
        to backend1:8080 backend2:8080
        
        # Health check configuration
        health_uri /health
        health_interval 10s
        health_timeout 5s
        health_status 200
        health_body `ok`
        
        # Health check headers
        health_headers X-Health-Check true
        
        # Follow redirects during health checks
        health_follow_redirects true
    }
}
```

### Passive Health Checks (Fails Filter)

```caddyfile
example.com {
    reverse_proxy {
        to backend1:8080 backend2:8080
        
        # Mark backend as unhealthy for these status codes
        fails_filter `5[0-9]{2}`
        
        # Or use regex patterns
        fails_filter `(5\d{2}|429)`
    }
}
```

### Circuit Breaker

```caddyfile
example.com {
    reverse_proxy {
        to backend1:8080
        
        # Circuit breaker expression (uses go-expr or native)
        circuit_breaker rate(10, 60s)
        
        # Or custom expression
        circuit_breaker failures > 5 and window == 60s
    }
}
```

### Flapping Detection

```caddyfile
example.com {
    reverse_proxy {
        to backend1:8080
        
        # Detect flapping (rapid up/down transitions)
        flapping_retries 3
        flapping_interval 30s
        flapping_window 5m
    }
}
```

---

## Request Rewriting

### Strip Path Prefix/Suffix

```caddyfile
# Strip /api prefix before proxying
example.com/api {
    reverse_proxy localhost:8080 {
        strip_prefix /api
    }
}

# Strip suffix
example.com/files {
    reverse_proxy localhost:8080 {
        strip_suffix .html
    }
}

# Rewrite path field
example.com/api {
    reverse_proxy localhost:8080 {
        rewrite * /v1{path}
    }
}
```

### Header Rewriting

```caddyfile
example.com {
    reverse_proxy localhost:8080 {
        # Upstream request headers
        header_up Host {upstream_hostport}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-Port {server_port}
        header_up X-Request-ID {request.id}
        
        # Response headers to strip
        header_down -Server
        header_down -X-Powered-By
        
        # Add custom response headers
        header_down X-Proxy "Caddy"
    }
}
```

---

## Transport Configuration

### HTTP Transport

```caddyfile
example.com {
    reverse_proxy localhost:8080 {
        transport http {
            # TLS settings for upstream
            tls
            tls_connection_safety_timeout 10s
            tls_handshake_timeout 10s
            tls_max_size 2MB
            tls_min_version tls1.2
            tls_server_name upstream.example.com
            
            # Buffer sizes
            read_buffer 4KB
            write_buffer 4KB
            max_response_header_size 8KB
            
            # Timeouts
            dial_timeout 30s
            dial_fallback_delay 500ms
            fallback_delay 3s
            
            # HTTP/2 settings
            initial_stream_window_size 65535
            initial_connection_window_size 65535
            max_concurrent_streams 128
            max_streams 10000
            
            # Proxy protocol support
            proxy_protocol 1|2|*|header
            
            # TLS ALPN for upstream
            tls_alpn h2
            
            # Force HTTPS to upstream
            force_https true
            
            # Disable keep-alives
            ows true
            
            # Require SNI on upstream
            strict_sni_host true
        }
    }
}
```

### FastCGI Transport

```caddyfile
# PHP via FastCGI
example.com {
    reverse_proxy {
        to unix//run/php/php-fpm.sock
        
        transport fastcgi {
            split .php
            index index.php
            root /var/www/html
            
            # Environment variables for PHP
            env APP_ENV production
            env APP_DEBUG false
            
            # Timeouts
            read_timeout 30s
            write_timeout 30s
            
            # Keep-alive interval
            keepalive 60s
            
            # Max bytes per second
            maxbytespersec 10MB
        }
    }
}
```

### H2C Transport (HTTP/2 Cleartext)

```caddyfile
# HTTP/2 without TLS
example.com {
    reverse_proxy h2c://localhost:9090
}

# With explicit transport config
example.com {
    reverse_proxy localhost:9090 {
        transport h2c {
            read_buffer 4KB
        }
    }
}
```

### WebSocket Transport

```caddyfile
# WebSocket proxy (automatically handles upgrade)
example.com/ws {
    reverse_proxy localhost:8080 {
        transport websocket {
            read_buffer 4KB
        }
    }
}
```

---

## Proxy Protocol

```caddyfile
example.com {
    reverse_proxy upstream:8080 {
        # Send PROXY protocol header to upstream
        proxy_protocol 2
        
        # Or accept PROXY from client (for cloud providers)
        trusted_proxies static private_ranges 10.0.0.0/8
    }
}
```

---

## Upstream Address Formats

```caddyfile
# Direct address
reverse_proxy localhost:8080

# With scheme
reverse_proxy http://localhost:8080
reverse_proxy https://localhost:8443

# Unix socket (Linux/macOS)
reverse_proxy unix//run/app.sock

# Unix domain socket (Windows named pipe)
reverse_proxy unix///./pipe/app

# Multiple backends with weights
reverse_backend:8080 backend2:8080 weight 2
```

---

## Advanced Patterns

### Blue-Green Deployment

```caddyfile
example.com {
    reverse_proxy {
        to blue:8080 green:8080
        
        # Route based on header
        lb_policy header_X_Deployment green
        
        health_uri /health
        health_interval 10s
    }
}
```

### API Gateway Pattern

```caddyfile
api.example.com {
    # Auth middleware via forward_auth
    forward_auth auth-service:9000 {
        uri /validate
        copy_headers Authorization
    }
    
    # Route to different backends by path
    handle /v1/* {
        reverse_proxy v1-backend:8080 {
            strip_prefix /v1
        }
    }
    
    handle /v2/* {
        reverse_proxy v2-backend:8080 {
            strip_prefix /v2
        }
    }
    
    # Default response
    respond "API Gateway" 200
}
```

### Rate Limiting (via external service)

```caddyfile
example.com {
    reverse_proxy ratelimit-service:9000 {
        header_up X-Real-IP {remote_host}
        header_up X-Request-ID {request.id}
    }
}
```

### Compression

```caddyfile
example.com {
    reverse_proxy localhost:8080 {
        # Enable response compression
        compression gzip
        
        # Or disable buffering for streaming
        buffer_responses false
    }
}
```

---

## Metrics Namespace

```caddyfile
example.com {
    reverse_proxy localhost:8080 {
        metrics /metrics/my-proxy
    }
}
```

---

## Troubleshooting

### Enable Debug Logging

```caddyfile
example.com {
    reverse_proxy localhost:8080 {
        # Debug mode for proxy
    }
}

# Or via CLI
caddy run --config Caddyfile 2>&1 | grep -i "reverse"
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check upstream is running and address is correct |
| TLS handshake error | Verify upstream cert or use `tls_insecure_skip_verify` equivalent via JSON |
| 502 Bad Gateway | Upstream returned invalid response; check upstream logs |
| Slow responses | Increase `dial_timeout` and check network latency |
| Connection reset | Check `read_buffer`/`write_buffer` sizes for large payloads |
