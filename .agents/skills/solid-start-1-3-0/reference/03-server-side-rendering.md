# Server-Side Rendering

SolidStart supports three SSR modes plus client-only rendering, configurable through `createHandler`.

## Entry Points

### entry-client.tsx

Browser entry point. Mounts the application and handles hydration:

```tsx title="src/entry-client.tsx"
import { mount, StartClient } from "@solidjs/start/client";

mount(() => <StartClient />, document.getElementById("app")!);
```

`mount` automatically calls `hydrate` (for SSR) or `render` (for CSR-only). This is the ideal place for client-specific startup code like service worker registration.

### entry-server.tsx

Server entry point. Provides the HTML document template:

```tsx title="src/entry-server.tsx"
import { createHandler, StartServer } from "@solidjs/start/server";

export default createHandler(() => (
  <StartServer
    document={({ assets, children, scripts }) => (
      <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="icon" href="/favicon.ico" />
          {assets}
        </head>
        <body>
          <div id="app">{children}</div>
          {scripts}
        </body>
      </html>
    )}
  />
));
```

The `document` prop receives:
- **`assets`** — CSS and other asset `<link>` tags
- **`children`** — The rendered application JSX
- **`scripts`** — JavaScript `<script>` tags for hydration

### app.tsx

Isomorphic root component. Runs on both server and client:

```tsx title="src/app.tsx"
import { Suspense } from "solid-js";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start/router";

export default function App() {
  return (
    <Router root={(props) => <Suspense>{props.children}</Suspense>}>
      <FileRoutes />
    </Router>
  );
}
```

## SSR Modes

Configure the rendering mode via `createHandler`'s options:

```tsx title="src/entry-server.tsx"
import { createHandler, StartServer } from "@solidjs/start/server";

export default createHandler(
  () => <StartServer document={...} />,
  { mode: "async" }  // Options: "sync", "async", "stream"
);
```

### Mode comparison

- **`sync`** — Uses `renderToString`. Fastest, but no async components. Best for simple pages.
- **`async`** — Uses `renderToStringAsync`. Supports async components and Suspense boundaries. Good balance of performance and flexibility.
- **`stream`** — Uses `renderToStream`. Streams HTML chunks as they resolve. Best Time to First Byte (TTFB), but most complex. **This is the default.**

### When to choose each mode

- Use `stream` for most applications — it provides the best user experience with progressive rendering
- Use `async` if you need simpler error handling or have issues with streaming
- Use `sync` only for very simple pages with no async data loading

## Disabling SSR (CSR-only)

Set `ssr: false` in configuration:

```ts title="app.config.ts"
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  ssr: false,
});
```

When SSR is disabled, `mount` in `entry-client.tsx` uses `render` instead of `hydrate`.

## Client-Only Components

Use `clientOnly` to render components exclusively in the browser:

```tsx
import { clientOnly } from "@solidjs/start";

const HeavyChart = clientOnly(() => import("./HeavyChart"));

export default function Page() {
  return <HeavyChart fallback={<div>Loading chart...</div>} />;
}
```

For entire pages:

```tsx title="routes/client-page.tsx"
import { clientOnly } from "@solidjs/start";

export default clientOnly(async () => ({ default: Page }), { lazy: true });

function Page() {
  // Runs only on the client
  return <div>Client-only page</div>;
}
```

## Request Events

Access the server request event from anywhere on the server using `getRequestEvent`:

```tsx
import { getRequestEvent } from "solid-js/web";

export default function Page() {
  const event = getRequestEvent();
  // event.locals — request-scoped data from middleware
  // event.request — standard Request object
  return <div>...</div>;
}
```

### Typing locals

Extend the `RequestEventLocals` interface:

```ts title="global.d.ts"
/// <reference types="@solidjs/start/env" />

declare module App {
  interface RequestEventLocals {
    user?: { id: string; name: string };
    startTime?: number;
  }
}
```

### nativeEvent

Access the underlying H3 event via `event.nativeEvent`. Use this for Vinxi HTTP helpers (cookies, sessions). Note that Vinxi helpers do not tree-shake — only import them in server-only files.
