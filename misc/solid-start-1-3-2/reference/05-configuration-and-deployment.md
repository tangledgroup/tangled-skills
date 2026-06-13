# Configuration & Deployment

## app.config.ts

The root configuration file exports settings for SolidStart, Vite, and Nitro using `defineConfig`:

```ts title="app.config.ts"
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({});
```

## defineConfig options

- **`ssr`** (`boolean`, default: `true`) — Toggle between client and server rendering
- **`solid`** (`object`) — Configuration for `vite-plugin-solid`
- **`extensions`** (`string[]`, default: `["js", "jsx", "ts", "tsx"]`) — File extensions treated as routes
- **`server`** (`object`) — Nitro server configuration (presets, prerendering)
- **`serialization`** (`object`) — Server function payload serialization settings
- **`appRoot`** (`string`, default: `"./src"`) — Path to application root
- **`routeDir`** (`string`, default: `"./routes"`) — Path to routes directory
- **`middleware`** (`string`) — Path to middleware file
- **`devOverlay`** (`boolean`, default: `true`) — Toggle dev overlay
- **`experimental.islands`** (`boolean`, default: `false`) — Enable islands mode
- **`vite`** (`ViteConfig` or function) — Vite configuration

## Configuring Vite

Pass Vite options directly, including plugins:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  vite: {
    plugins: [],
  },
});
```

Configure per-router (three routers exist):

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  vite({ router }) {
    // router is "server", "client", or "server-function"
    if (router === "server") {
      // server-specific Vite config
    } else if (router === "client") {
      // client-specific Vite config
    } else if (router === "server-function") {
      // server-function-specific Vite config
    }
    return { plugins: [] };
  },
});
```

## Serialization

Configure how server function payloads are serialized:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  serialization: {
    mode: "json", // or "js"
  },
});
```

### Modes

- **`json`** — Uses `JSON.parse` on the client. Safest for strict CSP (avoids `eval`). Payloads are slightly larger.
- **`js`** — Uses Seroval's JS serializer. Smaller payloads, better performance, but requires `unsafe-eval` in CSP.

Defaults: v1 uses `js`, v2 defaults to `json`.

### Supported types

Seroval plus web platform plugins support: `AbortSignal`, `CustomEvent`, `DOMException`, `Event`, `FormData`, `Headers`, `ReadableStream`, `Request`, `Response`, `URL`, `URLSearchParams`.

`RegExp` is disabled by default. JSON mode enforces a maximum serialization depth of 64.

## Configuring Nitro

The `server` option exposes Nitro configuration including deployment presets:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    preset: "netlify", // deployment target
  },
});
```

### Server presets

- `node` — Node.js server (default)
- `deno_server` — Deno server
- `bun` — Bun server

### Provider presets

- `netlify`, `netlify_edge` — Netlify Functions and Edge
- `vercel`, `vercel_edge` — Vercel Functions and Edge
- `aws_lambda` — AWS Lambda and Lambda@Edge
- `cloudflare`, `cloudflare_pages`, `cloudflare_module` — Cloudflare Workers and Pages
- `deno_deploy` — Deno Deploy

### Cloudflare special configuration

Cloudflare requires async local storage compatibility:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    preset: "cloudflare_module",
    rollupConfig: {
      external: ["__STATIC_CONTENT_MANIFEST", "node:async_hooks"],
    },
  },
});
```

In `wrangler.toml`:

```toml
compatibility_flags = [ "nodejs_compat" ]
```

## Route Pre-rendering (SSG)

Pre-render specific routes to static HTML at build time:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    prerender: {
      routes: ["/", "/about"],
    },
  },
});
```

Pre-render all routes by crawling links:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    prerender: {
      crawlLinks: true,
    },
  },
});
```

For advanced options, refer to [Nitro's prerender documentation](https://nitro.build/config#prerender).

## Building

```bash
npm run build    # or pnpm build / bun build
```

Generates production-ready bundles. After build, you'll be guided through deployment for your specific preset.

## Environment variables

Access environment variables in server functions:

```tsx
async function getData() {
  "use server";
  const apiKey = process.env.API_KEY;
  // ...
}
```

Store sensitive values like `SESSION_SECRET` in private environment variables, never hardcoded.
