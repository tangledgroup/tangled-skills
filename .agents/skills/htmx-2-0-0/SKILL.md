---
name: htmx-2-0-0
description: A skill for building interactive web applications with htmx 2.x, a JavaScript library that allows accessing modern browser features directly from HTML attributes without writing JavaScript. Use when creating dynamic web interfaces, implementing AJAX requests from HTML, working with server-driven UIs, integrating WebSockets/SSE, or migrating from JavaScript-heavy frameworks to hypermedia-driven architectures.
version: "2.0.0"
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

# htmx 2.x

## Overview

htmx is a dependency-free JavaScript library (~14k min.gz'd) that lets you access AJAX, CSS Transitions, WebSockets, and Server-Sent Events directly from HTML using attributes. It extends the core idea of HTML as hypertext — any element can issue HTTP requests, any event can trigger them, any HTTP verb can be used, and any element can be the update target.

The key philosophy: respond with **HTML**, not JSON. This keeps you within the original web programming model using Hypertext As The Engine Of Application State (HATEOAS).

htmx 2.x is the current major version. It drops IE11 support, moves all extensions out of core into separate packages, provides ESM/AMD/CJS module builds, and changes `hx-on` to require the `hx-on:` prefix format. Version 1.x continues to be maintained for IE11 compatibility.

## When to Use

- Building interactive web interfaces without writing JavaScript
- Implementing AJAX requests declaratively from HTML attributes
- Creating server-driven UIs where the server returns HTML fragments
- Adding progressive enhancement to existing traditional web applications
- Integrating real-time features (WebSockets, SSE) with minimal JavaScript
- Migrating away from heavy client-side frameworks (React, Vue, Angular)
- Building applications that pair well with Alpine.js, hyperscript, or vanilla JS
- Rapid prototyping where a full build toolchain is overkill

## Core Concepts

**Hypermedia-driven architecture**: htmx generalizes the `<a>` tag pattern. An anchor tells the browser "on click, GET this URL and load the response." htmx extends this so any element can issue any HTTP verb on any event and target any DOM element.

**Server returns HTML**: Unlike REST/JSON APIs, htmx expects HTML fragments (or full pages) as responses. The server drives the UI by returning markup that gets swapped into the DOM.

**Attributes over JavaScript**: Behavior is declared in HTML attributes (`hx-get`, `hx-post`, `hx-trigger`, etc.) rather than imperative JavaScript code. This preserves Locality of Behavior (LoB).

**Progressive enhancement**: With `hx-boost`, links and forms work without JavaScript — they simply use full-page navigation as a fallback.

## Installation / Setup

Via CDN (fastest):

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"
        integrity="sha384-H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V"
        crossorigin="anonymous"></script>
```

Via npm:

```sh
npm install htmx.org@2.0.10
```

Then in your build:

```js
import 'htmx.org';
// or for global window.htmx:
window.htmx = require('htmx.org');
```

Module-specific builds are available at `/dist/htmx.esm.js`, `/dist/htmx.amd.js`, and `/dist/htmx.cjs.js`.

Configure via `<meta>` tag or JavaScript:

```html
<meta name="htmx-config" content='{"defaultSwapStyle":"outerHTML"}'>
```

```js
htmx.config.defaultSwapStyle = 'outerHTML';
```

## Advanced Topics

**Core Attributes**: AJAX attributes (`hx-get`, `hx-post`, etc.), triggers, targets, and swap strategies → [Core Attributes](reference/01-core-attributes.md)

**Boosting and History**: Progressive enhancement with `hx-boost`, browser history management, URL pushing → [Boosting and History](reference/02-boosting-and-history.md)

**Out-of-Band Swaps and Selectors**: Piggybacking DOM updates, selecting response content, OOB swap strategies → [Out-of-Band Swaps](reference/03-out-of-band-swaps.md)

**WebSockets and SSE**: Real-time communication via extensions, `hx-ws` and `hx-sse` attributes → [WebSockets and SSE](reference/04-websockets-and-sse.md)

**Extensions**: Core and community extensions, installation patterns, custom extension API → [Extensions](reference/05-extensions.md)

**Events and Scripting**: htmx event lifecycle, `hx-on:` attributes, integrating 3rd-party libraries → [Events and Scripting](reference/06-events-and-scripting.md)

**HTTP Headers and Request/Response**: HX-* request/response headers, response handling configuration, status code behavior → [HTTP Headers](reference/07-http-headers.md)

**Validation, Security, and Configuration**: HTML5 validation integration, XSS prevention, CSP, CSRF, config options → [Validation and Security](reference/08-validation-and-security.md)

**1.x to 2.x Migration**: Breaking changes, extension separation, `hx-on` format changes, module builds → [Migration Guide](reference/09-migration-guide.md)
