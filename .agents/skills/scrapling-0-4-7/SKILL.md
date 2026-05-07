---
name: scrapling-0-4-7
description: Web scraping tool that converts web pages to Markdown using Scrapling v0.4.7's CLI. Use when extracting content from URLs, converting web pages to readable Markdown for AI context or documentation, scraping JS-rendered pages with browser automation, or bypassing anti-bot protections with stealthy fetching.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.4.7"
tags:
  - web-scraping
  - markdown
  - cli-tool
  - uvx
  - browser-automation
category: cli-tool
external_references:
  - https://scrapling.readthedocs.io/en/latest/
  - https://github.com/D4Vinci/Scrapling/tree/v0.4.7
---

# Scrapling 0.4.7

## Overview

Scrapling is an adaptive web scraping framework that provides a powerful CLI (`scrapling extract`) for downloading and extracting content from websites without writing code. The CLI supports plain HTTP requests, browser-based fetching (for JavaScript-rendered pages), and stealth mode (for anti-bot bypass).

Output format is determined by the output file extension: `.md` converts HTML to Markdown, `.txt` extracts clean text, and `.html` saves raw HTML.

This skill covers the `uvx 'scrapling[shell]'` CLI workflow for converting web pages to Markdown — either returned inline or saved to a file.

## When to Use

- A user provides a bare URL (e.g., `https://example.com`) — scrape it and return Markdown
- Extracting webpage content as clean Markdown for AI context, documentation, or notes
- Scraping JavaScript-rendered pages that require browser automation
- Bypassing Cloudflare or other anti-bot protections with stealthy fetching
- Targeting specific page sections with CSS selectors

## Default Workflow

The default behavior is: user provides a URL → scrape it → return Markdown inline.

**Default flags:** Every command includes `--ai-targeted` (strips noise for clean AI-ready output). The `get` mode additionally includes `--impersonate safari` (Safari browser headers for better compatibility and lower detection). These defaults apply unless the user explicitly requests different behavior.

Scrapling's CLI requires writing to a file with a `.md` extension to trigger HTML-to-Markdown conversion. The standard workflow uses a temporary file:

```bash
TMPFILE=$(mktemp /tmp/scrape-XXXXXX.md)
uvx 'scrapling[shell]' extract get 'https://example.com' "$TMPFILE" --impersonate safari --ai-targeted
cat "$TMPFILE"
rm -f "$TMPFILE"
```

The temp file is always created, read back, then deleted — never left behind.

When the user explicitly requests saving to a file, write directly to the target path instead:

```bash
uvx 'scrapling[shell]' extract get 'https://example.com' '/path/to/output.md' --impersonate safari --ai-targeted
```

## Fetch Modes

Three fetch modes are available. Default is `get` when no mode is specified.

### get (alias: simple-fetch)

Plain HTTP request. Fastest option, works for static pages. Default flags: `--impersonate safari --ai-targeted`.

```bash
uvx 'scrapling[shell]' extract get '<URL>' <output_file> --impersonate safari --ai-targeted
```

Common options:
- `-s, --css-selector TEXT` — Extract specific content via CSS selector
- `--timeout INTEGER` — Request timeout in seconds (default: 30)
- `--proxy TEXT` — Proxy URL (`http://user:pass@host:port`)
- `-H, --headers TEXT` — Custom headers (repeatable)
- `--cookies TEXT` — Cookies string (`name1=value1;name2=value2`)
- `-p, --params TEXT` — Query parameters (repeatable)
- `--impersonate TEXT` — Browser to impersonate (default: `safari`; e.g., `chrome`, `firefox`)
- `--ai-targeted` — Extract only main content, strip noise for AI consumption (default: on)

### fetch

Browser automation via DynamicFetcher. Use when the page requires JavaScript to render content. Default flag: `--ai-targeted`. Note: `--impersonate` is not available for browser-based fetchers — they use real browser rendering instead.

```bash
uvx 'scrapling[shell]' extract fetch '<URL>' <output_file> --ai-targeted
```

Common options:
- `--network-idle` — Wait for network idle before extracting
- `--wait INTEGER` — Additional wait time in milliseconds after page load
- `--wait-selector TEXT` — Wait for specific CSS selector before proceeding
- `--disable-resources` — Drop unnecessary resources (images, fonts) for speed
- `-s, --css-selector TEXT` — Extract specific content via CSS selector
- `--proxy TEXT` — Proxy URL
- `--block-ads` — Block ad and tracker domains
- `--ai-targeted` — Extract only main content, strip noise for AI consumption (default: on)

### stealthy-fetch (aliases: stealth-fetch, undetected-fetch)

Advanced stealth mode via StealthyFetcher. Use when the target site has anti-bot protections (Cloudflare, etc.). Default flag: `--ai-targeted`. Note: `--impersonate` is not available for browser-based fetchers — StealthyFetcher has its own built-in stealth mechanisms.

```bash
uvx 'scrapling[shell]' extract stealthy-fetch '<URL>' <output_file> --ai-targeted
```

Common options:
- `--solve-cloudflare` — Solve Cloudflare challenges automatically
- `--block-webrtc` — Block WebRTC to prevent IP leaks
- `--hide-canvas` — Add noise to canvas operations for fingerprint resistance
- `--proxy TEXT` — Proxy URL
- `--dns-over-https` — Route DNS through Cloudflare DoH to prevent DNS leaks
- `-s, --css-selector TEXT` — Extract specific content via CSS selector
- `--ai-targeted` — Extract only main content, strip noise for AI consumption (default: on)

## Usage Examples

### Default: URL only (get mode, return Markdown inline)

```bash
TMPFILE=$(mktemp /tmp/scrape-XXXXXX.md)
uvx 'scrapling[shell]' extract get 'https://example.com' "$TMPFILE" --impersonate safari --ai-targeted
cat "$TMPFILE"
rm -f "$TMPFILE"
```

### Save to a specific file

```bash
uvx 'scrapling[shell]' extract get 'https://example.com' './notes/example.md' --impersonate safari --ai-targeted
```

### Extract with CSS selector

```bash
TMPFILE=$(mktemp /tmp/scrape-XXXXXX.md)
uvx 'scrapling[shell]' extract get 'https://blog.example.com' "$TMPFILE" --impersonate safari --ai-targeted -s 'article'
cat "$TMPFILE"
rm -f "$TMPFILE"
```

### JavaScript-rendered page (fetch mode)

```bash
TMPFILE=$(mktemp /tmp/scrape-XXXXXX.md)
uvx 'scrapling[shell]' extract fetch 'https://app.example.com' "$TMPFILE" --ai-targeted --network-idle
cat "$TMPFILE"
rm -f "$TMPFILE"
```

### Anti-bot bypass (stealthy-fetch mode)

```bash
TMPFILE=$(mktemp /tmp/scrape-XXXXXX.md)
uvx 'scrapling[shell]' extract stealthy-fetch 'https://protected.example.com' "$TMPFILE" --ai-targeted --solve-cloudflare
cat "$TMPFILE"
rm -f "$TMPFILE"
```

### Override defaults

If the user requests different behavior (e.g., no impersonation, different browser, or raw output), adjust or omit the default flags accordingly:

```bash
# Different browser impersonation
uvx 'scrapling[shell]' extract get 'https://example.com' "$TMPFILE" --impersonate chrome --ai-targeted

# No impersonation, no ai-targeted (raw HTML output)
uvx 'scrapling[shell]' extract get 'https://example.com' "$TMPFILE"
```

The `--ai-targeted` flag extracts only main body content, strips noise tags (`script`, `style`, `noscript`, `svg`), removes hidden elements (CSS-hidden, `aria-hidden`, `template` tags), strips zero-width unicode characters, and removes HTML comments. For browser commands (`fetch`/`stealthy-fetch`), it also automatically enables ad blocking.

## Setup

- Requires `uv` for `uvx` (ephemeral execution without persistent install)
- No pre-installation needed — `uvx 'scrapling[shell]'` handles dependency resolution automatically
- For browser-based fetchers (`fetch`, `stealthy-fetch`), a Chromium browser must be available. If not installed, run:
  ```bash
  uvx 'scrapling[shell]' install
  ```
