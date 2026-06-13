# Migration and Quirks

Migration guides from older versions and other frameworks, plus known quirks and edge cases.

## htmx 1.x to 2.x Migration

### Breaking Changes

| Area | htmx 1 | htmx 2 |
|------|--------|--------|
| `hx-ws` | Built-in attribute | Removed — use ws extension with `ws-connect`/`ws-send` |
| `hx-sse` | Built-in attribute | Removed — use sse extension with `sse-connect`/`sse-swap` |
| `hx-on` | Single attribute for events | Removed — use `hx-on::*` wildcard attributes |
| `selfRequestsOnly` | `false` (cross-origin allowed) | `true` (same-origin only) |
| `scrollBehavior` | `"smooth"` | `"instant"` |
| DELETE requests | Form-encoded body | URL params (per RFC 9110) |
| `hx-on:click` | Valid syntax | Use `hx-on::click` (double colon) |

### Migration Steps

1. Replace `hx-ws=""` → `hx-ext="ws"` + `ws-connect`/`ws-send`
2. Replace `hx-sse=""` → `hx-ext="sse"` + `sse-connect`/`sse-swap`
3. Replace `hx-on:eventname="..."` → `hx-on::eventname="..."`
4. If using cross-origin requests, set `htmx.config.selfRequestsOnly = false`
5. If relying on smooth scroll, set `htmx.config.scrollBehavior = 'smooth'`
6. Review DELETE request handling (URL params vs body)

### Quick Compat

Use the `htmx-1-compat` extension to restore most defaults:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-htmx-1-compat@2.0.2"></script>
<body hx-ext="htmx-1-compat">
```

See reference file `09-core-extensions-1-compat.md` for details.

## intercooler.js Migration

intercooler.js was the predecessor to htmx. Most attributes map directly:

| intercooler | htmx |
|-------------|------|
| `ic-src` | `hx-get` |
| `ic-post-to` | `hx-post` |
| `ic-trigger` | `hx-trigger` |
| `ic-target` | `hx-target` |
| `ic-push-history-url` | `hx-push-url` |
| `ic-replace-history` | `hx-replace-url` |
| `ic-include-fields` | `hx-include` |
| `ic-headers` | `hx-headers` |
| `ic-select-on` | `hx-select` |
| `ic-deps` | `path-deps` extension |

## Hotwire / Turbo Migration

| Hotwire/Turbo | htmx |
|---------------|------|
| `<turbo-frame>` | `hx-get` with `hx-target` |
| `data-turbo-frame` | `hx-target` |
| `data-turbo-action="advance"` | `hx-push-url` |
| `data-turbo-action="replace"` | `hx-replace-url` |
| `<turbo-stream>` | `hx-swap-oob` |
| `data-turbo-confirm` | `hx-confirm` |
| Turbo Drive | `hx-boost` |
| `data-turbo-track` | Not directly — use cache-busting or ETags |

## Known Quirks

### Event Order

htmx events fire in this order:
1. `htmx:beforeRequest`
2. `htmx:beforeSend`
3. (XHR completes)
4. `htmx:afterRequest`
5. `htmx:beforeOnLoad`
6. `htmx:beforeSwap`
7. DOM swap occurs
8. `htmx:afterSwap`
9. `htmx:beforeSettle`
10. Attribute settling
11. `htmx:afterSettle`
12. `htmx:load`
13. `htmx:afterOnLoad`

### hx-on::* Double Colon

htmx 2 uses double colon (`hx-on::eventname`) to distinguish from custom events. Single colon was deprecated in htmx 1 and removed in htmx 2.

```html
<!-- htmx 1 (deprecated) -->
<button hx-on:click="alert('hi')">Click</button>

<!-- htmx 2 (correct) -->
<button hx-on::click="alert('hi')">Click</button>
```

### Form Submission and hx-post

When using `hx-post` on a `<form>`, the natural trigger is `submit`. The form's `action` attribute is ignored unless boosted.

```html
<form hx-post="/save">
  <!-- action="/other" is ignored -->
</form>
```

### Script Tags in Responses

By default, `<script>` tags in htmx responses are executed. Disable with:

```javascript
htmx.config.allowScriptTags = false;
```

### hx-target and Forms

`hx-target` on a form element targets the swap location. Without it, the form itself is the target.

### Boosted Links and External URLs

`hx-boost` only applies to same-origin links. External links navigate normally.

### Polling and Page Visibility

htmx does not automatically pause polling when the tab is hidden. Use the `visibilitychange` event:

```html
<div hx-get="/data"
     hx-trigger="every 5s"
     hx-on::visibility-change="if(evt.detail.hidden) htmx.trigger(this, 'abort'); else htmx.trigger(this, 'load')">
</div>
```

### hx-swap-oob and Template Elements

Use `<template>` for OOB swaps of table rows to avoid breaking table structure:

```html
<template hx-swap-oob="true">
  <tr id="row-1"><td>Data</td></tr>
</template>
```

### Response Codes and Swapping

By default, htmx only swaps on `200-299` responses. Other codes fire `htmx:responseError`. Customize via `htmx.config.responseHandling`.
