# Fetchers and Sessions

## Contents
- Response Object
- Fetcher (HTTP)
- DynamicFetcher (Playwright)
- StealthyFetcher (Anti-Bot)
- Session Classes
- ProxyRotator
- Configuring the Parser

## Response Object

All fetchers return a `Response` object, which extends `Selector` with HTTP metadata:

| Property | Description |
|---|---|
| `.status` | HTTP status code |
| `.reason` | Status message |
| `.cookies` | Response cookies as dict |
| `.headers` | Response headers |
| `.request_headers` | Request headers sent |
| `.history` | Redirect history |
| `.body` | Raw response body (always `bytes` since v0.4) |
| `.encoding` | Response encoding |
| `.meta` | Metadata dict (e.g., proxy used) |
| `.captured_xhr` | Captured XHR/fetch responses (when `capture_xhr` enabled) |

All `Selector` methods (`.css()`, `.xpath()`, `.find_all()`, etc.) work on Response objects.

## Fetcher (HTTP)

Fast HTTP requests via `curl_cffi` with TLS fingerprint impersonation.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher
page = Fetcher.get('https://example.com')
page = await AsyncFetcher.get('https://example.com')
```

Methods: `.get()`, `.post()`, `.put()`, `.delete()` (sync) and `async_get()`, `async_post()`, etc. (async).

Shared arguments:
- `stealthy_headers` — real browser headers + Google referer, default `True`
- `impersonate` — TLS fingerprint: `'chrome'`, `'firefox'`, `'safari'`, `'edge'`, or versioned like `'chrome110'`. Default: latest Chrome
- `http3` — use HTTP/3, default `False`
- `follow_redirects` — `"safe"` (default, SSRF protection), `True`, or `False`
- `timeout` — seconds, default 30
- `retries` / `retry_delay` — retry failed requests, defaults 3 / 1s
- `proxy` — single proxy URL
- `proxy_rotator` — `ProxyRotator` instance
- `cookies` — dict or list of dicts
- `headers` — override headers
- `selector_config` — per-request parser config dict

## DynamicFetcher (Playwright)

Browser-based fetching via Playwright with Chromium or real Chrome.

```python
from scrapling.fetchers import DynamicFetcher
page = DynamicFetcher.fetch('https://spa.example.com', network_idle=True)
page = await DynamicFetcher.async_fetch('https://spa.example.com')
```

Key arguments:
- `headless` — default `True`
- `disable_resources` — block fonts/images/media for speed (~25% faster)
- `network_idle` — wait for no network connections for 500ms
- `load_dom` — wait for `domcontentloaded`, default `True`
- `timeout` — milliseconds, default 30000
- `wait` — extra milliseconds after everything loads
- `page_action` — function receiving Playwright `page` object, runs after navigation (for automation)
- `page_setup` — function running before navigation (for event listeners, routes)
- `wait_selector` / `wait_selector_state` — wait for element in state (`attached`, `visible`, `hidden`, `detached`)
- `real_chrome` — use installed Chrome instead of bundled Chromium
- `cdp_url` — connect to remote browser via Chrome DevTools Protocol
- `block_ads` — block ~3,500 ad/tracker domains
- `blocked_domains` — set of domain names to block (subdomains matched too)
- `dns_over_https` — DNS-over-HTTPS via Cloudflare
- `capture_xhr` — regex pattern to capture XHR/fetch requests; results in `response.captured_xhr`
- `locale` / `timezone_id` — browser locale and timezone
- `user_data_dir` — persistent browser data directory (sessions only)
- `extra_flags` — additional browser launch flags

## StealthyFetcher (Anti-Bot)

Same as DynamicFetcher plus advanced anti-bot bypass. Handles Cloudflare Turnstile/Interstitial automatically.

```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://protected-site.com', solve_cloudflare=True)
```

Additional arguments beyond DynamicFetcher:
- `solve_cloudflare` — auto-solve Cloudflare challenges (set timeout ≥ 60s)
- `block_webrtc` — force WebRTC to respect proxy settings
- `hide_canvas` — add canvas noise to prevent fingerprinting
- `allow_webgl` — default `True`; disabling WebGL is not recommended (many WAFs check for it)

What it does automatically: bypasses CDP/WebRTC leaks, isolates JS execution, removes Playwright fingerprints, patches headless detection methods, defeats timezone mismatch attacks.

## Session Classes

Keep browser/connections alive across multiple requests. Each fetcher has a session variant:

| Fetcher | Sync Session | Async Session |
|---|---|---|
| `Fetcher` | `FetcherSession` (auto-detects sync/async) | — |
| `DynamicFetcher` | — | `AsyncDynamicSession` |
| `StealthyFetcher` | — | `AsyncStealthySession` |

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome', http3=True, timeout=30) as session:
    page1 = session.get('https://example1.com')
    page2 = session.post('https://example2.com', data={'key': 'value'})
```

Browser sessions support `max_pages` for a rotating pool of tabs (saves resources vs. single tab). `user_data_dir` enables persistent cookies/local storage.

## ProxyRotator

Automatic proxy rotation across requests.

```python
from scrapling.fetchers import ProxyRotator

rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://user:pass@proxy2:8080",
])

# String proxies for HTTP sessions
session = FetcherSession(proxy_rotator=rotator)

# Dict proxies (Playwright format) for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "u", "password": "p"},
])
session = AsyncStealthySession(proxy_rotator=rotator)
```

Custom rotation strategies via `strategy` function: `(proxies, current_index) -> (proxy, next_index)`. Default is cyclic rotation. Per-request override with `proxy=` argument.

When used with browser sessions, each proxy gets a separate context (browsers can't set proxy per tab).

## Configuring the Parser

Set parser options globally on any fetcher class:

```python
from scrapling.fetchers import Fetcher
Fetcher.configure(adaptive=True, keep_comments=False)
# Or:
Fetcher.adaptive = True
Fetcher.keep_comments = False
Fetcher.display_config()  # Show current config
```

Per-request override via `selector_config` dict argument on any fetch method.
