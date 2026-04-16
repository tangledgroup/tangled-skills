---
name: command-line-options-reference
description: Comprehensive reference for all curl command-line options organized by category, including HTTP/HTTPS, FTP, SSL/TLS, authentication, proxy, output control, and protocol-specific options.
version: "8.19.0"
---

# Command-Line Options Reference

## Option Syntax

- Short options: single dash, e.g., `-d`, `-v`, `-O`
- Long options: double dash, e.g., `--data`, `--verbose`, `--remote-name`
- Short options can be combined: `-OLv` = `-O -L -v`
- Boolean options disabled with `--no-option`: `--nobody`, `--nogloboff`
- `--next` resets parser state (global options persist)

## Authentication Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--user` | `-u` | Server user:password | `-u username:password` |
| `--basic` | | Use HTTP Basic authentication | `--basic -u user:pass` |
| `--digest` | | Use HTTP Digest authentication | `--digest -u user:pass` |
| `--ntlm` | | Use HTTP NTLM authentication | `--ntlm -u user:pass` |
| `--negotiate` | | Use HTTP Negotiate (SPNEGO) | `--negotiate -u user` |
| `--krb` | `-K` | Kerberos auth level (basic, safe, confidential, private) | `--krb level` |
| `--oauth2-bearer` | | OAuth 2.0 bearer token | `--oauth2-bearer TOKEN` |

## SSL/TLS Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--ssl` | `-P` | Use SSL/TLS for connection | `--ssl ftp://server.com` |
| `--ssl-reqd` | | Require SSL/TLS | `--ssl-reqd ftp://server.com` |
| `--cert` | | Client certificate file | `--cert client.pem` |
| `--cert-type` | | Certificate format (PEM, DER, P12) | `--cert-type PEM` |
| `--key` | | Private key file | `--key key.pem` |
| `--key-type` | | Private key format (PEM, DER, ENG) | `--key-type PEM` |
| `--pass` | | Private key password | `--pass secret` |
| `--cacert` | | CA certificate bundle | `--cacert ca-bundle.crt` |
| `--capath` | | Directory of CA certificates | `--capath /etc/ssl/certs` |
| `--ciphers` | | SSL cipher list | `--ciphers AES256-SHA` |
| `--curves` | | TLS key exchange curves | `--curves X25519:P-256` |
| `--pinnedpubkey` | | Public key hash to pin | `--pinnedpubkey "sha256/AABB..."` |
| `--crlfile` | | CRL file for certificate revocation | `--crlfile crl.pem` |
| `--tlsv1.0`-`--tlsv1.3` | | Require minimum TLS version | `--tlsv1.2` |
| `--tls-max` | | Maximum TLS version | `--tls-max 1.2` |
| `--tls13-ciphers` | | TLS 1.3 cipher suites | `--tls13-ciphers TLS_AES_256_GCM_SHA384` |
| `--egd-file` | | EGD socket path | `--egd-file /var/run/egd-pool` |
| `--random-file` | | Random file for SSL | `--random-file /dev/urandom` |
| `--egd-file` | | EGD entropy gatherer socket | `--egd-file PATH` |

## HTTP Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--request` | `-X` | Custom request method | `-X PATCH` |
| `--header` | `-H` | Custom header | `-H "Authorization: Bearer token"` |
| `--proxy-header` | | Proxy-specific header | `--proxy-header "X-Forwarded-For"` |
| `--http1.0` | | Use HTTP 1.0 | `--http1.0` |
| `--http1.1` | | Use HTTP 1.1 | `--http1.1` |
| `--http2` | | Require HTTP/2 (HTTPS only) | `--http2` |
| `--http2-prior-knowledge` | | HTTP/2 without ALPN negotiation | `--http2-prior-knowledge` |
| `--http3` | | Use HTTP/3 (QUIC) | `--http3` |
| `--http3-only` | | Require HTTP/3 only | `--http3-only` |
| `--user-agent` | `-A` | Custom User-Agent header | `-A "MyApp/1.0"` |
| `--referer` | `-e` | Referer header | `--referer https://example.com` |
| `--cookie` | `-b` | Cookie string | `-b "name=value"` |
| `--cookie-jar` | `-c` | Write cookies to file | `-c cookies.txt` |
| `--compressed` | | Request compressed response | `--compressed` |
| `--tr-encoding` | | Request chunked Transfer-Encoding | `--tr-encoding` |
| `--etag-compare` | | ETag for conditional GET | `--etag-compare "abc123"` |
| `--etag-save` | | Save ETag to file | `--etag-save etag.txt` |
| `--max-filesize` | `-r` | Maximum file size in bytes | `--max-filesize 1000000` |
| `--max-redirs` | `-L` | Maximum redirect count | `--max-redirs 20` |

## Data Transfer Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--data` | `-d` | HTTP POST data | `-d "name=value"` |
| `--data-raw` | | Same as --data, no @ interpretation | `--data-raw "@not-a-file"` |
| `--data-binary` | | Send binary data (no newline conversion) | `--data-binary @file.bin` |
| `--data-urlencode` | | URL-encode POST data | `--data-urlencode "name=value with spaces"` |
| `--form` | `-F` | Multipart form data | `-F "field=value" -F "file=@local.txt"` |
| `--upload-file` | `-T` | Upload file to server | `-T localfile.txt ftp://server.com/remote.txt` |
| `--upload-flags` | | Upload flags | `--upload-flags NO_CREDENTIALS` |

## Output Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--output` | `-o` | Write to file | `-o output.html` |
| `--remote-name` | `-O` | Use remote filename | `-O https://example.com/file.txt` |
| `--remote-name-all` | | Use remote name for all URLs | `--remote-name-all URL1 URL2` |
| `--remote-header-name` | | Use Content-Disposition header for filename | `--remote-header-name` |
| `--remote-time` | `-R` | Set local file time to remote time | `--remote-time` |
| `--create-dirs` | | Create directory structure | `--create-dirs` |
| `--output-dir` | | Directory for downloaded files | `--output-dir /tmp/downloads` |
| `--continue-at` | `-C` | Resume download at offset | `-C -` |
| `--range` | `-r` | Retrieve only a range of bytes | `-r 0-1023` |
| `--skip-existing` | | Skip URLs that result in downloaded file | `--skip-existing` |
| `--remove-on-error` | `-R` | Remove output file on error | `--remove-on-error` |

## Connection Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--url` | `-u` | URL to work with | `--url https://example.com` |
| `--interface` | `-i` | Network interface | `-i eth0` |
| `--ipv4` | `-4` | Use IPv4 only | `--ipv4` |
| `--ipv6` | `-6` | Use IPv6 only | `--ipv6` |
| `--local-port` | | Range of local ports to use | `--local-port 1000-2000` |
| `--dns-servers` | | DNS servers to use | `--dns-servers 8.8.8.8,1.1.1.1` |
| `--dns-interface` | | Network interface for DNS queries | `--dns-interface eth0` |
| `--connect-to` | | Map host:port to different host:port | `--connect-to example.com:443:localhost:8443` |
| `--resolve` | | Provide custom DNS resolution | `--resolve example.com:443:127.0.0.1` |
| `--retry` | | Number of retries on failure | `--retry 3` |
| `--retry-delay` | | Delay between retries (seconds) | `--retry-delay 5` |
| `--retry-max-time` | | Maximum retry time (seconds) | `--retry-max-time 30` |
| `--connect-timeout` | `-m` | Connection timeout (seconds) | `--connect-timeout 10` |
| `--max-time` | | Maximum total time (seconds) | `--max-time 60` |
| `--speed-limit` | | Abort if speed below this (bytes/sec) | `--speed-limit 1000` |
| `--speed-time` | | Time for speed-limit trigger (seconds) | `--speed-time 30` |

## Proxy Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--proxy` | `-x` | Use proxy server | `-x http://proxy:8080` |
| `--proxy-anyauth` | | Select proxy auth "any" method | `--proxy-anyauth` |
| `--proxy-basic` | | Use HTTP Basic for proxy | `--proxy-basic` |
| `--proxy-digest` | | Use HTTP Digest for proxy | `--proxy-digest` |
| `--proxy-ntlm` | | Use NTLM for proxy | `--proxy-ntlm` |
| `--proxy-user` | `-U` | Proxy user:password | `-U proxyuser:proxypass` |
| `--preproxy` | | Proxy before --proxy (chain) | `--preproxy http://chain-proxy:8080` |
| `--proxy-cacert` | | CA bundle for proxy SSL | `--proxy-cacert ca.pem` |
| `--proxy-capath` | | CA directory for proxy SSL | `--proxy-capath /path/to/certs` |
| `--proxy-insecure` | | Don't verify proxy SSL cert | `--proxy-insecure` |
| `--proxy-tlsv1` | | Require TLSv1 for proxy | `--proxy-tlsv1` |

## FTP Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--ftp-pret` | | Use PRET command before PASV | `--ftp-pret` |
| `--ftp-pasv` | | Use PASV instead of EPSV | `--ftp-pasv` |
| `--ftp-port` | | Use PORT for data connection | `--ftp-port 192,168,1,1:4000-5000` |
| `--ftp-skip-pasv-ip` | | Ignore PASV IP address | `--ftp-skip-pasv-ip` |
| `--ftp-method` | | Directory listing method (multirec, singlecwd, nocwd) | `--ftp-method multirec` |
| `--ftp-ssl-ccc` | | Send CCC after authentication | `--ftp-ssl-ccc` |
| `--ftp-ssl-ccc-mode` | | CCC mode (passive, active) | `--ftp-ssl-ccc-mode passive` |
| `--ftp-ssl-control` | | Require SSL for control, not data | `--ftp-ssl-control` |
| `--ftp-account` | | FTP account data | `--ftp-account ACCOUNT` |
| `--ftp-alternative-to-user` | | Alternative to USER command | `--ftp-alternative-to-user "str@site"` |
| `--disable-eprt` | | Disable EPRT and LPRT | `--disable-eprt` |
| `--disable-epsv` | | Disable EPSV | `--disable-epsv` |

## WebSocket Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--websocket` | `-I` | Negotiate WebSocket upgrade | `--websocket` |

## Verbose/Debug Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | More verbose output | `-v` or `-vv`, `-vvv` |
| `--silent` | `-s` | Silent mode (no progress meter) | `-s` |
| `--show-error` | `-S` | Show errors even with -s | `-sS` |
| `--trace` | `-trace` | Write trace to file | `--trace trace.txt` |
| `--trace-ascii` | | Trace with ASCII art | `--trace-ascii trace.txt` |
| `--trace-config` | | Control what gets traced | `--trace-config all` |
| `--trace-time` | | Prefix trace with timestamps | `--trace-time` |
| `--trace-ids` | | Include transfer IDs in verbose output | `--trace-ids` |
| `--dump-header` | `-D` | Dump headers to file | `-D headers.txt` |

## Progress Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--progress-bar` | `-#` | Display progress as bar | `-#` |
| `--no-progress-meter` | | Disable all progress output | `--no-progress-meter` |
| `--styled-output` | | Styled terminal output | `--styled-output` |

## Netrc and Configuration

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--netrc` | `-n` | Read credentials from .netrc | `--netrc` |
| `--netrc-optional` | | Use .netrc only if URL lacks auth | `--netrc-optional` |
| `--netrc-file` | | Specify netrc file path | `--netrc-file ~/.curl-netrc` |
| `--config` | `-K` | Read config from file | `--config ~/.curlrc` |

## Miscellaneous Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--location-trusted` | `-L` | Send auth to all redirects | `--location-trusted` |
| `--post301` | | Use POST for 301 redirect | `--post301` |
| `--post302` | | Use POST for 302 redirect | `--post302` |
| `--post303` | | Use POST for 303 redirect | `--post303` |
| `--path-as-is` | | Don't resolve .. segments | `--path-as-is` |
| `--globoff` | `-g` | Disable URL globbing | `--globoff` |
| `--disable` | | Disable all enabled protocols | `--disable` |
| `--proto` | | Enable/disable protocols | `--proto-default=https --proto -ftp` |
| `--proto-redir` | | Protocols allowed after redirect | `--proto-redir https,http` |
| `--haproxy-protocol` | | Send HAProxy PROXY protocol header | `--haproxy-protocol` |
| `--haproxy-clientip` | | Set HAProxy client IP | `--haproxy-clientip 1.2.3.4` |
| `--unix-socket` | | Connect via unix socket | `--unix-socket /var/run/docker.sock` |
| `--abstract-unix-socket` | | Connect via abstract unix socket | `--abstract-unix-socket docker` |
| `--true-ip` | | Use true IP for virtual hosts | `--true-ip 127.0.0.1` |
| `--alt-svc` | | Alt-Svc file to use | `--alt-svc alt-svc.txt` |
| `--disable-epsv` | | Disable EPSV for FTP | `--disable-epsv` |
| `--xattr` | | Use extended attributes for file metadata | `--xattr` |

## Write-Out Format Variables

Use with `--write-out` or `-w`:

| Variable | Description |
|----------|-------------|
| `%{url_effective}` | Final URL after redirects |
| `%{http_code}` | HTTP response code |
| `%{time_total}` | Total time in seconds |
| `%{time_namelookup}` | DNS resolution time |
| `%{time_connect}` | Time to establish TCP connection |
| `%{time_appconnect}` | Time to complete SSL/TLS handshake |
| `%{time_starttransfer}` | Time from start to first byte received |
| `%{size_download}` | Total downloaded bytes |
| `%{size_upload}` | Total uploaded bytes |
| `%{speed_download}` | Average download speed (bytes/sec) |
| `%{speed_upload}` | Average upload speed (bytes/sec) |
| `%{num_connects}` | Number of new connections |
| `%{redirect_count}` | Number of redirects followed |
| `%{content_type}` | Content-Type response header |
| `%{remote_ip}` | Remote IP address |
| `%{remote_port}` | Remote port number |
| `%{local_ip}` | Local IP address |
| `%{local_port}` | Local port number |

## Environment Variables

curl respects these environment variables:

| Variable | Description |
|----------|-------------|
| `http_proxy` / `HTTP_PROXY` | HTTP proxy URL |
| `https_proxy` / `HTTPS_PROXY` | HTTPS proxy URL |
| `ftp_proxy` / `FTP_PROXY` | FTP proxy URL |
| `all_proxy` / `ALL_PROXY` | Proxy for all protocols |
| `no_proxy` / `NO_PROXY` | Comma-separated list of hosts to bypass proxy |

The `-x`/`--proxy` flag overrides environment variables.
