# Settings

## Configuring the Router

Settings are managed through `PineconeRouter.settings()`, which both reads and writes configuration:

```javascript
// Set settings
PineconeRouter.settings({
  targetID: 'app',
  basePath: '/blog',
})

// Read current settings
const current = PineconeRouter.settings()
console.log(current.basePath) // '/blog'
```

In Alpine templates, use `$router.settings()`:

```html
<div x-data="app" x-init="$router.settings({ targetID: 'app' })"></div>
```

Configure during `alpine:init`:

```javascript
document.addEventListener('alpine:init', () => {
  window.PineconeRouter.settings({
    basePath: '/app',
    targetID: 'app',
  })
})
```

## Settings Reference

### `hash` (boolean, default: `false`)

Enable hash-based routing (`#/path` instead of `/path`):

```javascript
PineconeRouter.settings({ hash: true })
// Routes use #/about, #/profile/42 etc.
```

When enabled with `basePath`, the base path is added to template URLs but not to the hash pathname.

### `basePath` (string, default: `''`)

Prefix for all routes and template URLs. Set once and omit it from route declarations:

```javascript
PineconeRouter.settings({ basePath: '/blog' })
```

Now write `x-route="/about"` instead of `x-route="/blog/about"`, and `x-template="/views/home.html"` instead of `x-template="/blog/views/home.html"`. The base path is automatically prepended to route matching, navigation calls, and template fetch URLs.

### `targetID` (string | undefined, default: `undefined`)

Default element ID for rendering templates. Overrides the need for `.target` on every route:

```javascript
PineconeRouter.settings({ targetID: 'app' })
<!-- All templates render inside <div id="app"> by default -->
```

Per-route `.target` modifier overrides this global setting.

### `handleClicks` (boolean, default: `true`)

Whether to intercept anchor link clicks automatically:

- `true` (default): All internal `<a>` links use router navigation
- `false`: Links cause full page reload unless they have the `x-link` attribute

When disabled, add `x-link` to anchors you want routed:

```html
<a href="/path">Reloads the page</a>
<a href="/path" x-link>Uses router navigation</a>
```

To exclude individual links when clicks are enabled, add `native` or `data-native`:

```html
<a href="/foo" native>This reloads the page</a>
```

### `globalHandlers` (Handler\[\], default: `[]`)

Array of handler functions that run on every route, before route-specific handlers:

```javascript
PineconeRouter.settings({
  globalHandlers: [
    (ctx) => console.log('Route:', ctx.path),
    async (ctx, controller) => {
      // Auth check on every navigation
      if (ctx.path.startsWith('/admin') && !isAuthenticated()) {
        window.PineconeRouter.navigate('/login')
      }
    },
  ],
})
```

### `preload` (boolean, default: `false`)

Preload all external templates at low priority after the first page loads:

```javascript
PineconeRouter.settings({ preload: true })
```

Per-route `.preload` modifier takes precedence over this global setting.

### `fetchOptions` (RequestInit, default: `{}`)

Options passed to every template fetch request (excluding `priority` which is managed by the router):

```javascript
PineconeRouter.settings({
  fetchOptions: {
    headers: { 'X-Requested-With': 'Pinecone' },
    credentials: 'same-origin',
  },
})
```

### `pushState` (boolean, default: `true`)

Whether to call `history.pushState()` on navigation. When `false`, the URL does not change but internal [Navigation History](reference/04-navigation-history.md) still tracks paths:

```javascript
PineconeRouter.settings({ pushState: false })
// Navigation works, $history.back() works, but URL stays the same
```

## Events

Pinecone Router dispatches custom events on `document`:

- **`pinecone:start`** — Loading starts (before handlers execute)
- **`pinecone:end`** — Loading ends (after handlers and templates complete)
- **`pinecone:fetch-error`** — External template fetch failed (detail contains `{ error, url }`)

```javascript
document.addEventListener('pinecone:start', () => {
  document.body.classList.add('loading')
})
document.addEventListener('pinecone:end', () => {
  document.body.classList.remove('loading')
})
document.addEventListener('pinecone:fetch-error', (e) => {
  console.error('Template fetch failed:', e.detail.url, e.detail.error)
})
```

Check reactive loading state in templates:

```html
<div x-show="$router.loading">Loading...</div>
```
