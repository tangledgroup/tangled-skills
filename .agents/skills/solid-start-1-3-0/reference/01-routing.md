# Routing

SolidStart uses file-based routing. It traverses the `src/routes/` directory, collects all routes, and makes them accessible via `<FileRoutes />`. Routes are divided into two types:

- **UI routes** — Default export a Solid component (rendered as pages)
- **API routes** — Export named functions matching HTTP methods (`GET`, `POST`, etc.)

## Setting up the router

In `app.tsx`, wrap `<FileRoutes />` with your router of choice. The standard pattern uses `@solidjs/router`:

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

The `root` prop is the root layout for the entire app. Always wrap `props.children` in `<Suspense>` since each component is lazy-loaded automatically. Without it, you may see hydration errors.

## Basic routes

Each file in `routes/` maps to a URL path:

- `/blog` → `routes/blog.tsx`
- `/contact` → `routes/contact.tsx`
- `/` (root) → `routes/index.tsx`

Files named `index` render when no additional URL segments are requested for that directory.

## Nested routes

Create subdirectories for nested paths:

```
routes/
├── blog/
│   ├── article-1.tsx    # /blog/article-1
│   └── article-2.tsx    # /blog/article-2
└── work/
    ├── job-1.tsx        # /work/job-1
    └── job-2.tsx        # /work/job-2
```

## Nested layouts

Create a file with the same name as a route folder to act as a layout:

```
routes/
├── blog.tsx             # Layout for all /blog/* routes
└── blog/
    ├── article-1.tsx    # /blog/article-1
    └── article-2.tsx    # /blog/article-2
```

```tsx title="routes/blog.tsx"
import { RouteSectionProps } from "@solidjs/router";

export default function BlogLayout(props: RouteSectionProps) {
  return (
    <div>
      <h1>Blog</h1>
      {props.children}
    </div>
  );
}
```

Note: `blog/index.tsx` is different from `blog.tsx` — the index file only renders for the exact `/blog` path, while the layout wraps all children.

## Renaming index files

To avoid multiple `index.tsx` files, rename them to match their folder name in parentheses:

```
routes/
└── socials/
    └── (socials).tsx    # Renders at /socials (same as index.tsx)
```

## Escaping nested routes

Use parentheses to create a route that escapes its parent's layout:

```
routes/
├── users/
│   ├── index.tsx        # /users
│   └── projects.tsx     # /users/projects
└── users(details)/
    └── [id].tsx         # /users/1 (separate from /users/*)
```

## Dynamic routes

Use square brackets for dynamic segments:

- `/users/:id` → `routes/users/[id].tsx`
- `/users/:id/:name` → `routes/users/[id]/[name].tsx`
- `/*missing` → `routes/[...missing].tsx`

Access parameters with `useParams`:

```tsx title="routes/users/[id].tsx"
import { useParams } from "@solidjs/router";

export default function UserPage() {
  const params = useParams();
  return <div>User: {params.id}</div>;
}
```

### Optional parameters

Double square brackets make a parameter optional (matches with or without it):

```
routes/
└── users/
    └── [[id]].tsx       # Matches /users and /users/123
```

### Catch-all routes

Prefix with `...` to match any number of remaining segments:

```tsx title="routes/blog/[...post].tsx"
import { useParams } from "@solidjs/router";

export default function BlogPage() {
  const params = useParams();
  // For /blog/hello/world, params.post === "hello/world"
  return <div>Blog: {params.post}</div>;
}
```

## Route groups

Parentheses around folder names create route groups — they organize files without affecting URL structure:

```
routes/
└── (static)/
    ├── about-us/
    │   └── index.tsx    # /about-us (not /(static)/about-us)
    └── contact-us/
        └── index.tsx    # /contact-us
```

## Route configuration

Export a `route` object alongside your component for additional router configuration:

```tsx
import type { RouteDefinition } from "@solidjs/router";

export const route = {
  preload() {
    // Preload data before route renders
  },
} satisfies RouteDefinition;

export default function Page() {
  return <div>Content</div>;
}
```

## API Routes

API routes follow the same file-based conventions but export HTTP method functions instead of a default component:

```tsx title="routes/api/products.ts"
import type { APIEvent } from "@solidjs/start/server";

export async function GET(event: APIEvent) {
  // event.request — standard Request object
  // event.params — dynamic route parameters
  // event.fetch — internal fetch (no origin concerns)
  return { products: [] };
}

export async function POST(event: APIEvent) {
  const body = await event.request.json();
  return { created: true, ...body };
}
```

API routes are prioritized over UI routes at the same path. Returning without a response in a `GET` handler falls back to UI route handling (use `Accept` headers to distinguish).

### Sharing handlers

Bind multiple methods to a single handler:

```ts
async function handler(event: APIEvent) {
  // ...
}

export const GET = handler;
export const POST = handler;
```

### Dynamic API routes

```tsx title="routes/api/product/[category]/[brand].ts"
import type { APIEvent } from "@solidjs/start/server";

export async function GET({ params }: APIEvent) {
  return { category: params.category, brand: params.brand };
}
```

### GraphQL API

```tsx title="routes/graphql.ts"
import { buildSchema, graphql } from "graphql";
import type { APIEvent } from "@solidjs/start/server";

const schema = buildSchema(`
  type Query {
    hello: String
  }
`);

const rootValue = { hello: () => "Hello World" };

const handler = async (event: APIEvent) => {
  const body = await new Response(event.request.body).json();
  return graphql({ rootValue, schema, source: body.query });
};

export const GET = handler;
export const POST = handler;
```

### tRPC API

```tsx title="routes/api/trpc/[trpc].ts"
import type { APIEvent } from "@solidjs/start/server";
import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { appRouter } from "~/lib/router";

const handler = (event: APIEvent) =>
  fetchRequestHandler({
    endpoint: "/api/trpc",
    req: event.request,
    router: appRouter,
    createContext: () => ({}),
  });

export const GET = handler;
export const POST = handler;
```
