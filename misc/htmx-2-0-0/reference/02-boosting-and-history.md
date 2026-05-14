# Boosting and History

## Boosting (`hx-boost`)

`hx-boost` converts regular `<a>` tags and `<form>` elements into AJAX requests with graceful fallback to full-page navigation when JavaScript is disabled.

Place `hx-boost="true"` on a container element to boost all links and forms within it:

```html
<div hx-boost="true">
    <a href="/blog">Blog</a>
    <a href="/page2">Page 2</a>
</div>
```

For anchors, clicking issues a GET request and pushes the URL into history. The target is `<body>` with `innerHTML` swap by default.

For forms, the request uses GET or POST based on the `method` attribute, triggered by `submit`. The target is `<body>`. No URL is pushed automatically (use `hx-push-url` if needed).

### Progressive Enhancement

`hx-boost` degrades gracefully — without JavaScript, links and forms work with normal full-page navigation. This is known as progressive enhancement.

For non-boosted patterns, wrap htmx-enhanced inputs in a form for fallback:

```html
<form action="/search" method="GET">
    <input type="search" name="q"
           hx-get="/search"
           hx-trigger="keyup changed delay:500ms"
           hx-target="#results">
</form>
<div id="results"></div>
```

JavaScript-enabled users get live search; non-JS users press Enter for a full-page search.

### Notes

- `hx-boost` is inherited by child elements
- Only same-domain links are boosted (not local anchors or cross-domain)
- All requests use AJAX, so server-side redirects need care
- On the server, check `HX-Request: true` header to detect boosted requests

## History Management

htmx integrates with the browser history API to support back/forward navigation.

### Pushing URLs (`hx-push-url`)

Include `hx-push-url="true"` to push the request URL into the browser location bar and snapshot the current page state:

```html
<a hx-get="/blog" hx-push-url="true">Blog</a>
```

When clicked, htmx snapshots the DOM, makes the request, swaps the response, and pushes a new history entry. On back-button press, htmx restores the old content from cache.

If the page is not in cache (miss), htmx makes an AJAX request with `HX-History-Restore-Request: true` header. Set `htmx.config.historyRestoreAsHxRequest = false` to prevent this from also setting `HX-Request`, allowing your server to distinguish history restore requests from normal htmx requests.

### Important Rule

If you push a URL into history, you must be able to navigate to that URL and get a full page back. Users can copy/paste the URL. htmx needs the entire page when restoring from a cache miss.

### Replace URL (`hx-replace-url`)

Like `hx-push-url` but replaces the current history entry instead of adding a new one:

```html
<button hx-post="/update" hx-replace-url="true">Update</button>
```

### History Snapshot Element (`hx-history-elt`)

By default, htmx snapshots `<body>`. Override with `hx-history-elt`:

```html
<div id="main-content" hx-history-elt="this">
    <!-- content to snapshot -->
</div>
```

This element must be present on all pages for reliable history restoration.

### Preventing History Cache (`hx-history`)

Exclude sensitive pages from the history cache:

```html
<div hx-history="false">
    <!-- sensitive content not cached -->
</div>
```

Or set `htmx.config.historyCacheSize = 0` to disable caching entirely.

### Undoing 3rd-Party DOM Mutations

If a library mutates the DOM and you use history, use `hx-on::htmx:before-history-save` to undo changes before snapshotting:

```html
<div hx-on::htmx:before-history-save="myLib.undoChanges()">
    <!-- content managed by myLib -->
</div>
```

### Configuration

- **`htmx.config.historyEnabled`** — `true` by default, disable for testing
- **`htmx.config.historyCacheSize`** — Default 10 entries
- **`htmx.config.refreshOnHistoryMiss`** — If `true`, do full page refresh on cache miss instead of AJAX
- **`htmx.config.historyRestoreAsHxRequest`** — Default `true`. Set to `false` when using `HX-Request` header for partial responses
