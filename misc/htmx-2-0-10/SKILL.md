---
name: htmx-2-0-10
description: Complete reference for htmx 2.0.10 — the HTML attributes library for AJAX, WebSockets, SSE, and dynamic DOM updates without writing JavaScript. Covers all core attributes, 7 core extensions, 30+ community extensions, third-party integrations (Alpine.js, jQuery, hyperscript, SortableJS, Web Components, SweetAlert2, Tom Select), 25+ UX patterns, configuration, security, validation, history/boosting, caching, and migration guides.
---

# htmx 2.0.10

htmx is a JavaScript library that lets you build modern user interfaces directly in HTML — no JavaScript required for most interactions. It generalizes hypermedia controls via attributes like `hx-get`, `hx-post`, `hx-swap`, and `hx-trigger`.

## Overview

htmx is a JavaScript library that lets you build modern user interfaces directly in HTML — no JavaScript required for most interactions. It generalizes hypermedia controls via attributes like `hx-get`, `hx-post`, `hx-swap`, and `hx-trigger`.

## When to Use

- Building dynamic web UIs without a frontend framework (React, Vue, etc.)
- Progressive enhancement of existing HTML applications
- AJAX requests, real-time updates (SSE/WebSockets), and form handling from pure HTML
- Pairing with lightweight reactive libraries (Alpine.js, hyperscript)
- Migrating from intercooler.js, Hotwire/Turbo, or htmx 1.x

## Installation

### CDN
```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
```

### npm
```bash
npm install htmx.org
```

```javascript
import 'htmx.org';
```

### Download
Download from `https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.js` and serve locally.

## Core Concepts

### Making Requests
Add `hx-get`, `hx-post`, `hx-put`, `hx-patch`, or `hx-delete` to any element. The attribute value is the URL.

```html
<button hx-get="/items/42" hx-target="#result">Load Item</button>
```

### Triggers
Control when requests fire with `hx-trigger`. Default is the natural event (`click`, `submit`, `change`).

```html
<input hx-get="/search" hx-trigger="input changed delay:300ms" />
```

### Targets and Swapping
`hx-target` specifies where response content goes. `hx-swap` controls how it's inserted.

```html
<button hx-post="/items" hx-target="#list" hx-swap="beforeend">Add Item</button>
```

### Out of Band Swaps
Update multiple elements from one response using `hx-swap-oob` in the server response.

### Extensions
Augment htmx with extensions: SSE, WebSockets, preload, morphing, and 30+ community extensions.

```html
<body hx-ext="sse,ws,preload">
```

## Quick Start

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
</head>
<body>
  <!-- Basic AJAX button -->
  <button hx-get="/hello" hx-target="#output">Say Hello</button>
  <div id="output"></div>

  <!-- Form with validation and loading indicator -->
  <form hx-post="/save" hx-target="#result" hx-indicator="#spinner">
    <input name="name" required />
    <button type="submit" hx-disable>Save</button>
    <span id="spinner" class="htmx-indicator">Saving...</span>
  </form>
  <div id="result"></div>

  <!-- Boosted navigation (progressive enhancement) -->
  <nav hx-boost="true">
    <a href="/about">About</a>
    <a href="/contact">Contact</a>
  </nav>
  <main id="main"></main>
</body>
</html>
```

## Reference Files

### Core htmx
| File | Topic |
|------|-------|
| [01-ajax-requests.md](reference/01-ajax-requests.md) | AJAX attributes, triggers, targets, parameters, indicators, synchronization |
| [02-swapping-and-settling.md](reference/02-swapping-and-settling.md) | Swap styles, OOB swaps, CSS transitions, view transitions, hx-select, hx-preserve |
| [03-attributes-reference.md](reference/03-attributes-reference.md) | Complete attribute catalog — all 25+ core and extension attributes |
| [04-events-and-api.md](reference/04-events-and-api.md) | 40+ events, JavaScript API (htmx.ajax, htmx.swap, htmx.onLoad, etc.), scripting patterns |
| [05-configuration.md](reference/05-configuration.md) | All config variables, meta tags, response handling configuration |

### Core Extensions
| File | Topic |
|------|-------|
| [06-core-extensions-sse-ws.md](reference/06-core-extensions-sse-ws.md) | SSE extension (connect, swap, triggers, events) and WebSocket extension (send, receive, reconnection, socket wrapper API) |
| [07-core-extensions-head-idiomorph.md](reference/07-core-extensions-head-idiomorph.md) | head-support (head tag merging for boosted navigation) and idiomorph (DOM morphing swap strategy) |
| [08-core-extensions-preload-response-targets.md](reference/08-core-extensions-preload-response-targets.md) | preload (cache-ahead loading) and response-targets (route by HTTP status code) |
| [09-core-extensions-1-compat.md](reference/09-core-extensions-1-compat.md) | htmx-1-compat (restore htmx 1.x defaults for gradual migration) |

### Community Extensions
| File | Topic |
|------|-------|
| [10-community-extensions-ui.md](reference/10-community-extensions-ui.md) | loading-states, class-tools, attribute-tools, multi-swap, remove-me, morphdom-swap, alpine-morph |
| [11-community-extensions-data.md](reference/11-community-extensions-data.md) | json-enc, form-json (type preservation), json-enc-custom, client-side-templates (Mustache/Nunjucks/Handlebars), htmx-json |
| [12-community-extensions-utility.md](reference/12-community-extensions-utility.md) | path-deps, path-params, event-header, ajax-header, debug, no-cache, restored, safe-nonce, dynamic-url, optimistic, disable-element (legacy) |
| [13-community-extensions-integrations.md](reference/13-community-extensions-integrations.md) | signalr (.NET), amz-content-sha256 (AWS), hx-drag (drag-drop), replace-params |
| [14-building-extensions.md](reference/14-building-extensions.md) | Extension API — defineExtension, lifecycle hooks, custom swap strategies, publishing |

### Patterns and Integrations
| File | Topic |
|------|-------|
| [15-ux-patterns.md](reference/15-ux-patterns.md) | 25+ patterns: active search, click-to-edit, bulk update, infinite scroll, file upload, modals, tabs, keyboard shortcuts, drag-drop, async auth, web components |
| [16-third-party-integrations.md](reference/16-third-party-integrations.md) | Alpine.js, jQuery, hyperscript, VanillaJS, SortableJS, Web Components (shadow DOM), SweetAlert2, Tom Select |

## Advanced Topics

The following reference files cover advanced htmx topics:

| File | Topic |
|------|-------|
| [17-history-and-boosting.md](reference/17-history-and-boosting.md) | hx-push-url, hx-replace-url, hx-boost, history snapshots, cache miss handling, 3rd party cleanup |
| [18-security-and-validation.md](reference/18-security-and-validation.md) | HTML5 validation, hx-validate, CSRF, CSP/nonces, selfRequestsOnly, allowScriptTags, inheritance (hx-disinherit/hx-inherit) |
| [19-caching-and-performance.md](reference/19-caching-and-performance.md) | HTTP caching (ETag, Last-Modified, Vary), cache-busting, preload for performance, polling optimization |
| [20-migration-and-quirks.md](reference/20-migration-and-quirks.md) | htmx 1.x → 2.x migration, intercooler.js migration, Hotwire/Turbo patterns, known quirks and edge cases |
