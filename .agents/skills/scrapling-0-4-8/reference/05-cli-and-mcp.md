# CLI and MCP Server

## Contents
- Interactive Shell
- Extract Commands
- MCP Server Setup
- MCP Tools Reference

## Interactive Shell

IPython-based REPL with Scrapling shortcuts, automatic page management, and curl conversion tools. Requires `scrapling[shell]` extra.

```bash
scrapling shell
scrapling shell -c "get('https://example.com'); print(len(page.css('a')))"
scrapling shell --loglevel info
```

Built-in shortcuts (no imports needed):
- `get(url)`, `post(url)`, `put(url)`, `delete(url)` — HTTP requests via Fetcher
- `fetch(url)` — browser fetch via DynamicFetcher
- `stealthy_fetch(url)` — stealthy browser fetch
- `page` / `response` — last fetched page (auto-updated)
- `pages` — history of last 5 pages (Selectors object)
- `view(page)` — open page HTML in default browser

Curl conversion:
```python
request = uncurl(curl_command_string)   # Parse curl into Request object
curl2fetcher(curl_command_string)       # Execute curl command directly via Fetcher
```

## Extract Commands

Scrape websites from the terminal without writing code. Output format determined by file extension (`.html`, `.md`, `.txt`).

```bash
# HTTP GET — save as markdown
scrapling extract get "https://example.com" page.md

# With CSS selector to target specific content
scrapling extract get "https://blog.example.com" articles.md --css-selector "article"

# POST request
scrapling extract post "https://api.example.com" response.json --json '{"key": "value"}'

# Browser fetch (dynamic content)
scrapling extract fetch "https://spa.example.com" page.html

# Stealthy fetch (anti-bot bypass)
scrapling extract stealthy-fetch "https://protected.com" page.html

# AI-targeted mode — strips noise, hidden elements, prompt injection vectors
scrapling extract get "https://example.com" content.md --ai-targeted
```

Available commands: `get`, `post`, `put`, `delete`, `fetch`, `stealthy-fetch`.

Common options: `-H` / `--headers`, `--cookies`, `--timeout`, `--proxy`, `-s` / `--css-selector`, `-p` / `--params`, `--impersonate`, `--ai-targeted`.

## MCP Server Setup

Built-in Model Context Protocol server for AI-assisted scraping. Requires `scrapling[ai]` extra.

```bash
pip install "scrapling[ai]"
scrapling install
```

### Claude Desktop

Add to config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "/path/to/scrapling",
      "args": ["mcp"]
    }
  }
}
```

Find path with `which scrapling` (macOS/Linux) or `where scrapling` (Windows).

### Claude Code

```bash
claude mcp add ScraplingServer "/path/to/scrapling" mcp
```

### Docker

```json
{
  "mcpServers": {
    "ScraplingServer": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "pyd4vinci/scrapling", "mcp"]
    }
  }
}
```

Same logic applies to Cursor, Windsurf, and other MCP-compatible tools.

## MCP Tools Reference

| Tool | Description |
|---|---|
| `get` | Fast HTTP request with TLS impersonation, stealthy headers, HTTP/3 |
| `bulk_get` | Async parallel version of `get` for multiple URLs |
| `fetch` | Browser fetch via Chromium/Chrome with full control |
| `bulk_fetch` | Async parallel version of `fetch` |
| `stealthy_fetch` | Anti-bot bypass with Cloudflare solving |
| `bulk_stealthy_fetch` | Async parallel version of `stealthy_fetch` |
| `screenshot` | Capture PNG/JPEG screenshot, returned as image content block (not base64). Supports full-page, quality, `wait`, `wait_selector`, `network_idle` |
| `open_session` | Create persistent browser session (dynamic or stealthy) |
| `close_session` | Close persistent session |
| `list_sessions` | List active sessions with details |

Key capabilities:
- **CSS selector targeting** — select specific elements before passing to AI, saving tokens vs. sending full page
- **Content formats** — Markdown, HTML, or clean text extraction
- **Prompt injection protection** — automatic sanitization of hidden content (CSS-hidden, aria-hidden, zero-width chars, HTML comments, template tags)
- **Ad blocking** — browser tools block ~3,500 ad/tracker domains automatically
- **Proxy support** and **browser impersonation** on all tools
