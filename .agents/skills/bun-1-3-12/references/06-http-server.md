# Bun HTTP Server

Bun provides a built-in, high-performance HTTP server with native support for routing, cookies, TLS, WebSockets, and metrics. It's significantly faster than Node.js `http` module while maintaining API compatibility.

## Basic HTTP Server

### Simple Server

```typescript title="server.ts"
Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello, world!");
  },
});

console.log("Server running on http://localhost:3000");
```

Run with:
```bash
bun run server.ts
```

### Request Handling

```typescript
Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);
    
    // Get query parameters
    const name = url.searchParams.get("name") || "World";
    
    // Read request body
    const body = await req.json();
    
    return new Response(JSON.stringify({
      message: `Hello, ${name}!`,
      received: body,
    }), {
      headers: { "Content-Type": "application/json" },
    });
  },
});
```

## Server Configuration

### Basic Options

```typescript
const server = Bun.serve({
  // Port to listen on (default: 3000)
  port: 3000,
  
  // Host to bind to (default: all interfaces)
  hostname: "0.0.0.0",
  
  // Request handler
  fetch(req) { /* ... */ },
  
  // TLS configuration (see below)
  tls: {
    certPath: "./cert.pem",
    keyPath: "./key.pem",
  },
  
  // Development mode (pretty errors, etc.)
  development: true,
  
  // Request timeout in milliseconds
  idleTimeout: 30000,
});

console.log(`Server running on port ${server.port}`);
```

### Advanced Options

```typescript
Bun.serve({
  port: 3000,
  
  // IPv6 support
  ipv6: false,
  
  // Keep-alive timeout
  keepAlive: true,
  
  // Maximum request body size (bytes)
  requestBodySize: 1024 * 1024, // 1MB
  
  // Compression (automatic for responses > threshold)
  compression: "auto",
  
  // WebSocket upgrade handler
  websocket: {
    open(ws) { console.log("Client connected"); },
    message(ws, message) { ws.message(message); },
    close(ws) { console.log("Client disconnected"); },
  },
});
```

## Routing

### Manual Routing

```typescript title="server.ts"
function route(req: Request): Response {
  const url = new URL(req.url);
  const path = url.pathname;
  
  if (path === "/") {
    return new Response("Home page");
  }
  
  if (path === "/api/users") {
    return new Response(JSON.stringify({ users: [] }), {
      headers: { "Content-Type": "application/json" },
    });
  }
  
  if (path.startsWith("/api/users/")) {
    const id = path.split("/")[3];
    return new Response(JSON.stringify({ id }), {
      headers: { "Content-Type": "application/json" },
    });
  }
  
  return new Response("Not Found", { status: 404 });
}

Bun.serve({
  port: 3000,
  fetch: route,
});
```

### Request Method Handling

```typescript
function handle(req: Request): Response {
  const url = new URL(req.url);
  
  switch (req.method) {
    case "GET":
      return handleGet(url);
    case "POST":
      return handlePost(req, url);
    case "PUT":
      return handlePut(req, url);
    case "DELETE":
      return handleDelete(url);
    default:
      return new Response("Method Not Allowed", { status: 405 });
  }
}

async function handlePost(req: Request, url: URL): Promise<Response> {
  const body = await req.json();
  return new Response(JSON.stringify({ created: true }), {
    status: 201,
    headers: { "Content-Type": "application/json" },
  });
}

Bun.serve({ port: 3000, fetch: handle });
```

### Router Library Pattern

Create a simple router:

```typescript title="router.ts"
type RouteHandler = (req: Request, params: Record<string, string>) => Response | Promise<Response>;

class Router {
  private routes: Map<string, Map<string, RouteHandler>> = new Map();
  
  add(method: string, path: string, handler: RouteHandler) {
    if (!this.routes.has(path)) {
      this.routes.set(path, new Map());
    }
    this.routes.get(path)!.set(method, handler);
  }
  
  get(path: string, handler: RouteHandler) {
    this.add("GET", path, handler);
  }
  
  post(path: string, handler: RouteHandler) {
    this.add("POST", path, handler);
  }
  
  handle(req: Request): Response | Promise<Response> {
    const url = new URL(req.url);
    const path = url.pathname;
    const method = req.method;
    
    const methods = this.routes.get(path);
    if (methods && methods.has(method)) {
      return methods.get(method)! (req, {});
    }
    
    return new Response("Not Found", { status: 404 });
  }
}

const router = new Router();

router.get("/", () => new Response("Home"));
router.post("/api/users", async (req) => {
  const body = await req.json();
  return new Response(JSON.stringify({ created: true }), {
    headers: { "Content-Type": "application/json" },
  });
});

Bun.serve({ port: 3000, fetch: router.handle.bind(router) });
```

## Request Handling

### Reading Request Body

```typescript
async function handle(req: Request): Promise<Response> {
  // JSON body
  const json = await req.json();
  
  // Text body
  const text = await req.text();
  
  // Form data
  const formData = await req.formData();
  const username = formData.get("username");
  
  // Raw bytes
  const bytes = await req.arrayBuffer();
  const buffer = new Uint8Array(bytes);
  
  // Stream (for large files)
  const stream = req.body;
}
```

### Request Headers

```typescript
function handle(req: Request): Response {
  // Get header (case-insensitive)
  const contentType = req.headers.get("Content-Type");
  const authorization = req.headers.get("Authorization");
  
  // Check if header exists
  if (req.headers.has("X-Custom-Header")) {
    // ...
  }
  
  // Iterate all headers
  for (const [key, value] of req.headers) {
    console.log(`${key}: ${value}`);
  }
  
  return new Response("OK");
}
```

### Request URL and Query Params

```typescript
function handle(req: Request): Response {
  const url = new URL(req.url);
  
  // Pathname
  const path = url.pathname; // "/api/users/123"
  
  // Search params
  const page = url.searchParams.get("page"); // "1"
  const limit = url.searchParams.get("limit"); // "10"
  
  // All params as object
  const params: Record<string, string> = {};
  for (const [key, value] of url.searchParams) {
    params[key] = value;
  }
  
  // Origin
  const origin = url.origin; // "http://localhost:3000"
  
  return new Response(JSON.stringify({ path, page, limit }));
}
```

## Response Handling

### Basic Responses

```typescript
function handle(req: Request): Response {
  // Text response
  return new Response("Hello, world!");
  
  // JSON response
  return new Response(JSON.stringify({ message: "Hello" }), {
    headers: { "Content-Type": "application/json" },
  });
  
  // HTML response
  return new Response(`<!DOCTYPE html><html><body>Hello</body></html>`, {
    headers: { "Content-Type": "text/html" },
  });
  
  // File response
  const file = Bun.file("./path/to/file.txt");
  return new Response(file);
}
```

### Status Codes

```typescript
function handle(req: Request): Response {
  // Success
  return new Response("OK", { status: 200 });
  return new Response("Created", { status: 201 });
  
  // Client errors
  return new Response("Not Found", { status: 404 });
  return new Response("Bad Request", { status: 400 });
  return new Response("Unauthorized", { status: 401 });
  
  // Server errors
  return new Response("Internal Server Error", { status: 500 });
}
```

### Response Headers

```typescript
function handle(req: Request): Response {
  return new Response("Hello", {
    status: 200,
    headers: {
      "Content-Type": "text/plain",
      "X-Custom-Header": "custom-value",
      "Cache-Control": "max-age=3600",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

// Or using Headers object
const headers = new Headers();
headers.set("Content-Type", "text/plain");
headers.append("Set-Cookie", "session=abc123; Path=/");

return new Response("Hello", { headers });
```

### Streaming Responses

```typescript
async function* generateStream() {
  for (let i = 0; i < 10; i++) {
    yield `Line ${i}\n`;
    await new Promise(r => setTimeout(r, 100));
  }
}

function handle(req: Request): Response {
  return new Response(generateStream(), {
    headers: { "Content-Type": "text/plain" },
  });
}
```

## Cookies

### Reading Cookies

```typescript
function handle(req: Request): Response {
  const cookieHeader = req.headers.get("Cookie");
  
  if (!cookieHeader) {
    return new Response("No cookies");
  }
  
  // Parse cookies manually
  const cookies: Record<string, string> = {};
  cookieHeader.split("; ").forEach(cookie => {
    const [key, value] = cookie.split("=");
    cookies[key.trim()] = decodeURIComponent(value.trim());
  });
  
  const sessionId = cookies["session_id"];
  
  return new Response(`Session: ${sessionId}`);
}
```

### Setting Cookies

```typescript
function handle(req: Request): Response {
  const response = new Response("OK");
  
  // Simple cookie
  response.headers.append("Set-Cookie", "username=john; Path=/");
  
  // Cookie with options
  response.headers.append("Set-Cookie", 
    "session=abc123; " +
    "Path=/; " +
    "HttpOnly; " +
    "Secure; " +
    "SameSite=Strict; " +
    "Max-Age=3600"
  );
  
  return response;
}
```

### Cookie Helper Functions

```typescript
function setCookie(res: Response, name: string, value: string, options: {
  path?: string;
  maxAge?: number;
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: "Strict" | "Lax" | "None";
}) {
  let cookie = `${name}=${encodeURIComponent(value)}`;
  
  if (options.path) cookie += `; Path=${options.path}`;
  if (options.maxAge) cookie += `; Max-Age=${options.maxAge}`;
  if (options.httpOnly) cookie += "; HttpOnly";
  if (options.secure) cookie += "; Secure";
  if (options.sameSite) cookie += `; SameSite=${options.sameSite}`;
  
  res.headers.append("Set-Cookie", cookie);
}

// Usage
const res = new Response("OK");
setCookie(res, "session", "abc123", {
  path: "/",
  maxAge: 3600,
  httpOnly: true,
  secure: true,
  sameSite: "Strict",
});
```

## TLS/HTTPS

### Self-Signed Certificate

Generate certificate:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Start HTTPS server:
```typescript
Bun.serve({
  port: 443,
  tls: {
    certPath: "./cert.pem",
    keyPath: "./key.pem",
  },
  fetch(req) {
    return new Response("Secure!");
  },
});

console.log("HTTPS server running on https://localhost");
```

### PEM Format

```typescript
Bun.serve({
  port: 443,
  tls: {
    // Or use inline PEM strings
    cert: `-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----`,
    key: `-----PRIVATE KEY-----
...
-----END PRIVATE KEY-----`,
  },
  fetch(req) {
    return new Response("Secure!");
  },
});
```

### Let's Encrypt Integration

Use a tool like certbot to obtain certificates, then point to them:

```typescript
Bun.serve({
  port: 443,
  tls: {
    certPath: "/etc/letsencrypt/live/example.com/fullchain.pem",
    keyPath: "/etc/letsencrypt/live/example.com/privkey.pem",
  },
  fetch(req) {
    return new Response("Secure!");
  },
});
```

## WebSockets

### Basic WebSocket Server

```typescript title="websocket.ts"
Bun.serve({
  port: 3000,
  
  websocket: {
    // Called when client connects
    open(ws) {
      console.log("Client connected");
      ws.message("Welcome!");
    },
    
    // Called when message received
    message(ws, message: string) {
      console.log("Received:", message);
      
      // Echo back
      ws.message(`Server received: ${message}`);
    },
    
    // Called when client disconnects
    close(ws) {
      console.log("Client disconnected");
    },
    
    // Called on error
    error(ws, err) {
      console.error("WebSocket error:", err);
    },
  },
  
  // HTTP fallback
  fetch(req) {
    return new Response("WebSocket server running. Connect via ws://localhost:3000");
  },
});
```

### WebSocket Client Usage

```html title="index.html"
<!DOCTYPE html>
<html>
<body>
  <script>
    const ws = new WebSocket("ws://localhost:3000");
    
    ws.onopen = () => {
      console.log("Connected");
      ws.send("Hello, server!");
    };
    
    ws.onmessage = (event) => {
      console.log("Received:", event.data);
    };
    
    ws.onerror = (error) => {
      console.error("Error:", error);
    };
    
    ws.onclose = () => {
      console.log("Disconnected");
    };
  </script>
</body>
</html>
```

### WebSocket with Authentication

```typescript
Bun.serve({
  port: 3000,
  
  websocket: {
    // Upgrade handler (before connection is established)
    upgrade(req, server, tcp) {
      const auth = req.headers.get("Authorization");
      
      if (!auth || !auth.startsWith("Bearer ")) {
        return new Response("Unauthorized", { status: 401 });
      }
      
      // Valid token - allow upgrade
      return undefined;
    },
    
    open(ws) {
      ws.message("Authenticated connection established");
    },
    
    message(ws, message) {
      ws.message(`Echo: ${message}`);
    },
  },
});
```

### Broadcasting to All Clients

```typescript
const clients = new Set<Bun.WebSocket>();

Bun.serve({
  port: 3000,
  
  websocket: {
    open(ws) {
      clients.add(ws);
      console.log(`${clients.size} clients connected`);
    },
    
    message(ws, message) {
      // Broadcast to all clients
      clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.message(`Broadcast: ${message}`);
        }
      });
    },
    
    close(ws) {
      clients.delete(ws);
      console.log(`${clients.size} clients remaining`);
    },
  },
});
```

## Error Handling

### Try-Catch in Handler

```typescript
Bun.serve({
  port: 3000,
  
  async fetch(req) {
    try {
      const result = await riskyOperation();
      return new Response(JSON.stringify(result), {
        headers: { "Content-Type": "application/json" },
      });
    } catch (error) {
      console.error("Request error:", error);
      
      return new Response(JSON.stringify({ 
        error: "Internal Server Error",
        message: error instanceof Error ? error.message : "Unknown error"
      }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  },
});
```

### Global Error Handler

```typescript
function createErrorHandler() {
  return async (req: Request) => {
    try {
      return await handleRequest(req);
    } catch (error) {
      if (error instanceof SyntaxError) {
        return new Response("Invalid JSON", { status: 400 });
      }
      
      if (error instanceof NotFoundError) {
        return new Response("Not Found", { status: 404 });
      }
      
      console.error("Unhandled error:", error);
      return new Response("Internal Server Error", { status: 500 });
    }
  };
}

Bun.serve({
  port: 3000,
  fetch: createErrorHandler(),
});
```

## CORS

### Basic CORS Setup

```typescript
function withCORS(res: Response): Response {
  const headers = new Headers(res.headers);
  
  headers.set("Access-Control-Allow-Origin", "*");
  headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  headers.set("Access-Control-Max-Age", "86400");
  
  return new Response(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers,
  });
}

Bun.serve({
  port: 3000,
  
  fetch(req) {
    // Handle preflight requests
    if (req.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }
    
    const response = new Response("Hello");
    return withCORS(response);
  },
});
```

### Restricted CORS

```typescript
function withCORS(res: Response, origin: string | null): Response {
  const headers = new Headers(res.headers);
  
  // Only allow specific origins
  const allowedOrigins = ["https://app.example.com", "http://localhost:3000"];
  
  if (origin && allowedOrigins.includes(origin)) {
    headers.set("Access-Control-Allow-Origin", origin);
    headers.set("Access-Control-Allow-Credentials", "true");
  }
  
  headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE");
  headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  
  return new Response(res.body, { status: res.status, headers });
}

Bun.serve({
  port: 3000,
  
  fetch(req) {
    const origin = req.headers.get("Origin") || null;
    
    if (req.method === "OPTIONS") {
      return withCORS(new Response(null), origin);
    }
    
    return withCORS(new Response("Hello"), origin);
  },
});
```

## Middleware Pattern

### Request Logging

```typescript
function loggingMiddleware(next: (req: Request) => Response | Promise<Response>) {
  return async (req: Request) => {
    const start = Date.now();
    
    console.log(`${req.method} ${new URL(req.url).pathname}`);
    
    const response = await next(req);
    
    const duration = Date.now() - start;
    console.log(`  -> ${response.status} in ${duration}ms`);
    
    return response;
  };
}

// Usage
const handle = loggingMiddleware(async (req) => {
  return new Response("Hello");
});

Bun.serve({ port: 3000, fetch: handle });
```

### Chaining Middleware

```typescript
type Middleware = (req: Request, next: () => Response | Promise<Response>) => Response | Promise<Response>;

const middleware: Middleware[] = [];

function use(fn: Middleware) {
  middleware.push(fn);
}

function compose(req: Request): Response | Promise<Response> {
  let index = -1;
  
  return function next(): Response | Promise<Response> {
    index++;
    
    if (index >= middleware.length) {
      return handleRequest(req);
    }
    
    return middleware[index](req, next);
  };
}

// Define middleware
use((req, next) => {
  console.log("Before request");
  const res = next();
  console.log("After request");
  return res;
});

use((req, next) => {
  const auth = req.headers.get("Authorization");
  if (!auth) {
    return new Response("Unauthorized", { status: 401 });
  }
  return next();
});

// Final handler
function handleRequest(req: Request): Response {
  return new Response("Hello");
}

Bun.serve({ port: 3000, fetch: compose });
```

## Performance Tips

1. **Use streaming for large responses**: Don't load entire file into memory
2. **Enable compression**: Bun automatically compresses responses > 1KB
3. **Use HTTP/2**: Supported automatically with TLS
4. **Keep handlers async**: Avoid blocking the event loop
5. **Cache static files**: Use filesystem caching for repeated requests
6. **Use connection pooling**: For database/API calls

## Graceful Shutdown

```typescript
const server = Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello");
  },
});

console.log(`Server running on http://localhost:${server.port}`);

// Handle shutdown signals
process.on("SIGINT", () => {
  console.log("Shutting down...");
  server.stop();
  process.exit(0);
});

process.on("SIGTERM", () => {
  console.log("Shutting down...");
  server.stop();
  process.exit(0);
});
```

## Metrics and Monitoring

### Basic Metrics

```typescript
let requestCount = 0;
let errorCount = 0;
const responseTimes: number[] = [];

Bun.serve({
  port: 3000,
  
  async fetch(req) {
    const start = Date.now();
    requestCount++;
    
    try {
      const response = await handleRequest(req);
      responseTimes.push(Date.now() - start);
      
      // Keep last 1000 response times
      if (responseTimes.length > 1000) responseTimes.shift();
      
      return response;
    } catch (error) {
      errorCount++;
      throw error;
    }
  },
});

// Expose metrics endpoint
function handleRequest(req: Request): Response {
  const url = new URL(req.url);
  
  if (url.pathname === "/metrics") {
    const avgResponseTime = responseTimes.length > 0 
      ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length 
      : 0;
    
    return new Response(JSON.stringify({
      requestCount,
      errorCount,
      avgResponseTime: Math.round(avgResponseTime * 100) / 100,
      uptime: process.uptime(),
    }), {
      headers: { "Content-Type": "application/json" },
    });
  }
  
  return new Response("Hello");
}
```
