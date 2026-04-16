---
name: solid-router-0-16
description: A skill for using Solid Router v0.16, the universal router for SolidJS that provides fine-grained reactivity for route navigation with support for history-based, hash-based, static (SSR), and memory-based routing modes. Use when building single-page applications in SolidJS that require client-side routing, nested routes, data loading APIs, form actions, or universal rendering across server and client environments.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - solidjs
  - router
  - routing
  - navigation
  - ssr
  - reactivity
  - web-development
category: development
required_environment_variables: []
---

# Solid Router v0.16

Solid Router is the universal router for SolidJS that brings fine-grained reactivity to route navigation, enabling single-page applications to become multi-paged without full page reloads. It supports history-based, hash-based, static (SSR), and memory-based routing modes with declarative syntax, parallel data fetching, and universal rendering capabilities.

**Key Features:**
- Universal rendering (client-side, server-side, hash mode, memory mode)
- TypeScript support with full type safety
- Declarative route configuration via JSX or objects
- Parallel data fetching with preload functions
- Dynamic route parameters with validation
- Data APIs with caching and deduplication
- Form actions with optimistic updates
- Nested routes with layout components

## When to Use

Load this skill when:
- Setting up routing in a SolidJS application
- Implementing client-side navigation without page reloads
- Configuring nested routes and layout components
- Working with dynamic route parameters and wildcards
- Implementing data loading patterns with preload functions
- Using form actions for server mutations
- Building universal apps that render on both server and client
- Need hash-based or memory-based routing (testing)

## Quick Start

### Installation

```bash
npm add @solidjs/router
# or
pnpm add @solidjs/router
# or
yarn add @solidjs/router
```

**Peer dependency:** SolidJS v1.8.6 or later required.

### Basic Setup

Wrap your application with the Router component:

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

### With Root Layout

Add a root layout that persists across route changes:

```jsx
const App = (props) => (
  <>
    <nav>
      <a href="/">Home</a>
      <a href="/users">Users</a>
    </nav>
    <h1>My Application</h1>
    {props.children}
  </>
);

render(
  () => (
    <Router root={App}>
      <Route path="/" component={Home} />
      <Route path="/users" component={Users} />
    </Router>
  ),
  document.getElementById("app")
);
```

See [Core Concepts](references/01-core-concepts.md) for detailed routing patterns and [Data APIs](references/02-data-apis.md) for advanced data loading.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Route configuration, dynamic routes, nested routes, and navigation components
- [`references/02-data-apis.md`](references/02-data-apis.md) - Preload functions, query API, createAsync, actions, and form handling
- [`references/03-router-primitives.md`](references/03-router-primitives.md) - Hooks like useParams, useNavigate, useLocation, useSearchParams
- [`references/04-advanced-patterns.md`](references/04-advanced-patterns.md) - Config-based routing, alternative routers, SSR, deployment

## Common Patterns

### Dynamic Routes with Parameters

```jsx
<Route path="/users/:id" component={User} />
```

Access parameters in the component:

```jsx
import { useParams } from "@solidjs/router";

function User() {
  const params = useParams();
  return <h1>User ID: {params.id}</h1>;
}
```

### Nested Routes with Layouts

```jsx
<Route path="/users" component={UsersLayout}>
  <Route path="/" component={UsersList} />
  <Route path="/:id" component={UserDetail} />
</Route>
```

The layout component receives children via `props.children`.

### Catch-All (404) Route

```jsx
<Route path="*" component={NotFound} />
```

Or with a named parameter to capture the unmatched path:

```jsx
<Route path="*404" component={NotFound} />
// params.404 contains the unmatched path segment
```

### Lazy Loading Routes

```jsx
import { lazy } from "solid-js";

const Users = lazy(() => import("./pages/Users"));
const Home = lazy(() => import("./pages/Home"));

<Router root={App}>
  <Route path="/users" component={Users} />
  <Route path="/" component={Home} />
</Router>
```

## Troubleshooting

**Routes not matching:** Ensure paths start with `/` for absolute routes or omit for relative nested routes. Check that only leaf Route nodes have components assigned.

**404 on page refresh:** For deployed SPAs, configure your hosting to redirect all routes to index.html (see deployment guides in reference files).

**Navigation not working:** Verify Router component wraps your entire app. Check that links use `<A>` component or standard `<a>` tags without `target` attribute.

**Data loading waterfalls:** Use preload functions on routes to fetch data in parallel with navigation. See Data APIs reference for patterns.

**TypeScript errors:** Ensure SolidJS v1.8.6+ is installed as peer dependency. Import types from `@solidjs/router` when needed.
