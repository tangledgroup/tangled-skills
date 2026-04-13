---
name: htmx-4
description: A skill for building interactive web applications with htmx 4.0, a JavaScript library that provides HTML attributes for AJAX requests, CSS transitions, WebSockets, and Server-Sent Events without writing JavaScript. Use when creating dynamic user interfaces with hypermedia-driven architecture, migrating from htmx 2.x, or implementing modern web patterns using declarative HTML syntax.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - htmx
  - hypermedia
  - ajax
  - html
  - web-development
  - frontend
  - server-sent-events
  - websockets
category: development
---

# htmx-4

A comprehensive toolkit for building interactive web applications with htmx 4.0, a JavaScript library that allows accessing AJAX, CSS Transitions, WebSockets, and Server-Sent Events directly in HTML using attributes. htmx completes HTML as a hypertext by removing arbitrary constraints on which elements can make HTTP requests, which events can trigger them, which HTTP methods are available, and how responses can be swapped into the DOM.

**Key characteristics:**
- Small (~14KB min.gz'd), dependency-free, and extendable
- Uses native `fetch()` API (replaces XMLHttpRequest from htmx 2.x)
- Explicit attribute inheritance with `:inherited` modifier
- Swaps all HTTP responses including 4xx/5xx by default
- 60-second default timeout (vs unlimited in htmx 2.x)

## When to Use

Load this skill when:
- Building dynamic web interfaces without JavaScript frameworks
- Adding AJAX functionality to existing HTML applications
- Implementing real-time features with WebSockets or Server-Sent Events
- Migrating from htmx 2.x to htmx 4.0
- Creating hypermedia-driven applications (HATEOAS)
- Needing progressive enhancement with graceful degradation
- Working with server-side rendering frameworks

## Quick Start

### Installation via CDN

Add this to your `<head>` tag:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta1/dist/htmx.min.js"></script>
```

### Basic Usage

```html
<!-- Button that POSTs via AJAX and replaces itself with response -->
<button hx-post="/clicked" hx-swap="outerHTML">
  Click Me
</button>

<!-- Form that submits via AJAX -->
<form hx-post="/submit" hx-swap="outerHTML">
  <input name="username" placeholder="Username">
  <button type="submit">Submit</button>
</form>
```

The `hx-post` attribute triggers an AJAX request on the default event (click for buttons, submit for forms). The `hx-swap` attribute specifies how to replace the target element with the server response.

## Core Concepts

See [Core Concepts](references/01-core-concepts.md) for detailed explanation of:
- Request lifecycle and flow
- Attribute inheritance with `:inherited` modifier
- Target selection strategies
- Swap styles and OOB (out-of-band) swaps
- Multi-target updates with `<hx-partial>`

## Common Operations

### HTTP Methods

See [HTTP Attributes Reference](references/02-http-attributes.md) for:
- `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete`
- `hx-method` and `hx-action` for flexible method specification
- Request configuration with `hx-config`

### Triggers and Events

See [Triggers and Events](references/03-triggers-events.md) for:
- Standard DOM events (click, input, submit, keyup)
- Synthetic events (load, revealed, intersect)
- Event filters and modifiers (delay, throttle, changed, once)
- Polling with `every 1s` syntax
- Custom event handling

### Response Handling

See [Response Handling](references/04-response-handling.md) for:
- Swap styles (innerHTML, outerHTML, beforebegin, afterend, etc.)
- Out-of-band swaps with `hx-swap-oob`
- Status code handling with `hx-status`
- View transitions API support

### Real-time Features

See [Real-time Communication](references/05-realtime.md) for:
- Server-Sent Events (SSE) with `hx-sse:connect`
- WebSocket communication with `hx-ws:connect`
- Extension loading and configuration

## Configuration

htmx 4.0 introduces new configuration options and changes defaults from htmx 2.x:

```javascript
// Restore htmx 2.x behavior (optional)
htmx.config.implicitInheritance = true;  // Implicit attribute inheritance
htmx.config.noSwap = [204, 304, '4xx', '5xx'];  // Don't swap error responses
htmx.config.defaultTimeout = 0;  // No timeout (htmx 4 default: 60000ms)

// Enable view transitions
htmx.config.transitions = true;

// Configure history behavior
htmx.config.history = "reload";  // Full page reload on history navigation
htmx.config.history = false;  // Disable history
```

See [Configuration Reference](references/06-configuration.md) for complete config options.

## Extensions

htmx 4 ships with 9 core extensions loaded by including their script files:

```html
<script src="/path/to/htmx.min.js"></script>
<script src="/path/to/ext/sse.js"></script>
<script src="/path/to/ext/ws.js"></script>
```

Core extensions include:
- **alpine-compat**: Alpine.js compatibility
- **browser-indicator**: Native browser loading indicator
- **head-support**: Merge head tag information
- **htmx-2-compat**: htmx 2.x backward compatibility
- **optimistic**: Show expected content before server response
- **preload**: Early request triggering on mouseover/mousedown
- **sse**: Server-Sent Events support
- **upsert**: Update/insert elements by ID
- **ws**: WebSocket communication

See [Extensions Guide](references/07-extensions.md) for extension details.

## Migration from htmx 2.x

### Breaking Changes Summary

1. **Explicit inheritance**: Add `:inherited` to attributes that should inherit down DOM tree
2. **Error responses swap**: 4xx/5xx responses now swap by default
3. **`hx-delete` excludes form data**: Like `hx-get`, no longer includes enclosing form inputs
4. **No history cache**: Pages re-fetched on back navigation instead of localStorage retrieval
5. **60-second timeout**: Default timeout changed from 0 (unlimited) to 60000ms

### Attribute Renames

| htmx 2.x | htmx 4.x |
|----------|----------|
| `hx-disable` | `hx-ignore` |
| `hx-disabled-elt` | `hx-disable` |
| `hx-vars` | `hx-vals` with `js:` prefix |
| `hx-request` | `hx-config` |
| `hx-ext` | Include extension script directly |

### Event Renames

All events now follow pattern: `htmx:phase:action[:sub-action]`

| htmx 2.x | htmx 4.x |
|----------|----------|
| `htmx:beforeRequest` | `htmx:before:request` |
| `htmx:afterRequest` | `htmx:after:request` |
| `htmx:beforeSwap` | `htmx:before:swap` |
| `htmx:afterSwap` | `htmx:after:swap` |
| `htmx:configRequest` | `htmx:config:request` |
| All error events | `htmx:error` (consolidated) |

See [Migration Guide](references/08-migration.md) for complete migration checklist.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Request lifecycle, attribute inheritance, target selection, swap mechanics
- [`references/02-http-attributes.md`](references/02-http-attributes.md) - HTTP method attributes, request configuration, headers, values
- [`references/03-triggers-events.md`](references/03-triggers-events.md) - Trigger syntax, event filters, modifiers, custom events
- [`references/04-response-handling.md`](references/04-response-handling.md) - Swap styles, OOB swaps, status codes, view transitions
- [`references/05-realtime.md`](references/05-realtime.md) - SSE and WebSocket extensions, real-time patterns
- [`references/06-configuration.md`](references/06-configuration.md) - Config options, meta tags, environment setup
- [`references/07-extensions.md`](references/07-extensions.md) - Core extensions, custom extension development
- [`references/08-migration.md`](references/08-migration.md) - Complete htmx 2.x to 4.0 migration guide

**Note:** `{baseDir}` refers to the skill's base directory (e.g., `.agents/skills/htmx-4/`). All paths are relative to this directory.

## Troubleshooting

### Common Issues

**Requests not firing:**
- Check element has appropriate trigger attribute or default trigger matches element type
- Verify `hx-ignore` is not set on element or ancestors
- Ensure htmx script loads before elements are processed

**Inheritance not working:**
- Use `:inherited` modifier explicitly (e.g., `hx-confirm:inherited="..."`)
- Check for multiple inherited values (later ones replace earlier unless using `:append`)

**Error responses not showing:**
- htmx 4 swaps 4xx/5xx by default - design error responses as valid HTML
- Use `hx-status:5xx="swap:none"` to prevent swapping specific codes
- Set `htmx.config.noSwap = ['4xx', '5xx']` to restore htmx 2 behavior

**Form data not sending:**
- `hx-delete` and `hx-get` exclude form data by design
- Use `hx-include="closest form"` to explicitly include form inputs

**History navigation issues:**
- History no longer uses localStorage - pages re-fetch on back navigation
- Use `htmx.config.history = "reload"` for full page reload instead
- Set `htmx.config.history = false` to disable history entirely

See [Migration Guide](references/08-migration.md) for additional troubleshooting and the [Patterns](https://four.htmx.org/patterns) page for common use cases.
