---
name: webfetch
description: Fetches any URL and converts the full page to clean AI-targeted markdown using scrapling. Use when scraping arbitrary web pages, documentation, articles, or HTML content into a format suitable for AI context without requiring an API key.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.2.0"
tags:
  - webfetch
  - web-scraping
  - url-fetch
  - markdown
  - scrapling
  - ai-targeted
category: meta
external_references:
  - https://scrapling.io/
---

# Web Fetch — URL to Markdown

## Overview

Fetches any URL and converts the full page to clean AI-targeted markdown using `scrapling[shell]`'s `--ai-targeted` mode. The output is readable markdown optimized for AI context — no raw HTML, no noise.

A deterministic bash script handles all fetch execution — the agent always runs `bash scripts/fetch.sh <URL>` and never constructs commands on the fly. This ensures consistent behavior and prevents command-generation errors.

No API key or external service required. Uses `uvx 'scrapling[shell]'` for ephemeral execution — no persistent installs.

## When to Use

- Scraping arbitrary web pages into AI-readable markdown
- Fetching documentation, articles, or blog posts for context
- Converting HTML content to clean markdown without an API key
- Extracting page content from any public URL

## Usage

### Basic Fetch

Run `fetch.sh` with a URL:

```bash
bash scripts/fetch.sh <URL>
```

### Fetch to Specific Path

Use `--output` to save to a specific location:

```bash
bash scripts/fetch.sh <URL> --output ./output.md
```

The file persists at the specified path (not auto-deleted).

### Error Handling

If the URL cannot be reached, the script reports the error and exits non-zero:

```
Error: Failed to fetch URL: https://example.com
```

The script does not attempt to guess or correct URLs — it reports the fetch failure as-is.

## Core Concepts

### Deterministic Script Execution

The agent always runs `bash scripts/fetch.sh <URL>` — it never constructs `uvx` or `scrapling` commands on the fly. This ensures:

- **Consistent execution**: Always uses scrapling with correct flags
- **No command errors**: No risk of malformed `uvx` invocations
- **Clean output**: AI-targeted markdown, no raw HTML or noise
- **Temp file output**: Output saved to randomized temp file, path printed to stdout

### URL Validation

The script requires URLs to start with `http://` or `https://`. Missing schemes are rejected with a clear error message. If a URL cannot be fetched, the script reports the error without attempting to guess or correct it.

### Dependencies

- **bash** — shell scripting
- **uvx** — ephemeral Python package execution (runs `scrapling[shell]`)
