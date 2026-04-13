# htmx Triggers and Events Reference

This reference covers the complete trigger system, event handling, and timing mechanisms in htmx 2.x.

## Trigger Fundamentals

### Natural Triggers

By default, elements trigger on their "natural" events:

| Element Type | Natural Trigger |
|--------------|-----------------|
| `button`, `a`, `input[type="button"]` | `click` |
| `form` | `submit` |
| `input`, `select`, `textarea` | `change` |
| All other elements | `click` |

```html
<!-- Button triggers on click -->
<button hx-post="/save">Save</button>

<!-- Form triggers on submit -->
<form hx-post="/submit">
    <input name="data">
    <button type="submit">Submit</button>
</form>

<!-- Input triggers on change (when blurred after modification) -->
<input name="status" hx-post="/update-status">

<!-- Div triggers on click -->
<div hx-get="/content">Click me</div>
```

### Custom Triggers

Use `hx-trigger` to specify custom events:

```html
<!-- Mouse events -->
<div hx-get="/track" 
     hx-trigger="mouseenter">
    Hover me
</div>

<div hx-post="/click" 
     hx-trigger="dblclick">
    Double-click me
</div>

<!-- Keyboard events -->
<input name="search" 
       hx-get="/search" 
       hx-trigger="keyup">
       Type to search
</input>

<!-- Form events -->
<form hx-get="/validate" 
      hx-trigger="invalid">
    <input name="email" type="email" required>
</form>

<!-- Custom events -->
<div hx-get="/handle" 
     hx-trigger="custom-event">
    Trigger custom event
</div>
<script>
    htmx.trigger(document.querySelector('div'), 'custom-event');
</script>
```

## Trigger Modifiers

### once

Trigger only one time:

```html
<!-- Trigger on first click only -->
<button hx-get="/init" 
        hx-trigger="click once">
    Initialize
</button>

<!-- Trigger on load, once -->
<div hx-get="/analytics" 
     hx-trigger="load once">
    Track Pageview
</div>

<!-- Polling that stops after first response -->
<div hx-get="/status" 
     hx-trigger="every 5s once">
    Check Status Once
</div>
```

### changed

Only trigger if element value has changed:

```html
<!-- Only send request if input value changed -->
<input name="username" 
       hx-post="/update-username" 
       hx-trigger="input changed">
       Type username
</input>

<!-- Combined with delay for debounced search -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="keyup changed delay:300ms"
       hx-target="#results">
       Search...
</input>

<!-- Works with select elements -->
<select name="category" 
        hx-get="/products" 
        hx-trigger="changed">
    <option value="electronics">Electronics</option>
    <option value="books">Books</option>
</select>
```

### delay:Xms

Wait X milliseconds after event before triggering (debounce):

```html
<!-- Wait 500ms after last keyup -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="keyup changed delay:500ms"
       placeholder="Search...">

<!-- Delay on mouse movement -->
<div hx-get="/position" 
     hx-trigger="mousemove delay:100ms">
    Track Mouse
</div>

<!-- Multiple delays for different events -->
<div hx-get="/update" 
     hx-trigger="click delay:200ms, mouseenter delay:1s">
    Update
</div>
```

**Use case:** Debouncing user input to avoid excessive requests.

### throttle:Xms

Throttle events to once per X milliseconds:

```html
<!-- Send position update at most every 100ms -->
<div hx-get="/track" 
     hx-trigger="scroll throttle:100ms">
    Long content...
</div>

<!-- Throttled mouse tracking -->
<div hx-get="/mouse-position" 
     hx-trigger="mousemove throttle:50ms">
    Move mouse
</div>

<!-- Difference from delay: throttle sends immediately, then waits -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="keyup throttle:300ms">
       <!-- First keyup triggers immediately, next triggers 300ms later -->
</input>
```

**Comparison:**
- `delay`: Waits X ms after event stops, then triggers once
- `throttle`: Triggers immediately, then waits X ms before next trigger

### from:selector

Listen for events on a different element:

```html
<!-- Trigger when another element is clicked -->
<button id="trigger-btn">Click me</button>
<div hx-get="/response" 
     hx-trigger="click from:#trigger-btn">
    Response appears here
</div>

<!-- Keyboard shortcuts -->
<div hx-get="/save" 
     hx-trigger="keyup from:body[key=='s' && ctrlKey]">
    (Press Ctrl+S to save)
</div>

<!-- Trigger from parent container -->
<div id="container">
    <button>Button 1</button>
    <button>Button 2</button>
</div>
<div hx-get="/clicked" 
     hx-trigger="click from:#container">
    Container clicked
</div>

<!-- Combine with other modifiers -->
<input name="search">
<div hx-get="/results" 
     hx-trigger="keyup changed delay:300ms from:input[name='search']"
     id="results">
    Search results
</div>
```

### filter[expression]

Only trigger if JavaScript expression evaluates to true:

```html
<!-- Only trigger on Ctrl+Click -->
<div hx-get="/special" 
     hx-trigger="click[ctrlKey]">
    Ctrl+Click me
</div>

<!-- Only trigger if input has value -->
<input name="data">
<button hx-post="/submit" 
        hx-trigger="click[this.value.length > 0]">
    Submit if has value
</button>

<!-- Trigger on specific key -->
<div hx-get="/handle" 
     hx-trigger="keyup[key=='Escape']">
    Press Escape
</div>

<!-- Complex condition -->
<button hx-post="/action" 
        hx-trigger="click[confirmed && value > 0]">
    Action
</button>

<!-- Access event properties -->
<div hx-get="/click-info" 
     hx-trigger="click[buttons === 1]">
    Left-click only
</div>
```

**Available in filter:**
- Event properties: `ctrlKey`, `shiftKey`, `altKey`, `key`, `buttons`, etc.
- Element properties: `this.value`, `this.checked`, etc.
- Global variables and functions

## Special Trigger Events

### load

Trigger when element is loaded into the DOM:

```html
<!-- Trigger immediately when page loads -->
<div hx-get="/init" 
     hx-trigger="load">
    Initialize component
</div>

<!-- Load once on page load -->
<div hx-get="/analytics" 
     hx-trigger="load once">
    Track initial pageview
</div>

<!-- Combined with delay -->
<div hx-get="/delayed-init" 
     hx-trigger="load delay:1s">
    Initialize after 1 second
</div>
```

### revealed

Trigger when element scrolls into viewport:

```html
<!-- Lazy load images -->
<div hx-get="/image-content" 
     hx-trigger="revealed"
     hx-swap="outerHTML">
    <img src="placeholder.jpg" alt="Loading...">
</div>

<!-- Load more content on scroll -->
<div hx-get="/more-posts" 
     hx-trigger="revealed"
     hx-swap="beforeend"
     id="loader">
    <p>Loading more...</p>
</div>

<!-- Ad loading (only when visible) -->
<div hx-get="/ad" 
     hx-trigger="revealed once">
    Ad placeholder
</div>
```

### intersect

Trigger when element intersects viewport with options:

```html
<!-- Trigger when 50% of element is visible -->
<div hx-get="/content" 
     hx-trigger="intersect threshold:0.5">
    Content
</div>

<!-- Use custom root element -->
<div id="viewport">
    <div hx-get="/content" 
         hx-trigger="intersect root:#viewport threshold:1.0">
        Content when fully visible in viewport
    </div>
</div>

<!-- Multiple thresholds -->
<div hx-get="/track" 
     hx-trigger="intersect threshold:0.25, intersect threshold:0.5, intersect threshold:0.75">
    Track visibility progress
</div>
```

**Options:**
- `threshold:X` - Visibility threshold (0.0 to 1.0)
- `root:selector` - Custom root element for intersection

### every Xms

Poll at specified interval:

```html
<!-- Poll every 5 seconds -->
<div hx-get="/notifications" 
     hx-trigger="every 5s"
     hx-target="#notification-area">
    Notifications
</div>

<!-- Poll every 30 seconds -->
<div hx-get="/status" 
     hx-trigger="every 30s">
    System Status
</div>

<!-- Poll every 100 milliseconds (fast polling) -->
<div hx-get="/realtime-data" 
     hx-trigger="every 100ms">
    Real-time data
</div>

<!-- Stop polling with HTTP 286 status code -->
<!-- Server returns 286 When done to stop polling -->
```

**Stopping polling:**
- Server returns HTTP 286 (No Operation) status code
- Element is removed from DOM
- Manual trigger cancellation via JavaScript

### Multiple Triggers

Combine multiple triggers with commas:

```html
<!-- Trigger on click or Enter key -->
<button hx-post="/submit" 
        hx-trigger="click, keyup[key=='Enter']">
    Submit
</button>

<!-- Polling with manual trigger -->
<div hx-get="/data" 
     hx-trigger="every 10s, click">
    Refresh (auto or click)
</div>

<!-- Multiple events with different modifiers -->
<input name="search" 
       hx-get="/results" 
       hx-trigger="keyup changed delay:300ms, blur changed">
       Search...
</input>

<!-- Complex combination -->
<div hx-get="/update" 
     hx-trigger="mouseenter once, click, every 1m">
    Update on hover, click, or every minute
</div>
```

## Trigger Extensions

### WebSocket Triggers

Trigger requests based on WebSocket messages:

```html
<!-- Connect to WebSocket -->
<div hx-ws="connect:/ws">
    
    <!-- Trigger on specific message type -->
    <div hx-trigger="ws-message from:/ws"
         hx-get="/process-message"
         hx-target="#output">
        Messages appear here
    </div>
    
    <!-- Send message via WebSocket -->
    <button hx-ws="send:chat"
            hx-vals='{"text": "Hello"}'>
        Send Message
    </button>
</div>
```

See [WebSockets and SSE](06-websockets-sse.md) for detailed WebSocket documentation.

### SSE Triggers

Trigger on Server-Sent Events:

```html
<!-- Connect to SSE endpoint -->
<div hx-sse-connect="/events">
    
    <!-- Trigger on specific event -->
    <div hx-trigger="message from:/events"
         hx-get="/handle-event"
         hx-target="#updates">
        Updates appear here
    </div>
    
    <!-- Trigger on different event types -->
    <div hx-trigger="user_joined from:/events"
         hx-swap="beforeend">
        Track joins
    </div>
</div>
```

## Event System Overview

htmx fires events at every stage of the request lifecycle:

```
┌───────────────────────────────────────────────────────────────────────┐
│                        htmx Request Lifecycle                          │
├───────────────────────────────────────────────────────────────────────┤
│ 1. htmx:beforeProcessNode (before element is initialized)             │
│ 2. htmx:afterProcessNode (after element is initialized)               │
│ 3. htmx:confirm (before request, can cancel)                          │
│ 4. htmx:beforeRequest (before XHR created, can cancel)                │
│ 5. htmx:configRequest (parameters collected, can modify)              │
│ 6. htmx:beforeSend (just before request sent)                         │
│ 7. htmx:beforeOnLoad (response received, before processing)           │
│ 8. htmx:beforeSwap (before DOM update, can modify swap)               │
│ 9. htmx:afterSwap (content swapped into DOM)                          │
│10. htmx:afterSettle (attributes settled)                              │
│11. htmx:afterRequest (request complete)                               │
│12. htmx:load (new content loaded)                                     │
└───────────────────────────────────────────────────────────────────────┘
```

### Event Handlers with hx-on

Attach event handlers directly in HTML:

```html
<!-- Handle before request -->
<button hx-post="/save"
        hx-on::before-request="event.target.disabled = true">
    Save
</button>

<!-- Handle after swap -->
<div hx-get="/content"
     hx-on::after-swap="htmx.trigger(this, 'contentLoaded')">
    Content
</div>

<!-- Multiple handlers -->
<button hx-post="/submit"
        hx-on::before-request="this.classList.add('loading')"
        hx-on::after-request="this.classList.remove('loading')">
    Submit
</button>

<!-- Access event detail -->
<div hx-get="/data"
     hx-on::after-swap="console.log(event.detail.xhr.status)">
    Data
</div>

<!-- Call JavaScript function -->
<button hx-post="/action"
        hx-on::after-swap="handleResponse(event)">
    Action
</button>
<script>
    function handleResponse(event) {
        console.log('Response handled:', event.detail);
    }
</script>
```

**Syntax:** `hx-on::event-name="javascript code"`

### Event Details

All htmx events provide detail objects with context:

| Property | Description |
|----------|-------------|
| `detail.elt` | Element that triggered the request |
| `detail.target` | Target element for the swap |
| `detail.xhr` | XMLHttpRequest object |
| `detail.requestConfig` | Request configuration object |
| `detail.shouldSwap` | Whether content will be swapped (beforeSwap) |
| `detail.serverResponse` | Server response text (beforeSwap) |
| `detail.successful` | Whether request was successful (afterRequest) |
| `detail.failed` | Whether request failed (afterRequest) |

### Common Event Patterns

#### Cancel Request

```html
<!-- Confirm before delete -->
<button hx-delete="/api/item"
        hx-confirm="Delete this item?">
    Delete
</button>

<!-- Programmatic cancellation -->
<script>
    document.body.addEventListener('htmx:beforeRequest', (event) => {
        if (shouldCancel()) {
            event.preventDefault();
        }
    });
</script>
```

#### Modify Request Parameters

```javascript
// Add CSRF token to all requests
document.body.addEventListener('htmx:configRequest', (event) => {
    event.detail.parameters.csrf_token = getCSRFToken();
});

// Add timestamp to specific requests
document.body.addEventListener('htmx:configRequest', (event) => {
    if (event.detail.elt.classList.contains('timed')) {
        event.detail.parameters.timestamp = Date.now();
    }
});
```

#### Modify Swap Behavior

```javascript
// Use morphing for specific elements
document.body.addEventListener('htmx:beforeSwap', (event) => {
    if (event.detail.target.classList.contains('morph')) {
        event.detail.swapOverride = 'morphdom';
    }
});

// Conditional swapping based on response
document.body.addEventListener('htmx:beforeSwap', (event) => {
    if (event.detail.serverResponse.includes('ERROR')) {
        event.detail.shouldSwap = false;
    }
});
```

#### Handle Errors

```javascript
// Global error handler
document.body.addEventListener('htmx:afterRequest', (event) => {
    if (event.detail.failed) {
        console.error('Request failed:', event.detail.xhr.status);
        showNotification('Request failed', 'error');
    }
});

// Success handler
document.body.addEventListener('htmx:afterRequest', (event) => {
    if (event.detail.successful) {
        showNotification('Success!', 'success');
    }
});
```

#### Track Analytics

```javascript
// Track all htmx requests
document.body.addEventListener('htmx:beforeRequest', (event) => {
    analytics.track('htmx_request', {
        verb: event.detail.requestConfig.verb,
        path: event.detail.requestConfig.path,
        element: event.detail.elt.tagName
    });
});

// Track successful swaps
document.body.addEventListener('htmx:afterSwap', (event) => {
    analytics.track('htmx_swap', {
        target: event.detail.target.id,
        swapStyle: event.detail.requestConfig.swapSpec.swapStyle
    });
});
```

## Debugging Triggers

### Enable Logging

```javascript
// Log all htmx events
htmx.logAll();

// Custom logger
htmx.logger = function(elt, eventName, detail) {
    console.log(`[${eventName}]`, elt, detail);
};
```

### Inspect Trigger Configuration

```javascript
// Get trigger specs for an element
const element = document.querySelector('[hx-get]');
const triggerSpecs = htmx.getValue(element, 'hx-trigger');
console.log('Triggers:', triggerSpecs);
```

### Test Triggers Manually

```javascript
// Manually trigger an element
const button = document.querySelector('[hx-post]');
htmx.trigger(button, 'click');

// Trigger custom event
htmx.trigger(document.body, 'custom-event', {data: 'value'});
```

## Next Steps

- [Swapping](04-swapping.md) - DOM swap modes and options
- [Events and API Reference](08-events-api.md) - Complete event documentation
- [Common Patterns](10-common-patterns.md) - Real-world trigger patterns
