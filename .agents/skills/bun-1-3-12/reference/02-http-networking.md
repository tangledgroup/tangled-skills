# HTTP & Networking

## Bun.serve — HTTP Server

`Bun.serve` starts a high-performance HTTP server using Web-standard `fetch` API patterns.

### Basic Setup with Routes (v1.2.3+)

```ts
const server = Bun.serve({
  port: 3000,
  routes: {
    // Static response
    "/": () => new Response("Hello!"),

    // Dynamic route with params
    "/users/:id": req => new Response(`User ${req.params.id}`),

    // Per-HTTP method handlers
    "/api/posts": {
      GET: () => new Response("List posts"),
      POST: async req => Response.json({ created: true, ...(await req.json()) }),
    },

    // Wildcard route
    "/api/*": Response.json({ message: "Not found" }, { status: 404 }),

    // Redirect
    "/blog/hello": Response.redirect("/blog/hello/world"),

    // Serve a file lazily
    "/favicon.ico": Bun.file("./favicon.ico"),
  },

  // Fallback for unmatched routes (required if Bun < 1.2.3)
  fetch(req) {
    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Server running at ${server.url}`);
```

### Legacy fetch Handler (pre-1.2.3 or fallback)

```ts
const server = Bun.serve({
  port: 3000,
  fetch(req, server) {
    const url = new URL(req.url);

    if (url.pathname === "/") {
      return new Response("Hello!");
    }

    return new Response("Not Found", { status: 404 });
  },
});
```

### Port Configuration

```ts
Bun.serve({
  port: 8080,          // explicit port
  // or omit for default: $BUN_PORT > $PORT > $NODE_PORT > 3000
  hostname: "0.0.0.0", // default
});
```

Random available port:

```ts
const server = Bun.serve({ port: 0, fetch(req) { return new Response("ok"); } });
console.log(server.port); // randomly assigned port
console.log(server.url);  // http://localhost:<port>
```

### Unix Domain Sockets

```ts
Bun.serve({
  unix: "/tmp/my-socket.sock",
  fetch(req) { return new Response("ok"); },
});
```

Abstract namespace sockets (Linux):

```ts
Bun.serve({
  unix: "\0my-abstract-socket",
  fetch(req) { return new Response("ok"); },
});
```

### Idle Timeout

Default is 10 seconds of inactivity. Configure with `idleTimeout` (in seconds, max 255, 0 to disable):

```ts
Bun.serve({
  idleTimeout: 30,
  fetch(req) { return new Response("ok"); },
});
```

For long-lived streams (SSE), disable timeout per-request:

```ts
server.timeout(req, 0);
```

### HTML Imports for Full-Stack Apps

Import HTML files directly into server code:

```ts
import myApp from "./index.html";

Bun.serve({
  routes: {
    "/": myApp,
  },
});
```

**Development (`bun --hot`)**: Assets bundled on-demand with hot module replacement.

**Production (`bun build --target=bun`)**: Pre-built manifest served with zero runtime bundling overhead.

### Graceful Shutdown

```ts
const server = Bun.serve({ fetch(req) { return new Response("ok"); } });

process.on("SIGINT", () => {
  server.stop(); // or server.stop(true) to abort in-flight requests
});
```

## WebSockets

Bun implements the standard `WebSocket` API for both client and server.

### Server-Side WebSockets

```ts
Bun.serve({
  port: 3000,
  fetch(req, server) {
    const url = new URL(req.url);
    if (url.pathname === "/ws") {
      const [client, response] = WebSocket.pair();
      server.accept(client);
      client.addEventListener("message", msg => {
        client.send(`Echo: ${msg}`);
      });
      return response;
    }
    return new Response("Use /ws");
  },
});
```

### Client-Side WebSockets

```ts
const ws = new WebSocket("ws://localhost:3000/ws");

ws.addEventListener("open", () => {
  ws.send("Hello!");
});

ws.addEventListener("message", event => {
  console.log("Received:", event.data);
});
```

## TCP Sockets

```ts
const server = Bun.serve({
  port: 8080,
  socket: {
    onOpen(socket) {
      console.log("Client connected");
    },
    onMessage(socket, message) {
      socket.text(`Echo: ${message}`);
    },
    onClose(socket, code, reason) {
      console.log("Client disconnected");
    },
  },
});
```

## UDP Sockets

```ts
const socket = Bun.UDPSocket.open(41234);

socket.onmessage = (message, rinfo) => {
  console.log(`Received ${message.length} bytes from ${rinfo.address}:${rinfo.port}`);
  socket.send(message, rinfo.port, rinfo.address);
};
```

## DNS Resolution

```ts
// Resolve a hostname
const addresses = await Bun.dns.resolve("example.com");
console.log(addresses); // [{ address: "93.184.216.34", family: 4 }]

// Reverse lookup
const hostnames = await Bun.dns.reverse("93.184.216.34");
```

## fetch API

Bun implements the Web `fetch` standard with additional capabilities:

```ts
// Basic fetch
const res = await fetch("https://example.com");
const text = await res.text();

// POST with JSON
const response = await fetch("https://api.example.com/data", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ key: "value" }),
});

// Bun-specific: read file as request body
const response = await fetch("https://api.example.com/upload", {
  method: "POST",
  body: Bun.file("./data.json"),
});

// Bun-specific: local file fetch
const localFile = await fetch("file:///path/to/file.txt");
```

## TLS/HTTPS

```ts
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
```

Or inline certificates:

```ts
Bun.serve({
  port: 443,
  tls: {
    cert: fs.readFileSync("./cert.pem"),
    key: fs.readFileSync("./key.pem"),
  },
  fetch(req) {
    return new Response("Secure!");
  },
});
```
