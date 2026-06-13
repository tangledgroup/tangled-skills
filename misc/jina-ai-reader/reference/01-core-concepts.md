# Core Concepts

## Endpoints

Jina Reader exposes two primary endpoints:

- **`r.jina.ai`** — Read endpoint. Prepends to any URL to convert it to LLM-friendly markdown. Example: `https://r.jina.ai/https://example.com`.
- **`s.jina.ai`** — Search endpoint. Takes a search query and returns the top 5 results, each with full page content already extracted via the same technology behind `r.jina.ai`. Example: `https://s.jina.ai/your+query`.

## What Makes It Different From Standard Web Search

Most agent/RAG frameworks that offer web search return only the title, URL, and snippet from the search engine API. If you want the full article, you must fetch it yourself — dealing with browser rendering, JavaScript execution, CSS blocking, and anti-bot measures.

Jina Reader's `s.jina.ai` automatically fetches and processes the full content of each search result URL. You get readable markdown for all 5 results in a single call without handling any of the rendering complexity yourself.

## Supported Content Types

- **Web pages (HTML/xHTML)** — Rendered using headless Chrome via Puppeteer, with JavaScript execution support.
- **PDFs** — Parsed and rendered using PDF.js. Any publicly accessible PDF URL works.
- **MS Office documents** — Word, Excel, and PowerPoint files are converted to PDF/HTML using LibreOffice, then processed into markdown or images.
- **Images** — Auto-captioned using a vision language model (VLM) when the `x-with-generated-alt` header is set.

## Output Formats

The Reader API supports multiple output formats controlled by the `Accept` header:

- **Markdown** (default) — Clean, LLM-friendly markdown extracted from the page content.
- **HTML** — Raw `documentElement.outerHTML` returned when `x-respond-with: html` is set.
- **Text** — Plain `document.body.innerText` returned when `x-respond-with: text` is set.
- **Screenshot** — URL of a webpage screenshot returned when `x-respond-with: screenshot` is set.
- **JSON** — Structured output with `url`, `title`, and `content` fields. For search, returns a list of 5 results each with the same structure.

## Caching Behavior

Pages are cached for 3600 seconds (1 hour) by default. Requests that include cookies via `x-set-cookie` are not cached. You can control caching behavior:

- `x-no-cache: true` — Bypass cache entirely (equivalent to `x-cache-tolerance: 0`).
- `x-cache-tolerance` — Set custom tolerance in seconds.
