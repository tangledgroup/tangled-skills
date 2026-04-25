# Response Handling Reference

## Swap Styles

The `hx-swap` attribute controls how response content replaces the target element.

### DOM Manipulation Styles

| Style | Description | Example |
|-------|-------------|---------|
| `innerHTML` | Replace element's children (default) | `<div>Before</div>` → `<div>New content</div>` |
| `outerHTML` | Replace entire element | Element completely replaced |
| `beforebegin` | Insert before element | `<new></new><div>Original</div>` |
| `afterbegin` | Insert at start | `<div><new></new>Original</div>` |
| `afterend` | Insert after element | `<div>Original</div><new></new>` |
| `beforeend` | Insert at end | `<div>Original<new></new></div>` |

### Morph Styles (requires idiomorph)

Morph styles preserve element state and event listeners:

```html
<!-- Inner morph: preserve children state -->
<div hx-get="/data" hx-swap="innerMorph">Content</div>

<!-- Outer morph: preserve element state -->
<div hx-get="/data" hx-swap="outerMorph">Content</div>
```

### Special Styles

| Style | Description |
|-------|-------------|
| `textContent` | Set text content only (no HTML parsing) |
| `delete` | Remove target element entirely |
| `none` | Don't swap content (use for side effects) |

```html
<!-- Update text only -->
<span hx-get="/count" hx-swap="textContent">5</span>

<!-- Delete element on success -->
<button hx-post="/remove" hx-swap="delete">Remove</button>

<!-- Side effect only -->
<button hx-post="/log" hx-swap="none">Log Action</button>
```

### Swap Style Aliases

htmx 4 provides convenient aliases:

| Alias | Equivalent |
|-------|------------|
| `before` | `beforebegin` |
| `after` | `afterend` |
| `prepend` | `afterbegin` |
| `append` | `beforeend` |

```html
<!-- Using aliases -->
<div hx-get="/data" hx-swap="prepend">Prepend</div>
<div hx-get="/data" hx-swap="append">Append</div>
```

## Swap Options

Swap styles can include options using `option:value` syntax:

### Scroll Behavior

```html
<!-- Scroll to top of page -->
<div hx-get="/page" hx-swap="innerHTML show:top">Load Page</div>

<!-- Scroll to bottom of target -->
<div hx-get="/messages" hx-swap="innerHTML show:bottom scrollTarget:#chat">
  Messages
</div>

<!-- Scroll specific element into view -->
<div hx-get="/data" hx-swap="innerHTML show:#result:nearest">Load</div>
```

Options: `top`, `bottom`, `nearest`, or CSS selector with position

### Delay

Add delay before swapping:

```html
<!-- 300ms delay -->
<div hx-get="/data" hx-swap="innerHTML delay:300ms">Loading...</div>

<!-- 1 second delay -->
<div hx-get="/data" hx-swap="innerHTML delay:1s">Loading...</div>
```

### Ignore Title

Prevent title tag in response from updating page title:

```html
<div hx-get="/page" hx-swap="innerHTML ignoreTitle:true">Load</div>
```

### Combined Options

```html
<!-- Multiple options -->
<div hx-get="/data" 
     hx-swap="innerHTML show:bottom delay:100ms ignoreTitle:true">
  Load Data
</div>
```

## Out-of-Band (OOB) Swaps

OOB swaps update elements outside the normal target by including `hx-swap-oob` attributes in response HTML.

### Basic OOB Syntax

```html
<!-- Server response -->
<div hx-swap-oob="innerHTML:#notifications">
  <div class="alert">Success!</div>
</div>

<div hx-swap-oob="outerHTML:#sidebar">
  <nav>Updated sidebar</nav>
</div>

<!-- Main content swaps into normal target -->
<div class="content">Main response</div>
```

### OOB Swap Behaviors

| Behavior | Description | Example |
|----------|-------------|---------|
| `innerHTML:#id` | Replace children of element | `<div hx-swap-oob="innerHTML:#box">` |
| `outerHTML:#id` | Replace entire element | `<div hx-swap-oob="outerHTML:#box">` |
| `true` | Auto-detect from id attribute | `<div id="box" hx-swap-oob="true">` |
| `delete` | Remove element | `<div id="loading" hx-swap-oob="delete">` |
| `prepend:#id` | Prepend to element | `<div hx-swap-oob="prepend:#list">` |
| `append:#id` | Append to element | `<div hx-swap-oob="append:#list">` |

### Auto-Detect with `true`

Element's own `id` attribute determines target:

```html
<!-- Server response -->
<div id="notification" hx-swap-oob="true">
  <div class="alert">Saved!</div>
</div>

<!-- Swaps into #notification on page -->
```

### Deleting Elements

Remove loading indicators or temporary elements:

```html
<!-- Response includes element to delete -->
<div id="loading-spinner" hx-swap-oob="delete">
  Loading...
</div>

<div class="result">Actual content</div>
```

Page must have `<div id="loading-spinner">` for this to work.

### OOB Swap Order (htmx 4)

Critical change from htmx 2:

1. **Main content swaps first** into target
2. **OOB elements swap after** (in document order from response)
3. **`<hx-partial>` elements swap last** (in document order)

```html
<!-- Server response -->
<!-- 1. Main content swaps first -->
<div class="main">Main response content</div>

<!-- 2. OOB swaps after (in this order) -->
<div hx-swap-oob="innerHTML:#notifications">Notification</div>
<div hx-swap-oob="outerHTML:#sidebar">Sidebar</div>

<!-- 3. Partials swap last -->
<hx-partial hx-target="#count">5</hx-partial>
```

**Migration impact:** If OOB swaps created DOM that main swap depended on, restructure to make swaps independent.

## Multi-Target with `<hx-partial>`

The `<hx-partial>` element provides explicit multi-target updates:

```html
<!-- Server response -->
<hx-partial hx-target="#messages" hx-swap="beforeend">
  <div class="message">New message</div>
</hx-partial>

<hx-partial hx-target="#count" hx-swap="innerHTML">
  <span>5</span>
</hx-partial>

<hx-partial hx-target="#timestamp" hx-swap="textContent">
  Just now
</hx-partial>

<!-- Main content -->
<div>Response body</div>
```

Each partial specifies:
- `hx-target`: Which element to update
- `hx-swap`: How to update it (optional, defaults to innerHTML)

Partials swap in document order after main content and OOB swaps.

## Status Code Handling

htmx 4 swaps all HTTP responses by default, including 4xx and 5xx errors (changed from htmx 2).

### `hx-status` Attribute

Specify different behavior per status code:

```html
<!-- Handle validation errors -->
<form hx-post="/save" 
      hx-status:422="swap:innerHTML target:#errors select:#validation-errors"
      hx-status:5xx="swap:none push:false">
  <input name="email">
  <button type="submit">Save</button>
</form>
```

### Status Code Syntax

| Pattern | Matches |
|---------|---------|
| `200` | Exact code 200 |
| `4xx` | Any 4xx error (400-499) |
| `50x` | Any 50x error (500-509) |
| `5xx` | Any 5xx error (500-599) |

### Status Config Options

Each status code can specify:
- `swap`: Swap style (e.g., `innerHTML`, `none`)
- `target`: Target selector
- `select`: CSS selector to extract from response
- `push`: Whether to push URL to history (`true`/`false`)
- `replace`: Whether to replace history entry (`true`/`false`)
- `transition`: Whether to use view transition

```html
<!-- Comprehensive error handling -->
<form hx-post="/submit"
      hx-status:400="swap:innerHTML target:#errors"
      hx-status:401="swap:none redirect:/login"
      hx-status:422="swap:innerHTML target:#form-errors select:.error-messages"
      hx-status:5xx="swap:none alert:Server error. Please try again.">
  <button type="submit">Submit</button>
</form>
```

### Preventing Error Swaps Globally

Restore htmx 2 behavior (don't swap 4xx/5xx):

```javascript
htmx.config.noSwap = [204, 304, '4xx', '5xx'];
```

Or for specific codes:

```javascript
htmx.config.noSwap = [422, 500, 503];
```

## Response Content Selection

### `hx-select`

Extract specific content from response before swapping:

```html
<!-- Only swap .result div from full HTML response -->
<div hx-get="/search" 
     hx-select=".result" 
     hx-target="#search-results">
  Search...
</div>
```

Server can return full page HTML, htmx extracts only `.result`.

### `hx-select-oob`

Mark elements in response for OOB swap:

```html
<!-- Server response -->
<div hx-select-oob="#notifications">
  <div class="alert">Saved!</div>
</div>

<div class="main-content">Response body</div>
```

Client specifies where OOB content goes:

```html
<button hx-post="/save" 
        hx-select-oob="#notifications">#notification-container</button>
```

## View Transitions

htmx 4 supports the [View Transitions API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API) for smooth animations between swaps.

### Enable View Transitions

```javascript
htmx.config.transitions = true;
```

Or per-element:

```html
<div hx-get="/page" 
     hx-swap="innerHTML transition:true">
  Load with Transition
</div>
```

### Transition Options

```html
<!-- Skip transition for specific swap -->
<div hx-get="/data" hx-swap="innerHTML transition:false">No Transition</div>

<!-- Force transition -->
<div hx-get="/data" hx-swap="innerHTML transition:true">Force Transition</div>
```

### Custom Transitions with CSS

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 0.3s;
  animation-timing-function: ease-in-out;
}

::view-transition-old(root) {
  animation-name: fade-out;
}

::view-transition-new(root) {
  animation-name: fade-in;
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### Cancelling Transitions

```javascript
document.addEventListener('htmx:before:viewTransition', function(evt) {
  if (!shouldAnimate()) {
    evt.preventDefault();
  }
});
```

## Indicators and Loading States

### `hx-indicator`

Specify loading indicator element:

```html
<!-- Show spinner during request -->
<div hx-get="/data" hx-indicator="#spinner">
  <div id="spinner" class="hidden">Loading...</div>
  <button>Load Data</button>
</div>
```

htmx adds `hx-visible` class to indicator during request.

### CSS Classes During Request

htmx automatically manages these CSS classes:

| Class | When Applied | To Which Element |
|-------|--------------|------------------|
| `htmx-request` | During request | Triggering element |
| `htmx-added` | Before swap | Newly added elements |
| `htmx-swapping` | During swap | Target element |
| `htmx-settling` | During settle | Target element |

```css
/* Visual feedback during requests */
.htmx-request {
  opacity: 0.5;
  pointer-events: none;
}

/* Animation for new content */
.htmx-added {
  animation: fade-in 0.3s ease-in;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Custom Indicator Styles

```javascript
// Customize indicator class names
htmx.config.indicatorClass = 'loading';
htmx.config.requestClass = 'making-request';
htmx.config.addedClass = 'new-content';
htmx.config.settlingClass = 'settling';
htmx.config.swappingClass = 'swapping';
```

## History Management

### `hx-push-url`

Push URL to browser history:

```html
<!-- Push custom URL to history -->
<div hx-get="/api/data" hx-push-url="true">Load Data</div>

<!-- Push specific URL -->
<button hx-post="/search" hx-push-url="/results?q=htmx">Search</button>

<!-- Boolean from JavaScript -->
<a hx-get="/page" hx-push-url='js:shouldPushUrl()'>Link</a>
```

### `hx-replace-url`

Replace current history entry instead of pushing:

```html
<button hx-post="/update" hx-replace-url="/status/updated">Update</button>
```

### History Configuration

```javascript
// Disable history entirely
htmx.config.history = false;

// Use full page reload on history navigation
htmx.config.history = "reload";

// Default behavior (fetch and swap into body)
htmx.config.history = true;
```

**Note:** htmx 4 no longer caches pages in localStorage. Pages are re-fetched on back navigation.

## Server Sent Headers

Server can control client behavior via response headers:

### HX-Redirect

Redirect to URL:

```
HX-Redirect: /new-page
```

### HX-Refresh

Refresh current page:

```
HX-Refresh: true
```

### HX-Location

Client-side redirect with content swap:

```
HX-Location: /new-page
```

### HX-Push-Url

Push URL to history:

```
HX-Push-Url: /results?q=htmx
```

### HX-Replace-Url

Replace current history entry:

```
HX-Replace-Url: /status/updated
```

### HX-Trigger

Trigger client events:

```
HX-Trigger: search-complete
```

Or with payload:

```
HX-Trigger: {"name": "search-complete", "detail": {"query": "htmx"}}
```

### HX-Retarget

Override target element:

```
HX-Retarget: #custom-target
```

### HX-Reswap

Override swap style:

```
HX-Reswap: outerHTML
```

### HX-Reselect

Override `hx-select` value:

```
HX-Reselect: .different-selector
```

## Error Handling

### Error Event Details

```javascript
document.addEventListener('htmx:error', function(evt) {
  const error = evt.error;
  const requestConfig = evt.detail.requestConfig;
  const target = evt.target;
  const xhr = evt.detail.xhr; // Or fetchRequest
  
  console.log('Error:', error);
  console.log('Status:', xhr?.status);
  console.log('Response:', xhr?.response);
  
  // Custom error handling
  if (xhr?.status === 422) {
    showValidationErrors(xhr.response);
  } else if (xhr?.status >= 500) {
    showServerError();
  }
});
```

### Per-Element Error Handling

```html
<form hx-post="/submit"
      hx-on::htmx:error='(evt) => {
        const status = evt.detail.xhr.status;
        if (status === 422) {
          document.getElementById("errors").innerHTML = evt.detail.xhr.response;
        }
      }'>
  <button type="submit">Submit</button>
</form>
```
