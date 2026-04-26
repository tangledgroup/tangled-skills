# SSL/TLS and HTTP/3

## Enabling SSL

Add `ssl` parameter to the `listen` directive:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate     /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/cert.key;

    location / {
        proxy_pass http://backend;
    }
}
```

## Protocol Configuration

Restrict to modern TLS versions:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

## Cipher Configuration

Specify allowed ciphers:

```nginx
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

## Certificate Configuration

Multiple certificates for multi-protocol (RSA + ECDSA):

```nginx
ssl_certificate     example.com.rsa.crt;
ssl_certificate_key example.com.rsa.key;
ssl_certificate     example.com.ecdsa.crt;
ssl_certificate_key example.com.ecdsa.key;
```

Variable-based certificate selection (SNI):

```nginx
ssl_certificate     $ssl_server_name.crt;
ssl_certificate_key $ssl_server_name.key;
```

## Session Configuration

Optimize TLS session reuse:

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;
```

## OCSP Stapling

Improve TLS handshake performance with OCSP stapling:

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/ssl/chain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

## Diffie-Hellman Parameters

Generate custom DH parameters for DHE cipher suites:

```nginx
ssl_dhparam /etc/nginx/ssl/dhparam.pem;
```

## Certificate Compression

Supported with OpenSSL 3.2+ or BoringSSL:

```nginx
ssl_certificate_compression on;
```

## HTTP/2

Enable HTTP/2 alongside SSL:

```nginx
listen 443 ssl http2;
```

HTTP/2 requires TLS and is enabled per `listen` directive.

## QUIC and HTTP/3

Support for QUIC/HTTP/3 is available since version 1.25.0. Requires OpenSSL 3.5.1+ (or BoringSSL, LibreSSL, QuicTLS).

Build from source with:

```bash
./configure --with-http_v3_module --with-cc-opt="-I../boringssl/include" --with-ld-opt="-L../boringssl/build -lstdc++"
```

Configure a server with QUIC:

```nginx
server {
    listen 443 ssl quic;
    http3 on;

    ssl_certificate     /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/cert.key;

    location / {
        proxy_pass http://backend;
    }
}
```

Key HTTP/3 directives:
- `http3 on` — enable HTTP/3
- `http3_max_concurrent_streams N` — max concurrent streams (default: 128)
- `http3_stream_buffer_size size` — buffer per stream (default: 64k)
- `quic_host_key` — EC private key for QUIC
- `quic_retry on` — enable QUIC retry packets

The `listen` directive gains the `quic` parameter to accept QUIC connections on UDP.

## Redirect HTTP to HTTPS

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

## HSTS

Send Strict-Transport-Security header:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```
