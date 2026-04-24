# CDP API Reference

> **Source:** Obscura README.md (v0.1.0)
> **Loaded from:** SKILL.md (via progressive disclosure)

Obscura implements the Chrome DevTools Protocol over WebSocket, enabling compatibility with Puppeteer and Playwright. The CDP server listens on port 9222 by default.

## Supported Domains

### Target

- `createTarget` — Create a new browsing context (tab/page)
- `closeTarget` — Close a browsing context
- `attachToTarget` — Attach debugger to an existing target
- `createBrowserContext` — Create isolated browser context (incognito-like)
- `disposeBrowserContext` — Destroy a browser context and all its targets

### Page

- `navigate` — Navigate page to a URL
- `getFrameTree` — Get the frame tree of the page
- `addScriptToEvaluateOnNewDocument` — Inject script into new documents
- Lifecycle events — `load`, `domcontentloaded`, `networkidle0`

### Runtime

- `evaluate` — Execute JavaScript expression in page context
- `callFunctionOn` — Call a function on a JavaScript object
- `getProperties` — Get properties of an object
- `addBinding` — Bind a Python/Rust function to the JS context

### DOM

- `getDocument` — Get the root DOM node
- `querySelector` — Find element by CSS selector
- `querySelectorAll` — Find all elements by CSS selector
- `getOuterHTML` — Get outer HTML of a node
- `resolveNode` — Get object id for a DOM node

### Network

- `enable` — Enable network domain events
- `setCookies` — Set cookies for a domain
- `getCookies` — Get cookies for a domain
- `setExtraHTTPHeaders` — Set custom HTTP headers
- `setUserAgentOverride` — Override user agent string

### Fetch

- `enable` — Enable request interception
- `continueRequest` — Let intercepted request proceed
- `fulfillRequest` — Respond to intercepted request with custom response
- `failRequest` — Fail intercepted request with error code

Live interception allows modifying requests before they are sent.

### Storage

- `getCookies` — Retrieve stored cookies
- `setCookies` — Set cookies in storage
- `deleteCookies` — Remove cookies from storage

### Input

- `dispatchMouseEvent` — Simulate mouse events (click, move, etc.)
- `dispatchKeyEvent` — Simulate keyboard events (keyDown, keyUp, char)

### LP (Custom Domain)

- `getMarkdown` — Convert DOM to Markdown representation

This is an Obscura-specific extension not part of standard CDP. Useful for AI agents that consume structured text from web pages.

## Connection Endpoints

```
# WebSocket endpoint for browser connection
ws://127.0.0.1:9222/devtools/browser

# Direct page WebSocket (after target creation)
ws://127.0.0.1:9222/devtools/page/<page-id>
```
