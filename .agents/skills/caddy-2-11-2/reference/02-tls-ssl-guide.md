# TLS/SSL Configuration Guide

Complete guide to TLS/SSL configuration in Caddy 2.11.2.

## Automatic HTTPS

Caddy enables HTTPS by default for all sites with valid hostnames:

```caddyfile
# Auto-enables HTTPS via Let's Encrypt or ZeroSSL
example.com { ... }

# Disable automatic HTTPS redirect
example.com {
    auto_https off
}

# Strict mode (default) - redirects HTTP to HTTPS
auto_https strict

# Ignore invalid Host headers
auto_https ignore_invalid_hsts

# Don't bind to port 80
auto_https disable_redirects
```

### Automatic HTTPS Behavior

| Domain Type | Behavior |
|-------------|----------|
| Public domain (e.g., `example.com`) | Auto-HTTPS via ACME (Let's Encrypt/ZeroSSL) |
| Local/internal name (e.g., `localhost`, `192.168.x.x`) | Local CA or self-signed certificate |
| IP address | Self-signed certificate |
| No hostname (`:443` only) | No automatic HTTPS |

---

## TLS Certificate Sources

### ACME Issuers (Let's Encrypt / ZeroSSL)

```caddyfile
# Default: Let's Encrypt
example.com {
    tls admin@example.com
}

# ZeroSSL
example.com {
    tls {
        issuer acme zerossl
    }
}

# Custom ACME server
example.com {
    tls {
        ca https://my-acme-server/dir
    }
}

# With External Account Binding (EAB)
example.com {
    tls {
        eab key_id mac_key
    }
}

# DNS challenge for wildcard certs
*.example.com {
    tls {
        dns cloudflare {env.CLOUDFLARE_API_KEY}
    }
}
```

### File-based Certificates

```caddyfile
# Load from files
example.com {
    tls /path/to/cert.pem /path/to/key.pem
}

# Multiple certificate pairs (for SNI)
example.com {
    tls cert1.pem key1.pem cert2.pem key2.pem
}
```

### Folder Loader

```caddyfile
# Load all .pem/.key pairs from a directory
example.com {
    tls /etc/caddy/certs/
}
```

### Internal CA (Local PKI)

```caddyfile
# Use Caddy's built-in local CA
internal.example.com {
    tls internal
}

# For IP addresses
192.168.1.100 {
    tls internal
}
```

---

## ACME Settings

### Global ACME Options

```caddyfile
{
    # Email for ACME account (used for all sites)
    email admin@example.com
    
    # Or set per-site with tls directive
    
    # DNS providers for ACME challenges
    dns cloudflare {env.CLOUDFLARE_API_KEY}
    dns digitalocean {env.DIGITALOCEAN_TOKEN}
    
    # ACME CA endpoint (default: Let's Encrypt)
    acme_ca https://acme-v02.api.letsencrypt.org/directory
    
    # ZeroSSL CA
    # acme_ca https://acme.zerossl.com/v2/DV90
}
```

### Per-Site ACME Options

```caddyfile
example.com {
    tls admin@example.com {
        # ACME server
        ca https://acme.example.com/dir
        
        # CA root certificate (for private CA)
        ca_root /etc/ssl/ca-root.pem
        
        # Key type for certificates
        key_type ed25519  # or p256, p384, rsa2048, rsa4096
        
        # DNS challenge provider
        dns cloudflare {env.CLOUDFLARE_API_KEY}
        
        # DNS challenge propagation
        propagation_delay 30s
        propagation_timeout 2m
        
        # DNS servers for resolution
        resolvers 8.8.8.8 1.1.1.1
        
        # DNS TTL for records
        dns_ttl 5m
        
        # Override domain for DNS challenge
        dns_challenge_override_domain example.com
        
        # External Account Binding
        eab key_id mac_key
        
        # On-demand certificate issuance (arbitrary hostnames)
        on_demand
        
        # Reuse private keys across certificates
        reuse_private_keys
        
        # Force automate (skip DNS check for ACME)
        force_automate
        
        # Certificate renewal window ratio (0.0-1.0, default ~30 days)
        renewal_window_ratio 0.33
        
        # Custom issuer module
        issuer acme zerossl
        
        # Custom certificate getter
        get_certificate local
        
        # Insecure secrets logging (debugging)
        insecure_secrets_log /tmp/caddy-secrets.log
    }
}
```

---

## TLS Protocol Configuration

### Protocol Versions

```caddyfile
example.com {
    tls {
        # Minimum and maximum TLS versions
        protocols tls1.2 tls1.3
        
        # Only TLS 1.3
        protocols tls1.3
    }
}
```

**Supported protocol values:** `tls1.0`, `tls1.1`, `tls1.2`, `tls1.3`, `all`

### Cipher Suites

```caddyfile
example.com {
    tls {
        ciphers TLS_AES_256_GCM_SHA384
                  TLS_CHACHA20_POLY1305_SHA256
                  TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
                  TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    }
}
```

**Common cipher suite names:**
- `TLS_AES_128_GCM_SHA256`
- `TLS_AES_256_GCM_SHA384`
- `TLS_CHACHA20_POLY1305_SHA256`
- `ECDHE-RSA-WITH-AES-128-GCM-SHA256`
- `ECDHE-RSA-WITH-AES-256-GCM-SHA384`

### Elliptic Curves

```caddyfile
example.com {
    tls {
        curves x25519 secp384r1 secp521r1
    }
}
```

**Supported curves:** `x25519`, `secp256r1`, `secp384r1`, `secp521r1`

---

## Client Certificate Authentication (mTLS)

### Basic Client Auth

```caddyfile
secure.example.com {
    tls {
        client_auth {
            mode request          # Ask for cert (optional)
        }
    }
}
```

**Client auth modes:**

| Mode | Behavior |
|------|----------|
| `request` | Request client certificate (optional) |
| `require` | Require client certificate |
| `verify_if_given` | Verify if client provides cert |
| `require_and_verify` | Require and verify client certificate |

### Trusted Certificates

```caddyfile
secure.example.com {
    tls {
        client_auth {
            mode require_and_verify
            
            # Trust from a PEM file
            trusted_leaf_cert_file /etc/caddy/client-ca.pem
            
            # Or trust from inline base64 DER
            trusted_leaf_cert <base64_der>
            
            # Or use a trust pool module
            trust_pool verisign {
                url https://pki.goog/globalsign/
            }
        }
    }
}
```

### Client Auth with User Mapping

```caddyfile
secure.example.com {
    tls {
        client_auth {
            mode require_and_verify
            trusted_leaf_cert_file /etc/caddy/client-ca.pem
            
            # Map certificate fields to Caddy variables
            application_policies <oid...>
        }
    }
    
    basicauth {
        admin "{tls_client_issuer_dn_cn}" $2a$14$...
    }
}
```

**Available TLS client variables:**
- `{tls_client_dn}` - Distinguished Name
- `{tls_client_cn}` - Common Name
- `{tls_client_issuer_dn}` - Issuer DN
- `{tls_client_issuer_dn_cn}` - Issuer CN
- `{tls_client_serial}` - Serial number
- `{tls_client_pkix_sha256}` - Subject key hash

---

## ALPN Configuration

```caddyfile
example.com {
    tls {
        # Application-Layer Protocol Negotiation
        alpn h3 http/1.1 h2
    }
}

# HTTP/3 only (no HTTP/1 or HTTP/2)
h3.example.com {
    tls {
        alpn h3
    }
    protocols h3
}
```

**Supported ALPN values:** `h3`, `h3-04` (HTTP/3), `h2` (HTTP/2), `http/1.1` (HTTP/1.1)

---

## Certificate Selection

### Custom Certificate Selection Policy

```caddyfile
example.com {
    tls {
        certificate_selection {
            # Match any tag
            any_tag cert-tag
            
            # Preferred curves
            preferred_curves x25519 secp384r1
            
            # Preferred signatures
            preferred_signatures ECDSAwithSHA256 RSA-PSS-with-SHA256
        }
    }
}
```

---

## Encrypted ClientHello (ECH)

ECH provides privacy for the TLS Server Name Indication (SNI).

```caddyfile
# Configure ECH in the TLS app (JSON config required)
# In Caddyfile, use the tls directive with ECH options

private.example.com {
    tls {
        # ECH configuration requires JSON
        # See: https://caddyserver.com/docs/json/apps/tls/encrypedclienthello/
    }
}
```

**ECH is configured via JSON:**

```json
{
  "apps": {
    "tls": {
      "encrypted_client_hello": {
        "configuration": {
          "resolution_order": ["fallback"],
          "fallback": {
            "key_file": "/etc/caddy/ech-key.json",
            "config_file": "/etc/caddy/ech-config.json"
          }
        }
      }
    }
  }
}
```

---

## OCSP Stapling

OCSP stapling is enabled by default. Configure via JSON:

```json
{
  "apps": {
    "tls": {
      "automation": {
        "policies": [{
          "issuers": [{
            "module": "acme",
            "ca": "https://acme-v02.api.letsencrypt.org/directory"
          }]
        }]
      }
    }
  }
}
```

---

## TLS Connection Policies

For fine-grained control over TLS connections, use JSON configuration:

```json
{
  "apps": {
    "http": {
      "servers": {
        "example": {
          "listen": [":443"],
          "tls_connection_policies": [
            {
              "match": {
                "sni": ["secure.example.com"]
              },
              "cipher_suites": ["TLS_AES_256_GCM_SHA384"],
              "curves": ["x25519", "secp384r1"],
              "protocols": {
                "min": "tls1.2",
                "max": "tls1.3"
              },
              "client_auth": {
                "mode": "require_and_verify",
                "trusted_leaf_cert_file": "/etc/caddy/client-ca.pem"
              }
            }
          ]
        }
      }
    }
  }
}
```

---

## Certificate Storage

Caddy stores certificates in its configured storage module. Default locations:

| Platform | Default Path |
|----------|-------------|
| Linux | `~/.local/share/caddy/pki/` |
| macOS | `~/Library/Application Support/Caddy/pki/` |
| Windows | `%LOCALAPPDATA%\Caddy\pki\` |

### Custom Storage Location

```caddyfile
{
    storage filesystem {
        path /var/lib/caddy
    }
}
```

### JSON Configuration

```json
{
  "storage": {
    "module": "filesystem",
    "root": "/var/lib/caddy"
  }
}
```

---

## Trusted CA Installation

Install Caddy's local CA into system trust stores:

```bash
# Install local CA cert
sudo caddy trust

# Specify a particular CA
caddy trust --ca my-ca-id

# Remove from trust store
caddy untrust

# Specific certificate
caddy untrust --cert /path/to/cert.pem
```

---

## Security Best Practices

### Recommended TLS Configuration

```caddyfile
# Modern secure configuration
secure.example.com {
    tls admin@example.com {
        # Only TLS 1.2+
        protocols tls1.2 tls1.3
        
        # Strong cipher suites only
        ciphers TLS_AES_256_GCM_SHA384
                  TLS_CHACHA20_POLY1305_SHA256
                  TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
                  TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        
        # Modern curves only
        curves x25519 secp384r1
        
        # Strong key type
        key_type ed25519
        
        # HTTP/3 support
        alpn h3 http/1.1 h2
        
        # Client auth for sensitive endpoints
        client_auth {
            mode verify_if_given
        }
    }
}
```

### Security Headers (via Caddyfile)

```caddyfile
secure.example.com {
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Content-Security-Policy "default-src 'self'"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
    }
}
```
