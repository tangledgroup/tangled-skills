# Solid Router Core Concepts

This reference covers fundamental routing patterns, dynamic routes, nested routes, and navigation components in Solid Router v0.16.

## Route Configuration

### JSX-Based Routes (Recommended)

Define routes as child components of `<Router>`:

```jsx
import { Router, Route } from "@solidjs/router";

<Router root={App}>
  <Route path="/" component={Home} />
  <Route path="/users" component={Users} />
  <Route path="/about" component={About} />
</Router>
```

### Route Props

| Prop | Type | Description |
|------|------|-------------|
| `path` | string | Path pattern for the route (e.g., `/users/:id`) |
| `component` | Component | Component to render when route matches |
| `matchFilters` | MatchFilters | Validation constraints for parameters |
| `children` | JSX.Element | Nested Route definitions |
| `preload` | RoutePreloadFunc | Function called during preload/navigation |

### Router Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | JSX.Element \| RouteDefinition\[] | - | Route definitions |
| `root` | Component | - | Top-level layout component |
| `base` | string | "" | Base URL for route matching |
| `actionBase` | string | "/_server" | Root URL for server actions |
| `preload` | boolean | true | Enable/disable preloads globally |
| `explicitLinks` | boolean | false | Require `<A>` component for all links |

## Dynamic Routes

### Path Parameters

Use colon notation to define dynamic segments:

```jsx
<Route path="/users/:id" component={User} />
<Route path="/posts/:slug/comments/:commentId" component={Comment} />
```

Access parameters with `useParams()`:

```jsx
import { useParams } from "@solidjs/router";

function User() {
  const params = useParams();
  // params.id, params.slug, etc.
  return <h1>User: {params.id}</h1>;
}
```

### Optional Parameters

Add `?` to make a parameter optional:

```jsx
// Matches /stories and /stories/123 but not /stories/123/comments
<Route path="/stories/:id?" component={Stories} />
```

### Wildcard Routes

Use `*` to match remaining path segments:

```jsx
// Matches any path starting with /foo
<Route path="/foo/*" component={Foo} />

// Capture the wildcard segment
<Route path="/foo/*rest" component={Foo} />
// params.rest contains "bar/baz" for /foo/bar/baz
```

**Note:** Wildcards must be the last segment of the path.

### Multiple Paths

Define multiple paths for a single route to prevent re-rendering on navigation:

```jsx
// Component stays mounted when switching between login and register
<Route path={["/login", "/register"]} component={AuthForm} />
```

## Parameter Validation with MatchFilters

Validate parameters using `matchFilters`:

```jsx
import type { MatchFilters } from "@solidjs/router";

const filters: MatchFilters = {
  parent: ["mom", "dad"], // Enum values
  id: /^\d+$/, // Regex pattern (only numbers)
  withHtmlExtension: (v: string) => 
    v.length > 5 && v.endsWith(".html"), // Custom function
};

<Route
  path="/users/:parent/:id/:withHtmlExtension"
  component={User}
  matchFilters={filters}
/>;
```

**Match examples:**
- `/users/mom/123/contact.html` ✓ matches
- `/users/dad/456/about.html` ✓ matches
- `/users/aunt/123/contact.html` ✗ parent not in enum
- `/users/mom/me/contact.html` ✗ id doesn't match regex
- `/users/dad/123/contact` ✗ missing .html extension

## Nested Routes

### Basic Nesting

Nested routes inherit parent path segments:

```jsx
// These are equivalent:
<Route path="/users/:id" component={User} />

<Route path="/users">
  <Route path="/:id" component={User} />
</Route>
```

### Layout Components with Children

Use `props.children` to render nested route content:

```jsx
function UsersLayout(props) {
  return (
    <div>
      <h1>Users Section</h1>
      <nav>
        <a href="/users">All Users</a>
        <a href="/users/settings">Settings</a>
      </nav>
      {props.children}
    </div>
  );
}

<Route path="/users" component={UsersLayout}>
  <Route path="/" component={UsersList} />
  <Route path="/:id" component={UserDetail} />
  <Route path="/settings" component={UserSettings} />
</Route>
```

### Deep Nesting

Routes can be nested indefinitely:

```jsx
<Route path="/" component={(props) => <div>Level 1 {props.children}</div>}>
  <Route path="layer1" component={(props) => <div>Level 2 {props.children}</div>}>
    <Route path="layer2" component={() => <div>Level 3</div>} />
  </Route>
</Route>
```

Only leaf routes (innermost Route components) become navigable routes.

### Common Mistake: Parent Routes Without Separate Definition

```jsx
// This won't work as expected - /users won't render UsersList
<Route path="/users" component={UsersLayout}>
  <Route path="/:id" component={UserDetail} />
</Route>

// Correct: define parent route separately
<Route path="/users" component={UsersList} />
<Route path="/users">
  <Route path="/:id" component={UserDetail} />
</Route>

// Or: use explicit path="/" for parent
<Route path="/users" component={UsersLayout}>
  <Route path="/" component={UsersList} />
  <Route path="/:id" component={UserDetail} />
</Route>
```

## Navigation Components

### `<A>` Component

The recommended way to create links in Solid Router:

```jsx
import { A } from "@solidjs/router";

<A href="/users">Users</A>
<A href="/users/123">User 123</A>
<A href="/">Home</A>
```

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `href` | string | Path to navigate to (relative or absolute) |
| `activeClass` | string | CSS class when link is active (default: "active") |
| `inactiveClass` | string | CSS class when inactive (default: "inactive") |
| `end` | boolean | Match href exactly (don't match descendants) |
| `replace` | boolean | Replace history entry instead of pushing |
| `state` | any | State to pass via history API |
| `noScroll` | boolean | Disable scroll-to-top on navigation |

**Active Link Styling:**

```jsx
// /users link is active on /users and /users/123
<A href="/users">Users</A>

// /users link is active ONLY on /users, not /users/123
<A href="/users" end>Users</A>

// Custom classes
<A href="/about" activeClass="font-bold text-blue-500" inactiveClass="text-gray-400">
  About
</A>
```

### Relative Paths in Nested Routes

Links resolve relative to the current route:

```jsx
function UsersLayout() {
  return (
    <nav>
      {/* Resolves to /users from anywhere in /users/* routes */}
      <A href="/">All Users</A>
      
      {/* Resolves to /users/settings from anywhere in /users/* routes */}
      <A href="/settings">Settings</A>
      
      {/* Resolves to /users from /users/123 (goes up one level) */}
      <A href="../">Back to Users</A>
    </nav>
  );
}
```

### `<Navigate>` Component

For programmatic redirects:

```jsx
import { Navigate } from "@solidjs/router";

// Simple redirect
<Route path="/old-path" component={() => <Navigate href="/new-path" />} />

// Conditional redirect with function
function getPath({ navigate, location }) {
  return user?.isAdmin ? "/admin" : "/login";
}

<Route path="/redirect" component={() => <Navigate href={getPath} />} />
```

**Props:** Same as `<A>` component (`href`, `replace`, `state`, etc.)

## Standard Anchor Tags

Regular `<a>` tags work automatically (unless `explicitLinks` is true):

```jsx
// This works the same as <A> by default
<a href="/users">Users</a>

// This will do a full page reload (target attribute disables interception)
<a href="/users" target="_self">Users</a>
```

## Route Matching Priority

Routes are matched in order of specificity:
1. Exact matches first (`/users` before `/users/*`)
2. Static segments before parameters (`/users/new` before `/users/:id`)
3. Required parameters before optional (`/users/123` matches `:id` before `:id?`)
4. Order of definition (earlier routes checked first for same specificity)

```jsx
// /users/new will match the static route, not :id
<Route path="/users/:id" component={User} />
<Route path="/users/new" component={NewUser} />

// Better: define specific routes before parameters
<Route path="/users/new" component={NewUser} />
<Route path="/users/:id" component={User} />
```
