# AJAX Requests

Core htmx mechanics for making HTTP requests from HTML attributes.

## Core Request Attributes

| Attribute | Method | Description |
|-----------|--------|-------------|
| `hx-get` | GET | Fetch content from the server |
| `hx-post` | POST | Submit data to the server |
| `hx-put` | PUT | Replace a resource on the server |
| `hx-patch` | PATCH | Partially update a resource |
| `hx-delete` | DELETE | Delete a resource (uses URL params per RFC 9110) |

```html
<button hx-get="/items/42" hx-target="#result">Load Item</button>
<form hx-post="/items" hx-target="#list">
  <input name="name" />
  <button type="submit">Add</button>
</form>
```

## Triggers (`hx-trigger`)

Controls when a request fires. Default is the natural event (`click` for buttons, `change` for inputs, `submit` for forms).

### Natural Events
```html
<input hx-get="/search" hx-trigger="keyup" />
<button hx-post="/action" hx-trigger="mouseenter">Hover Me</button>
```

### Event Modifiers

| Modifier | Syntax | Example |
|----------|--------|---------|
| Throttle | `throttle:<ms>` | `hx-trigger="keyup throttle:300ms"` |
| Rate | `rate:<ms>` | `hx-trigger="keyup rate:1s"` (fires once per interval) |
| Changed | `changed` | `hx-trigger="change changed"` (only if value changed) |
| Once | `once` | `hx-trigger="click once"` (fire only once) |
| From | `from:<selector>` | `hx-trigger="click from:body"` (listen elsewhere) |
| Target | `target:<selector>` | `hx-trigger="click target:.btn"` (filter by target) |
| Not | `not:<selector>` | `hx-trigger="click not:.disabled"` (exclude targets) |
| Consumed | `consumed` | `hx-trigger="click consumed"` (stop propagation) |
| Queue | `queue:<strategy>` | `hx-trigger="keyup queue:none"` or `queue:last` or `queue:drop` or `queue:take` |

### Multiple Triggers
```html
<input hx-get="/search" hx-trigger="keyup changed delay:300ms, enter" />
```

### Special Events

| Event | Description |
|-------|-------------|
| `load` | Fires when element is processed by htmx |
| `intersect` | Fires when element enters viewport (IntersectionObserver) |
| `every` | Fires on interval: `hx-trigger="every 3s"` |
| `pageshow` | Fires on back-button restore |

### Intersection Options
```html
<div hx-get="/more" hx-trigger="intersect once"
     hx-on::before-request="htmx.trigger(this, 'removeMe')">
  Load more content
</div>
```

### Polling
```html
<!-- Simple polling -->
<div hx-get="/status" hx-trigger="every 5s"></div>

<!-- Polling with indicator -->
<div hx-get="/status" hx-trigger="every 2s" hx-indicator="#spinner"></div>

<!-- Conditional polling via hx-on -->
<div hx-get="/notifications"
     hx-trigger="every 10s"
     hx-on::after-request="if(htmx.find('.has-new')) this.removeAttribute('hx-trigger')">
</div>
```

## Targets (`hx-target`)

Specifies where the response content is swapped into.

### CSS Selectors
```html
<button hx-get="/data" hx-target="#result">Load</button>
```

### Extended Selectors

| Value | Description |
|-------|-------------|
| `this` | The element with the attribute |
| `closest <selector>` | Closest ancestor matching selector |
| `find <selector>` | First descendant matching selector |
| `next <selector>` | Next sibling matching selector |
| `previous <selector>` | Previous sibling matching selector |
| `body` | The `<body>` element |

```html
<tr>
  <td>
    <button hx-delete="/items/1"
            hx-target="closest tr"
            hx-swap="outerHTML swap:1s">
      Delete
    </button>
  </td>
</tr>
```

## Parameters

### `hx-include` — Include Additional Fields

```html
<form id="my-form">
  <input name="name" value="John" />
</form>
<button hx-post="/save" hx-include="#my-form">Save All</button>
```

### `hx-params` — Filter Parameters

| Value | Description |
|-------|-------------|
| `*` | Include all params (default) |
| `none` | Include no params |
| `not field1,field2` | Exclude specific fields |
| `only field1,field2` | Include only specific fields |

```html
<form hx-post="/save" hx-params="not password,csrf_token">
  <input name="name" />
  <input name="password" type="password" />
</form>
```

### `hx-vals` — Add Extra Values (Static JSON)

```html
<button hx-post="/api/items"
        hx-vals='{"format": "json", "version": 2}'>
  Submit
</button>
```

### `hx-vars` — Add Dynamic Values (JavaScript Expressions)

> ⚠️ Requires `htmx.config.allowEval = true`. Prefer `hx-vals` with static data.

```html
<button hx-post="/api/items"
        hx-vars='{"timestamp": Date.now(), "scrollY": window.scrollY}'>
  Submit
</button>
```

### File Uploads

Use standard `<input type="file">` inside an `hx-post` form. htmx automatically uses `FormData` for file uploads.

```html
<form hx-post="/upload" hx-encoding="multipart/form-data">
  <input name="file" type="file" />
  <button type="submit" hx-disable>Upload</button>
</form>
```

### `hx-encoding`

| Value | Description |
|-------|-------------|
| `multipart/form-data` | For file uploads |
| `application/x-www-form-urlencoded` | Default form encoding |

## Request Indicators (`hx-indicator`)

Shows a loading indicator while the request is in flight. The element gets class `htmx-request` added/removed.

```html
<button hx-post="/save" hx-indicator="#spinner">
  Save
  <span id="spinner" class="htmx-indicator">Loading...</span>
</button>

<style>
  .htmx-indicator { display: none; }
  .htmx-request .htmx-indicator { display: inline; }
  .htmx-indicator.htmx-request { display: inline; }
</style>
```

## `hx-disabled-elt` — Disable Elements During Request

```html
<form hx-post="/save" hx-disabled-elt="find button">
  <input name="name" />
  <button type="submit">Save (will be disabled during request)</button>
</form>
```

Uses same extended selector syntax as `hx-target`.

## Synchronization (`hx-sync`)

Controls how concurrent requests are handled on the same element.

| Strategy | Description |
|----------|-------------|
| `drop` | Drop the new request if one is already in flight (default) |
| `queue` | Queue the new request, fire after current completes |
| `abort` | Abort the current request, start the new one |
| `replace` | Abort current and replace with the new request |
| `none` | Allow concurrent requests |

```html
<input hx-get="/search"
       hx-trigger="keyup changed delay:300ms"
       hx-sync="this:abort" />
```

Scope modifiers: `this`, `closest <selector>`, `body`.

## Headers (`hx-headers`)

Add custom headers to requests:

```html
<button hx-post="/api/data"
        hx-headers='{"X-CSRF-Token": "abc123", "Accept": "application/json"}'>
  Submit
</button>
```

htmx automatically adds:
- `HX-Request: true`
- `HX-Trigger: <trigger-element-id>`
- `HX-Trigger-Name: <trigger-element-name>`
- `HX-Target: <target-value>`
- `HX-Current-URL: <current-url>`

## hx-on* Inline Scripting

Attach event handlers directly in HTML:

```html
<button hx-post="/save"
        hx-on::before-request="this.textContent = 'Saving...'"
        hx-on::after-request="this.textContent = 'Saved!'"
        hx-on::error="this.textContent = 'Error!'">
  Save
</button>
```

Available events: `::before-request`, `::after-request`, `::before-swap`, `::after-swap`, `::before-on-load`, `::after-on-load`, `::abort`, `::config-request`, etc.

## hx-request

Fine-grained request configuration:

```html
<button hx-post="/api/data"
        hx-request='{
          "timeout": 5000,
          "credentials": "include",
          "headers": {"X-Custom": "value"},
          "confirm": "Are you sure?"
        }'>
  Submit with timeout
</button>
```

| Option | Description |
|--------|-------------|
| `timeout` | Request timeout in milliseconds |
| `credentials` | `"include"`, `"same-origin"`, `"omit"` |
| `headers` | Object of additional headers |
| `confirm` | Confirmation message (browser confirm dialog) |
| `validate` | `true`/`false` — force validation on/off |
| `noHeaders` | Array of header names to exclude from default htmx headers |
