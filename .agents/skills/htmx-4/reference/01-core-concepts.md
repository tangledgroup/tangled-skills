# htmx-4 Core Concepts

## Request Lifecycle

When an htmx-triggered request occurs, the following phases execute in order:

1. **Init**: Element is processed and event listeners attached
2. **Before Request**: `htmx:before:request` fires (cancellable)
3. **Config Request**: `htmx:config:request` fires for request configuration
4. **Before Send**: Request is prepared with headers and values
5. **Before Response**: `htmx:before:response` fires (cancellable)
6. **Swap**: Response content swapped into DOM
7. **After Swap**: `htmx:after:swap` fires
8. **Settle**: Attributes restored, `htmx:after:settle` fires

### Cancelling Requests

Requests can be cancelled by preventing default on any before events:

```javascript
document.body.addEventListener('htmx:before:request', function(evt) {
  if (!isValidState()) {
    evt.preventDefault();  // Cancel the request
  }
});
```

## Attribute Inheritance

In htmx 4.0, attribute inheritance is **explicit** by default (changed from implicit in htmx 2.x).

### Using `:inherited` Modifier

Add `:inherited` to any attribute that should inherit down the DOM tree:

```html
<!-- Parent sets confirm dialog for all children -->
<div hx-confirm:inherited="Are you sure?">
  <button hx-delete="/item/1">Delete Item 1</button>
  <button hx-delete="/item/2">Delete Item 2</button>
</div>
```

Without `:inherited`, the confirm dialog would only apply to the div itself.

### Using `:append` Modifier

Use `:append` to add to inherited values instead of replacing them:

```html
<div hx-include:inherited="#global-fields">
  <form hx-include:inherited:append=".extra">
    <!-- Form includes both #global-fields and .extra -->
  </form>
</div>
```

### Reverting to Implicit Inheritance

To restore htmx 2.x behavior:

```javascript
htmx.config.implicitInheritance = true;
```

Or use the `htmx-2-compat` extension.

## Target Selection

htmx determines which element to update based on these rules (in order):

1. **Explicit `hx-target`**: Uses specified selector
2. **Inherited `hx-target:inherited`**: Inherits from ancestor
3. **Element itself**: Default for most elements
4. **Closest form**: For inputs, buttons, and labels
5. **Document body**: Fallback

### Target Selectors

```html
<!-- Target specific element -->
<button hx-post="/save" hx-target="#result">Save</button>

<!-- Target ancestor -->
<input hx-post="/search" hx-target="closest .search-box">

<!-- Target descendant -->
<div hx-get="/data" hx-target "> .data-container">Load</div>

<!-- Inherited target for all children -->
<div hx-target:inherited="#main-content">
  <a hx-get="/page1">Page 1</a>
  <a hx-get="/page2">Page 2</a>
</div>
```

## Swap Styles

The `hx-swap` attribute controls how response content replaces the target.

### DOM Swap Styles

| Style | Description |
|-------|-------------|
| `innerHTML` | Replace element's children (default) |
| `outerHTML` | Replace entire element |
| `beforebegin` | Insert before element |
| `afterbegin` | Insert at start of element |
| `afterend` | Insert after element |
| `beforeend` | Insert at end of element |

### Morph Swap Styles

Requires [idiomorph](https://github.com/wildlyinaccurate/idiomorph) library:

| Style | Description |
|-------|-------------|
| `innerMorph` | Morph element's children, preserving state |
| `outerMorph` | Morph entire element, preserving state |

### Other Swap Styles

| Style | Description |
|-------|-------------|
| `textContent` | Set text content (no HTML parsing) |
| `delete` | Remove target element entirely |

### Swap Aliases

htmx 4 provides convenient aliases:

| Alias | Equivalent |
|-------|------------|
| `before` | `beforebegin` |
| `after` | `afterend` |
| `prepend` | `afterbegin` |
| `append` | `beforeend` |

### Swap Options

Swap styles can include options in the format `style:option1:value1 option2:value2`:

```html
<!-- Scroll to top after swap -->
<div hx-get="/data" hx-swap="innerHTML show:top">Load</div>

<!-- Ignore title tag in response -->
<div hx-get="/page" hx-swap="innerHTML ignoreTitle:true">Load</div>

<!-- Add 300ms delay before swapping -->
<div hx-get="/data" hx-swap="innerHTML delay:300ms">Load</div>
```

## Out-of-Band (OOB) Swaps

OOB swaps allow updating elements outside the normal target using `hx-swap-oob` attribute in the response HTML.

### Basic OOB Swap

Server returns HTML with `hx-swap-oob` attributes:

```html
<!-- Server response -->
<div hx-swap-oob="innerHTML:#notifications">
  <div class="alert">Item saved!</div>
</div>

<div hx-swap-oob="outerHTML:#sidebar">
  <nav>New sidebar content</nav>
</div>

<!-- Main content (swaps into normal target) -->
<div>Main response content</div>
```

### OOB Swap Behaviors

| Behavior | Description |
|----------|-------------|
| `innerHTML:#id` | Replace children of #id |
| `outerHTML:#id` | Replace entire #id element |
| `true` | Auto-detect target from element's id attribute |
| `delete` | Remove the element |
| `prepend:#id` | Prepend to #id |
| `append:#id` | Append to #id |

### OOB Swap Order (htmx 4)

In htmx 4, swap order changed from htmx 2:

1. **Main content swaps first**
2. **OOB elements swap after** (in document order)
3. **`<hx-partial>` elements swap last** (in document order)

This matters if swaps depend on each other - restructure to make swaps independent.

## Multi-Target Updates with `<hx-partial>`

The `<hx-partial>` element provides explicit control over multi-target updates as an alternative to OOB swaps:

```html
<!-- Server response with partials -->
<hx-partial hx-target="#messages" hx-swap="beforeend">
  <div class="message">New message</div>
</hx-partial>

<hx-partial hx-target="#count">
  <span>5</span>
</hx-partial>

<!-- Main content -->
<div>Response body</div>
```

Each `<hx-partial>` specifies its own target and swap strategy, evaluated in document order after the main swap.

## Selecting Response Content

Use `hx-select` to extract specific content from the server response:

```html
<!-- Only swap the .result div from response -->
<div hx-get="/search" hx-select=".result" hx-target="#search-results">
  Search...
</div>
```

Server can return full HTML, and htmx extracts only `.result` before swapping.

## Extended Selectors

htmx supports extended selector syntax beyond standard CSS:

| Selector | Description |
|----------|-------------|
| `closest selector` | Closest ancestor matching selector |
| `find selector` | First descendant matching selector |
| `next selector` | Next sibling matching selector |
| `previous selector` | Previous sibling matching selector |
| `document` | Document root |
| `window` | Window object |

```html
<!-- Target closest form ancestor -->
<button hx-post="/save" hx-target="closest form">Save</button>

<!-- Find first .error within result -->
<div hx-get="/validate" hx-select="find .error">Validate</div>
```

## Security Considerations

### `hx-eval` and Content Security Policy

htmx uses `eval()` for:
- Event filters in `hx-trigger` (e.g., `click[ctrlKey]`)
- JavaScript values in `hx-vals` (e.g., `js:getValue()`)

This can conflict with strict Content Security Policy (CSP). Use nonces:

```javascript
htmx.config.inlineScriptNonce = "your-nonce-value";
htmx.config.inlineStyleNonce = "your-nonce-value";
```

Or set via meta tag:

```html
<meta name="htmx-config" content='{"inlineScriptNonce": "your-nonce-value"}'>
```

### XSS Prevention

- Never insert untrusted user input directly into htmx attributes
- Use server-side escaping for all dynamic content
- Validate and sanitize `hx-vals` JavaScript expressions
- Consider CSP implications of `eval()` usage

## Performance Optimization

### Debouncing and Throttling

Use trigger modifiers to limit request frequency:

```html
<!-- Debounce: wait 1s after last input -->
<input hx-get="/search" hx-trigger="input changed delay:1s">

<!-- Throttle: max 1 request per 500ms -->
<div hx-get="/position" hx-trigger="scroll throttle:500ms">
```

### Preloading

Use the preload extension to fetch content on mouseover:

```html
<a hx-get="/expensive-page" hx-ext="preload" hx-trigger="mouseover from:body">
  Load Expensive Page
</a>
```

### Lazy Loading

Load content when it enters viewport:

```html
<div hx-get="/heavy-content" hx-trigger="revealed">
  Loading...
</div>
```

Or use intersection observer with threshold:

```html
<div hx-get="/image" hx-trigger="intersect threshold:0.5 once">
```

## Debugging

### Enable Logging

```javascript
htmx.config.logAll = true;  // Log all htmx events
```

### Inspect Elements

htmx adds CSS classes during request lifecycle:

- `htmx-request`: Element has active request
- `htmx-added`: Newly added element (before swap)
- `htmx-swapping`: Element being swapped
- `htmx-settling`: Element settling after swap

```css
.htmx-request { opacity: 0.5; }
.htmx-added { animation: fade-in 0.3s; }
```

### Browser DevTools

- Check Network tab for AJAX requests
- Look for HX-* headers in request/response
- Inspect console for htmx logs and errors
- Use `htmx:before:request` breakpoint for debugging
