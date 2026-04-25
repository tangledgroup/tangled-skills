# SolidStart Troubleshooting Guide

## Common Issues and Solutions

### Hydration Mismatch Errors

**Symptom:** Console warning about hydration mismatch or component not rendering correctly.

**Causes:**
- Server and client render different HTML
- Using `window` or `document` during server render
- Random values generated on both sides

**Solution 1: Use onMount for client-only operations**

```tsx
// ❌ Bad: Accessing window during render
export default function Page() {
  const width = typeof window !== "undefined" ? window.innerWidth : 0;
  return <div>Width: {width}</div>;
}

// ✅ Good: Use onMount
import { createSignal, onMount } from "solid-js";

export default function Page() {
  const [width, setWidth] = createSignal(0);
  
  onMount(() => {
    setWidth(window.innerWidth);
  });
  
  return <div>Width: {width()}</div>;
}
```

**Solution 2: Use client-only components**

```tsx
import clientOnly from "@solidjs/start";

const Chart = clientOnly(() => import("./Chart"), { lazy: false });

export default function Dashboard() {
  return (
    <main>
      <Chart fallback={<div>Loading chart...</div>} />
    </main>
  );
}
```

**Solution 3: Ensure consistent data**

```tsx
// ❌ Bad: Different data on server and client
export default function UserPage() {
  const user = import.meta.env.SSR ? serverUser : clientUser;
  return <div>{user.name}</div>;
}

// ✅ Good: Fetch data consistently
import { createResource } from "solid-js";

export default function UserPage() {
  const [user] = createResource(() => fetch("/api/user").then(r => r.json()));
  
  return user.loading ? <Loading /> : <div>{user().name}</div>;
}
```

### Server Function Not Working

**Symptom:** "Server function not found" or function executes on client.

**Checklist:**
1. File starts with `"use server"` directive (first line)
2. Function is exported (not default export)
3. File is NOT in `src/routes/` directory
4. Build completed successfully

**Correct Structure:**

```tsx
// ✅ src/server/create-user.tsx
"use server"; // Must be first line

export async function createUser(name: string, email: string) {
  // Server-only code here
  return await db.user.create({ data: { name, email } });
}

// ❌ Wrong: Default export
"use server";
export default function createUser() { /* ... */ }

// ❌ Wrong: Missing directive
export async function createUser() { /* ... */ }

// ❌ Wrong: In routes directory
// src/routes/server/create-user.tsx - Won't work!
```

### Route Not Matching

**Symptom:** 404 error or route not loading.

**Checklist:**
1. File is in `src/routes/` (or configured routeDir)
2. File has default export for page routes
3. Filename matches URL pattern correctly

**Dynamic Route Patterns:**

```tsx
// ✅ src/routes/users/[id].tsx → /users/123
export default function UserPage(props: { params: { id: string } }) {
  return <h1>User {props.params.id}</h1>;
}

// ✅ src/routes/blog/[[year]]/index.tsx → /blog or /blog/2024
export default function BlogIndex() { /* ... */ }

// ✅ src/routes/files/[...path].tsx → /files/anything/here
export default function FilesPage(props: { params: { path: string } }) {
  return <h1>Path: {props.params.path}</h1>;
}

// ❌ Wrong: Missing brackets
// src/routes/users/id.tsx - Won't be dynamic!

// ❌ Wrong: No default export for page
export async function GET() { /* API only, no page */ }
```

### Build Errors

**Symptom:** Build fails with TypeScript or Vite errors.

**Solution 1: Clear caches**

```bash
# Remove build artifacts
rm -rf node_modules/.vite .vercel dist

# Reinstall and rebuild
npm ci
npm run build
```

**Solution 2: Check TypeScript configuration**

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
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

**Solution 3: Check Node.js version**

```bash
# Check required version (from .nvmrc or package.json)
cat .nvmrc
# Output: 20.0.0

# Use nvm to switch version
nvm use
```

### API Route Not Returning Response

**Symptom:** API endpoint returns blank or hangs.

**Solution: Ensure all code paths return a response**

```tsx
// ❌ Bad: Missing return
export async function GET(event) {
  const id = new URL(event.request.url).searchParams.get("id");
  const user = await getUser(id);
  // Missing return!
}

// ✅ Good: Always return response
export async function GET(event) {
  const id = new URL(event.request.url).searchParams.get("id");
  const user = await getUser(id);
  
  if (!user) {
    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" }
    });
  }
  
  return new Response(JSON.stringify(user), {
    headers: { "Content-Type": "application/json" }
  });
}

// ✅ Better: Helper function
function json(data: any, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}

export async function GET(event) {
  const user = await getUser(/* ... */);
  return user ? json(user) : json({ error: "Not found" }, 404);
}
```

### CORS Errors

**Symptom:** Browser console shows CORS policy blocked request.

**Solution: Handle OPTIONS and set headers**

```tsx
// src/routes/api/data.tsx
export async function OPTIONS(event) {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*", // Or specific origin
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Access-Control-Max-Age": "86400",
    }
  });
}

export async function GET(event) {
  const response = new Response(JSON.stringify({ data: "..." }), {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    }
  });
  
  return response;
}
```

### Environment Variables Not Available

**Symptom:** `VITE_` variables undefined or server variables exposed.

**Understanding Variable Exposure:**

```tsx
// ✅ Client: VITE_ prefix required
const apiUrl = import.meta.env.VITE_API_URL; // Works

// ❌ Client: No VITE_ prefix
const secret = import.meta.env.SECRET_KEY; // Undefined!

// ✅ Server: Any variable (in server functions/API routes)
const secret = process.env.SECRET_KEY; // Works in server context

// ❌ Server: VITE_ in server is fine but unnecessary
const apiUrl = process.env.VITE_API_URL; // Works but not recommended
```

**Correct Usage:**

```tsx
// Client component
export default function Page() {
  const apiBase = import.meta.env.VITE_API_URL; // Public only
  return <div>API: {apiBase}</div>;
}

// Server function
"use server";
export async function secretAction() {
  const key = process.env.SECRET_KEY; // Server-only
  return /* ... */;
}
```

### Middleware Not Executing

**Symptom:** Middleware code doesn't run.

**Checklist:**
1. Middleware is configured in `app.config.ts`
2. Middleware file exports default middleware
3. Check console for errors in middleware

**Correct Setup:**

```tsx
// src/middleware/auth.ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: async (event) => {
    console.log("Auth middleware running"); // Should appear in logs
    
    const auth = event.request.headers.get("authorization");
    if (!auth) {
      return new Response("Unauthorized", { status: 401 });
    }
  },
});

// app.config.ts
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  middleware: "./src/middleware/auth.ts", // Must be configured!
});
```

### Streaming SSR Issues

**Symptom:** Page loads slowly or streaming not working.

**Solution: Check rendering mode**

```tsx
// src/entry-server.tsx
import { createHandler, StartServer } from "@solidjs/start/server";

export default createHandler(
  () => <StartServer document={/* ... */} />,
  { 
    mode: "stream", // Default and recommended
    
    // Optional: Custom handlers
    onCompleteShell: ({ write }) => {
      console.log("Shell complete");
    },
    onCompleteAll: ({ write }) => {
      console.log("All complete");
    }
  }
);
```

### Type Errors with Route Parameters

**Symptom:** TypeScript can't infer route parameter types.

**Solution: Use RouteParams utility type**

```tsx
// ❌ Manual typing (error-prone)
export default function Page(props: { params: { id: string } }) {
  // ...
}

// ✅ Using RouteParams
import type { RouteParams } from "@solidjs/start/router";

type UserRouteParams = RouteParams<"/users/[id]">;
// Automatically infers: { id: string }

export default function Page(props: { params: UserRouteParams }) {
  const id: string = props.params.id; // Type-safe
}
```

### Performance Issues

**Symptom:** Slow page loads or high bundle size.

**Solution 1: Enable code splitting**

Routes are automatically split, but ensure large libraries aren't in shared code:

```tsx
// ✅ Lazy load heavy components
import { lazy } from "solid-js";

const ChartLibrary = lazy(() => import("./ChartLibrary"));

export default function Dashboard() {
  return (
    <Suspense fallback={<Loading />}>
      <ChartLibrary />
    </Suspense>
  );
}
```

**Solution 2: Optimize images**

```tsx
// Use next-gen formats and lazy loading
<img 
  src="/image.webp" 
  loading="lazy" 
  decoding="async"
  width="800"
  height="600"
/>
```

**Solution 3: Prerender static routes**

```ts
// app.config.ts
export default defineConfig({
  server: {
    prerender: {
      routes: ["/", "/about", "/pricing"], // Pre-render these
    }
  }
});
```

### Development Overlay Issues

**Symptom:** Error overlay not showing or causing hydration mismatch.

**Solution: Configure dev overlay**

```ts
// app.config.ts
export default defineConfig({
  devOverlay: true, // Enable (default)
  
  // Or disable if causing issues
  devOverlay: false,
});
```

### Hot Module Reload Not Working

**Symptom:** Changes don't reflect without manual refresh.

**Checklist:**
1. Entry files have `// @refresh reload` directive
2. Other files have `// @refresh reset` or no directive
3. Vite dev server is running

```tsx
// ✅ src/entry-client.tsx
// @refresh reload
import { mount, StartClient } from "@solidjs/start/client";

mount(() => <StartClient />, document.getElementById("app")!);

// ✅ src/entry-server.tsx
// @refresh reload
import { createHandler, StartServer } from "@solidjs/start/server";

export default createHandler(/* ... */);

// ✅ Regular components (auto-refresh)
export default function Component() {
  return <div>Content</div>;
}
```

### Database Connection Issues

**Symptom:** Database queries fail in server functions.

**Solution: Use connection pooling and proper initialization**

```tsx
// src/lib/db.ts
import { PrismaClient } from "@prisma/client";

// Prevent multiple instances in development
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (import.meta.env.DEV) {
  globalForPrisma.prisma = prisma;
}

// Server function
"use server";
export async function getUsers() {
  return prisma.user.findMany(); // Reuses connection
}
```

## Debugging Techniques

### Enable Verbose Logging

```ts
// app.config.ts
export default defineConfig({
  vite: {
    logLevel: "info", // Or "warn", "error"
  },
});
```

### Check Build Output

```bash
# Analyze bundle size
npm run build -- --analyze

# Or use rollup-plugin-visualizer
npm i -D rollup-plugin-visualizer
```

### Inspect Server Functions

```tsx
import { getServerFunctionMeta } from "@solidjs/start";

export default function Debug() {
  const meta = getServerFunctionMeta();
  
  return (
    <pre>
      {JSON.stringify({
        serverFunctionId: meta?.id,
        isServer: import.meta.env.SSR,
      }, null, 2)}
    </pre>
  );
}
```

### Network Tab Inspection

1. Open browser DevTools > Network tab
2. Check API requests for status codes and responses
3. Verify server function calls show correct headers (`X-Server-Id`)

## Getting Help

If issues persist:

1. **Check official docs:** https://docs.solidjs.com/solid-start
2. **GitHub Issues:** https://github.com/solidjs/solid-start/issues
3. **Discord:** https://discord.com/invite/solidjs
4. **Reddit:** https://reddit.com/r/solidjs

When reporting issues, include:
- SolidStart version (`npm list @solidjs/start`)
- Node.js version (`node --version`)
- Relevant error messages
- Minimal reproduction if possible
