# Routing Modes

Solid Router provides four routing modes for different environments and deployment scenarios.

## History Router (`Router`)

The default router uses the browser's History API (`pushState` / `replaceState`) for standard URL-based navigation. This is the recommended mode for most applications.

```jsx
import { render } from "solid-js/web";
import { Router } from "@solidjs/router";

render(() => <Router />, document.getElementById("app"));
```

**Props:**

- `base` — Base URL prefix for matching routes (e.g., `/app`)
- `root` — Top-level layout component wrapping all routes
- `rootPreload` — Preload function for the root layout
- `actionBase` — Root URL for server actions, default: `/_server`
- `preload` — Enable/disable preloads globally (default: `true`)
- `explicitLinks` — When `true`, disables all anchor interception; only `<A>` components are handled by the router. Default: `false`. To disable interception for a specific plain link, set `target` to any value (e.g., `<a target="_self">`).
- `singleFlight` — Enable/disable single-flight mutations (default: `true`)
- `transformUrl` — Function to rewrite URLs before matching

### SPA Deployment

When deploying client-side routed SPAs without SSR, configure your server to fallback to `index.html`:

**Netlify** — `_redirects` file:
```
/*   /index.html   200
```

**Vercel** — `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

## Hash Router (`HashRouter`)

Uses the URL hash fragment (`#`) for routing. Useful when you cannot configure server-side redirects or need to support environments where History API is unavailable.

```jsx
import { HashRouter } from "@solidjs/router";

<HashRouter />;
```

HashRouter renders paths with a `#` prefix and parses paths from the hash. It listens to the `hashchange` event instead of `popstate`. URLs look like `example.com/#/users/123`.

## Static Router (`StaticRouter`)

Used for server-side rendering. Takes a URL string and renders the matching route tree without browser history management. The `<Router>` component automatically falls back to `StaticRouter` on the server.

```jsx
import { isServer } from "solid-js/web";
import { Router } from "@solidjs/router";

<Router url={isServer ? req.url : ""} />;
```

The StaticRouter reads from the `getRequestEvent()` if no URL is provided. It supports the `RequestEvent.router` extension for SSR data, matches, and submission state.

## Memory Router (`MemoryRouter`)

Maintains an in-memory history stack. Useful for testing and non-browser environments.

```jsx
import { MemoryRouter, createMemoryHistory } from "@solidjs/router";

// Default usage
<MemoryRouter />;

// With custom history
const history = createMemoryHistory();
<MemoryRouter history={history} />;
```

`createMemoryHistory` returns an object with:

- `get()` — Current URL string
- `set(change)` — Push or replace a location change
- `go(delta)` — Navigate forward/backward in history
- `back()` / `forward()` — Convenience methods
- `listen(callback)` — Subscribe to history changes

## Router Internals

All routers are built on `createRouter`, which accepts a `RouterIntegration`:

```ts
interface RouterIntegration {
  signal: Signal<LocationChange>;
  create?: (router: RouterContext) => void;
  utils?: Partial<RouterUtils>;
}

interface RouterUtils {
  renderPath(path: string): string;
  parsePath(str: string): string;
  go(delta: number): void;
  beforeLeave: BeforeLeaveLifecycle;
  paramsWrapper: (getParams, branches) => Params;
  queryWrapper: (getQuery) => SearchParams;
}
```

Each router mode provides its own integration — History Router uses `window.history`, Hash Router uses `window.location.hash`, Static Router uses a fixed signal, and Memory Router uses an in-memory stack.
