# ddg-utils.sh — Utility Library

## Contents
- Overview
- Usage
- Available Functions

## Overview

`ddg-utils.sh` is a sourceable utility library that provides individual functions for DuckDuckGo search operations. Source it when you need URL builders, multi-backend fetching, format conversion, or jq filters inside your own scripts or inline workflows.

**Execution intent**: **Read as reference** — source the library in your own bash sessions or scripts to access its functions.

```bash
source scripts/ddg-utils.sh
```

## Usage

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

## Available Functions

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
