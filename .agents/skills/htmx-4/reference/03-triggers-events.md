# Triggers and Events Reference

## Trigger Syntax Overview

The `hx-trigger` attribute specifies what events cause htmx to make a request. A trigger value can be:

- **Standard DOM event**: `click`, `input`, `submit`, `keyup`
- **Synthetic event**: `load`, `revealed`, `intersect`
- **Polling**: `every 1s`
- **Multiple triggers**: Comma-separated list
- **Event with filters**: `click[ctrlKey]`
- **Event with modifiers**: `input changed delay:1s`

```html
<!-- Simple event -->
<button hx-post="/action" hx-trigger="click">Click</button>

<!-- Event with filter -->
<input hx-get="/search" hx-trigger="keyup[key=='Enter']">

<!-- Event with modifiers -->
<input hx-get="/search" hx-trigger="input changed delay:1s">

<!-- Multiple triggers -->
<div hx-get="/data" hx-trigger="load, click refresh">Load</div>

<!-- Polling -->
<div hx-get="/updates" hx-trigger="every 5s">Updates...</div>
```

## Default Triggers

When `hx-trigger` is omitted, htmx uses element-specific defaults:

| Element | Default Trigger |
|---------|-----------------|
| `<input>`, `<textarea>`, `<select>` | `change` |
| `<form>` | `submit` |
| Everything else | `click` |

## Standard DOM Events

Any standard DOM event can trigger a request:

```html
<!-- Mouse events -->
<button hx-post="/action" hx-trigger="mousedown">MouseDown</button>
<div hx-get="/data" hx-trigger="mouseenter">Hover</div>

<!-- Keyboard events -->
<input hx-get="/search" hx-trigger="keydown">
<div hx-get="/next" hx-trigger="keyup[key=='ArrowRight']">Next</div>

<!-- Form events -->
<form hx-post="/submit" hx-trigger="submit">Submit</form>
<input hx-get="/validate" hx-trigger="input">

<!-- Focus events -->
<input hx-get="/focus-data" hx-trigger="focus">

<!-- Custom events -->
<div hx-get="/data" hx-trigger="my-custom-event">Custom</div>
```

## Event Filters

Filters are JavaScript expressions in `[brackets]` that must return `true` for the request to fire. The DOM event object is available inside the filter:

```html
<!-- Check event property -->
<div hx-get="/data" hx-trigger="click[ctrlKey]">Ctrl+Click</div>

<!-- Check key pressed -->
<input hx-get="/submit" hx-trigger="keyup[key=='Enter']">

<!-- Multiple conditions -->
<div hx-get="/data" hx-trigger="click[ctrlKey && shiftKey]">
  Ctrl+Shift+Click
</div>

<!-- Call global function -->
<button hx-post="/action" hx-trigger="click[canProceed()]">Action</button>

<script>
function canProceed() {
  return window.someState === 'ready';
}
</script>

<!-- Check element value -->
<input hx-get="/validate" hx-trigger="change[value.length > 3]">

<!-- Access event target -->
<div hx-get="/data" hx-trigger="click[target.classList.contains('active')]">
  Click active
</div>
```

**Security note:** Filters use `eval()` under the hood. Be careful with untrusted input.

## Event Modifiers

Modifiers change how events behave:

### `once`

Event triggers only once (first occurrence):

```html
<button hx-get="/load-once" hx-trigger="click once">Load Once</button>

<!-- Load content when first revealed -->
<div hx-get="/lazy-content" hx-trigger="revealed once">Loading...</div>
```

### `changed`

Only trigger if element's value changed since last trigger:

```html
<!-- Only send request if value actually changed -->
<input hx-get="/search" hx-trigger="input changed">

<!-- Combine with delay for efficient searching -->
<input hx-get="/search" hx-trigger="input changed delay:500ms">
```

Note: `change` is a DOM event. `changed` is an htmx modifier.

### `delay`

Wait before triggering (debounce). Resets if event fires again:

```html
<!-- Wait 1s after user stops typing -->
<input hx-get="/search" hx-trigger="input delay:1s">

<!-- Short delay for responsive UI -->
<div hx-get="/position" hx-trigger="scroll delay:100ms">
```

### `throttle`

Trigger immediately, then ignore events for interval:

```html
<!-- Max 2 scroll events per second -->
<div hx-get="/position" hx-trigger="scroll throttle:500ms">Scroll</div>
```

Timeline example:
```
  0ms  scroll → request fires
100ms  scroll → ignored (within throttle window)
200ms  scroll → ignored
500ms         → throttle window ends
600ms  scroll → request fires
```

### `from`

Listen for event on different element using CSS selector:

```html
<!-- Hotkey: listen for Enter on body -->
<div hx-get="/submit" hx-trigger="keyup[key=='Enter'] from:body">
  Press Enter anywhere
</div>

<!-- Listen on document -->
<div hx-get="/data" hx-trigger="custom-event from:document">Document Event</div>

<!-- Listen on closest form -->
<button hx-get="/validate" hx-trigger="submit from:closest form">Validate</button>

<!-- Listen on specific element -->
<div hx-get="/data" hx-trigger="click from:#trigger-btn">Triggered by #trigger-btn</div>
```

Selector is evaluated once at initialization, not re-evaluated.

### `target`

Only trigger if `event.target` matches selector:

```html
<!-- Listen on parent for clicks on children -->
<div hx-get="/data" hx-trigger="click target:.child-button from:body">
  <button class="child-button">Child 1</button>
  <button class="other-button">Child 2 (won't trigger)</button>
</div>
```

Useful for elements that might not exist yet.

### `consume`

Prevent event from propagating to parent htmx elements:

```html
<div hx-get="/parent">
  Parent
  <button hx-get="/child" hx-trigger="click consume">Child (stops propagation)</button>
</div>
```

Without `consume`, clicking child would trigger both requests.

### `queue`

Queue events if request already in flight:

```html
<!-- Queue all clicks -->
<button hx-post="/process" hx-trigger="click queue:all">Process All</button>

<!-- Queue only last click (default) -->
<button hx-post="/process" hx-trigger="click queue:last">Process Last</button>

<!-- Queue only first click -->
<button hx-post="/process" hx-trigger="click queue:first">Process First</button>

<!-- Don't queue (drop new events) -->
<button hx-post="/process" hx-trigger="click queue:none">Process One</button>
```

Options: `all`, `last` (default), `first`, `none`

## Synthetic Events

htmx provides synthetic events beyond standard DOM events:

### `load`

Fires when element is loaded into DOM:

```html
<!-- Load content immediately when page loads -->
<div hx-get="/initial-data" hx-trigger="load">Loading...</div>

<!-- Multiple elements can use load -->
<div hx-get="/header" hx-trigger="load"></div>
<div hx-get="/footer" hx-trigger="load"></div>
```

### `revealed`

Fires when element scrolls into viewport:

```html
<!-- Lazy load when scrolled into view -->
<div hx-get="/heavy-content" hx-trigger="revealed">Loading...</div>

<!-- Load images as user scrolls -->
<img hx-get="/image-large.jpg" hx-trigger="revealed" hx-swap="outerHTML">
```

For elements in scrolling containers, use `intersect` with `root` modifier instead.

### `intersect`

Fires when element intersects viewport (Intersection Observer):

```html
<!-- Basic intersection -->
<tr hx-get="/more-rows" hx-trigger="intersect once" hx-swap="afterend">
  <td>Load more...</td>
</tr>

<!-- With root container -->
<div hx-get="/data" hx-trigger="intersect root:#scroll-container">Intersect</div>

<!-- With threshold (50% visible) -->
<div hx-get="/data" hx-trigger="intersect threshold:0.5">50% Visible</div>

<!-- Fire only once -->
<div hx-get="/analytics" hx-trigger="intersect once">Track View</div>
```

Options:
- `root:selector`: Custom root element for intersection
- `threshold:X`: Float 0.0-1.0 for intersection percentage
- `once`: Fire only first time

## Polling

Use `every <duration>` to poll periodically:

```html
<!-- Poll every second -->
<div hx-get="/updates" hx-trigger="every 1s">Updates...</div>

<!-- Poll every 30 seconds -->
<div hx-get="/status" hx-trigger="every 30s">Status</div>

<!-- Poll with filter -->
<div hx-get="/updates" hx-trigger='every 5s [window.shouldPoll]'>Polling</div>

<script>
window.shouldPoll = true;
// Set to false to stop polling
</script>
```

Durations support: `ms`, `s` (seconds), `m` (minutes)

## Multiple Triggers

Comma-separated triggers, each with own options:

```html
<!-- Load on page load, then on click -->
<div hx-get="/data" hx-trigger="load, click">Data</div>

<!-- Different options per trigger -->
<div hx-get="/news" hx-trigger="load, click delay:1s">News</div>

<!-- Complex combination -->
<input hx-get="/search" hx-trigger="input changed delay:500ms, keyup[key=='Enter']">
```

## Custom Events

Trigger requests from custom events fired via JavaScript or server headers:

### From JavaScript

```html
<div hx-get="/data" hx-trigger="custom-event">Custom Event</div>

<script>
// Fire custom event
const event = new CustomEvent('custom-event', { detail: { data: 'value' } });
document.body.dispatchEvent(event);
</script>
```

### From Server (HX-Trigger Header)

Server sends `HX-Trigger: event-name` header:

```html
<!-- Listen on body for server-triggered events -->
<div hx-get="/update" hx-trigger="server-event from:body">Update</div>
```

```javascript
// Server response (Express.js example)
res.setHeader('HX-Trigger', 'server-event');
res.send('Response content');
```

### Accessing Event Detail

```html
<div hx-get="/data" hx-trigger="custom-event" hx-vals='js:getEventDetail(event)'>
  Custom
</div>

<script>
let lastDetail = {};
document.addEventListener('custom-event', (e) => {
  lastDetail = e.detail;
});

function getEventDetail() {
  return lastDetail;
}
</script>
```

## htmx Events Reference

htmx fires events at various lifecycle points. All follow pattern: `htmx:phase:action[:sub-action]`

### Request Lifecycle Events

| Event | Fires | Cancellable |
|-------|-------|-------------|
| `htmx:before:init` | Before htmx initializes | No |
| `htmx:after:init` | After htmx initializes | No |
| `htmx:before:process` | Before element is processed | No |
| `htmx:after:process` | After element is processed | No |
| `htmx:before:request` | Before request starts | Yes |
| `htmx:config:request` | During request configuration | Yes |
| `htmx:before:send` | Before request sent | No |
| `htmx:before:response` | Before response read | Yes |
| `htmx:after:request` | After request completes | No |
| `htmx:finally:request` | Always after request (success/failure) | No |

### Swap Events

| Event | Fires | Cancellable |
|-------|-------|-------------|
| `htmx:before:swap` | Before content swapped | Yes |
| `htmx:after:swap` | After content swapped | No |
| `htmx:before:settle` | Before settle phase | No |
| `htmx:after:settle` | After settle phase | No |

### History Events

| Event | Fires | Cancellable |
|-------|-------|-------------|
| `htmx:before:history:push` | Before pushing to history | No |
| `htmx:after:history:push` | After pushing to history | No |
| `htmx:before:history:replace` | Before replacing history | No |
| `htmx:after:history:replace` | After replacing history | No |
| `htmx:before:history:update` | Before history update | No |
| `htmx:after:history:update` | After history update | No |
| `htmx:before:restore-history` | Before restoring from history | No |

### Error Events

All errors consolidated to single event:

| Event | Fires | Details |
|-------|-------|---------|
| `htmx:error` | On any error | `error`, `request`, `target`, `detail` |

### View Transition Events

| Event | Fires | Cancellable |
|-------|-------|-------------|
| `htmx:before:viewTransition` | Before view transition | Yes |
| `htmx:after:viewTransition` | After view transition | No |

### Cleanup Events

| Event | Fires | Cancellable |
|-------|-------|-------------|
| `htmx:before:cleanup` | Before element cleanup | No |
| `htmx:after:cleanup` | After element cleanup | No |

## Event Listeners

### Using `hx-on` Attribute

```html
<!-- Listen to htmx events -->
<div hx-get="/data"
     hx-on::htmx:before-request="event => {
       if (!isValid()) event.preventDefault();
     }"
     hx-on::htmx:after-swap="event => {
       console.log('Swapped!', event.detail);
     }">
  Load Data
</div>

<!-- Multiple listeners -->
<form hx-post="/submit"
      hx-on::htmx:before-send="startSpinner()"
      hx-on::htmx:after-request="stopSpinner()">
  <button type="submit">Submit</button>
</form>
```

### Using JavaScript

```javascript
// Global listener
document.body.addEventListener('htmx:before:request', function(evt) {
  console.log('Request about to start:', evt.target);
});

// Element-specific listener
const element = document.querySelector('#my-element');
element.addEventListener('htmx:after:swap', function(evt) {
  console.log('Swap complete:', evt.detail);
});

// Using htmx.on()
htmx.on('htmx:before:request', function(evt) {
  // Handler
}, document.body);
```

### Event Object Structure

```javascript
document.addEventListener('htmx:after:request', function(evt) {
  // evt.target: Element that triggered request
  // evt.detail: Detail object with request info
  
  const detail = evt.detail;
  console.log('Request:', detail.requestConfig);
  console.log('Response:', detail.xhr || detail.fetchRequest);
  console.log('PathInfo:', detail.pathInfo);
  console.log('Failed:', detail.failed);
  console.log('Success:', detail.success);
});
```

## Migration from htmx 2.x Event Names

| htmx 2.x | htmx 4.x |
|----------|----------|
| `htmx:beforeRequest` | `htmx:before:request` |
| `htmx:afterRequest` | `htmx:after:request` |
| `htmx:beforeSwap` | `htmx:before:swap` |
| `htmx:afterSwap` | `htmx:after:swap` |
| `htmx:afterSettle` | `htmx:after:swap` |
| `htmx:configRequest` | `htmx:config:request` |
| `htmx:beforeProcessNode` | `htmx:before:process` |
| `htmx:afterProcessNode` | `htmx:after:init` |
| `htmx:historyRestore` | `htmx:before:restore-history` |
| `htmx:pushedIntoHistory` | `htmx:after:history:push` |
| All error events | `htmx:error` |

Validation events (`htmx:validation:*`) and XHR events (`htmx:xhr:*`) are removed.
