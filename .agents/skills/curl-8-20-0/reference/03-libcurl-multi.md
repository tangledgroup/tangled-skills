# libcurl Multi Interface

## Overview

The multi interface enables multiple simultaneous transfers in a single thread using a "pull" model — the application drives when and how data is transferred. All functions are prefixed with `curl_multi`.

## Objectives

1. **Pull interface** — the application decides when to ask libcurl to transfer data
2. **Multiple concurrent transfers** in one thread
3. **Combined file descriptor waiting** — wait on both application and curl FDs simultaneously
4. **Event-based scaling** — handle thousands of parallel connections

## Architecture: One Multi Handle, Many Easy Handles

```
multi handle (curl_multi_init)
├── easy handle 1 (curl_easy_init → curl_multi_add_handle)
├── easy handle 2
├── easy handle 3
└── ...
```

## Basic Workflow

```c
CURLM *multi = curl_multi_init();

// Create and configure easy handles
CURL *easy1 = curl_easy_init();
curl_easy_setopt(easy1, CURLOPT_URL, "https://example.com/file1");
curl_easy_setopt(easy1, CURLOPT_WRITEFUNCTION, write_cb);

CURL *easy2 = curl_easy_init();
curl_easy_setopt(easy2, CURLOPT_URL, "https://example.com/file2");
curl_easy_setopt(easy2, CURLOPT_WRITEFUNCTION, write_cb);

// Add to multi handle (does not start transfer)
curl_multi_add_handle(multi, easy1);
curl_multi_add_handle(multi, easy2);

// Drive the transfers
int still_running = 0;
do {
    CURLMcode mc = curl_multi_perform(multi, &still_running);
    // Check mc for errors

    // Wait for activity (with timeout from libcurl)
    long timeout_ms;
    curl_multi_timeout(multi, &timeout_ms);
    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    // Use poll or select to wait
    curl_multi_poll(multi, NULL, 0, &tv, NULL);

} while (still_running > 0);

// Check completed transfers
CURLMsg *msg;
int pending;
while ((msg = curl_multi_info_read(multi, &pending))) {
    if (msg->msg == CURLMSG_DONE) {
        CURL *easy = msg->easy_handle;
        CURLcode result = msg->data.result;
        // Handle completion...

        curl_multi_remove_handle(multi, easy);
        curl_easy_cleanup(easy);
    }
}

curl_multi_cleanup(multi);
```

## Two API Styles

### select()-Oriented (Legacy)

Uses `curl_multi_fdset()` to extract fd_sets for `select()` or `poll()`, then `curl_multi_perform()` to drive transfers. Simpler but does not scale well beyond hundreds of connections.

### multi_socket (Recommended for Scale)

Uses `curl_multi_socket_action()` with socket and timer callbacks. Designed for high-performance operation with thousands of connections.

```c
void socket_cb(CURL *easy, curl_socket_t sock, int action,
               void *userp, void *socketp) {
    if (action == CURLCSELECT_IN || action == CURLCSELECT_OUT) {
        // Register 'sock' for read/write events in your event loop
    } else {
        // CURLCSELECT_NONE — deregister the socket
    }
}

void timer_cb(CURLM *multi, long timeout_ms, void *userp) {
    if (timeout_ms >= 0) {
        // Set a timer for timeout_ms milliseconds
    } else {
        // Cancel any existing timer
    }
}

// Setup callbacks
curl_multi_setopt(multi, CURLMOPT_SOCKETFUNCTION, socket_cb);
curl_multi_setopt(multi, CURLMOPT_SOCKETDATA, &my_data);
curl_multi_setopt(multi, CURLMOPT_TIMERFUNCTION, timer_cb);
curl_multi_setopt(multi, CURLMOPT_TIMERDATA, &my_data);

// Drive transfers when socket activity occurs
curl_multi_socket_action(multi, sock, ev_bitmask, &still_running);
```

When a socket has the expected activity (readable/writable), call `curl_multi_socket_action()` with that socket and the event bitmask.

## Key Functions

- `curl_multi_init()` — create multi handle
- `curl_multi_add_handle(multi, easy)` — add an easy handle to the stack
- `curl_multi_remove_handle(multi, easy)` — remove an easy handle
- `curl_multi_perform(multi, &still_running)` — drive all active transfers
- `curl_multi_socket_action(multi, sock, ev_bitmask, &still_running)` — event-driven drive
- `curl_multi_poll(multi, fds, nfds, timeout_ms, &timeout)` — wait for activity
- `curl_multi_fdset(multi, &fdread, &fdwrite, &fdexcep)` — extract fd sets
- `curl_multi_timeout(multi, &timeout_ms)` — get suggested select timeout
- `curl_multi_info_read(multi, &pending)` — read completion messages
- `curl_multi_cleanup(multi)` — destroy multi handle

## Important Rules

- You **must** call `curl_easy_cleanup()` for every easy handle before or after removing it from the multi stack
- Completed transfers leave the easy handle in the multi stack — you must explicitly remove it
- Adding handles does not start transfers — you drive them with `curl_multi_perform()` or `curl_multi_socket_action()`
- You can add/remove handles at any time, even during active transfers

## Share Interface

Enable data sharing between easy handles (cookies, DNS cache, TLS session cache, connection cache):

```c
CURLSH *share = curl_share_init();
curl_share_setopt(share, CURLSHOPT_SHARE, CURL_LOCK_DATA_COOKIE);
curl_share_setopt(share, CURLSHOPT_SHARE, CURL_LOCK_DATA_DNS);
curl_share_setopt(share, CURLSHOPT_SHARE, CURL_LOCK_DATA_SSL_SESSION);

// If multi-threaded, provide mutex callbacks
curl_share_setopt(share, CURLSHOPT_LOCKFUNC, my_lock_cb);
curl_share_setopt(share, CURLSHOPT_UNLOCKFUNC, my_unlock_cb);

// Attach to easy handles
curl_easy_setopt(easy1, CURLOPT_SHARE, share);
curl_easy_setopt(easy2, CURLOPT_SHARE, share);

// When done
curl_share_cleanup(share);
```

Shareable data types: `CURL_LOCK_DATA_COOKIE`, `CURL_LOCK_DATA_DNS`, `CURL_LOCK_DATA_SSL_SESSION`, `CURL_LOCK_DATA_CONNECT`, `CURL_LOCK_DATA_HSTS`.

Note: The connection pool and HSTS cache are not thread-safe in the share API — use mutex callbacks when sharing across threads.

## CURLMNWC (Multi Network Change Clear)

Since 7.84.0, libcurl provides `curl_multi_setopt()` with `CURLMOPT_PIPELINING` network change control via `curl_multi_setopt(multi, CURLMOPT_MAX_CONNS_PER_HOST, ...)`.

The `CURLMNWC_*` constants define what to clear:

- `CURLMNWC_CLEAR_CONNS (1L << 1)` — prevent further reuse of existing connections
- `CURLMNWC_CLEAR_DNS (1L << 2)` — clear the DNS cache associated with a host

**New in 8.20.0**: `CURLMNWC_CLEAR_ALL (1L << 0)` clears all network change types at once, including both connections and DNS cache. This is useful when network conditions change (e.g., switching from WiFi to cellular) and you want to reset all cached state:

```c
curl_multi_setopt(multi, CURLMOPT_PIPELINING, CURLPIPE_NOTHING);
// Clear everything after network change
curl_easy_setopt(handle, CURLOPT_CLEAR_REFERENCES, CURLMNWC_CLEAR_ALL);
```

## New in 8.20.0

**Thread pool and queue**: libcurl now uses a thread pool with queue-based dispatch for DNS resolving, replacing the older per-request thread model. This provides better resource management under high concurrency and eliminates orphaned variable references.

**CURLMNWC_CLEAR_ALL**: New constant added to `multi.h` for clearing all network change types in one call.
