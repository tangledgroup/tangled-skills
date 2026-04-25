---
name: obscura-0-1-0
description: Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs real JavaScript via V8, supports Chrome DevTools Protocol (CDP), and acts as a drop-in replacement for headless Chrome with Puppeteer and Playwright. Use when building scrapers, automating web interactions, or replacing headless Chrome with lower memory footprint (~30 MB vs 200+ MB) and built-in anti-detection capabilities.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - headless browser
  - web scraping
  - rust
  - cdp
  - puppeteer
  - playwright
  - v8
  - anti-detection
category: web-scraping
external_references:
  - https://github.com/h4ckf0r0day/obscura/tree/v0.1.0
  - https://chromedevtools.github.io/devtools-protocol/
  - https://github.com/h4ckf0r0day/obscura
  - https://github.com/h4ckf0r0day/obscura/releases/tag/v0.1.0
  - https://github.com/h4ckf0r0day/obscura/releases
---
## Overview
Obscura is a headless browser engine written in Rust, built for web scraping and AI agent automation. It runs real JavaScript via V8 (through `deno_core`), implements the Chrome DevTools Protocol, and serves as a drop-in replacement for headless Chrome with Puppeteer and Playwright.

Key advantages over headless Chrome:

- **Memory**: ~30 MB vs 200+ MB
- **Binary size**: ~70 MB vs 300+ MB
- **Page load**: ~85 ms vs ~500 ms
- **Startup**: instant vs ~2 seconds
- **Anti-detection**: built-in via `--stealth` feature

Single binary. No Chrome, no Node.js, no external dependencies.

## When to Use
- Web scraping at scale with lower resource usage than headless Chrome
- AI agent workflows needing browser automation
- Replacing Puppeteer/Playwright backend without changing client code
- Environments where stealth (anti-fingerprinting + tracker blocking) matters
- Parallel scraping workloads with many concurrent pages

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Architecture
Obscura is a Rust workspace with six crates:

- **obscura-dom** — HTML parsing via `html5ever`, CSS selectors via `selectors`/`cssparser`
- **obscura-net** — HTTP client layer using `reqwest`; stealth variant uses `wreq`
- **obscura-js** — JavaScript execution via V8 through `deno_core`, bridging DOM and network
- **obscura-browser** — Browser orchestration combining DOM, JS, and network layers
- **obscura-cdp** — Chrome DevTools Protocol implementation over WebSocket (`tokio-tungstenite`)
- **obscura-cli** — CLI binaries (`obscura` main + `obscura-worker` for parallel scraping)

## Installation / Setup
### Prebuilt Binaries

Download from [Releases](https://github.com/h4ckf0r0day/obscura/releases):

```bash
# Linux x86_64
curl -LO https://github.com/h4ckf0r0day/obscura/releases/download/v0.1.0/obscura-x86_64-linux.tar.gz
tar xzf obscura-x86_64-linux.tar.gz

# macOS Apple Silicon
curl -LO https://github.com/h4ckf0r0day/obscura/releases/download/v0.1.0/obscura-aarch64-macos.tar.gz
tar xzf obscura-aarch64-macos.tar.gz

# macOS Intel
curl -LO https://github.com/h4ckf0r0day/obscura/releases/download/v0.1.0/obscura-x86_64-macos.tar.gz
tar xzf obscura-x86_64-macos.tar.gz
```

Windows: download `.zip` from the releases page and extract.

### Build From Source

```bash
git clone https://github.com/h4ckf0r0day/obscura.git
cd obscura
cargo build --release

# With stealth mode (anti-detection + tracker blocking)
cargo build --release --features stealth
```

Requires Rust 1.75+. First build takes ~5 minutes (V8 compiles from source, cached on subsequent builds).

## Usage Examples
### Fetch a page

```bash
# Get the page title
obscura fetch https://example.com --eval "document.title"

# Extract all links
obscura fetch https://example.com --dump links

# Render JavaScript and dump HTML
obscura fetch https://news.ycombinator.com --dump html

# Wait for dynamic content to finish loading
obscura fetch https://example.com --wait-until networkidle0
```

### Start the CDP server

```bash
obscura serve --port 9222

# With stealth mode
obscura serve --port 9222 --stealth
```

### Scrape in parallel

```bash
obscura scrape url1 url2 url3 \
  --concurrency 25 \
  --eval "document.querySelector('h1').textContent" \
  --format json
```

### Puppeteer integration

```javascript
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://127.0.0.1:9222/devtools/browser',
});

const page = await browser.newPage();
await page.goto('https://news.ycombinator.com');

const stories = await page.evaluate(() =>
  Array.from(document.querySelectorAll('.titleline > a'))
    .map(a => ({ title: a.textContent, url: a.href }))
);
console.log(stories);

await browser.disconnect();
```

### Playwright integration

```javascript
import { chromium } from 'playwright-core';

const browser = await chromium.connectOverCDP({
  endpointURL: 'ws://127.0.0.1:9222',
});

const page = await browser.newContext().then(ctx => ctx.newPage());
await page.goto('https://en.wikipedia.org/wiki/Web_scraping');
console.log(await page.title());

await browser.close();
```

### Form submission and login

```javascript
await page.goto('https://quotes.toscrape.com/login');
await page.evaluate(() => {
  document.querySelector('#username').value = 'admin';
  document.querySelector('#password').value = 'admin';
  document.querySelector('form').submit();
});
// Obscura handles the POST, follows 302 redirects, maintains cookies
```

## Advanced Topics
## Advanced Topics

- [Stealth Mode](reference/01-stealth-mode.md)
- [Cdp Api](reference/02-cdp-api.md)
- [Cli Reference](reference/03-cli-reference.md)

