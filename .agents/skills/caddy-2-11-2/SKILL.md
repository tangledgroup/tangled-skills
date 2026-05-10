---
name: caddy-2-11-2
description: Complete Caddy 2.11.2 web server toolkit covering Caddyfile configuration, JSON API, automatic HTTPS with Let's Encrypt and ZeroSSL, reverse proxy, TLS/SSL, PKI, and modules. Use when configuring Caddy as a web server or reverse proxy, setting up automatic HTTPS, managing certificates, or implementing production-ready HTTP/HTTPS servers.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - web server
  - reverse proxy
  - HTTPS
  - Caddyfile
  - automatic SSL
  - ACME
  - HTTP/3
  - TLS
  - PKI
category: infrastructure
external_references:
  - https://github.com/caddyserver/caddy/tree/v2.11.2
  - https://caddy.community
  - https://caddyserver.com/docs/
  - https://caddyserver.com/docs/api-tutorial
  - https://caddyserver.com/docs/caddyfile-tutorial
  - https://github.com/caddyserver/website
---

# Caddy 2.11.2

## Overview

Caddy is a powerful, enterprise-ready, open source web server with automatic HTTPS written in Go. It is an extensible server platform that uses TLS by default, serving as both a web server and a general-purpose platform for running Go applications. Caddy's core manages configuration while modular "apps" (implemented as Caddy modules) provide functionality — the `http` and `tls` apps ship standard.

Key capabilities:

- **Automatic HTTPS** — ZeroSSL and Let's Encrypt for public names, fully-managed local CA for internal names and IPs, multi-issuer fallback, Encrypted ClientHello (ECH) support
- **Zero-downtime config reloads** — Graceful reloads via API or `caddy reload` with automatic rollback on failure
- **HTTP/1.1, HTTP/2, and HTTP/3** — All supported by default
- **Modular architecture** — Highly extensible plugin system, no external dependencies (not even libc)
- **Single static binary** — Written in Go with higher memory safety guarantees
- **Admin API** — RESTful JSON API at `localhost:2019` for dynamic configuration with ACID guarantees
- **Structured logging** — Zero-allocation structured logs in JSON format, configurable encoders and writers
- **Prometheus metrics** — Built-in monitoring with request duration, size, and error counters

Caddy's native configuration is a JSON document, but the Caddyfile config adapter provides a simplified, human-friendly format preferred for manual configuration. Other adapters support JSON5, YAML, TOML, and more.

## When to Use

- Configuring Caddy as a web server or reverse proxy
- Setting up automatic HTTPS with Let's Encrypt or ZeroSSL
- Creating Caddyfile configurations for sites and services
- Managing TLS certificates (public, local CA, wildcard, ECH)
- Building Go applications on the Caddy platform
- Implementing production-ready HTTP/HTTPS servers with zero-downtime reloads
- Configuring on-demand TLS for dynamic domain management
- Setting up Prometheus monitoring and structured logging
- Deploying Caddy as a systemd service, Docker container, or Windows service
- Writing custom Caddy modules or config adapters

## Core Concepts

**Caddy is a platform, not just a web server.** At its core, Caddy loads configuration and manages "apps" — Go modules that implement `Start()` and `Stop()` lifecycle methods. The `http` app handles web serving; the `tls` app manages certificates. Custom apps can extend Caddy for any long-running Go program.

**Configuration is a single JSON document.** Nearly all configuration lives in one config document rather than being scattered across CLI flags, environment variables, and files. The admin API loads, changes, and persists this document with zero-downtime reloads.

**Caddyfile vs JSON.** The Caddyfile is a config adapter — convenient for hand-crafted configs but less expressive than native JSON. JSON supports partial config changes, config traversal with `@id` tags, and full API compatibility. Caddyfile is preferred for manual editing; JSON for automation and programmatic deployment.

**Automatic HTTPS is default.** Any site with a hostname gets HTTPS automatically. Public domains use ACME CAs (Let's Encrypt, ZeroSSL) with HTTP or TLS-ALPN challenges. Local hosts (`localhost`, IPs) use Caddy's built-in local CA. Certificates are managed in the background with exponential backoff retry and multi-issuer fallback.

**Modules extend everything.** Caddy's plugin system uses Go imports to register modules. Each module has a namespace (e.g., `http.handlers.reverse_proxy`) and name. Modules are loaded from JSON, provisioned, validated, used, then cleaned up during config reloads. Standard modules ship built-in; third-party modules require custom builds via `xcaddy`.

## Advanced Topics

**Caddyfile Reference**: Structure, blocks, directives, matchers, placeholders, snippets, and named routes → [Caddyfile Reference](reference/01-caddyfile-reference.md)

**Global Options**: Server-wide settings for admin API, logging, TLS, storage, metrics, PKI, and more → [Global Options](reference/02-global-options.md)

**Directives**: Complete reference of all standard Caddyfile directives with syntax and examples → [Directives Reference](reference/03-directives-reference.md)

**Request Matchers**: Path, method, header, query, remote IP, protocol, and expression matchers → [Request Matchers](reference/04-request-matchers.md)

**Command Line**: CLI subcommands for running, reloading, adapting, validating, and managing Caddy → [Command Line Reference](reference/05-command-line.md)

**Admin API**: RESTful endpoints for dynamic configuration with zero-downtime reloads → [Admin API Reference](reference/06-admin-api.md)

**Automatic HTTPS**: Certificate management, ACME challenges, local CA, wildcard certs, ECH, on-demand TLS → [Automatic HTTPS](reference/07-automatic-https.md)

**Architecture and Operations**: Module lifecycle, config management, logging, metrics, service deployment → [Architecture and Operations](reference/08-architecture-operations.md)
