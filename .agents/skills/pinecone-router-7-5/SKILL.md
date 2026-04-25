---
name: pinecone-router-7-5
description: A comprehensive toolkit for building client-side routing in Alpine.js applications using Pinecone Router v7.5, providing route matching, template rendering, handlers, navigation history, and TypeScript support for single-page applications.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - alpinejs
  - routing
  - client-side-routing
  - single-page-application
  - javascript
  - typescript
  - templates
  - navigation
category: development
required_environment_variables: []

external_references:
  - https://github.com/rxmarcel/pinecone-router
  - https://www.npmjs.com/package/pinecone-router
---

# Pinecone Router 7.5


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A comprehensive toolkit for building client-side routing in Alpine.js applications using Pinecone Router v7.5, providing route matching, template rendering, handlers, navigation history, and TypeScript support for single-page applications.

A small, easy-to-use, and feature-packed router for Alpine.js that provides declarative routing with inline/external templates, route handlers, navigation history, and full TypeScript support.

## When to Use

- Building single-page applications (SPAs) with Alpine.js
- Implementing client-side routing without framework overhead
- Creating dynamic routes with parameters (named, optional, rest, wildcard)
- Needing template-based rendering with embedded scripts
- Requiring route handlers for authentication, data fetching, or redirects
- Implementing custom navigation history management
- Building TypeScript Alpine.js applications with type-safe routing

## Setup

### CDN Installation

Include Pinecone Router **before** Alpine.js in your document's `<head>`:

```html
<script src="https://cdn.jsdelivr.net/npm/pinecone-router@7.5.0/dist/router.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

### NPM Installation

```bash
npm install pinecone-router
```

```javascript
import PineconeRouter from 'pinecone-router'
import Alpine from 'alpinejs'

Alpine.plugin(PineconeRouter)
Alpine.start()
```

### Browser Module

```javascript
import PineconeRouter from 'https://cdn.jsdelivr.net/npm/pinecone-router@7.5.0/dist/router.esm.js'
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/module.esm.js'

Alpine.plugin(PineconeRouter)
Alpine.start()
```

## Quick Start

### Basic Routing Example

```html
<div x-data="app()">
  <!-- Home route with inline template -->
  <template x-route="/" x-template>
    <h1>Welcome!</h1>
    <p>What's your name?</p>
    <input @enter="$router.navigate('/' + $el.value)"></input>
  </template>

  <!-- Route with named parameter -->
  <template x-route="/:name" x-handler="handler" x-template>
    <h1>Hello <span x-text="$params.name"></span>!</h1>
    <button @click="$history.back()">Go Back</button>
  </template>

  <!-- 404 not found route -->
  <template x-route="notfound" x-template>
    <h1>Page Not Found</h1>
  </template>
</div>

<script>
  document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
      handler(context, controller) {
        // Access route params: context.params.name
        if (context.params.name === 'easter') {
          this.$router.navigate('/easter-egg')
        }
      },
    }))
  })
</script>
```

## Core Features

See [Route Matching](references/01-route-matching.md) for detailed pattern syntax and examples.

See [Templates](references/02-templates.md) for inline templates, external templates, and embedded scripts.

See [Handlers](references/03-handlers.md) for route handlers, async operations, and data passing.

See [Navigation](references/04-navigation.md) for navigation history, back/forward operations, and programmatic navigation.

## Magic Helpers

Pinecone Router provides three magic helpers accessible in Alpine.js components:

- **`$router`**: Access the PineconeRouter object for navigation and configuration
- **`$history`**: Access navigation history methods (back, forward, canGoBack, etc.)
- **`$params`**: Access current route parameters as an object

```html
<div x-data="{ }">
  <p>Current path: <span x-text="$router.context.path"></span></p>
  <p>Route params: <span x-text="$params.name"></span></p>
  <button @click="$history.back()" x-show="$history.canGoBack()">Back</button>
</div>
```

## Reference Files

- [`references/01-route-matching.md`](references/01-route-matching.md) - Route patterns, parameters, matching rules, and segment types
- [`references/02-templates.md`](references/02-templates.md) - Inline templates, external templates, modifiers, embedded scripts with x-run directive
- [`references/03-handlers.md`](references/03-handlers.md) - Route handlers, async operations, data passing, global handlers, cancellation
- [`references/04-navigation.md`](references/04-navigation.md) - Navigation history, programmatic navigation, events, loading states
- [`references/05-api-reference.md`](references/05-api-reference.md) - Complete TypeScript API reference, settings, objects, and interfaces

## Troubleshooting

### Templates Not Rendering

1. Ensure `x-template` directive is present on the route template element
2. Check that target element exists if using `.target` modifier
3. Verify external template URLs are accessible (check browser console for fetch errors)
4. Confirm Alpine.js initializes after Pinecone Router plugin

### Route Parameters Not Accessible

1. Use `$params.paramName` in templates, not `context.params` directly
2. Ensure parameter names match exactly (case-sensitive in access, case-insensitive in matching)
3. Check route pattern syntax: `/:paramName` for named params

### Navigation History Issues

1. Use `$history.canGoBack()` before calling `$history.back()`
2. Remember that redirects don't add to history
3. Duplicates are automatically filtered from history entries

### Hash Routing Not Working

```javascript
// Enable hash routing in settings
document.addEventListener('alpine:init', () => {
  window.PineconeRouter.settings({ hash: true })
})
```

See [Settings](references/05-api-reference.md#settings-object) for configuration options.

### TypeScript Integration

Import types from pinecone-router:

```typescript
import type { Handler, HandlerContext, Settings } from 'pinecone-router'

const myHandler: Handler<unknown, string> = (context: HandlerContext, controller) => {
  return `Hello ${context.params.name}`
}
```

## Compatibility

| Pinecone Router Version | Alpine.js Version |
|------------------------|-------------------|
| v7.x                   | v3                |
| v2.x                   | v3                |
| v1.x                   | v2                |

## Important Notes

1. **Trailing slashes are normalized** - Both `/about` and `/about/` work identically
2. **Matching is case-insensitive** - `/Home` matches `/home`
3. **Handlers run before templates** - Use handlers for redirects before rendering
4. **All navigation cancels ongoing handlers** - Prevents race conditions
5. **Templates don't re-render on param changes** - Use `x-effect` or `$watch` for reactive updates
6. **Embedded scripts run once per route visit** - Use `x-run.once` for library initialization
7. **Default notfound route logs error** - Override with custom `x-route="notfound"` template

## Common Patterns

### Authentication Guard

See [Handlers](references/03-handlers.md#authentication-guards) for implementation examples.

### Data Fetching Pattern

See [Handlers](references/03-handlers.md#async-data-fetching) for async operations with AbortController.

### Layout with Shared Components

See [Templates](references/02-templates.md#multiple-external-templates) for including header/footer templates.

### Dynamic Template URLs

See [Templates](references/02-templates.md#template-url-interpolation) for using route params in template paths.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
