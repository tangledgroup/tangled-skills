# Route Patterns

## Dynamic Parameters

Use `:paramName` to capture a URL segment as a parameter. Access it via `useParams()` or `props.params`.

```jsx
<Route path="/users/:id" component={User} />
```

For `/users/42`, `params.id` is `"42"`.

**Animation note**: Routes sharing the same path match are treated as the same route. To force re-render when a parameter changes, wrap in a keyed `<Show>`:

```jsx
<Show when={params.something} keyed>
  <MyComponent />
</Show>
```

## Optional Parameters

Append `?` to make a parameter optional:

```jsx
<Route path="/stories/:id?" component={Stories} />
```

Matches both `/stories` and `/stories/123`.

## Wildcard Routes

Use `*` to match any remaining path segments:

```jsx
// Matches foo/, foo/a, foo/a/b/c
<Route path="foo/*" component={Foo} />
```

Name the wildcard to expose it as a parameter:

```jsx
<Route path="foo/*any" component={Foo} />
```

The wildcard token must be the last part of the path. `foo/*any/bar` does not create valid routes.

For catch-all 404 pages, use `*404` or `*all`:

```jsx
<Route path="*404" component={NotFound} />
```

## Multiple Paths

Define multiple paths for a single route using an array. The route remains mounted when switching between matched locations:

```jsx
<Route path={["login", "register"]} component={AuthForm} />
```

Navigating from `/login` to `/register` does not cause the component to re-render.

## Match Filters

Validate path parameters with `matchFilters`. Each filter can be an enum array, RegExp, or custom function:

```jsx
import type { MatchFilters } from "@solidjs/router";

const filters: MatchFilters = {
  parent: ["mom", "dad"],          // enum values
  id: /^\d+$/,                     // regex
  ext: (v) => v.endsWith(".html"), // custom function
};

<Route
  path="/users/:parent/:id/:ext"
  component={User}
  matchFilters={filters}
/>;
```

If validation fails, the route does not match.

## Nested Routes

Routes can be nested in two equivalent ways:

```jsx
// Flat syntax
<Route path="/users/:id" component={User} />

// Nested syntax
<Route path="/users">
  <Route path="/:id" component={User} />
</Route>
```

**Important**: Only leaf `<Route>` nodes (innermost routes without children) become navigable routes. If you want the parent to also be a route, define it separately:

```jsx
// This does NOT make /users its own route
<Route path="/users" component={Users}>
  <Route path="/:id" component={User} />
</Route>

// Correct: define both
<Route path="/users" component={Users} />
<Route path="/users/:id" component={User} />

// Or use nested with explicit leaf
<Route path="/users">
  <Route path="/" component={Users} />
  <Route path="/:id" component={User} />
</Route>
```

### Nested Layouts with `props.children`

Parent routes render their matched output where `props.children` is placed:

```jsx
function PageWrapper(props) {
  return (
    <div>
      <h1>We love our users!</h1>
      {props.children}
      <A href="/">Back Home</A>
    </div>
  );
}

<Route path="/users" component={PageWrapper}>
  <Route path="/" component={Users} />
  <Route path="/:id" component={User} />
</Route>
```

Nesting is indefinite — each level wraps the next via `props.children`.

## Preload Functions

Preload functions start data fetching parallel to route loading. They are called when the route loads or eagerly on link hover.

```jsx
function preloadUser({ params, location, intent }) {
  // params: same as useParams()
  // location: { pathname, search, hash, query, state, key }
  // intent: "initial" | "navigate" | "native" | "preload"
  return fetch(`/api/users/${params.id}`).then(r => r.json());
}

<Route path="/users/:id" component={User} preload={preloadUser} />;
```

Intent values:

- `"initial"` — Route is being initially shown (page load)
- `"native"` — Navigation from browser (back/forward)
- `"navigate"` — Navigation from router (`<A>` click or `navigate()`)
- `"preload"` — Not navigating, just preloading (link hover)

Common pattern: export preload in a dedicated `.data.js` file so it can be imported without loading the route component.

## RouteSectionProps

Every route component receives:

```ts
interface RouteSectionProps<T = unknown> {
  params: Params;        // Path parameters
  location: Location;    // Current location
  data: T;              // Return value from preload function
  children?: JSX.Element; // Nested route output
}
```

## RouteDefinition (Object Syntax)

Routes can be defined as plain objects for config-based routing:

```ts
type RouteDefinition<S extends string | string[] = any, T = unknown> = {
  path?: S;
  matchFilters?: MatchFilters<S>;
  preload?: RoutePreloadFunc<T>;
  children?: RouteDefinition | RouteDefinition[];
  component?: Component<RouteSectionProps<T>>;
  info?: Record<string, any>;
};
```

The `info` field stores arbitrary metadata accessible via `useCurrentMatches()`.
