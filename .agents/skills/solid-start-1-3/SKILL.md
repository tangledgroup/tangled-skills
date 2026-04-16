---
name: solid-start-1-3
description: Fullstack framework for SolidJS providing SSR, SSG, API routes, and file-based routing. Use when building performant web applications with unified rendering modes, server functions, and deployment adapters for Vercel, Netlify, Cloudflare, and more.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - solidjs
  - fullstack
  - ssr
  - ssg
  - api-routes
  - file-routing
  - server-functions
  - typescript
category: framework
required_environment_variables: []
---

# SolidStart 1.3

SolidStart is a fullstack framework for SolidJS that brings fine-grained reactivity to the entire stack. Built with unified rendering and isomorphic code execution, it enables highly performant and scalable web applications with SSR, SSG, streaming, and API routes.

## When to Use

- Building fullstack SolidJS applications requiring server-side rendering
- Creating apps with file-based routing and API endpoints
- Deploying to platforms like Vercel, Netlify, Cloudflare, or Node.js servers
- Implementing server functions for secure backend logic
- Needing streaming SSR for faster time-to-interactive
- Building static sites with prerendering capabilities

## Quick Start

### Installation

Create a new SolidStart project:

```bash
# Using npm
npm create solid@latest -- -s

# Using pnpm
pnpm create solid@latest -s

# Using bun
bun create solid@latest --s
```

### Project Structure

```
my-app/
├── public/           # Static assets (icons, images, fonts)
├── src/              # Core application (aliased to ~/)
│   ├── routes/       # File-based routing for pages and APIs
│   ├── app.tsx       # Root component with Router
│   ├── entry-client.tsx    # Client-side hydration entry
│   └── entry-server.tsx    # Server-side rendering entry
├── app.config.ts     # SolidStart configuration
├── package.json
└── tsconfig.json
```

See [Core Concepts](references/01-core-concepts.md) for detailed architecture explanation.

### Basic Configuration

Create `app.config.ts`:

```ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  ssr: true, // false for CSR-only mode
  server: { preset: "netlify" }, // Deployment adapter
});
```

Common presets include: `vercel`, `netlify`, `cloudflare`, `node-server`, `bun-server`, `deno-server`.

See [Configuration Reference](references/02-configuration.md) for all options.

## Common Operations

### Creating Routes

Routes are defined in `src/routes/`:

```tsx
// src/routes/index.tsx - renders at /
export default function Home() {
  return <h1>Home Page</h1>;
}

// src/routes/about.tsx - renders at /about
export default function About() {
  return <h1>About Page</h1>;
}

// src/routes/[id].tsx - dynamic route at /:id
export default function DynamicPage(props: { params: { id: string } }) {
  return <h1>ID: {props.params.id}</h1>;
}

// src/routes/blog/[slug]/index.tsx - nested dynamic route
export default function BlogPost() {
  return <article>Blog post content</article>;
}
```

See [Routing Guide](references/03-routing.md) for advanced patterns.

### API Routes

Create API endpoints by exporting HTTP methods:

```tsx
// src/routes/api/users.tsx
export async function GET(event) {
  const users = await fetchUsersFromDatabase();
  return new Response(JSON.stringify(users), {
    headers: { "Content-Type": "application/json" }
  });
}

export async function POST(event) {
  const body = await event.request.json();
  const user = await createUser(body);
  return new Response(JSON.stringify(user), {
    status: 201,
    headers: { "Content-Type": "application/json" }
  });
}
```

See [API Routes Reference](references/04-api-routes.md) for complete HTTP method support.

### Server Functions

Use server functions for secure backend logic:

```tsx
// src/server/create-user.tsx
"use server";

export async function createUser(name: string, email: string) {
  // This code runs only on the server
  const user = await db.user.create({ data: { name, email } });
  return user;
}
```

Usage in components:

```tsx
import { createUser } from "~/server/create-user";

export default function UserForm() {
  const handleSubmit = async (e) => {
    e.preventDefault();
    const user = await createUser("John", "john@example.com");
    console.log(user);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Name" />
      <input name="email" placeholder="Email" />
      <button type="submit">Create User</button>
    </form>
  );
}
```

See [Server Functions Guide](references/05-server-functions.md) for validation and error handling.

### Client-Only Components

For components that should only run on the client:

```tsx
import clientOnly from "@solidjs/start";

const ClientComponent = clientOnly(() => import("./ClientComponent"), {
  lazy: false, // Load immediately or lazily
});

export default function Page() {
  return (
    <main>
      <ClientComponent fallback={<div>Loading...</div>} />
    </main>
  );
}
```

See [Rendering Modes](references/01-core-concepts.md#rendering-modes) for details.

## Build and Deploy

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

After building, deployment instructions are provided based on your preset.

See [Deployment Guide](references/06-deployment.md) for platform-specific configurations.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Architecture, rendering modes, and isomorphic patterns
- [`references/02-configuration.md`](references/02-configuration.md) - Complete app.config.ts options and Vite integration
- [`references/03-routing.md`](references/03-routing.md) - File-based routing, dynamic routes, nested layouts
- [`references/04-api-routes.md`](references/04-api-routes.md) - HTTP methods, request/response handling, middleware
- [`references/05-server-functions.md`](references/05-server-functions.md) - Server functions, validation with seroval, single-flight
- [`references/06-deployment.md`](references/06-deployment.md) - Adapters for Vercel, Netlify, Cloudflare, Node.js, Bun, Deno

## Troubleshooting

### Hydration Mismatch

Ensure server and client render identical HTML. Check for:
- `window` or `document` references in rendered components
- Different data between server and client
- Use `onMount` for client-only operations

### Server Function Not Working

Verify:
- File contains `"use server"` directive at top
- Function is exported (not default export)
- Serialization mode matches your CSP requirements (`js` mode requires `eval`)

### Route Not Matching

Check:
- File is in `src/routes/` directory
- File has default export for page routes
- Dynamic params use correct syntax: `[param].tsx` or `[[optional]].tsx`

See [Troubleshooting Guide](references/07-troubleshooting.md) for more issues.
