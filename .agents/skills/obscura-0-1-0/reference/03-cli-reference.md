# CLI Reference

> **Source:** Obscura README.md (v0.1.0)
> **Loaded from:** SKILL.md (via progressive disclosure)

Obscura provides two binaries: `obscura` (main CLI) and `obscura-worker` (parallel scraping workers).

## `obscura serve`

Start a CDP WebSocket server for Puppeteer/Playwright connections.

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `9222` | WebSocket port |
| `--proxy` | — | HTTP/SOCKS5 proxy URL |
| `--stealth` | off | Enable anti-detection + tracker blocking |
| `--workers` | `1` | Number of parallel worker processes |
| `--obey-robots` | off | Respect robots.txt |

Example:

```bash
obscura serve --port 9222 --stealth --workers 4
```

## `obscura fetch <URL>`

Fetch and render a single page.

| Flag | Default | Description |
|------|---------|-------------|
| `--dump` | `html` | Output format: `html`, `text`, or `links` |
| `--eval` | — | JavaScript expression to evaluate and print result |
| `--wait-until` | `load` | Wait condition: `load`, `domcontentloaded`, `networkidle0` |
| `--selector` | — | Wait for CSS selector to appear before proceeding |
| `--stealth` | off | Enable anti-detection mode |
| `--quiet` | off | Suppress startup banner |

Examples:

```bash
# Render page and extract title
obscura fetch https://example.com --eval "document.title"

# Wait for network to idle, then dump text
obscura fetch https://news.ycombinator.com --wait-until networkidle0 --dump text

# Extract all links
obscura fetch https://example.com --dump links
```

## `obscura scrape <URL...>`

Scrape multiple URLs in parallel using worker processes.

| Flag | Default | Description |
|------|---------|-------------|
| `--concurrency` | `10` | Number of parallel workers |
| `--eval` | — | JavaScript expression to evaluate per page |
| `--format` | `json` | Output format: `json` or `text` |

Example:

```bash
obscura scrape url1 url2 url3 \
  --concurrency 25 \
  --eval "document.querySelector('h1').textContent" \
  --format json
```

## `obscura-worker`

Internal binary used by `obscura scrape` for parallel worker processes. Not intended for direct use.
