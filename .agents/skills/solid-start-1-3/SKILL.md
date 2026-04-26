---
name: solid-start-1-3
description: Fullstack framework for SolidJS providing SSR, SSG, API routes, file-based routing, and server functions. Use when building performant web applications with unified rendering modes (CSR, SSR sync/async/streaming, SSG), isomorphic code execution, single-flight mutations, and deployment adapters for Vercel, Netlify, Cloudflare, AWS, Azure, Bun, Deno, and more.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.0"
tags:
  - solidjs
  - fullstack
  - ssr
  - ssg
  - csr
  - api-routes
  - file-routing
  - server-functions
  - typescript
  - vinxi
  - nitro
  - vite
category: framework
external_references:
  - https://start.solidjs.com/
  - https://github.com/solidjs/solid-start
  - https://docs.solidjs.com/solid-start
---

# SolidStart 1.3

## Overview

SolidStart is an open-source meta-framework built on top of [SolidJS](https://www.solidjs.com/) that unifies the components that make up a web application. It uses [Vinxi](https://vinxi.vercel.app/), an agnostic framework bundler combining [Vite](https://vitejs.dev/) for development and [Nitro](https://nitro.build/) for production server runtime.

SolidStart avoids being opinionated — it provides only the essential pieces to get started. While templates include common tools, SolidStart itself does not ship with a Router or Metadata library, leaving those choices open.

**Key capabilities:**

- **Fine-grained reactivity** — Powered by Solid's fine-grained reactive signals
- **Isomorphic code execution** — Code written once runs correctly on both client and server
- **Multiple rendering modes** — CSR, SSR (sync, async, streaming), and SSG
- **File-based routing** — Routes defined by file structure in `src/routes/`
- **Server functions** — Functions marked `"use server"` that run exclusively on the server
- **Single-flight mutations** — Data updates and re-fetching in a single HTTP request
- **Deployment presets** — Deploy to 20+ platforms via Nitro (Vercel, Netlify, Cloudflare, AWS, Azure, Bun, Deno, Node.js)

## When to Use

- Building fullstack web applications with SolidJS
- Needing SSR, SSG, or CSR with fine-grained reactivity
- Creating API routes alongside UI routes in the same project
- Implementing server-only functions (database access, session management)
- Deploying to edge platforms (Cloudflare Workers, Netlify Edge, Vercel Edge)
- Building applications requiring real-time features (WebSockets)
- Migrating from SolidStart v1 to v2

## Core Concepts

### Isomorphic Code

SolidStart's driving principle is that code should be **isomorphic** — written once and executed correctly whether on the client or server. Components in `src/routes/` run on both sides automatically.

### Rendering Modes

SolidStart supports three rendering paradigms, configurable per-application:

- **Client-Side Rendering (CSR)** — JavaScript runs entirely in the browser
- **Server-Side Rendering (SSR)** — HTML generated on the server with three sub-modes:
  - `sync` — Synchronous rendering via `renderToString`
  - `async` — Async rendering via `renderToStringAsync`
  - `stream` — Streaming HTML via `renderToStream` (default)
- **Static Site Generation (SSG)** — Routes pre-rendered to static HTML at build time

### Server Functions

Functions marked with `"use server"` directive run exclusively on the server. This enables safe database access, session management, and sensitive operations without exposing logic to the client. SolidStart uses [Seroval](https://github.com/lxsmnsyc/seroval) for high-performance serialization of arguments and return values between server and client.

### Single-Flight Mutations

A unique SolidStart feature: when an action updates data on the server, preloaded queries are automatically revalidated and streamed back in the **same HTTP response**. This eliminates the traditional two-request pattern (update + refetch).

## Project Structure

```
my-app/
├── public/              # Static assets (images, fonts, favicon)
├── src/
│   ├── routes/          # File-based routing (pages and API routes)
│   │   └── index.tsx    # Home page
│   ├── app.tsx          # Root component (shared client/server)
│   ├── entry-client.tsx # Browser entry point (hydration)
│   └── entry-server.tsx # Server entry point (SSR document)
├── app.config.ts        # SolidStart/Vite/Nitro configuration
├── package.json
└── tsconfig.json
```

- **`public/`** — Static files served at their exact path relative to this directory
- **`src/`** — Application code, aliased to `~/` for imports
- **`src/routes/`** — UI routes (default export a component) and API routes (export HTTP method functions)
- **`app.tsx`** — Isomorphic root component wrapping the router with `<FileRoutes />`
- **`entry-client.tsx`** — Browser startup, calls `mount(() => <StartClient />, ...)`
- **`entry-server.tsx`** — Server startup, provides document template to `<StartServer>`

## Installation / Setup

Create a new SolidStart project:

```bash
# npm
npm create solid@latest -- -s

# pnpm
pnpm create solid@latest -s

# bun
bun create solid@latest --s
```

The CLI prompts for a template (basic, bare, with-tailwindcss, with-prisma, etc.), SSR preference, and TypeScript/JavaScript.

Then install dependencies and start:

```bash
cd my-app
npm install    # or pnpm install / bun install
npm run dev    # starts on http://localhost:3000
```

Build for production:

```bash
npm run build   # generates production bundles via Vinxi/Nitro
```

## Usage Examples

### Basic page with file-based routing

```tsx title="src/routes/index.tsx"
export default function Index() {
  return <div>Welcome to my site!</div>;
}
```

### Server function for data fetching

```tsx
import { query, createAsync } from "@solidjs/router";

const getPosts = query(async () => {
  "use server";
  return await fetch("https://my-api.com/posts").then((r) => r.json());
}, "posts");

export default function Page() {
  const posts = createAsync(() => getPosts());
  return <ul>{posts()?.map((p) => <li>{p.title}</li>)}</ul>;
}
```

### API route

```tsx title="src/routes/api/hello.ts"
import type { APIEvent } from "@solidjs/start/server";

export async function GET(event: APIEvent) {
  return { message: "Hello from the API!" };
}
```

### Middleware for request logging

```ts title="src/middleware/index.ts"
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: (event) => {
    console.log("Request:", event.request.url);
  },
});
```

```ts title="app.config.ts"
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  middleware: "src/middleware/index.ts",
});
```

## Advanced Topics

**Routing**: File-based routing, nested layouts, dynamic routes, catch-all, route groups → See [Routing](reference/01-routing.md)

**Data Fetching & Mutation**: Server functions, queries, actions, single-flight mutations, form handling → See [Data Fetching & Mutation](reference/02-data-fetching-and-mutation.md)

**Server-Side Rendering**: SSR modes (sync/async/stream), entry points, createHandler, streaming HTML → See [Server-Side Rendering](reference/03-server-side-rendering.md)

**Middleware & Sessions**: Request lifecycle hooks, locals, session management, authentication → See [Middleware & Sessions](reference/04-middleware-and-sessions.md)

**Configuration & Deployment**: defineConfig, Vite/Nitro options, serialization modes, prerendering, deployment presets → See [Configuration & Deployment](reference/05-configuration-and-deployment.md)

**Advanced Topics**: Security (CSP/CORS/CSRF), WebSockets, clientOnly components, static assets, CSS styling → See [Advanced Topics](reference/06-advanced-topics.md)
