# Components Reference

## `<Router>`

The main router component for browser environments. Automatically uses `StaticRouter` on the server.

Props:

- `children` — Route definitions as `<Route>` JSX or `RouteDefinition` objects
- `root` — Top-level layout component wrapping all routes
- `base` — Base URL prefix for route matching
- `actionBase` — Root URL for server actions (default: `/_server`)
- `preload` — Enable/disable preloads globally (default: `true`)
- `explicitLinks` — When `true`, only `<A>` components are intercepted; plain `<a>` tags trigger full page navigation. Default: `false`.
- `singleFlight` — Enable/disable single-flight mutations (default: `true`)
- `transformUrl` — Function to rewrite URLs before matching

## `<A>`

Router-aware anchor tag. Like `<a>` but with base path resolution, relative paths, and active class styling.

Props:

- `href` — Route path (resolved relative to current route; prefix with `/` for absolute)
- `noScroll` — Disable auto-scroll to top on navigation
- `replace` — Replace history entry instead of pushing (default: `false`)
- `state` — Value pushed to `location.state` via `pushState`
- `inactiveClass` — Class when link does not match current location (default: `"inactive"`)
- `activeClass` — Class when link matches (default: `"active"`)
- `end` — When `true`, only exact match activates the link. When `false` (default), descendant paths also activate (e.g., `href="/users"` is active at `/users/123`).

Active matching includes descendants by default. Use `end` for links to root `/` which would otherwise match everything:

```jsx
<A href="/" end>Home</A>
```

## `<Navigate />`

Immediately navigates to a path when rendered. Useful for redirects from within route components.

Props:

- `href` — Path string or function `(args) => string`
- `state` — Custom state for the navigation

The function form receives `{ navigate, location }`:

```jsx
function getPath({ navigate, location }) {
  return "/some-path";
}

<Route path="/redirect" component={() => <Navigate href={getPath} />} />;
```

## `<Route>`

Defines a route segment.

Props:

- `path` — Path pattern string (supports `:param`, `:param?`, `*wildcard`)
- `component` — Component to render when matched
- `matchFilters` — Parameter validation constraints
- `children` — Nested `<Route>` definitions
- `preload` — Preload function called during route load or link hover

Only leaf `<Route>` nodes (without children) become navigable routes. Parent routes with children act as layout wrappers via `props.children`.
