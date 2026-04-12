# Pinecone Router 7.5 API Reference

Complete TypeScript API reference for Pinecone Router v7.5, including all objects, interfaces, settings, and programmatic methods.

## PineconeRouter Object

Main router instance accessible via multiple methods:

### Access Methods

```javascript
// From Alpine component (magic helper)
this.$router

// From global JavaScript
window.PineconeRouter

// From Alpine global
Alpine.$router
```

### Properties

```typescript
interface PineconeRouter {
  readonly name: string        // "PineconeRouter"
  readonly version: string     // "7.5.0"
  
  routes: RoutesMap            // Map of all registered routes
  context: Context             // Current route context
  history: NavigationHistory   // Navigation history
  
  loading: boolean             // True while navigation/handlers running
  
  settings: (value?: Partial<Settings>) => Settings  // Get/set settings
}
```

### Methods

#### `add(path, options)`

Add a route programmatically:

```typescript
add(path: string, options: RouteOptions): void
```

**Example:**
```javascript
window.PineconeRouter.add('/dynamic-route', {
  name: 'dynamic-page',
  templates: ['/dynamic.html'],
  handlers: [myHandler],
  targetID: 'app',
  preload: true,
  interpolate: false
})
```

**Notes:**
- As of v7.4.0, programmatic routes create template elements appended to `<body>`
- Templates function identically to declarative `x-template` routes
- `notfound` route can be overridden (only exception to "route exists" error)

#### `remove(path)`

Remove a route:

```typescript
remove(path: string): void
```

**Example:**
```javascript
window.PineconeRouter.remove('/temporary-route')
```

**Notes:**
- Removes route and associated templates
- Template elements are removed from DOM
- Cannot remove `notfound` route (must use `add` to override instead)

#### `navigate(path, fromPopState, firstLoad, index)`

Navigate to a path:

```typescript
navigate(
  path: string,
  fromPopState?: boolean,   // Internal: true from popstate event
  firstLoad?: boolean,      // Internal: true on browser page load
  index?: number            // Internal: history index being navigated to
): Promise<void>
```

**Example:**
```javascript
// Basic navigation (returns promise)
await window.PineconeRouter.navigate('/about')

// Navigation with error handling
try {
  await window.PineconeRouter.navigate('/expensive-route')
  console.log('Navigation completed')
} catch (error) {
  console.error('Navigation failed:', error)
}
```

**Notes:**
- Returns promise that resolves when handlers complete
- Cancels any ongoing navigation/handlers
- Updates browser history (if `pushState` enabled)
- Adds path to navigation history (unless redirect)

#### `match(path)`

Check if path matches a route without navigating:

```typescript
match(path: string): { route: Route; params: Record<string, string | undefined> }
```

**Example:**
```javascript
const result = window.PineconeRouter.match('/users/john')

if (result.route) {
  console.log('Matched:', result.route.path)     // "/users/:username"
  console.log('Params:', result.params)          // { username: "john" }
} else {
  console.log('No matching route')
}
```

**Returns:**
- `{ route: Route, params: {...} }` if matched
- `{ route: undefined, params: {} }` if no match

## Settings Object

Configure router behavior via `PineconeRouter.settings()`:

### Get Settings

```javascript
const currentSettings = window.PineconeRouter.settings()
console.log(currentSettings.hash)  // false
```

### Set Settings

```javascript
window.PineconeRouter.settings({
  hash: true,
  targetID: 'app'
})
```

Returns updated settings object.

### Settings Properties

```typescript
interface Settings {
  /**
   * Enable hash routing (URLs become example.com/#/path)
   * @default false
   */
  hash: boolean

  /**
   * Base path prepended to routes and template URLs
   * @default ''
   */
  basePath: string

  /**
   * Default target element ID for template rendering
   * Override with .target modifier on individual routes
   * @default undefined
   */
  targetID?: string

  /**
   * Automatically intercept anchor tag clicks
   * When false, only links with x-link attribute are intercepted
   * @default true
   */
  handleClicks: boolean

  /**
   * Handlers that run on every route match
   * Execute before route-specific handlers
   * @default []
   */
  globalHandlers: Handler<unknown, unknown>[]

  /**
   * Preload all templates after initial page load
   * Individual routes can override with .preload modifier
   * @default false
   */
  preload: boolean

  /**
   * Fetch options for template requests (excluding priority)
   * Passed as second argument to fetch()
   * @default {}
   */
  fetchOptions: RequestInit

  /**
   * Enable browser history.pushState() calls
   * When false, URL doesn't change on navigation
   * @default true
   */
  pushState: boolean
}
```

### Configuration Examples

#### Hash Routing for Static Hosting

```javascript
window.PineconeRouter.settings({
  hash: true
})
// URLs: example.com/#/about instead of example.com/about
```

#### Subdirectory Deployment

```javascript
window.PineconeRouter.settings({
  basePath: '/myapp'
})
// Routes: /about → /myapp/about
// Templates: /home.html → /myapp/home.html
```

#### Global Authentication Handler

```javascript
window.PineconeRouter.settings({
  globalHandlers: [
    (context, controller) => {
      const publicRoutes = ['/', '/login', '/register']
      if (!publicRoutes.includes(context.path) && !isLoggedIn()) {
        window.PineconeRouter.navigate('/login')
      }
    }
  ]
})
```

#### Custom Fetch Options

```javascript
window.PineconeRouter.settings({
  fetchOptions: {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'X-Custom-Header': 'value'
    },
    credentials: 'include',
    cache: 'no-cache'
  }
})
```

#### Preload All Templates

```javascript
window.PineconeRouter.settings({
  preload: true,
  fetchOptions: {
    priority: 'low'  // Preload doesn't block initial page
  }
})
```

## Context Object

Current route information, always up-to-date:

### Properties

```typescript
interface Context {
  /**
   * Current path (e.g., "/users/john")
   */
  readonly path: string

  /**
   * Matched route object (undefined if no match)
   */
  readonly route?: Route

  /**
   * Route parameters as key-value pairs
   */
  readonly params: Record<string, string | undefined>
}
```

### Access Methods

```javascript
// From Alpine component
$router.context.path
$router.context.route
$router.context.params

// From global JavaScript
window.PineconeRouter.context.path

// From handlers (use provided context parameter)
function handler(context, controller) {
  context.path
  context.route
  context.params
}
```

### Usage Example

```html
<div x-data="{ }">
  <p>Path: <span x-text="$router.context.path"></span></p>
  <p>Route: <span x-text="$router.context.route?.path || 'N/A'"></span></p>
  <p>Params: <span x-text="JSON.stringify($router.context.params)"></span></p>
</div>
```

## Route Object

Represents a registered route:

### Properties

```typescript
interface Route {
  /**
   * Regex pattern used for matching (internal)
   */
  readonly pattern: RegExp

  /**
   * Raw route path pattern (e.g., "/users/:username")
   */
  readonly path: string

  /**
   * Route name (falls back to path if not specified)
   */
  readonly name: string

  /**
   * Handler functions for this route
   */
  handlers: Handler<unknown, unknown>[]

  /**
   * Template URLs for this route
   */
  templates: string[]

  /**
   * Match a path against this route
   * @returns Parameter object or undefined
   */
  match(path: string): undefined | { [key: string]: string }
}
```

### Route Options

Options for programmatic route creation:

```typescript
interface RouteOptions {
  /**
   * Handler functions (array or single function)
   */
  handlers?: Handler<unknown, unknown>[]

  /**
   * Enable parameter interpolation in template URLs
   */
  interpolate?: boolean

  /**
   * Template URL(s) to fetch
   */
  templates?: string[]

  /**
   * Target element ID for rendering
   */
  targetID?: string

  /**
   * Preload this route's templates
   */
  preload?: boolean

  /**
   * Custom route name
   */
  name?: string
}
```

### Usage Example

```javascript
const route: Route = {
  path: '/users/:username',
  pattern: /^\/users\/(?<username>[^/]+?)\/?$/i,
  name: 'user-profile',
  handlers: [loadUser, renderProfile],
  templates: ['/templates/user-profile.html'],
  
  match(path) {
    // Returns { username: 'john' } for '/users/john'
  }
}
```

## NavigationHistory Object

Tracks navigation history independently from browser:

### Properties

```typescript
interface NavigationHistory {
  /**
   * Current position in history (0-indexed)
   */
  index: number

  /**
   * Array of visited paths (duplicates filtered)
   */
  entries: string[]

  /**
   * Check if back navigation is possible
   */
  canGoBack(): boolean

  /**
   * Navigate to previous entry
   */
  back(): void

  /**
   * Check if forward navigation is possible
   */
  canGoForward(): boolean

  /**
   * Navigate to next entry
   */
  forward(): void

  /**
   * Navigate to specific index
   */
  to(index: number): void
}
```

### Access Methods

```javascript
// From Alpine component (magic helper)
$history.entries
$history.index
$history.back()
$history.canGoBack()

// From global JavaScript
window.PineconeRouter.history.entries
window.PineconeRouter.history.back()
```

### Usage Example

```html
<div x-data="{ }">
  <nav>
    <button @click="$history.back()" :disabled="!$history.canGoBack()">
      Back (<span x-text="$history.index"></span>)
    </button>
    
    <button @click="$history.forward()" :disabled="!$history.canGoForward()">
      Forward
    </button>
  </nav>
  
  <ol>
    <template x-for="(entry, i) in $history.entries" :key="i">
      <li :class="{ active: i === $history.index }" x-text="entry"></li>
    </template>
  </ol>
</div>
```

## Handler Type

Type definition for route handlers:

### Type Signature

```typescript
type Handler<In, Out> = (
  context: HandlerContext<In>,
  controller: AbortController
) => Out | Promise<Out>
```

**Type parameters:**
- `In`: Data type from previous handler (via `context.data`)
- `Out`: Return type passed to next handler

### HandlerContext Interface

```typescript
interface HandlerContext<T = unknown> extends Context {
  /**
   * Data returned by previous handler
   */
  readonly data: T

  /**
   * Matched route object
   */
  readonly route: Route
}
```

Note: `HandlerContext` extends `Context`, so it also includes `path`, `route`, and `params`.

### Handler Examples

#### Synchronous Handler

```typescript
const syncHandler: Handler<unknown, void> = (context, controller) => {
  console.log('Sync handler:', context.path)
  // Returns undefined implicitly
}
```

#### Async Handler Returning Data

```typescript
async function fetchData(
  context: HandlerContext<unknown>,
  controller: AbortController
): Promise<UserData> {
  const response = await fetch(`/api/user/${context.params.id}`, {
    signal: controller.signal
  })
  return response.json()
}
```

#### Handler Receiving Data

```typescript
function processData(
  context: HandlerContext<UserData>,  // Receives UserData from previous handler
  controller: AbortController
): void {
  const user = context.data  // Type: UserData
  console.log('Processing user:', user.name)
}
```

## RoutesMap Type

Map of all registered routes:

```typescript
type RoutesMap = Map<string, Route> & {
  get(key: 'notfound'): Route
}
```

### Usage

```javascript
// Iterate all routes
for (const [path, route] of window.PineconeRouter.routes) {
  console.log(path, '→', route.path)
}

// Get specific route
const homeRoute = window.PineconeRouter.routes.get('/')

// Notfound route always exists
const notfoundRoute = window.PineconeRouter.routes.get('notfound')
```

## Magic Helpers

Alpine.js magic helpers provided by Pinecone Router:

### `$router`

Full PineconeRouter object:

```html
<div x-data="{ }">
  <button @click="$router.navigate('/about')">Go to About</button>
  <p>Version: <span x-text="$router.version"></span></p>
  <p>Loading: <span x-text="$router.loading"></span></p>
</div>
```

### `$history`

NavigationHistory object:

```html
<div x-data="{ }">
  <button @click="$history.back()" :disabled="!$history.canGoBack()">Back</button>
  <p>Visited: <span x-text="$history.entries.length"></span> pages</p>
</div>
```

### `$params`

Route parameters object:

```html
<template x-route="/user/:username" x-template>
  <div x-data="{ }">
    <h1>User: <span x-text="$params.username"></span></h1>
  </div>
</template>
```

## Directives

### `x-route`

Declare a route on template elements:

```html
<template x-route="/path-pattern"></template>
```

**Modifiers:**
- `:name`: Assign custom name to route
  ```html
  <template x-route:name="homepage" x-route="/"></template>
  ```

### `x-template`

Specify template content for a route:

```html
<!-- Inline template -->
<template x-route="/" x-template>
  <h1>Home</h1>
</template>

<!-- External template -->
<template x-route="/about" x-template="/about.html"></template>

<!-- Multiple templates -->
<template x-route="/" x-template="['/header.html', '/home.html']"></template>
```

**Modifiers:**
- `.target.id`: Render into element with specified ID
  ```html
  <template x-route="/" x-template.target.app>Content</template>
  ```
- `.preload`: Fetch template after initial page load
  ```html
  <template x-route="/about" x-template.preload="/about.html"></template>
  ```
- `.interpolate`: Replace route params in URL
  ```html
  <template x-route="/docs/:page" x-template.interpolate="/docs/:page.html"></template>
  ```

### `x-handler`

Specify handler functions for a route:

```html
<!-- Single handler -->
<template x-route="/about" x-handler="showAbout"></template>

<!-- Multiple handlers -->
<template x-route="/post/:id" x-handler="[checkAuth, loadPost, trackView]"></template>

<!-- Anonymous function -->
<template x-route="/redirect" x-handler="(ctx) => $router.navigate('/')"></template>
```

**Modifiers:**
- `.global`: Run handler on every route
  ```html
  <div x-data="router()" x-handler.global="[logRoute, checkAuth]"></div>
  ```

### `x-run` (v7.5+)

Control embedded script execution:

```html
<!-- Run once per route -->
<script x-run.once>
  initializeChartLibrary()
</script>

<!-- Run once globally (by ID) -->
<script x-run.once id="analytics-init">
  initAnalytics()
</script>

<!-- Conditional execution -->
<script x-run:on="$router.context.route === '/admin'">
  initializeAdminTools()
</script>

<!-- Combined -->
<script x-run.once:on="$params.role === 'admin'">
  setupAdminFeatures()
</script>
```

## Events

Custom events dispatched by Pinecone Router:

### `pinecone:start`

Dispatched when navigation/loading begins:

```javascript
document.addEventListener('pinecone:start', () => {
  NProgress.start()
})
```

### `pinecone:end`

Dispatched when navigation/loading completes:

```javascript
document.addEventListener('pinecone:end', () => {
  NProgress.done()
})
```

### `pinecone:fetch-error`

Dispatched when template fetch fails:

```javascript
document.addEventListener('pinecone:fetch-error', (event) => {
  console.error('Fetch error:', event.detail)
  // event.detail contains error information
})
```

## Alpine.js Type Extensions

Pinecone Router extends Alpine.js types:

### XAttributes Extension

```typescript
declare module 'alpinejs' {
  interface XAttributes {
    _x_PineconeRouter_undoTemplate: () => void
    _x_PineconeRouter_template?: HTMLElement[]
    _x_PineconeRouter_templateUrls?: string[]
    _x_PineconeRouter_route: string
  }
}
```

### Magics Extension

```typescript
declare module 'alpinejs' {
  interface Magics<T> {
    $router: PineconeRouter
    $history: NavigationHistory
    $params: Context['params']
  }
}
```

### Alpine Extension

```typescript
declare module 'alpinejs' {
  interface Alpine {
    $router: PineconeRouter
  }
}
```

## Window Extension

```typescript
declare global {
  interface Window {
    PineconeRouter: PineconeRouter
    Alpine: Alpine
  }
}
```

## Constants and Defaults

### Default Settings

```javascript
{
  hash: false,
  basePath: '',
  targetID: undefined,
  handleClicks: true,
  globalHandlers: [],
  preload: false,
  fetchOptions: {},
  pushState: true
}
```

### Version Information

```javascript
window.PineconeRouter.name    // "PineconeRouter"
window.PineconeRouter.version // "7.5.0"
```

## Export Summary

All types can be imported from pinecone-router:

```typescript
import type {
  Handler,
  HandlerContext,
  Context,
  Route,
  RouteOptions,
  MatchResult,
  PineconeRouter,
  RoutesMap,
  NavigationHistory,
  Settings,
  RouteTemplate
} from 'pinecone-router'

// Default export is the plugin itself
import PineconeRouterPlugin from 'pinecone-router'

Alpine.plugin(PineconeRouterPlugin)
```

## Complete Type Hierarchy

```
PineconeRouter (main instance)
├── settings: Settings
├── context: Context
│   ├── path: string
│   ├── route?: Route
│   └── params: Record<string, string | undefined>
├── history: NavigationHistory
│   ├── index: number
│   ├── entries: string[]
│   ├── canGoBack(): boolean
│   ├── back(): void
│   ├── canGoForward(): boolean
│   ├── forward(): void
│   └── to(index: number): void
├── routes: RoutesMap (Map<string, Route>)
│   └── Route
│       ├── pattern: RegExp
│       ├── path: string
│       ├── name: string
│       ├── handlers: Handler[]
│       ├── templates: string[]
│       └── match(path): MatchResult
└── loading: boolean

Handler<In, Out>(context: HandlerContext<In>, controller: AbortController) → Out | Promise<Out>
└── HandlerContext<T>
    ├── data: T (from previous handler)
    └── extends Context (path, route, params)
```
