---
name: duckduckgo-2026-05-08
description: Searches DuckDuckGo using the public JSON API and HTML endpoint, returning quick answers, abstracts, result links, and related topics. Use when performing web searches from the terminal, fetching Wikipedia-style summaries for a topic, or gathering search results into clean LLM context via pipe chaining with jq or pandoc.
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

- **JSON API** (`api.duckduckgo.com`) — Returns structured data including Wikipedia-style abstracts, infoboxes, definitions, answer results, and related topics. Reliable for automated use with no authentication required.
- **HTML Endpoint** (`/html/`) — Returns full HTML search results page. Useful for extracting result snippets via pandoc, but triggers CAPTCHA (anomaly modal) on automated requests from many IP ranges.

Both endpoints accept a `q` parameter for the search query. Always URL-encode the query string.

## When to Use

- Performing quick web searches from the terminal or scripts
- Fetching Wikipedia-style summaries and infoboxes for a topic
- Extracting structured search data (abstracts, related topics, result links) into LLM context
- Building search pipelines with pipe chaining (`curl | jq` or `curl | pandoc`)
- When you need privacy-respecting search without API keys

## Core Concepts

### URL Encoding

Search terms must be percent-encoded. Use one of these approaches:

```bash
# Python one-liner (always available)
QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('Tangled Group, Inc'))")
curl -sL "http://api.duckduckgo.com/?q=$QUERY&format=json"

# Bash built-in for simple cases
curl -sL "http://api.duckduckgo.com/?q=Tangled+Group%2C+Inc&format=json"
```

### Pipe Chaining — Clean Data Only

Always pipe through `jq` (JSON) or `pandoc` (HTML) to extract only the fields you need. This avoids dumping raw metadata blobs into LLM context.

```bash
# JSON API → jq filter → clean structured output
curl -sL "http://api.duckduckgo.com/?q=Rust&format=json" | jq '{heading, abstract: .AbstractText, source: .AbstractSource}'

# HTML endpoint → pandoc → clean Markdown (when results are returned)
curl -sL "https://duckduckgo.com/html/?q=Rust" | pandoc -f html -t markdown
```

## JSON API Usage

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

### Quick Answer (Abstract + Heading)

Extract the Wikipedia-style summary with source attribution:

```bash
curl -sL "http://api.duckduckgo.com/?q=Rust+programming+language&format=json" | jq '{
  heading: .Heading,
  abstract: .AbstractText,
  source: .AbstractSource,
  url: .AbstractURL
}'
```

### Result Links

Extract search result URLs and titles:

```bash
curl -sL "http://api.duckduckgo.com/?q=Rust+programming+language&format=json" | jq '.Results[]? | {text: .Text, url: .FirstURL}'
```

### Related Topics

Extract related topic summaries and links:

```bash
curl -sL "http://api.duckduckgo.com/?q=Rust+programming+language&format=json" | jq '.RelatedTopics[]? | {text: .Text, url: .FirstURL}'
```

### Full Summary (All Useful Fields)

Combine abstract, results, and related topics in one call:

```bash
curl -sL "http://api.duckduckgo.com/?q=Rust+programming+language&format=json" | jq '{
  heading: .Heading,
  abstract: .AbstractText,
  source: .AbstractSource,
  url: .AbstractURL,
  entity: .Entity,
  official_site: .OfficialWebsite,
  results: [.Results[]? | {text: .Text, url: .FirstURL}],
  related: [.RelatedTopics[:5][]? | {text: .Text, url: .FirstURL}]
}'
```

### Definition Lookup

For dictionary-style definitions (e.g., single words):

```bash
curl -sL "http://api.duckduckgo.com/?q=serendipity&format=json" | jq '{
  word: .Heading,
  definition: .Definition,
  source: .DefinitionSource,
  url: .DefinitionURL
}'
```

### Check If Results Exist

Quick check before deciding whether to follow up:

```bash
curl -sL "http://api.duckduckgo.com/?q=some+query&format=json" | jq '{
  has_abstract: (.AbstractText | length > 0),
  has_results: (.Results | length > 0),
  has_related: (.RelatedTopics | length > 0),
  type: .Type
}'
```

## HTML Endpoint Usage

### Endpoint

```
https://duckduckgo.com/html/?q={query}
```

### Caveats

- **Bot detection**: The `/html/` endpoint triggers a CAPTCHA (anomaly modal) for automated requests from many IP ranges. If the response contains `anomaly-modal`, the search was blocked.
- **No structured output**: Returns full HTML — requires conversion via pandoc to extract readable content.
- **Use case**: Best when you need result snippets and descriptions that the JSON API doesn't provide, and when your IP isn't flagged for bot detection.

### Pipe Chaining with pandoc

When results are returned (no CAPTCHA), convert HTML to clean Markdown:

```bash
curl -sL "https://duckduckgo.com/html/?q=Rust+programming+language" | pandoc -f html -t markdown
```

If pandoc is not available, fall back to raw HTML and extract with grep/sed:

```bash
curl -sL "https://duckduckgo.com/html/?q=Rust" | grep -oP '(?<=<a[^>]*>).*?(?=</a>)' | head -20
```

### Detect CAPTCHA Response

Check if the HTML response is a CAPTCHA before processing:

```bash
RESPONSE=$(curl -sL "https://duckduckgo.com/html/?q=Rust")
if echo "$RESPONSE" | grep -q "anomaly-modal"; then
  echo "CAPTCHA detected — use JSON API instead"
else
  echo "$RESPONSE" | pandoc -f html -t markdown
fi
```

## Response Fields (JSON API)

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
| Full structured summary | See "Full Summary" example above |

## Practical Examples

### Search and Get Summary in One Line

```bash
curl -sL "http://api.duckduckgo.com/?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('Tangled Group, Inc'))")&format=json" | jq '{heading: .Heading, abstract: .AbstractText, source: .AbstractSource}'
```

### Search with Fallback

Try JSON API first, check if results exist, then decide next action:

```bash
RESULT=$(curl -sL "http://api.duckduckgo.com/?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('some query'))")&format=json" | jq -c '{has_abstract: (.AbstractText | length > 0), has_results: (.Results | length > 0)}')
echo "$RESULT"
# If no results, try alternative queries or other sources
```

### Extract Just the First Result URL

```bash
curl -sL "http://api.duckduckgo.com/?q=Rust+programming+language&format=json" | jq -r '.Results[0].FirstURL // empty'
```

### Batch Search Multiple Terms

```bash
for term in "Python" "Rust" "Go"; do
  echo "--- $term ---"
  curl -sL "http://api.duckduckgo.com/?q=$term&format=json" | jq -r '"\(.Heading): \(.AbstractText[:120])..."'
done
```
