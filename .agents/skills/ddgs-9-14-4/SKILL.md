---
name: ddgs-9-14-4
description: Metasearch library aggregating results from 10+ web search services (Google, Bing, DuckDuckGo, Brave, Yahoo, Yandex, Wikipedia, Startpage, Mojeek, Grokipedia). Provides text, image, video, news, and book search plus URL content extraction. Use when searching the web, finding images/videos/news, extracting page content, or running a local search API server without API keys.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ddgs
  - search
  - metasearch
  - websearch
  - duckduckgo
  - google
  - bing
category: networking
external_references:
  - https://github.com/deedy5/ddgs/tree/v9.14.4
  - https://pypi.org/project/ddgs/
---

# DDGS 9.14.4 — Dux Distributed Global Search

## Overview

DDGS is a Python metasearch library that aggregates results from diverse web search services through a single unified API. It supports **5 search categories** (text, images, videos, news, books) across **10+ backends**, with optional API server, MCP server, and DHT peer-to-peer cache network.

Requires **Python 3.10+**. Base install has zero external API keys needed.

## When to Use

- Web text search across multiple engines (Google, Bing, DuckDuckGo, Brave, Yahoo, Yandex, Wikipedia, Startpage, Mojeek, Grokipedia)
- Image search with filters (size, color, type, layout, license)
- Video search with resolution/duration/license filters
- News search with time-based filtering
- Book search via Anna's Archive
- URL content extraction (Markdown, plain text, rich text, raw HTML, bytes)
- Running a local REST API server for search (FastAPI, port 4479)
- Integrating as an MCP server tool for AI agents

## Core Concepts

### DDGS Class

The `DDGS` class is **lazy-loaded** (imported via metaclass proxy). It accepts `proxy`, `timeout`, and `verify` arguments in the constructor. All search methods return `list[dict[str, str]]`.

```python
from ddgs import DDGS

results = DDGS().text("python programming", max_results=5)
```

### Search Engines

Each search category has dedicated backends. The `backend` parameter selects which engine to use (`"auto"` tries all available). Results are deduplicated and ranked by a built-in aggregator.

| Method | Available backends |
|--------|-------------------|
| `text()` | `bing`, `brave`, `duckduckgo`, `google`, `grokipedia`, `mojeek`, `startpage`, `yandex`, `yahoo`, `wikipedia` |
| `images()` | `bing`, `duckduckgo` |
| `videos()` | `duckduckgo` |
| `news()` | `bing`, `duckduckgo`, `yahoo` |
| `books()` | `annasarchive` |

### DDGS Class Constructor

```python
DDGS(proxy: str | None = None, timeout: int = 5, verify: bool | str = True)
```

- `proxy` — HTTP proxy URL (`http://user:pass@host:port`, `socks5h://...`)
- `timeout` — HTTP request timeout in seconds (default: 5)
- `verify` — SSL verification: `True` (verify), `False` (skip), or path to PEM file

### Common Parameters

All search methods share these parameters unless noted:

- `query` (str, required) — Search query string
- `region` (str) — Region code like `us-en`, `uk-en`, `ru-ru`. Default: `"us-en"`
- `safesearch` (str) — `"on"`, `"moderate"`, `"off"`. Default: `"moderate"`
- `timelimit` (str \| None) — Time filter: `"d"` (day), `"w"` (week), `"m"` (month), `"y"` (year). Default: `None`
- `max_results` (int \| None) — Maximum results to return. Default: `10`
- `page` (int) — Result page number. Default: `1`
- `backend` (str) — Engine name or `"auto"`. Default: `"auto"`

## Usage Examples

### Text Search

```python
from ddgs import DDGS

# Basic search
results = DDGS().text("live free or die", region="us-en", safesearch="off")
for r in results:
    print(r["title"], r["href"])

# Search with time limit and specific backend
results = DDGS().text("python tutorial", timelimit="m", backend="google")

# Filetype search
results = DDGS().text("russia filetype:pdf", safesearch="off", timelimit="y")
```

Each result is a dict with `title`, `href`, `body` keys.

### Image Search

```python
from ddgs import DDGS

results = DDGS().images(
    query="butterfly",
    region="us-en",
    safesearch="off",
    timelimit="m",
    size="Large",
    color="Monochrome",
    license_image="Public",
)
for r in results:
    print(r["title"], r["image"], f"{r['width']}x{r['height']}", r["source"])
```

Image result keys: `title`, `image`, `thumbnail`, `url`, `height`, `width`, `source`.

Additional filters: `size` (Small/Medium/Large/Wallpaper), `color`, `type_image` (photo/clipart/gif/transparent/line), `layout` (Square/Tall/Wide), `license_image` (any/Public/Share/ShareCommercially/Modify/ModifyCommercially).

### Video Search

```python
from ddgs import DDGS

results = DDGS().videos(
    query="tutorial",
    resolution="high",
    duration="short",
)
for r in results:
    print(r["title"], r["content"], r["duration"])
```

Video result keys include `title`, `content` (watch URL), `description`, `duration`, `embed_html`, `embed_url`, `images` (large/medium/motion/small dict), `provider`, `published`, `publisher`, `statistics` (viewCount), `uploader`.

### News Search

```python
from ddgs import DDGS

results = DDGS().news("technology", timelimit="d", backend="bing")
for r in results:
    print(r["date"], r["title"], r["url"])
```

News result keys: `date`, `title`, `body`, `url`, `image`, `source`.

### Book Search

```python
from ddgs import DDGS

results = DDGS().books("sea wolf jack london")
for r in results:
    print(r["title"], r["author"], r["publisher"])
```

Book result keys: `title`, `author`, `publisher`, `info`, `url`, `thumbnail`.

### URL Content Extraction

```python
from ddgs import DDGS

# Markdown output (default)
result = DDGS().extract("https://example.com")
print(result["content"])  # Markdown text

# Plain text
result = DDGS().extract("https://example.com", fmt="text_plain")

# Raw HTML
result = DDGS().extract("https://example.com", fmt="text")

# Raw bytes
result = DDGS().extract("https://example.com", fmt="content")
```

Output formats: `text_markdown` (default), `text_plain`, `text_rich`, `text`, `content`.

### CLI Usage

```bash
# Text search
ddgs text -q "python" --max-results 5

# Image search
ddgs images -q "cats"

# News with time limit
ddgs news -q "tech" --timelimit d

# Save to JSON
ddgs text -q "dogs" -o results.json --format json

# Save to CSV
ddgs text -q "dogs" -o results.csv --format csv

# Extract URL content
ddgs extract -u https://example.com
ddgs extract -u https://example.com -f text_plain
```

## Installation

```bash
pip install -U ddgs       # Base install (text, images, videos, news, books, extract)
pip install -U ddgs[api]  # + API server (FastAPI)
pip install -U ddgs[mcp]  # + MCP server (stdio transport)
pip install -U ddgs[dht]  # + DHT peer-to-peer cache network
```

Base dependencies: `click`, `primp`, `lxml`, `httpx[http2,socks,brotli]`, `fake-useragent`.

## API Server

Start a FastAPI server on port 4479 (requires `ddgs[api]`):

```bash
ddgs api              # Start in foreground
ddgs api -d           # Start detached (background)
ddgs api -s           # Stop detached server
ddgs api --host 127.0.0.1 --port 4479
ddgs api -pr socks5h://127.0.0.1:9150  # With proxy
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search/text` | GET, POST | Text search |
| `/search/images` | GET, POST | Image search |
| `/search/news` | GET, POST | News search |
| `/search/videos` | GET, POST | Video search |
| `/search/books` | GET, POST | Book search |
| `/extract` | GET, POST | Extract content from URL |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc documentation |

### Docker Compose

```bash
git clone https://github.com/deedy5/ddgs && cd ddgs
docker-compose up --build
```

## MCP Server

Requires `ddgs[mcp]`. Starts an MCP server via stdio transport:

```bash
ddgs mcp              # Start MCP server
ddgs mcp -pr socks5h://127.0.0.1:9150  # With proxy
```

### Available Tools

| Tool | Description |
|------|-------------|
| `search_text` | Web text search |
| `search_images` | Image search |
| `search_news` | News search |
| `search_videos` | Video search |
| `search_books` | Book search |
| `extract_content` | Extract content from a URL |

### Client Configuration

For MCP clients (Cursor, Claude Desktop):

```json
{
  "mcpServers": {
    "ddgs": {
      "command": "ddgs",
      "args": ["mcp"]
    }
  }
}
```

## DHT Network (BETA)

Optional peer-to-peer distributed cache. Results are shared anonymously between users, reducing rate limits and latency. **90% faster** repeated queries (50ms vs 1-2s).

```bash
pip install -U ddgs[dht]
# macOS: brew install gmp first
```

When running `ddgs api`, the node automatically participates in the network. All search methods transparently check the DHT cache first, then fall back to live search.

DHT adds these API endpoints (requires `ddgs[api]`):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dht/cache` | GET/POST/DELETE | Cache management |
| `/dht/status` | GET | Service status and metrics |
| `/dht/peers` | GET | Connected peers list |
| `/dht/map` | GET | Network graph view |
| `/dht/metrics` | GET | Prometheus metrics |

**Platform support**: Linux and macOS only. Windows not supported.

## Advanced Topics

**Search Engine Architecture**: Deep dive into `BaseSearchEngine`, engine registration, result aggregation, and adding custom backends → [Reference: Engine Architecture](reference/01-engine-architecture.md)

**DHT Network Details**: Peer discovery, cache propagation, network topology, and performance characteristics → [Reference: DHT Network](reference/02-dht-network.md)

## CLI Reference

Full CLI command reference with all options:

```bash
ddgs --help
ddgs text --help
ddgs images --help
ddgs api --help
ddgs mcp --help
ddgs extract --help
```

CLI supports `--format json` / `--format csv` for output, `-o` for file output, `--no-color` to disable terminal colors, and `-pr` for proxy configuration.
