# Community Extensions: Utility

Utility extensions for paths, headers, debugging, caching, and misc functionality.

## path-deps

Express inter-element dependencies based on URLs (inspired by intercooler.js). When one element makes a request, dependent elements are also refreshed.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-path-deps@2.0.0/path-deps.js"></script>
```

### Usage
```html
<!-- When cart updates, also refresh the total and badge -->
<div hx-post="/cart/add"
     path-deps="/cart/total /cart/badge">
  <button>Add to Cart</button>
</div>

<div id="total" hx-get="/cart/total"></div>
<div id="badge" hx-get="/cart/badge"></div>
```

### Dependency Declaration

```html
<!-- This element depends on /items/list — refresh when that path is hit -->
<div hx-get="/items/count"
     path-deps-push="/items/list">
  Item count
</div>
```

| Attribute | Description |
|-----------|-------------|
| `path-deps="<paths>"` | These paths depend on the current element's request |
| `path-deps-push="<paths>"` | This element depends on these paths |

---

## path-params

Populate URL path variables from request parameters. Used params are removed from query string/body.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-path-params@2.0.0/path-params.js"></script>
```

### Usage
```html
<form hx-post="/items/{id}/activate"
      hx-ext="path-params">
  <input name="id" value="42" />
  <button type="submit">Activate</button>
</form>
```

Sends POST to `/items/42/activate` with `id` removed from body.

---

## event-header

Adds a `Triggering-Event` header (JSON-serialized event) to requests.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-event-header@2.0.0/event-header.js"></script>
```

### Usage
```html
<button hx-post="/api"
        hx-ext="event-header">
  Click (sends triggering event in header)
</button>
```

Server receives `Triggering-Event: {"type":"click","target":"button",...}`.

---

## ajax-header

Adds `X-Requested-With: XMLHttp` or configurable header to all htmx requests.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-ajax-header@2.0.0/ajax-header.js"></script>
```

### Usage
```html
<body hx-ext="ajax-header">
  <!-- All requests now include X-Requested-With header -->
</body>
```

---

## debug

Log all htmx events for a specific element via `console.debug`.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-debug@2.0.0/debug.js"></script>
```

### Usage
```html
<div hx-get="/data" hx-ext="debug">
  <!-- All htmx events for this element logged to console -->
</div>
```

> Note: In development, `htmx.logAll()` is often sufficient without this extension.

---

## no-cache

Force htmx to bypass client and server caches by adding cache-busting parameters and headers.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-no-cache@1.0.0/no-cache.js"></script>
```

### Usage
```html
<div hx-get="/data"
     hx-ext="no-cache"
     hx-trigger="every 5s">
  <!-- Always fetches fresh data, bypassing all caches -->
</div>
```

Adds `HX-No-Cache: true` header and cache-busting query parameter.

---

## restored

Triggers an event when browser back-button is detected during `hx-boost` navigation.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-restored@2.0.0/restored.js"></script>
```

### Usage
```html
<body hx-boost="true" hx-ext="restored">
  <div hx-on::restored="console.log('Page restored from history')">
    Content
  </div>
</body>
```

Fires `restored` event on elements when back/forward navigation occurs.

---

## safe-nonce

Improve CSP security by allowing known trusted inline scripts through nonce validation.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-safe-nonce@1.0.0/safe-nonce.js"></script>
```

### Usage
```html
<head>
  <meta http-equiv="Content-Security-Policy"
        content="script-src 'nonce-abc123'">
</head>
<body hx-ext="safe-nonce"
      hx-safe-nonce-meta-selector="meta[csp-hx-nonce]">
  <!-- Inline scripts in responses get nonce applied -->
</body>
```

Helps avoid XSS issues with Content Security Policy by safely applying nonces to inline scripts returned in htmx responses.

---

## dynamic-url

Dynamic URL path templating using `{varName}` placeholders resolved via custom function or `window.` fallback.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-dynamic-url@1.0.0/dynamic-url.js"></script>
```

### Usage
```html
<div hx-ext="dynamic-url">
  <button hx-get="/users/{userId}/profile">
    Profile (resolves userId from window.app.userId)
  </button>
</div>

<script>
  window.app = { userId: 42 };
</script>
```

Useful when request paths depend on application state without using `hx-vals`.

---

## optimistic

Optimistically update the UI before the server response arrives for improved perceived performance.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-optimistic@1.0.0/optimistic.js"></script>
```

### Usage
```html
<form hx-post="/items"
      hx-ext="optimistic"
      optimistic-get="#optimistic-template">
  <input name="name" />
  <button type="submit">Add</button>
</form>

<template id="optimistic-template">
  <div class="item optimistic">
    <span class="name"></span>
    <span class="status">Adding...</span>
  </div>
</template>
```

Shows template immediately, replaces with server response when it arrives. Reverts on error.

---

## disable-element (Legacy)

> ⚠️ Superseded by core `hx-disabled-elt` attribute in htmx 2.

Disables the element during an htmx request. Use `hx-disabled-elt="this"` instead.

---

## include-vals (Legacy)

> ⚠️ Superseded by core `hx-vals` attribute in htmx 2.

Programmatically include values in requests. Use `hx-vals='{"key":"value"}'` instead.
