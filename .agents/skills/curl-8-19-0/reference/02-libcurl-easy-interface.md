---
name: libcurl-easy-interface-reference
description: Complete reference for libcurl easy interface (curl_easy_* functions) covering handle creation, option setting, data transfer, and cleanup. Includes all major API functions with usage patterns.
version: "8.19.0"
---

# libcurl Easy Interface Reference

## Core Functions

### Handle Management

```c
#include <curl/curl.h>

// Initialize a new easy handle (returns CURL* or NULL on failure)
CURL *curl_easy_init(void);

// Cleanup an easy handle (must be called for each curl_easy_init())
void curl_easy_cleanup(CURL *easy_handle);

// Reset all options to defaults on an existing handle
void curl_easy_reset(CURL *easy_handle);

// Duplicate a handle with all current options
CURL *curl_easy_duphandle(CURL *easy_handle);
```

### Transfer Execution

```c
// Perform a single blocking transfer (returns CURLcode)
CURLcode curl_easy_perform(CURL *easy_handle);

// Pause/unpause a transfer (protocol-dependent)
CURLcode curl_easy_pause(CURL *easy_handle, int bitmask);
// bitmask: CURLPAUSE_RECV / CURLPAUSE_SEND / CURLPAUSE_ALL / CURLPAUSE_CONT

// Maintain connection for persistent connections
CURLcode curl_easy_upkeep(CURL *easy_handle);
```

### Data I/O (for non-callback usage)

```c
// Send data on an established connection
CURLcode curl_easy_send(CURL *easy_handle, void *buffer,
                        size_t buflen, size_t *nwritten);

// Receive data from an established connection
CURLcode curl_easy_recv(CURL *easy_handle, void *buffer,
                        size_t buflen, size_t *nread);
```

### String Utilities

```c
// URL-encode a string (caller must free result with curl_free)
char *curl_easy_escape(CURL *easy_handle, const char *string, int length);

// URL-decode a string
char *curl_easy_unescape(CURL *easy_handle, const char *string,
                         int length, int *outlength);

// Deprecated aliases
char *curl_escape(const char *string, int length);
char *curl_unescape(const char *string, int length);
void   curl_free(void *ptr);
```

### Header Inspection

```c
// Get a specific header from the last transfer
struct curl_slist *curl_easy_header(CURL *easy_handle,
                                     const char *name,
                                     const char *value,
                                     int index,
                                     int reverse);

// Iterate over headers
struct curl_slist *curl_easy_nextheader(CURL *easy_handle,
                                         int direction,
                                         int kind,
                                         const char *name,
                                         int index);
```

### Options

```c
// Set options (returns CURLcode)
CURLcode curl_easy_setopt(CURL *easy_handle, CURLoption option, parameter);

// Get option by name
const struct curl_easyoption *curl_easy_option_by_name(const char *name);

// Get option by ID
const struct curl_easyoption *curl_easy_option_by_id(int id);

// Iterate through all options
const struct curl_easyoption *curl_easy_option_next(
    const struct curl_easyoption *prev);
```

### Version and Info

```c
// Get error string for a CURLcode
const char *curl_easy_strerror(CURLcode code);

// Get transfer information (returns CURLcode)
CURLcode curl_easy_getinfo(CURL *easy_handle, CURLINFO info, ...);

// Get date string from HTTP header
time_t curl_getdate(const char *p, const time_t *unused);

// Get environment variable value (thread-safe)
char *curl_getenv(const char *variable);
```

### SSL Session Management

```c
// Export SSL session data to DER format (returns allocated memory)
unsigned char *curl_easy_ssls_export(CURL *easy_handle, size_t *outlen);

// Import SSL session from DER data
CURLcode curl_easy_ssls_import(CURL *easy_handle,
                               const unsigned char *data, size_t length);
```

### WebSocket API

```c
// Start a WebSocket connection
CURLcode curl_ws_send(CURL *easy_handle, void *buffer,
                      size_t buflen, size_t *sent,
                      struct curl_ws_frame **metap);

// Receive WebSocket data
CURLcode curl_ws_recv(CURL *easy_handle, void *buffer,
                      size_t buflen, size_t *nrecv,
                      struct curl_ws_frame **metap);

// Get WebSocket metadata after receive
struct curl_ws_frame *curl_ws_meta(CURL *easy_handle);

// Start a WebSocket frame send (advanced)
CURLcode curl_ws_start_frame(CURL *easy_handle,
                             unsigned int control,
                             size_t *frameid);
```

### URL Parser API

```c
#include <curl/urlapi.h>

// Parse a URL string into components
CURLUcode curl_url(void);           // Create URL object (deprecated)
CURLU *curl_url_dup(CURLU *url);    // Duplicate URL object
void   curl_url_cleanup(CURLU *url); // Free URL object

// Get components from parsed URL
CURLUcode curl_url_get(CURLU *url, CURLUPart what, char **value, unsigned int flags);

// Set components of a URL
CURLUcode curl_url_set(CURLU *url, CURLUPart what, const char *value, unsigned int flags);

// Get error string for CURLUcode
const char *curl_url_strerror(CURLUcode code);
```

### Global Functions

```c
// Initialize libcurl (call once at program start)
CURLcode curl_global_init(long flags);

// Memory allocation callbacks (optional, for custom allocators)
CURLcode curl_global_init_mem(curl_malloc_callback *m,
                               curl_free_callback *f,
                               curl_realloc_callback *r,
                               curl_strdup_callback *s,
                               curl_calloc_callback *c);

// Cleanup libcurl (call once at program exit)
void   curl_global_cleanup(void);

// Get version string
char  *curl_version(void);

// Get detailed version info
struct curl_version_info *curl_version_info(int which);

// Trace API for debugging
CURLcode curl_global_trace(const char *config);
```

### Share Interface

```c
#include <curl/multi.h>

// Initialize a share object
CURLSH *curl_share_init(void);

// Set share options
CURLcode curl_share_setopt(CURLSH *share, CURLSHoption option, parameter);

// Cleanup share object
void   curl_share_cleanup(CURLSH *share);

// Get error string for share operations
const char *curl_share_strerror(CURLSHcode code);
```

## Common CURLOPT Values

### URL and Protocol

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_URL` | char * | Target URL |
| `CURLOPT_PROTOCOLS` | long | Bitmask of allowed protocols (CURLPROTO_*) |
| `CURLOPT_REDIR_PROTOCOLS` | long | Protocols allowed after redirect |
| `CURLOPT_CUSTOMREQUEST` | char * | Custom HTTP method (GET, POST, PUT, PATCH, etc.) |
| `CURLOPT_HTTPGET` | long | Force GET request (1 = yes) |
| `CURLOPT_NOBODY` | long | No body in response (HEAD-like) |

### Authentication

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_USERPWD` | char * | "user:password" for authentication |
| `CURLOPT_PROXYUSERPWD` | char * | Proxy credentials |
| `CURLOPT_HTTPAUTH` | long | Auth methods (CURLAUTH_BASIC, CURLAUTH_DIGEST, etc.) |
| `CURLOPT_PROXYAUTH` | long | Proxy auth methods |
| `CURLOPT_NETRC` | long | Use .netrc file for credentials |

### SSL/TLS

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_SSL_VERIFYPEER` | long | Verify peer certificate (1 = yes) |
| `CURLOPT_SSL_VERIFYHOST` | long | Verify hostname in cert (2 = strict) |
| `CURLOPT_CAINFO` | char * | Path to CA bundle file |
| `CURLOPT_CAPATH` | char * | Directory containing CA certificates |
| `CURLOPT_CERTFILE` | char * | Client certificate file (DER format) |
| `CURLOPT_KEYPASSWD` | char * | Private key password |
| `CURLOPT_SSLVERSION` | long | Force SSL version (SSLV3, TLSV1, etc.) |

### HTTP Options

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_HTTPHEADER` | curl_slist * | Custom headers list |
| `CURLOPT_POSTFIELDS` | char * | POST data body |
| `CURLOPT_POSTFIELDSIZE` | long | POST data size (0 = strlen) |
| `CURLOPT_HTTP_VERSION` | long | HTTP version (CURL_HTTP_VERSION_1_0, _1_1, _2, _2TLS, _2_PRI_KNOW, _3) |
| `CURLOPT_FOLLOWLOCATION` | long | Follow redirects (1 = yes) |
| `CURLOPT_MAXREDIRS` | long | Maximum redirects to follow |
| `CURLOPT_TIMEOUT` | long | Maximum time for entire transfer (seconds) |
| `CURLOPT_CONNECTTIMEOUT` | long | Connection timeout (seconds) |

### Callbacks and Data

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_WRITEFUNCTION` | size_t (*) | Write callback function |
| `CURLOPT_WRITEDATA` | void * | User data for write callback |
| `CURLOPT_HEADERFUNCTION` | size_t (*) | Header callback function |
| `CURLOPT_HEADERDATA` | void * | User data for header callback |
| `CURLOPT_READFUNCTION` | size_t (*) | Read callback (uploads) |
| `CURLOPT_READDATA` | void * | User data for read callback |
| `CURLOPT_PROGRESSFUNCTION` | int (*) | Progress callback |
| `CURLOPT_PROGRESSDATA` | void * | User data for progress callback |
| `CURLOPT_DEBUGFUNCTION` | int (*) | Debug callback |
| `CURLOPT_DEBUGDATA` | void * | User data for debug callback |

### Output Control

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_FILE` / `CURLOPT_WRITEDATA` | FILE * | Output file (default: stdout) |
| `CURLOPT_STDERR` | FILE * | Error output (default: stderr) |
| `CURLOPT_NOPROGRESS` | long | Disable progress meter (set to 0L to enable) |
| `CURLOPT_VERBOSE` | long | Enable verbose output (1 = yes) |
| `CURLOPT_HEADER` | long | Include header in output (1 = yes) |
| `CURLOPT_NOSIGNAL` | long | Ignore signals (for multi-threaded use) |

### Connection Control

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_PROXY` | char * | Proxy host:port |
| `CURLOPT_PROXYTYPE` | long | Proxy type (CURLPROXY_HTTP, SOCKS4, etc.) |
| `CURLOPT_FRESH_CONNECT` | long | Force new connection (1 = yes) |
| `CURLOPT_FORBID_REUSE` | long | Close connection after transfer (1 = yes) |
| `CURLOPT_MAXCONNECTS` | long | Maximum cached connections |
| `CURLOPT_INTERFACE` | char * | Network interface name |
| `CURLOPT_LOCALPORT` | long | Local port number to bind |

### FTP Options

| Option | Parameter Type | Description |
|--------|---------------|-------------|
| `CURLOPT_FTP_USE_EPSV` | long | Use EPSV (1 = yes) |
| `CURLOPT_FTP_USE_EPRT` | long | Use EPRT (1 = yes) |
| `CURLOPT_FTPPORT` | char * | IP for active FTP PORT command |
| `CURLOPT_QUOTE` | curl_slist * | Commands to run before transfer |
| `CURLOPT_POSTQUOTE` | curl_slist * | Commands to run after transfer |

### Error Handling

```c
// Get transfer info after curl_easy_perform()
double time_total, size_download, speed_download;
curl_easy_getinfo(curl, CURLINFO_TOTAL_TIME, &time_total);
curl_easy_getinfo(curl, CURLINFO_SIZE_DOWNLOAD_T, &size_download);
curl_easy_getinfo(curl, CURLINFO_SPEED_DOWNLOAD_T, &speed_download);
curl_easy_getinfo(curl, CURLINFO_HTTP_VERSION, &http_version);
curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

// Error buffer (set with CURLOPT_ERRORBUFFER before perform)
char errbuf[CURL_ERROR_SIZE];
curl_easy_setopt(curl, CURLOPT_ERRORBUFFER, errbuf);
```

## Usage Pattern Summary

```c
// 1. Initialize global state (once per program)
curl_global_init(CURL_GLOBAL_ALL);

// 2. Create handle
CURL *curl = curl_easy_init();

// 3. Set options
curl_easy_setopt(curl, CURLOPT_URL, "https://example.com/");
curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
curl_easy_setopt(curl, CURLOPT_WRITEDATA, outfile);

// 4. Perform transfer
CURLcode res = curl_easy_perform(curl);

// 5. Get info if needed
long http_code;
curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);

// 6. Cleanup handle
curl_easy_cleanup(curl);

// 7. Cleanup global state (once per program)
curl_global_cleanup();
```
