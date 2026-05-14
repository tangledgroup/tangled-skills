# libcurl Easy Interface

## Overview

The easy interface is libcurl's primary API for single, synchronous transfers. All functions are prefixed with `curl_easy`. It uses a handle-based model: create a handle, configure options, perform the transfer, then clean up.

## Handle Lifecycle

```c
#include <curl/curl.h>

// 1. Initialize global libcurl (once per program lifetime)
curl_global_init(CURL_GLOBAL_ALL);

// 2. Create an easy handle
CURL *handle = curl_easy_init();

// 3. Set options
curl_easy_setopt(handle, CURLOPT_URL, "https://example.com/");

// 4. Perform the transfer
CURLcode result = curl_easy_perform(handle);
if (result != CURLE_OK) {
    fprintf(stderr, "Error: %s\n", curl_easy_strerror(result));
}

// 5. Optionally reuse handle for another transfer
curl_easy_setopt(handle, CURLOPT_URL, "https://example.com/other");
curl_easy_perform(handle);

// 6. Cleanup
curl_easy_cleanup(handle);
curl_global_cleanup();
```

**Key principles:**
- Call `curl_global_init()` exactly once per program lifetime
- One easy handle per transfer (or thread)
- Never share the same handle across threads simultaneously
- Reuse handles for persistent connections — libcurl reuses TCP connections automatically
- Options are sticky — they remain set until changed
- Use `curl_easy_reset(handle)` to clear all options
- Use `curl_easy_duphandle(handle)` to clone a handle with all its options

## Setting Options

`curl_easy_setopt()` configures handle behavior. Over 300 options exist. Common categories:

**URL and transfer:**
- `CURLOPT_URL` — the URL to transfer (required)
- `CURLOPT_FOLLOWLOCATION` — follow HTTP redirects
- `CURLOPT_MAXREDIRS` — maximum redirect count (default 50)
- `CURLOPT_TIMEOUT` — total time limit in seconds
- `CURLOPT_CONNECTTIMEOUT` — connection time limit
- `CURLOPT_LOW_SPEED_LIMIT` / `CURLOPT_LOW_SPEED_TIME` — abort if speed drops below threshold

**Data callbacks:**
- `CURLOPT_WRITEFUNCTION` / `CURLOPT_WRITEDATA` — receive downloaded data
- `CURLOPT_READFUNCTION` / `CURLOPT_READDATA` — supply upload data
- `CURLOPT_HEADERFUNCTION` / `CURLOPT_HEADERDATA` — receive headers
- `CURLOPT_PROGRESSFUNCTION` / `CURLOPT_PROGRESSDATA` — transfer progress
- `CURLOPT_DEBUGFUNCTION` / `CURLOPT_DEBUGDATA` — verbose debug info

**Authentication:**
- `CURLOPT_USERNAME` / `CURLOPT_PASSWORD` — credentials
- `CURLOPT_HTTPAUTH` — auth method bitmask (`CURLAUTH_BASIC`, `CURLAUTH_DIGEST`, `CURLAUTH_NTLM`, `CURLAUTH_NEGOTIATE`)

**TLS/SSL:**
- `CURLOPT_SSL_VERIFYPEER` — verify server certificate (default 1, never disable in production)
- `CURLOPT_SSL_VERIFYHOST` — verify hostname matches certificate
- `CURLOPT_SSLCERT` / `CURLOPT_SSLKEY` — client certificate and key
- `CURLOPT_CAINFO` / `CURLOPT_CAPATH` — custom CA bundle

**Proxy:**
- `CURLOPT_PROXY` — proxy URL
- `CURLOPT_PROXYUSERNAME` / `CURLOPT_PROXYPASSWORD` — proxy credentials

## Write Callback

The write callback receives downloaded data:

```c
size_t write_callback(void *buffer, size_t size, size_t nmemb, void *userp) {
    size_t total = size * nmemb;
    // process 'total' bytes from 'buffer'
    return total;  // must return bytes processed
}

curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_callback);
curl_easy_setopt(handle, CURLOPT_WRITEDATA, &my_data);
```

If no callback is set, libcurl writes to stdout by default. The default callback can write to a `FILE *` via `CURLOPT_WRITEDATA`, but this crashes on Windows DLL — always use an explicit callback on Windows.

## Read Callback (Upload)

For uploading data:

```c
size_t read_callback(void *buffer, size_t size, size_t nmemb, void *userp) {
    // fill 'buffer' with data
    return bytes_written;  // 0 signals end of data
}

curl_easy_setopt(handle, CURLOPT_READFUNCTION, read_callback);
curl_easy_setopt(handle, CURLOPT_UPLOAD, 1L);
```

## Getting Info After Transfer

`curl_easy_getinfo()` extracts transfer metadata after `curl_easy_perform()`:

```c
long http_code;
curl_easy_getinfo(handle, CURLINFO_RESPONSE_CODE, &http_code);

double total_time;
curl_easy_getinfo(handle, CURLINFO_TOTAL_TIME, &total_time);

double download_size;
curl_easy_getinfo(handle, CURLINFO_SIZE_DOWNLOAD, &download_size);
```

Common info options: `CURLINFO_RESPONSE_CODE`, `CURLINFO_TOTAL_TIME`, `CURLINFO_CONNECT_TIME`, `CURLINFO_APPCONNECT_TIME`, `CURLINFO_SIZE_DOWNLOAD`, `CURLINFO_SIZE_UPLOAD`, `CURLINFO_EFFECTIVE_URL`, `CURLINFO_CONTENT_TYPE`.

## MIME API (since 7.56.0)

The recommended way to post multipart forms or send emails:

```c
CURL *easy = curl_easy_init();
curl_mime *mime = curl_mime_init(easy);
curl_mimepart *part = curl_mime_addpart(mime);

// Text field
curl_mime_data(part, "value", CURL_ZERO_TERMINATED);
curl_mime_name(part, "field_name");

// File field
part = curl_mime_addpart(mime);
curl_mime_filedata(part, "myfile.txt");
curl_mime_name(part, "file");
curl_mime_type(part, "text/plain");

curl_easy_setopt(easy, CURLOPT_MIMEPOST, mime);
curl_easy_perform(easy);
curl_mime_free(mime);
curl_easy_cleanup(easy);
```

MIME handles support nested subparts via `curl_mime_subparts()` for complex multipart structures (used in SMTP and IMAP).

## Error Handling

All easy functions return `CURLcode`. Use `curl_easy_strerror()` for human-readable messages:

```c
char error[CURL_ERROR_SIZE];
curl_easy_setopt(handle, CURLOPT_ERRORBUFFER, error);

if (curl_easy_perform(handle) != CURLE_OK) {
    fprintf(stderr, "Error: %s (%s)\n", error, curl_easy_strerror(result));
}
```

Common error codes:
- `CURLE_OK` (0) — success
- `CURLE_UNSUPPORTED_PROTOCOL` (1) — protocol not compiled in
- `CURLE_URL_MALFORMAT` (3) — malformed URL
- `CURLE_COULDNT_RESOLVE_HOST` (6) — DNS failure
- `CURLE_COULDNT_CONNECT` (7) — connection refused
- `CURLE_REMOTE_ACCESS_DENIED` (9) — 403 or access denied
- `CURLE_SSL_CACERT` (60) — SSL certificate verification failed
- `CURLE_OPERATION_TIMEDOUT` (28) — transfer timed out

## Header API (since 7.48.0)

Access HTTP response headers by name or iteration:

```c
struct curl_header *all = curl_easy_nextheader(handle, CURLH_HEADER, NULL);
while (all) {
    const char *name = curl_easy_header(handle, all, CURLH_NAME);
    const char *value = curl_easy_header(handle, all, CURLH_VALUE);
    all = curl_easy_header(handle, all, CURLH_NEXT);
}
```

Or get a specific header:

```c
const char *ct = curl_easy_header(handle, "Content-Type", CURLH_VALUE | CURLH_CASEInsensitive);
```

## Threading

libcurl is thread-safe but has no internal synchronization. Rules:
- Never share an easy handle across threads simultaneously
- Set `CURLOPT_NOSIGNAL(1L)` on all handles in multi-threaded programs (disables signal-based DNS timeouts)
- Build with c-ares or threaded-resolver for proper timeout support without signals
- TLS backends (OpenSSL 1.1.0+, mbedTLS with threading enabled) are thread-safe
