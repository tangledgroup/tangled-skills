# URL Syntax and Schemes

## URL Structure

A curl URL consists of optional components separated by divider characters:

```
[scheme][divider][userinfo][hostname][port number][path][query][fragment]
```

Example with all components:

```
https://user:password@www.example.com:80/index.html?foo=bar#top
```

## "RFC 3986 plus"

curl's URL parser is grounded in RFC 3986 but allows pragmatic deviations:

**Spaces**: URLs cannot contain literal spaces — they must be percent-encoded. Exception: `Location:` redirect headers with spaces are re-encoded to `%20` by curl.

**Non-ASCII**: Byte values outside printable ASCII range are automatically percent-encoded.

**Multiple slashes**: curl accepts one, two, or three slashes after the colon (`http:/`, `http://`, `http:///`).

**Scheme-less URLs**: curl guesses the protocol from hostname prefix:

- `ftp.` → FTP
- `dict.` → DICT
- `ldap.` → LDAP
- `imap.` → IMAP
- `smtp.` → SMTP
- `pop3.` → POP3
- all others → HTTP

**Globbing**: curl supports `[N-M]` ranges and `{one,two,three}` lists in URLs. These characters (`[]{}`) are reserved in RFC 3986. Disable with `-g`/`--globoff`.

## Supported Schemes

**Transfer schemes** (case-insensitive):

`dict`, `file`, `ftp`, `ftps`, `gopher`, `gophers`, `http`, `https`, `imap`, `imaps`, `ldap`, `ldaps`, `mqtt`, `pop3`, `pop3s`, `rtmp`, `rtmpe`, `rtmps`, `rtmpt`, `rtmpte`, `rtmpts`, `rtsp`, `smb`, `smbs`, `smtp`, `smtps`, `telnet`, `tftp`

**Proxy schemes**: `http`, `https`, `socks4`, `socks4a`, `socks5`, `socks5h`, `socks`

## Default Ports by Scheme

- DICT 2628, FTP 21, FTPS 990, GOPHER 70, GOPHERS 70
- HTTP 80, HTTPS 443
- IMAP 143, IMAPS 993
- LDAP 389, LDAPS 636
- MQTT 1883
- POP3 110, POP3S 995
- RTMP 1935, RTMPS 443, RTMPT 80
- RTSP 554
- SCP 22, SFTP 22
- SMB 445, SMBS 445
- SMTP 25, SMTPS 465
- TELNET 23, TFTP 69

## Hostname Details

**localhost**: Since curl 7.77.0, `localhost` resolves to loopback addresses (`127.0.0.1`, `::1`) without DNS resolution, ensuring the host is truly local.

**IPv6**: Use brackets in URLs: `http://[2001:1890:1112:1::20]/`. Requires `-g` to disable globbing interpretation of brackets.

**Link-local IPv6**: Scope identifier must be numeric or match an existing interface, and `%` must be URL-escaped as `%25`: `sftp://[fe80::1234%251]/`

**IDN (International Domain Names)**: When built with libidn2, curl uses IDNA 2008. With WinIDN on Windows, it uses IDNA 2003 Transitional Processing.

## Userinfo

The `user:password@` component sets authentication credentials. Use of userinfo in URLs is discouraged for security reasons (passwords may appear in process listings, logs, etc.). Prefer `-u` option instead.

For IMAP, POP3, and SMTP, login options can follow the password with a semicolon separator.

## Scheme-Specific Behaviors

### FTP

- Path specifies the file to retrieve relative to the user's home directory
- Omitting the file returns a directory listing
- To access the server root explicitly, start path with `//` or `/%2f`

### FILE

- On Windows, hostname must be `localhost`, `127.0.0.1`, or blank
- Drive letters accepted: `file:///C:/path/to/file`

### IMAP

Path and query encode mailbox operations:

```
imap://user@host/INBOX/;UID=1                    # fetch by UID
imap://user@host/INBOX/;MAILINDEX=1              # fetch first message
imap://user@host/INBOX?NEW                        # check for NEW messages
imap://user@host/INBOX?SUBJECT%20shadows          # search subject
```

### SFTP / SCP

Path is absolute on the server. Use `/~/` prefix for paths relative to the user's home directory:

```bash
curl -u $USER sftp://home.example.com/~/.bashrc
```

## libcurl URL API

libcurl provides a dedicated URL parsing/generation API (since 7.62.0) separate from its internal parser, avoiding cross-parser security risks:

```c
#include <curl/curl.h>

CURLU *h = curl_url();                          // create handle
curl_url_set(h, CURLUPART_URL, "https://example.com:449/foo", 0);  // parse URL
char *scheme;
curl_url_get(h, CURLUPART_SCHEME, &scheme, 0);  // extract part
curl_url_cleanup(h);                            // free handle
```

Available parts: `CURLUPART_SCHEME`, `CURLUPART_USER`, `CURLUPART_PASSWORD`, `CURLUPART_HOST`, `CURLUPART_PORT`, `CURLUPART_PATH`, `CURLUPART_QUERY`, `CURLUPART_FRAGMENT`, `CURLUPART_ZONEID`.

Relative URL resolution via redirect:

```c
curl_url_set(h, CURLUPART_URL, "../test?another", 0);  // resolves relative to current URL
```
