# SolidStart Core Concepts

## Architecture Overview

SolidStart is built on top of [Vinxi](https://vinxi.org), a multi-router framework that enables unified rendering. The architecture separates concerns between:

- **Client runtime**: Handles hydration and client-side navigation
- **Server runtime**: Manages SSR, API routes, and server functions
- **Shared code**: Isomorphic utilities that work on both environments

## Rendering Modes

SolidStart supports three rendering modes via `createHandler`:

### Streaming (Default)

Fastest time-to-first-byte with progressive HTML delivery:

```tsx
// src/entry-server.tsx
import { createHandler, StartServer } from "@solidjs/start/server";

export default createHandler(
  () => (
    <StartServer
      document={({ assets, children, scripts }) => (
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            {assets}
          </head>
          <body>
            <div id="app">{children}</div>
            {scripts}
          </body>
        </html>
      )}
    />
  ),
  { mode: "stream" } // Default mode
);
```

Benefits:
- Shell HTML sent immediately
- Components hydrate as they're ready
- Best for content-heavy pages

### Synchronous Rendering

Complete rendering before response:

```tsx
export default createHandler(() => <StartServer />, {
  mode: "sync",
});
```

Use when:
- Need complete HTML before sending response
- Simpler debugging requirements
- SEO-critical pages requiring full content

### Asynchronous Rendering

Full streaming without shell optimization:

```tsx
export default createHandler(() => <StartServer />, {
  mode: "async",
});
```

Use for custom streaming implementations.

## Entry Points

### Client Entry (`entry-client.tsx`)

Handles client-side hydration:

```tsx
// @refresh reload
import { mount, StartClient } from "@solidjs/start/client";

mount(() => <StartClient />, document.getElementById("app")!);
```

The `@refresh reload` directive ensures this file reloads the page on changes (required for entry points).

### Server Entry (`entry-server.tsx`)

Manages server-side rendering:

```tsx
// @refresh reload
import { createHandler, StartServer } from "@solidjs/start/server";

export default createHandler(() => (
  <StartServer
    document={({ assets, children, scripts }) => (
      <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="icon" href="/favicon.ico" />
          {assets} {/* Styles and critical CSS */}
        </head>
        <body>
          <div id="app">{children}</div>
          {scripts} {/* Hydration scripts */}
        </body>
      </html>
    )}
  />
));
```

### App Component (`app.tsx`)

Root component with routing:

```tsx
import { MetaProvider, Title } from "@solidjs/meta";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start/router";
import { Suspense } from "solid-js";

export default function App() {
  return (
    <Router
      root={props => (
        <MetaProvider>
          <Title>My App</Title>
          <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
          </nav>
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
```

## Client-Only Components

Components that should only render on the client:

```tsx
import clientOnly from "@solidjs/start";

// Lazy load a client-only component
const ChartComponent = clientOnly(() => import("./Chart"), {
  lazy: false, // Load immediately; set to true for on-demand loading
});

export default function Dashboard() {
  return (
    <main>
      <h1>Dashboard</h1>
      <ChartComponent
        fallback={<div>Loading chart...</div>}
        data={chartData}
      />
    </main>
  );
}
```

Server renders the `fallback` prop; client replaces with actual component.

## Isomorphic Code Patterns

Code that runs on both server and client:

```tsx
// ✅ Good: Use solid-js/web utilities
import { isServer, isClient } from "solid-js/web";

export function usePlatform() {
  return isServer ? "server" : "client";
}

// ✅ Good: Environment variables
export const API_URL = import.meta.env.PROD
  ? "https://api.example.com"
  : "http://localhost:3000";

// ❌ Bad: Direct browser API access
export function getClientInfo() {
  if (typeof window !== "undefined") { // Avoid this pattern
    return window.navigator.userAgent;
  }
  return "";
}

// ✅ Better: Use onMount for client-only
import { onMount, createSignal } from "solid-js";

export function useClientInfo() {
  const [info, setInfo] = createSignal("");
  
  onMount(() => {
    setInfo(window.navigator.userAgent);
  });
  
  return info;
}
```

## Request Event Access

Access the request event in components:

```tsx
import { getRequestEvent } from "solid-js/web";

export default function PageWithRequestInfo() {
  // Only available during SSR
  const event = getRequestEvent();
  
  if (event) {
    const userAgent = event.request.headers.get("user-agent");
    const url = new URL(event.request.url);
    
    // Set response headers
    event.response.headers.set("X-Custom-Header", "value");
    
    // Set status code via component
    return <HttpStatusCode code={404} />;
  }
  
  return <div>Client-side content</div>;
}
```

## Response Control Components

### HttpHeader

Set or append response headers:

```tsx
import { HttpHeader } from "@solidjs/start";

export default function PageWithHeaders() {
  return (
    <main>
      <HttpHeader name="X-Custom-Header" value="custom-value" />
      <HttpHeader name="Cache-Control" value="no-cache" append />
      <h1>Page with custom headers</h1>
    </main>
  );
}
```

### HttpStatusCode

Set response status code:

```tsx
import { HttpStatusCode } from "@solidjs/start";

export default function NotFoundPage() {
  return (
    <main>
      <HttpStatusCode code={404} text="Not Found" />
      <h1>Page Not Found</h1>
    </main>
  );
}
```

## Assets and Scripts

The `StartServer` component provides:

- `{assets}`: Critical CSS and style tags (placed in `<head>`)
- `{scripts}`: Hydration scripts and JS bundles (placed before `</body>`)

Custom assets can be added via route-level or component-level imports.

## Data Fetching Patterns

### Server-Side Data Fetching

Fetch data during SSR using route modules:

```tsx
// src/routes/posts/[id].tsx
import { createSignal, onMount } from "solid-js";

export default function PostPage(props: { params: { id: string } }) {
  const [post, setPost] = createSignal(null);
  
  // Client-side fetch after hydration
  onMount(async () => {
    const res = await fetch(`/api/posts/${props.params.id}`);
    setPost(await res.json());
  });
  
  return (
    <article>
      {post() ? <PostContent post={post()} /> : <Loading />}
    </article>
  );
}
```

### Using Server Functions

For secure data operations:

```tsx
import { getPost } from "~/server/get-post";

export default function PostPage(props: { params: { id: string } }) {
  const [post, setPost] = createSignal(null);
  
  onMount(async () => {
    setPost(await getPost(props.params.id));
  });
  
  return <article>{post()?.title}</article>;
}
```

See [Server Functions](05-server-functions.md) for complete guide.

## TypeScript Configuration

SolidStart includes TypeScript support out of the box:

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "jsx": "preserve",
    "jsxImportSource": "solid-js",
    "paths": {
      "~/*": ["./src/*"]
    }
  }
}
```

The `~` alias maps to the `src` directory.

## Environment Variables

Access environment variables via `import.meta.env`:

```tsx
// Public variables (prefix with VITE_)
const apiUrl = import.meta.env.VITE_API_URL;

// Build-time constants
const isDev = import.meta.env.DEV;
const isProd = import.meta.env.PROD;

// Server-only variables (not exposed to client)
// Accessible only in server functions and API routes
const secretKey = process.env.SECRET_KEY;
```

Public variables must be prefixed with `VITE_` to be bundled into client code.
