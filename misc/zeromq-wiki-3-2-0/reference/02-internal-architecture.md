# Internal Architecture

## Overview

libzmq is approximately 10,000 lines of C++ code. Its complexity comes not from line count but from the sheer number of orthogonal combinations it handles: multiple operating systems, architectures (ARM to Itanium), compilers (gcc, MSVC, SunStudio), 20+ language bindings, different transports (in-process to multicast), multiple messaging patterns, connect/bind directionality, and persistent vs. transient connections.

## Global State

libzmq has no global variables. Instead, the user creates a **context** explicitly (`ctx_t` class) which stores all global state:

- List of available inproc endpoints
- List of sockets closed but still lingering due to unsent messages
- I/O thread pool
- Poller instances

This prevents issues when the library is linked into an executable twice.

## Concurrency Model

ØMQ uses message passing for internal concurrency — no mutexes, condition variables, or semaphores for orchestration. Each object lives in its own thread and no other thread ever touches it. Threads communicate by sending **commands** (internal messages, distinct from user-level ØMQ messages).

Derive from `object_t` base class to send and receive commands:

```cpp
// Send a 'term' command with linger=100 to object p
send_term (p, 100);

// Handle the 'term' command
void my_object_t::process_term (int linger) {
    // Implement your action here
}
```

For commands sent across the object tree (not along its lattices), a sequence counter mechanism ensures the destination won't disappear while the command is in-flight:

- Sender calls `inc_seqnum()` which increments `sent_seqnum` synchronously
- Receiver increments `processed_seqnum` when processing
- Object cannot shut down while `processed_seqnum < sent_seqnum`

Critical sections are used only when: (1) data must be accessible from any thread at any time, and (2) the guarded data is never touched on the critical path.

## Threading Model

Two kinds of threads in ØMQ:

1. **Application threads** — created outside ØMQ, used to access the API
2. **I/O threads** — created inside ØMQ, used to send/receive messages in background

From ØMQ's perspective, a "thread" is any object with a **mailbox** (`mailbox_t` class) — a queue for incoming commands processed in order. I/O threads map 1-to-1 with OS threads. Sockets have their own mailboxes and are treated as separate threads by ØMQ, even though multiple sockets can share one application thread. Sockets can be migrated between OS threads (e.g., Java binding passing a socket to the GC thread for destruction).

## I/O Threads

Each I/O thread (`io_thread_t`) owns a **poller** object (`poller_t`) — an abstraction over OS polling mechanisms (`select_t`, `poll_t`, `epoll_t`, etc.).

Objects living in I/O threads derive from `io_object_t`, providing:

- `add_fd()` / `rm_fd()` — register/unregister file descriptors with callbacks (`in_event`, `out_event`)
- `add_timer()` / `cancel_timer()` — register/cancel timers with `timer_event` callback

The I/O thread itself registers its mailbox file descriptor with the poller, firing `in_event` when commands arrive for dispatch.

## Object Trees

Internal objects are organized into tree hierarchies rooted at sockets. Each object can live in a different thread. The root (socket) lives in an application thread; remaining objects live in I/O threads.

Purpose: deterministic shutdown. When an object shuts down, it sends shutdown requests to all children and waits for confirmations before shutting down itself.

Termination sequence uses commands:

- `term` — parent asks child to shut down
- `term_ack` — child confirms termination
- `term_req` — child asks parent to shut it down (self-initiated)

The object tree mechanism is implemented in `own_t` class (derived from `object_t`).

## The Reaper Thread

`zmq_close()` should have POSIX-like behavior — return immediately even with pending outbound data. The socket sends a `reap` command to the reaper thread (`reaper_t`), which handles all handshaking in the application thread's stead. A dedicated thread is needed because ØMQ can be initialized with zero I/O threads (for in-process communication only).

## Messages

Message design optimizes for both very small and very large messages:

**Very Small Messages (VSMs)**: For messages ≤ `ZMQ_MAX_VSM_SIZE` (default 30 bytes), data is stored directly in the `zmq_msg_t` structure on the stack — no heap allocation. The `content` field contains the `ZMQ_VSM` constant.

**Heap Messages**: For larger messages, a `msg_content_t` structure is allocated on the heap containing:

- `data` — buffer address
- `size` — buffer size
- `ffn` — deallocation function pointer
- `hint` — hint value for deallocator
- `refcnt` — reference count (for shared buffers)

Buffer and metadata can be allocated in a single memory chunk to minimize allocations. `zmq_msg_copy()` does not physically copy the buffer — it creates a new `zmq_msg_t` pointing to the same buffer with incremented refcount.

**User-supplied buffers**: When the application provides its own buffer, metadata is allocated separately (cannot share the same memory chunk).

## Pipes

Pipes connect objects across threads. Each pipe has two endpoints (one in each thread's object). Messages flow through pipes between sender and receiver.

## Message Scheduling

All scheduling algorithms work on a flat array of pipes. Active pipes are at the beginning, passive pipes at the end. A single `active` variable determines how many initial pipes are active.

Deactivation is O(1): swap the deactivated pipe with the last active pipe and decrement `active`. This means load-balancing and fair-queueing are both O(1) operations regardless of total pipe count.

## Key Classes Summary

| Class | Purpose |
|-------|---------|
| `ctx_t` | Global state / context |
| `object_t` | Base class for command sending/receiving |
| `own_t` | Object tree ownership and termination |
| `io_thread_t` | Background I/O thread |
| `io_object_t` | Helper for objects in I/O threads (fd/timer registration) |
| `poller_t` | Abstraction over OS polling (select/poll/epoll) |
| `mailbox_t` | Command queue for inter-object communication |
| `reaper_t` | Dedicated thread for socket cleanup |
| `thread_t` | OS-agnostic thread wrapper |
