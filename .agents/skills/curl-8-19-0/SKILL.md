---
name: curl-8-19-0
description: Complete toolkit for curl 8.19.0 CLI tool and libcurl C library covering command-line usage, URL syntax, HTTP/HTTPS/FTP/SFTP/multi-protocol transfers, authentication, proxies, SSL/TLS, cookie handling, WebSocket support, MIME API, multi-interface programming, and comprehensive option reference. Use when making HTTP requests from the terminal, writing scripts that download/upload data, building C applications with libcurl, or working with any of curl's 30+ supported protocols including IMAP, SMTP, POP3, LDAP, MQTT, RTMP, and SFTP.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "8.19.0"
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
  - https://github.com/curl/curl/tree/curl-8_19_0/docs
---

# curl 8.19.0

## Overview

curl is a command-line tool and libcurl C library for transferring data from or to servers using URLs. It supports over 30 protocols including HTTP, HTTPS, FTP, SFTP, SMTP, IMAP, POP3, LDAP, MQTT, RTMP, WebSocket, and more. curl is powered by libcurl for all transfer-related features and is one of the most widely used network tools in existence.

## When to Use

- Making HTTP/HTTPS requests from the terminal or scripts
- Downloading/uploading files via FTP/SFTP/SMB
- Sending POST data or multipart form submissions
- Working with APIs (REST, GraphQL, etc.)
- Building C applications that need network transfer capabilities via libcurl
- Automating file transfers in CI/CD pipelines
- Testing web services and endpoints
- Handling authentication (Basic, Digest, NTLM, Kerberos)
- Configuring proxies (HTTP, SOCKS4/5)

## Core Concepts

### Protocol Support

curl supports these protocols (URL schemes):

| Protocol | Description |
|----------|-------------|
| DICT | Dictionary lookups |
| FILE | Local file access |
| FTP / FTPS | File transfer with/without TLS |
| GOPHER / GOPHERS | Gopher protocol |
| HTTP / HTTPS | Web protocols (0.9, 1.0, 1.1, 2, 3) |
| IMAP / IMAPS | Email reading |
| LDAP / LDAPS | Directory lookups |
| MQTT / MQTTS | Message queuing (subscribe/publish) |
| POP3 / POP3S | Email retrieval |
| RTMP(S) | Streaming media |
| RTSP | Real Time Streaming Protocol |
| SCP / SFTP | SSH file transfer |
| SMB(S) | Windows file sharing |
| SMTP / SMTPS | Email sending |
| TELNET | Interactive terminal sessions |
| TFTP | Trivial FTP |
| WS / WSS | WebSocket |

### URL Syntax

URLs follow the pattern: `protocol://[user:password@]host[:port]/path?query#fragment`

Special characters in URLs (like `{`, `}`, `[`, `]`) are interpreted as globbing patterns. Use `--globoff` or `-g` to disable globbing, or quote the URL.

IPv6 addresses must be enclosed in brackets: `http://[2001:1890:1112:1::20]/`

### Globbing Patterns

curl supports URL globbing for specifying multiple URLs:

```bash
# Brace expansion
curl https://example.com/{one,two,three}.jpg

# Range with brackets
curl ftp://ftp.example.com/file[1-100].txt
curl ftp://ftp.example.com/file[001-100].txt   # Leading zeros
curl ftp://ftp.example.com/file[a-z].txt        # Letters
curl https://example.com/file[1-100:10].txt     # Step counter (every 10th)

# Nested patterns
curl https://example.com/archive[1996-1999]/vol[1-4]/part{a,b,c}.html
```

### Authentication Methods

| Method | Options | Description |
|--------|---------|-------------|
| Basic | `-u user:pass` or `--user` | Base64-encoded credentials (insecure) |
| Digest | `--digest` | Challenge-response authentication |
| NTLM | `--ntlm` | Windows NT LAN Manager auth |
| Negotiate | `--negotiate` | SPNEGO/Kerberos |
| Kerberos | `--krb` | Kerberos 4/5 for FTP |

### Proxy Support

curl supports HTTP and SOCKS proxies:

```bash
# Set proxy
curl -x http://proxy.example.com:8080 https://example.com
curl --proxy user:pass@proxy:8080 https://example.com

# Environment variables (if not using -x)
export http_proxy=http://proxy:8080
export https_proxy=https://proxy:8080
export all_proxy=socks5://proxy:1080
export no_proxy=".internal.example.com,localhost"

# Proxy tunneling for SSL
curl --proxy-tunnel -x http://proxy:8080 https://example.com
```

### SSL/TLS Options

```bash
# Specify CA certificate bundle
curl --cacert /path/to/ca-bundle.crt https://example.com

# Specify client certificate and key
curl --cert client.pem --key key.pem https://example.com

# Require SSL
curl --ssl-reqd ftp://secure.server.com/file.txt

# Force TLS version
curl --tlsv1.2 https://example.com
curl --tlsv1.3 https://example.com

# Disable certificate verification (insecure!)
curl -k https://self-signed.example.com

# Pin public key
curl --pinnedpubkey sha256/AABBCC... https://example.com

# TLS 1.3 specific ciphers
curl --tls13-ciphers TLS_AES_256_GCM_SHA384 https://example.com
```

### HTTP Options

```bash
# Custom request method
curl -X PATCH https://api.example.com/resource

# Set headers
curl -H "Authorization: Bearer token" -H "Content-Type: application/json" https://api.example.com

# HTTP version control
curl --http1.1 https://example.com     # Force HTTP/1.1
curl --http2 https://example.com       # Require HTTP/2 (HTTPS only)
curl --http2-prior-knowledge https://example.com  # HTTP/2 without ALPN
curl --http3 https://example.com       # HTTP/3 (QUIC)

# Follow redirects
curl -L https://example.com/redirect

# Custom user agent
curl -A "MyApp/1.0" https://example.com

# Chunked transfer encoding
curl -H "Transfer-Encoding: chunked" ...
```

### Data Transfer Options

```bash
# POST data
curl -d "name=value&key=data" https://api.example.com
curl -d @data.json https://api.example.com    # Read from file

# Binary POST (no special interpretation)
curl --data-binary @file.bin https://example.com

# Raw POST (no @ interpretation)
curl --data-raw "@not-a-filename" https://example.com

# URL-encoded POST
curl --data-urlencode "name=value with spaces" https://api.example.com

# Multipart form upload
curl -F "field=value" -F "file=@local.txt" https://api.example.com
curl -F "file=<text-from-file.txt" https://api.example.com  # Read as text field
curl -F "file@remote.txt;type=text/plain;filename=renamed.txt" https://api.example.com

# Upload to FTP
curl -T localfile.txt ftp://ftp.example.com/remote.txt
curl -T "{file1,file2}" ftp://ftp.example.com/

# Download options
curl -o output.html https://example.com    # Save with specific name
curl -O https://example.com/file.txt       # Use remote filename
curl -J -O https://example.com             # Use Content-Disposition filename
```

### Output and Progress

```bash
# Verbose output (debugging)
curl -v https://example.com          # Show headers with > < markers
curl -vv https://example.com         # More detail (transfer IDs, timing)
curl -vvv https://example.com        # Full content trace
curl --trace-ascii dump.txt URL      # Binary trace to file

# Silent mode
curl -s https://example.com          # No progress meter
curl -sS https://example.com         # Silent + show errors on failure

# Write-out format (for scripting)
curl -w "HTTP Status: %{http_code}\nTime: %{time_total}s\nSize: %{size_download}\n" \
     -o /dev/null -s https://example.com

# Progress bar
curl -# https://example.com/largefile.zip    # Progress bar instead of meter
```

### Timeouts and Limits

```bash
curl --connect-timeout 10 https://example.com   # Connection timeout (seconds)
curl --max-time 30 https://example.com           # Maximum total time
curl --max-filesize 10000000 https://example.com # Max file size in bytes
curl --retry 3 --retry-delay 5 https://example.com  # Retry on failure
curl --limit-rate 100k https://example.com       # Rate limit
```

### Cookie Handling

```bash
# Load cookies from file
curl -b cookies.txt https://example.com

# Save cookies to jar
curl -c cookies.txt https://example.com

# Both (load and save)
curl -b cookies.txt -c cookies.txt https://example.com

# From browser cookie files (Netscape/Mozilla format auto-detected)
curl -b /path/to/browser/cookies.sqlite ...
```

### FTP Options

```bash
# FTPS with SSL required
curl --ssl-reqd ftp://secure.server.com/file.txt

# Custom FTP commands before transfer
curl --quote "DELE oldfile.txt" ftp://ftp.example.com/newfile.txt

# Passive mode
curl -P 0 ftp://ftp.example.com/file.txt    # Continue from byte 0
curl --ftp-pasv ftp://ftp.example.com/      # Use PASV (not EPSV)

# FTP method selection
curl --ftp-method=multirec ftp://ftp.example.com/dir/  # Try all directory listing methods
```

### Range and Resumption

```bash
# Download partial file
curl -r 0-1023 https://example.com/file.txt   # First 1024 bytes
curl -r 1024-2047 https://example.com/file.txt # Second 1024 bytes

# Resume interrupted download
curl -C - -o file.zip https://example.com/largefile.zip
```

### Parallel Transfers

```bash
# Transfer multiple URLs in parallel
curl --parallel --parallel-max 8 \
     https://example.com/a.txt \
     https://example.com/b.txt \
     https://example.com/c.txt
```

## Installation / Setup

### Install curl

```bash
# Debian/Ubuntu
sudo apt install curl

# RHEL/CentOS
sudo yum install curl

# macOS
brew install curl

# Windows (via winget)
winget install curl
```

### Verify Installation

```bash
curl --version
# Output: curl 8.19.0 (platform) libcurl/8.19.0 OpenSSL/3.x ...
```

## Usage Examples

### Basic HTTP Requests

```bash
# Simple GET
curl https://api.example.com/data

# POST with JSON
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"test","value":42}' \
     https://api.example.com/endpoint

# PUT request
curl -X PUT -H "Content-Type: application/json" \
     -d '{"id":1,"status":"active"}' \
     https://api.example.com/resource/1

# DELETE request
curl -X DELETE https://api.example.com/resource/1
```

### API Authentication

```bash
# Bearer token
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/protected

# Basic authentication
curl -u username:password https://api.example.com/api

# API key in header
curl -H "X-API-Key: your-key-here" https://api.example.com/data
```

### File Operations

```bash
# Download with progress
curl -O https://example.com/largefile.zip

# Download multiple files
curl -O https://example.com/file1.txt -O https://example.com/file2.txt

# FTP download
curl -u user:pass ftp://ftp.example.com/README.txt

# SFTP download
curl -u username --key ~/.ssh/id_rsa sftp://server.com/path/to/file

# Upload to S3 (presigned URL)
curl -X PUT -T localfile.bin "https://s3.amazonaws.com/bucket/object?AWSAccessKeyId=..."
```

### Web Scraping

```bash
# Get page title
curl -s https://example.com | grep '<title>'

# Download all images from a page
curl -sL https://example.com | grep -oP 'src="\K[^"]*\.(jpg|png|gif)' | \
  while read img; do curl -O "$img"; done

# Follow redirects and save
curl -L -o output.html https://short.url/redirect
```

### Health Checks

```bash
# Simple health check (exit code based)
curl -sf https://api.example.com/health || echo "Service down"

# Check with timeout
curl --connect-timeout 5 --max-time 10 -s -o /dev/null -w "%{http_code}" \
     https://api.example.com/health

# JSON response pretty-printed (requires jq)
curl -s https://api.example.com/data | jq .
```

### Testing Endpoints

```bash
# Test with verbose output
curl -v https://localhost:8443/api/test 2>&1 | grep -E '(< |>|\{)'

# Check response headers only
curl -I https://example.com

# Test WebSocket
curl -i -N \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8080/ws
```

## Advanced Topics

For detailed documentation on advanced topics, see the reference files:

- **libcurl Tutorial**: Complete guide to programming with libcurl in C
- **libcurl Easy Interface**: Single-transfer API (curl_easy_* functions)
- **libcurl Multi Interface**: Concurrent transfers API (curl_multi_* functions)
- **Command-Line Options**: Full reference of all curl CLI options
- **URL Syntax**: Detailed URL parsing and globbing rules
- **HTTP Cookies**: Cookie handling in depth
- **SSL/TLS Configuration**: Certificate management, cipher suites, ECH, HSTS
- **HTTP/3 Support**: QUIC protocol support details

## References

- Official documentation: https://github.com/curl/curl/tree/curl-8_19_0/docs
- curl website: https://curl.se/
- libcurl documentation: https://curl.se/libcurl/
- GitHub repository: https://github.com/curl/curl
