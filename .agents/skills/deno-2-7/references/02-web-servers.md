# Building Web Servers

Deno provides powerful built-in APIs for building HTTP servers. This guide covers server creation, routing, middleware, file serving, WebSockets, and advanced patterns.

## Basic HTTP Server

### Using Deno.serve (Recommended)

The `Deno.serve()` API is the preferred way to build HTTP servers:

```typescript
// Simple server
Deno.serve((_req: Request) => {
  return new Response("Hello, world!");
});
```

This starts a server on port 8000 by default.

### Specifying Port and Host

```typescript
// Listen on specific port
Deno.serve({ port: 3000 }, (_req) => {
  return new Response("Hello on port 3000!");
});

// Listen on specific host and port
Deno.serve({ hostname: "0.0.0.0", port: 8080 }, (_req) => {
  return new Response("Accessible from all interfaces!");
});

// Listen on Unix socket
Deno.serve({ hostname: "/tmp/server.sock" }, (_req) => {
  return new Response("Unix socket server!");
});
```

### Async Handler

Handlers can be async and throw errors:

```typescript
Deno.serve(async (req) => {
  try {
    const data = await fetch("https://api.example.com/data");
    const json = await data.json();
    return new Response(JSON.stringify(json));
  } catch (error) {
    return new Response(`Error: ${error.message}`, { status: 500 });
  }
});
```

## Request Handling

### Reading Request URL and Method

```typescript
Deno.serve((req) => {
  const url = new URL(req.url);
  const method = req.method;
  
  return new Response(
    `Method: ${method}\nPath: ${url.pathname}\nSearch: ${url.search}`
  );
});
```

### Reading Request Headers

```typescript
Deno.serve((req) => {
  const contentType = req.headers.get("content-type");
  const authorization = req.headers.get("authorization");
  const userAgent = req.headers.get("user-agent");
  
  return new Response(
    `Content-Type: ${contentType}\nAuth: ${authorization}\nUA: ${userAgent}`
  );
});
```

### Reading Request Body

```typescript
Deno.serve(async (req) => {
  // For JSON body
  const json = await req.json();
  return new Response(JSON.stringify({ received: json }));
  
  // For text body
  // const text = await req.text();
  
  // For form data
  // const formData = await req.formData();
  
  // For raw bytes
  // const bytes = await req.arrayBuffer();
});
```

### Handling POST Requests

```typescript
Deno.serve(async (req) => {
  if (req.method === "POST") {
    const body = await req.json();
    
    // Process the data
    const result = {
      message: `Received: ${body.message}`,
      timestamp: new Date().toISOString()
    };
    
    return new Response(JSON.stringify(result), {
      headers: { "content-type": "application/json" }
    });
  }
  
  return new Response("Send a POST request", { status: 405 });
});
```

## Response Handling

### Setting Status and Headers

```typescript
Deno.serve((req) => {
  return new Response("Created", {
    status: 201,
    headers: {
      "content-type": "text/plain",
      "x-custom-header": "custom-value",
      "cache-control": "max-age=3600"
    }
  });
});
```

### JSON Responses

```typescript
Deno.serve((req) => {
  const data = { message: "Hello", timestamp: Date.now() };
  
  return Response.json(data);
  // Equivalent to:
  // return new Response(JSON.stringify(data), {
  //   headers: { "content-type": "application/json; charset=utf-8" }
  // });
});
```

### HTML Responses

```typescript
Deno.serve((req) => {
  const html = `
    <!DOCTYPE html>
    <html>
      <head><title>Hello</title></head>
      <body><h1>Hello, World!</h1></body>
    </html>
  `;
  
  return new Response(html, {
    headers: { "content-type": "text/html; charset=utf-8" }
  });
});
```

### Redirects

```typescript
Deno.serve((req) => {
  const url = new URL(req.url);
  
  if (url.pathname === "/old") {
    return Response.redirect("https://example.com/new", 301);
  }
  
  return new Response("Not a redirect");
});
```

## Simple Routing

### Path-Based Routing

```typescript
Deno.serve((req) => {
  const url = new URL(req.url);
  const path = url.pathname;
  
  switch (path) {
    case "/":
      return new Response("Home page");
    case "/about":
      return new Response("About page");
    case "/api/users":
      return Response.json({ users: [] });
    default:
      return new Response("Not found", { status: 404 });
  }
});
```

### Parameter Extraction

```typescript
Deno.serve((req) => {
  const url = new URL(req.url);
  const path = url.pathname;
  
  // Match /users/:id pattern
  const match = path.match(/^\/users\/(\d+)$/);
  if (match) {
    const userId = match[1];
    return Response.json({ id: userId, name: "User " + userId });
  }
  
  return new Response("Not found", { status: 404 });
});
```

### Query Parameters

```typescript
Deno.serve((req) => {
  const url = new URL(req.url);
  const searchParams = url.searchParams;
  
  const page = searchParams.get("page") || "1";
  const limit = searchParams.get("limit") || "10";
  const sort = searchParams.get("sort");
  
  return Response.json({
    page: parseInt(page),
    limit: parseInt(limit),
    sort: sort
  });
});
```

## Middleware Pattern

### Creating Middleware

```typescript
type Handler = (req: Request) => Response | Promise<Response>;
type Middleware = (req: Request, next: Handler) => Response | Promise<Response>;

// Logging middleware
const loggingMiddleware: Middleware = async (req, next) => {
  console.log(`${req.method} ${req.url}`);
  const start = Date.now();
  
  const response = await next(req);
  
  const duration = Date.now() - start;
  console.log(`  -> ${response.status} in ${duration}ms`);
  
  return response;
};

// Error handling middleware
const errorMiddleware: Middleware = async (req, next) => {
  try {
    return await next(req);
  } catch (error) {
    console.error(error);
    return new Response(`Internal Server Error: ${error.message}`, {
      status: 500
    });
  }
};

// Compose middleware
function composeMiddleware(...middlewares: Middleware[]): Handler {
  return async (req: Request) => {
    let index = -1;
    
    async function dispatch(i: number): Promise<Response> {
      if (i <= index) {
        throw new Error("next() called multiple times");
      }
      
      index = i;
      
      const middleware = middlewares[i];
      if (middleware === undefined) {
        return new Response("Not found", { status: 404 });
      }
      
      return await middleware(req, dispatch.bind(null, i + 1));
    }
    
    return dispatch(0);
  };
}

// Usage
const handler = composeMiddleware(
  loggingMiddleware,
  errorMiddleware,
  (req) => new Response("Hello!")
);

Deno.serve(handler);
```

### CORS Middleware

```typescript
const corsMiddleware: Middleware = (req, next) => {
  const response = next(req);
  
  // Add CORS headers to response
  Promise.resolve(response).then(res => {
    res.headers.set("Access-Control-Allow-Origin", "*");
    res.headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    res.headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  });
  
  // Handle preflight requests
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "86400"
      }
    });
  }
  
  return response;
};
```

## File Serving

### Serving Static Files

```typescript
import { serveDir } from "@std/http/file-server";

Deno.serve({ port: 8000 }, async (req) => {
  const url = new URL(req.url);
  
  // Serve files from ./static directory
  return serveDir(req, {
    fsRoot: "./static",
    showDenyList: true,
    listing: true, // Enable directory listing
    indexName: "index.html",
    quiet: false,
    cors: true,
    redirectTrailingSlash: true,
    acceptRanges: true
  });
});
```

### Custom File Server

```typescript
Deno.serve(async (req) => {
  const url = new URL(req.url);
  let filePath = url.pathname;
  
  // Serve index.html for root path
  if (filePath === "/") {
    filePath = "/index.html";
  }
  
  try {
    // Prevent directory traversal
    const cleanPath = filePath.replace(/^\/+/, "");
    const fullPath = "./static/" + cleanPath;
    
    const stat = await Deno.stat(fullPath);
    
    if (stat.isDirectory) {
      return serveDir(req, { fsRoot: "./static" });
    }
    
    const file = await Deno.open(fullPath);
    const mimeType = getMimeType(filePath);
    
    return new Response(file.readable, {
      headers: {
        "content-type": mimeType,
        "content-length": stat.size.toString()
      }
    });
  } catch (error) {
    if (error instanceof Deno.errors.NotFound) {
      return new Response("Not found", { status: 404 });
    }
    throw error;
  }
});

function getMimeType(path: string): string {
  const ext = path.split(".").pop()?.toLowerCase();
  const types: Record<string, string> = {
    "html": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "json": "application/json",
    "png": "image/png",
    "jpg": "image/jpeg",
    "gif": "image/gif",
    "svg": "image/svg+xml"
  };
  return types[ext || ""] || "application/octet-stream";
}
```

## WebSockets

### WebSocket Server

```typescript
import { upgradeWebSocket } from "@std/http/upgraded-websocket";

Deno.serve(async (req) => {
  const url = new URL(req.url);
  
  if (url.pathname === "/ws") {
    const conn = await upgradeWebSocket(req);
    
    // Handle incoming messages
    for await (const message of conn) {
      console.log("Received:", message);
      
      // Echo the message back
      await conn.send(message);
    }
  }
  
  return new Response("WebSocket endpoint: /ws");
});
```

### WebSocket with JSON

```typescript
Deno.serve(async (req) => {
  const url = new URL(req.url);
  
  if (url.pathname === "/chat") {
    const conn = await upgradeWebSocket(req);
    
    conn.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data as string);
        
        // Broadcast to all connected clients
        broadcast({
          type: "message",
          content: data.content,
          timestamp: Date.now()
        });
        
      } catch (error) {
        conn.send(JSON.stringify({ error: "Invalid JSON" }));
      }
    });
    
    conn.addEventListener("close", () => {
      console.log("Client disconnected");
    });
    
    // Send welcome message
    conn.send(JSON.stringify({ type: "welcome", message: "Connected!" }));
  }
});

// Simple broadcast implementation
const connections: Set<any> = new Set();

function broadcast(data: unknown) {
  const message = JSON.stringify(data);
  for (const conn of connections) {
    try {
      conn.send(message);
    } catch (error) {
      // Connection may be closed
    }
  }
}
```

## Server Options

### Advanced Configuration

```typescript
Deno.serve({
  // Listen address
  hostname: "0.0.0.0",
  port: 8000,
  
  // ACME/TLS for automatic HTTPS
  // acme: { 
  //   email: "admin@example.com",
  //   hostnames: ["example.com"]
  // },
  
  // TLS configuration
  // cert: "./cert.pem",
  // key: "./key.pem",
  
  // Server name for SNI
  // alpnProtocols: ["h2", "http/1.1"],
  
  // Maximum number of concurrent requests
  // signal: new AbortController().signal,
  
  // Callback when server starts
  async onListen({ hostname, port }) {
    console.log(`Server running at http://${hostname}:${port}/`);
  }
}, handler);
```

### Graceful Shutdown

```typescript
const ac = new AbortController();

const listener = Deno.serve({ 
  port: 8000,
  signal: ac.signal 
}, handler);

// Handle shutdown signals
Deno.addSignalListener("SIGINT", () => {
  console.log("Shutting down...");
  ac.abort();
});

Deno.addSignalListener("SIGTERM", () => {
  console.log("Shutting down...");
  ac.abort();
});

// Wait for server to close
try {
  await listener.finished;
} catch (error) {
  if (error instanceof DOMException && error.name === "AbortError") {
    console.log("Server closed gracefully");
  } else {
    throw error;
  }
}

console.log("Shutdown complete");
```

## Performance Tips

### Keep-Alive Connections

Deno automatically handles HTTP keep-alive. No configuration needed.

### Compression

```typescript
import { encodeGzip } from "@std/encoding/gzip";

Deno.serve(async (req) => {
  const acceptEncoding = req.headers.get("accept-encoding");
  
  if (acceptEncoding?.includes("gzip")) {
    const content = await generateLargeContent();
    const compressed = await encodeGzip(content);
    
    return new Response(compressed, {
      headers: {
        "content-type": "text/plain",
        "content-encoding": "gzip"
      }
    });
  }
  
  return new Response(await generateLargeContent());
});
```

### Connection Pooling for Outgoing Requests

```typescript
// Reuse connections when making multiple requests to same host
const client = new HttpClient();

for (const url of urls) {
  const response = await client.fetch(url);
  // ...
}
```

## Using Third-Party Frameworks

### Oak Framework

```typescript
import { Application, Router } from "https://deno.land/x/oak@v12.6.3/mod.ts";

const app = new Application();
const router = new Router();

router
  .get("/", (ctx) => {
    ctx.body = { message: "Hello" };
  })
  .get("/users/:id", (ctx) => {
    const id = ctx.params.id;
    ctx.body = { id };
  });

app.use(router.routes());
app.use(router.allowedMethods());

await app.listen({ port: 8000 });
```

### Fresh Framework

Fresh is a minimalistic web framework for Deno:

```bash
# Create new Fresh project
deno run -A -r https://fresh.deno.dev my-fresh-app
cd my-fresh-app
deno task dev
```

## Common Patterns

### Health Check Endpoint

```typescript
Deno.serve((req) => {
  const url = new URL(req.url);
  
  if (url.pathname === "/health") {
    return Response.json({ 
      status: "healthy",
      uptime: Deno.env.get("UPTIME") || "unknown"
    });
  }
  
  // ... other routes
});
```

### API Versioning

```typescript
Deno.serve((req) => {
  const url = new URL(req.url);
  const match = url.pathname.match(/^\/api\/v(\d+)/);
  
  if (match) {
    const version = parseInt(match[1]);
    
    if (version === 1) {
      return handleV1(req, url);
    } else if (version === 2) {
      return handleV2(req, url);
    }
  }
  
  return new Response("Not found", { status: 404 });
});
```

### Rate Limiting

```typescript
const requestCounts = new Map<string, { count: number; resetTime: number }>();

const rateLimitMiddleware: Middleware = (req, next) => {
  const ip = req.headers.get("x-forwarded-for") || "unknown";
  const now = Date.now();
  const windowMs = 60 * 1000; // 1 minute
  const maxRequests = 100;
  
  const limit = requestCounts.get(ip);
  
  if (!limit || now > limit.resetTime) {
    requestCounts.set(ip, { count: 1, resetTime: now + windowMs });
  } else if (limit.count >= maxRequests) {
    return new Response("Too many requests", { status: 429 });
  } else {
    limit.count++;
  }
  
  return next(req);
};
```

## Related Topics

- [Permissions and Security](01-permissions.md) - Network permissions for servers
- [API Reference](06-api-reference.md) - HTTP and networking APIs
- [Testing Guide](05-testing.md) - Testing HTTP servers
