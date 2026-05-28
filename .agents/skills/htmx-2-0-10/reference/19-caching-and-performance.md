# Caching and Performance

HTTP caching strategies, cache-busting, and performance optimization with htmx.

## HTTP Caching

htmx respects standard HTTP caching headers. The browser may serve cached responses for GET requests.

### Last-Modified / If-Modified-Since

```
GET /data
→ 200 OK (Last-Modified: Wed, 21 Oct 2025 07:28:00 GMT)

GET /data
→ If-Modified-Since: Wed, 21 Oct 2025 07:28:00 GMT
→ 304 Not Modified (no body sent)
```

htmx handles `304` responses automatically — no swap occurs.

### ETag / If-None-Match

```
GET /data
→ 200 OK (ETag: "abc123")

GET /data
→ If-None-Match: "abc123"
→ 304 Not Modified
```

### Vary Header with HX-Request

Tell the cache to differentiate between normal and htmx requests:

```
Vary: HX-Request
```

This ensures the cache serves full pages to normal requests and partial fragments to htmx AJAX requests.

## Cache Busting

### getCacheBusterParam

Append a timestamp to GET request URLs to bypass cache:

```javascript
htmx.config.getCacheBusterParam = function() {
  return Date.now().toString();
};
```

Appends `?__htmx=1716800000000` to GET requests.

### no-cache Extension

For specific elements, use the `no-cache` community extension:

```html
<div hx-get="/data"
     hx-ext="no-cache"
     hx-trigger="every 5s">
  Always fresh data
</div>
```

## Preload Extension for Perceived Performance

Preload likely-next pages before the user navigates:

```html
<body hx-ext="preload">
  <nav>
    <a href="/dashboard" preload>Dashboard</a>
    <a href="/settings" preload>Settings</a>
  </nav>
</body>
```

On `mousedown`, the page is fetched and cached. When the user actually clicks, the response appears nearly instant.

## triggerSpecsCache

Cache parsed trigger specifications for performance:

```javascript
htmx.config.triggerSpecsCache = new Map();
```

Enables caching of `hx-trigger` parsing results across elements with identical trigger strings.

## Performance Tips

### Minimize Swap Targets

Smaller DOM regions swap faster. Target specific elements rather than large containers:

```html
<!-- Better: target specific cell -->
<button hx-get="/status" hx-target="#status-cell">Refresh</button>

<!-- Slower: swaps entire row -->
<button hx-get="/status" hx-target="closest tr">Refresh</button>
```

### Use hx-select to Reduce Response Size

```html
<div hx-get="/page" hx-select="#widget-only">
  <!-- Only this part of response is used -->
</div>
```

Server can return full page but only the selected fragment is processed.

### Avoid Unnecessary Polling

Use conditional polling — stop when data is current:

```html
<div hx-get="/notifications"
     hx-trigger="every 10s"
     hx-on::after-request="if(!htmx.find('.has-new')) this.removeAttribute('hx-trigger')">
</div>
```

### Use hx-sync for Rapid Events

Prevent request pileup on rapid keyup:

```html
<input hx-get="/search"
       hx-trigger="keyup changed delay:300ms"
       hx-sync="this:abort" />
```

`abort` cancels in-flight requests when new ones fire.

### Use morph Instead of innerHTML

For large DOM updates, morphing reuses nodes and avoids re-initialization overhead:

```html
<div hx-get="/data" hx-swap="morph">
  <!-- Preserves event listeners and input state -->
</div>
```
