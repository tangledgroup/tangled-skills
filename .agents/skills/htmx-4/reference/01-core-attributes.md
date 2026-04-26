# Core Attributes Reference

## Request Attributes

### `hx-get`

Issue a GET request to the specified URL.

```html
<button hx-get="/example">Get Some HTML</button>
```

Swaps returned HTML into the `innerHTML` of the button by default. Empty `hx-get=""` makes a GET to the current URL and swaps the current page.

### `hx-post`

Issue a POST request to the specified URL.

```html
<button hx-post="/account/enable" hx-target="body">
  Enable Your Account
</button>
```

### `hx-put`, `hx-delete`, `hx-patch`

Same pattern as above but with different HTTP methods:

```html
<button hx-delete="/account/123">Delete</button>
<button hx-put="/account/123">Update</button>
<button hx-patch="/account/123">Patch</button>
```

### `hx-push-url`

Push a URL into the browser history after a request completes. Creates a new history entry for back/forward navigation.

```html
<div hx-get="/blog" hx-push-url="true">Blog</div>
```

Values:
- `true` — pushes the fetched URL
- `false` — disables pushing (overrides inheritance or `hx-boost`)
- A custom URL string — pushes that specific URL instead

In htmx 4.0, history restoration issues a full page request rather than using sessionStorage snapshots, making it more reliable and secure.

### `hx-boost`

Boost normal `<a>` and `<form>` elements to use AJAX instead of full page navigation. Falls back to normal behavior if JavaScript is disabled (progressive enhancement).

```html
<div hx-boost="true">
  <a href="/page1">Go To Page 1</a>
  <a href="/page2">Go To Page 2</a>
</div>
```

For anchors: issues GET, pushes URL, targets `<body>` with `innerHTML` swap.
For forms: uses the form's method (GET/POST), triggers on submit, targets `<body>`.

Configure boost behavior with a config string:

```html
<body hx-boost:inherited='swap:"innerHTML", target:"#main", select:"#content"'>
```

## Target and Swap Attributes

### `hx-target`

Specifies where to insert the response content. Defaults to `this` (the element making the request).

```html
<button hx-post="/register" hx-target="#response-div">Register</button>
<div id="response-div"></div>
```

Supports extended selectors:
- CSS selectors: `#results`, `.container`, `[data-target]`
- `closest <selector>` — nearest ancestor matching selector
- `find <selector>` — first child descendant matching selector
- `findAll <selector>` — all child descendants matching selector
- `next` / `next <selector>` — next sibling (optionally filtered)
- `previous` / `previous <selector>` — previous sibling (optionally filtered)

### `hx-swap`

Controls how the response content is inserted. Defaults to `innerHTML`.

**Swap methods:**

- `innerHTML` — replaces content inside element
- `outerHTML` — replaces entire element
- `textContent` — replaces text without parsing as HTML (safe for plain text responses)
- `beforebegin` / `before` — inserts before element
- `afterbegin` / `prepend` — inserts as first child
- `beforeend` / `append` — inserts as last child
- `afterend` / `after` — inserts after element
- `innerMorph` — morphs content using idiomorph algorithm, preserving state and focus
- `outerMorph` — morphs entire element using idiomorph
- `delete` — removes element (ignores response)
- `none` — doesn't insert content (out-of-band swaps still work)
- `upsert` — updates existing elements by ID, inserts new ones (requires upsert extension)

**Modifiers:**

```html
<div hx-swap="innerHTML transition:true"></div>        <!-- View Transitions API -->
<div hx-swap="innerHTML swap:1s"></div>                <!-- Delay before swap -->
<div hx-swap="innerHTML settle:200ms"></div>           <!-- Delay between swap and settle -->
<div hx-swap="innerHTML ignoreTitle:true"></div>       <!-- Don't update page title -->
<div hx-swap="beforeend scroll:bottom"></div>          <!-- Auto-scroll after swap -->
```

### `hx-select`

Select a subset of the response to swap using a CSS query selector.

```html
<button hx-get="/page" hx-select="#content">Load Content</button>
```

### `hx-select-oob`

Select content for out-of-band swap (separate from main content swap). Comma-separated list of selectors, optionally with swap strategy.

```html
<button hx-get="/update" hx-select-oob="#alert,#sidebar:afterbegin">
  Update Multiple
</button>
```

### `hx-swap-oob`

Place this on elements in the **response** to swap them "out of band" — into locations other than the main target.

```html
<!-- In server response: -->
<div><!-- main content --></div>
<div id="alerts" hx-swap-oob="true">Saved!</div>
```

The first div goes to the normal target. The second div replaces the element with `id="alerts"` wherever it exists in the page.

Values: `true` (equivalent to `outerHTML`), any valid `hx-swap` value, or swap value with CSS selector.

## Trigger Attribute

### `hx-trigger`

Specifies what triggers an AJAX request. Can be standard events, synthetic events, polling expressions, or multiple comma-separated triggers.

```html
<div hx-get="..." hx-trigger="click">Click Me</div>
<input hx-get="..." hx-trigger="input changed delay:1s">
<div hx-get="..." hx-trigger="revealed">Loading...</div>
<div hx-get="..." hx-trigger="every 2s">Waiting...</div>
```

**Defaults when omitted:**
- `<input>`, `<textarea>`, `<select>` → `change`
- `<form>` → `submit`
- Everything else → `click`

**Event filters** — JavaScript expression in brackets:

```html
<div hx-get="..." hx-trigger="click[ctrlKey]">...</div>
<input hx-get="..." hx-trigger="keyup[key=='Enter']">
<div hx-get="..." hx-trigger="click[ctrlKey&&shiftKey]">...</div>
```

**Event modifiers:**

- `once` — triggers only the first time
- `changed` — triggers only if value has changed since last fire
- `delay:<time>` — waits before triggering (resets on each event)
- `throttle:<time>` — triggers then ignores further events for interval
- `from:<selector>` — listens on a different element
- `target:<selector>` — filters to events originating from selector
- `consume` — prevents the event from bubbling
- `queue:<strategy>` — queues events (`drop`, `merge`, or delay in ms)

**Synthetic events:**

- `load` — fires when htmx first processes the element
- `revealed` — fires when element scrolls into view
- `intersect` — fires based on IntersectionObserver with options
- `every <interval>` — polling (e.g., `every 2s`)

## Parameter Attributes

### `hx-include`

Include additional element values in the request using CSS selectors.

```html
<button hx-post="/register" hx-include="[name='email']">Register</button>
```

Supports extended selectors (`closest`, `find`, `next`, `previous`) and `this`. Use `inherit` keyword to merge with parent includes.

### `hx-vals`

Add arbitrary values to request parameters as JSON or JavaScript expression.

```html
<div hx-get="/search" hx-vals='{"category": "books"}'>Search</div>
<div hx-get="/search" hx-vals='js:{query: document.querySelector("#q").value}'>Search</div>
```

Use `:append` modifier to merge with parent values instead of replacing. Values override form data with matching keys. Can return a Promise for async resolution.

### `hx-headers`

Add custom headers to the request as JSON.

```html
<div hx-get="/data" hx-headers='{"myHeader": "My Value"}'>Get Data</div>
```

Use `js:` prefix to evaluate JavaScript. Useful for CSRF tokens:

```html
<html hx-headers='{"X-CSRF-TOKEN": "token_here"}'>
```

### `hx-encoding`

Switch request encoding to `multipart/form-data` for file uploads.

```html
<form hx-post="/upload" hx-encoding="multipart/form-data">
  <input type="file" name="file">
  <button type="submit">Upload</button>
</form>
```

## Behavior Attributes

### `hx-confirm`

Show a confirmation dialog before issuing the request.

```html
<button hx-delete="/account" hx-confirm="Are you sure?">Delete Account</button>
```

Uses `window.confirm()` by default. Can be customized via the `htmx:confirm` event.

### `hx-disable`

Disable elements during request flight.

```html
<button hx-post="/submit" hx-disable="this">Submit</button>
<form hx-post="/example" hx-disable="find input[type='text'], find button">
```

Supports extended selectors and comma-separated lists.

### `hx-indicator`

Specify elements that get the `htmx-request` class during request flight (for spinners).

```html
<button hx-post="/example" hx-indicator="#spinner">Post It!</button>
<img id="spinner" class="htmx-indicator" src="/img/bars.svg" alt="Loading...">
```

Default CSS for `.htmx-indicator` fades in opacity with transition.

### `hx-preserve`

Keep an element unchanged during HTML replacement by ID.

```html
<div id="video-player" hx-preserve>...</div>
```

Must have a stable `id`. Preserved through history navigation too. Note: some elements (inputs, iframes) may lose state — consider the morphdom extension for complex cases.

### `hx-ignore`

Prevent htmx from processing any attributes on an element and its descendants. Used for security when injecting raw HTML.

```html
<div hx-ignore>
    <%= raw(user_content) %>
</div>
```

Cannot be bypassed by injected content.

## Event Handling Attributes

### `hx-on:*`

Embed inline scripts to respond to events directly on elements. The event name is part of the attribute name after a colon.

```html
<div hx-on:click="alert('Clicked!')">Click</div>
```

For htmx events, use double-colon shorthand (omits "htmx" prefix):

```html
<button hx-get="/info" hx-on::before-request="alert('Making a request!')">
  Get Info!
</button>
```

Use dashes instead of colons for JSX compatibility:

```html
<button hx-get="/info" hx-on--before-request="alert('Making a request!')">
  Get Info!
</button>
```

Deprecated form: `hx-on="eventName: script"` (cannot be mixed with `hx-on:*` on same element).

## Attribute Inheritance

In htmx 4.0, inheritance is **explicit** by default. Use the `:inherited` modifier to hoist attributes to parent elements.

```html
<div hx-confirm:inherited="Are you sure?" hx-target:inherited="#main">
  <button hx-delete="/account">Delete</button>
  <button hx-put="/account">Update</button>
</div>
```

To restore htmx 2.x implicit inheritance behavior:

```html
<script>htmx.config.implicitInheritance = true;</script>
```

## Synchronization

htmx 4.0 provides request synchronization to coordinate multiple concurrent requests. Prevents race conditions when multiple elements update the same target.

Configure via `hx-sync` attribute or globally through configuration.
