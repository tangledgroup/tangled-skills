# Programmatic API

## Adding Routes

Add routes at any time using `PineconeRouter.add(path, options)`:

```javascript
PineconeRouter.add('/about', {
  templates: ['/views/about.html'],
  handlers: [loadAboutData],
  name: 'about-page',
})
```

### RouteOptions

| Option | Type | Description |
|--------|------|-------------|
| `handlers` | `Handler[]` | Array of handler functions |
| `templates` | `string[]` | Array of template URLs to fetch |
| `targetID` | `string` | Element ID to render templates into (overrides global) |
| `preload` | `boolean` | Preload this route's templates |
| `interpolate` | `boolean` | Replace `:param` in template URLs with route params |
| `name` | `string` | Optional name for the route |

### Programmatic Templates

As of v7.4.0, programmatically added templates are automatically created as `<template>` elements appended to the end of `<body>`. They behave identically to declarative templates — hidden on route change, shown on match.

If no `targetID` is set (globally or per-route), content renders at the bottom of the body after the created template element.

```javascript
document.addEventListener('alpine:init', () => {
  window.PineconeRouter.settings({ targetID: 'app' })

  window.PineconeRouter.add('/dynamic-page', {
    templates: ['/views/dynamic.html'],
  })

  // Override the notfound route
  window.PineconeRouter.add('notfound', {
    templates: ['/views/404.html'],
  })
})
```

Note: Handlers added this way do not have access to Alpine component `this` context.

## Removing Routes

Remove a route by its path:

```javascript
const removed = PineconeRouter.remove('/about')
// Returns true if the route existed and was removed
```

Removing a route also removes its associated template element from the DOM.

## Matching Routes Externally

Check which route matches a given path without navigating:

```javascript
const result = PineconeRouter.match('/users/42')
console.log(result.route.path)   // '/users/:id'
console.log(result.params)       // { id: '42' }
```

## Navigating from JavaScript

Use `PineconeRouter.navigate(path)` to navigate programmatically:

```javascript
// Basic navigation
window.PineconeRouter.navigate('/profile/42')

// In an Alpine component
this.$router.navigate('/settings')

// Via Alpine global
Alpine.$router.navigate('/dashboard')
```

Navigation is a promise — await it to know when handlers and templates complete:

```javascript
await window.PineconeRouter.navigate('/posts')
console.log('Navigation complete')
```

## Named Routes

Assign a name to a route for identification:

Declarative syntax with `x-route:name`:

```html
<template x-route:homepage="/"></template>
<template x-route:user-profile="/users/:id"></template>
```

Programmatic syntax:

```javascript
PineconeRouter.add('/', { name: 'homepage' })
```

Access the name in handlers:

```javascript
handler(context) {
  console.log(context.route.name) // 'homepage'
}
```

Names are optional and do not need to be unique. If no name is provided, the route path is used as the name.

## Accessing the Router Object

The PineconeRouter object is available through multiple entry points:

- `$router` — magic helper inside Alpine components
- `window.PineconeRouter` — global JavaScript access
- `Alpine.$router` — Alpine namespace access
- `PineconeRouter` — global variable (CDN builds)

### PineconeRouter Object Reference

```
PineconeRouter.name          // "pinecone-router"
PineconeRouter.version       // "7.5.0"
PineconeRouter.routes        // Map<string, Route> — all registered routes
PineconeRouter.context       // Context — current route info
PineconeRouter.history       // NavigationHistory — navigation stack
PineconeRouter.loading       // boolean — true while navigating
PineconeRouter.settings()    // Settings — read/write configuration
PineconeRouter.add(path, opts)
PineconeRouter.remove(path)
PineconeRouter.navigate(path)
PineconeRouter.match(path)
```
