# Router Primitives

All primitives read from the Router and Route context. They must be called within a route component tree.

## `useParams`

Returns a reactive store-like object with current route path parameters.

```jsx
import { useParams } from "@solidjs/router";

const params = useParams();

// Reactive access to path parameters
const userId = () => params.id;
```

Use with `createResource` for parameter-driven data fetching:

```jsx
const [user] = createResource(() => params.id, fetchUser);
```

## `useNavigate`

Returns a navigation function. Accepts a path and optional configuration.

```jsx
import { useNavigate } from "@solidjs/router";

const navigate = useNavigate();

// Navigate to a path
navigate("/users");

// With options
navigate("/login", {
  replace: true,   // Replace history entry (default: false)
  scroll: true,    // Scroll to top (default: true)
  resolve: true,   // Resolve against current route (default: true)
  state: myState   // Push to location.state
});

// History navigation
navigate(-1); // Back
navigate(1);  // Forward
```

The `state` is serialized using the structured clone algorithm — not all object types are supported.

## `useLocation`

Returns a reactive location object with current URL information.

```jsx
import { useLocation } from "@solidjs/router";

const location = useLocation();

// Reactive properties
const pathname = () => location.pathname;
const search = () => location.search;
const hash = () => location.hash;
const state = () => location.state;
const query = location.query; // Reactive search params object
```

Properties:

- `pathname` — URL path
- `search` — Query string (including `?`)
- `hash` — Hash fragment (including `#`)
- `query` — Parsed query parameters as reactive object
- `state` — History state
- `key` — Unique navigation key

## `useSearchParams`

Returns a tuple of `[params, setParams]` for reactive query string management.

```jsx
import { useSearchParams } from "@solidjs/router";

const [searchParams, setSearchParams] = useSearchParams();

// Read
const page = () => searchParams.page; // String value

// Update (merged into current query string)
setSearchParams({ page: "2" });

// Remove a key (use '', undefined, or null)
setSearchParams({ page: "" });
```

Updates behave like navigation — accepts the same second parameter as `navigate`. Auto-scrolling is disabled by default on search param updates.

Values are always strings. Property names retain their casing.

## `useIsRouting`

Returns a signal indicating whether the router is currently in a transition (Suspense/Transition active during route resolution).

```jsx
import { useIsRouting } from "@solidjs/router";

const isRouting = useIsRouting();

return (
  <div classList={{ "opacity-50": isRouting() }}>
    <MyContent />
  </div>
);
```

Useful for showing loading states during concurrent rendering.

## `useMatch`

Creates a memo that checks if a given path matches the current location. Returns match information or undefined.

```jsx
import { useMatch } from "@solidjs/router";

const match = useMatch(() => props.href);

return <div classList={{ active: Boolean(match()) }} />;
```

Accepts optional `matchFilters` as the second argument for parameter validation.

## `useCurrentMatches`

Returns all route matches for the current location. Useful for building breadcrumbs or accessing route metadata.

```jsx
import { useCurrentMatches } from "@solidjs/router";

const matches = useCurrentMatches();

const breadcrumbs = createMemo(() =>
  matches().map((m) => m.route.info.breadcrumb)
);
```

Each match contains `params`, `path`, and `route` (with `info`, `component`, `preload`).

## `usePreloadRoute`

Returns a function to manually preload a route. This is what happens automatically on link hover, exposed as an API.

```jsx
import { usePreloadRoute } from "@solidjs/router";

const preload = usePreloadRoute();

// Preload route and its data
preload("/users/settings", { preloadData: true });

// Preload route component only
preload("/users/settings", { preloadData: false });
```

## `useBeforeLeave`

Registers a handler called before leaving the current route. Useful for unsaved changes confirmation.

```jsx
import { useBeforeLeave } from "@solidjs/router";

useBeforeLeave((e) => {
  if (form.isDirty && !e.defaultPrevented) {
    e.preventDefault(); // Block the navigation

    setTimeout(() => {
      if (window.confirm("Discard unsaved changes?")) {
        e.retry(true); // Retry with force=true to skip handlers again
      }
    }, 100);
  }
});
```

Event arguments:

- `from` — Current location (before change)
- `to` — Target path or history delta
- `options` — Navigate options passed to `navigate`
- `defaultPrevented` — Whether a previous handler called `preventDefault`
- `preventDefault()` — Block the route change
- `retry(force?)` — Retry the same navigation. Pass `true` to skip leave handlers again.

## `useHref`

Resolves a path against the current route and applies the router's render function (e.g., adding `#` for HashRouter).

```jsx
import { useHref } from "@solidjs/router";

const href = useHref(() => "/users");
```

## `useResolvedPath`

Returns a memo with the path resolved against the current route context.

```jsx
import { useResolvedPath } from "@solidjs/router";

const resolved = useResolvedPath(() => "../edit");
```
