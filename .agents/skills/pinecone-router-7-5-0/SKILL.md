---
name: pinecone-router-7-5-0
description: A comprehensive toolkit for building client-side routing in Alpine.js applications using Pinecone Router v7.5, providing route matching, template rendering, handlers, navigation history, and TypeScript support for single-page applications. Use when building SPAs with Alpine.js that require declarative HTML-based routing, external template loading, async data fetching in route handlers, hash or history-based navigation, or programmatic route management without a build step.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "7.5.0"
tags:
  - alpinejs
  - router
  - spa
  - client-side-routing
  - single-page-application
  - history-api
  - template-engine
category: frontend-framework
external_references:
  - https://github.com/pinecone-router/router
  - https://www.npmjs.com/package/pinecone-router
---

# Pinecone Router v7.5

## Overview

Pinecone Router is a small, easy-to-use, and feature-packed client-side router for Alpine.js. At approximately 3 KB gzipped with zero dependencies, it provides declarative HTML-based routing through Alpine.js directives (`x-route`, `x-template`, `x-handler`), supporting inline templates, external template fetching, async route handlers with abort support, navigation history management, hash routing, base path configuration, and full TypeScript definitions.

It integrates as an Alpine.js plugin and exposes three magic helpers — `$router`, `$history`, and `$params` — for accessing router state from within Alpine components.

## When to Use

- Building single-page applications with Alpine.js that need client-side routing
- Routing without a build step (CDN or browser module installation)
- Applications needing inline HTML templates or externally fetched template files
- Routes that require async data fetching before rendering (handler-based guards and data loading)
- Projects needing navigation history with back/forward controls independent of the browser
- Hash-based routing for environments without server-side URL rewriting
- TypeScript projects requiring type-safe routing APIs

## Core Concepts

**Declarative Routing**: Routes are declared in HTML using `<template>` elements with the `x-route` directive. No JavaScript route configuration is needed for basic setups.

**Route Matching**: Supports literal segments (`/about`), named params (`/:id`), optional params (`/:id?`), rest params (`/:path+`), wildcards (`/:path*`), file extensions (`/:name.mp4`), and extension patterns (`/:name.(mp4|mov)`). Trailing slashes are normalized, matching is case-insensitive.

**Templates**: Routes display content through `x-template` — either inline (children of the `<template>` tag) or external (fetched HTML files from URLs). Templates support preloading, target element rendering, and URL interpolation with route params.

**Handlers**: Functions that execute before templates render, registered via `x-handler`. Handlers receive a context object with route info and an `AbortController` for cancellation. They run sequentially, can be async, and can pass data between each other by returning values.

**Navigation History**: An independent history stack tracking visited paths (excluding duplicates and redirects), accessible via `$history.back()`, `$history.forward()`, `$history.canGoBack()`, and `$history.entries`.

## Installation / Setup

### CDN

Include before Alpine.js in the `<head>`:

```html
<script src="https://cdn.jsdelivr.net/npm/pinecone-router@7.5.0/dist/router.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/cdn.min.js"></script>
```

### NPM

```bash
npm install pinecone-router
```

```javascript
import PineconeRouter from 'pinecone-router'
import Alpine from 'alpinejs'

Alpine.plugin(PineconeRouter)
Alpine.start()
```

### Browser Module (ESM)

```javascript
import PineconeRouter from 'https://cdn.jsdelivr.net/npm/pinecone-router@7.5.0/dist/router.esm.js'
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/module.esm.js'

Alpine.plugin(PineconeRouter)
```

## Usage Examples

### Basic SPA with Inline Templates

```html
<div x-data="app">
  <!-- Home route -->
  <template x-route="/" x-template>
    <h1>Welcome!</h1>
    <p>Your name?</p>
    <input @keydown.enter="$router.navigate('/'+$el.value)">
  </template>

  <!-- Dynamic route with named param -->
  <template x-route="/:name" x-handler="greetHandler" x-template>
    <h1>Hello <span x-text="$params.name"></span>!</h1>
    <button @click="$history.back()">Go Back</button>
  </template>

  <!-- 404 fallback -->
  <template x-route="notfound" x-template>
    <h1>Page Not Found</h1>
  </template>
</div>

<script>
  document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
      greetHandler(context, controller) {
        if (context.params.name === 'admin') {
          this.$router.navigate('/login')
        }
      },
    }))
  })
</script>
```

### External Templates with Preloading

```html
<div x-data="app">
  <template x-route="/" x-template.preload="/views/home.html"></template>
  <template x-route="/profile/:id" x-template="/views/profile.html"></template>
  <template x-route="notfound" x-template.preload="/views/404.html"></template>
</div>

<script>
  document.addEventListener('alpine:init', () => {
    window.PineconeRouter.settings({
      targetID: 'app',  // render templates inside <div id="app">
    })
  })
</script>

<div id="app"></div>
```

### Async Handler with Data Passing

```html
<template x-route="/posts" x-handler="[fetchPosts, renderPosts]" x-template="/views/posts.html"></template>

<script>
  Alpine.data('app', () => ({
    async fetchPosts(ctx, controller) {
      const response = await fetch('/api/posts', { signal: controller.signal })
      return await response.json()  // passed to next handler via ctx.data
    },
    renderPosts(ctx) {
      console.table(ctx.data)  // array of posts from previous handler
    },
  }))
</script>
```

### Loading Events with nProgress

```javascript
document.addEventListener('pinecone:start', () => NProgress.start())
document.addEventListener('pinecone:end', () => NProgress.done())
document.addEventListener('pinecone:fetch-error', (e) => console.error(e.detail))
```

## Advanced Topics

**Route Matching & Parameters**: Named params, optional segments, wildcards, rest params, file extensions, and accessing `$params` → [Route Matching](reference/01-route-matching.md)

**Templates Deep Dive**: Inline templates, external templates, `.target`, `.preload`, `.interpolate` modifiers, embedded scripts with `x-run`, multiple root elements → [Templates](reference/02-templates.md)

**Handlers**: Route handlers, global handlers, async handlers with AbortController, data passing between handlers, handler chaining → [Handlers](reference/03-handlers.md)

**Navigation History**: The `$history` magic helper, back/forward navigation, history entries, duplicate and redirect handling → [Navigation History](reference/04-navigation-history.md)

**Configuration & Settings**: `basePath`, `hash` routing, `targetID`, `handleClicks`, `globalHandlers`, `preload`, `fetchOptions`, `pushState` → [Settings](reference/05-settings.md)

**Programmatic API**: Adding and removing routes with JavaScript, `PineconeRouter.add()`, `PineconeRouter.remove()`, `PineconeRouter.match()`, named routes → [Programmatic API](reference/06-programmatic-api.md)

**TypeScript Reference**: Full type definitions for `Handler`, `HandlerContext`, `Context`, `Route`, `Settings`, `NavigationHistory`, and Alpine magic helpers → [TypeScript Types](reference/07-typescript-types.md)
