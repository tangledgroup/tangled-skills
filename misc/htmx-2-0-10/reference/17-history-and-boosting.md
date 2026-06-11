# History and Boosting

Browser history management, back-button support, and progressive enhancement via boosting.

## hx-push-url

Push a new URL into the browser address bar after an AJAX request. This enables back-button navigation.

```html
<button hx-get="/items/42"
        hx-push-url="true"
        hx-target="#main">
  Load Item
</button>
```

URL is automatically set to the request path. Customize with explicit URL:

```html
<button hx-get="/items/42"
        hx-push-url="/items/42?tab=details"
        hx-target="#main">
  Load with custom URL
</button>
```

### History Snapshots

When `hx-push-url` is used, htmx saves a snapshot of the `<body>` (or `hx-history-elt`) to an in-memory cache. On back-button press:
1. htmx restores the snapshot from cache
2. Fires `htmx:afterHistoryRestore` event
3. URL updates to the cached entry

### Cache Miss Handling

If the history cache miss occurs (e.g., page was reloaded and cache lost):
- Default: full page reload (`htmx.config.refreshOnHistoryMiss = false` by default means it does NOT reload)
- Set `htmx.config.refreshOnHistoryMiss = true` for full reload on cache miss

```javascript
htmx.config.refreshOnHistoryMiss = true;
```

## hx-replace-url

Same as `hx-push-url` but replaces the current history entry instead of pushing a new one. No back-button entry created.

```html
<div hx-get="/feed"
     hx-trigger="every 30s"
     hx-replace-url="true">
  Live feed (URL updates but no history entry)
</div>
```

## hx-history-elt

Use a specific element instead of `<body>` for history snapshots:

```html
<body hx-boost="true">
  <header>...</header>
  <main id="app" hx-history-elt="#app">
    <!-- Only this element is snapshotted -->
  </main>
  <footer>...</footer>
</body>
```

Useful when parts of the page (sidebar, header) should not be part of history snapshots.

## hx-history

Disable history caching for a specific element:

```html
<div hx-history="false">
  <!-- This content is excluded from history snapshots -->
  <div id="live-clock"></div>
</div>
```

## hx-boost

Progressively enhance links and forms to use AJAX. Falls back to normal navigation if JavaScript is disabled.

### Boosting a Whole Page

```html
<body hx-boost="true">
  <!-- All <a> and <form> elements inside are boosted -->
  <a href="/items/42">Loads via AJAX</a>
  <form action="/search" method="get">
    <input name="q" />
  </form>
</body>
```

### Boosting Specific Elements

```html
<a href="/page" hx-boost="true">AJAX navigation</a>
<a href="/page">Normal navigation (no hx-boost)</a>
```

### Disabling Boost Inheritance

```html
<body hx-boost="true">
  <div hx-boost="false">
    <a href="/external">Normal navigation</a>
  </div>
</body>
```

### How Boosting Works

1. `<a href="...">` → converted to `hx-get` with the href value
2. `<form action="..." method="get|post">` → converted to `hx-get` or `hx-post`
3. Response is swapped into `<body>` (for boosted links) or form's target
4. `<title>` from response updates document title
5. URL is pushed via `hx-push-url`
6. If JS disabled, normal navigation works (progressive enhancement)

### Graceful Degradation

Boosted links work without JavaScript — they fall back to standard HTTP navigation. This is the key advantage over `hx-get` on buttons.

## 3rd Party Library History Cleanup

When using libraries that create DOM state (charts, editors, selects), clean up before saving history:

```javascript
// Before saving snapshot
document.body.addEventListener('htmx:beforeHistorySave', function(evt) {
  // Destroy TomSelect instances
  document.querySelectorAll('.tom-select').forEach(function(el) {
    if (el.tomselect) el.tomselect.destroy();
  });
  // Destroy Sortable instances
  document.querySelectorAll('.sortable').forEach(function(el) {
    if (el._sortable) el._sortable.destroy();
  });
});

// After restoring from history
document.body.addEventListener('htmx:afterHistoryRestore', function(evt) {
  // Re-initialize
  document.querySelectorAll('.tom-select').forEach(function(el) {
    new TomSelect(el, { /* options */ });
  });
  document.querySelectorAll('.sortable').forEach(function(el) {
    new Sortable(el, { /* options */ });
  });
});
```

## History Configuration

```javascript
htmx.config.historyEnabled = true;           // Enable/disable history
htmx.config.historyCacheSize = 10;            // Number of cached pages
htmx.config.refreshOnHistoryMiss = false;     // Reload on cache miss?
```
