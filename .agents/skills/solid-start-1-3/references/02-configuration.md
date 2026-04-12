# SolidStart Configuration Reference

## app.config.ts

The main configuration file for SolidStart projects:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  // Core options
  ssr: true,
  publicDir: "./public",
  appRoot: "./src",
  routeDir: "./routes",
  
  // Server configuration
  server: { preset: "netlify" },
  
  // Vite configuration
  vite: {},
  
  // Solid-specific options
  solid: {},
  
  // File extensions
  extensions: ["jsx", "tsx"],
  
  // Middleware
  middleware: "./src/middleware.ts",
  
  // Development overlay
  devOverlay: true,
  
  // Experimental features
  experimental: {
    islands: false,
  },
  
  // Serialization mode for server functions
  serialization: {
    mode: "js", // or "json"
  },
});
```

## Core Options

### ssr

Enable or disable server-side rendering:

```ts
export default defineConfig({
  ssr: true,  // Default: SSR enabled
});

// CSR-only mode (no SSR)
export default defineConfig({
  ssr: false,
});
```

When `ssr: false`, all routes render client-side only. Useful for dashboards or apps requiring authentication before rendering.

### publicDir

Customize the static assets directory:

```ts
export default defineConfig({
  publicDir: "./static", // Default: "./public"
});
```

Files in this directory are served at the root path (e.g., `./public/logo.png` → `/logo.png`).

### appRoot

Change the application source directory:

```ts
export default defineConfig({
  appRoot: "./app", // Default: "./src"
});
```

Affects the base path for `app.tsx`, `entry-client.tsx`, and `entry-server.tsx`.

### routeDir

Customize the routes directory:

```ts
export default defineConfig({
  routeDir: "./pages", // Default: "./routes"
});
```

Routes will be loaded from `./app/pages` instead of `./src/routes`.

### extensions

Add custom file extensions:

```ts
export default defineConfig({
  extensions: ["jsx", "tsx", "md", "mdx"], // Default: ["js", "jsx", "ts", "tsx"]
});
```

Useful for MDX support or custom component extensions.

## Server Configuration

### Presets

Deployment presets configure the server adapter:

```ts
// Vercel (Node.js functions)
export default defineConfig({
  server: { preset: "vercel" },
});

// Netlify (Edge functions)
export default defineConfig({
  server: { preset: "netlify" },
});

// Cloudflare Pages
export default defineConfig({
  server: { preset: "cloudflare" },
});

// Node.js server
export default defineConfig({
  server: { preset: "node-server" },
});

// Bun runtime
export default defineConfig({
  server: { preset: "bun-server" },
});

// Deno runtime
export default defineConfig({
  server: { preset: "deno-server" },
});
```

### Custom Server Options

Full control over Vinxi server configuration:

```ts
export default defineConfig({
  server: {
    preset: "node-server",
    prerender: {
      crawl: true,
      routes: ["/", "/about"], // Routes to prerender
    },
  },
});
```

## Vite Configuration

Extend Vite configuration:

```ts
export default defineConfig({
  vite: {
    build: {
      minify: "terser",
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["solid-js", "@solidjs/router"],
          },
        },
      },
    },
    server: {
      port: 3000,
      host: "0.0.0.0",
    },
    plugins: [
      // Custom Vite plugins
    ],
  },
});
```

### Conditional Vite Config

Different config for router types:

```ts
export default defineConfig({
  vite: (options) => {
    if (options.router === "server") {
      return {
        // Server-side build config
        build: { ssr: true },
      };
    }
    if (options.router === "client") {
      return {
        // Client-side build config
        build: { cssCodeSplit: true },
      };
    }
    return {};
  },
});
```

## Solid Configuration

Configure `vite-plugin-solid`:

```ts
export default defineConfig({
  solid: {
    generate: "universal", // or "dom", "ssr"
    hot: true,
    include: ["**/*.tsx", "**/*.jsx"],
    exclude: ["**/node_modules/**"],
    transformOptions: {
      jsx: true,
      babel: {
        plugins: [
          ["babel-plugin-jsx-event-modifiers"],
        ],
      },
    },
  },
});
```

## Middleware Configuration

Add custom middleware:

```ts
// src/middleware.ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: async (event) => {
    // Modify request or return response
    const auth = event.request.headers.get("authorization");
    if (!auth) {
      return new Response("Unauthorized", { status: 401 });
    }
  },
  onBeforeResponse: async (event, response) => {
    // Modify response
    response.body.headers.set("X-Custom-Header", "value");
  },
});

// app.config.ts
export default defineConfig({
  middleware: "./src/middleware.ts",
});
```

Multiple middleware files:

```ts
export default defineConfig({
  middleware: ["./src/auth-middleware.ts", "./src/logging-middleware.ts"],
});
```

## Development Overlay

Control the dev error overlay:

```ts
export default defineConfig({
  devOverlay: true, // Default: show overlay on errors
});

// Disable overlay
export default defineConfig({
  devOverlay: false,
});
```

## Experimental Features

### Islands Architecture

Opt-out rendering for better performance:

```ts
export default defineConfig({
  experimental: {
    islands: true, // Render only interactive components
  },
});
```

When enabled, only components marked as islands are hydrated on the client.

## Serialization Mode

Configure server function serialization:

```ts
// Default: uses custom binary format with eval()
export default defineConfig({
  serialization: {
    mode: "js", // Faster, requires eval()
  },
});

// JSON mode: compatible with strict CSP
export default defineConfig({
  serialization: {
    mode: "json", // Slower, no eval required
  },
});
```

**Important**: 
- `js` mode uses `eval()` which may violate strict Content Security Policy
- `json` mode is more CSP-friendly but slower
- In SolidStart v2, `json` will be the default

## Environment-Specific Config

Use environment variables for different environments:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    preset: process.env.VERCEL ? "vercel" : "node-server",
  },
  vite: {
    build: {
      sourcemap: process.env.NODE_ENV === "development",
    },
  },
});
```

## Full Example Configuration

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  // Rendering
  ssr: true,
  
  // Directories
  publicDir: "./public",
  appRoot: "./src",
  routeDir: "./routes",
  
  // Deployment target
  server: { 
    preset: process.env.VERCEL ? "vercel" : "node-server",
    prerender: {
      crawl: true,
      routes: ["/", "/about", "/pricing"],
    },
  },
  
  // File extensions
  extensions: ["js", "jsx", "ts", "tsx", "mdx"],
  
  // Middleware
  middleware: "./src/middleware.ts",
  
  // Dev overlay
  devOverlay: true,
  
  // Experimental features
  experimental: {
    islands: false,
  },
  
  // Server function serialization
  serialization: {
    mode: "js",
  },
  
  // Vite config
  vite: {
    css: {
      postcss: "./postcss.config.js",
    },
    build: {
      target: "esnext",
    },
  },
  
  // Solid config
  solid: {
    generate: "universal",
    hot: true,
  },
});
```

## Migration from Vite Config

If migrating from a Vite-only project:

```ts
// Old: vite.config.ts
export default {
  plugins: [solid()],
  resolve: { alias: { "~": "./src" } },
};

// New: app.config.ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  // SolidStart handles routing and SSR automatically
  vite: {
    resolve: { alias: { "~": "./src" } },
  },
});
```

Most Vite options can be passed through the `vite` property.
