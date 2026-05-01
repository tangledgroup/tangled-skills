# Protocols Reference

## HTTP / HTTPS

curl supports HTTP/0.9 (optionally), HTTP/1.0, HTTP/1.1, HTTP/2 (with multiplexing and server push), and HTTP/3 (QUIC).

**Methods:** GET, HEAD, POST, PUT, DELETE, OPTIONS, PATCH, and custom methods via `-X`/`--request`.

**Content encoding**: Automatic decompression for gzip, deflate, brotli, and zstd. Control with `--compressed`, `--compressed-ssh`, or `CURLOPT_ACCEPT_ENCODING`.

**Transfer-Encoding: chunked**: Supported in uploads.

**HTTP/1.1 trailers**: Both sending and receiving.

**ETags**: curl caches and re-sends ETags for conditional requests.

### POST Data

```bash
# URL-encoded form (application/x-www-form-urlencoded)
curl -d "key=value&foo=bar" https://example.com/api

# Auto URL-encode
curl --data-urlencode "name=John Doe" https://example.com/api

# Multipart form-data (with file upload)
curl -F "file=@photo.jpg;type=image/jpeg" -F "desc=A photo" https://example.com/upload

# Safe form string (no @ interpretation, for untrusted input)
curl --form-string "user_input=hello @world" https://example.com/api
```

Multiple `-F` flags create multiple form fields. Multiple files in one field:

```bash
curl -F "pics=@dog.gif,cat.gif" https://example.com/upload
```

### Custom HTTP Method

```bash
curl -X DELETE https://api.example.com/resource/123
curl -X PATCH -d '{"status":"active"}' -H "Content-Type: application/json" https://api.example.com/resource/123
```

### Time Conditions (Conditional GET)

```bash
# Download only if remote file is newer than local copy
curl -z local.html -o local.html https://remote.example.com/remote.html

# Download only if remote file is older than local copy
curl -z -local.html https://remote.example.com/remote.html

# Specify a date directly
curl -z "Jan 12 2012" https://example.com/file
```

### HTTP Fixes in 8.20.0

- Credentials are cleared better on redirect
- Digest nonce is cleared on cross-origin redirect
- Proxy credentials are cleared on port or scheme change
- `Curl_compareheader` now handles multiple comma-separated values correctly
- Secure schemes pushed over insecure connections are prevented (HTTP/2 server push fix)

## FTP / FTPS

**Passive mode (default)**: Server opens data port, client connects. Works when client is behind firewall.

**Active mode (PORT)**: Client opens port, server connects back. Use `-P`/`--ftp-port`:

```bash
curl -P 192.168.0.10 ftp://example.com/file   # specific IP
curl -P le0 ftp://example.com/file             # specific interface
curl -P - ftp://example.com/file               # default address
```

**Upload resume:**

```bash
curl -C - -T file ftp://ftp.example.com/path/file
```

**Directory listing**: Omit the filename to get a listing. Use `//` prefix for server root (vs user home).

**FTPS modes**:
- Implicit: `ftps://` scheme — SSL on both control and data connections
- Explicit: `--ssl-reqd ftp://` — upgrades plain FTP to SSL

```bash
# Explicit FTPS (recommended)
curl --ssl-reqd ftp://files.example.com/secrets.txt

# Implicit FTPS
curl ftps://files.example.com/secrets.txt
```

### FTP Fixes in 8.20.0

- MDTM date parser made stricter (again) to reject malformed dates
- PWD responses containing control characters are now rejected
- DATA hostname is no longer unnecessarily duplicated (strdup removed)

## SFTP / SCP

Uses SSH backend (libssh2 or OpenSSL). Supports password and public key authentication.

```bash
# Password auth
curl -u username sftp://example.com/etc/issue

# Key-based auth
curl -u username --key ~/.ssh/id_rsa sftp://example.com/path/file

# Known hosts verification
curl --ssh-host-public-key-file ~/.ssh/known_hosts sftp://example.com/file

# SCP with key
curl -u user: --key ~/.ssh/id_rsa scp://example.com/~/file.txt
```

Path `/~/` prefix accesses files relative to the remote user's home directory.

## IMAP / IMAPS

Access mailboxes, fetch emails, search, and upload via APPEND:

```bash
# List folders
curl imap://user@mail.example.com/

# Select INBOX
curl imap://user@mail.example.com/INBOX

# Fetch message by UID
curl imap://user@mail.example.com/INBOX/;UID=1

# Search for messages with "shadows" in subject
curl imap://user@mail.example.com/INBOX?SUBJECT%20shadows

# Check for NEW messages
curl imap://user@mail.example.com/INBOX?NEW

# Custom IMAP command
curl -X "UID SEARCH ALL" imap://user@mail.example.com/INBOX
```

Authentication: Clear Text and SASL (Plain, Login, CRAM-MD5, Digest-MD5, NTLM, Kerberos 5, External).

## SMTP / SMTPS

Send emails with libcurl or CLI:

```bash
# Send email (pipe message body)
echo -e "From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\n\r\nHello" | \
  curl --mail-from sender@example.com --mail-rcpt recipient@example.com \
  smtp://smtp.example.com

# With authentication
curl -u user:pass --mail-from sender@example.com --mail-rcpt recipient@example.com \
  --upload-file email.msg smtp://smtp.example.com
```

Authentication methods: Plain, Login, CRAM-MD5, Digest-MD5, NTLM, Kerberos 5, External.

Use `--mail-rcpt` multiple times for multiple recipients.

## POP3 / POP3S

Retrieve and manage emails:

```bash
# List emails
curl pop3://user@pop.example.com/

# Retrieve email #1
curl pop3://user@pop.example.com/1

# Custom command (STAT)
curl -X "STAT" pop3://user@pop.example.com/
```

Authentication: Clear Text, APOP, and SASL methods.

## LDAP

Full LDAP URL support per RFC 2255:

```bash
# Search for people with email in a domain
curl -B "ldap://ldap.example.com/o=frontec??sub?mail=*sth.example.com"

# With authentication
curl -u user:passwd "ldap://ldap.example.com/o=org??sub?mail=*"

# NTLM auth on Windows
curl --ntlm "ldap://user@ldap.example.com/o=org??sub?mail=*"
```

Default protocol version is LDAPv3 with LDAPv2 fallback.

## MQTT

Subscribe and publish topics:

```bash
# Publish to a topic
curl -d "message payload" mqtt://broker.example.com/topic/name

# Subscribe to a topic
curl mqtt://broker.example.com/topic/name
```

URL scheme: `mqtt://broker/topic`.

## WebSocket (libcurl only, since 7.86.0)

WebSocket communication is message-based over HTTP(S). Use `ws://` or `wss://` schemes.

```c
CURL *easy = curl_easy_init();
curl_easy_setopt(easy, CURLOPT_URL, "wss://example.com/ws");
curl_easy_setopt(easy, CURLOPT_CONNECT_ONLY, 1L);

// Perform the HTTP upgrade
curl_easy_perform(easy);

// Send a WebSocket message
size_t sent;
curl_ws_send(easy, "Hello", (size_t)6, &sent, 0);

// Receive a message
const char *recvd;
size_t recvd_len;
int fin;
enum curl_ws_type type;
curl_ws_recv(easy, &recvd, &recvd_len, &fin);
```

Control frames (PING, PONG, CLOSE) are handled automatically. Messages may be fragmented across multiple frames — `curl_ws_recv()` delivers complete messages.

## TELNET

Basic telnet support for passing stdin to the remote server:

```bash
curl telnet://remote.example.com
curl -tTTYPE=vt100 telnet://remote.example.com   # set terminal type
curl -tXDISPLOC=myhost:1 telnet://remote.example.com  # set X display
```

Use `-N`/`--no-buffer` for unbuffered output on slow connections.

## DICT

Dictionary lookups:

```bash
curl dict://dict.org/m:curl           # match terms
curl dict://dict.org/d:curl:jargon    # define in jargon dictionary
curl dict://dict.org/find:curl        # alias for match
```

## Other Protocols

**FILE**: Local file access via `file://localhost/path/to/file`. On Windows, drive letters supported.

**SMB/SMBS**: SMBv1 over TCP or SSL with NTLMv1 authentication. **Note**: SMB is disabled by default in 8.20.0 — use `--enable-smb` at build time to include it.

**TFTP**: Simple upload/download without authentication.

**GOPHER/GOPHERS**: Legacy protocol support.

**RTMP/RTMPT/RTMPE/RTMPS**: **Dropped in 8.20.0**. Adobe Real-Time Messaging Protocol support has been removed.

**RTSP**: Real Time Streaming Protocol with OPTIONS method.

## DNS Resolution (New in 8.20.0)

curl now uses a thread pool with queue-based dispatch for DNS resolving, replacing the older per-request threaded-resolver model. This provides:

- Better resource management under high concurrency
- Elimination of orphaned variable references
- Fixed HTTPS lookup when not on port 443 (async ares)
- Fixed query counter handling in async ares

Happy Eyeballs now includes resolution time delay for better concurrent connection attempt handling, and limits concurrent attempts via `cf-ip-happy`.
