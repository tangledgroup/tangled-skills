# Handlers

## Overview

Handlers are functions that execute when a route is matched. They run **before** templates render, allowing you to redirect, fetch data, or display content programmatically without templates.

Register handlers with the `x-handler` directive:

```html
<template x-route="/profile/:id" x-handler="loadProfile"></template>
<template x-route="/admin" x-handler="[checkAuth, loadDashboard]"></template>
```

## Handler Signature

Each handler receives two arguments:

```javascript
handler(context, controller) {
  // context: HandlerContext — route info + data from previous handler
  // controller: AbortController — for cancellation
}
```

### Context Object

The `context` parameter is a `HandlerContext` containing:

- `context.path` — the current URL path
- `context.params` — captured route parameters (e.g., `{ id: "42" }`)
- `context.route` — the matched `Route` object (path, name, pattern)
- `context.data` — the return value from the previous handler (or `undefined` for the first handler)

### AbortController

The `controller` parameter is a standard [`AbortController`](https://developer.mozilla.org/en-US/docs/Web/API/AbortController):

- `controller.signal` — pass to `fetch()` to auto-cancel when user navigates away
- `controller.abort()` — cancel subsequent handlers in the chain

## Handler Execution Model

- Handlers run **sequentially** and are **awaited** automatically
- A handler's return value is passed to the next handler via `context.data`
- Any navigation call (`$router.navigate()`) cancels all pending handlers
- The global `$router.context` is not updated until all handlers complete

## Examples

### Simple Handler — Render Content from JS

```html
<template x-route="/greet/:name" x-handler="greet"></template>
<div id="app"></div>

<script>
  Alpine.data('app', () => ({
    greet(context) {
      document.querySelector('#app').innerHTML =
        `<h1>Hello, ${context.params.name}!</h1>`
    },
  }))
</script>
```

### Redirect in Handler

```html
<template x-route="/old-page" x-handler="redirectHandler"></template>

<script>
  Alpine.data('app', () => ({
    redirectHandler(context) {
      this.$router.navigate('/new-page')
      // Subsequent handlers on /old-page will not run
    },
  }))
</script>
```

### Async Data Fetching with Abort

```html
<template x-route="/posts" x-handler="[fetchPosts, renderPosts]" x-template="/views/posts.html"></template>

<script>
  Alpine.data('app', () => ({
    async fetchPosts(ctx, controller) {
      try {
        const response = await fetch('/api/posts', { signal: controller.signal })
        return await response.json()  // passed to renderPosts as ctx.data
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Fetch failed:', err.message)
          controller.abort()  // stops template rendering and subsequent handlers
        }
      }
    },
    renderPosts(ctx) {
      if (ctx.data) {
        console.table(ctx.data)  // array of posts
      }
    },
  }))
</script>
```

### Handler Array with Anonymous Functions

```html
<template x-route="/redirect-home" x-handler="[(ctx) => $router.navigate('/'), neverRuns]"></template>
```

### Cancel Subsequent Handlers Without Redirecting

```javascript
errorHandler(ctx, controller) {
  if (someErrorCondition) {
    document.querySelector('#app').innerHTML = '<h1>Error</h1>'
    controller.abort()  // stops remaining handlers, template not rendered
  }
}
```

## Global Handlers

Define handlers that run on **every** route using the `.global` modifier. These execute before route-specific handlers:

```html
<div x-data="app" x-handler.global="[logEveryRoute, checkAuth]">
  <template x-route="/" x-template>...</template>
  <template x-route="/profile" x-template>...</template>
</div>

<script>
  Alpine.data('app', () => ({
    logEveryRoute(context) {
      console.log('Navigated to:', context.path)
    },
    checkAuth(context) {
      if (context.path.startsWith('/admin') && !isAuthenticated()) {
        this.$router.navigate('/login')
      }
    },
  }))
</script>
```

Set global handlers programmatically in [Settings](reference/05-settings.md) with `globalHandlers`.

## Handler Best Practices

- Use the `context` parameter for route data, not `$router.context` — the global context is not updated until handlers finish
- Always check `err.name !== 'AbortError'` in async handlers to avoid logging expected cancellations
- Return data from handlers to pass it to the next handler in the chain
- Use `controller.abort()` to prevent template rendering on errors
- Handlers bound to Alpine components have access to `this` (the component instance)
