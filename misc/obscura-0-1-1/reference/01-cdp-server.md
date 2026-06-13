# CDP Server

## Overview

Obscura implements the Chrome DevTools Protocol (CDP) over WebSocket, making it a drop-in replacement for headless Chrome when used with Puppeteer or Playwright. The server listens on `ws://127.0.0.1:<port>/devtools/browser` by default.

## Server Startup

```bash
obscura serve --port 9222
```

The CDP server binds to `127.0.0.1:<port>` and accepts both HTTP (for `/json/*` endpoints) and WebSocket connections (for `/devtools/browser` and `/devtools/page/<id>`).

### HTTP Endpoints

- **`/json/version`** — Returns browser version info (`Obscura/0.1.1`)
- **`/json/list`** — Lists available targets (pages)
- **`/json/protocol`** — Returns CDP protocol version (`1.3`)

### WebSocket Connection

Clients connect via `ws://127.0.0.1:<port>/devtools/browser`. On connection, the server creates a default page and session.

## Implemented CDP Domains

### Target

Page/target lifecycle management:

- `Target.setDiscoverTargets` — Enable target discovery events
- `Target.getTargets` — List all targets
- `Target.createTarget` — Create a new page (optionally with initial URL)
- `Target.closeTarget` — Close a page
- `Target.attachToTarget` / `Target.detachFromTarget` — Attach debugger session
- `Target.createBrowserContext` / `Target.disposeBrowserContext` — Browser context management

### Page

Page navigation and lifecycle:

- `Page.enable` — Enable page domain events
- `Page.navigate` — Navigate to URL with `waitUntil` support (`load`, `domcontentloaded`, `networkidle0`, `networkidle2`)
- `Page.getFrameTree` — Get frame hierarchy
- `Page.addScriptToEvaluateOnNewDocument` — Preload scripts on new pages
- `Page.setLifecycleEventsEnabled` — Enable lifecycle event emission

Lifecycle events emitted per navigation:

1. `Page.lifecycleEvent` (init)
2. `Runtime.executionContextsCleared`
3. `Page.frameNavigated`
4. `Runtime.executionContextCreated` (default + isolated)
5. `Page.lifecycleEvent` (commit)
6. Network events for each resource
7. `Page.lifecycleEvent` (DOMContentLoaded)
8. `Page.domContentEventFired`
9. `Page.lifecycleEvent` (load)
10. `Page.loadEventFired`
11. `Page.lifecycleEvent` (networkIdle) — if reached
12. `Page.frameStoppedLoading`

### Runtime

JavaScript evaluation:

- `Runtime.enable` — Enable runtime domain
- `Runtime.evaluate` — Execute JavaScript expression, supports `returnByValue`
- `Runtime.callFunctionOn` — Call function on remote object, supports `awaitPromise`
- `Runtime.getProperties` — Get object properties
- `Runtime.addBinding` — Add binding to isolate

Remote objects support both by-value and by-reference (objectId) return modes.

### DOM

DOM tree inspection:

- `DOM.enable` — Enable DOM domain
- `DOM.getDocument` — Get full document tree (configurable depth)
- `DOM.querySelector` — Single element query by CSS selector
- `DOM.querySelectorAll` — Multiple elements query
- `DOM.getOuterHTML` — Get outer HTML of a node
- `DOM.describeNode` — Describe node with children
- `DOM.resolveNode` — Resolve node to remote object

### Network

HTTP request/response management:

- `Network.enable` — Enable network domain events
- `Network.setExtraHTTPHeaders` — Set custom headers for requests
- `Network.setUserAgentOverride` — Override user agent
- `Network.getCookies` — Get cookies for current page
- `Network.setCookies` — Set cookies
- `Network.clearBrowserCookies` — Clear all cookies
- `Network.setCacheDisabled` — Disable HTTP cache
- `Network.setRequestInterception` — Enable request interception

### Fetch

Live request interception (pauses requests before they are sent):

- `Fetch.enable` — Enable with URL patterns
- `Fetch.disable` — Disable interception
- `Fetch.continueRequest` — Resume a paused request (optionally modifying URL, method, body)
- `Fetch.fulfillRequest` — Respond to a paused request with custom status, headers, and body
- `Fetch.failRequest` — Fail a paused request with error reason
- `Fetch.getResponseBody` — Get response body

When `Fetch.enable` is active during navigation, the server pauses at intercepted requests, sends `Fetch.requestPaused` events, and waits for client resolution before continuing.

### Storage

Cookie management:

- `Storage.getCookies` — List all cookies
- `Storage.setCookies` — Set cookies (supports domain from URL)
- `Storage.deleteCookies` — Delete cookies by name and domain

### Input

Mouse and keyboard event dispatch:

- `Input.dispatchMouseEvent` — Dispatch mouse events (`mousePressed`, `mouseReleased`)
- `Input.dispatchKeyEvent` — Dispatch keyboard events

Mouse click handling follows link navigation: when a click is dispatched on an `<a>` element, the page navigates to the href.

### LP (Lightweight Parser)

DOM-to-Markdown conversion:

- `LP.getMarkdown` — Convert the page body to Markdown format

Supports headings, paragraphs, lists, tables, links, images, code blocks, and blockquotes. Useful for AI agent workflows that need structured text from rendered pages.

### Browser

Browser-level operations:

- `Browser.getVersion` — Returns `Obscura/0.1.1` with protocol version `1.3`
- `Browser.close` — Close the browser
- `Browser.getWindowForTarget` — Get window bounds (default 1280x720)
- `Browser.setDownloadBehavior` — No-op stub
- `Browser.getWindowBounds` — Window dimensions

### Stubbed Domains

These domains return empty success responses:

`Emulation`, `Log`, `Performance`, `Security`, `CSS`, `Accessibility`, `ServiceWorker`, `Inspector`, `Debugger`, `Profiler`, `HeapProfiler`, `Overlay`

## Multi-Worker Mode

With `--workers N`, the CLI spawns N worker processes on sequential ports (`port+1` through `port+N`) and runs a TCP load balancer on the primary port. Connections are round-robined across workers. The `/json/*` endpoints also round-robin.

```bash
obscura serve --port 9222 --workers 4
# Workers on ports 9223, 9224, 9225, 9226
# Load balancer on port 9222
```

### Changes in 0.1.1

- Load balancer no longer panics on unwrap — handles edge cases gracefully
- `/json/version` now round-robins through workers for consistent responses
- Dead workers return HTTP 502 instead of silently dropping connections
