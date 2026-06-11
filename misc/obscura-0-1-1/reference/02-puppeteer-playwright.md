# Puppeteer and Playwright Integration

## Overview

Obscura's CDP server makes it a drop-in replacement for headless Chrome. Connect Puppeteer or Playwright via WebSocket to `ws://127.0.0.1:<port>/devtools/browser`.

## Puppeteer

Use `puppeteer-core` (not full `puppeteer`, which bundles Chromium).

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

### Form Submission and Login

Obscura handles POST requests, follows 302 redirects, and maintains cookies across navigations:

```javascript
await page.goto('https://quotes.toscrape.com/login');
await page.evaluate(() => {
  document.querySelector('#username').value = 'admin';
  document.querySelector('#password').value = 'admin';
  document.querySelector('form').submit();
});
// Obscura handles the POST, follows redirect, maintains cookies
```

### JavaScript-Triggered Navigation

When page JavaScript calls `location.assign()` or form submission triggers a POST redirect, Obscura intercepts the pending navigation and processes it through the CDP layer automatically.

## Playwright

Use `playwright-core` (not full `playwright`, which bundles browsers).

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

## Supported CDP Features for Automation

### Navigation

- `page.goto(url)` with `waitUntil` options (`load`, `domcontentloaded`, `networkidle`)
- Frame navigation via `Page.frameNavigated` events
- JavaScript-initiated navigation (`location.assign`, form POST redirects)

### Evaluation

- `page.evaluate()` — Execute arbitrary JavaScript
- `page.$(selector)` / `page.$$(selector)` — DOM queries via CSS selectors
- Remote object inspection with property access

### Network

- Custom headers via `Network.setExtraHTTPHeaders`
- User agent override via `Network.setUserAgentOverride`
- Cookie management via `Network.getCookies` / `Network.setCookies`
- Request interception via `Fetch.enable` + `Fetch.fulfillRequest`

### Input

- Mouse click dispatch via `Input.dispatchMouseEvent`
- Keyboard events via `Input.dispatchKeyEvent`

## Limitations vs Full Chrome

- No screenshot/PDF generation (no rendering engine)
- No WebSocket client support beyond CDP transport
- No service worker execution
- No WebGL/WebGPU canvas operations
- Cookie expiration tracking is simplified (session-based)
- Window dimensions are fixed at 1280x720

## Worker Binary for Parallel Scraping

The `obscura-worker` binary is a lightweight process used by `obscura scrape`. It accepts JSON commands over stdin and returns JSON results over stdout:

```json
{"cmd": "navigate", "url": "https://example.com"}
{"cmd": "evaluate", "expression": "document.title"}
{"cmd": "title"}
{"cmd": "dump_html"}
{"cmd": "dump_text"}
{"cmd": "shutdown"}
```

Each command returns a response:

```json
{"ok": true, "result": {"title": "Example Domain", "url": "https://example.com/"}}
```
