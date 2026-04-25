# Solid Router Advanced Patterns

This reference covers config-based routing, alternative router modes, SSR patterns, and deployment configurations for Solid Router v0.16.

## Config-Based Routing

Instead of JSX, define routes as JavaScript objects for dynamic or programmatic route configuration.

### Array of Route Definitions

```jsx
import { lazy } from "solid-js";
import { Router } from "@solidjs/router";

const routes = [
  {
    path: "/",
    component: lazy(() => import("/pages/index.js")),
  },
  {
    path: "/users",
    component: lazy(() => import("/pages/users.js")),
    children: [
      {
        path: "/",
        component: lazy(() => import("/pages/users/index.js")),
      },
      {
        path: "/:id",
        component: lazy(() => import("/pages/users/[id].js")),
        children: [
          {
            path: "/settings",
            component: lazy(() => import("/pages/users/[id]/settings.js")),
          },
        ],
      },
      {
        path: "/*all",
        component: lazy(() => import("/pages/users/[...all].js")),
      },
    ],
  },
  {
    path: "/*all",
    component: lazy(() => import("/pages/[...all].js")), // 404
  },
];

render(() => <Router>{routes}</Router>, document.getElementById("app"));
```

### Single Route Definition

```jsx
const route = {
  path: "/",
  component: lazy(() => import("/pages/index.js")),
};

render(() => <Router>{route}</Router>, document.getElementById("app"));
```

### Route Object Structure

```typescript
type RouteDefinition = {
  path: string;
  component: Component;
  matchFilters?: MatchFilters;
  preload?: RoutePreloadFunc;
  children?: RouteDefinition[];
  info?: any; // Custom metadata
};
```

### Dynamic Route Generation

Generate routes from filesystem or API:

```jsx
// Example: Generate routes from a manifest
const routeManifest = await fetch("/routes.json").then(r => r.json());

const routes = routeManifest.map(route => ({
  path: route.path,
  component: lazy(() => import(`./pages/${route.file}`)),
  children: route.children?.map(child => ({
    path: child.path,
    component: lazy(() => import(`./pages/${child.file}`))
  })),
}));

<Router>{routes}</Router>;
```

## Alternative Router Modes

### HashRouter (Hash-Based Routing)

Use hash-based routing instead of history API:

```jsx
import { HashRouter } from "@solidjs/router";

render(() => <HashRouter>{routes}</HashRouter>, document.getElementById("app"));
```

**When to use:**
- Legacy browser support requirements
- Apps embedded in existing sites
- When server can't handle arbitrary paths
- GitHub Pages or similar static hosting without rewrite rules

**URL format:** `example.com/#/users/123` instead of `example.com/users/123`

### MemoryRouter (Testing)

Use memory-based routing for testing without browser dependencies:

```jsx
import { MemoryRouter } from "@solidjs/router";

// In test file
render(() => (
  <MemoryRouter initialUrl="/users/123">
    <Route path="/users/:id" component={UserPage} />
  </MemoryRouter>
), container);
```

**Props:**
- `initialUrl` - Starting URL for tests
- `initialEntries` - Array of history entries

**Testing Example:**

```jsx
import { render, fireEvent } from "@solidjs/testing-library";
import { MemoryRouter, Route, A } from "@solidjs/router";

test("navigation works", async () => {
  const { getByText } = render(() => (
    <MemoryRouter initialUrl="/">
      <Route path="/" component={() => (
        <>
          <h1>Home</h1>
          <A href="/about">About</A>
        </>
      )} />
      <Route path="/about" component={() => <h1>About</h1>} />
    </MemoryRouter>
  ));
  
  fireEvent.click(getByText("About"));
  await waitFor(() => getByText("About"));
});
```

### Static Router (SSR)

For server-side rendering, the Router automatically uses static mode:

```jsx
import { isServer } from "solid-js/web";
import { Router } from "@solidjs/router";

// On server, pass the request URL
function App() {
  return (
    <Router url={isServer ? req.url : ""}>
      {routes}
    </Router>
  );
}
```

**Static routing characteristics:**
- No client-side navigation
- Renders single route based on URL
- No history API interactions
- Preload functions still work for data fetching

## Server-Side Rendering Patterns

### Basic SSR Setup

```jsx
// server.js (Node.js example)
import { renderToString } from "solid-js/web";
import { Router } from "@solidjs/router";
import App from "./App";

app.get("*", async (req, res) => {
  const html = await renderToString(() => (
    <Router url={req.url}>
      <App />
    </Router>
  ));
  
  res.send(`<!DOCTYPE html><html><body>${html}</body></html>`);
});
```

### Progressive Enhancement with Forms

Forms work without JavaScript:

```jsx
const updateUser = action(async (formData) => {
  const id = formData.get("id");
  const name = formData.get("name");
  await db.updateUser(id, { name });
  throw redirect(`/users/${id}`);
}, "update-user"); // Name required for SSR

// This form works even without JavaScript
<form action={updateUser} method="post">
  <input type="hidden" name="id" value={user.id} />
  <input type="text" name="name" value={user.name} />
  <button type="submit">Update</button>
</form>
```

### Action Names for SSR

Actions need stable names for server serialization:

```jsx
// Good: named action
const deleteItem = action(async (formData) => {
  // ...
}, "delete-item");

// In template - serializes to string
<form action={deleteItem} method="post">
  <!-- Server renders: action="/_server/delete-item" -->
</form>

// Bad: anonymous action (won't work with SSR)
const badAction = action(async (formData) => {
  // ...
});
```

### Custom Action Base URL

Change the default `/_server` prefix:

```jsx
<Router actionBase="/api/actions">
  {/* Actions will serialize to /api/actions/action-name */}
</Router>
```

## Deployment Configurations

### Netlify

Create `_redirects` file in `public/` or `static/`:

```
/*   /index.html   200
```

Or in `netlify.toml`:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Vercel

Create `vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

Or use the automatic detection (works for most SolidJS projects).

### Nginx

Add fallback to index.html:

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

### Apache

Create `.htaccess`:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

### Docker

Ensure your server returns index.html for all routes:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install && npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Base Path Configuration

For apps deployed under a subdirectory:

```jsx
<Router base="/my-app">
  <Route path="/" component={Home} />
  <Route path="/users" component={Users} />
</Router>
```

**Effects:**
- Routes match against `/my-app/users`, not `/users`
- `<A href="/users">` resolves to `/my-app/users`
- Server must redirect `/my-app/*` to index.html

### Environment-Based Base Path

```jsx
const BASE_PATH = import.meta.env.VITE_BASE_PATH || "";

<Router base={BASE_PATH}>
  {routes}
</Router>
```

## Explicit Links Mode

Require `<A>` component for all client-side navigation:

```jsx
<Router explicitLinks={true}>
  {/* Only <A> tags do client-side navigation */}
  {/* Regular <a> tags will do full page reloads */}
</Router>
```

**When to use:**
- Prevent accidental client-side navigation
- Clear distinction between internal/external links
- Migration from server-rendered sites

```jsx
// Client-side navigation (stays in SPA)
<A href="/users">Users</A>

// Full page reload
<a href="/users">Users</a>

// Also full page reload (target attribute)
<a href="/users" target="_self">Users</a>
```

## Error Boundaries with Routes

Catch rendering errors in specific routes:

```jsx
import { ErrorBoundary } from "solid-js";

function RouteWithErrorBoundary() {
  return (
    <ErrorBoundary fallback={(error) => <ErrorPage error={error} />}>
      <ExpensiveRoute />
    </ErrorBoundary>
  );
}

<Route path="/expensive" component={RouteWithErrorBoundary} />
```

## Global Error Handling

Handle 404 and errors at app level:

```jsx
const App = (props) => {
  const location = useLocation();
  
  return (
    <div>
      <Header />
      <main>
        {props.children}
      </main>
      <Footer />
    </div>
  );
};

<Router root={App}>
  <Route path="/" component={Home} />
  <Route path="/users" component={Users} />
  {/* Catch-all 404 */}
  <Route path="*" component={NotFoundPage} />
</Router>
```

## Migration from v0.9.x

### Removed: `<Outlet>` and `<Routes>`

Use `props.children` instead:

```jsx
// Old (v0.9.x)
<Layout>
  <Outlet />
</Layout>

// New (v0.10+)
function Layout(props) {
  return (
    <div>
      <Header />
      {props.children}
      <Footer />
    </div>
  );
}
```

### Removed: `data` Functions and `useRouteData`

Use preload functions instead:

```jsx
// Old
const User = {
  component: UserPage,
  data: ({ params }) => fetchUser(params.id)
};

// New
async function preloadUser({ params }) {
  void getUser(params.id); // Using query API
}

<Route path="/users/:id" component={UserPage} preload={preloadUser} />
```

### Removed: `element` Prop

Use `component` prop only:

```jsx
// Old
<Route path="/" element={<Home />} />

// New
<Route path="/" component={Home} />
```

## Performance Tips

### Enable Preloads (Default)

Preloads run on link hover for faster navigation:

```jsx
<Router preload={true}>
  {routes}
</Router>
```

### Lazy Load All Routes

Reduce initial bundle size:

```jsx
const routes = [
  { path: "/", component: lazy(() => import("./pages/Home")) },
  { path: "/users", component: lazy(() => import("./pages/Users")) },
  // ...
];
```

### Code Split by Route Group

```jsx
// Large feature gets its own chunk
const Dashboard = lazy(() => import("./features/Dashboard"));
<Route path="/dashboard" component={Dashboard} />
```

### Disable Preloads for Heavy Routes

```jsx
function heavyPreload({ params }) {
  // Expensive operation, don't run on hover
  if (intent === "preload") return;
  fetchData(params.id);
}

<Route path="/heavy" component={HeavyPage} preload={heavyPreload} />
```
