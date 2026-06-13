# Events and JavaScript API

Complete reference for htmx events, the JavaScript API, and scripting patterns.

## Event Reference

All htmx events are custom DOM events. Listen with `addEventListener` or `hx-on*`.

### Request Lifecycle Events

| Event | Timing | Cancelable | Detail |
|-------|--------|------------|--------|
| `htmx:beforeRequest` | Before request starts | Yes | `elt`, `path`, `triggeringEvent`, `requestConfig` |
| `htmx:beforeSend` | XHR created, before send | Yes | `xhr`, `elt`, `path` |
| `htmx:afterRequest` | After request completes | No | `xhr`, `elt`, `failed`, `successful`, `path` |
| `htmx:afterOnLoad` | After all onLoad handlers | No | `elt`, `xhr` |
| `htmx:confirm` | Before request, for custom confirm | Yes | `detail` — call `preventDefault()` and resolve manually |

### Config Event

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:configRequest` | Before sending, modify request | `parameters`, `unfilteredParameters`, `headers`, `errors`, `withCredentials`, `timeout`, `messageBody`, `confirmMessage`, `triggeringEvent` |

```javascript
document.body.addEventListener('htmx:configRequest', function(evt) {
  evt.detail.headers['X-Custom-Auth'] = getAuthToken();
});
```

### Swap Events

| Event | Timing | Cancelable | Detail |
|-------|--------|------------|--------|
| `htmx:beforeOnLoad` | Response received, before parsing | Yes | `elt`, `xhr`, `target`, `withCredentials` |
| `htmx:beforeSwap` | Before DOM swap | Yes (modify `detail.swapStyle`) | `elt`, `xhr`, `target`, `shouldSwap`, `swapStyle`, `detail` |
| `htmx:afterSwap` | After DOM swap, before settle | No | `elt`, `xhr`, `target`, `finalElts` |
| `htmx:beforeSettle` | Before attribute settling | Yes | `elt`, `xhr`, `toSwapElts`, `detail` |
| `htmx:afterSettle` | After attribute settling | No | `elt`, `xhr`, `toSwapElts` |
| `htmx:load` | On target element after swap | No | `target` |

```javascript
document.body.addEventListener('htmx:beforeSwap', function(evt) {
  if (evt.detail.xhr.status === 403) {
    evt.detail.shouldSwap = false;
    alert('Access denied!');
  }
});
```

### History Events

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:historyCacheError` | History cache error | `error`, `elt` |
| `htmx:beforeHistorySave` | Before saving history snapshot | `historyCache` |
| `htmx:afterHistoryRestore` | After restoring from history | `path` |
| `htmx:beforeHistoryUpdate` | Before pushing to history | `title`, `url` |

### Validation Events

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:validation:validate` | During validation | `name`, `valid`, `value`, `elt`, `error`, `errors` |
| `htmx:validation:failed` | Validation failed | `name`, `valid`, `value`, `elt`, `error`, `errors` |
| `htmx:validation:halted` | Request halted due to validation | `elt`, `errors` |
| `htmx:validation:warn` | Validation warning | `name`, `message`, `elt` |

### Error Events

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:responseError` | HTTP error response | `error`, `xhr`, `elt`, `failureCode` |
| `htmx:timeout` | Request timeout | `elapsedTime`, `elt` |
| `htmx:abort` | Request aborted | `elt` |
| `htmx:sending` | Alias for beforeSend | — |

### SSE Extension Events

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:sseOpen` | SSE connection established | `elt`, `source` |
| `htmx:sseError` | SSE connection error | `error`, `source` |
| `htmx:sseBeforeMessage` | Before SSE message swap | `elt` — cancelable |
| `htmx:sseMessage` | After SSE message swap | `elt` |
| `htmx:sseClose` | SSE connection closed | `elt`, `type` (nodeMissing/nodeReplaced/message) |

### WebSocket Extension Events

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:wsConnecting` | Connection attempt | `event.type` |
| `htmx:wsOpen` | Connection established | `elt`, `event`, `socketWrapper` |
| `htmx:wsClose` | Connection closed | `elt`, `event`, `socketWrapper` |
| `htmx:wsError` | Socket error | `elt`, `error`, `socketWrapper` |
| `htmx:wsBeforeMessage` | Message received, before processing | `elt`, `message`, `socketWrapper` — cancelable |
| `htmx:wsAfterMessage` | After message processed | `elt`, `message`, `socketWrapper` |
| `htmx:wsConfigSend` | Before sending, modify message | `parameters`, `headers`, `errors`, `messageBody`, `elt`, `socketWrapper` — cancelable |
| `htmx:wsBeforeSend` | Just before send | `elt`, `message`, `socketWrapper` — cancelable |
| `htmx:wsAfterSend` | After send | `elt`, `message`, `socketWrapper` |

## JavaScript API

### Event Handling

```javascript
// Listen for any htmx event
htmx.on('htmx:afterRequest', function(evt) {
  console.log('Request completed:', evt.detail.path);
});

// Listen on specific element
htmx.on(document.getElementById('form'), 'htmx:afterRequest', function(evt) {
  console.log('Form submitted');
});

// Remove listener
const handler = function(evt) { /* ... */ };
htmx.on('htmx:afterRequest', handler);
htmx.off('htmx:afterRequest', handler);
```

### onLoad Handlers

Register callbacks for elements swapped into the DOM:

```javascript
htmx.onLoad(function(elt) {
  // Called for every element with htmx attributes after swap
  if (elt.querySelector('.chart')) {
    initChart(elt.querySelector('.chart'));
  }
});

// With selector filter
htmx.onLoad('.sortable', function(elt) {
  new Sortable(elt, { /* options */ });
});
```

### DOM Helpers

```javascript
// Find single element (like document.getElementById for IDs, querySelector for others)
const el = htmx.find('#my-element');
const el = htmx.find('.my-class');

// Find all matching elements
const els = htmx.findAll('.items');

// Find closest ancestor
const row = htmx.closest(button, 'tr');
```

### Trigger Events Programmatically

```javascript
// Trigger a custom event on an element
htmx.trigger('#my-element', 'custom:event', { data: 'value' });

// Trigger on body
htmx.trigger(window, 'refresh-data');
```

### AJAX Requests from JavaScript

```javascript
// GET request
htmx.ajax('GET', '/items/42', '#result');

// POST with form values
htmx.ajax('POST', '/items', {
  source: '#my-form',
  target: '#result',
  headers: { 'X-Custom': 'value' }
});

// With values
htmx.ajax('GET', '/search', {
  values: { q: 'hello', page: 1 },
  target: '#results'
});
```

### Swap Content Programmatically

```javascript
htmx.swap('#target', '<p>New content</p>', 'innerHTML');
htmx.swap('#target', '<p>New content</p>', 'innerHTML transition:true');
```

### Process Elements

Re-process an element (or subtree) for htmx attributes:

```javascript
// Useful after dynamically inserting HTML
const div = document.createElement('div');
div.innerHTML = '<button hx-get="/data">Load</button>';
document.body.appendChild(div);
htmx.process(div);
```

### Get Form Values

```javascript
const values = htmx.values(document.getElementById('my-form'));
// Returns: { name: "John", age: "30" }
```

### Logging

```javascript
// Log all htmx events to console
htmx.logAll();

// Set custom logger
htmx.logger = {
  log: function(...args) { console.log('[htmx]', ...args); },
  error: function(...args) { console.error('[htmx]', ...args); }
};
```

## Scripting Patterns

### Inline Scripting with hx-on*

```html
<button hx-post="/save"
        hx-on::before-request="this.disabled = true; this.textContent = 'Saving...'"
        hx-on::after-request="this.disabled = false; this.textContent = 'Saved!'"
        hx-on::error="this.disabled = false; this.textContent = 'Retry'">
  Save
</button>
```

### 3rd Party Library Initialization

```html
<div hx-get="/chart-data"
     hx-on::after-on-load="initChart(this.querySelector('canvas'))">
</div>
```

### Cleanup Before History Save

```javascript
document.body.addEventListener('htmx:beforeHistorySave', function(evt) {
  // Clean up 3rd party library state before saving snapshot
  document.querySelectorAll('.tom-select').forEach(function(el) {
    if (el.tomselect) el.tomselect.destroy();
  });
});

document.body.addEventListener('htmx:afterHistoryRestore', function(evt) {
  // Re-initialize after restore
  document.querySelectorAll('.tom-select').forEach(function(el) {
    new TomSelect(el, { /* options */ });
  });
});
```

### Custom Confirm Dialog

```javascript
document.body.addEventListener('htmx:confirm', function(evt) {
  evt.preventDefault();
  evt.detail.issueRequest = function() {
    // Custom dialog logic
    if (confirm(evt.detail.question)) {
      evt.detail.issueRequest();
    }
  };
});
```

### Intercept and Modify Responses

```javascript
document.body.addEventListener('htmx:beforeOnLoad', function(evt) {
  // Modify response text before parsing
  const text = evt.detail.xhr.responseText;
  if (text.includes('<html')) {
    // Full page response — extract body
    evt.detail.shouldSwap = false;
  }
});
```
