---
name: htmx-4-0-0
description: "A skill for building interactive web applications with htmx 4.0 (currently at 4.0.0-beta2), a JavaScript library that provides HTML attributes for AJAX requests, CSS transitions, WebSockets, and Server-Sent Events without writing JavaScript. Use when creating dynamic user interfaces with hypermedia-driven architecture, migrating from htmx 2.x, or implementing modern web patterns using declarative HTML syntax. Note: 4.0 is not yet a stable release — latest stable is 2.0.10."
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.0.0-beta2"
tags:
  - htmx
  - hypermedia
  - ajax
  - html-attributes
  - server-driven-ui
  - websockets
  - sse
category: frontend
external_references:
  - https://four.htmx.org/
  - https://github.com/bigskysoftware/htmx
---

# htmx 4.0

## Overview

htmx is a lightweight JavaScript library that lets you access modern browser features (AJAX, WebSockets, SSE) directly from HTML using attributes like `hx-get`, `hx-post`, and `hx-trigger`. It follows the original web programming model: the server sends HTML in response to user actions, and htmx swaps that HTML into the DOM. This is called **HATEOAS** (Hypertext As The Engine Of Application State).

htmx 4.0 is a major release built on the `fetch()` API (replacing XMLHttpRequest), with explicit attribute inheritance, improved extension architecture based on event hooks, and enhanced swap strategies including morph-based updates via [idiomorph](https://github.com/bigskysoftware/idiomorph).

Key characteristics:
- Single JavaScript file, no dependencies, no build step required
- ~14KB minified+gzipped
- HTML responses from the server (not JSON)
- Declarative — behavior lives in HTML attributes
- Progressive enhancement friendly
- Supports extensions for SSE, WebSockets, preload, and more

## When to Use

- Building dynamic web interfaces without JavaScript frameworks
- Implementing AJAX requests declaratively from HTML
- Creating server-driven UIs where the server controls rendering
- Integrating WebSockets or Server-Sent Events with HTML
- Migrating from htmx 2.x to htmx 4.x
- Replacing JavaScript-heavy SPAs with hypermedia-driven architectures
- Adding interactivity to existing HTML pages with minimal code

## Installation / Setup

htmx is a single JavaScript file with no dependencies. No build step required.

### CDN (recommended for quick start)

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta2"
        integrity="sha384-v+EMKtNUAo5enmQxBqgoU/FWvVvvZHvITNzurHSl4kzvCs94wdlgHUci1lliKWKz"
        crossorigin="anonymous"></script>
```

### ES Module

```html
<script type="module" src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta2/dist/htmx.esm.min.js"></script>
```

### npm

```bash
npm install htmx.org@4.0.0-beta2
```

```javascript
import 'htmx.org';
// or named import:
import htmx from 'htmx.org';
```

### Self-hosted

Download `htmx.min.js` and include it in your `<head>`:

```html
<script src="/js/htmx.min.js"></script>
```

### htmax (bundled extensions)

The `htmax.js` file bundles htmx with the most popular extensions in a single file: SSE, WebSockets, preload, browser-indicator, download, optimistic, and targets. Extensions are automatically available without separate loading.

```html
<script src="/js/htmax.min.js"></script>
```

## Core Concepts

### Hypermedia Controls

HTML has two native elements that issue HTTP requests: `<a>` (GET) and `<form>` (POST/GET). htmx generalizes this — **any element** can issue **any type of HTTP request** to **any URL**, triggered by **any event**, with the response placed **anywhere in the DOM**.

```html
<button hx-post="/clicked" hx-target="#output" hx-swap="outerHTML">
  Click Me
</button>
<output id="output"></output>
```

htmx expects **HTML responses** from the server, not JSON. The server controls what the user sees.

### Attribute Inheritance (Explicit in 4.0)

In htmx 4.0, attribute inheritance is **explicit by default** using the `:inherited` modifier. This is a major change from htmx 2.x where inheritance was implicit.

```html
<div hx-confirm:inherited="Are you sure?">
  <button hx-delete="/account">Delete Account</button>
  <button hx-put="/account">Update Account</button>
</div>
```

### Request Lifecycle

1. User triggers an event (click, input, etc.)
2. htmx collects form data and parameters
3. An AJAX request is issued via `fetch()`
4. Server returns HTML
5. htmx selects content from the response (`hx-select`)
6. Content is swapped into the target (`hx-target`, `hx-swap`)
7. CSS transitions are applied if element IDs are stable

## Advanced Topics

**Core Attributes Reference**: All hx-* attributes with syntax and examples → [Core Attributes](reference/01-core-attributes.md)

**Response Headers**: Server-controlled behavior via HX-* headers → [Response Headers](reference/02-response-headers.md)

**Extensions System**: SSE, WebSockets, preload, building custom extensions → [Extensions](reference/03-extensions.md)

**Migration from htmx 2.x**: Breaking changes and upgrade guide → [Migration Guide](reference/04-migration-guide.md)
