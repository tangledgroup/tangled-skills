# Extensions

htmx 4.0 supports extensions to augment its core hypermedia infrastructure. Extensions hook into standard events rather than callback extension points. They are lightweight with no performance penalty and apply page-wide without requiring `hx-ext` on parent elements.

## Loading Extensions

Include the extension script after htmx:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta2/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta2/dist/ext/hx-sse.js"></script>
```

With a bundler:

```javascript
import 'htmx.org';
import 'htmx.org/dist/ext/hx-sse';
```

### Restricting Extensions

Use an allow list via meta tag:

```html
<meta name="htmx-config" content='{"extensions": "my-ext,another-ext"}'>
```

Without this config, all registered extensions are active.

## Core Extensions

Extensions maintained by the htmx team and shipped with htmx:

- **sse** — Server-Sent Events streaming
- **ws** — WebSocket bidirectional communication
- **head-support** — Merge `<head>` tag information (styles, scripts) in responses
- **preload** — Preload content on hover or other events
- **browser-indicator** — Show browser's native loading indicator during requests
- **alpine-compat** — Compatibility with Alpine.js
- **htmx-2-compat** — Compatibility layer for htmx 2.x code (restores implicit inheritance, old event names, error-swapping defaults)
- **optimistic** — Optimistic UI updates
- **upsert** — Update-or-insert swap strategy for dynamic lists
- **download** — Save responses as file downloads with streaming progress
- **ptag** — Per-element polling tags to skip unchanged content
- **targets** — Swap the same response into multiple elements
- **history-cache** — Client-side history cache in `sessionStorage` for instant back/forward navigation

## SSE Extension

Server-Sent Events provide a unidirectional stream from server to client.

```html
<div hx-sse:connect="/stream">
  <div hx-sse="message" hx-target="#output"></div>
</div>
<div id="output"></div>
```

`hx-sse:connect` establishes the SSE connection. `hx-sse="eventName"` listens for specific event types on the stream.

## WebSocket Extension

WebSockets provide bidirectional real-time communication.

```html
<div hx-ws:connect="/ws">
  <form hx-ws="send">
    <input name="message">
    <button type="submit">Send</button>
  </form>
</div>
```

`hx-ws:connect` establishes the WebSocket connection. `hx-ws="send"` sends form data over the socket.

## Building Custom Extensions

htmx 4 uses an event-based extension API (replacing the callback-based API from htmx 2.x).

### Defining an Extension

```javascript
htmx.registerExtension("my-ext", {
  init: (internalAPI) => {
    // Called once when extension is registered
    // Store internalAPI reference if needed
  },
  htmx_before_request: (elt, detail) => {
    // Called before each request
    return false; // Return false to cancel
  },
  htmx_after_request: (elt, detail) => {
    // Called after each request completes
  },
});
```

### Event Hooks

Event names use underscores instead of colons:

**Core Lifecycle:**
- `htmx_before_init` / `htmx_after_init` — element initialization
- `htmx_before_process` / `htmx_after_process` — element processing
- `htmx_before_cleanup` / `htmx_after_cleanup` — element cleanup

**Request Lifecycle:**
- `htmx_config_request` — configure request before sending
- `htmx_before_request` — before request is sent
- `htmx_before_response` — after fetch, before body consumed
- `htmx_after_request` — after request completes
- `htmx_finally_request` — always called after request
- `htmx_error` — on request error

**Swap Events:**
- `htmx_before_swap` / `htmx_after_swap` — content swap
- `htmx_before_settle` / `htmx_after_settle` — settle phase
- `handle_swap` — custom swap handler (direct call)

**History Events:**
- `htmx_before_history_update` / `htmx_after_history_update`
- `htmx_after_history_push` / `htmx_after_history_replace`
- `htmx_before_history_restore`

### Cancelling Events

Return `false` or set `detail.cancelled = true`:

```javascript
htmx.registerExtension("validator", {
  htmx_before_request: (elt, detail) => {
    if (!isValid(detail.ctx)) {
      return false; // Cancel request
    }
  },
});
```

### Internal API

The `init` hook receives an internal API object:

```javascript
let api;
htmx.registerExtension("my-ext", {
  init: (internalAPI) => { api = internalAPI; },
  htmx_after_init: (elt) => {
    let value = api.attributeValue(elt, "hx-my-attr");
    let specs = api.parseTriggerSpecs("click, keyup delay:500ms");
    let { method, action } = api.determineMethodAndAction(elt, evt);
  },
});
```

Available methods:
- `attributeValue(elt, name, defaultVal, returnElt)` — get attribute value with inheritance
- `parseTriggerSpecs(spec)` — parse trigger specification string
- `determineMethodAndAction(elt, evt)` — get HTTP method and URL
- `createRequestContext(elt, evt)` — create request context object
- `collectFormData(elt, form, submitter)` — collect form data
- `handleHxVals(elt, body)` — process `hx-vals` attribute

### Custom Swap Strategies

```javascript
htmx.registerExtension("my-swap", {
  handle_swap: (swapStyle, target, fragment, swapSpec) => {
    if (swapStyle === "my-custom-swap") {
      target.appendChild(fragment);
      return true; // Handled
    }
    return false; // Not handled
  },
});
```

### Request Context

The `detail.ctx` object contains request information:

```javascript
{
  sourceElement,    // Element triggering request
  sourceEvent,      // Event that triggered request
  status,           // Request status
  target,           // Target element for swap
  swap,             // Swap strategy
  request: {
    action,         // Request URL
    method,         // HTTP method
    headers,        // Request headers
    body,           // Request body (FormData)
    validate,       // Whether to validate
    abort,          // Function to abort request
    signal,         // AbortSignal
  },
  response: {       // Available after request
    raw,            // Raw Response object
    status,         // HTTP status code
    headers,        // Response headers
  },
  text,             // Response text (after request)
  hx                // HX-* response headers (parsed)
}
```
