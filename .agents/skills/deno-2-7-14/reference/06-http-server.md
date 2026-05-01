# HTTP Server

## Built-in HTTP Server

Deno provides `Deno.serve()` for building HTTP servers with support for HTTP/1.1 and HTTP/2.

### Hello World

```typescript
Deno.serve((_req) => {
  return new Response("Hello, World!");
});
```

Run with: `deno run --allow-net server.ts`

The handler can return a `Response` or a `Promise<Response>`, so async handlers work naturally.

### Listening on a Specific Port

By default, `Deno.serve` listens on port 8000. Customize with options:

```typescript
// Custom port
Deno.serve({ port: 4242 }, handler);

// Custom port and hostname
Deno.serve({ port: 4242, hostname: "0.0.0.0" }, handler);
```

### Inspecting Requests

```typescript
Deno.serve(async (req) => {
  console.log("Method:", req.method);
  const url = new URL(req.url);
  console.log("Path:", url.pathname);
  console.log("Query:", url.searchParams);
  console.log("Headers:", req.headers);

  if (req.body) {
    const body = await req.text();
    console.log("Body:", body);
  }

  return new Response("OK");
});
```

> Note: `req.text()` can fail if the client disconnects before the body is fully received. Handle this case with try/catch.

### Returning JSON Responses

```typescript
Deno.serve((req) => {
  const body = JSON.stringify({ message: "NOT FOUND" });
  return new Response(body, {
    status: 404,
    headers: {
      "content-type": "application/json; charset=utf-8",
    },
  });
});
```

### Streaming Responses

```typescript
Deno.serve((req) => {
  const body = new ReadableStream({
    async start(controller) {
      const timer = setInterval(() => {
        controller.enqueue("Hello, World!\n");
      }, 1000);

      // Store for cleanup
      (req as any)._timer = timer;
    },
    cancel() {
      clearInterval((req as any)._timer);
    },
  });

  return new Response(body.pipeThrough(new TextEncoderStream()), {
    headers: {
      "content-type": "text/plain",
      "cache-control": "no-cache",
    },
  });
});
```

### HTTPS Support

```typescript
Deno.serve({
  port: 8443,
  cert: await Deno.readTextFile("./certs/cert.pem"),
  key: await Deno.readTextFile("./certs/key.pem"),
}, handler);
```

### HTTP/2 Support

HTTP/2 is automatically enabled when TLS is configured.

### Serving WebSockets

```typescript
Deno.serve({
  port: 8000,
  onListen: ({ hostname, port }) => {
    console.log(`Server running at http://${hostname}:${port}/`);
  },
}, async (req) => {
  const url = new URL(req.url);

  if (url.pathname === "/ws") {
    const { socket, response } = Deno.upgradeWebSocket(req);

    socket.onopen = () => {
      console.log("WebSocket connection opened");
    };

    socket.onmessage = (event) => {
      console.log("Received:", event.data);
      socket.send(`Echo: ${event.data}`);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    return response;
  }

  return new Response("Visit /ws for WebSocket");
});
```

### Default Fetch Export

For Deno Deploy, export a `fetch` handler:

```typescript
export function fetch(request: Request): Response {
  return new Response("Hello from Deno Deploy!");
}
```

### Using @std/http

The standard library provides HTTP utilities:

```typescript
import { serveDir } from "jsr:@std/http/file-server";
import { ServerSentEvent, serveDir } from "jsr:@std/http";

// Serve static files
Deno.serve((req) => {
  return serveDir(req, {
    showDir: true,
    showDotFiles: false,
  });
});
```

### Graceful Shutdown

```typescript
const server = Deno.serve({ port: 8000 }, handler);

// Later, shut down gracefully
await server.shutdown();
```

### onListen Hook

Get notified when the server starts listening:

```typescript
Deno.serve({
  port: 8000,
  onListen: ({ hostname, port }) => {
    console.log(`Listening on http://${hostname}:${port}`);
  },
}, handler);
```
