# PKI and Certificate Management

Complete guide to Caddy's Public Key Infrastructure (PKI) app for certificate lifecycle management.

## Overview

Caddy includes a built-in PKI app that manages:
- **Certificate issuance** via ACME (Let's Encrypt, ZeroSSL, custom CA)
- **Local CA** for internal/private domains
- **Certificate storage** and rotation
- **OCSP stapling** and renewal
- **Certificate pinning** and trust management

---

## PKI App Configuration

```json
{
  "apps": {
    "pki": {
      "cas": {
        "local": {}
      },
      "certificate_roles": {},
      "retain_certs": true
    }
  }
}
```

### Custom CA Configuration

```json
{
  "apps": {
    "pki": {
      "cas": {
        "local": {
          "root_ca_key_storage": "local",
          "intermediate_ca_key_storage": "local",
          "root": "/path/to/root-ca.pem",
          "root_key": "/path/to/root-ca-key.pem"
        }
      }
    }
  }
}
```

---

## Certificate Automation Policies

### Default Policy (All Domains)

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

### Per-Domain Policies

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
                "ca": "https://acme-v02.api.letsencrypt.org/directory"
              }
            ],
            "subjects": ["example.com", "*.example.com"]
          },
          {
            "issuers": [
              {
                "module": "acme",
                "email": "admin@example.com",
                "ca": "https://acme.zerossl.com/v2/DV90"
              }
            ],
            "subjects": ["zerossl-site.com"]
          },
          {
            "issuers": [
              {
                "module": "internal"
              }
            ],
            "subjects": ["*.internal.local"]
          }
        ]
      }
    }
  }
}
```

### On-Demand Issuance (Arbitrary Hostnames)

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
                "email": "admin@example.com"
              }
            ],
            "on_demand": {
              "max_requests": 3,
              "rate_limit": "1m",
              "interval": "10s",
              "burst": 5
            }
          }
        ]
      }
    }
  }
}
```

**On-demand settings:**
- `max_requests` — Maximum concurrent on-demand requests
- `rate_limit` — Time window for rate limiting
- `interval` — Minimum time between requests
- `burst` — Maximum burst size

---

## ACME Issuer Configuration

### Let's Encrypt

```json
{
  "issuers": [
    {
      "module": "acme",
      "email": "admin@example.com",
      "ca": "https://acme-v02.api.letsencrypt.org/directory",
      "challenges": {
        "http": {},
        "tls-alpn-01": {},
        "dns": {}
      }
    }
  ]
}
```

### ZeroSSL

```json
{
  "issuers": [
    {
      "module": "acme",
      "email": "admin@example.com",
      "ca": "https://acme.zerossl.com/v2/DV90",
      "eab": {
        "key_id": "<EAB_KEY_ID>",
        "mac_key": "<EAB_MAC_KEY>"
      }
    }
  ]
}
```

### DNS Challenge Providers

```json
{
  "challenges": {
    "dns": {
      "provider": {
        "name": "cloudflare",
        "api_token": {"$env": "CLOUDFLARE_API_KEY"}
      }
    }
  }
}
```

**Supported DNS providers:**
- `cloudflare`
- `digitalocean`
- `gandi`
- `godaddy`
- `namecheap`
- `route53` (AWS)
- `ovh`
- `hetzner`
- `infomaniak`
- `lexicon`

### DNS Challenge Configuration

```json
{
  "challenges": {
    "dns": {
      "provider": {
        "name": "cloudflare",
        "api_token": {"$env": "CLOUDFLARE_API_KEY"}
      },
      "resolvers": ["8.8.8.8", "1.1.1.1"],
      "propagation_timeout": "2m",
      "propagation_delay": "30s",
      "disable_resolvedns_check": false,
      "override_domain": "example.com"
    }
  }
}
```

### Key Type Configuration

```json
{
  "issuers": [
    {
      "module": "acme",
      "key_type": "ed25519"
    }
  ]
}
```

**Supported key types:** `p256`, `p384`, `rsa2048`, `rsa4096`, `ed25519`

---

## Internal CA (Local PKI)

### Basic Configuration

```json
{
  "apps": {
    "tls": {
      "automation": {
        "policies": [
          {
            "issuers": [
              {
                "module": "internal"
              }
            ],
            "subjects": ["*.local", "localhost"]
          }
        ]
      }
    }
  }
}
```

### Custom Local CA

```json
{
  "apps": {
    "pki": {
      "cas": {
        "local": {
          "root": "/etc/caddy/pki/authorities/local/ca.crt",
          "root_key": "/etc/caddy/pki/authorities/local/ca.key"
        }
      }
    },
    "tls": {
      "automation": {
        "policies": [
          {
            "issuers": [
              {
                "module": "internal"
              }
            ],
            "subjects": ["*.mylocal.com"]
          }
        ]
      }
    }
  }
}
```

### Internal Issuer Options

```json
{
  "issuers": [
    {
      "module": "internal",
      "key_type": "p256",
      "not_before": "2024-01-01T00:00:00Z",
      "not_after": "2030-01-01T00:00:00Z"
    }
  ]
}
```

---

## Certificate Storage

### Filesystem Storage (Default)

```json
{
  "storage": {
    "module": "filesystem",
    "root": "~/.local/share/caddy"
  }
}
```

### S3-Compatible Storage

```json
{
  "storage": {
    "module": "blobstore",
    "provider": {
      "module": "s3",
      "access_key_id": {"$env": "AWS_ACCESS_KEY_ID"},
      "secret_access_key": {"$env": "AWS_SECRET_ACCESS_KEY"},
      "region": "us-east-1",
      "bucket": "caddy-certificates"
    }
  }
}
```

---

## Certificate Lifecycle

### Renewal Settings

```json
{
  "automation": {
    "policies": [
      {
        "issuers": [{"module": "acme"}],
        "renewal_window_ratio": 0.33,
        "renewal_window": "720h"
      }
    ]
  }
}
```

**Renewal settings:**
- `renewal_window_ratio` — Fraction of cert lifetime before expiry to renew (default: ~30 days)
- `renewal_window` — Fixed renewal window duration

### Certificate Retention

```json
{
  "apps": {
    "pki": {
      "retain_certs": true,
      "certificate_removal": true
    }
  }
}
```

---

## ACME Server (Built-in CA)

Caddy can act as an ACME server for managing certificates across infrastructure:

```json
{
  "apps": {
    "pki": {
      "cas": {
        "acme": {
          "_name": "my-acme",
          "root_ca_key_storage": "local",
          "intermediate_ca_key_storage": "local",
          "policy": {
            "allowed": [
              {"origins": ["10.0.0.0/8"]},
              {"match": {"sni": ["*.internal.example.com"]}}
            ]
          }
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
                "ca": "http://acme-server:8010/dir",
                "challenges": {
                  "dns": {
                    "provider": {
                      "name": "cloudflare",
                      "api_token": {"$env": "CLOUDFLARE_API_KEY"}
                    }
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

---

## Certificate API Endpoints

### List CAs

```bash
curl localhost:2019/pki/ca/
# Returns: ["local", "acme-issuer-id"]
```

### Get CA Info

```bash
curl localhost:2019/pki/ca/local | jq
```

### List Certificates

```bash
# List all certificates for a CA
curl localhost:2019/pki/ca/local/certificates | jq

# List specific CA's certificates
curl localhost:2019/pki/ca/acme/certificates | jq
```

### Export Certificate

```bash
# Get certificate chain
curl localhost:2019/pki/certificates/export | jq
```

---

## CLI Commands for PKI

### Trust Management

```bash
# Install Caddy's local CA into system trust store
sudo caddy trust

# Install specific CA
caddy trust --ca my-ca-id

# Remove from trust store
caddy untrust

# Specific certificate
caddy untrust --cert /path/to/cert.pem
```

### Storage Migration

```bash
# Export storage contents
caddy storage export -c Caddyfile.old -o caddy-storage.tar.gz

# Import to new config
caddy storage import -c Caddyfile.new -i caddy-storage.tar.gz

# Pipe between different storage backends
caddy storage export -c old-config.json -o- | \
  caddy storage import -c new-config.json -i-
```

---

## Certificate Debugging

### View Certificate Details

```bash
# Check what certificates Caddy has loaded
curl localhost:2019/config/apps/tls/automation/policies | jq

# Check pending/queued operations
curl localhost:2019/config/apps/pki | jq
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Rate limited by ACME CA | Wait or use different email/account |
| DNS challenge failing | Verify DNS provider credentials and record propagation |
| Certificate not renewed | Check `renewal_window` settings and storage permissions |
| Local CA not trusted | Run `caddy trust` with appropriate privileges |
| OCSP stapling failing | Ensure Caddy can reach OCSP responder on port 80 |

---

## Best Practices

1. **Use separate ACME accounts** for production vs staging environments
2. **Configure DNS challenges** for wildcard certificates
3. **Set up email notifications** for certificate expiry warnings
4. **Use internal CA** for all internal/private services
5. **Enable OCSP stapling** (default) to improve TLS handshake performance
6. **Regularly rotate** ACME account keys and CA roots
7. **Monitor certificate inventory** via the admin API
8. **Test renewal** before production deployment
