---
name: libcurl-multi-interface-reference
description: Complete reference for libcurl multi interface (curl_multi_* functions) covering concurrent transfers, event-based I/O with select() and multi_socket API, timeout handling, and transfer management.
version: "8.19.0"
---

# libcurl Multi Interface Reference

## Overview

The multi interface allows multiple simultaneous transfers in a single thread without blocking. It provides two flavors:

1. **Select-based** - Uses `curl_multi_fdset()` with standard `select()`/`poll()`
2. **Socket-based (multi_socket)** - Event-driven API for high-performance scaling to thousands of connections

## Select-Based Multi Interface

### Handle Management

```c
#include <curl/multi.h>

// Create a multi handle (returns CURLM* or NULL)
CURLM *curl_multi_init(void);

// Cleanup multi handle
void curl_multi_cleanup(CURLM *multi_handle);

// Get error string for CURLMcode
const char *curl_multi_strerror(CURLMcode code);
```

### Adding/Removing Easy Handles

```c
// Add an easy handle to the multi stack
CURLMcode curl_multi_add_handle(CURLM *multi_handle, CURL *easy_handle);

// Remove an easy handle from the multi stack
CURLMcode curl_multi_remove_handle(CURLM *multi_handle, CURL *easy_handle);

// Get all current easy handles
struct CURLMsg **curl_multi_get_handles(CURLM *multi_handle);
```

### Performing Transfers

```c
// Perform available work (non-blocking)
// *running_transfers is set to number of still-running transfers
CURLMcode curl_multi_perform(CURLM *multi_handle, int *running_transfers);
```

### Wait for Activity (Select-Based)

```c
// Fill fd_sets for select() call
// Returns bitmask: CURL_POLL_IN / CURL_POLL_OUT / CURL_POLL_NONE / CURL_POLL_REMOVE
int curl_multi_fdset(CURLM *multi_handle,
                     fd_set *read_fd_set,
                     fd_set *write_fd_set,
                     fd_set *exc_fd_set,
                     int *max_fd);

// Get recommended timeout in milliseconds
CURLMcode curl_multi_timeout(CURLM *multi_handle, long *milliseconds);

// Wait for socket activity (preferred over select + timeout)
CURLMcode curl_multi_poll(CURLM *multi_handle,
                          struct curl_waitfd *extra_fds,
                          unsigned int extra_nfds,
                          int timeout_ms,
                          int *ret);

// Modern replacement for fdset/timeout/poll
CURLMcode curl_multi_wait(CURLM *multi_handle,
                          struct curl_fd *fds,
                          unsigned int nfds,
                          int timeout_ms,
                          int *ret);
```

### Checking Completed Transfers

```c
// Get information about completed transfers
// Returns CURLMsg* (queue), NULL when empty
struct CURLMsg *curl_multi_info_read(CURLM *multi_handle,
                                      int *msgs_in_queue);

// Message structure:
typedef struct {
    CURLMSG msg;           // CURLMSG_DONE, etc.
    CURL easy_handle;      // Which handle completed
    union {
        void   *whatever;  // Protocol-specific data pointer
        int    result;     // CURLcode return code
    } data;
} CURLMsg;

// Message types:
enum CURLMSG {
    CURLMSG_NONE,    // No message
    CURLMSG_DONE,    // Transfer completed
    CURLMSG_OTHER    // Unknown message type
};
```

### Multi Interface Options

```c
CURLMcode curl_multi_setopt(CURLM *multi_handle, CURLMOpt option, parameter);

// Maximum number of simultaneous connections
curl_multi_setopt(multi, CURLMOPT_MAXCONNECTS, 10L);

// Connection cache sharing between handles
curl_multi_setopt(multi, CURLMOPT_PIPELINING, 1L);

// Socket callback (for multi_socket API)
curl_multi_setopt(multi, CURLMOPT_SOCKETFUNCTION, socket_callback);
curl_multi_setopt(multi, CURLMOPT_SOCKETDATA, user_data);

// Timer callback (for multi_socket API)
curl_multi_setopt(multi, CURLMOPT_TIMERFUNCTION, timer_callback);
curl_multi_setopt(multi, CURLMOPT_TIMERDATA, user_data);
```

### Getting Transfer Count

```c
// Get number of currently active transfers
CURLMcode curl_multi_get_handles(CURLM *multi_handle);
```

## Multi-Socket Interface (High Performance)

The multi_socket API is designed for event-driven applications using epoll, kqueue, libevent, libev, etc.

### Socket Callback Pattern

```c
// Called when socket activity changes
void socket_callback(CURL *easy, curl_socket_t sock, int what, void *userp, void *socketp);
// what: CURL_POLL_IN / CURL_POLL_OUT / CURL_POLL_REMOVE / CURL_POLL_NONE

// Called when timeout expires
void timer_callback(CURLM *multi, long timeout_ms, void *userp);

int main(void) {
    CURLM *multi = curl_multi_init();

    // Set callbacks
    curl_multi_setopt(multi, CURLMOPT_SOCKETFUNCTION, socket_callback);
    curl_multi_setopt(multi, CURLMOPT_SOCKETDATA, &socket_data);
    curl_multi_setopt(multi, CURLMOPT_TIMERFUNCTION, timer_callback);
    curl_multi_setopt(multi, CURLMOPT_TIMERDATA, &timer_data);

    // Add easy handles...

    // Start: call with CURL_SOCKET_TIMEOUT to trigger initial callbacks
    curl_multi_socket_action(multi, CURL_SOCKET_TIMEOUT, 0, &running);

    while (running) {
        // Wait for activity on registered sockets
        // When activity occurs or timeout expires:
        int events = POLLIN;  // or POLLOUT depending on socket callback
        curl_multi_socket_action(multi, active_socket, events, &running);

        // Check for completed transfers
        int msgq = 0;
        struct CURLMsg *msg;
        while ((msg = curl_multi_info_read(multi, &msgq))) {
            if (msg->msg == CURLMSG_DONE) {
                CURLcode result = msg->data.result;
                // Handle completion
            }
        }
    }

    curl_multi_cleanup(multi);
    return 0;
}
```

### Socket Action API

```c
// Primary multi_socket function (replaces curl_multi_perform)
CURLMcode curl_multi_socket_action(CURLM *multi_handle,
                                    curl_socket_t sockfd,
                                    int ev_bitmask,
                                    int *running_handles);

// Convenience wrappers:
CURLMcode curl_multi_socket(CURLM *multi_handle,
                            curl_socket_t sockfd,
                            int *running_handles);

CURLMcode curl_multi_socket_all(CURLM *multi_handle,
                                 int *running_handles);
```

### Wake Up Multi Handle

```c
// Interrupt a waiting curl_multi_poll/wait call
CURLMcode curl_multi_wakeup(CURLM *multi_handle);
```

## Blocking Restrictions in Multi Interface

Certain operations remain blocking even with the multi interface:

- Name resolution (unless c-ares or threaded-resolver backends are used)
- file:// transfers
- TELNET transfers

For non-blocking DNS, use c-ares backend.

## Complete Example: Select-Based

```c
#include <curl/curl.h>
#include <curl/multi.h>
#include <stdio.h>
#include <unistd.h>

#define MAX_HANDLES 10

int main(void) {
    CURLM *multi;
    CURL *handles[MAX_HANDLES];
    int still_running = 0;
    int num_urls = 3;
    const char *urls[] = {
        "https://example.com/",
        "https://curl.se/",
        "https://httpbin.org/get"
    };

    curl_global_init(CURL_GLOBAL_ALL);
    multi = curl_multi_init();

    // Create and add handles
    for (int i = 0; i < num_urls; i++) {
        handles[i] = curl_easy_init();
        curl_easy_setopt(handles[i], CURLOPT_URL, urls[i]);
        curl_easy_setopt(handles[i], CURLOPT_WRITEFUNCTION, fwrite);
        curl_easy_setopt(handles[i], CURLOPT_WRITEDATA, stdout);
        curl_multi_add_handle(multi, handles[i]);
    }

    // Process transfers
    do {
        CURLMcode mc = curl_multi_perform(multi, &still_running);

        if (mc == CURLM_OK) {
            int timeout;
            curl_multi_timeout(multi, &timeout);
            if (timeout < 0) timeout = 1000;

            // Wait with select() or poll()
            struct timeval tv;
            tv.tv_sec = timeout / 1000;
            tv.tv_usec = (timeout % 1000) * 1000;

            fd_set rd, wr, ex;
            FD_ZERO(&rd); FD_ZERO(&wr); FD_ZERO(&ex);
            int max_fd = -1;
            curl_multi_fdset(multi, &rd, &wr, &ex, &max_fd);

            if (max_fd >= 0) {
                select(max_fd + 1, &rd, &wr, &ex, &tv);
            } else {
                usleep(timeout * 1000);
            }
        }

        // Check for completed transfers
        int msgq = 0;
        struct CURLMsg *msg;
        while ((msg = curl_multi_info_read(multi, &msgq))) {
            if (msg->msg == CURLMSG_DONE) {
                CURL *easy = msg->easy_handle;
                CURLcode res = msg->data.result;
                printf("Transfer %p completed with code %d\n", easy, res);
            }
        }

    } while (still_running > 0);

    // Cleanup
    for (int i = 0; i < num_urls; i++) {
        curl_multi_remove_handle(multi, handles[i]);
        curl_easy_cleanup(handles[i]);
    }
    curl_multi_cleanup(multi);
    curl_global_cleanup();

    return 0;
}
```

## Multi Interface vs Easy Interface

| Feature | Easy Interface | Multi Interface |
|---------|---------------|-----------------|
| Transfers | Single, blocking | Multiple, concurrent |
| Threading | One per transfer | Single thread |
| I/O Model | Blocking | Event-driven (select/poll/epoll) |
| Complexity | Simple | Moderate |
| Scale | Limited by threads | Thousands of connections |
| Use case | Scripts, simple apps | High-concurrency applications |

## Key Differences from Easy Interface

1. `curl_easy_perform()` → `curl_multi_perform()` (non-blocking)
2. Handle is added to multi stack before starting
3. Must check `curl_multi_info_read()` for completion
4. Use `curl_multi_fdset()` or `curl_multi_poll()` to wait for activity
5. Easy handle must be removed from multi stack before cleanup
