# Extensions Guide

## Overview

htmx 4 ships with 9 core extensions that add specialized functionality. Extensions are loaded by including their script files after htmx.

## Loading Extensions

### Basic Loading

```html
<!-- Load htmx first -->
<script src="/path/to/htmx.min.js"></script>

<!-- Then load extensions -->
<script src="/path/to/ext/sse.js"></script>
<script src="/path/to/ext/ws.js"></script>
<script src="/path/to/ext/preload.js"></script>
```

Extensions are automatically registered when loaded. No additional configuration needed.

### Restricting Extensions

Limit which extensions can load:

```html
<meta name="htmx-config" content='{"extensions": "sse, ws, preload"}'>
<script src="/htmx.min.js"></script>
```

Or via JavaScript:

```javascript
htmx.config.extensions = 'sse,ws,preload';
```

### Using htmax Bundle

The `htmax.js` file bundles htmx with popular extensions:

```html
<script src="/path/to/htmax.min.js"></script>
```

Includes: SSE, WebSocket, preload, browser-indicator, download, optimistic, targets

## Core Extensions

### alpine-compat

Initializes Alpine.js on fragments before swap, ensuring Alpine components work correctly with htmx.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/alpine-compat.js"></script>
<script src="/alpine.js"></script>

<div hx-get="/component" hx-swap="innerHTML">
  <!-- Alpine components in response will initialize correctly -->
</div>
```

**Use case:** Integrating htmx with Alpine.js for reactive UI components.

### browser-indicator

Shows the browser's native loading indicator during requests instead of custom spinners.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/browser-indicator.js"></script>

<!-- Automatically shows native loading indicator -->
<button hx-post="/slow-action">Submit</button>
```

**Configuration:**
```javascript
htmx.config.browserIndicatorClass = 'loading';
```

**Use case:** Simple loading feedback without custom CSS/HTML.

### download

Triggers file downloads from htmx requests.

**Usage:**
```html
<!-- Download file when clicked -->
<a hx-get="/api/download/report.pdf" 
   hx-download="report.pdf"
   download="report.pdf">
  Download Report
</a>

<!-- Dynamic filename -->
<button hx-post="/generate" 
        hx-download='js:"report-" + Date.now() + ".pdf"'>
  Generate & Download
</button>
```

**Attributes:**
- `hx-download`: Filename for download
- `download`: Native HTML5 download attribute (recommended)

**Use case:** File generation, exports, and downloads without page navigation.

### head-support

Merges `<head>` tag information (styles, scripts, meta tags) from htmx responses into the current page.

**Usage:**
```html
<head>
  <script src="/htmx.min.js"></script>
  <script src="/ext/head-support.js"></script>
</head>

<body>
  <div hx-get="/page-with-styles">Load Page</div>
</body>
```

**Server response:**
```html
<head>
  <title>New Title</title>
  <link rel="stylesheet" href="/new-style.css">
  <meta name="description" content="New description">
</head>
<div>Page content</div>
```

**Configuration:**
```javascript
// How to handle different head elements
htmx.config.headScripts = 'replace';  // or 'append', 'true'
htmx.config.headStyles = 'merge';     // or 'replace', 'true'
htmx.config.headTitles = 'true';      // or 'false'
htmx.config.headOthers = 'merge';     // or 'replace', 'true'
```

**Use case:** Partial page loads that need to update styles, scripts, or metadata.

### htmx-2-compat

Restores htmx 2.x behavior for easier migration.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/htmx-2-compat.js"></script>
```

**Restores:**
- Implicit attribute inheritance
- Old event names (e.g., `htmx:beforeRequest`)
- Previous error-swapping defaults (no swap on 4xx/5xx)
- Removed configuration options

**Migration strategy:**
1. Load htmx-2-compat extension initially
2. Gradually update to htmx 4 syntax
3. Remove extension when migration complete

**Use case:** Simplifying migration from htmx 2.x to 4.0.

### optimistic

Shows expected content from a template before server responds, then updates with actual response.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/optimistic.js"></script>

<!-- Show optimistic UI immediately -->
<form hx-post="/add-item" 
      hx-ext="optimistic"
      hx-optimistic="<div class='item'>New Item...</div>">
  <input name="item">
  <button type="submit">Add</button>
</form>
```

**Configuration:**
```javascript
// Custom optimistic template
htmx.config.optimisticPrefix = 'opt_';
```

**Use case:** Form submissions where you can predict the result (e.g., adding list items).

### preload

Triggers requests early (on mouseover/mousedown) for near-instant page loads.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/preload.js"></script>

<!-- Preload on mouseover -->
<a hx-get="/expensive-page" 
   hx-ext="preload"
   hx-trigger="mouseover from:body">
  Load Expensive Page
</a>
```

**Configuration:**
```javascript
// Customize preload behavior
htmx.config.preloadAfter = 50;  // milliseconds before navigation
htmx.config.preloadLinks = true;  // Auto-preload all links
```

**Migration from htmx 2:**
```html
<!-- htmx 2 -->
<a hx-get="/page" hx-ext="preload">Link</a>

<!-- htmx 4 (more explicit) -->
<a hx-get="/page" hx-ext="preload" hx-trigger="mouseover from:body">Link</a>
```

**Use case:** Navigation links to heavy pages, improving perceived performance.

### sse (Server-Sent Events)

Provides server-to-client streaming via SSE protocol. See [Real-time Communication](05-realtime.md#server-sent-events-sse) for detailed usage.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/sse.js"></script>

<div hx-sse:connect="/events/stream">
  <div id="updates" hx-sse:swap="update"></div>
</div>
```

**Use case:** Notifications, live updates, real-time feeds.

### upsert

Updates existing elements by ID and inserts new ones, preserving unmatched elements.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/upsert.js"></script>

<div hx-get="/items" 
     hx-swap="upsert:#container">
  Load Items
</div>
```

**Server response:**
```html
<!-- Elements with IDs are updated, others inserted -->
<div id="item-1">Updated Item 1</div>
<div id="item-2">Updated Item 2</div>
<div>New Item (inserted)</div>
```

**Swap styles:**
- `upsert:selector`: Upsert into selector
- `outerUpsert:selector`: Outer upsert into selector

**Use case:** List updates where some items change and others are added.

### ws (WebSocket)

Provides bidirectional WebSocket communication. See [Real-time Communication](05-realtime.md#websockets) for detailed usage.

**Usage:**
```html
<script src="/htmx.min.js"></script>
<script src="/ext/ws.js"></script>

<div hx-ws:connect="ws://example.com/socket">
  <div id="chat" hx-trigger="ws:message"></div>
  <form hx-post="" hx-ws:send="message">
    <input name="text">
    <button type="submit">Send</button>
  </form>
</div>
```

**Use case:** Chat, collaborative editing, real-time gaming.

## Third-Party Extensions

htmx has a rich ecosystem of community extensions:

### Popular Extensions

- **htmx-debug**: Enhanced debugging and logging
- **htmx-cors**: CORS preflight handling
- **htmx-multi-use**: Reuse responses multiple times
- **htmx-ls-cache**: LocalStorage caching
- **htmx-rest-json**: RESTful JSON handling
- **htmx-accordion**: Accordion UI component
- **htmx-pagination**: Pagination helpers

Find more at: https://github.com/htmx-org/htmx-extensions

## Developing Custom Extensions

### Extension API

Extensions implement a method map:

```javascript
htmx.registerExtension('my-extension', {
  // Called when extension is initialized
  init: function(api) {
    console.log('Extension initialized');
    return {};
  },
  
  // Called for each element with hx-ext="my-extension"
  onEvent: function(eventName, event) {
    if (eventName === 'htmx:beforeRequest') {
      // Modify request
      const elt = event.target;
      const config = event.detail.requestConfig;
      
      // Add custom header
      config.headers['X-Custom'] = 'value';
    }
  },
  
  // Get value from attribute
  getValue: function(elt, attributeName, defaultValue) {
    return elt.getAttribute(attributeName) || defaultValue;
  }
});
```

### Extension Lifecycle Events

Extensions can listen to all htmx events:

| Event | Description |
|-------|-------------|
| `htmx:beforeRequest` | Before request starts |
| `htmx:configRequest` | During request configuration |
| `htmx:beforeSend` | Before request sent |
| `htmx:beforeSwap` | Before content swapped |
| `htmx:afterSwap` | After content swapped |
| `htmx:afterSettle` | After settle phase |

### Example: Custom Header Extension

```javascript
htmx.registerExtension('auth-header', {
  init: function(api) {
    return {};
  },
  
  onEvent: function(eventName, event) {
    if (eventName === 'htmx:configRequest') {
      const config = event.detail.requestConfig;
      
      // Add auth token from localStorage
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
  }
});
```

**Usage:**
```html
<div hx-get="/api/protected" hx-ext="auth-header">
  Load Protected Data
</div>
```

### Example: Request Caching Extension

```javascript
htmx.registerExtension('cache', {
  init: function(api) {
    const cache = new Map();
    
    return {
      cacheGet: function(key) {
        const item = cache.get(key);
        if (item && Date.now() - item.timestamp < 60000) {
          return item.value;
        }
        cache.delete(key);
        return null;
      },
      
      cacheSet: function(key, value) {
        cache.set(key, { value, timestamp: Date.now() });
      }
    };
  },
  
  onEvent: function(eventName, event, info) {
    if (eventName === 'htmx:beforeRequest') {
      const elt = event.target;
      const url = elt.getAttribute('hx-get');
      
      if (!url) return;
      
      // Check cache
      const cached = info.extensionState.cacheGet(url);
      if (cached) {
        event.preventDefault();
        htmx.swap(elt, cached, 'innerHTML');
      }
    } else if (eventName === 'htmx:afterRequest') {
      const elt = event.target;
      const url = elt.getAttribute('hx-get');
      
      if (!url || !event.detail.success) return;
      
      // Cache response
      info.extensionState.cacheSet(url, event.detail.xhr.response);
    }
  }
});
```

**Usage:**
```html
<div hx-get="/api/expensive" hx-ext="cache">
  Load Cached Data
</div>
```

## Extension Best Practices

### Naming Conventions

- Use hyphenated names: `my-extension` not `myExtension`
- Prefix with domain if needed: `acme-auth`
- Avoid conflicts with core extensions

### Error Handling

```javascript
htmx.registerExtension('safe-extension', {
  onEvent: function(eventName, event) {
    try {
      // Extension logic
    } catch (error) {
      console.error('Extension error:', error);
      // Don't break htmx functionality
    }
  }
});
```

### State Management

```javascript
htmx.registerExtension('stateful-extension', {
  init: function(api) {
    // Return extension state (preserved across requests)
    return {
      count: 0,
      lastUpdate: null
    };
  },
  
  onEvent: function(eventName, event, info) {
    // Access state via info.extensionState
    info.extensionState.count++;
  }
});
```

### Testing Extensions

```javascript
// Unit test extension
describe('my-extension', () => {
  it('should add custom header', () => {
    const events = [];
    
    htmx.on('htmx:configRequest', (e) => events.push(e));
    
    // Trigger request with extension
    const elt = document.createElement('button');
    elt.setAttribute('hx-post', '/test');
    elt.setAttribute('hx-ext', 'my-extension');
    document.body.appendChild(elt);
    
    htmx.trigger(elt, 'click');
    
    const event = events[0];
    expect(event.detail.requestConfig.headers['X-Custom']).toBe('value');
  });
});
```

## Debugging Extensions

### Enable Logging

```javascript
htmx.config.logAll = true;
```

### Extension Event Monitoring

```javascript
// Monitor all extension events
document.body.addEventListener('htmx:beforeRequest', (evt) => {
  console.log('Request:', evt.target.getAttribute('hx-ext'));
});

// Check extension state
const extensions = htmx.getExtensions();
console.log('Loaded extensions:', extensions);
```

### Browser DevTools

- Check Console for extension logs
- Monitor Network tab for modified requests
- Use breakpoints in extension code
