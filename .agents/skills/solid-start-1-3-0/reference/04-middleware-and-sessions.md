# Middleware & Sessions

## Middleware

Middleware intercepts HTTP requests and responses. It is configured by exporting from a dedicated file and registering it in `app.config.ts`.

### Basic setup

```ts title="src/middleware/index.ts"
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: (event) => {
    console.log("Request:", event.request.url);
    event.locals.startTime = Date.now();
  },
  onBeforeResponse: (event) => {
    const duration = Date.now() - event.locals.startTime;
    console.log(`Request took ${duration}ms`);
  },
});
```

```ts title="app.config.ts"
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  middleware: "src/middleware/index.ts",
});
```

### Lifecycle events

- **`onRequest`** — Fires before the route handler. Use for: storing data in `event.locals`, modifying request headers, early redirects
- **`onBeforeResponse`** — Fires after the route handler but before sending the response. Use for: setting response headers, logging metrics, modifying response body

### Locals

`event.locals` is a plain JavaScript object for request-scoped data sharing between middleware and server-side code:

```ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: (event) => {
    event.locals.user = { name: "John Wick" };
  },
});
```

Access from server functions via `getRequestEvent`:

```tsx
import { getRequestEvent } from "solid-js/web";

const getUser = query(async () => {
  "use server";
  const event = getRequestEvent();
  return event?.locals?.user;
}, "user");
```

### Headers

Read and modify headers via `event.request.headers` and `event.response.headers` (standard Web API `Headers` interface):

```ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: (event) => {
    const userAgent = event.request.headers.get("user-agent");
    event.response.headers.set("X-Custom-Header", "value");
  },
});
```

Headers set in `onRequest` can be overridden by route handlers. Headers set in `onBeforeResponse` are finalized for the client.

### Cookies

Use Vinxi helpers for cookie management:

```ts
import { createMiddleware } from "@solidjs/start/middleware";
import { getCookie, setCookie } from "vinxi/http";

export default createMiddleware({
  onRequest: (event) => {
    const theme = getCookie(event.nativeEvent, "theme");
    setCookie(event.nativeEvent, "session", "abc123", {
      httpOnly: true,
      secure: true,
      maxAge: 60 * 60 * 24, // 1 day
    });
  },
});
```

### Custom responses

Return a `Response` from middleware to short-circuit the request pipeline:

```ts
import { createMiddleware } from "@solidjs/start/middleware";

export default createMiddleware({
  onRequest: () => {
    return new Response("Unauthorized", { status: 401 });
  },
});
```

### Redirects

Use solid-router's `redirect` helper:

```ts
import { createMiddleware } from "@solidjs/start/middleware";
import { redirect } from "@solidjs/router";

const REDIRECT_MAP: Record<string, string> = {
  "/signup": "/auth/signup",
  "/login": "/auth/login",
};

export default createMiddleware({
  onRequest: (event) => {
    const { pathname } = new URL(event.request.url);
    if (pathname in REDIRECT_MAP) {
      return redirect(REDIRECT_MAP[pathname], 301);
    }
  },
});
```

### JSON responses

Use solid-router's `json` helper:

```ts
import { createMiddleware } from "@solidjs/start/middleware";
import { json } from "@solidjs/router";

export default createMiddleware({
  onRequest: (event) => {
    if (!event.request.headers.get("Authorization")) {
      return json({ error: "Unauthorized" }, { status: 401 });
    }
  },
});
```

### Chaining middleware

Pass an array of functions to execute sequentially:

```ts
import { createMiddleware } from "@solidjs/start/middleware";

function logRequest(event) {
  console.log(event.request.url);
}

function addHeaders(event) {
  event.response.headers.set("X-Powered-By", "SolidStart");
}

export default createMiddleware({
  onRequest: [logRequest, addHeaders],
});
```

### Limitations

- **Do not use middleware for authorization** — it does not run on every request (especially during client-side navigation). Perform authorization checks close to the data source (API routes, server functions)
- **Keep middleware lightweight** — avoid heavy computation or database queries
- **No blocking operations** — CPU-intensive tasks belong in route handlers or background jobs

## Sessions

Sessions maintain state between requests using encrypted and signed cookies.

### How sessions work

1. Server creates a session with a unique ID
2. Session data is encrypted, signed, and stored in a cookie
3. Browser sends the cookie with each request
4. Server decrypts and verifies the signature
5. Session expires after timeout or on sign-out

For larger applications, store session data in a database and keep only the session ID in the cookie.

### Session helpers

Vinxi provides session helpers (server-side only):

- `useSession` — Initialize or retrieve a session
- `getSession` — Get current session or create new
- `updateSession` — Update session data
- `clearSession` — Clear the session

### Creating a session

```ts title="src/lib/session.ts"
import { useSession } from "vinxi/http";

type SessionData = {
  userId?: string;
  theme: "light" | "dark";
};

export async function useThemeSession() {
  "use server";
  const session = await useSession<SessionData>({
    password: process.env.SESSION_SECRET as string,
    name: "theme",
  });

  if (!session.data.theme) {
    await session.update({ theme: "light" });
  }

  return session;
}
```

Generate a strong password (32+ characters):

```bash
openssl rand -base64 32
```

### Getting session data

```ts
export async function getThemeSession() {
  "use server";
  const session = await useThemeSession();
  return session.data.theme;
}
```

### Updating session data

```ts
export async function updateThemeSession(data: SessionData) {
  "use server";
  const session = await useThemeSession();
  await session.update(data);
}
```

### Clearing the session

```ts
export async function clearThemeSession() {
  "use server";
  const session = await useThemeSession();
  await session.clear();
}
```

### Session with authentication

Combine sessions with server functions for auth:

```tsx
import { query, redirect } from "@solidjs/router";
import { useSession } from "vinxi/http";

const getCurrentUserQuery = query(async (id: string) => {
  "use server";
  const session = await useSession({
    password: process.env.SESSION_SECRET as string,
    name: "session",
  });

  if (session.data.userId) {
    return await db.users.get({ id: session.data.userId });
  } else {
    throw redirect("/login");
  }
}, "currentUser");
```
