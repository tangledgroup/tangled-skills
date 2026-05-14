---
name: duckduckgo
description: Searches DuckDuckGo via its HTML endpoint using scrapling. Returns results as markdown (default), raw HTML, compact JSON, or YAML. Use when performing web searches from within an agent workflow without requiring a search API key or external service.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.2.0"
tags:
  - duckduckgo
  - search
  - web-search
  - scrapling
  - scraping
category: web
external_references:
  - https://html.duckduckgo.com/html/
---

# DuckDuckGo Search

## Overview

Searches DuckDuckGo via its HTML endpoint (`html.duckduckgo.com/html/`) using `scrapling` for fetching and parsing. Supports four output formats — all sourced from the same HTML API:

- **Markdown** (default) — clean, AI-targeted markdown from scrapling
- **HTML** — raw `.web-result` HTML elements
- **JSON** — compact array of `{title, url, domain, snippet}` objects
- **YAML** — structured list of result mappings

No API key or external search service required. Uses `uvx 'scrapling[shell]'` for ephemeral execution.

## When to Use

- Performing web searches from within an agent workflow
- Gathering search result snippets, titles, and URLs programmatically
- Research tasks that need structured search output (JSON/YAML) for downstream processing
- Situations where Google/Bing APIs are unavailable or require authentication

## Usage Examples

### Markdown (default)

Run `search.sh` with a query — no format flag needed:

```bash
bash scripts/search.sh "tangled group"
```

Output is clean markdown produced by scrapling's `--ai-targeted` mode, streamed directly to stdout.

### HTML

Request raw HTML when you need the full DOM structure:

```bash
bash scripts/search.sh "tangled group" --format html
```

Returns `.web-result` divs with all CSS classes, links, and snippets intact.

### JSON

Get compact JSON for programmatic processing:

```bash
bash scripts/search.sh "tangled group" --format json
```

Output:

```json
[{"title":"Tangled Group, Inc.","url":"https://tangledgroup.com/","domain":"tangledgroup.com","snippet":"We are a software development company..."},...]
```

Each result object contains only fields present in the HTML: `title`, `url`, `domain`, `snippet`. Missing fields are omitted.

### YAML

Get structured YAML output:

```bash
bash scripts/search.sh "tangled group" --format yaml
```

Output:

```yaml
- title: 'Tangled Group, Inc.'
  url: 'https://tangledgroup.com/'
  domain: 'tangledgroup.com'
  snippet: |
    We are a software development company...
```

## Core Concepts

### Output Pipeline

All four formats use the same source — DuckDuckGo's HTML endpoint:

1. `search.sh` constructs the URL: `https://html.duckduckgo.com/html/?q=<encoded-query>`
2. `uvx 'scrapling[shell]' extract get` fetches and isolates `.web-result` elements
3. For **markdown/json/yaml**: scrapling's `--ai-targeted` flag produces clean, AI-friendly output
4. For **html**: raw HTML passed through without `--ai-targeted` to preserve original DOM structure
5. For **json/yaml**: HTML saved to a temp file, then `format.py` parses it using Python's built-in `html.parser`

### Temp File Handling

All formats create temporary files in `/tmp/` using `mktemp` with PID-based prefixes (`ddg-search-${$}-XXXXXX`) to ensure uniqueness under parallel execution. Files are automatically cleaned up on exit via a bash `trap` handler (covers normal exit, SIGINT, SIGTERM).

### Query Encoding

Query is passed to Python via stdin (not shell argument expansion) to prevent shell injection. `urllib.parse.quote` URL-encodes the query. Multi-word queries are handled correctly — `"tangled group"` becomes `tangled%20group`.

### Dependencies

- **bash** — shell scripting
- **uvx** — ephemeral Python package execution (runs `scrapling[shell]`)
- **python3** — query encoding and HTML-to-JSON/YAML formatting (builtins only: `html.parser`, `json`, `sys`, `urllib.parse`, `re`)
