---
name: haproxy-3-3-0
description: Complete HAProxy 3.3.0 toolkit for load balancing, reverse proxying,
  SSL/TLS termination, and traffic management. Use when configuring HTTP/TCP load
  balancers, implementing high availability, managing SSL certificates, setting up
  health checks, configuring ACLs and content switching, or deploying HAProxy as a
  production-grade reverse proxy and load balancer.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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
  - https://github.com/haproxy/haproxy/tree/v3.3.0/doc
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/configuration.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/intro.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/lua.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/management.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/peers.txt
  - https://github.com/haproxy/haproxy/blob/v3.3.0/doc/proxy-protocol.txt
---

# HAProxy 3.3.0

## Overview

HAProxy is a high-performance, event-driven, non-blocking TCP/HTTP load balancer and reverse proxy. Written in C, it operates as a single process with multiple threads (one per CPU core by default), isolating itself into a chroot jail after startup. It supports HTTP/1.x, HTTP/2, HTTP/3 (QUIC), raw TCP, UDP, and UNIX sockets on both frontend and backend sides.

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
