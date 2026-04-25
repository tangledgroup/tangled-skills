# htmx Events and JavaScript API Reference

This reference covers the complete event system and JavaScript API for htmx 2.x.

## Event System Overview

htmx fires events at every stage of the request lifecycle, allowing you to inspect and modify behavior.

### Request Lifecycle Events

#### htmx:beforeProcessNode

Fired before htmx processes a DOM node:

```javascript
document.body.addEventListener('htmx:beforeProcessNode', (event) => {
    const element = event.detail.elt;
    console.log('About to process:', element);
    
    // Modify element before processing
    if (shouldModify(element)) {
        element.setAttribute('hx-disabled', 'true');
    }
});
```

**Detail properties:**
- `elt` - Element being initialized

#### htmx:afterProcessNode

Fired after htmx processes a DOM node:

```javascript
document.body.addEventListener('htmx:afterProcessNode', (event) => {
    const element = event.detail.elt;
    console.log('Processed:', element);
    
    // Initialize third-party libraries
    if (element.querySelector('.tooltip')) {
        Tooltip.init(element);
    }
});
```

#### htmx:beforeRequest

Fired before an AJAX request is issued:

```javascript
document.body.addEventListener('htmx:beforeRequest', (event) => {
    console.log('Request starting:', {
        element: event.detail.elt,
        target: event.detail.target,
        verb: event.detail.requestConfig.verb,
        path: event.detail.requestConfig.path
    });
    
    // Cancel request
    if (shouldCancel()) {
        event.preventDefault();
    }
});
```

**Detail properties:**
- `elt` - Element that dispatched the request
- `target` - Target element
- `boosted` - Whether request is via boosted element
- `requestConfig` - Request configuration object

#### htmx:configRequest

Fired after parameters are collected, allows modification:

```javascript
document.body.addEventListener('htmx:configRequest', (event) => {
    // Add CSRF token to all requests
    event.detail.parameters.csrf_token = getCSRFToken();
    
    // Add custom headers
    event.detail.headers['X-Custom-Header'] = 'value';
    
    // Modify parameters
    event.detail.parameters.timestamp = Date.now();
});
```

**Detail properties:**
- `parameters` - Request parameters (modifiable)
- `unfilteredParameters` - Parameters before hx-params filtering
- `headers` - Request headers (modifiable)
- `elt` - Triggering element
- `target` - Target element
- `verb` - HTTP verb

#### htmx:beforeSend

Fired just before request is sent (cannot cancel):

```javascript
document.body.addEventListener('htmx:beforeSend', (event) => {
    console.log('Sending request:', event.detail.requestConfig.path);
    
    // Show loading indicator
    showLoadingSpinner();
});
```

#### htmx:beforeOnLoad

Fired after response is received, before processing:

```javascript
document.body.addEventListener('htmx:beforeOnLoad', (event) => {
    // Cancel swap entirely
    if (shouldCancelSwap()) {
        event.preventDefault();
    }
    
    // Access response
    console.log('Response received:', event.detail.xhr.responseText);
});
```

#### htmx:beforeSwap

Fired before content is swapped into DOM:

```javascript
document.body.addEventListener('htmx:beforeSwap', (event) => {
    console.log('About to swap:', {
        target: event.detail.target,
        response: event.detail.serverResponse.substring(0, 100),
        swapStyle: event.detail.requestConfig.swapSpec.swapStyle
    });
    
    // Cancel swap
    if (shouldCancel()) {
        event.preventDefault();
    }
    
    // Modify swap behavior
    event.detail.shouldSwap = true;           // Whether to swap
    event.detail.ignoreTitle = false;         // Whether to update title
    event.detail.isError = false;             // Whether this is an error
    event.detail.selectOverride = '.content'; // Override hx-select
    event.detail.swapOverride = 'innerHTML';  // Override hx-swap
    event.detail.target = document.getElementById('new-target'); // Change target
});
```

**Detail properties:**
- `elt` - Target of the swap
- `xhr` - XMLHttpRequest object
- `boosted` - Whether request was boosted
- `requestConfig` - Request configuration
- `shouldSwap` - Whether content will be swapped (modifiable)
- `ignoreTitle` - Whether to ignore title tags (modifiable)
- `isError` - Whether error events should trigger (modifiable)
- `serverResponse` - Server response text
- `selectOverride` - Override for hx-select
- `swapOverride` - Override for hx-swap
- `target` - Target element (modifiable)

#### htmx:afterSwap

Fired after content is swapped into DOM:

```javascript
document.body.addEventListener('htmx:afterSwap', (event) => {
    console.log('Swapped content:', event.detail.elt);
    
    // Initialize new content
    initializeNewContent(event.detail.elt);
});
```

#### htmx:afterSettle

Fired after DOM has settled:

```javascript
document.body.addEventListener('htmx:afterSettle', (event) => {
    console.log('Settled:', event.detail.elt);
    
    // Scroll to updated content
    event.detail.elt.scrollIntoView({ behavior: 'smooth' });
});
```

#### htmx:afterRequest

Fired after request completes:

```javascript
document.body.addEventListener('htmx:afterRequest', (event) => {
    if (event.detail.successful) {
        console.log('Request successful');
        showNotification('Success!', 'success');
    } else if (event.detail.failed) {
        console.error('Request failed:', event.detail.xhr.status);
        showNotification('Error', 'error');
    }
});
```

**Detail properties:**
- `successful` - Whether response has 20x status
- `failed` - Whether request failed
- `xhr` - XMLHttpRequest object

### Confirmation Events

#### htmx:confirm

Fired on every trigger, allows async confirmation:

```javascript
document.body.addEventListener('htmx:confirm', (event) => {
    // Check if element has custom confirm attribute
    if (event.detail.target.hasAttribute('data-confirm-custom')) {
        event.preventDefault();
        
        // Show custom confirmation dialog
        customConfirm(event.detail.question).then((confirmed) => {
            if (confirmed) {
                event.detail.issueRequest(true); // Skip built-in confirm
            }
        });
    }
});
```

**Detail properties:**
- `elt` - Element in question
- `issueRequest(skipConfirmation)` - Function to issue request
- `path` - Request path
- `target` - Target element
- `triggeringEvent` - Original event
- `verb` - HTTP verb
- `question` - Confirmation question text

### History Events

#### htmx:historyRestore

Fired when history restoration occurs:

```javascript
document.body.addEventListener('htmx:historyRestore', (event) => {
    console.log('Restoring history:', {
        path: event.detail.path,
        cacheMiss: event.detail.cacheMiss
    });
});
```

#### htmx:beforeHistorySave

Fired before content is saved to history cache:

```javascript
document.body.addEventListener('htmx:beforeHistorySave', (event) => {
    // Modify content before saving
    const elt = event.detail.historyElt;
    
    // Remove temporary elements
    elt.querySelectorAll('.temp').forEach(el => el.remove());
});
```

#### htmx:historyCacheMiss

Fired when history cache miss occurs:

```javascript
document.body.addEventListener('htmx:historyCacheMiss', (event) => {
    console.log('Cache miss for:', event.detail.path);
    
    // Modify request before fetching
    event.detail.xhr.setRequestHeader('X-From-History', 'true');
});
```

### Out-of-Band Swap Events

#### htmx:oobBeforeSwap

Fired before OOB swap:

```javascript
document.body.addEventListener('htmx:oobBeforeSwap', (event) => {
    console.log('OOB swap:', {
        target: event.detail.target,
        fragment: event.detail.fragment
    });
    
    // Cancel this OOB swap
    event.detail.shouldSwap = false;
});
```

#### htmx:oobAfterSwap

Fired after OOB swap:

```javascript
document.body.addEventListener('htmx:oobAfterSwap', (event) => {
    console.log('OOB swapped:', event.detail.elt);
});
```

#### htmx:oobErrorNoTarget

Fired when OOB target not found:

```javascript
document.body.addEventListener('htmx:oobErrorNoTarget', (event) => {
    console.warn('OOB target not found:', event.detail.target);
    console.log('Content:', event.detail.content);
});
```

### Error Events

#### htmx:loadError

Fired when load handling fails:

```javascript
document.body.addEventListener('htmx:onLoadError', (event) => {
    console.error('Load error:', event.detail.exception);
});
```

#### htmx:historyCacheError

Fired when history cache save fails:

```javascript
document.body.addEventListener('htmx:historyCacheError', (event) => {
    console.error('History cache error:', event.detail.cause);
});
```

### View Transition Events

#### htmx:beforeTransition

Fired before view transition:

```javascript
document.body.addEventListener('htmx:beforeTransition', (event) => {
    // Cancel transition
    if (shouldSkipTransition()) {
        event.preventDefault();
    }
});
```

## JavaScript API

### Element Manipulation

#### htmx.find(selector, [root])

Find a single element:

```javascript
// Find in document
const div = htmx.find('#my-div');

// Find within element
const child = htmx.find(parent, '.child-class');
```

#### htmx.findAll(selector, [root])

Find all matching elements:

```javascript
// Find all divs
const divs = htmx.findAll('div');

// Find within element
const inputs = htmx.find(form, 'input');
```

#### htmx.closest(elt, selector)

Find closest ancestor:

```javascript
const row = htmx.closest(cell, 'tr');
const form = htmx.closest(input, 'form');
```

### Class Manipulation

#### htmx.addClass(elt, className, [delay])

Add class to element:

```javascript
// Immediate
htmx.addClass(element, 'active');

// With delay
htmx.addClass(element, 'fade-in', 500);
```

#### htmx.removeClass(elt, className, [delay])

Remove class from element:

```javascript
htmx.removeClass(element, 'loading');
htmx.removeClass(element, 'temp', 1000);
```

#### htmx.toggleClass(elt, className)

Toggle class on element:

```javascript
htmx.toggleClass(element, 'collapsed');
```

#### htmx.takeClass(elt, className)

Take class from siblings:

```javascript
// Remove class from siblings, add to element
htmx.takeClass(activeTab, 'active');
```

### Element Removal

#### htmx.remove(elt, [delay])

Remove element from DOM:

```javascript
// Immediate
htmx.remove(element);

// With delay
htmx.remove(toast, 3000); // Remove after 3 seconds
```

### AJAX Requests

#### htmx.ajax(verb, path, context)

Issue AJAX request programmatically:

```javascript
// Simple request
htmx.ajax('GET', '/data', '#target');

// With options
htmx.ajax('POST', '/submit', {
    target: '#result',
    values: { name: 'John', age: 30 },
    headers: { 'X-Custom': 'value' },
    swap: 'innerHTML'
});

// Returns Promise
htmx.ajax('GET', '/data', '#target')
    .then(() => console.log('Complete!'))
    .catch((err) => console.error('Error:', err));
```

**Context options:**
- `source` - Source element for attribute resolution
- `target` - Target element or selector
- `values` - Values to submit
- `headers` - Custom headers
- `swap` - Swap style
- `select` - Selector for response content
- `handler` - Callback for response HTML

### Event Handling

#### htmx.on(eventName, listener)

Add global event listener:

```javascript
const listener = htmx.on('htmx:afterRequest', (event) => {
    console.log('Request complete:', event);
});
```

#### htmx.on(target, eventName, listener)

Add event listener to element:

```javascript
const listener = htmx.on('#my-form', 'htmx:beforeRequest', (event) => {
    console.log('Form request starting');
});
```

#### htmx.off(eventName, listener)

Remove global event listener:

```javascript
htmx.off('htmx:afterRequest', listener);
```

#### htmx.off(target, eventName, listener)

Remove element event listener:

```javascript
htmx.on('#btn', 'click', handler);
htmx.off('#btn', 'click', handler);
```

#### htmx.trigger(elt, eventName, [detail])

Trigger event on element:

```javascript
// Custom event
htmx.trigger(element, 'custom-event');

// With detail
htmx.trigger(element, 'data-loaded', { data: response });

// On selector
htmx.trigger('#my-element', 'refresh');
```

### Content Processing

#### htmx.process(elt)

Process new content for htmx attributes:

```javascript
// Add HTML dynamically
document.body.innerHTML += '<div hx-get="/data">Load</div>';

// Process new content
htmx.process(document.body);

// Process specific element
htmx.process(newElement);
```

#### htmx.onLoad(callback)

Register callback for newly loaded content:

```javascript
htmx.onLoad((element) => {
    // Initialize tooltips
    if (element.querySelector('[data-tooltip]')) {
        Tooltip.init(element);
    }
    
    // Run animations
    if (element.classList.contains('animate')) {
        animateElement(element);
    }
});
```

### Swapping

#### htmx.swap(target, content, swapSpec)

Perform manual swap:

```javascript
htmx.swap('#target', '<div>New content</div>', {
    swapStyle: 'innerHTML',
    swapDelay: 100,
    settleDelay: 200
});

// With options
htmx.swap('#target', htmlContent, {
    swapStyle: 'outerHTML',
    select: '.content',
    selectOOB: '#notification'
});
```

### Value Resolution

#### htmx.values(elt, [requestType])

Get values from element:

```javascript
// Get form values
const values = htmx.values(form);
console.log(values); // { field1: 'value1', field2: 'value2' }

// Specify request type
const postValues = htmx.values(button, 'post');
const getValues = htmx.values(link, 'get');
```

### Utility Functions

#### htmx.parseInterval(string)

Parse interval string:

```javascript
const ms = htmx.parseInterval('2s');    // 2000
const ms2 = htmx.parseInterval('500ms'); // 500
```

#### htmx.closest(elt, selector)

Find closest matching ancestor:

```javascript
const row = htmx.closest(cell, 'tr');
const card = htmx.closest(title, '.card');
```

## Configuration

### htmx.config

Global configuration object:

```javascript
// History configuration
htmx.config.historyEnabled = true;
htmx.config.historyCacheSize = 20;
htmx.config.refreshOnHistoryMiss = false;

// Swap configuration
htmx.config.defaultSwapStyle = 'innerHTML';
htmx.config.defaultSwapDelay = 0;
htmx.config.defaultSettleDelay = 20;

// Request configuration
htmx.config.timeout = 0; // ms (0 = disabled)
htmx.config.withCredentials = false;
htmx.config.selfRequestsOnly = true;

// Indicator configuration
htmx.config.includeIndicatorStyles = true;
htmx.config.indicatorClass = 'htmx-indicator';
htmx.config.requestClass = 'htmx-request';
htmx.config.addedClass = 'htmx-added';
htmx.config.settlingClass = 'htmx-settling';
htmx.config.swappingClass = 'htmx-swapping';

// Security configuration
htmx.config.allowEval = true;
htmx.config.allowScriptTags = true;
htmx.config.inlineScriptNonce = '';
htmx.config.inlineStyleNonce = '';

// WebSocket configuration
htmx.config.wsReconnectDelay = 'full-jitter';
htmx.config.wsBinaryType = 'blob';

// Scroll configuration
htmx.config.scrollBehavior = 'instant'; // 'instant', 'smooth', 'auto'
htmx.config.defaultFocusScroll = false;
htmx.config.scrollIntoViewOnBoost = true;

// View transitions
htmx.config.globalViewTransitions = false;

// Response handling
htmx.config.responseHandling = [
    { code: '204', swap: 'none' },
    { code: '301-399', swap: 'none', error: true }
];

// Other options
htmx.config.disableSelector = '[hx-disable], [data-hx-disable]';
htmx.config.disableInheritance = false;
htmx.config.getCacheBusterParam = false;
htmx.config.ignoreTitle = false;
htmx.config.allowNestedOobSwaps = true;
htmx.config.historyRestoreAsHxRequest = true;
htmx.config.reportValidityOfForms = false;
```

### Custom Logger

```javascript
htmx.logger = function(elt, eventName, detail) {
    console.log(`[${eventName}]`, elt, detail);
};

// Enable logging
htmx.logAll();

// Disable logging
htmx.logNone();
```

## Extension API

### Define Extension

```javascript
htmx.defineExtension('my-extension', {
    
    // Called for every event
    onEvent: function(eventName, eventDetail) {
        console.log(eventName, eventDetail);
    },
    
    // Get value from attribute
    getValue: function(event, rootElt, attrName, selector) {
        return 'custom-value';
    },
    
    // Check if attribute is inline source
    isInlineSourceAttr: function(attrName) {
        return attrName === 'my-inline-attr';
    }
});
```

### Remove Extension

```javascript
htmx.removeExtension('my-extension');
```

## Abort Requests

### htmx:abort Event

Trigger to abort in-flight request:

```html
<button id="send" hx-post="/api">Send</button>
<button id="cancel">Cancel</button>

<script>
document.getElementById('cancel').addEventListener('click', () => {
    htmx.trigger(document.getElementById('send'), 'htmx:abort');
});
</script>
```

## Next Steps

- [Server Responses](09-server-responses.md) - Response headers and status codes
- [Common Patterns](10-common-patterns.md) - Real-world examples
- [Security Best Practices](12-security-best-practices.md) - Security guidance
