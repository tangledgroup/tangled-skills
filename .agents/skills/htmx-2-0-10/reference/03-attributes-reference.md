# Attributes Reference

Complete catalog of all htmx 2.0.10 attributes with descriptions and usage examples.

## Core Request Attributes

### `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete`

Issue an AJAX request using the specified HTTP method. The attribute value is the URL.

```html
<button hx-get="/items/42">Load</button>
<form hx-post="/items"><input name="name" /><button>Save</button></form>
<button hx-delete="/items/1">Delete</button>
```

## Core Response Attributes

### `hx-target`

Specifies the DOM element to swap the response into. Accepts CSS selectors and extended selectors (`this`, `closest X`, `find X`, `next X`, `previous X`, `body`).

```html
<button hx-get="/data" hx-target="#result">Load</button>
<button hx-delete="/row/1" hx-target="closest tr">Delete Row</button>
```

### `hx-swap`

Controls how the response is inserted. Default: `innerHTML`.

```html
<div hx-get="/items" hx-swap="beforeend"></div>
<div hx-get="/data" hx-swap="outerHTML transition:true swap:200ms"></div>
<button hx-delete="/item/1" hx-swap="delete">Remove</button>
```

Options: `transition:true`, `swap:<ms>`, `settle:<ms>`, `ignoreTitle:true`, `scroll:<target>`, `show:<element>`.

### `hx-select`

Select a subset of the response using a CSS selector before swapping.

```html
<div hx-get="/page" hx-select="#main-content"></div>
```

### `hx-swap-oob`

Out-of-band swap — update elements outside the normal target. Include in server response.

```html
<!-- In server response: -->
<div id="clock" hx-swap-oob="true">3:00 PM</div>
<ul id="list" hx-swap-oob="beforeend"><li>New</li></ul>
```

### `hx-select-oob`

Select specific elements from the response for out-of-band swapping.

```html
<div hx-get="/dashboard" hx-select-oob="#clock #user-info"></div>
```

## Event Attributes

### `hx-trigger`

Controls when the request fires. Default is natural event.

```html
<input hx-get="/search" hx-trigger="keyup changed delay:300ms" />
<div hx-get="/poll" hx-trigger="every 5s"></div>
<div hx-get="/visible" hx-trigger="intersect once"></div>
<button hx-post="/action" hx-trigger="click from:body not:.disabled"></button>
```

Modifiers: `throttle`, `rate`, `changed`, `once`, `from`, `target`, `not`, `consumed`, `queue`, `delay`.

### `hx-on*`

Attach inline event handlers. Use `hx-on::<event>` syntax.

```html
<button hx-post="/save"
        hx-on::before-request="this.textContent='Saving...'"
        hx-on::after-request="this.textContent='Saved!'">
  Save
</button>
```

## Parameter Attributes

### `hx-include`

Include additional form fields from other elements in the request.

```html
<form id="filters"><input name="category" value="books" /></form>
<button hx-get="/search" hx-include="#filters">Search</button>
```

### `hx-params`

Control which form parameters are included.

```html
<form hx-post="/save" hx-params="not password">
  <input name="name" />
  <input name="password" type="password" />
</form>
```

Values: `*` (all), `none`, `not field1,field2`, `only field1,field2`.

### `hx-vals`

Add static extra values as JSON.

```html
<button hx-post="/api" hx-vals='{"format":"json","v":2}'>Submit</button>
```

### `hx-vars`

Add dynamic values from JavaScript expressions (requires `allowEval`).

```html
<button hx-post="/api" hx-vars='{"ts": Date.now()}'>Submit</button>
```

## Behavior Attributes

### `hx-push-url`

Push a URL into the browser address bar after the request. Enables back-button support.

```html
<button hx-get="/items/42" hx-push-url="true">Load Item</button>
<button hx-get="/items/42" hx-push-url="/items/42">Load with custom URL</button>
```

### `hx-replace-url`

Same as `hx-push-url` but replaces history entry instead of pushing.

```html
<div hx-get="/page" hx-trigger="every 10s" hx-replace-url="true"></div>
```

### `hx-confirm`

Show a browser confirmation dialog before the request.

```html
<button hx-delete="/items/1" hx-confirm="Are you sure?">Delete</button>
```

### `hx-disable`

Disable the element while the request is in flight.

```html
<button hx-post="/save" hx-disable>Submit</button>
```

### `hx-disabled-elt`

Disable other elements during the request. Uses extended selector syntax.

```html
<form hx-post="/save" hx-disabled-elt="find button">
  <button type="submit">Save</button>
</form>
```

### `hx-indicator`

Element to show as loading indicator (gets `htmx-request` class).

```html
<button hx-post="/save" hx-indicator=".spinner">
  Save <span class="spinner htmx-indicator">⏳</span>
</button>
```

### `hx-validate`

Force form validation before request.

```html
<form hx-post="/save" hx-validate="true">
  <input name="email" type="email" required />
</form>
```

### `hx-inherit`

Control which attributes are inherited from ancestor elements.

```html
<div hx-target="#result">
  <button hx-get="/data" hx-inherit="hx-swap:hx-target">
    Inherits target but not swap
  </button>
</div>
```

### `hx-disinherit`

Prevent specific attributes from being inherited.

```html
<div hx-target="#global-result">
  <button hx-get="/data" hx-disinherit="hx-target" hx-target="#local">
    Does not inherit parent's target
  </button>
</div>
```

## Extension Attributes

### `hx-ext`

Enable one or more extensions on an element.

```html
<body hx-ext="sse,ws,preload">
<div hx-ext="response-targets" hx-post="/api"></div>
```

### `hx-headers`

Add custom headers to requests.

```html
<button hx-post="/api" hx-headers='{"X-CSRF":"abc","Accept":"application/json"}'>Submit</button>
```

### `hx-encoding`

Set the request encoding. Default is `application/x-www-form-urlencoded`.

```html
<form hx-post="/upload" hx-encoding="multipart/form-data">
  <input type="file" name="file" />
</form>
```

### `hx-sync`

Control concurrent request handling.

```html
<input hx-get="/search" hx-trigger="keyup changed delay:200ms" hx-sync="this:abort" />
```

Strategies: `drop`, `queue`, `abort`, `replace`, `none`.

### `hx-request`

Fine-grained request configuration as JSON.

```html
<button hx-post="/api"
        hx-request='{"timeout":5000,"credentials":"include"}'>
  Submit
</button>
```

Options: `timeout`, `credentials`, `headers`, `confirm`, `validate`, `noHeaders`.

### `hx-preserve`

Preserve elements during swap using CSS selectors on the response.

```html
<form hx-post="/save" hx-preserve="input[type=file]">
  <input type="file" name="attachment" />
</form>
```

### `hx-history`

Control whether element is included in history snapshots.

```html
<div hx-history="false">Not saved in history</div>
```

### `hx-history-elt`

Use a specific element (instead of `<body>`) for history snapshots.

```html
<div hx-boost="true" hx-history-elt="#app">
  <div id="app">...</div>
</div>
```

## Boosting

### `hx-boost`

Progressively enhance links and forms to use AJAX. Falls back to normal navigation if JS is disabled.

```html
<body hx-boost="true">
  <a href="/items/42">Load via AJAX</a>
  <form action="/search" method="get">
    <input name="q" />
  </form>
</body>

<!-- Boost only specific elements -->
<a href="/page" hx-boost="true">AJAX Link</a>
<div hx-boost="false">
  <a href="/page">Normal navigation</a>
</div>
```

## Extension-Specific Attributes

### SSE Extension
| Attribute | Description |
|-----------|-------------|
| `sse-connect="<url>"` | Connect to SSE endpoint |
| `sse-swap="<event-name>"` | Listen for named SSE events |
| `sse-close="<event-name>"` | Close connection on event |

### WebSocket Extension
| Attribute | Description |
|-----------|-------------|
| `ws-connect="<url>"` | Connect to WebSocket endpoint |
| `ws-send` | Send form data as JSON to nearest WebSocket |

### Preload Extension
| Attribute | Description |
|-----------|-------------|
| `preload` | Preload the element's request on trigger event |

### Response Targets Extension
| Attribute | Description |
|-----------|-------------|
| `hx-target-[CODE]` | Target for specific HTTP status code |
| `hx-target-error` | Target for 4xx/5xx errors |

### Loading States Extension
| Attribute | Description |
|-----------|-------------|
| `data-loading` | Show element during request |
| `data-loading-class` | Add classes during request |
| `data-loading-class-remove` | Remove classes during request |
| `data-loading-disable` | Disable element during request |
| `data-loading-aria-busy` | Add aria-busy during request |
| `data-loading-delay="<ms>"` | Delay before showing loading state |
| `data-loading-target="<selector>"` | Target for loading state |
| `data-loading-path="<path>"` | Filter by request path |
| `data-loading-states` | Scope boundary for loading states |

### Class Tools Extension
| Attribute | Description |
|-----------|-------------|
| `classes` | Add/remove/toggle CSS classes with timing |
| `apply-parent-classes` | Apply classes to parent (for OOB updates) |
