---
name: duckduckgo
description: Searches DuckDuckGo using the HTML endpoint (default, html→markdown via scrapling) and JSON API (--format json), returning clean markdown results, quick answers, abstracts, result links, and related topics. Use when performing web searches from the terminal, fetching Wikipedia-style summaries for a topic, or gathering search results into clean LLM context.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - web-search
  - web search
  - duckduckgo
category: web
external_references:
  - http://api.duckduckgo.com/
  - https://duckduckgo.com/
---

# DuckDuckGo Public APIs

## Overview

DuckDuckGo provides two public, undocumented endpoints for programmatic search:

- **HTML Endpoint** (`/html/`, default) — Returns full HTML search results page, automatically converted to clean markdown. Default format is `html` with `scrapling` backend for anti-bot evasion and native `.md` output.
- **JSON API** (`api.duckduckgo.com`) — Returns structured data including Wikipedia-style abstracts, infoboxes, definitions, answer results, and related topics. Access via `--format json`. Reliable for automated use with no authentication required.

Both endpoints accept a `q` parameter for the search query. Always URL-encode the query string.

## When to Use

- Performing quick web searches from the terminal or scripts
- Fetching Wikipedia-style summaries and infoboxes for a topic
- Extracting structured search data (abstracts, related topics, result links) into LLM context
- Building search pipelines with pipe chaining
- When you need privacy-respecting search without API keys

## Format × Backend Matrix

| Format | scrapling (default) | curl | wget |
|--------|-----------|------|------|
| **html / markdown** (default) | Native `.md` via `--ai-targeted` + `--css-selector '.web-result'` | Raw HTML → extract `.web-result` → pandoc → markdown | Raw HTML → extract `.web-result` → pandoc → markdown |
| **json** | Falls back to curl/wget (scrapling breaks JSON) | Raw JSON as-is | Raw JSON as-is |

- **html / markdown** (default): Scrapling provides native `.md` output with anti-bot evasion and `--css-selector '.web-result'` for targeted extraction. curl/wget fetch raw HTML, extract only `.web-result` elements via python3 html.parser, then convert to markdown via pandoc.
- **json**: Always uses curl or wget. Scrapling transforms content and breaks JSON parsing.
- `--pretty` flag prettifies JSON output through `jq .`.

## Scripts

All paths are relative to this skill's directory (where SKILL.md lives).

### Fetch Backends

Three HTTP backends are supported. Scrapling is the default for anti-bot evasion and native markdown output:

| Priority | Backend | Best For | Requires |
|----------|---------|----------|----------|
| 1 (default) | **scrapling** | Anti-bot evasion, JS rendering, native `.md` output | `uvx` |
| 2 | **curl** | Fast, reliable fetching with enhanced browser headers | `curl` |
| 3 | **wget** | Fallback when curl is unavailable | `wget` |

### ddg-search.sh — Standalone CLI (Execute)

Run `ddg-search.sh` to search DuckDuckGo and get filtered output. This is the primary entry point.

```bash
# Default: HTML → markdown via scrapling (no command arg needed)
bash scripts/ddg-search.sh "Rust programming language"

# JSON API commands (use --format json)
bash scripts/ddg-search.sh "Rust" summary --format json
bash scripts/ddg-search.sh "Rust" results --format json --limit 5
bash scripts/ddg-search.sh "Rust" related --format json --limit 3
bash scripts/ddg-search.sh "serendipity" definition --format json
bash scripts/ddg-search.sh "Tangled Group, Inc" full --format json
bash scripts/ddg-search.sh "some query" check --format json

# Pretty-printed JSON
bash scripts/ddg-search.sh "AI agents" full --format json --pretty

# Force a specific backend for HTML→markdown
bash scripts/ddg-search.sh "Rust" --backend curl
bash scripts/ddg-search.sh "Rust" --backend wget

# With language variant
bash scripts/ddg-search.sh "Rust" summary --format json --lang en-us
```

**Commands:** `html` (default), `summary`, `results`, `related`, `definition`, `full`, `check`

**Options:** `--limit N`, `--lang CODE`, `--timeout SEC`, `--backend B`, `--format F`, `--pretty`, `--help`

**Backends:** `scrapling` (default), `auto`, `curl`, `wget`

**Formats:** `html` (default), `json`, `markdown`

### ddg-utils.sh — Utility Library

Source `ddg-utils.sh` when you need individual functions inside your own scripts. Provides URL builders, multi-backend fetching, format conversion, and jq filters. See the full reference for available functions and usage examples → [ddg-utils.sh](reference/01-ddg-utils.md)

## Advanced Topics

**Utility Library**: Functions for URL building, fetching, and JSON filtering → [ddg-utils.sh](reference/01-ddg-utils.md)

**Configurable Constants**: Environment variables for customizing behavior → [Configurable Constants](reference/02-configurable-constants.md)

**JSON API**: Endpoint details, query parameters, response fields, jq selectors → [JSON API](reference/03-json-api.md)

**HTML Endpoint**: Bot detection caveats, scrapling/curl/wget backends, CAPTCHA handling → [HTML Endpoint](reference/04-html-endpoint.md)

**Examples**: Self-contained scripts for common search patterns → [Examples](reference/05-examples.md)
