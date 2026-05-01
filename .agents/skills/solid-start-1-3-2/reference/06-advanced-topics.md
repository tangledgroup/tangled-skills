# Advanced Topics

## Security

### XSS (Cross-Site Scripting)

Solid automatically escapes values in JSX expressions. Protection does not apply to `innerHTML`. Best practices:

- Set a Content Security Policy (CSP) header
- Validate and sanitize user inputs on server and client
- Avoid `innerHTML`; if necessary, sanitize with DOMPurify
- Sanitize attributes containing user data within `<noscript>` elements
- Validate URL `origin` and `protocol` for user-provided URLs

### Content Security Policy (CSP)

#### With nonce (recommended for strict CSP)

```ts title="src/middleware/index.ts"
import { createMiddleware } from "@solidjs/start/middleware";
import { randomBytes } from "crypto";

export default createMiddleware({
  onRequest: (event) => {
    const nonce = randomBytes(16).toString("base64");
    event.locals.nonce = nonce;

    const csp = `default-src 'self'; script-src 'nonce-${nonce}' 'strict-dynamic'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'`;
    event.response.headers.set("Content-Security-Policy", csp);
  },
});
```

Pass the nonce to `createHandler`:

```tsx title="src/entry-server.tsx"
import { createHandler, StartServer } from "@solidjs/start/server";

export default createHandler(
  () => <StartServer /* ... */ />,
  (event) => ({ nonce: event.locals.nonce })
);
```

Use `serialization.mode: "json"` for strict CSP (avoids `unsafe-eval`).

#### Without nonce

```ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onBeforeResponse: (event) => {
    const csp = `default-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'`;
    event.response.headers.set("Content-Security-Policy", csp);
  },
});
```

### CORS (Cross-Origin Resource Sharing)

```ts
import { createMiddleware } from "@solidjs/start/middleware";
import { json } from "@solidjs/router";

const TRUSTED_ORIGINS = ["https://my-app.com"];

export default createMiddleware({
  onBeforeResponse: (event) => {
    const { request, response } = event;
    response.headers.append("Vary", "Origin, Access-Control-Request-Method");

    const origin = request.headers.get("Origin");
    const url = new URL(request.url);
    const isApi = url.pathname.startsWith("/api");

    if (isApi && origin && TRUSTED_ORIGINS.includes(origin)) {
      if (request.method === "OPTIONS" && request.headers.get("Access-Control-Request-Method")) {
        return json(null, {
          headers: {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "OPTIONS, POST, PUT, PATCH, DELETE",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
          },
        });
      }
      response.headers.set("Access-Control-Allow-Origin", origin);
    }
  },
});
```

### CSRF (Cross-Site Request Forgery)

```ts
import { createMiddleware } from "@solidjs/start/middleware";
import { json } from "@solidjs/router";

const SAFE_METHODS = ["GET", "HEAD", "OPTIONS", "TRACE"];
const TRUSTED_ORIGINS = ["https://another-app.com"];

export default createMiddleware({
  onRequest: (event) => {
    if (!SAFE_METHODS.includes(event.request.method)) {
      const url = new URL(event.request.url);
      const origin = event.request.headers.get("Origin");

      if (origin) {
        const parsed = new URL(origin);
        if (parsed.origin !== url.origin && !TRUSTED_ORIGINS.includes(parsed.host)) {
          return json({ error: "origin invalid" }, { status: 403 });
        }
      }

      // HTTPS without Origin — check Referer
      if (!origin && url.protocol === "https:") {
        const referer = event.request.headers.get("Referer");
        if (!referer) {
          return json({ error: "referer not supplied" }, { status: 403 });
        }
        const parsedRef = new URL(referer);
        if (parsedRef.protocol !== "https:") {
          return json({ error: "referer invalid" }, { status: 403 });
        }
      }
    }
  },
});
```

## WebSockets

WebSocket support is experimental (depends on Nitro's experimental WebSocket feature):

```ts title="app.config.ts"
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    experimental: { websocket: true },
  },
}).addRouter({
  name: "ws",
  type: "http",
  handler: "./src/ws.ts",
  target: "server",
  base: "/ws",
});
```

```ts title="src/ws.ts"
import { eventHandler } from "vinxi/http";

export default eventHandler({
  handler() {},
  websocket: {
    async open(peer) {
      console.log("open", peer.id, peer.url);
    },
    async message(peer, msg) {
      console.log("msg", peer.id, msg.text());
    },
    async close(peer, details) {
      console.log("close", peer.id);
    },
    async error(peer, error) {
      console.log("error", peer.id, error);
    },
  },
});
```

## Static Assets

### Public directory

Files in `public/` are served at their exact path:

```
public/
├── favicon.ico           → /favicon.ico
├── images/
│   └── logo.png          → /images/logo.png
└── documents/
    └── report.pdf        → /documents/report.pdf
```

Reference with absolute paths:

```tsx
<img src="/images/logo.png" alt="Logo" />
```

Use public directory for: documents, service workers, images/audio/video, manifest files, metadata (`robots.txt`, sitemaps), favicon.

### Importing assets

Vite hashes imported assets for cache busting:

```tsx
import logo from "./solid.png";

export default function About() {
  return <img src={logo} alt="Logo" />;
  // Renders as: /assets/solid.2d8efhg.png
}
```

Use imports when you want automatic hashing and cache busting. Use public directory when you need stable, human-readable URLs.

## CSS and Styling

### Standard CSS

Import CSS files alongside components:

```tsx title="Card.tsx"
import "./Card.css";

export default function Card(props) {
  return (
    <div class="card">
      <h1>{props.title}</h1>
      <p>{props.text}</p>
    </div>
  );
}
```

### CSS Modules

Use `.module.css` extension for scoped styles:

```css title="Card.module.css"
.card {
  background-color: #446b9e;
}
```

```tsx
import styles from "./Card.module.css";

export default function Card(props) {
  return (
    <div class={styles.card}>
      <h1>{props.title}</h1>
    </div>
  );
}
```

Works with `.scss` and `.sass` as well (`.module.scss`, `.module.sass`).

## Head and Metadata

SolidStart does not ship with a metadata library. Use `@solidjs/meta`:

```tsx
import { Title, Meta } from "@solidjs/meta";

export default function About() {
  return (
    <>
      <Title>About | My Site</Title>
      <Meta name="description" content="About page" />
      <Meta property="og:title" content="About My Site" />
      <h1>About</h1>
    </>
  );
}
```

For site-wide metadata, add `Meta` tags in the root layout or document template.

## Service Workers

Place service worker files in `public/` and register in `entry-client.tsx`:

```tsx title="src/entry-client.tsx"
import { mount, StartClient } from "@solidjs/start/client";

mount(() => <StartClient />, document.getElementById("app")!);

if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js");
  });
}
```

## Migrating from v1 to v2

Key changes when upgrading:

1. **Update dependencies**: `@solidjs/start@2`, `vite@7`, `@solidjs/vite-plugin-nitro-2`
2. **Remove `vinxi`** as a dependency
3. **Replace `app.config.ts`** with `vite.config.ts`:

```ts title="vite.config.ts"
import { solidStart } from "@solidjs/start/config";
import { defineConfig } from "vite";
import { nitroV2Plugin } from "@solidjs/vite-plugin-nitro-2";

export default defineConfig(() => ({
  plugins: [solidStart({ middleware: "./src/middleware/index.ts" }), nitroV2Plugin()],
}));
```

4. **Update scripts**: Use native Vite commands (`vite dev`, `vite build`, `vite preview`)
5. **Replace `vinxi/http` imports** with `@solidjs/start/http`
6. **Add `"types": ["@solidjs/start/env"]`** to `tsconfig.json` compilerOptions
7. **Serialization defaults**: v2 defaults to `json` mode (v1 used `js`)
