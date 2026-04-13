# htmx Core Concepts

This reference covers the fundamental concepts, architecture, and principles of htmx 2.x.

## What is htmx?

htmx is a JavaScript library that allows you to access modern browser features directly from HTML, without writing JavaScript. It extends HTML with attributes that enable:

- AJAX requests from any element (not just forms and links)
- WebSocket and Server-Sent Events connections
- Custom event handling
- DOM manipulation via server responses
- Client-side templating and validation

## Core Philosophy

### HTML as the Primary Interface

htmx treats HTML as a hypertext, where behavior is defined alongside structure:

```html
<!-- Traditional approach: HTML + separate JavaScript -->
<a href="/blog">Blog</a>
<script>
  document.querySelector('a').addEventListener('click', (e) => {
    e.preventDefault();
    fetch('/blog').then(r => r.text()).then(html => {
      document.getElementById('content').innerHTML = html;
    });
  });
</script>

<!-- htmx approach: behavior in HTML -->
<a hx-get="/blog" hx-target="#content">Blog</a>
```

### Locality of Behavior

Behavior is defined where it's used, not in separate JavaScript files:

```html
<!-- Behavior lives with the element -->
<button hx-post="/like" 
        hx-confirm="Do you like this?"
        hx-target="#counter"
        hx-swap="innerHTML">
    Like
</button>
```

### Progressive Enhancement

htmx applications work without JavaScript and enhance progressively:

```html
<!-- Works without JS (form submits normally) -->
<!-- Enhances with JS (AJAX submission) -->
<form action="/submit" method="post" 
      hx-post="/submit" 
      hx-target="#result"
      hx-swap="outerHTML">
    <input name="message" required>
    <button type="submit">Send</button>
</form>
```

## Architecture

### Request-Response Cycle

1. **Trigger**: An event occurs (click, change, custom event)
2. **Request**: htmx collects values and sends HTTP request
3. **Response**: Server returns HTML fragment
4. **Swap**: Response is inserted into DOM using specified swap mode
5. **Settle**: Attributes are settled and events fired

```
┌─────────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐     ┌────────┐
│   Trigger   │ ──> │ Request  │ ──> │ Server  │ ──> │  Swap    │ ──> │Settle  │
│  (click)    │     │ (POST)   │     │ (HTML)  │     │(innerHTML)│     │(events)│
└─────────────┘     └──────────┘     └─────────┘     └──────────┘     └────────┘
```

### Value Resolution

htmx collects form values in a specific order:

1. Element's own values (if it has them)
2. Values from `hx-include` elements
3. Values from the closest enclosing form
4. Values overridden by `hx-vals` or `hx-vars`

```html
<form id="main-form">
    <input name="user_id" value="123">
    
    <button hx-post="/comment" 
            hx-vals='{"post_id": 456}'>
        Comment
    </button>
    <!-- Sends: user_id=123, post_id=456 -->
</form>
```

### Attribute Inheritance

Child elements inherit `hx-*` attributes from parents unless overridden:

```html
<div hx-post="/api" hx-target="#results">
    <button>Post 1</button>      <!-- Uses inherited attributes -->
    <button hx-post="/other">    <!-- Overrides post URL -->
        Post 2
    </button>
</div>

<!-- Explicitly disable inheritance -->
<div hx-post="/api" hx-disinherit="hx-target">
    <button>No target inherited</button>
</div>
```

## Key Attributes Overview

### HTTP Method Attributes

These trigger requests when the element is activated:

| Attribute | Method | Description |
|-----------|--------|-------------|
| `hx-get` | GET | Retrieve resource |
| `hx-post` | POST | Create resource |
| `hx-put` | PUT | Replace resource |
| `hx-patch` | PATCH | Partial update |
| `hx-delete` | DELETE | Remove resource |

```html
<!-- All trigger on natural event (click for button) -->
<button hx-get="/data">Load</button>
<button hx-post="/save">Save</button>
<button hx-put="/update">Update</button>
<button hx-patch="/modify">Modify</button>
<button hx-delete="/remove">Remove</button>
```

### Control Attributes

These modify request behavior:

| Attribute | Purpose |
|-----------|---------|
| `hx-trigger` | When to trigger the request |
| `hx-target` | Where to put the response |
| `hx-swap` | How to insert the response |
| `hx-sync` | Request synchronization |
| `hx-vals` | Additional values to send |
| `hx-vars` | Dynamic values from JavaScript |
| `hx-include` | Elements to include in values |
| `hx-exclude` | Elements to exclude from values |
| `hx-select` | Select specific content from response |
| `hx-confirm` | Confirmation dialog before request |
| `hx-prompt` | Prompt user for input |

### Extended Attributes

These provide additional functionality:

| Attribute | Purpose |
|-----------|---------|
| `hx-push-url` | Push URL to browser history |
| `hx-replace-url` | Replace current URL |
| `hx-headers` | Add custom headers |
| `hx-http-headers` | Alias for hx-headers |
| `hx-vars` | JavaScript expression values |
| `hx-indicator` | Loading indicator element |
| `hx-disabled-elt` | Elements to disable during request |
| `hx-request` | Request configuration |
| `hx-validate` | Force/disable validation |
| `hx-on::*` | Event handlers |

## Configuration

### Meta Tag Configuration

Configure htmx globally using meta tags:

```html
<head>
    <!-- Set default swap style -->
    <meta name="htmx-config" content='{"defaultSwapStyle": "outerHTML"}'>
    
    <!-- Enable history cache -->
    <meta name="htmx-history-cache-size" content="20">
    
    <!-- Disable eval for CSP compliance -->
    <meta name="htmx-allow-eval" content="false">
    
    <!-- Set request timeout -->
    <meta name="htmx-timeout" content="10000">
</head>
```

### JavaScript Configuration

Configure via `htmx.config`:

```javascript
// Update history cache size
htmx.config.historyCacheSize = 30;

// Disable history
htmx.config.historyEnabled = false;

// Set default swap delay
htmx.config.defaultSwapDelay = 100;

// Configure request timeout
htmx.config.timeout = 5000;

// Enable view transitions globally
htmx.config.globalViewTransitions = true;

// Disable script tag evaluation (CSP)
htmx.config.allowScriptTags = false;

// Set custom indicators class
htmx.config.indicatorClass = 'loading';

// Configure response handling
htmx.config.responseHandling = [
    { code: '204', swap: 'none' },
    { code: '301-399', swap: 'none', error: true }
];
```

### Available Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `defaultSwapStyle` | string | `'innerHTML'` | Default swap method |
| `defaultSwapDelay` | number | `0` | Delay before swapping (ms) |
| `defaultSettleDelay` | number | `20` | Delay after swapping (ms) |
| `historyCacheSize` | number | `10` | Pages to cache for history |
| `historyEnabled` | boolean | `true` | Enable browser history |
| `timeout` | number | `0` | Request timeout (ms, 0=disabled) |
| `allowEval` | boolean | `true` | Allow eval-like functionality |
| `allowScriptTags` | boolean | `true` | Evaluate script tags |
| `withCredentials` | boolean | `false` | Include cookies in requests |
| `includeIndicatorStyles` | boolean | `true` | Inject indicator CSS |
| `indicatorClass` | string | `'htmx-indicator'` | Loading indicator class |
| `requestClass` | string | `'htmx-request'` | Class during request |
| `addedClass` | string | `'htmx-added'` | Class for new elements |
| `settlingClass` | string | `'htmx-settling'` | Class during settling |
| `swappingClass` | string | `'htmx-swapping'` | Class during swapping |
| `refreshOnHistoryMiss` | boolean | `false` | Refresh on history miss |
| `scrollBehavior` | string | `'instant'` | Scroll animation behavior |
| `globalViewTransitions` | boolean | `false` | Enable view transitions |
| `selfRequestsOnly` | boolean | `true` | Only same-domain requests |
| `ignoreTitle` | boolean | `false` | Ignore title tags in response |

## Data Attributes Prefix

All htmx attributes can use the `data-` prefix for HTML validation:

```html
<!-- Both are equivalent -->
<button hx-post="/save">Save</button>
<button data-hx-post="/save">Save</button>
```

The `data-` prefix is required when using strict HTML validators or when htmx attributes conflict with other libraries.

## Browser Support

htmx 2.x supports modern browsers:

- Chrome/Edge 60+
- Firefox 60+
- Safari 11+
- Opera 47+

For IE11 support, use [htmx 1.x](https://v1.htmx.org).

## Performance Considerations

### Minimal Bundle Size

htmx is ~15KB minified and gzipped, with no dependencies.

### No Build Step Required

Use directly from CDN or include as a static file:

```html
<script src="htmx.min.js"></script>
```

### Efficient DOM Updates

htmx uses efficient DOM manipulation:

- Direct innerHTML replacement (fastest)
- DocumentFragment for multiple elements
- Minimal reflows and repaints

### Caching

htmx caches history in localStorage:

```javascript
// Configure cache size
htmx.config.historyCacheSize = 20;

// Cache is automatically managed
// No manual intervention needed
```

## Security Considerations

### CSRF Protection

htmx sends standard form requests, so existing CSRF protection works:

```html
<!-- Include CSRF token in forms -->
<form hx-post="/submit">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <button type="submit">Submit</button>
</form>
```

### Content Security Policy

Configure htmx for CSP compliance:

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'nonce-{{ nonce }}'">

<!-- Disable eval and configure nonce -->
<script>
    htmx.config.allowEval = false;
    htmx.config.inlineScriptNonce = '{{ nonce }}';
    htmx.config.inlineStyleNonce = '{{ nonce }}';
</script>
```

### Same-Origin Requests

By default, htmx only allows same-origin requests:

```javascript
// Enable cross-origin if needed (use with caution)
htmx.config.selfRequestsOnly = false;
```

See [Security Best Practices](12-security-best-practices.md) for comprehensive security guidance.

## Next Steps

- [Request Attributes Reference](02-request-attributes.md) - All HTTP method attributes
- [Triggers and Events](03-triggers-and-events.md) - Complete trigger system guide
- [Swapping](04-swapping.md) - DOM swap modes and options
- [Common Patterns](10-common-patterns.md) - Real-world usage examples
