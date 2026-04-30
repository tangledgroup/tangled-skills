# API Reference

## Read Endpoint (`r.jina.ai`)

### Basic Usage

Prepend `https://r.jina.ai/` to any URL:

```bash
curl -sL "https://r.jina.ai/https://en.wikipedia.org/wiki/Artificial_intelligence"
```

### SPA With Hash-Based Routing

Content after `#` is not sent to the server. Use POST with a `url` body parameter:

```bash
curl -X POST "https://r.jina.ai/" -d 'url=https://example.com/#/route'
```

### Waiting For Dynamic Content

Some SPAs show preload content before loading the main content dynamically. Two approaches:

**Specify a timeout** — Reader waits for network idle until the timeout is reached:

```bash
curl "https://r.jina.ai/https://example.com/" -H "x-timeout: 30"
```

**Wait for a specific selector** — Reader waits until the CSS selector appears:

```bash
curl "https://r.jina.ai/https://example.com/" -H "x-wait-for-selector: #main-content"
```

### Streaming Mode

Useful when standard mode returns incomplete results. Each chunk contains progressively more complete information — the last chunk is the final result. This differs from LLM text-generation streaming.

```bash
curl -H "Accept: text/event-stream" "https://r.jina.ai/https://en.m.wikipedia.org/wiki/Main_Page"
```

Streaming is also useful for interleaving I/O and LLM processing — feed each chunk to your LLM as it arrives:

```text
Reader API:  chunk1 ----> chunk2 ----> chunk3
                    |              |           |
                    v              |           |
Your LLM:          process(chunk1)            |
                                   process(chunk2)
                                                  process(chunk3)
```

### JSON Mode

Returns structured output with `url`, `title`, and `content` fields:

```bash
curl -H "Accept: application/json" "https://r.jina.ai/https://en.m.wikipedia.org/wiki/Main_Page"
```

### Generated Alt Text

Auto-caption images lacking `alt` tags using a VLM. Format: `!(Image [idx]: [caption])[img_URL]`. Off by default for better latency:

```bash
curl -H "X-With-Generated-Alt: true" "https://r.jina.ai/https://en.m.wikipedia.org/wiki/Main_Page"
```

## Search Endpoint (`s.jina.ai`)

### Basic Usage

Prepend `https://s.jina.ai/` to an URL-encoded query:

```bash
curl -sL "https://s.jina.ai/Who%20will%20win%202024%20US%20presidential%20election%3F"
```

Returns top 5 results, each with full content extracted via `r.jina.ai` technology.

### In-Site Search

Restrict results to specific domains using the `site` query parameter:

```bash
curl "https://s.jina.ai/When%20was%20Jina%20AI%20founded%3F?site=jina.ai&site=github.com"
```

### JSON Mode For Search

Returns 5 results in a list, each with `title`, `content`, and `url`:

```bash
curl -H "Accept: application/json" "https://s.jina.ai/your+query"
```

## Request Headers Reference

- **`x-with-generated-alt: true`** — Enable VLM-based image captioning for images without alt tags.
- **`x-set-cookie`** — Forward cookie settings. Requests with cookies are not cached.
- **`x-respond-with: markdown`** — Return markdown without going through readability filtering.
- **`x-respond-with: html`** — Return raw `documentElement.outerHTML`.
- **`x-respond-with: text`** — Return `document.body.innerText`.
- **`x-respond-with: screenshot`** — Return URL of the webpage screenshot.
- **`x-proxy-url`** — Specify a proxy server for fetching content.
- **`x-cache-tolerance`** — Custom cache tolerance in seconds (default: 3600).
- **`x-no-cache: true`** — Bypass cache entirely (equivalent to `x-cache-tolerance: 0`).
- **`x-target-selector`** — CSS selector to extract content from a specific element instead of the full page.
- **`x-wait-for-selector`** — CSS selector to wait for before returning content. Can be omitted if same as `x-target-selector`.
- **`x-timeout`** — Explicit timeout in seconds. Reader waits for network idle until this duration.

## Rate Limits

The service is free, stable, and scalable. Rate limits apply — check the [official pricing page](https://jina.ai/reader#pricing) for current limits.
