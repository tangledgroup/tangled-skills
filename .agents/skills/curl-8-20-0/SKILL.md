---
name: curl-8-20-0
description: CLI tool and C library for multi-protocol data transfers supporting HTTP/HTTPS, FTP, SFTP, and 30+ protocols. Covers command-line usage, authentication, proxies, SSL/TLS, and WebSocket support. Use when making HTTP requests from the terminal, writing scripts that download/upload data, building C applications with libcurl, or working with curl's supported protocols.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - HTTP client
  - FTP
  - URL transfer
  - libcurl
  - CLI tool
  - HTTPS
  - SSL/TLS
  - WebSocket
  - multi-protocol
category: networking
external_references:
  - https://github.com/curl/curl/tree/curl-8_20_0/docs
  - https://curl.se/
  - https://curl.se/libcurl/
  - https://curl.se/ch/8.20.0.html
  - https://github.com/curl/curl
---

# curl 8.20.0

## Overview

curl is a command-line tool and library (libcurl) for transferring data with URLs. It supports over 30 protocols including HTTP, HTTPS, FTP, FTPS, SFTP, SCP, IMAP, SMTP, POP3, LDAP, MQTT, RTMP, SMB, TELNET, TFTP, DICT, GOPHER, and FILE. libcurl provides a C API with easy, multi, share, URL, MIME, header, and WebSocket interfaces used by applications across 101 operating systems and 28 CPU architectures.

curl handles persistent connections, SOCKS proxies, HTTP/2 multiplexing, HTTP/3 (QUIC), TLS with multiple backends (OpenSSL, GnuTLS, wolfSSL, mbedTLS, rustls, Schannel, Secure Transport), authentication methods (Basic, Digest, NTLM, Negotiate/SPNEGO, Kerberos), cookie jars, content encoding (gzip, deflate, brotli, zstd), and much more.

## When to Use

- Making HTTP(S) GET/POST/PUT/DELETE requests from the command line
- Downloading or uploading files via HTTP, FTP, SFTP, SCP, SMB
- Scripting data transfers with URL globbing, parallel downloads, and config files
- Building C applications that need network transfer capabilities via libcurl
- Working with mail protocols (IMAP, SMTP, POP3) from the command line or C code
- Implementing WebSocket communication in C applications
- Performing multi-protocol transfers with authentication, proxies, and TLS
- Parsing and manipulating URLs programmatically with the libcurl URL API

## Core Concepts

**URL syntax**: curl follows "RFC 3986 plus" — grounded in RFC 3986 with pragmatic deviations for real-world URLs. Supports scheme-less URLs (guesses protocol from hostname prefix), allows one to three slashes after the colon, percent-encodes non-ASCII bytes, and handles spaces in `Location:` headers by re-encoding to `%20`.

**Globbing**: The CLI supports URL ranges `[N-M]` and lists `{one,two,three}` for batch transfers. Use `-g`/`--globoff` to disable globbing (needed for IPv6 bracket addresses in URLs).

**Persistent connections**: When multiple URLs share the same host on one command line, curl reuses the TCP connection. This applies across protocols and is automatic — no special option needed.

**Protocol guessing**: Without an explicit scheme, curl guesses from hostname prefix: `ftp.` → FTP, `dict.` → DICT, `ldap.` → LDAP, `imap.` → IMAP, `smtp.` → SMTP, `pop3.` → POP3, everything else → HTTP.

## New in 8.20.0

**Thread pool resolver**: curl now uses a thread pool and queue for DNS resolving, replacing the older threaded-resolver implementation. This provides better resource management and eliminates orphaned variable references.

**NTLM disabled by default**: NTLM authentication is no longer enabled by default at build time. Use `--enable-ntlm` to include it.

**SMB disabled by default**: SMB protocol support is opt-in only. Use `--enable-smb` to compile with SMB support.

**CURLMNWC_CLEAR_ALL**: New multi interface constant for clearing all network change types (connections, DNS cache, etc.) via `curl_multi_setopt()`.

**Dropped RTMP support**: The RTMP protocol is no longer supported.

**Build requirement changes**: Minimum c-ares 1.16.0, minimum CMake 3.18+.

**Security fixes**: 8 security vulnerabilities addressed including cross-proxy Digest auth state leak (CVE-2026-7168), OCSP stapling bypass with Apple SecTrust (CVE-2026-7009), netrc credential leak with reused proxy connection (CVE-2026-6429), stale custom cookie host causing cookie leak (CVE-2026-6276), proxy credentials leak over redirect-to-proxy (CVE-2026-6253), SMB connection reuse issues (CVE-2026-5773), HTTP Negotiate connection reuse (CVE-2026-5545), and connection reuse ignoring TLS requirement (CVE-2026-4873).

**HSTS and Alt-Svc improvements**: HSTS list capped, expired entries skipped when reading from file, duplicate host handling improved. Alt-Svc list capped at 5,000 entries, priority field removed from struct, expired entries skipped.

**Happy Eyeballs resolution time delay**: Added for better concurrent connection attempts.

## Installation / Setup

curl is typically pre-installed on Linux and macOS. On Unix, build from source:

```bash
./configure --with-openssl [--with-gnutls --with-wolfssl]
make
make test   # optional
sudo make install
```

For custom install paths:

```bash
./configure --prefix=$HOME/curl-install --with-openssl
make && make install
```

Use `curl-config` to query build features and linker flags:

```bash
curl-config --cflags    # compiler include flags
curl-config --libs      # linker flags
curl-config --feature   # enabled features (SSL, HTTP2, etc.)
curl-config --protocols # supported protocols
```

## Usage Examples

**Basic downloads:**

```bash
# GET a webpage to stdout
curl https://www.example.com/

# Save with custom filename
curl -o page.html https://www.example.com/

# Save with remote filename
curl -O https://www.example.com/file.txt

# Multiple files with remote names
curl -O https://example.com/a.txt -O https://example.com/b.txt
```

**POST data:**

```bash
# URL-encoded form POST
curl -d "name=Rafael&phone=3320780" https://www.example.com/guest.cgi

# Auto URL-encode POST data
curl --data-urlencode "name=Rafael Sagula&phone=3320780" https://www.example.com/guest.cgi

# Multipart form with file upload
curl -F "file=@cooltext.txt" -F "yourname=Daniel" https://www.example.com/postit.cgi

# Form string (safe for untrusted input, no @ interpretation)
curl --form-string "comment=Hello @world" https://www.example.com/post
```

**Authentication:**

```bash
# HTTP Basic auth
curl -u user:passwd https://example.com/

# Auto-negotiate most secure auth method the server supports
curl --anyauth -u user:passwd https://example.com/

# SFTP with SSH key
curl -u username --key ~/.ssh/id_rsa sftp://example.com/etc/issue

# SCP with password-protected key
curl -u username: --key ~/.ssh/id_rsa --pass key_password scp://example.com/~/file.txt
```

**Upload:**

```bash
# FTP upload
curl -T uploadfile -u user:passwd ftp://ftp.example.com/myfile

# HTTP PUT
curl -T file https://www.example.com/myfile

# Append to remote file (FTP)
curl -T localfile -a ftp://ftp.example.com/remotefile
```

**Headers and verbose output:**

```bash
# Include response headers in output
curl -i https://example.com/

# Save headers to file
curl --dump-header headers.txt https://example.com/

# HEAD request (headers only)
curl -I https://example.com/

# Add custom header
curl -H "X-Custom-Header: value" https://example.com/

# Suppress internal header (e.g., Host:)
curl -H "Host:" https://example.com/

# Verbose protocol trace
curl -v https://example.com/

# Full hex+ASCII trace to file
curl --trace-ascii trace.txt https://example.com/
```

**Redirects and cookies:**

```bash
# Follow redirects (default: up to 50)
curl -L https://example.com/redirect

# Save and reuse cookies
curl -c cookies.txt https://example.com/          # save cookies
curl -b cookies.txt https://example.com/other     # load cookies
curl -b cookies.txt -c cookies.txt https://example.com/  # read+write same file
```

**Speed limits and timeouts:**

```bash
# Abort if speed drops below 3000 bytes/sec for 60 seconds
curl -Y 3000 -y 60 https://far-away.example.com

# Throttle to 10KB/s max
curl --limit-rate 10K https://example.com/largefile

# Total time limit: 30 minutes
curl -m 1800 https://example.com/
```

**Range requests:**

```bash
# First 100 bytes (HTTP byte range)
curl -r 0-99 https://www.example.com/

# Last 500 bytes
curl -r -500 https://www.example.com/
```

**Proxy:**

```bash
# HTTP proxy
curl -x proxy.example.com:8888 https://example.com/

# Proxy with authentication
curl -U proxyuser:proxypass -x proxy:8888 https://example.com/

# SOCKS5 proxy
curl --socks5 proxy.example.com:1080 https://example.com/

# No proxy for specific hosts
curl --noproxy example.com,localhost -x proxy:8888 https://example.com/
```

**Custom output with write-out:**

```bash
# Print download size and HTTP status code
curl -s -o /dev/null -w "Size: %{size_download} bytes, HTTP: %{http_code}\n" https://example.com/
```

## Advanced Topics

**URL Syntax and Schemes**: URL parsing rules, scheme support, globbing, security considerations → [URL Syntax](reference/01-url-syntax.md)

**libcurl Easy Interface**: Single-transfer C API, handle lifecycle, callbacks, options, error handling → [Easy Interface](reference/02-libcurl-easy.md)

**libcurl Multi Interface**: Concurrent transfers in a single thread, socket-based event loop, poll API, CURLMNWC_CLEAR_ALL → [Multi Interface](reference/03-libcurl-multi.md)

**SSL/TLS and Certificates**: TLS backends, certificate verification, client certs, HSTS, ECH, Alt-Svc → [SSL/TLS](reference/04-ssl-tls.md)

**Protocols Reference**: Protocol-specific behaviors for HTTP, FTP, SFTP, IMAP, SMTP, POP3, MQTT, WebSocket → [Protocols](reference/05-protocols.md)

**Security and Configuration**: Security best practices, .netrc, config files, environment variables, write-out format → [Security and Config](reference/06-security-config.md)
