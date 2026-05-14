# HTML Endpoint

## Contents
- Endpoint
- Caveats
- HTML Search with scrapling (Default)
- HTML Search with curl or wget (Fallback)
- Detect CAPTCHA Response

## Endpoint

```
https://duckduckgo.com/html/?q={query}
```

## Caveats

- **Bot detection**: The `/html/` endpoint triggers a CAPTCHA (anomaly modal) for automated requests from many IP ranges. If the response contains `anomaly-modal`, the search was blocked.
- **Format conversion**: HTML output is automatically converted to markdown via scrapling (native `.md`) or pandoc (for curl/wget backends).
- **Use case**: Best when you need result snippets and descriptions that the JSON API doesn't provide.

## HTML Search with scrapling (Default)

Run `assets/example-scrapling-search.sh` to fetch HTML results using scrapling's anti-bot backend (default):

```bash
bash assets/example-scrapling-search.sh "Rust programming language"
```

Or via the CLI (scrapling + html are both defaults):

```bash
bash scripts/ddg-search.sh "Rust"
```

Scrapling impersonates Safari, handles JS rendering, and outputs clean markdown natively — no pandoc needed.

## HTML Search with curl or wget (Fallback)

When scrapling is unavailable, use curl or wget with `.web-result` extraction and pandoc conversion:

```bash
# Curl fetches raw HTML, extracts .web-result elements, converts to markdown via pandoc
bash scripts/ddg-search.sh "Rust" --backend curl

# Wget fallback
bash scripts/ddg-search.sh "Rust" --backend wget
```

**How it works:** The curl/wget backends fetch the full HTML page, then `ddg_extract_web_results()` uses python3's built-in `html.parser` to extract only `<div class="...web-result ...">` elements — matching what scrapling does with `--css-selector '.web-result'`. This strips nav, footer, ads, and other page chrome before pandoc converts to markdown.

If pandoc is not installed, a warning is printed to stderr and raw HTML is returned instead.

## Detect CAPTCHA Response

Run `assets/example-captcha-detect.sh` to test if your IP is being blocked:

```bash
bash assets/example-captcha-detect.sh "test query"
```

Exit code 0 = clean, exit code 1 = blocked. When blocked, use the JSON API instead.
