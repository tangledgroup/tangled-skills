---
name: duckduckgo-2026-05-08
description: Searches DuckDuckGo using the HTML endpoint (default, html→markdown via scrapling) and JSON API (--format json), returning clean markdown results, quick answers, abstracts, result links, and related topics. Use when performing web searches from the terminal, fetching Wikipedia-style summaries for a topic, or gathering search results into clean LLM context.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2026-05-08"
tags:
  - duckduckgo
  - search
  - web-search
  - curl
  - jq
  - information-retrieval
category: cli-tool
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
| **html / markdown** (default) | Native `.md` via `--ai-targeted` | Raw HTML → pandoc → markdown | Raw HTML → pandoc → markdown |
| **json** | Falls back to curl/wget (scrapling breaks JSON) | Raw JSON as-is | Raw JSON as-is |

- **html / markdown** (default): Scrapling provides native `.md` output with anti-bot evasion. curl/wget fetch raw HTML then convert via pandoc.
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

### ddg-utils.sh — Utility Library (Source)

Source `ddg-utils.sh` when you need individual functions inside your own scripts or inline workflows. Provides URL builders, multi-backend fetching, format conversion, and jq filters.

```bash
# Source the library
source scripts/ddg-utils.sh

# Build URLs (output to stdout, capture in variable)
JSON_URL=$(ddg_json_url "Rust programming")
HTML_URL=$(ddg_html_url "Rust programming")

# Convenience fetchers (auto-select backend)
RAW_JSON=$(ddg_fetch_json "Rust programming")     # curl/wget only, returns JSON
RAW_MD=$(ddg_fetch_html "Rust programming")        # scrapling→md or curl/wget→pandoc→md

# Format conversion (read HTML from stdin, output markdown)
echo "<h1>Hello</h1>" | ddg_convert_html_to_md

# Low-level backend fetchers (read URL, output raw body)
BODY=$(ddg_scrapling_fetch "$HTML_URL")            # anti-bot, JS rendering → markdown
BODY=$(ddg_curl_fetch "$JSON_URL")                  # enhanced browser headers → raw body
BODY=$(ddg_wget_fetch "$HTML_URL")                  # fallback → raw body

# Filter JSON from stdin (pipe JSON into these functions)
echo "$RAW_JSON" | ddg_summary
echo "$RAW_JSON" | ddg_results 5
echo "$RAW_JSON" | ddg_related 3
echo "$RAW_JSON" | ddg_definition
echo "$RAW_JSON" | ddg_full 5
echo "$RAW_JSON" | ddg_check
```

**Available functions:**

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `ddg_encode_query <q>` | URL-encode query string | query text | encoded string |
| `ddg_json_url <q> [opts]` | Build JSON API URL | query + optional params | full URL |
| `ddg_html_url <q>` | Build HTML endpoint URL | query text | full URL |
| `ddg_http_fetch <url>` | Auto-detect and fetch | URL | raw body |
| `ddg_scrapling_fetch <url>` | Fetch via scrapling | URL | markdown (.md) |
| `ddg_curl_fetch <url>` | Fetch via curl (enhanced headers) | URL | raw body |
| `ddg_wget_fetch <url>` | Fetch via wget | URL | raw body |
| `ddg_convert_html_to_md` | Convert HTML stdin → markdown | stdin HTML | markdown |
| `ddg_fetch_json <q> [opts]` | Fetch JSON API response | query + params | raw JSON |
| `ddg_fetch_html <q>` | Fetch HTML → markdown | query text | markdown |
| `ddg_summary` | Extract heading + abstract | stdin JSON | filtered JSON |
| `ddg_results [N]` | Extract result links | stdin JSON | JSON array |
| `ddg_related [N]` | Extract related topics | stdin JSON | JSON array |
| `ddg_definition` | Extract dictionary definition | stdin JSON | filtered JSON |
| `ddg_full [N]` | Full structured summary | stdin JSON | pretty JSON |
| `ddg_check` | Check result existence | stdin JSON | boolean flags |

### Configurable Constants

Set these environment variables before sourcing or running scripts:

```bash
DDG_JSON_BASE=http://api.duckduckgo.com/   # JSON API base URL (default)
DDG_HTML_BASE=https://duckduckgo.com/html/  # HTML endpoint base URL (default)
DDG_TIMEOUT=15                              # Fetch timeout in seconds (default)
DDG_HTTP_BACKEND=scrapling                  # Force backend: scrapling (default), auto, curl, wget
DDG_OUTPUT_FORMAT=html                      # Output format: html (default), json, markdown
DDG_PRETTY_JSON=0                           # Prettify JSON via jq (1 = yes)
```

## JSON API

### Endpoint

```
http://api.duckduckgo.com/?q={query}&format=json
```

### Query Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL-encoded) |
| `format` | Output format — `json` or `js` (JSONP) |
| `no_redirect` | Set to `1` to prevent auto-redirect on exact matches |
| `skip_disambig` | Set to `1` to skip disambiguation pages |
| `dl` | Language variant: `en-us`, `zh-cn`, etc. |
| `ka` | Set to `w` for Wikipedia-style answer box |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `Heading` | string | Title of the matched entity |
| `AbstractText` | string | Wikipedia-style summary paragraph |
| `AbstractSource` | string | Source name (e.g., "Wikipedia") |
| `AbstractURL` | string | URL to the source article |
| `Answer` | string | Direct answer for math, conversion, etc. |
| `AnswerType` | string | Type of direct answer |
| `Definition` | string | Dictionary definition (for word queries) |
| `DefinitionSource` | string | Source of the definition |
| `DefinitionURL` | string | URL to the dictionary entry |
| `Entity` | string | Entity type classification |
| `Image` | string | Relative URL to entity image/logo |
| `Infobox` | object | Structured data table (Wikipedia infobox) |
| `OfficialDomain` | string | Official domain of the entity |
| `OfficialWebsite` | string | Full official website URL |
| `Redirect` | string | Redirect target if query was disambiguated |
| `Results` | array | Search result links with text and URLs |
| `RelatedTopics` | array | Related topics with summaries and links |
| `Type` | string | Result type: `A` (abstract), `D` (definition), `R` (results), or empty |

### Recommended jq Selectors by Use Case

| Use Case | jq Filter |
|----------|-----------|
| Quick summary | `{heading: .Heading, abstract: .AbstractText}` |
| With source attribution | `{heading: .Heading, abstract: .AbstractText, source: .AbstractSource, url: .AbstractURL}` |
| Result links only | `.Results[]? \| {text: .Text, url: .FirstURL}` |
| Related topics (top 5) | `.RelatedTopics[:5][]? \| {text: .Text, url: .FirstURL}` |
| Dictionary definition | `{word: .Heading, definition: .Definition, source: .DefinitionSource}` |

## HTML Endpoint

### Endpoint

```
https://duckduckgo.com/html/?q={query}
```

### Caveats

- **Bot detection**: The `/html/` endpoint triggers a CAPTCHA (anomaly modal) for automated requests from many IP ranges. If the response contains `anomaly-modal`, the search was blocked.
- **Format conversion**: HTML output is automatically converted to markdown via scrapling (native `.md`) or pandoc (for curl/wget backends).
- **Use case**: Best when you need result snippets and descriptions that the JSON API doesn't provide.

### HTML Search with scrapling (Default)

Run `assets/example-scrapling-search.sh` to fetch HTML results using scrapling's anti-bot backend (default):

```bash
bash assets/example-scrapling-search.sh "Rust programming language"
```

Or via the CLI (scrapling + html are both defaults):

```bash
bash scripts/ddg-search.sh "Rust"
```

Scrapling impersonates Safari, handles JS rendering, and outputs clean markdown natively — no pandoc needed.

### HTML Search with curl or wget (Fallback)

When scrapling is unavailable, use curl or wget with automatic pandoc conversion:

```bash
# Curl fetches raw HTML, automatically converted to markdown via pandoc
bash scripts/ddg-search.sh "Rust" --backend curl

# Wget fallback
bash scripts/ddg-search.sh "Rust" --backend wget
```

If pandoc is not installed, a warning is printed to stderr and raw HTML is returned instead.

### Detect CAPTCHA Response

Run `assets/example-captcha-detect.sh` to test if your IP is being blocked:

```bash
bash assets/example-captcha-detect.sh "test query"
```

Exit code 0 = clean, exit code 1 = blocked. When blocked, use the JSON API instead.

## Advanced Topics

**Search Examples**: Self-contained scripts for common search patterns → [Examples](assets/)
- `assets/example-quick-search.sh` — Single query summary
- `assets/example-batch-search.sh` — Multiple terms at once
- `assets/example-with-fallback.sh` — Search with existence check and conditional output
- `assets/example-html-search.sh` — HTML endpoint → markdown (auto backend)
- `assets/example-scrapling-search.sh` — Anti-bot HTML search using scrapling
- `assets/example-captcha-detect.sh` — Test if HTML endpoint is blocked
- `assets/example-json-pretty.sh` — Pretty-printed JSON output
