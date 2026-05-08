---
name: scrapling-0-4-7
description: Web scraping tool that converts web pages to Markdown using Scrapling v0.4.7's CLI. Use when extracting content from URLs, converting web pages to readable Markdown for AI context or documentation, scraping JS-rendered pages with browser automation, or bypassing anti-bot protections with stealthy fetching.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.2"
tags:
  - web-search
  - web scrape
  - web scraping
  - browser automation
category: web
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

Use `scripts/scrape.sh` (Execute) — a wrapper that handles the temp-file workflow automatically (creates `.md` temp file, runs scrapling, outputs to stdout, cleans up):

```bash
bash scripts/scrape.sh 'https://example.com'
```

When saving to a specific file:

```bash
bash scripts/scrape.sh -o '/path/to/output.md' 'https://example.com'
```

## Fetch Modes

Three fetch modes are available. Default is `get` when no mode is specified.

### get (alias: simple-fetch)

Plain HTTP request. Fastest option, works for static pages. Default flags: `--impersonate safari --ai-targeted`.

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

Common options:
- `--solve-cloudflare` — Solve Cloudflare challenges automatically
- `--block-webrtc` — Block WebRTC to prevent IP leaks
- `--hide-canvas` — Add noise to canvas operations for fingerprint resistance
- `--proxy TEXT` — Proxy URL
- `--dns-over-https` — Route DNS through Cloudflare DoH to prevent DNS leaks
- `-s, --css-selector TEXT` — Extract specific content via CSS selector
- `--ai-targeted` — Extract only main content, strip noise for AI consumption (default: on)

## CLI Usage

The `scripts/scrape.sh` script (Execute) wraps the `uvx 'scrapling[shell]'` CLI, handling temp-file creation, output, and cleanup automatically. Paths are relative to this skill's directory.

```bash
# Default: URL only → Markdown to stdout (get mode, --ai-targeted, --impersonate safari)
bash scripts/scrape.sh 'https://example.com'

# Save to file instead of stdout
bash scripts/scrape.sh -o './notes/example.md' 'https://example.com'

# Extract with CSS selector
bash scripts/scrape.sh -s 'article' 'https://blog.example.com'

# JavaScript-rendered page (fetch mode)
bash scripts/scrape.sh --mode fetch 'https://app.example.com'

# Anti-bot bypass (stealthy mode)
bash scripts/scrape.sh --mode stealthy 'https://protected.example.com'

# Pass extra flags for mode-specific options
bash scripts/scrape.sh --mode fetch --extra '--network-idle' 'https://app.example.com'
bash scripts/scrape.sh --mode stealthy --extra '--solve-cloudflare' 'https://protected.example.com'

# Override defaults: different browser, no ai-targeted
bash scripts/scrape.sh --impersonate chrome 'https://example.com'
bash scripts/scrape.sh --no-ai-targeted 'https://example.com'
```

**Script options:**
| Flag | Description |
|------|-------------|
| `--mode get\|fetch\|stealthy` | Fetch mode (default: `get`) |
| `-s, --css-selector TEXT` | Extract specific content via CSS selector |
| `-o, --output FILE` | Save to file instead of stdout |
| `--impersonate BROWSER` | Browser headers: `safari` (default), `chrome`, `firefox`. Only for `get` mode. |
| `--ai-targeted` | Strip noise for AI consumption (default: on) |
| `--no-ai-targeted` | Disable ai-targeted output |
| `--extra 'FLAGS'` | Pass extra flags directly to scrapling (e.g., `--network-idle`, `--solve-cloudflare`) |

The `--ai-targeted` flag extracts only main body content, strips noise tags (`script`, `style`, `noscript`, `svg`), removes hidden elements (CSS-hidden, `aria-hidden`, `template` tags), strips zero-width unicode characters, and removes HTML comments. For browser commands (`fetch`/`stealthy-fetch`), it also automatically enables ad blocking.

## Setup

- Requires `uv` for `uvx` (ephemeral execution without persistent install)
- No pre-installation needed — `uvx 'scrapling[shell]'` handles dependency resolution automatically
- For browser-based fetchers (`fetch`, `stealthy-fetch`), a Chromium browser must be available. If not installed, run:
  ```bash
  uvx 'scrapling[shell]' install
  ```
