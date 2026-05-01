# SSL/TLS and Certificates

## TLS Backends

curl supports multiple TLS libraries, selected at build time:

- **OpenSSL** (1.1.x, 3.x) — most common
- **GnuTLS**
- **wolfSSL**
- **mbedTLS**
- **rustls-ffi**
- **Schannel** (Windows native)
- **Secure Transport** (Apple native)

Check which backends are available:

```bash
curl -V | grep SSL
curl-config --feature  # lists compiled features including SSL
```

At runtime, query with libcurl:

```c
const curl_version_info_data *data = curl_version_info(CURLVERSION_NOW);
printf("TLS: %s\n", data->ssl_version);
```

## Certificate Verification

curl verifies server certificates by default. It checks the signature chain against a trusted CA store and validates that the certificate matches the hostname in the URL.

**CA Store selection:**
- Windows with Schannel → native Windows CA store (default)
- macOS with certain backends → Apple SecTrust services
- All other platforms → file-based CA bundle

**Locate the default CA bundle:**

```bash
curl -v https://example.com/ 2>&1 | grep "CAfile"
```

**Use a custom CA bundle:**

```bash
curl --cacert /path/to/ca-bundle.crt https://example.com/
```

Environment variables also work: `CURL_CA_BUNDLE`, `SSL_CERT_FILE`, `SSL_CERT_DIR`.

On Windows, curl searches for `curl-ca-bundle.crt` in: application directory → current working directory → Windows System directory → Windows Directory → PATH directories.

**Use native CA store:**

```bash
curl --ca-native https://example.com/
```

**Skip verification (not recommended for production):**

```bash
curl -k https://self-signed.example.com/
# or
curl --insecure https://self-signed.example.com/
```

## Client Certificates

Mutual TLS authentication uses client certificates:

```bash
# PEM certificate with password
curl -E /path/to/cert.pem:password https://mTLS.example.com/

# Certificate and key as separate files
curl --cert client.crt --key client.key https://mTLS.example.com/
```

In libcurl:

```c
curl_easy_setopt(handle, CURLOPT_SSLCERTTYPE, "PEM");
curl_easy_setopt(handle, CURLOPT_SSLCERT, "/path/to/cert.pem");
curl_easy_setopt(handle, CURLOPT_SSLKEY, "/path/to/key.pem");
curl_easy_setopt(handle, CURLOPT_KEYPASSWD, "password");
```

## TLS Version Control

Force a specific TLS version:

```bash
curl --tlsv1.2 https://example.com/
curl --tlsv1.3 https://example.com/
```

Set minimum TLS version:

```bash
curl --tls-max 1.3 https://example.com/
```

## Extract CA Certificate from a Server

```bash
curl -w %{certs} https://example.com > cacert.pem
```

The output contains the certificate with `BEGIN CERTIFICATE` / `END CERTIFICATE` markers.

## HSTS (HTTP Strict Transport Security)

Since 7.77.0, curl supports RFC 6797 HSTS. When a server sends an HSTS header, subsequent HTTP-only requests to that host are automatically upgraded to HTTPS.

```bash
# Enable HSTS with file cache
curl --hsts hsts.cache https://example.com/

# In-memory only (no file)
curl --hsts "" https://example.com/
```

libcurl options:
- `CURLOPT_HSTS_CTRL` — enable/disable HSTS for a handle
- `CURLOPT_HSTS` — filename for persistent HSTS cache

Cache file format (text, one entry per line):

```
# comment lines ignored
.example.com "20251231 23:59:59"
```

Hostname is dot-prefixed if subdomains are included. Timestamp is expiration time in GMT.

**New in 8.20.0**: HSTS list is now capped to prevent unbounded growth. Expired entries read from file are skipped during loading. Duplicate host handling improved — when a duplicate host adds subdomains, that entry is used.

## Alt-Svc (Alternative Services)

RFC 7838 support allows servers to advertise alternative protocols/hosts via the `Alt-Svc` header. curl maintains a cache of these mappings.

```bash
# Save and reuse alt-svc cache
curl --alt-svc altsvc.cache https://example.com/
```

Cache file format (nine space-separated fields per line):

```
h2 quic.tech 8443 h3-22 quic.tech 8443 "20190808 06:18:37" 0 0
```

Fields: source ALPN, source host, source port, dest ALPN, dest host, dest port, expiration timestamp, persist flag, priority.

Enabled by default since curl 7.73.0. Build with `--enable-alt-svc` if needed.

**New in 8.20.0**: Alt-Svc list is now capped at 5,000 entries to prevent unbounded memory growth. The priority field was removed from the internal struct. Expired entries read from file are skipped during loading.

## HTTP/3 (QUIC)

curl supports HTTP/3 via QUIC using ngtcp2 (stable) or quiche (experimental).

```bash
# Use only HTTP/3
curl --http3-only https://example.org:4433/

# HTTP/3 with fallback to HTTP/2
curl --http3 https://example.org:4433/
```

**HTTPS eyeballing**: With `--http3`, curl attempts HTTP/2 via TLS+TCP in parallel if HTTP/3 does not respond quickly. Default hard timeout is 200ms, soft timeout (no data seen) is 100ms. Override with `--happy-eyeballs-timeout-ms`.

Build requirements for ngtcp2: OpenSSL 3.5.0+ (or quictls), nghttp3, and ngtcp2 libraries.

**New in 8.20.0**: HTTPS eyeballing now uses async DNS resolution for HTTP/3. Happy Eyeballs has resolution time delay added for better concurrent connection attempt handling. `curl_ngtcp2` callbacks extended and updated for ngtcp2 1.22.0+.

## ECH (Encrypted Client Hello)

EXPERIMENTAL — do not use in production. ECH encrypts the TLS ClientHello to hide the server name from network observers.

```bash
# With DNS-over-HTTPS for HTTPS RR retrieval
curl --ech true --doh-url https://one.one.one.one/dns-query https://example.com/
```

Requires OpenSSL with ECH support, wolfSSL, BoringSSL, AWS-LC, or rustls-ffi as the TLS backend. Build curl with `--enable-ech`.

## TLS-Specific Environment Variables

```bash
# Custom CA bundle file
export CURL_CA_BUNDLE=/path/to/ca-bundle.crt

# SSL context options (libcurl only)
# CURLOPT_SSL_OPTIONS bitmask controls behaviors like:
# CURLSSLOPT_ALLOW_BEAST — workaround for BEAST attack
# CURLSSLOPT_NO_REVOKE — skip certificate revocation checks (Schannel)
# CURLSSLOPT_NATIVE_CA — use native CA store
```

## Security Fixes in 8.20.0

Several TLS-related security vulnerabilities were fixed:

- **CVE-2026-7009**: OCSP stapling bypass with Apple SecTrust — connections could be reused ignoring TLS requirements
- **CVE-2026-4873**: Connection reuse ignores TLS requirement — a connection established with one TLS setting could be reused for another request requiring different TLS
- **BoringSSL coexist fixes**: Improved coexistence of BoringSSL with Schannel/WinCrypt on Windows
- **wolfSSL improvements**: wolfCrypt DES API used for NTLM, SHA-512/256 delegation to wolfSSL API
