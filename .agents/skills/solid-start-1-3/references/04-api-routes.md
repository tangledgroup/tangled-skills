# SolidStart API Routes Reference

## Creating API Routes

API routes are created by exporting HTTP method handlers from route files:

```tsx
// src/routes/api/users.tsx
export async function GET(event) {
  const users = await fetchAllUsers();
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

## Supported HTTP Methods

All standard HTTP methods are supported:

```tsx
// src/routes/api/resource.tsx
export async function GET(event) {
  // Handle GET requests
  return new Response("GET");
}

export async function POST(event) {
  // Handle POST requests
  return new Response("POST");
}

export async function PUT(event) {
  // Handle PUT requests
  return new Response("PUT");
}

export async function PATCH(event) {
  // Handle PATCH requests
  return new Response("PATCH");
}

export async function DELETE(event) {
  // Handle DELETE requests
  return new Response("DELETE");
}

export async function HEAD(event) {
  // Handle HEAD requests (automatically handled by GET if not defined)
  return new Response(null, { status: 200 });
}

export async function OPTIONS(event) {
  // Handle preflight CORS requests
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
  });
}
```

## Request Event API

The event object provides access to request details:

```tsx
export async function GET(event) {
  // Request object
  const url = new URL(event.request.url);
  const method = event.request.method;
  
  // Headers
  const authHeader = event.request.headers.get("authorization");
  const contentType = event.request.headers.get("content-type");
  
  // Query parameters
  const searchParams = new URLSearchParams(url.search);
  const page = searchParams.get("page");
  const limit = searchParams.get("limit");
  
  // Request body (for POST, PUT, PATCH)
  const body = await event.request.json();
  // Or for form data:
  const formData = await event.request.formData();
  
  // Client address (when available)
  const clientAddress = event.clientAddress;
  
  // Locals (for storing request-scoped data)
  event.locals.userId = "123";
  
  return new Response("OK");
}
```

## Response Handling

### JSON Responses

Helper function for JSON responses:

```tsx
function json(data: any, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    }
  });
}

export async function GET(event) {
  const users = await fetchUsers();
  return json(users);
}

export async function POST(event) {
  const user = await createUser(await event.request.json());
  return json(user, 201);
}
```

### Streaming Responses

Stream large responses:

```tsx
export async function GET(event) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      let i = 0;
      const interval = setInterval(() => {
        controller.enqueue(encoder.encode(`Line ${i++}\n`));
        if (i >= 100) {
          clearInterval(interval);
          controller.close();
        }
      }, 100);
    }
  });
  
  return new Response(stream, {
    headers: {
      "Content-Type": "text/plain",
      "Transfer-Encoding": "chunked",
    }
  });
}
```

### File Downloads

Serve file downloads:

```tsx
export async function GET(event) {
  const filePath = "/path/to/file.pdf";
  const file = await fetch(filePath);
  
  return new Response(file.body, {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": "attachment; filename=document.pdf",
    }
  });
}
```

## Error Handling

### HTTP Errors

Return appropriate status codes:

```tsx
export async function GET(event) {
  const id = new URL(event.request.url).searchParams.get("id");
  
  if (!id) {
    return json({ error: "ID required" }, 400);
  }
  
  const resource = await fetchResource(id);
  
  if (!resource) {
    return json({ error: "Not found" }, 404);
  }
  
  return json(resource);
}
```

### Error Responses

Common error patterns:

```tsx
export async function POST(event) {
  try {
    const body = await event.request.json();
    
    if (!body.email || !body.password) {
      return json(
        { error: "Email and password required" },
        400
      );
    }
    
    const user = await authenticate(body.email, body.password);
    
    if (!user) {
      return json(
        { error: "Invalid credentials" },
        401
      );
    }
    
    return json({ token: generateToken(user) });
    
  } catch (error) {
    if (error instanceof SyntaxError) {
      return json({ error: "Invalid JSON" }, 400);
    }
    
    return json(
      { error: "Internal server error" },
      500
    );
  }
}
```

## Authentication

### Token-Based Auth

```tsx
// src/routes/api/protected.tsx
export async function GET(event) {
  const authHeader = event.request.headers.get("authorization");
  
  if (!authHeader?.startsWith("Bearer ")) {
    return json({ error: "Unauthorized" }, 401);
  }
  
  const token = authHeader.slice(7);
  const user = await verifyToken(token);
  
  if (!user) {
    return json({ error: "Invalid token" }, 401);
  }
  
  // Store user in locals for downstream use
  event.locals.user = user;
  
  return json({ data: "Protected content", user });
}
```

### Session-Based Auth

```tsx
import { parse, serialize } from "cookie-es";

export async function GET(event) {
  const cookies = parse(event.request.headers.get("cookie") || "");
  const sessionId = cookies.session;
  
  if (!sessionId) {
    return json({ error: "Not authenticated" }, 401);
  }
  
  const session = await getSession(sessionId);
  
  if (!session) {
    return json({ error: "Session expired" }, 401);
  }
  
  return json({ user: session.user });
}

export async function POST(event) {
  // Login and create session
  const { email, password } = await event.request.json();
  const user = await authenticate(email, password);
  
  if (!user) {
    return json({ error: "Invalid credentials" }, 401);
  }
  
  const sessionId = generateSessionId();
  await createSession(sessionId, user);
  
  const response = json({ success: true });
  response.headers.set(
    "Set-Cookie",
    serialize("session", sessionId, {
      httpOnly: true,
      secure: import.meta.env.PROD,
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 1 week
    })
  );
  
  return response;
}
```

## CORS Configuration

Handle cross-origin requests:

```tsx
// src/routes/api/public.tsx
export async function OPTIONS(event) {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Access-Control-Max-Age": "86400",
    }
  });
}

export async function GET(event) {
  const response = json({ data: "Public API" });
  response.headers.set("Access-Control-Allow-Origin", "*");
  return response;
}
```

### CORS Helper

```tsx
function withCors(response: Response, origin = "*") {
  response.headers.set("Access-Control-Allow-Origin", origin);
  response.headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  response.headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  return response;
}

export async function GET(event) {
  return withCors(json({ data: "CORS enabled" }));
}
```

## Rate Limiting

Simple in-memory rate limiter:

```tsx
// src/utils/rate-limiter.ts
const requestCounts = new Map<string, { count: number; resetAt: number }>();

export function checkRateLimit(key: string, limit: number, windowMs: number) {
  const now = Date.now();
  const existing = requestCounts.get(key);
  
  if (!existing || now > existing.resetAt) {
    requestCounts.set(key, { count: 1, resetAt: now + windowMs });
    return { allowed: true, remaining: limit - 1 };
  }
  
  if (existing.count >= limit) {
    return { allowed: false, remaining: 0, retryAfter: existing.resetAt - now };
  }
  
  existing.count++;
  requestCounts.set(key, existing);
  return { allowed: true, remaining: limit - existing.count };
}

// src/routes/api/search.tsx
export async function GET(event) {
  const clientIp = event.clientAddress || "unknown";
  const rateLimit = checkRateLimit(clientIp, 100, 60000); // 100 requests per minute
  
  if (!rateLimit.allowed) {
    return json(
      { error: "Rate limit exceeded" },
      429,
      { "Retry-After": String(Math.ceil(rateLimit.retryAfter / 1000)) }
    );
  }
  
  const results = await search(new URL(event.request.url).searchParams.get("q"));
  
  return json(results, 200, {
    "X-RateLimit-Remaining": String(rateLimit.remaining),
  });
}
```

## Request Validation

Validate incoming requests:

```tsx
import { object, string, number, validate } from "seroval";

const createUserSchema = object({
  name: string(),
  email: string().email(),
  age: number().min(0).max(150).optional(),
});

export async function POST(event) {
  const body = await event.request.json();
  const result = validate(createUserSchema, body);
  
  if (result.errors) {
    return json(
      { error: "Validation failed", details: result.errors },
      400
    );
  }
  
  const user = await createUser(result.value);
  return json(user, 201);
}
```

## File Uploads

Handle file uploads:

```tsx
export async function POST(event) {
  const formData = await event.request.formData();
  const file = formData.get("file") as File;
  
  if (!file) {
    return json({ error: "No file provided" }, 400);
  }
  
  // Validate file type
  if (!file.type.startsWith("image/")) {
    return json({ error: "Only images allowed" }, 400);
  }
  
  // Save file
  const buffer = await file.arrayBuffer();
  const filePath = await saveFile(buffer, file.name);
  
  return json({ url: `/uploads/${file.name}` });
}
```

## Webhooks

Receive webhooks:

```tsx
// src/routes/api/webhooks/github.tsx
import { createHmac } from "crypto";

export async function POST(event) {
  const signature = event.request.headers.get("x-hub-signature-256");
  const payload = await event.text();
  
  // Verify signature
  const hmac = createHmac("sha256", process.env.GITHUB_WEBHOOK_SECRET!);
  const expected = "sha256=" + hmac.update(payload).digest("hex");
  
  if (signature !== expected) {
    return json({ error: "Invalid signature" }, 401);
  }
  
  const event_type = event.request.headers.get("x-github-event");
  const data = JSON.parse(payload);
  
  if (event_type === "push") {
    await handlePush(data);
  }
  
  return json({ received: true });
}
```

## GraphQL API

Simple GraphQL endpoint:

```tsx
// src/routes/api/graphql.tsx
export async function POST(event) {
  const { query, variables } = await event.request.json();
  
  try {
    const result = await executeGraphQL(query, variables);
    return json(result);
  } catch (error) {
    return json(
      { errors: [{ message: error.message }] },
      400
    );
  }
}

async function executeGraphQL(query: string, variables?: any) {
  // Implement GraphQL execution
  // Or use a library like graphql-yoga
}
```

## API Versioning

Version your APIs:

```tsx
// src/routes/api/v1/users.tsx
export async function GET(event) {
  // V1 API response format
  return json({
    version: "1.0",
    users: await fetchUsers(),
  });
}

// src/routes/api/v2/users.tsx
export async function GET(event) {
  // V2 API with different format
  return json({
    version: "2.0",
    data: {
      users: await fetchUsersWithRelations(),
    },
    meta: {
      total: 100,
      page: 1,
    }
  });
}
```

## Pagination

Implement cursor-based pagination:

```tsx
export async function GET(event) {
  const searchParams = new URL(event.request.url).searchParams;
  const limit = parseInt(searchParams.get("limit") || "20");
  const cursor = searchParams.get("cursor");
  
  const { items, nextCursor } = await fetchPaginatedItems({
    limit,
    cursor,
  });
  
  return json({
    data: items,
    meta: {
      hasMore: !!nextCursor,
      nextCursor,
    }
  });
}
```

## Health Check Endpoint

```tsx
// src/routes/api/health.tsx
export async function GET(event) {
  const checks = {
    status: "ok",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  };
  
  // Optional: check database connection
  try {
    await db.ping();
    checks.database = "connected";
  } catch {
    checks.database = "disconnected";
    checks.status = "degraded";
  }
  
  return json(checks, checks.status === "ok" ? 200 : 503);
}
```
