---
name: obscura-0-1-1
description: Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs real JavaScript via V8, supports Chrome DevTools Protocol (CDP), and acts as a drop-in replacement for headless Chrome with Puppeteer and Playwright. Use when building scrapers, automating web interactions, replacing headless Chrome with lower memory footprint (~30 MB vs 200+ MB), or needing built-in anti-detection capabilities.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.1"
tags:
  - headless-browser
  - web-scraping
  - rust
  - cdp
  - puppeteer
  - playwright
  - v8
  - anti-detection
category: web-scraping
external_references:
  - https://github.com/h4ckf0r0day/obscura/tree/v0.1.1
  - https://chromedevtools.github.io/devtools-protocol/
  - https://github.com/h4ckf0r0day/obscura
  - https://github.com/h4ckf0r0day/obscura/releases/tag/v0.1.1
  - https://github.com/h4ckf0r0day/obscura/releases
---

# Obscura 0.1.1

## Overview

Obscura is a headless browser engine written in Rust, built for web scraping and AI agent automation. It runs real JavaScript via V8 (through Deno Core), supports the Chrome DevTools Protocol (CDP), and acts as a drop-in replacement for headless Chrome when used with Puppeteer and Playwright.

Designed for automation at scale rather than desktop browsing, Obscura achieves dramatic resource savings:

- **Memory**: ~30 MB vs 200+ MB for headless Chrome
- **Binary size**: ~70 MB vs 300+ MB
- **Page load**: 51–85 ms vs ~500–800 ms
- **Startup**: Instant vs ~2 seconds
- **Anti-detection**: Built-in (with `--stealth` feature)

Single binary. No Chrome, no Node.js, no external dependencies.

## Changes in 0.1.1

Patch release over 0.1.0 with three bug fixes:

- Load balancer no longer panics on unwrap; `/json/version` round-robins through workers; dead workers return 502 instead of silent drops
- `--stealth` flag actually takes effect in serve mode; log message reflects what's compiled in
- Shadow DOM polyfill no longer throws TypeError on parentNode assignment (fixes Cloudflare Turnstile and similar)

## When to Use

- Web scraping at scale with minimal memory footprint
- AI agent automation that needs real JavaScript execution
- Replacing headless Chrome in Puppeteer or Playwright workflows
- Environments where anti-detection is required (stealth mode)
- Parallel URL processing with concurrent worker processes
- Converting rendered HTML pages to Markdown via CDP

## Core Concepts

### Architecture

Obscura is a Rust workspace with six crates:

- **obscura-cli** — Command-line interface (`obscura` and `obscura-worker` binaries)
- **obscura-browser** — Browser context, page lifecycle, navigation
- **obscura-cdp** — Chrome DevTools Protocol server implementation
- **obscura-dom** — HTML5 DOM tree (via html5ever), CSS selectors
- **obscura-js** — JavaScript runtime (Deno Core + V8 engine)
- **obscura-net** — HTTP client, cookies, robots.txt, tracker blocklist

### Three Modes of Operation

1. **CLI fetch** — Single-page fetch with `obscura fetch <url>`
2. **CDP server** — WebSocket server for Puppeteer/Playwright via `obscura serve`
3. **Parallel scrape** — Multi-URL scraping with `obscura scrape url1 url2 ...`

### Page Lifecycle

Pages progress through lifecycle states: `Idle` → `Loading` → `DomContentLoaded` → `Loaded` → `NetworkIdle`. Navigation supports wait conditions: `load`, `domcontentloaded`, `networkidle0`, `networkidle2`.

### Browser Context

Each `BrowserContext` encapsulates a cookie jar, HTTP client, user agent, proxy URL, robots.txt cache, and stealth flag. Pages share context within a session.

## CLI Reference

### `obscura serve`

Start a CDP WebSocket server compatible with Puppeteer and Playwright.

```bash
# Default: port 9222
obscura serve

# Custom port
obscura serve --port 9333

# With stealth mode (anti-detection + tracker blocking)
obscura serve --stealth

# With proxy
obscura serve --proxy http://user:pass@proxy:8080

# Multiple worker processes with load balancer
obscura serve --workers 4
```

Flags:

- `--port` (default: `9222`) — WebSocket port
- `--proxy` — HTTP/SOCKS5 proxy URL
- `--stealth` — Enable anti-detection + tracker blocking
- `--workers` (default: `1`) — Number of parallel worker processes
- `--obey-robots` — Respect robots.txt

When run without a subcommand, `obscura` defaults to serve mode on the specified port.

### `obscura fetch <URL>`

Fetch and render a single page.

```bash
# Get page title via JavaScript evaluation
obscura fetch https://example.com --eval "document.title"

# Dump rendered HTML
obscura fetch https://example.com --dump html

# Extract readable text
obscura fetch https://news.ycombinator.com --dump text

# List all links
obscura fetch https://example.com --dump links

# Wait for dynamic content (network idle)
obscura fetch https://example.com --wait-until networkidle0

# Wait for a CSS selector to appear
obscura fetch https://example.com --selector "#main-content"

# Stealth mode
obscura fetch https://example.com --stealth --eval "document.title"
```

Flags:

- `--dump` (default: `html`) — Output format: `html`, `text`, or `links`
- `--eval` — JavaScript expression to evaluate and print result
- `--wait-until` (default: `load`) — Wait condition: `load`, `domcontentloaded`, `networkidle0`
- `--selector` — Wait for CSS selector before dumping
- `--stealth` — Anti-detection mode
- `--quiet` — Suppress banner and status messages
- `--user-agent` — Custom user agent string

### `obscura scrape <URL...>`

Scrape multiple URLs in parallel using worker processes.

```bash
# Scrape 3 URLs with default concurrency (10)
obscura scrape url1 url2 url3 --format json

# Evaluate JavaScript on each page
obscura scrape url1 url2 --eval "document.title" --concurrency 25

# Text output format
obscura scrape url1 url2 url3 --format text
```

Flags:

- `--concurrency` (default: `10`) — Number of parallel workers
- `--eval` — JavaScript expression to evaluate per page
- `--format` (default: `json`) — Output format: `json` or `text`

JSON output includes per-result timing and overall statistics.

## Advanced Topics

**CDP Server Architecture**: Domains, protocol implementation, WebSocket handling → [CDP Server](reference/01-cdp-server.md)

**Puppeteer and Playwright Integration**: Connecting via CDP, form submission, page automation → [Automation Integration](reference/02-puppeteer-playwright.md)

**Stealth Mode**: Anti-fingerprinting, tracker blocking, TLS spoofing → [Stealth Mode](reference/03-stealth-mode.md)

**Internal Architecture**: Crate structure, V8 runtime, DOM tree, HTTP client → [Architecture Deep Dive](reference/04-architecture.md)
