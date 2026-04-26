# TypeScript Types

Pinecone Router provides full TypeScript definitions via `dist/types.d.ts`.

## Core Types

### Handler

```typescript
export type Handler<In, Out> = (
  context: HandlerContext<In>,
  controller: AbortController
) => Out | Promise<Out>
```

`In` is the value returned by the previous handler (available as `context.data`). `Out` is the return value passed to the next handler.

### HandlerContext

```typescript
export interface HandlerContext<T = unknown> extends Context {
  readonly data: T
  readonly route: Route
}
```

Extended context passed to handlers, adding `data` (from previous handler) and guaranteed `route`.

### Context

```typescript
export interface Context {
  readonly path: string
  readonly route?: Route
  readonly params: Record<string, string | undefined>
}
```

Global context accessible via `$router.context`, `PineconeRouter.context`, or the first argument to handlers.

### Route

```typescript
export interface Route {
  readonly pattern: RegExp
  readonly path: string
  readonly name: string
  match(path: string): undefined | { [key: string]: string }
  handlers: Handler<unknown, unknown>[]
  templates: string[]
}
```

### RouteOptions

```typescript
export interface RouteOptions {
  handlers?: Route['handlers']
  interpolate?: boolean
  templates?: string[]
  targetID?: string
  preload?: boolean
  name?: string
}
```

### Settings

```typescript
export interface Settings {
  hash: boolean
  basePath: string
  targetID?: string
  handleClicks: boolean
  globalHandlers: Handler<unknown, unknown>[]
  preload: boolean
  fetchOptions: RequestInit
  pushState: boolean
}
```

### NavigationHistory

```typescript
export interface NavigationHistory {
  index: number
  entries: string[]
  canGoBack(): boolean
  back(): void
  canGoForward(): boolean
  forward(): void
  to(index: number): void
}
```

### PineconeRouter

```typescript
export interface PineconeRouter {
  readonly name: string
  readonly version: string
  routes: RoutesMap
  context: Context
  settings: (value?: Partial<Settings>) => Settings
  history: NavigationHistory
  loading: boolean
  add(path: string, options: RouteOptions): void
  remove(path: string): boolean
  navigate(path: string): Promise<void>
  match(path: string): { route: Route; params: Context['params'] }
}

export type RoutesMap = Map<string, Route> & {
  get(key: 'notfound'): Route
}
```

## Alpine.js Module Augmentation

Pinecone Router augments the Alpine.js types to register magic helpers:

```typescript
declare module 'alpinejs' {
  interface Magics<T> {
    $router: PineconeRouter
    $history: NavigationHistory
    $params: Context['params']
  }

  interface Alpine {
    $router: PineconeRouter
  }
}
```

## Usage with TypeScript

```typescript
import PineconeRouter from 'pinecone-router'
import Alpine from 'alpinejs'

Alpine.plugin(PineconeRouter)

// Type-safe handler
const authHandler: Handler<unknown, void> = (context, controller) => {
  if (context.path.startsWith('/admin') && !isAuthenticated()) {
    // Access $router via Alpine global for redirects outside component context
    window.PineconeRouter.navigate('/login')
  }
}

// Configure with types
PineconeRouter.settings({
  targetID: 'app',
  basePath: '/app',
  globalHandlers: [authHandler],
})

// Type-safe navigation
await PineconeRouter.navigate('/profile/42')

// Type-safe route matching
const { route, params } = PineconeRouter.match('/users/123')
```
