---
name: scrapling-0-4-8
description: Adaptive web scraping framework for Python providing HTML parsing with CSS/XPath/text/regex selection, HTTP and browser-based fetchers with anti-bot bypass, adaptive element tracking that survives website changes, a Scrapy-like spider crawling system with pause/resume, proxy rotation, and an MCP server for AI integration. Use when building scrapers, crawlers, or data extraction pipelines needing resilience to website structure changes and anti-bot protections.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - scrapling
  - web-scraping
  - html-parsing
  - crawler
  - anti-bot
  - adaptive-scraping
category: library
external_references:
  - https://github.com/D4Vinci/Scrapling/tree/v0.4.8
  - https://scrapling.readthedocs.io/en/latest/
---

# Scrapling 0.4.8

## Overview

Scrapling is an adaptive web scraping framework for Python that handles everything from a single HTTP request to full-scale concurrent crawls. Its parser learns from website changes and automatically relocates elements when pages update. Its fetchers bypass anti-bot systems like Cloudflare Turnstile out of the box. Its spider framework supports concurrent multi-session crawls with pause/resume and automatic proxy rotation.

Key differentiators:
- **Adaptive scraping** — elements are relocated after website structure changes using similarity algorithms, no AI required
- **Anti-bot bypass** — StealthyFetcher handles Cloudflare Turnstile/Interstitial automatically
- **Scrapy-like spiders** — async crawling framework with concurrency control, checkpointing, and streaming
- **MCP server** — built-in Model Context Protocol server for AI-assisted scraping

## When to Use

- Parsing HTML with CSS/XPath/text/regex selection and DOM traversal
- Fetching websites via HTTP (with TLS impersonation), Playwright browsers, or stealthy anti-bot bypass
- Building concurrent crawlers that follow links, export results, and survive interruptions
- Scraping sites behind Cloudflare or other anti-bot protections
- Integrating web scraping into AI workflows via MCP server
- Rapid prototyping with the interactive shell

## Installation / Setup

```bash
# Parser only (no fetchers)
pip install scrapling

# With fetchers (HTTP + browser-based)
pip install "scrapling[fetchers]"
scrapling install          # downloads browsers and system dependencies

# With MCP server for AI integration
pip install "scrapling[ai]"

# Interactive shell and extract commands
pip install "scrapling[shell]"

# Everything
pip install "scrapling[all]"
scrapling install          # still needed for browser dependencies
```

Docker: `docker pull pyd4vinci/scrapling` (includes all extras and browsers).

Requires Python 3.10+.

## Core Concepts

**Selector** — the core parsing object wrapping an HTML document or element. Supports CSS, XPath, text-based, regex-based, and filter-based selection. Returns `Selector` (single) or `Selectors` (list subclass) objects. All text values are `TextHandler` objects (string subclass with `.clean()`, `.json()`, `.re()` methods).

**Response** — extends Selector with HTTP metadata: `.status`, `.headers`, `.cookies`, `.body` (bytes), `.url`, `.meta`.

**Fetcher classes** — `Fetcher` (HTTP via curl_cffi, TLS impersonation), `DynamicFetcher` (Playwright Chromium/Chrome for JS rendering), `StealthyFetcher` (anti-bot bypass with Cloudflare solving). Each has sync and async variants plus session classes for state persistence.

**Adaptive feature** — save element properties with `auto_save=True`, then relocate after website changes with `adaptive=True`. Uses SQLite by default; custom storage backends supported.

**Spider system** — Scrapy-inspired async crawler with `start_urls`, `parse()` callbacks, `response.follow()`, concurrency limits, pause/resume via checkpoints, streaming mode, multi-session routing, proxy rotation, and blocked-request retry.

## Usage Examples

Parse HTML directly:
```python
from scrapling import Selector
page = Selector('<html><body><h1>Hello</h1></body></html>')
title = page.css('h1::text').get()          # 'Hello'
articles = page.find_all('article')          # Selectors list
```

Fetch with HTTP (browser impersonation):
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com', impersonate='chrome')
print(page.css('title::text').get())
```

Fetch dynamic content with browser:
```python
from scrapling.fetchers import DynamicFetcher
page = DynamicFetcher.fetch('https://spa.example.com', network_idle=True)
items = page.css('.item')
```

Bypass anti-bot protections:
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://protected-site.com', solve_cloudflare=True)
```

Adaptive scraping — survive website changes:
```python
from scrapling.fetchers import Fetcher
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
# First run: save element properties
products = page.css('.product', auto_save=True)
# Later, after website redesign: relocate with same selector
products = page.css('.product', adaptive=True)
```

Basic spider:
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {"title": item.css('h2::text').get()}

result = MySpider().start()
result.items.to_json("output.json")
```

## Advanced Topics

**Parsing Deep Dive**: Selector/Selectors classes, TextHandler, DOM traversal, selector generation → [Parsing](reference/01-parsing.md)

**Fetchers and Sessions**: HTTP fetcher with TLS impersonation, DynamicFetcher with Playwright, StealthyFetcher with anti-bot bypass, session management, proxy rotation → [Fetchers](reference/02-fetchers.md)

**Adaptive Scraping**: Save/match phases, auto_save/adaptive arguments, manual save/retrieve/relocate, custom storage backends → [Adaptive Scraping](reference/03-adaptive-scraping.md)

**Spider Framework**: Spider class, callbacks, concurrency, pause/resume, streaming, multi-session routing, proxy rotation, blocked-request handling, lifecycle hooks → [Spiders](reference/04-spiders.md)

**CLI and MCP Server**: Interactive shell, extract commands (GET/POST/fetch/stealthy-fetch), MCP server setup for Claude/Cursor, MCP tools reference → [CLI and MCP](reference/05-cli-and-mcp.md)
