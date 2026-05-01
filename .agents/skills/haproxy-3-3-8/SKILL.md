---
name: haproxy-3-3-8
description: Complete HAProxy 3.3.8 toolkit for load balancing, reverse proxying,
  SSL/TLS termination, and traffic management. Includes cumulative bug fixes from
  3.3.0 through 3.3.8 covering QUIC/HTTP3 hardening, SSL memory safety, mux-h1/h2
  robustness, Lua scripting fixes, ACME improvements, and CLI permission checks.
  Use when configuring HTTP/TCP load balancers, implementing high availability,
  managing SSL certificates, setting up health checks, configuring ACLs and content
  switching, or deploying HAProxy as a production-grade reverse proxy and load balancer.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.3.8"
tags:
  - load balancing
  - reverse proxy
  - SSL termination
  - high availability
  - HTTP proxy
  - TCP proxy
  - health checks
  - ACLs
category: infrastructure
external_references:
  - https://www.haproxy.org/download/3.3/src/haproxy-3.3.8.tar.gz
  - https://github.com/haproxy/haproxy
  - https://www.haproxy.org/
---

# HAProxy 3.3.8

## Overview

HAProxy is a high-performance, event-driven, non-blocking TCP/HTTP load balancer and reverse proxy. Written in C, it operates as a single process with multiple threads (one per CPU core by default), isolating itself into a chroot jail after startup. It supports HTTP/1.x, HTTP/2, HTTP/3 (QUIC), raw TCP, UDP, and UNIX sockets on both frontend and backend sides.

Version 3.3.8 is a maintenance release in the 3.3 branch (LTS, released November 2025). Per HAProxy's policy, maintenance versions contain only bug fixes — no new features. Version 3.3.8 includes cumulative fixes from 3.3.0 through 3.3.8 addressing critical security issues (memory leaks, buffer overflows, heap overflows), QUIC/HTTP3 protocol hardening, mux-h1/h2 robustness, Lua scripting stability, ACME certificate management improvements, and CLI permission enforcement.

Key capabilities include:

- **Load balancing** with 10+ algorithms: round-robin, leastconn, source, URI, hdr, first, consistent hashing, random, rdp-cookie, and url_param
- **SSL/TLS termination** with SNI-based multi-hosting (50,000+ domains supported), OCSP stapling, TLS tickets, dynamic record sizing, and certificate rotation at runtime
- **Health checking** via TCP connect, HTTP request, SMTP hello, SSL hello, LDAP, SQL, Redis, send/expect scripts, and external checks
- **Content switching** using ACLs that match on any element of requests/responses: source IP, headers, cookies, URLs, payload offsets
- **Stickiness/persistence** via cookie insertion/rewriting, source IP hashing, and stick-tables replicated across HAProxy nodes
- **PROXY protocol** v1 and v2 support for preserving client addresses through multiple proxy layers
- **Runtime management** via Unix socket CLI for live configuration changes, server state management, SSL certificate updates, and statistics
- **Lua scripting** (Lua 5.3) for custom sample fetches, converters, actions, services, and tasks
- **QUIC/HTTP3** with congestion control tuning, dedicated per-connection sockets, and retry protection
- **DNS resolution** with built-in resolver supporting round-robin DNS, SRV records, and runtime address updates

## When to Use

- Configuring HAProxy as an HTTP or TCP reverse proxy in front of application servers
- Setting up load balancing across multiple backend servers with health checks
- Implementing SSL/TLS termination with SNI-based multi-hosting
- Building high-availability architectures with keepalived/VRRP integration
- Performing content-based routing using ACLs and sample fetching
- Preserving client IP addresses through proxy chains with PROXY protocol
- Managing HAProxy at runtime via the CLI socket (server weight changes, SSL updates)
- Writing Lua scripts for custom HAProxy behavior
- Configuring stick-tables for rate limiting, DDoS protection, or session persistence
- Setting up QUIC/HTTP3 listeners with proper tuning
- Implementing multi-process or master-worker deployment modes
- Tuning performance parameters (buffer sizes, connection limits, thread counts)

## Core Concepts

**Frontends** accept incoming connections on listening sockets and apply frontend-specific processing rules before passing traffic to backends. They represent the client-facing side of proxying.

**Backends** define server farms with load balancing algorithms, health checks, and backend-specific processing rules. They represent the server-facing side.

**Listen sections** combine frontend and backend into a single proxy definition, useful for simple TCP passthrough or straightforward HTTP proxying.

**Proxies** are the fundamental configuration entities. HAProxy supports configurations with 300,000+ distinct proxies in a single process. Each connection is served by exactly one thread, so you need at least as many connections as threads to utilize all processing capacity.

**ACLs (Access Control Lists)** match conditions on sampled data extracted from connections, requests, or responses. They enable content-based routing, traffic filtering, and conditional actions. ACLs use fetch functions to extract values and matching operators to compare them against patterns.

**Sample fetching** extracts data from any point in the connection lifecycle. Fetches produce samples that can be converted, compared, stored in variables, logged, or used as action conditions. Samples have types (boolean, integer, string, IP address) and scopes (proc, sess, txn, req, res, check).

## Configuration Structure

HAProxy configuration files use a simple text format with sections:

- **global** — process-wide settings (maxconn, threads, SSL defaults, logging, chroot)
- **defaults** — default values inherited by all subsequent proxy sections
- **frontend** — client-facing proxy definitions with bind addresses and routing rules
- **backend** — server farm definitions with load balancing algorithms and health checks
- **listen** — combined frontend+backend (single proxy definition)
- **peers** — stick-table replication between HAProxy nodes
- **resolvers** — DNS resolver configuration for runtime address resolution
- **cache** — HTTP response cache configuration

Configuration supports environment variables within double quotes, conditional blocks (.if/.elif/.else/.endif), and time/size formats with unit suffixes (ms, s, m, h, d for time; k, m, g for size).

## Usage Examples

Basic HTTP reverse proxy:

```
global
    daemon
    maxconn 4096
    log 127.0.0.1 local0

defaults
    mode http
    timeout connect 5s
    timeout client 30s
    timeout server 30s

frontend http-in
    bind *:80
    default_backend web-servers

backend web-servers
    balance roundrobin
    server web1 192.168.1.10:8080 check
    server web2 192.168.1.11:8080 check
```

SSL termination with SNI:

```
frontend https-in
    bind *:443 ssl crt /etc/haproxy/certs/ alpn h2,http/1.1
    default_backend web-servers
```

Content-based routing with ACLs:

```
frontend http-in
    bind *:80
    acl is_api path_beg /api/
    acl is_static path_end .css .js .png .jpg
    use_backend api-servers if is_api
    use_backend static-servers if is_static
    default_backend web-servers
```

TCP load balancing with PROXY protocol:

```
listen tcp-app
    bind *:2222 accept-proxy
    mode tcp
    server srv1 10.0.0.1:22 send-proxy-v2 check
    server srv2 10.0.0.2:22 send-proxy-v2 check
```

Rate limiting with stick-tables:

```
frontend http-in
    bind *:80
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 100 }
    default_backend web-servers
```

## Advanced Topics

**Configuration Reference**: Complete reference for all configuration keywords in global, defaults, frontend, backend, listen, peers, resolvers, and cache sections → [Configuration Reference](reference/01-configuration-reference.md)

**ACLs and Sample Fetching**: Access control lists, sample fetch functions, converters, conditions, and content switching patterns → [ACLs and Sample Fetching](reference/02-acls-and-samples.md)

**Management and Runtime CLI**: Starting, stopping, reloading, Unix socket commands, statistics, server state management, and seamless upgrades → [Management and Runtime CLI](reference/03-management-and-runtime.md)

**Lua Scripting**: Lua integration architecture, sample fetches, converters, actions, services, tasks, sockets, and non-blocking design patterns → [Lua Scripting](reference/04-lua-scripting.md)

**PROXY Protocol and Peers**: PROXY protocol v1/v2 specification, TLV types, stick-table replication protocol between HAProxy nodes → [PROXY Protocol and Peers](reference/05-proxy-protocol-and-peers.md)

## Patch Notes (3.3.0 → 3.3.8)

All fixes are cumulative. Any 3.3.Z version includes all fixes from earlier versions in the branch.

### 3.3.8 (2026-04-30)

**Major/Critical:**
- BUG/MAJOR: http-htx — store new host in chunk for scheme-based normalization
- BUG/MAJOR: mux-h1 — deal with true 64-bit integers to emit chunk sizes
- BUG/MEDIUM: mux_h1 — fix stack buffer overflow in h1_append_chunk_size()
- BUG/MEDIUM: http-htx — don't use data from HTX message to update authority
- BUG/MEDIUM: http-htx — loop on full host value during scheme-based normalization
- BUG/MEDIUM: tasks — don't loop in task_schedule() if a task is running
- BUG/MEDIUM: mux-fcgi — properly handle full buffer for FCGI_PARAM record
- BUG/MEDIUM: acme — fix segfault on newOrder with empty authorizations

**SSL/TLS:**
- Fix memory leaks on realloc failure in ssl_ckch.c and ssl_sock.c
- Fix double-free on failed realloc in ssl_sock.c
- Validate minimum keyshare_len in smp_fetch_ssl_keyshare_groups
- Prevent integer overflow in distcc token parsing

**Other notable fixes:**
- tcpcheck: allow connection reuse without prior traffic
- peers: fix logical "and" when checking for local in PEER_APP_ST_STARTING
- peers: fix wrong flag reported twice for dump_flags
- http-htx: don't normalize empty path for OPTIONS requests
- acme: skip auth/challenge steps when newOrder returns a certificate
- Fix various typos and spelling mistakes in user-visible messages
- tools: my_memspn/my_memcspn wrong cast causing incorrect byte reading
- tools: fix memory leak in indent_msg() on out of memory
- sample: fix memory leak in check_when_cond(), fix NULL strm dereference

### 3.3.7 (2026-04-23)

**Major/Critical:**
- BUG/MAJOR: mux-h2 — detect incomplete transfers on HEADERS frames
- BUG/MAJOR: sched — protect task->expire on 32-bit platforms
- BUG/MAJOR: slz — always limit fixed output to less than worst case literals
- BUG/MEDIUM: htx — fix function used to change part of a block value when defrag
- BUG/MEDIUM: jwt — fix heap overflow in ECDSA signature DER conversion
- BUG/MEDIUM: payload — validate SNI name_len in req.ssl_sni
- BUG/MEDIUM: mux-h1 — disable 0-copy forwarding when draining the request
- BUG/MEDIUM: peers — trash of expired entries delayed after fullresync
- BUG/MEDIUM: cli — properly handle too big payload on command line
- BUG/MEDIUM: samples — fix handling of SMP_T_METH samples
- BUG/MEDIUM: mux-fcgi — prevent record-length truncation with large bufsize
- BUG/MEDIUM: ssl/cli — tls-keys commands warn when accessed without admin level
- BUG/MEDIUM: ssl/ocsp — ocsp commands warn when accessed without admin level
- BUG/MEDIUM: map/cli — CLI commands lack admin permission checks

**Notable:**
- hlua: fix stack overflow in httpclient headers conversion, format-string vulnerability, use-after-free
- peers: fix OOB heap write in dictionary cache update
- spoe: fix pointer arithmetic overflow
- resolvers: fix memory leak on AAAA additional records
- quic: close conn on packet reception with incompatible frame
- Multiple ACME fixes (resource leaks, error handling, argument checks)
- DOC: mention QUIC server support

### 3.3.6 (2026-03-19)

**Major/Critical:**
- BUG/MAJOR: h3 — check body size with content-length on empty FIN
- BUG/MEDIUM: ssl — handle receiving early data with BoringSSL/AWS-LC
- BUG/MEDIUM: peers — enforce check on incoming table key type

**Notable:**
- Extensive thread execution context (thread_exec_ctx) infrastructure for debugging/profiling
- mworker improvements and stability fixes
- h2/h3: properly ignore R bit in GOAWAY and WINDOW_UPDATE
- spoe: properly abort processing on client abort
- New set-dumpable=libs debug support with execution context tracking

### 3.3.5 (2026-03-09)

**Major/Critical:**
- BUG/MAJOR: qpack — unchecked length passed to huffman decoder
- BUG/MAJOR: fcgi — fix param decoding by properly checking its size
- BUG/MAJOR: resolvers — properly lowered names found in DNS response
- BUG/MEDIUM: mux-h2 — always report pending errors to the stream
- BUG/MEDIUM: stream — handle TASK_WOKEN_RES as a stream event
- BUG/MEDIUM: hpack — correctly deal with too large decoded numbers

**Notable:**
- qpack: fix 1-byte OOB reads in decoding, correctly deal with too large decoded numbers
- mux-h2: add tune.h2.log-errors setting for error logging control
- hlua: properly enable/disable line receives, fix end of request detection
- promex: fix server iteration when last server is deleted

### 3.3.4 (2026-02-19)

**Major/Critical:**
- BUG/MAJOR: revert mux-quic BUG_ON on locally closed QCS
- BUG/MEDIUM: h3 — reject frontend CONNECT as currently not implemented
- BUG/MEDIUM: ssl — SSL backend sessions used after free
- BUG/MEDIUM: applet — fix test on shut flags for legacy applets (v2)

**Notable:**
- mux-h2/quic: stop sending via fast-forward if stream is closed
- mux-h1: stop sending via fast-forward for unexpected states
- Extensive deviceatlas addon fixes (resource leaks, off-by-one, race conditions)
- ssl-f-use parser error handling improvements

### 3.3.3 (2026-02-12)

**Major/Critical:**
- BUG/MAJOR: quic — reject invalid token
- BUG/MAJOR: quic — fix parsing frame type
- BUG/MEDIUM: lb-chash — always properly initialize lb_nodes with dynamic servers

**Notable:**
- h1: strictly verify quoting in chunk extensions
- balance random: consider req rate when loads are equal
- ssl: SSL_CERT_DIR environment variable support
- Fine-grained task profiling settings at runtime

### 3.3.2 (2026-01-29)

**Major/Critical:**
- BUG/MAJOR: applet — don't call I/O handler if the applet was shut
- BUG/MEDIUM: peers — properly handle shutdown when trying to get a line
- BUG/MEDIUM: mworker — can't use signals after a failed reload
- BUG/MEDIUM: mux-h1 — update kop value during zero-copy forwarding
- BUG/MEDIUM: stconn — move data from kip to kop during zero-copy forwarding
- BUG/MEDIUM: ssl — fix msg callbacks on QUIC connections
- BUG/MEDIUM: hlua — fix invalid lua_pcall() usage in hlua_traceback()
- BUG/MEDIUM: quic — fix ACK ECN frame parsing
- BUG/MEDIUM: log — parsing log-forward options may result in segfault
- BUG/MEDIUM: ssl — fix error path on generate-certificates
- BUG/MEDIUM: promex — server iteration may rely on stale server

**Notable:**
- mux-h2: graceful close at 75% glitches threshold
- Lua 5.5 support added
- Certificate compression can be disabled (tune.ssl.certificate-compression)
- ECH configuration for QUIC listeners

### 3.3.1 (2025-12-19)

**Major/Critical:**
- BUG/MEDIUM: ssl — don't reuse TLS session if connection's SNI differs
- BUG/MEDIUM: ssl — always check ALPN after handshake
- BUG/MEDIUM: ssl — don't store ALPN for check connections
- BUG/MEDIUM: ssl — don't resume session for check connections
- BUG/MEDIUM: http-ana — properly detect client abort when forwarding response
- BUG/MEDIUM: http-ana — don't close server connection on read0 in TUNNEL mode
- BUG/MEDIUM: h3 — fix access to QCS sd definitely
- BUG/MEDIUM: quic — don't try to use hystart if not implemented
- BUG/MEDIUM: backend — do not remove CO_FL_SESS_IDLE in assign_server()

**Notable:**
- ECH (Encrypted Client Hello) support details documented
- QUIC congestion control algorithm (cc-algo) server keyword
- SNI hash-based TLS session caching improvements
- spop mode documentation improvements
