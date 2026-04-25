# JSON Configuration Guide

Complete guide to Caddy's native JSON configuration format.

## Overview

Caddy's native configuration is a JSON document that fully describes the server state. All other config formats (Caddyfile, etc.) are adapted to this JSON structure before use.

## Top-Level Structure

```json
{
  "admin": { ... },
  "logging": { ... },
  "apps": { ... }
}
```

---

## Admin Configuration

Controls the administration endpoint:

```json
{
  "admin": {
    "listen": ":2019",
    "shutdown_pause_duration": "30s",
    "origins": ["localhost", "127.0.0.1"],
    "trusted_origins": ["*"],
    "enable_profiling": false,
    "identity_provider": { ... },
    "key_auth": {
      "headers": ["Authorization"]
    }
  }
}
```

### Disable Admin API

```json
{
  "admin": {
    "disabled": true
  }
}
```

---

## Logging Configuration

```json
{
  "logging": {
    "logs": {
      "default": {
        "writer": {
          "module": "file",
          "output": {
            "module": "file",
            "filename": "/var/log/cidy/access.log",
            "rotation": {
              "rotate_size": "10MiB",
              "rotate_keep": 10,
              "rotate_keep_age": "30d"
            }
          },
          "encoder": {
            "module": "console",
            "time_format": "2006-01-02T15:04:05.000Z07:00"
          }
        },
        "encoder_console": {},
        "log_calls": true,
        "level": "INFO",
        "exclude": ["httpServerError"]
      },
      "recorder": {
        "writer": {
          "module": "file",
          "output": {
            "module": "file",
            "filename": "/var/log/ciddy/recorder.log"
          }
        }
      }
    }
  }
}
```

### Log Encoders

| Encoder | Module Name | Description |
|---------|-------------|-------------|
| Console | `console` | Human-readable, colorized output |
| Unified | `unified` | Caddy's default log format |
| JSON | `json` | Machine-parseable JSON lines |

---

## HTTP App Configuration

```json
{
  "apps": {
    "http": {
      "servers": {
        "server-name": {
          "listen": [":443"],
          "listener_wrap": null,
          "protocols": ["h1", "h2", "h3"],
          "routes": [...],
          "tls_connection_policies": [...],
          "trusted_proxies": {...},
          "allow_h2c": false,
          "strict_dedup_routes": true
        }
      },
      "flightslog": {},
      "http_port": 80,
      "https_port": 443,
      "http2": {
        "max_request_duration": "10s"
      },
      "grpc": {}
    }
  }
}
```

### Server Configuration

```json
{
  "apps": {
    "http": {
      "servers": {
        "example": {
          "listen": [":443"],
          "protocols": ["h1", "h2", "h3"],
          "tracing": {
            "continue_from": "https://opentelemetry.io/go"
          },
          "metrics": true,
          "no_stdlib": true,
          "idle_timeout": "30s",
          "read_header_timeout": "5s",
          "max_header_bytes": 1048576
        }
      }
    }
  }
}
```

### Routes Structure

```json
{
  "apps": {
    "http": {
      "servers": {
        "example": {
          "routes": [
            {
              "match": [
                {
                  "host": ["example.com"]
                }
              ],
              "handle": [
                {
                  "handler": "subroute",
                  "routes": [
                    {
                      "handle": [
                        {
                          "handler": "static_response",
                          "body": "Hello, World!"
                        }
                      ]
                    },
                    {
                      "handle": [
                        {
                          "handler": "file_server",
                          "root": "/var/www/html"
                        }
                      ],
                      "terminal": true
                    }
                  ]
                }
              ],
              "terminal": true
            }
          ]
        }
      }
    }
  }
}
```

### Route Matchers

```json
{
  "match": [
    {
      "host": ["example.com", "*.example.com"],
      "path": ["/api/*", "/docs"],
      "method": ["GET", "POST"],
      "header": {
        "Content-Type": ["application/json"]
      },
      "remote_ip": ["10.0.0.0/8", "192.168.1.1"],
      "query": {
        "page": ["1"],
        "q": ["*"]
      }
    }
  ]
}
```

### Named Routes with @id

```json
{
  "apps": {
    "http": {
      "servers": {
        "example": {
          "routes": [
            {
              "@id": "api-route",
              "handle": [
                {
                  "handler": "reverse_proxy",
                  "upstreams": [
                    {"dial": "backend1:8080"},
                    {"dial": "backend2:8080"}
                  ]
                }
              ],
              "terminal": true
            }
          ]
        }
      }
    }
  }
}
```

---

## TLS App Configuration

```json
{
  "apps": {
    "tls": {
      "automation": {
        "policies": [
          {
            "issuers": [
              {
                "module": "acme",
                "email": "admin@example.com",
                "ca": "https://acme-v02.api.letsencrypt.org/directory",
                "challenges": {
                  "http": {},
                  "tls-alpn-01": {},
                  "dns": {
                    "provider": {
                      "name": "cloudflare",
                      "api_token": {"$env": "CLOUDFLARE_API_KEY"}
                    }
                  }
                }
              }
            ],
            "subjects": ["example.com"],
            "on_demand": {
              "max_requests": 3,
              "rate_limit": "1m"
            },
            "renewal_window_ratio": 0.33
          }
        ]
      },
      "certificate_removal": true,
      "default_issuers": ["acme"]
    }
  }
}
```

---

## PKI App Configuration

```json
{
  "apps": {
    "pki": {
      "cas": {
        "local": {
          "root_ca_key_storage": "local",
          "intermediate_ca_key_storage": "local"
        }
      },
      "certificate_roles": {},
      "retain_certs": true
    }
  }
}
```

---

## Storage Configuration

### Filesystem Storage

```json
{
  "storage": {
    "module": "filesystem",
    "root": "~/.local/share/caddy"
  }
}
```

### Other Storage Modules

| Module | Description |
|--------|-------------|
| `filesystem` | Local filesystem (default) |
| `blobstore` | S3-compatible object storage |

---

## Module Registration Pattern

Caddy modules are registered using Go's init() pattern:

```go
import (
    "github.com/caddyserver/caddy/v2"
)

func init() {
    caddy.RegisterModule(MyHandler{})
}

type MyHandler struct{}

func (MyHandler) CaddyModule() caddy.ModuleInfo {
    return caddy.ModuleInfo{
        ID:  "http.handlers.my_handler",
        New: func() caddy.Module { return &MyHandler{} },
    }
}

func (h *MyHandler) Provision(ctx caddy.Context) error {
    // Setup resources
    return nil
}

func (h *MyHandler) ServeHTTP(w http.ResponseWriter, r *http.Request, _ interface{}) error {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Hello from custom handler!"))
    return nil
}

func (h *MyHandler) Cleanup() error {
    // Clean up resources
    return nil
}
```

---

## API Operations

### POST /load — Set/Replace Config

```bash
curl -X POST localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @caddy.json
```

### GET /config/[path] — Export Config

```bash
# Get entire config
curl localhost:2019/config/ | jq

# Get specific path
curl localhost:2019/config/apps/http/servers/example/routes | jq

# Pretty print
curl localhost:2019/config/ | python3 -m json.tool
```

### POST /config/[path] — Create/Replace/Append

```bash
# Append to array (routes)
curl -X POST localhost:2019/config/apps/http/servers/example/routes/... \
    -H "Content-Type: application/json" \
    -d '{
        "handle": [{"handler": "static_response", "body": "New route"}]
    }'

# Replace object value
curl -X POST localhost:2019/config/apps/http/servers/example/idle_timeout \
    -H "Content-Type: application/json" \
    -d '"30s"'
```

### PUT /config/[path] — Create/Insert

```bash
# Insert into array at specific index
curl -X PUT localhost:2019/config/apps/http/servers/example/routes/0 \
    -H "Content-Type: application/json" \
    -d '{...}'
```

### PATCH /config/[path] — Modify Existing Element

```bash
# Modify existing element in place
curl -X PATCH localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
    -H "Content-Type: application/json" \
    -d '"Modified response"'
```

### DELETE /config/[path] — Delete Value

```bash
# Delete entire route
curl -X DELETE localhost:2019/config/apps/http/servers/example/routes/0

# Delete specific setting
curl -X DELETE localhost:2019/config/apps/http/servers/example/idle_timeout
```

### POST /adapt — Adapt Without Running

```bash
# Adapt Caddyfile to JSON (via API)
curl -X POST localhost:2019/adapt \
    -H "Content-Type: text/caddyfile" \
    --data-binary @Caddyfile | jq

# With adapter parameter
curl -X POST localhost:2019/adapt \
    -H "Content-Type: application/json5" \
    --data-binary '@config.json5' | jq
```

### POST /stop — Stop Process

```bash
curl -X POST localhost:2019/stop
```

---

## Using @id for Config Traversal

Named routes and blocks make API operations easier:

```json
{
  "apps": {
    "http": {
      "servers": {
        "example": {
          "routes": [
            {
              "@id": "my-api-route",
              "handle": [
                {
                  "handler": "reverse_proxy",
                  "upstreams": [{"dial": "backend:8080"}]
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

Then access via API:

```bash
# Get by ID
curl localhost:2019/config/apps/http/servers/example/routes/@id/my-api-route | jq

# Modify by ID
curl -X PATCH localhost:2019/config/apps/http/servers/example/routes/@id/my-api-route/handle/0/upstreams/0/dial \
    -H "Content-Type: application/json" \
    -d '"new-backend:8080"'
```

---

## Config Examples

### Minimal Production Config

```json
{
  "admin": {
    "listen": ":2019"
  },
  "logging": {
    "logs": {
      "default": {
        "writer": {
          "module": "file",
          "output": {
            "module": "file",
            "filename": "/var/log/ciddy/access.log",
            "rotation": {
              "rotate_size": "10MiB",
              "rotate_keep": 10
            }
          },
          "encoder": {
            "module": "console"
          }
        }
      }
    }
  },
  "apps": {
    "http": {
      "servers": {
        "example": {
          "listen": [":443"],
          "protocols": ["h1", "h2", "h3"],
          "routes": [
            {
              "handle": [
                {
                  "handler": "static_response",
                  "body": "Hello, World!"
                }
              ],
              "terminal": true
            }
          ]
        }
      }
    },
    "tls": {
      "automation": {
        "policies": [
          {
            "issuers": [
              {
                "module": "acme",
                "email": "admin@example.com"
              }
            ]
          }
        ]
      }
    }
  }
}
```

### Reverse Proxy with Load Balancing

```json
{
  "apps": {
    "http": {
      "servers": {
        "lb": {
          "listen": [":443"],
          "routes": [
            {
              "handle": [
                {
                  "handler": "reverse_proxy",
                  "upstreams": [
                    {"dial": "backend1:8080"},
                    {"dial": "backend2:8080"},
                    {"dial": "backend3:8080"}
                  ],
                  "lb_policy": "round_robin",
                  "health_uri": "/health",
                  "health_interval": "10s"
                }
              ],
              "terminal": true
            }
          ]
        }
      }
    }
  }
}
```
