# Security and Configuration

## Security Best Practices

### Never Disable Certificate Verification in Production

```bash
curl -k https://example.com/   # NEVER do this in production
```

Instead, fix the CA store or use `--cacert` to point to the correct CA bundle.

### Avoid Passwords on Command Lines

Passwords in command-line arguments are visible via `ps` and process listings. Use config files instead:

```bash
echo "user = user:passwd" | curl -K - https://secret.example.com/
```

Or use a protected config file:

```bash
# ~/.curlrc (mode 600)
user = user:passwd
```

Then simply: `curl https://secret.example.com/`

### Untrusted URLs

When accepting URLs from external users:
- Validate the scheme before passing to curl — attackers can use `file://`, `gopher://`, or other schemes
- Check the hostname to prevent localhost access (`127.0.0.1`, `localhost`)
- Watch for custom port numbers that could target local services
- Use libcurl's URL API (`curl_url()`) to parse and inspect URLs before use

### Clear Text Passwords

HTTP Basic, FTP, and TELNET send credentials unencrypted. Prefer:
- HTTPS with Digest, NTLM, or Negotiate authentication
- SSH-based protocols (SFTP, SCP)
- TLS-wrapped protocols (IMAPS, SMTPS, POP3S, FTPS)

## .netrc

curl supports `.netrc` for automatic login credentials:

```
machine example.com login myuser password mypass
machine ftp.example.com login ftpuser password ftppass
```

Enable with `-n`/`--netrc` (required) or `--netrc-optional` (used only if no other auth is provided).

**Warning**: `.netrc` stores passwords in plain text. File permissions should be `600`.

## Config Files

curl reads `~/.curlrc` (or `~/_curlrc` on Windows) automatically on startup.

```ini
# ~/.curlrc
-m 1800                          # 30 minute timeout
proxy = proxy.domain.com:8080    # default proxy
user-agent = "MyApp/1.0"         # custom user agent
```

- Options can use short flags (`-m`) or long names without dashes (`timeout`)
- Separate option and value with spaces, `=`, or `:`
- Lines starting with `#` are comments
- Values with spaces need double quotes: `"value with spaces"`
- Use `-q` to skip the default config file
- Use `-K filename` to specify a custom config file
- `-K -` reads config from stdin (hides options from process tables)

## Environment Variables

**Proxy variables:**

```bash
export http_proxy=http://proxy:8080
export https_proxy=http://proxy:8080
export ftp_proxy=http://proxy:8080
export ALL_PROXY=socks5://socks-proxy:1080
export NO_PROXY=localhost,.example.com,192.168.0.0/24
```

`-x`/`--proxy` on the command line overrides environment variables.

**CA bundle:**

```bash
export CURL_CA_BUNDLE=/path/to/ca-bundle.crt
# Also supported:
export SSL_CERT_FILE=/path/to/cert.pem
export SSL_CERT_DIR=/path/to/certs/
```

## Write-Out Format (`-w`/`--write-out`)

Extract transfer information after completion:

```bash
curl -s -o /dev/null -w "HTTP %{http_code}, Size %{size_download}, Time %{time_total}\n" https://example.com/
```

Common format variables:

- `%{http_code}` — HTTP response code
- `%{size_download}` — total bytes downloaded
- `%{size_upload}` — total bytes uploaded
- `%{speed_download}` — average download speed (bytes/sec)
- `%{speed_upload}` — average upload speed (bytes/sec)
- `%{time_total}` — total transfer time in seconds
- `%{time_connect}` — time to establish connection
- `%{time_appconnect}` — time to SSL/SSH handshake completion
- `%{time_starttransfer}` — time until first byte is about to be transferred
- `%{num_redirects}` — number of redirects followed
- `%{remote_ip}` — remote IP address
- `%{remote_port}` — remote port number
- `%{effective_url}` — final URL after redirects
- `%{content_type}` — content type of response
- `%{exitcode}` — curl's exit code

## Verbose and Debug Output

```bash
# Verbose mode (protocol details to stderr)
curl -v https://example.com/

# Extra verbose (more internal info)
curl -vvv https://example.com/

# Full trace to file (hex + ASCII)
curl --trace trace.log https://example.com/

# ASCII-only trace
curl --trace-ascii trace.txt https://example.com/

# Trace with timestamp
curl --trace-ascii trace.txt --trace-time https://example.com/
```

In libcurl, enable verbose output with `CURLOPT_VERBOSE(1L)` and use `CURLOPT_DEBUGFUNCTION` to receive debug callbacks.

## Parallel Transfers

Download multiple files in parallel:

```bash
curl -O https://example.com/file1 --parallel
curl -O https://example.com/file1 -O https://example.com/file2 --parallel
```

Or use URL globbing for batch downloads:

```bash
curl -O https://example.com/images/[001-100].jpg
curl -O https://example.com/{page1,page2,page3}.html
```

## Resuming Transfers

Continue interrupted downloads or uploads:

```bash
# Resume HTTP/FTP download
curl -C - -o file.zip https://example.com/file.zip

# Resume FTP upload
curl -C - -T file.zip ftp://ftp.example.com/file.zip
```

`-C -` tells curl to automatically determine the resume position.

## Interface and Network Control

```bash
# Bind to specific network interface
curl --interface eth0 https://example.com/
curl --interface 192.168.1.10 https://example.com/

# Force IPv4 or IPv6
curl --ipv4 https://example.com/
curl --ipv6 https://example.com/

# Local port range
curl --local-port 8000-9000 https://example.com/

# DNS-over-HTTPS
curl --doh-url https://cloudflare-dns.com/dns-query https://example.com/
```

## libcurl Security Considerations

**Global init in multi-threaded programs:**
- Call `curl_global_init(CURL_GLOBAL_ALL)` once before any other libcurl calls
- Never call it from multiple threads simultaneously
- Use `curl_global_cleanup()` once when done

**Handle isolation:**
- One easy handle per thread — never share handles across threads
- Set `CURLOPT_NOSIGNAL(1L)` in multi-threaded programs

**Memory management:**
- libcurl copies strings set via `curl_easy_setopt()` — the original string can be freed after setting
- Use `curl_free()` to free memory allocated by libcurl (e.g., from `curl_url_get()`)
- Replace malloc/free/realloc with custom functions via `curl_global_init_mem()` if needed

**Error buffer:**
- Always use `CURLOPT_ERRORBUFFER` for human-readable error messages:

```c
char errbuf[CURL_ERROR_SIZE];
curl_easy_setopt(handle, CURLOPT_ERRORBUFFER, errbuf);
```

## Security Fixes in 8.20.0

Eight security vulnerabilities were fixed in this release:

- **CVE-2026-7168**: Cross-proxy Digest auth state leak — Digest authentication state could leak across different proxy connections
- **CVE-2026-7009**: OCSP stapling bypass with Apple SecTrust — OCSP verification could be bypassed on macOS
- **CVE-2026-6429**: netrc credential leak with reused proxy connection — credentials from .netrc could leak when proxy connections were reused
- **CVE-2026-6276**: Stale custom cookie host causes cookie leak — cookies set for one host could leak to another via stale hostname
- **CVE-2026-6253**: Proxy credentials leak over redirect-to-proxy — proxy credentials could leak when following redirects to a proxy
- **CVE-2026-5773**: Wrong reuse of SMB connection — SMB connections could be incorrectly reused across different requests
- **CVE-2026-5545**: Wrong reuse of HTTP Negotiate connection — Negotiate authentication connections could be incorrectly reused
- **CVE-2026-4873**: Connection reuse ignores TLS requirement — connections established without required TLS settings could be reused for requests requiring those settings

**HTTP credential clearing improvements**: Credentials are now cleared better on redirect, digest nonce is cleared on cross-origin redirect, and proxy credentials are cleared on port or scheme change.

**NTLM disabled by default**: NTLM authentication is no longer compiled in by default. Use `--enable-ntlm` to include it. This reduces attack surface for deployments that don't need NTLM.

**SMB disabled by default**: SMB protocol support requires explicit `--enable-smb` at build time, reducing exposure to SMB-related vulnerabilities.
