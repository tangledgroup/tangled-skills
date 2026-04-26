# Automatic HTTPS

Caddy enables HTTPS automatically for all sites with a hostname or IP. Certificate management is fully automated in the background with multi-issuer fallback and exponential backoff retry.

## How It Works

When a site block has a hostname (e.g., `example.com`), Caddy:

1. Obtains a TLS certificate automatically
2. Serves the site over HTTPS
3. Redirects HTTP to HTTPS
4. Renews certificates before expiry
5. Falls back to alternative issuers on failure

This behavior is controlled by the `auto_https` global option and can be customized per-site with the `tls` directive.

## Public Certificates

For public domain names, Caddy uses ACME-compatible CAs:

- **Let's Encrypt** — Default production endpoint
- **ZeroSSL** — Default production endpoint

Caddy tries Let's Encrypt first, then ZeroSSL. If both fail, it backs off exponentially (max 1 day between attempts, up to 30 days). During retries with Let's Encrypt, Caddy switches to their staging environment to avoid rate limits.

### Hostname Requirements

Qualify for publicly-trusted certificates if:

- Non-empty
- Alphanumerics, hyphens, dots, and wildcard (`*`) only
- Do not start or end with a dot (RFC 1034)
- Not localhost (`.localhost`, `.local`, `.internal`, `.home.arpa` TLDs excluded)
- Not an IP address
- Single wildcard `*` as left-most label only

## ACME Challenges

### HTTP Challenge (default, enabled)

Requires port 80 externally accessible. Caddy serves a temporary cryptographic resource that the CA validates via DNS A/AAAA lookup.

```caddy
# No explicit config needed — enabled by default
```

### TLS-ALPN Challenge (default, enabled)

Requires port 443 externally accessible. Uses TLS handshake with special ServerName and ALPN values for validation.

When both challenges are enabled, Caddy randomly chooses one to avoid accidental dependence, then learns which is most successful over time.

### DNS Challenge

Does not require open ports. Requires a caddy-dns plugin for your DNS provider:

```caddy
{
    acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Or per-site:

```caddy
example.com {
    tls {
        dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    }
}
```

DNS challenge is required for wildcard certificates. When enabled, other challenges are disabled by default.

CNAME delegation is supported — delegate `_acme-challenge` subdomain to another zone:

```caddy
tls {
    dns_challenge_override_domain _acme-challenge.example.com
}
```

## Local HTTPS

For non-public hosts (`localhost`, `127.0.0.1`, internal IPs), Caddy uses its built-in local CA:

- Root key generated with cryptographically-secure PRNG
- Intermediate certificate signs leaf certificates
- Root auto-installed into system trust store on first use
- Stored in data directory at `pki/authorities/local`

To force internal certificates:

```caddy
{
    local_certs
}

# Or per-site:
example.internal {
    tls internal
}
```

Install the root CA certificate when running as unprivileged user:

```bash
sudo caddy trust
```

Root certificate location: `$HOME/.local/share/caddy/pki/authorities/local/root.crt`

## Wildcard Certificates

Caddy manages wildcard certificates for qualifying names (`*.example.com`):

```caddy
*.example.com {
    root * /var/www
    file_server
}
```

Wildcard requires DNS challenge (Let's Encrypt requirement). As of Caddy 2.10, when a wildcard certificate is automated, Caddy uses it for individual subdomains in the configuration without obtaining separate certificates.

## Encrypted ClientHello (ECH)

ECH protects the SNI field in TLS handshakes from eavesdropping:

```caddy
{
    dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    ech example.com
}
```

Caddy automatically generates, publishes, and serves ECH configurations via HTTPS DNS records. The `public_name` (outer SNI) must point to your server — Caddy obtains a certificate for it.

Key considerations:
- Requires caddy-dns module for DNS record publication
- Clients need DoH/DoT enabled for secure DNS lookups
- Use wildcard certificates to avoid leaking subdomains to CT logs
- Choose a single public name for all sites to maximize anonymity set
- Caddy handles key rotation automatically

## On-Demand TLS

Dynamically obtain certificates during the first TLS handshake:

```caddy
{
    on_demand_tls {
        ask http://localhost:8080/ask
        rate_limit 10 1m
    }
}

https:// {
    # No specific domain names needed
    reverse_proxy localhost:8080
}
```

Useful when:
- Domain names unknown at config time
- DNS records not yet configured
- Customer domains you don't control

The `ask` endpoint must return HTTP 200 to permit certificate issuance. Rate limiting prevents abuse.

## Issuer Fallback

Caddy supports fully-redundant automatic failover between CAs:

1. Try Let's Encrypt production
2. Try ZeroSSL production
3. Exponential backoff (max 1 day, up to 30 days)
4. During LE retries, use staging endpoint to avoid rate limits

Custom issuers can be configured:

```caddy
{
    acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

## Testing

Always use staging endpoints during development to avoid rate limits:

```caddy
{
    acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

Let's Encrypt rate limits can block access for up to a week.

## Storage

Certificates, keys, and ACME assets stored in the configured storage module. Default: file system at:

- Linux/BSD: `$HOME/.local/share/caddy`
- Windows: `%AppData%\Caddy`
- macOS: `$HOME/Library/Application Support/Caddy`

Multiple Caddy instances sharing storage automatically coordinate certificate management as a cluster.

## Error Handling

Certificate management runs in the background and does not block startup:

1. Retry once after brief pause
2. Switch to next challenge type
3. Try next issuer (LE → ZeroSSL)
4. Exponential backoff (max 1 day, up to 30 days)

Internal rate limit: 10 attempts per ACME account per 10 seconds.
