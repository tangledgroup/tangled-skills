---
name: solid-router-0-16-1
description: The universal router for SolidJS providing fine-grained reactivity for route navigation with support for history-based, hash-based, static (SSR), and memory-based routing modes. Use when building single-page applications in SolidJS that require client-side routing, nested routes, data loading APIs, form actions, or universal rendering across server and client environments.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.16.1"
tags:
  - solidjs
  - router
  - spa
  - routing
  - ssg
  - ssr
category: framework
external_references:
  - https://docs.solidjs.com/solid-router/
  - https://github.com/solidjs/solid-router
---

# Solid Router 0.16.1

## Overview

Solid Router (`@solidjs/router`) brings fine-grained reactivity to route navigation, enabling single-page applications to become multi-paged without full page reloads. It is fully integrated into the SolidJS ecosystem with declarative syntax, universal rendering, and parallel data fetching through preload functions and a query caching API.

Key features:

- **All routing modes** — History-based (`Router`), hash-based (`HashRouter`), static for SSR (`StaticRouter`), and memory-based for testing (`MemoryRouter`)
- **TypeScript-first** — Full type safety for route parameters, match filters, and data APIs
- **Universal rendering** — Seamless server-side and client-side rendering with the same router
- **Declarative routes** — Define routes as JSX components or plain objects
- **Preload functions** — Parallel data fetching following render-as-you-fetch pattern
- **Dynamic route parameters** — URL patterns with parameters, optional segments, and wildcards
- **Data APIs with caching** — `query`, `createAsync`, `action` with deduplication and revalidation
- **Form actions** — Server-like mutation actions with `redirect`, `reload`, and `json` response helpers

## When to Use

- Building a SolidJS single-page application that needs client-side routing
- Setting up nested routes with shared layouts using `props.children`
- Implementing data fetching alongside route transitions with preload functions
- Building SSR applications that need the same router on server and client
- Creating form-based mutations with automatic revalidation
- Migrating from Solid Router 0.9.x (where `<Outlet>`, `<Routes>`, and `useRouteData` were removed)
- Needing hash-based or memory-based routing for special deployment or testing scenarios

## Installation / Setup

Install the package and wrap your application root with a Router component:

```jsx
import { render } from "solid-js/web";
import { Router, Route } from "@solidjs/router";

import Home from "./pages/Home";
import Users from "./pages/Users";

render(
  () => (
    <Router>
      <Route path="/" component={Home} />
      <Route path="/users" component={Users} />
    </Router>
  ),
  document.getElementById("app")
);
```

For SSR, pass the URL on the server side:

```jsx
import { isServer } from "solid-js/web";
import { Router } from "@solidjs/router";

<Router url={isServer ? req.url : ""} />;
```

## Core Concepts

**Routes are defined declaratively** — Each `<Route>` specifies a `path` and a `component`. Only leaf routes (innermost `<Route>` components without children) become actual navigable routes. Parent routes act as layout wrappers via `props.children`.

**The root prop** — A top-level layout component passed to `<Router root={App}>` wraps every route. It is the ideal place for navigation bars, context providers, and shared UI that persists across page changes.

**Props passed to route components** — Every route component receives `params` (path parameters), `location` (current URL info), `data` (preload return value), and `children` (nested route output).

```jsx
export default function User(props) {
  return (
    <div>
      <h1>User {props.params.id}</h1>
      {props.children}
    </div>
  );
}
```

**Preload functions** — A `preload` function on a route receives `{ params, location, intent }` and is called when the route loads or eagerly on link hover. Its return value is passed as `props.data` to the component (except when intent is `"preload"`).

```jsx
function preloadUser({ params, location, intent }) {
  // Called on route load and on link hover
  return fetch(`/api/users/${params.id}`).then(r => r.json());
}

<Route path="/users/:id" component={User} preload={preloadUser} />;
```

## Usage Examples

### Basic Setup with Root Layout and 404

```jsx
import { lazy } from "solid-js";
import { render } from "solid-js/web";
import { Router, Route } from "@solidjs/router";

const Users = lazy(() => import("./pages/Users"));
const Home = lazy(() => import("./pages/Home"));
const NotFound = lazy(() => import("./pages/404"));

const App = (props) => (
  <>
    <nav>
      <a href="/">Home</a>
      <a href="/users">Users</a>
    </nav>
    <main>{props.children}</main>
  </>
);

render(
  () => (
    <Router root={App}>
      <Route path="/" component={Home} />
      <Route path="/users" component={Users} />
      <Route path="*404" component={NotFound} />
    </Router>
  ),
  document.getElementById("app")
);
```

### Dynamic Route with Match Filters

```jsx
import { lazy } from "solid-js";
import { Router, Route } from "@solidjs/router";
import type { MatchFilters } from "@solidjs/router";

const User = lazy(() => import("./pages/User"));

const filters: MatchFilters = {
  parent: ["mom", "dad"],
  id: /^\d+$/,
};

render(
  () => (
    <Router>
      <Route
        path="/users/:parent/:id"
        component={User}
        matchFilters={filters}
      />
    </Router>
  ),
  document.getElementById("app")
);
```

### Config-Based Routing (Object Syntax)

```jsx
import { lazy } from "solid-js";
import { Router } from "@solidjs/router";

const routes = [
  {
    path: "/users",
    component: lazy(() => import("/pages/users.js")),
  },
  {
    path: "/users/:id",
    component: lazy(() => import("/pages/users/[id].js")),
    children: [
      { path: "/", component: lazy(() => import("/pages/users/[id]/index.js")) },
      { path: "/settings", component: lazy(() => import("/pages/users/[id]/settings.js")) },
      { path: "/*all", component: lazy(() => import("/pages/users/[id]/[...all].js")) },
    ],
  },
  { path: "/", component: lazy(() => import("/pages/index.js")) },
  { path: "/*all", component: lazy(() => import("/pages/[...all].js")) },
];

render(() => <Router>{routes}</Router>, document.getElementById("app"));
```

## Advanced Topics

**Routing Modes**: History, Hash, Static (SSR), and Memory routers with configuration options → [Routing Modes](reference/01-routing-modes.md)

**Route Patterns**: Dynamic parameters, optional segments, wildcards, multiple paths, match filters, and nested routes → [Route Patterns](reference/02-route-patterns.md)

**Data APIs**: `query`, `createAsync`, `createAsyncStore`, `action`, `useAction`, `useSubmission`, response helpers (`redirect`, `reload`, `json`) → [Data APIs](reference/03-data-apis.md)

**Components Reference**: `<Router>`, `<A>`, `<Navigate>`, `<Route>` props and behavior → [Components Reference](reference/04-components-reference.md)

**Router Primitives**: `useParams`, `useNavigate`, `useLocation`, `useSearchParams`, `useIsRouting`, `useMatch`, `useCurrentMatches`, `usePreloadRoute`, `useBeforeLeave` → [Router Primitives](reference/05-router-primitives.md)
