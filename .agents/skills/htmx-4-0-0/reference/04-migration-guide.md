# Migration Guide from htmx 2.x to 4.x

## Quick Start

Two major behavioral changes between htmx 2.x and 4.x:

1. **Attribute inheritance** is explicit by default (was implicit in 2.x)
2. **400/500 response codes** are swapped by default (were not swapped in 2.x)

Restore htmx 2.x behavior with two config lines:

```html
<script>
  htmx.config.implicitInheritance = true;
  htmx.config.noSwap = [204, 304, '4xx', '5xx'];
</script>
<script src="https://cdn.jsdelivr.net/npm/htmx.org@next/dist/htmx.min.js"></script>
```

Or load the `htmx-2-compat` extension, which restores implicit inheritance, old event names, and previous error-swapping defaults:

```html
<script src="/path/to/htmx.js"></script>
<script src="/path/to/ext/htmx-2-compat.js"></script>
```

Most htmx 2 apps should work with either approach. Then migrate incrementally.

## Upgrade Checker

htmx 4 ships with a command-line tool that scans your templates and JS files for htmx 2 code needing updates:

```bash
npx htmx.org@next upgrade-check -- ./path/to/project/root
npx htmx.org@next upgrade-check --ext .vue ./path/to/project/root
```

Scans `.html`, `.php`, `.js`, `.ts`, `.jinja`, `.jinja2`, `.j2`, `.erb`, and `.hbs` files by default. Output is `file:line` format, clickable in most editors. Requires Python 3.

## What Changed

### `fetch()` replaces `XMLHttpRequest`

All requests use the native `fetch()` API. This cannot be reverted. Benefits include better streaming support, standard AbortController integration, and modern error handling.

### Explicit Attribute Inheritance

In htmx 2.x, child elements implicitly inherited parent attributes like `hx-target`. In 4.x, use the `:inherited` modifier:

```html
<!-- htmx 2.x (implicit) -->
<div hx-target="#main">
  <button hx-get="/page1">Page 1</button>
  <button hx-get="/page2">Page 2</button>
</div>

<!-- htmx 4.x (explicit) -->
<div hx-target:inherited="#main">
  <button hx-get="/page1">Page 1</button>
  <button hx-get="/page2">Page 2</button>
</div>
```

### Error Responses Are Swapped

In htmx 4.x, `4xx` and `5xx` responses are swapped into the DOM by default. This allows error pages to be rendered as HTML and displayed inline. To restore old behavior:

```javascript
htmx.config.noSwap = [204, 304, '4xx', '5xx'];
```

### History Support Changed

htmx 4.x no longer snapshots the DOM into `sessionStorage`. Instead, it issues a full page request on history navigation. This is more reliable and eliminates security concerns with accessible storage.

If you need client-side caching for instant back/forward, use the `history-cache` extension.

### Extension API Changed Completely

The callback-based API from htmx 2.x is replaced with event hooks:

| htmx 2.x | htmx 4.x | Migration Notes |
|----------|----------|-----------------|
| `init(api)` | `init(api)` | Same name, store API reference for other hooks |
| `getSelectors()` | `htmx_after_init` | Check `api.attributeValue(elt, "attr")` instead of returning selectors |
| `onEvent(name, evt)` | Specific hooks | Replace with `htmx_before_request`, `htmx_after_swap`, etc. (use underscores) |
| `transformResponse(text, xhr, elt)` | `htmx_after_request` | Modify `detail.ctx.text` directly |
| `isInlineSwap(swapStyle)` | `handle_swap` | Return `true` if handled, `false` if not |

Event hook names use underscores instead of colons: `htmx_before_request` instead of `htmx:beforeRequest`.

### Event Names

htmx 4 supports both camelCase and kebab-case event names. The kebab-case form works with `hx-on:*`:

```html
<!-- Both work in htmx 4 -->
<button hx-on:htmx:before-request="...">...</button>
<button hx-on:htmx:beforeRequest="...">...</button>
<!-- Shorthand for htmx events -->
<button hx-on::before-request="...">...</button>
```

### New Swap Strategies

- `innerMorph` / `outerMorph` — morph-based DOM updates via idiomorph, preserving state and focus
- `upsert` — update-or-insert by ID (requires upsert extension)
- `textContent` — safe text replacement without HTML parsing

### CSS Transitions

htmx 4 supports the View Transitions API via the `transition:true` swap modifier:

```html
<div hx-swap="innerHTML transition:true"></div>
```

Enable globally: `htmx.config.transitions = true`.

### Boost Configuration

`hx-boost` now accepts a config string for fine-grained control:

```html
<body hx-boost:inherited='swap:"innerHTML", target:"#main", select:"#content"'>
```

## Common Migration Patterns

### Adding `:inherited` to parent attributes

Find parent elements with htmx attributes and add `:inherited`:

```html
<!-- Before (htmx 2) -->
<form hx-post="/save" hx-target="#result">
  <button>Save</button>
</form>

<!-- After (htmx 4) -->
<form hx-post="/save" hx-target:inherited="#result">
  <button>Save</button>
</form>
```

### Handling error responses

If your server returns 400/500 with HTML error pages, they will now be displayed inline. If you want to handle errors differently:

```javascript
document.body.addEventListener('htmx:afterRequest', (evt) => {
  if (evt.detail.xhr.status >= 400) {
    // Custom error handling
  }
});
```

### Migrating extensions

Replace callback-based hooks with event-based hooks. See the [Extensions](reference/03-extensions.md) reference for the new API.
