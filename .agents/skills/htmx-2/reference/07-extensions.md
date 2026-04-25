# htmx Extensions Guide

This reference covers built-in and community extensions for extending htmx functionality.

## Extension Basics

### Loading Extensions

Load extensions via script tags:

```html
<!-- Load htmx first -->
<script src="https://unpkg.com/htmx.org/dist/htmx.min.js"></script>

<!-- Load extensions -->
<script src="https://unpkg.com/htmx.org/dist/ext/ws.js"></script>
<script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>
<script src="https://unpkg.com/htmx.org/dist/ext/json-enc.js"></script>

<!-- Use extension on element -->
<div hx-ext="ws,sse,json-enc"
     hx-ws="connect:/socket">
    Content
</div>
```

### Enabling Extensions

Use `hx-ext` attribute to enable extensions:

```html
<!-- Single extension -->
<div hx-ext="json-enc"
     hx-post="/api">
    Submit JSON
</div>

<!-- Multiple extensions (comma-separated) -->
<div hx-ext="ws,idiomorph"
     hx-ws="connect:/ws"
     hx-swap="morph">
    Real-time with morphing
</div>

<!-- Disable inherited extension -->
<div hx-ext="json-enc"
     hx-disinherit="hx-ext">
    <button>No JSON encoding here</button>
</div>
```

## Core Extensions

### head-support

Merge `<head>` tag information from responses.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/head.js"></script>

<!-- Use head merge -->
<div hx-ext="head"
     hx-get="/page"
     hx-swap="innerHTML head:merge">
    Content
</div>
```

**Head swap modes:**
- `merge` - Merge new head tags with existing (default)
- `append` - Append new head tags
- `false` - Don't process head tags

**Server response:**
```html
<head>
    <title>New Title</title>
    <style>.new-class { color: red; }</style>
    <link rel="stylesheet" href="new.css">
</head>
<div>New content</div>
```

### idiomorph

Morphing swap strategy that preserves DOM state.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/idiomorph.js"></script>

<!-- Use morph swap -->
<div hx-ext="idiomorph"
     hx-get="/content"
     hx-swap="morph">
    
    <!-- Input focus preserved -->
    <input name="data" value="existing">
    
    <!-- Video state preserved -->
    <video src="movie.mp4" controls></video>
</div>
```

**Benefits:**
- Preserves input focus
- Maintains video/audio playback
- Keeps third-party widget state
- Smooth DOM transitions

**Morph options:**
```html
<!-- Specific morph configuration -->
<div hx-ext="idiomorph"
     hx-swap="morph:innerHTML,children">
    Content
</div>
```

### preload

Preload HTML fragments into browser cache.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/preload.js"></script>

<!-- Preload on hover -->
<a href="/article/123" 
   hx-get="/article/123"
   hx-ext="preload"
   hx-trigger="hover 1s">
    Read Article
</a>

<!-- Preload on reveal -->
<div hx-get="/lazy-section"
     hx-ext="preload"
     hx-trigger="revealed"
     hx-swap="outerHTML">
    Preview
</div>
```

**Preload strategies:**
- `hover Xs` - Preload after X seconds of hover
- `reveal` - Preload when element scrolls into view
- Manual preload via JavaScript

### response-targets

Swap different targets based on HTTP response codes.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/response-targets.js"></script>

<!-- Different targets for different status codes -->
<div hx-ext="response-targets"
     hx-post="/api/action"
     hx-target="#content"
     hx-target-400="#error-message"
     hx-target-401="#login-form"
     hx-target-500="#server-error">
    Submit Action
</div>

<div id="content"></div>
<div id="error-message" class="error"></div>
<div id="login-form" style="display:none"></div>
<div id="server-error" class="error"></div>
```

**Supported status codes:**
- Any HTTP status code (200, 201, 400, 401, 403, 404, 500, etc.)

### sse (Server-Sent Events)

One-way server-to-client streaming.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>

<!-- Connect to SSE stream -->
<div hx-sse-connect="/events">
    
    <!-- Trigger on specific event -->
    <div hx-trigger="sse:new_message"
         hx-swap="beforeend">
        Messages
    </div>
</div>
```

See [WebSockets and SSE](06-websockets-sse.md) for detailed SSE documentation.

### ws (WebSocket)

Bidirectional real-time communication.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/ws.js"></script>

<!-- Connect to WebSocket -->
<div hx-ws="connect:/ws">
    
    <!-- Send message -->
    <form hx-ws="send">
        <input name="text">
        <button type="submit">Send</button>
    </form>
    
    <!-- Receive messages -->
    <div hx-trigger="ws-message"
         hx-swap="beforeend">
        Chat
    </div>
</div>
```

See [WebSockets and SSE](06-websockets-sse.md) for detailed WebSocket documentation.

### htmx-1-compat

Roll back htmx 2.x behavior changes to htmx 1.x defaults.

```html
<!-- Load compatibility extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/htmx-1-compat.js"></script>

<!-- Apply to entire page -->
<body hx-ext="htmx-1-compat">
    <!-- htmx 1.x behavior here -->
</body>
```

**Use when:** Migrating from htmx 1.x and need gradual transition.

### json-enc

Encode request parameters as JSON.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/json-enc.js"></script>

<!-- Send JSON instead of form data -->
<div hx-ext="json-enc"
     hx-post="/api/users"
     hx-vals='{"name": "John", "age": 30, "active": true}'>
    Create User
</div>
```

**Request body:**
```json
{
  "name": "John",
  "age": 30,
  "active": true
}
```

**Headers automatically set:**
- `Content-Type: application/json`

## Community Extensions

### class-tools

Swap CSS classes on elements.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/class-tools.js"></script>

<!-- Add/remove classes -->
<div hx-ext="class-tools"
     hx-get="/toggle-theme"
     classes="add:dark-mode remove:light-mode">
    Toggle Theme
</div>
```

### morphdom-swap

Alternative morphing using morphdom library.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/morphdom-swap.js"></script>

<!-- Use morphdom swap -->
<div hx-ext="morphdom-swap"
     hx-get="/content"
     hx-swap="morphdom">
    Content
</div>
```

### alpine-morph

Morphing for Alpine.js applications.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/alpine-morph.js"></script>

<!-- Preserve Alpine state -->
<div hx-ext="alpine-morph"
     hx-get="/content"
     hx-swap="alpine-morph"
     x-data="{ count: 0 }">
    <button @click="count++">{{ count }}</button>
</div>
```

### client-side-templates

Transform JSON responses to HTML using templates.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/client-side-templates.js"></script>

<!-- Template definition -->
<template id="user-template">
    <div class="user">
        <h3>{{name}}</h3>
        <p>{{email}}</p>
    </div>
</template>

<!-- Use template -->
<div hx-ext="client-side-templates"
     hx-get="/api/user/123"
     hx-trigger="load"
     data-template="user-template">
    Loading...
</div>
```

### loading-states

Manage loading states during requests.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/loading-states.js"></script>

<!-- Define loading state -->
<button hx-post="/submit"
        hx-ext="loading-states"
        loading-class="btn-loading"
        loading-text="Submitting..."
        disabled-while-loading="true">
    Submit
</button>
```

### path-deps

Express element dependencies based on paths.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/path-deps.js"></script>

<!-- Dependent request -->
<div hx-get="/comments"
     hx-ext="path-deps"
     path-deps="#post-selector">
    Comments
</div>

<!-- Parent that sets dependency -->
<select id="post-selector" 
        hx-get="/posts"
        hx-target="#posts">
    <option value="1">Post 1</option>
    <option value="2">Post 2</option>
</select>
```

### remove-me

Remove elements after a delay.

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/remove-me.js"></script>

<!-- Remove after 3 seconds -->
<div hx-ext="remove-me"
     remove-me="3s"
     class="toast">
    Action completed!
</div>
```

## Building Custom Extensions

### Extension API

Create custom extensions using `htmx.defineExtension()`:

```javascript
htmx.defineExtension('my-extension', {
    
    // Called when element is initialized
    onEvent: function(name, event) {
        if (name === 'htmx:beforeRequest') {
            console.log('Request about to start:', event);
        }
    },
    
    // Get value for attribute
    getValue: function(evt, rootElt, attrName, selector) {
        // Return custom value
    }
});
```

### Extension Lifecycle

```javascript
htmx.defineExtension('debug', {
    
    // Called for every htmx event
    onEvent: function(eventName, eventDetail) {
        console.log(`[${eventName}]`, eventDetail);
        
        // Available events:
        // - htmx:beforeRequest
        // - htmx:afterRequest
        // - htmx:beforeSwap
        // - htmx:afterSwap
        // - htmx:beforeSend
        // - etc.
    },
    
    // Modify request configuration
    isInlineSourceAttr: function(attrName) {
        return attrName === 'my-inline-attr';
    }
});
```

### Example: Analytics Extension

```javascript
htmx.defineExtension('analytics', {
    onEvent: function(eventName, event) {
        if (eventName === 'htmx:beforeRequest') {
            // Track outgoing request
            analytics.track('htmx_request', {
                verb: event.detail.requestConfig.verb,
                path: event.detail.requestConfig.path,
                element: event.detail.elt.tagName
            });
        } else if (eventName === 'htmx:afterRequest') {
            // Track request result
            analytics.track('htmx_request_result', {
                success: event.detail.successful,
                status: event.detail.xhr.status,
                duration: event.detail.requestConfig.duration
            });
        }
    }
});

// Use extension
<div hx-ext="analytics"
     hx-get="/data">
    Track This
</div>
```

## Extension Registry

### Official Extensions

Hosted at https://github.com/bigskysoftware/htmx-extensions:

- `ajax-header` - Add X-Requested-With header
- `alpine-morph` - Alpine.js morphing
- `class-tools` - Class manipulation
- `client-side-templates` - JSON to HTML templates
- `debug` - Debug logging
- `event-header` - Include triggering event in headers
- `form-json` - JSON form encoding with type preservation
- `head-support` - Head tag merging
- `htmx-1-compat` - htmx 1.x compatibility
- `idiomorph` - DOM morphing
- `json-enc` - JSON request encoding
- `loading-states` - Loading state management
- `morphdom-swap` - morphdom-based swapping
- `multi-swap` - Multiple element swaps
- `no-cache` - Bypass caching
- `path-deps` - Path dependencies
- `path-params` - Path parameter substitution
- `preload` - Preload content
- `remove-me` - Auto-remove elements
- `response-targets` - Response code targets
- `safe-nonce` - CSP nonce handling
- `sse` - Server-Sent Events
- `ws` - WebSockets

### Finding Extensions

Search for community extensions:
- GitHub: https://github.com/topics/htmx-extension
- htmx Website: https://htmx.org/extensions/
- npm: https://www.npmjs.com/search?q=htmx

## Troubleshooting

### Extension Not Loading

**Check:**
1. Load order: htmx → extensions → your code
2. Script paths are correct
3. No JavaScript errors in console

```html
<!-- Correct load order -->
<script src="htmx.min.js"></script>
<script src="ext/ws.js"></script>
<script src="ext/sse.js"></script>
<!-- Your HTML with hx-ext attributes -->
```

### Extension Not Working

**Verify:**
1. `hx-ext` attribute includes extension name
2. Extension is loaded before element is processed
3. Required attributes are present

```javascript
// Debug extension loading
console.log(htmx.getExtensions());
```

### Conflicting Extensions

Some extensions may conflict:

```html
<!-- Use only one morph extension -->
<div hx-ext="idiomorph"  <!-- NOT both idiomorph and morphdom-swap -->
     hx-swap="morph">
    Content
</div>
```

## Next Steps

- [Events and API Reference](08-events-api.md) - Extension event hooks
- [Server Responses](09-server-responses.md) - Response handling
- [Common Patterns](10-common-patterns.md) - Extension usage patterns
