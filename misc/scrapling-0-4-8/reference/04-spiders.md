# Spiders

## Contents
- Spider Basics
- Request Object and response.follow()
- Concurrency Control
- Sessions in Spiders
- Proxy Rotation
- Blocked Request Handling
- Pause/Resume (Checkpoints)
- Streaming Mode
- Development Mode
- Lifecycle Hooks
- Results and Statistics
- Logging

## Spider Basics

Scrapy-inspired async crawling framework. Subclass `Spider`, define `start_urls` and `parse()`:

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {"title": item.css('h2::text').get()}

        # Follow links
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

result = MySpider().start()
result.items.to_json("output.json")
```

Every spider needs: `name` (unique ID), `start_urls` (list of URLs), `parse()` (async generator yielding dicts or follow-up requests).

Spider class attributes:
- `allowed_domains` — restrict crawling to specific domains (subdomains matched automatically)
- `robots_txt_obey` — respect robots.txt Disallow/Crawl-delay/Request-rate, default `False`

Export: `result.items.to_json(path)` or `.to_jsonl(path)`. Parent directories created automatically.

## Request Object and response.follow()

```python
from scrapling.spiders import Request

# Direct construction
yield Request("https://example.com/page", callback=self.parse_page, priority=5)

# Via response.follow (preferred — resolves relative URLs, sets Referer)
yield response.follow("/page", callback=self.parse_page)
```

Request arguments: `url`, `sid` (session ID), `callback`, `priority` (higher = first), `dont_filter` (skip deduplication), `meta` (dict passed to response), plus any `**kwargs` forwarded to session fetch method.

`response.follow()` inherits callback, sid, priority, and session kwargs from the original request unless overridden. Set `referer_flow=False` to skip Referer header.

Deduplication: requests fingerprinted by URL + method + body + session ID. Fingerprint tuning: `fp_include_kwargs`, `fp_keep_fragments`, `fp_include_headers` (all default `False`).

## Concurrency Control

| Attribute | Default | Description |
|---|---|---|
| `concurrent_requests` | 4 | Max simultaneous requests |
| `concurrent_requests_per_domain` | 0 | Per-domain limit (0 = none) |
| `download_delay` | 0.0 | Seconds between requests |

```python
class PoliteSpider(Spider):
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0
```

Use `spider.start(use_uvloop=True)` for faster event loop (requires `uvloop`/`winloop`).

## Sessions in Spiders

Override `configure_sessions()` to set up multiple fetcher types:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/"]

    def configure_sessions(self, manager):
        manager.add("http", FetcherSession())  # Default (first added)
        manager.add("stealth", AsyncStealthySession(headless=True))

    async def parse(self, response: Response):
        for link in response.css("a.product::attr(href)").getall():
            yield response.follow(link, sid="stealth", callback=self.parse_product)

    async def parse_product(self, response: Response):
        yield {"name": response.css("h1::text").get("")}
```

`manager.add(session_id, session, default=False, lazy=False)`. First added session is default. `lazy=True` starts session on first use only. Per-request kwargs (headers, wait_selector, etc.) are forwarded to the session's fetch method.

## Proxy Rotation

```python
from scrapling.fetchers import ProxyRotator

def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("default", FetcherSession(proxy_rotator=rotator))
```

Proxy used is stored in `response.meta["proxy"]`. Per-request override with `proxy=` kwarg.

## Blocked Request Handling

Default blocked status codes: 401, 403, 407, 429, 444, 500, 502, 503, 504. Retries up to `max_blocked_retries` (default 3). On retry, previous proxy is cleared so rotator assigns a fresh one.

Override detection:
```python
async def is_blocked(self, response: Response) -> bool:
    if response.status in {403, 429}:
        return True
    body = response.body.decode("utf-8", errors="ignore")
    return "access denied" in body.lower()
```

Override retry behavior:
```python
async def retry_blocked_request(self, request: Request, response: Response) -> Request:
    request.sid = "stealth"  # Switch to stealth session on block
    return request
```

## Pause/Resume (Checkpoints)

Enable with `crawldir`:

```python
spider = MySpider(crawldir="crawl_data/my_spider")
result = spider.start()
if result.paused:
    print("Run again to resume")
```

Ctrl+C saves checkpoint (pending requests + seen fingerprints) and exits gracefully. Second Ctrl+C forces immediate stop. Resume with same `crawldir` — skips `start_requests()`, restores queue. Checkpoints saved every 5 minutes by default (configurable via `interval` in seconds). Auto-cleaned on successful completion.

## Streaming Mode

Real-time item access (requires async context):

```python
import anyio

async def main():
    spider = MySpider()
    async for item in spider.stream():
        print(item)
        print(f"Items so far: {spider.stats.items_scraped}")

anyio.run(main)
```

Works with checkpoints too. Use `spider.pause()` to shut down from within the loop.

## Development Mode

Cache responses to disk on first run, replay on subsequent runs — iterate on `parse()` without hitting servers:

```python
class MySpider(Spider):
    development_mode = True
    development_cache_dir = "/tmp/cache"  # Optional, default .scrapling_cache/{name}/
```

Cache keyed by request fingerprint. Body base64-encoded. No automatic expiration — delete cache dir to force fresh crawl. Stats include `cache_hits` and `cache_misses`.

## Lifecycle Hooks

```python
async def on_start(self, resuming: bool = False):
    # Setup before crawling

async def on_close(self):
    # Cleanup after crawl (completed or paused)

async def on_error(self, request: Request, error: Exception):
    # Handle failed requests

async def on_scraped_item(self, item: dict) -> dict | None:
    # Return item to keep, None to drop

async def start_requests(self):
    # Custom initial requests instead of start_urls
    yield Request("https://example.com/login", method="POST", data={"user": "admin"}, callback=self.after_login)
```

## Results and Statistics

```python
result = MySpider().start()

result.items.to_json("output.json")
result.completed  # bool
result.paused     # bool

stats = result.stats
stats.requests_count
stats.failed_requests_count
stats.blocked_requests_count
stats.offsite_requests_count
stats.robots_disallowed_count
stats.cache_hits / stats.cache_misses
stats.items_scraped / stats.items_dropped
stats.response_bytes
stats.elapsed_seconds
stats.requests_per_second
stats.response_status_count   # {'status_200': 150, ...}
stats.domains_response_bytes  # {'example.com': 1234567}
stats.sessions_requests_count # {'http': 120, 'stealth': 34}
stats.proxies                 # list of proxies used
stats.custom_stats            # set via self.stats.custom_stats['key'] = value
```

## Logging

Built-in logger via `self.logger`. Customize:

```python
class MySpider(Spider):
    logging_level = logging.INFO
    logging_format = "[%(asctime)s]:({spider_name}) %(levelname)s: %(message)s"
    log_file = "logs/my_spider.log"  # Console + file

async def parse(self, response: Response):
    self.logger.info(f"Processing {response.url}")
```
