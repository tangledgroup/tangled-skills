---
name: htmx-2
description: A skill for building interactive web applications with htmx 2.x, a JavaScript library that allows accessing modern browser features directly from HTML attributes without writing JavaScript. Use when creating dynamic web interfaces, implementing AJAX requests from HTML, working with server-driven UIs, integrating WebSockets/SSE, or migrating from JavaScript-heavy frameworks to hypermedia-driven architectures.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - htmx
  - html
  - ajax
  - web-development
  - frontend
  - hypermedia
  - server-rendered
  - progressive-enhancement
category: development

external_references:
  - https://htmx.org/docs
  - https://github.com/bigskysoftware/htmx
---

# htmx-2 Skill


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for building interactive web applications with htmx 2.x, a JavaScript library that allows accessing modern browser features directly from HTML attributes without writing JavaScript. Use when creating dynamic web interfaces, implementing AJAX requests from HTML, working with server-driven UIs, integrating WebSockets/SSE, or migrating from JavaScript-heavy frameworks to hypermedia-driven architectures.

A comprehensive toolkit for building interactive web applications using **htmx 2.x**, a JavaScript library that allows you to access modern browser features directly from HTML, without writing JavaScript. Htmx enables hypermedia-driven development where HTML remains the primary interface for defining application behavior.

## When to Use

- Building dynamic web interfaces without JavaScript frameworks
- Adding interactivity to server-rendered applications
- Implementing AJAX requests, WebSocket connections, or SSE directly from HTML
- Creating progressive enhancement layers on top of traditional HTML
- Migrating from heavy JavaScript SPAs (React, Vue, Angular) to simpler architectures
- Working with modern browser features (View Transitions, Intersection Observer) from HTML
- Building real-time features with WebSockets and Server-Sent Events
- Implementing complex UI patterns (modals, tabs, live search, infinite scroll) with minimal code

## Quick Start

### Installation

Add htmx to your project via CDN (recommended for quick start):

```html
<!-- Minified production version -->
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" 
        integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz" 
        crossorigin="anonymous"></script>

<!-- Development version with source maps -->
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.08/dist/htmx.js" 
        integrity="sha384-ezjq8118wdwdRMj+nX4bevEi+cDLTbhLAeFF688VK8tPDGeLUe0WoY2MZtSla72F" 
        crossorigin="anonymous"></script>
```

Or install via npm for build systems:

```bash
npm install htmx.org@2.0.8
```

Then import in your JavaScript bundle:

```javascript
import 'htmx.org';
// Make global htmx object available (recommended)
window.htmx = require('htmx.org');
```

### Basic Usage

The core concept: any HTML element can make HTTP requests and update the DOM:

```html
<!-- Simple GET request on click -->
<button hx-get="/clicked" hx-target="#result">
    Click Me!
</button>
<div id="result"></div>

<!-- POST request with form data -->
<form hx-post="/submit" hx-target="#form-result">
    <input name="username" placeholder="Username">
    <button type="submit">Submit</button>
</form>
<div id="form-result"></div>
```

See [Core Concepts](references/01-core-concepts.md) for detailed explanation of htmx fundamentals.

## Common Operations

### AJAX Requests

Use HTTP method attributes to trigger requests:

```html
<!-- GET request -->
<a hx-get="/data" hx-target="#container">Load Data</a>

<!-- POST request -->
<button hx-post="/save" hx-vals='{"id": 123}'>Save</button>

<!-- PUT/PATCH/DELETE -->
<button hx-put="/users/123">Update User</button>
<button hx-patch="/users/123">Patch User</button>
<button hx-delete="/users/123" hx-confirm="Delete this user?">Delete</button>
```

See [Request Attributes Reference](references/02-request-attributes.md) for all HTTP method attributes.

### Triggers and Events

Control when requests fire using `hx-trigger`:

```html
<!-- Trigger on custom event -->
<div hx-get="/update" hx-trigger="mouseenter">Hover me</div>

<!-- Polling every 2 seconds -->
<div hx-get="/news" hx-trigger="every 2s">News Ticker</div>

<!-- Debounced search (500ms delay) -->
<input name="q" 
       hx-get="/search" 
       hx-trigger="keyup changed delay:500ms"
       hx-target="#results"
       placeholder="Search...">

<!-- Trigger only once -->
<div hx-get="/init" hx-trigger="load once">Initial Load</div>

<!-- Trigger when element scrolls into view -->
<div hx-get="/load-more" hx-trigger="revealed">Load More</div>
```

See [Trigger System Guide](references/03-triggers-and-events.md) for comprehensive trigger documentation.

### Swapping Content

Control how responses are inserted into the DOM:

```html
<!-- Default: replace innerHTML -->
<div hx-get="/content" id="target">Loading...</div>

<!-- Replace entire element -->
<div hx-get="/content" hx-swap="outerHTML">Loading...</div>

<!-- Append to end -->
<div hx-get="/item" hx-swap="beforeend"><ul id="list"></ul></div>

<!-- Prepend to start -->
<div hx-get="/item" hx-swap="afterbegin"><ul id="list"></ul></div>

<!-- Insert before target -->
<div hx-get="/sidebar" hx-swap="beforebegin" id="main">Content</div>

<!-- With swap delay and scrolling -->
<div hx-get="/content" 
     hx-swap="innerHTML swap:100ms settle:200ms scroll:top">
    Loading...
</div>
```

See [Swapping and DOM Updates](references/04-swapping.md) for all swap modes and options.

### Out-of-Band Swaps

Update multiple elements from a single response:

```html
<!-- In your HTML -->
<div id="message-area"></div>
<div id="content">
    <button hx-post="/submit">Submit</button>
</div>

<!-- Server returns -->
<div id="message-area" hx-swap-oob="true">Success!</div>
<div>New content for main area</div>
```

See [Out-of-Band Swaps Guide](references/05-oob-swaps.md) for OOB swap patterns.

### WebSockets and SSE

Real-time communication without JavaScript:

```html
<!-- WebSocket connection -->
<div hx-ws="connect:/ws"
     hx-trigger="every 3s"
     hx-get="/messages"
     hx-target="#chat">
    Chat messages appear here
</div>

<!-- Server-Sent Events -->
<div hx-sse-connect="/events"
     hx-trigger="message from:/events"
     hx-get="/process-event"
     hx-target="#updates">
    Real-time updates
</div>
```

See [Real-Time Communication](references/06-websockets-sse.md) for WebSocket/SSE patterns.

### Extensions

Extend htmx functionality:

```html
<!-- Load extensions -->
<script src="https://unpkg.com/htmx.org/dist/ext/ws.js"></script>
<script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>
<script src="https://unpkg.com/htmx.org/dist/ext/json-enc.js"></script>

<!-- Use extension on element -->
<div hx-ext="json-enc"
     hx-post="/api"
     hx-vals='{"name": "John", "age": 30}'>
    Submit JSON
</div>

<!-- Multiple extensions -->
<div hx-ext="ws,sse,idiomorph"
     hx-ws="connect:/socket">
    Real-time with morphing
</div>
```

See [Extensions Guide](references/07-extensions.md) for built-in and custom extensions.

## Reference Files

This skill uses a modular reference system for progressive disclosure:

### Core Documentation

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - htmx fundamentals, architecture, and core principles
- [`references/02-request-attributes.md`](references/02-request-attributes.md) - All HTTP method attributes (hx-get, hx-post, etc.)
- [`references/03-triggers-and-events.md`](references/03-triggers-and-events.md) - Trigger system, event handling, and timing
- [`references/04-swapping.md`](references/04-swapping.md) - DOM swap modes, morphing, and view transitions
- [`references/05-oob-swaps.md`](references/05-oob-swaps.md) - Out-of-band swaps for updating multiple elements

### Advanced Topics

- [`references/06-websockets-sse.md`](references/06-websockets-sse.md) - WebSockets and Server-Sent Events
- [`references/07-extensions.md`](references/07-extensions.md) - Built-in extensions and custom extension development
- [`references/08-events-api.md`](references/08-events-api.md) - Complete event system and JavaScript API reference
- [`references/09-server-responses.md`](references/09-server-responses.md) - Response headers, status codes, and server patterns
- [`references/10-common-patterns.md`](references/10-common-patterns.md) - Common UI patterns (modals, tabs, forms, etc.)

### Migration and Best Practices

- [`references/11-migration-v1-to-v2.md`](references/11-migration-v1-to-v2.md) - Migrating from htmx 1.x to 2.x
- [`references/12-security-best-practices.md`](references/12-security-best-practices.md) - Security considerations and best practices
- [`references/13-performance-optimization.md`](references/13-performance-optimization.md) - Performance tuning and optimization techniques

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/htmx-2/`). All paths are relative to this directory.

## Troubleshooting

### Common Issues

**htmx not working after dynamic content insertion:**
```javascript
// Process new content manually
htmx.process(document.body);
```

**Request not firing:**
- Check browser console for errors
- Verify `hx-*` attributes are spelled correctly (or use `data-hx-*`)
- Ensure htmx script loads before elements are processed

**Element not updating:**
- Verify `hx-target` selector matches an element in the DOM
- Check server response contains valid HTML
- Use browser DevTools Network tab to inspect responses

**Extensions not loading:**
```html
<!-- Load htmx first, then extensions -->
<script src="htmx.min.js"></script>
<script src="ext/ws.js"></script>
<script src="ext/sse.js"></script>
```

### Debugging

Enable comprehensive logging:

```javascript
// Log all htmx events
htmx.logAll();

// Custom logger
htmx.logger = function(elt, event, data) {
    console.log('htmx:', event, elt, data);
};
```

See [Events and API Reference](references/08-events-api.md) for complete debugging guide.

### Getting Help

- [htmx Documentation](https://htmx.org/docs/) - Official documentation
- [htmx Examples](https://htmx.org/examples/) - Working code examples
- [htmx GitHub Issues](https://github.com/bigskysoftware/htmx/issues) - Bug reports and feature requests
- [htmx Discord](https://htmx.org/discord/) - Community support

## Key Concepts

### No JavaScript Required (But Optional)

htmx works entirely from HTML attributes, but can be extended with JavaScript:

```html
<!-- Pure HTML approach -->
<button hx-get="/data" hx-target="#result">Load</button>

<!-- With JavaScript enhancement -->
<button hx-get="/data" 
        hx-target="#result"
        hx-on::before-request="htmx.ajax('POST', '/analytics', {values: {action: 'load'}})">
    Load with Analytics
</button>
```

### Progressive Enhancement

htmx applications work without JavaScript and enhance progressively:

```html
<!-- Fallback to normal form submission if JS disabled -->
<form action="/submit" method="post" 
      hx-post="/submit" 
      hx-target="#result">
    <input name="data">
    <button type="submit">Submit</button>
</form>
```

### Server-Driven UI

Respond with HTML fragments, not JSON:

```html
<!-- Server returns HTML, not JSON -->
<div id="user-info">
    <h3>{{ user.name }}</h3>
    <p>{{ user.email }}</p>
</div>
```

### HATEOAS Support

htmx naturally supports Hypermedia As The Engine Of Application State:

```html
<!-- Links in response drive next actions -->
<div id="posts">
    {% for post in posts %}
    <article>
        <h2>{{ post.title }}</h2>
        <a hx-get="/posts/{{ post.id }}" hx-target="#post-detail">
            Read More
        </a>
    </article>
    {% endfor %}
</div>
```

For more architectural patterns, see [Core Concepts](references/01-core-concepts.md).

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
