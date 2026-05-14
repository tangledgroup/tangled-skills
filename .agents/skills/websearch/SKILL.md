---
name: websearch
description: Searches DuckDuckGo via its HTML endpoint and outputs results as raw YAML. Uses a deterministic bash script that always hits `html.duckduckgo.com/html`, extracts search results, and prints exact YAML output.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.2.0"
tags:
  - websearch
  - web-search
  - duckduckgo
  - yaml-output
  - scrapling
  - scraping
category: meta
external_references:
  - https://html.duckduckgo.com/html/
---

# Web Search — DuckDuckGo to YAML

## Overview

Searches DuckDuckGo via its HTML endpoint (`html.duckduckgo.com/html/`) and outputs results as raw YAML. Final output of skill is complete YAML shown to the user **exactly as produced — never summarized, never transformed**.

A deterministic bash script handles all search execution — the agent always runs `bash scripts/search.sh <query>` and never constructs commands on the fly. This ensures consistent behavior and prevents command-generation errors.

No API key or external service required. Uses `uvx 'scrapling[shell]'` for ephemeral execution — no persistent installs.

## When to Use

- Performing web searches from within an agent workflow
- Gathering titles, URLs, and snippets as structured YAML
- Research tasks that need exact web search results shown to the user
- Web search and show results as original YAML **exactly as produced — never summarized, never transformed**

### API Limitations

DuckDuckGo's HTML endpoint has inherent limitations:

- **First page only** — only the top ~10 results are returned
- **No pagination** — there are no additional pages or "next page" links
- **Top results only** — deeper results are not accessible via this endpoint
- **These are the only results available** — do not attempt to fetch more pages or suggest that more results exist

If more results are needed, reformulate the query with different keywords rather than attempting pagination.

## Usage Examples

### Basic Search

Run `search.sh` with a query:

```bash
bash scripts/search.sh "tangled group"
```

The script output is shown to the user exactly as produced — raw YAML:

```yaml
- title: 'Tangled Group, Inc.'
  url: 'https://tangledgroup.com/'
  domain: 'tangledgroup.com'
  snippet: |
    We are a software development company...

- title: 'Tangled Group - LinkedIn'
  url: 'https://www.linkedin.com/company/tangled-group'
  domain: 'linkedin.com'
  snippet: |
    Software engineering services and consulting...
```

## Core Concepts

### Deterministic Script Execution

The agent always runs `bash scripts/search.sh <query>` — it never constructs `uvx` or `scrapling` commands on the fly. This ensures:

- **Consistent endpoint**: Always uses DuckDuckGo's HTML endpoint
- **No command errors**: No risk of malformed `uvx` invocations
- **Exact output**: Script output is shown to the user as-is, never summarized or transformed
- **Clean output**: No scrapling INFO logs or delimiter noise

### YAML Output Format

The script output is shown to the user exactly as produced — no changes, no summarization. Each result in the YAML list contains these fields (only present if available in the HTML):

- title
- url
- domain
- snippet

### Dependencies

- **bash** — shell scripting
- **uvx** — ephemeral Python package execution (runs `scrapling[shell]`)
- **python3** — query encoding and HTML-to-YAML formatting (builtins only: `html.parser`, `re`, `sys`, `urllib.parse`)
