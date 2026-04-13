# Deno Namespace API Reference

The global `Deno` namespace provides APIs for filesystem operations, networking, subprocesses, and other system-level functionality. This reference covers the most commonly used APIs.

## File System APIs

### Reading Files

```typescript
// Read entire file as bytes
const data = await Deno.readFile("file.txt");
// or synchronous
const dataSync = Deno.readFileSync("file.txt");

// Read file as text
const text = await Deno.readTextFile("file.txt");
const textSync = Deno.readTextFileSync("file.txt");

// Read file with encoding
const utf8 = await Deno.readTextFile("file.txt", { encoding: "utf8" });
```

### Writing Files

```typescript
// Write bytes to file
await Deno.writeFile("output.txt", new Uint8Array([1, 2, 3]));
Deno.writeFileSync("output.txt", new Uint8Array([1, 2, 3]));

// Write text to file
await Deno.writeTextFile("output.txt", "Hello, world!");
Deno.writeTextFileSync("output.txt", "Hello, world!");

// Write with options
await Deno.writeFile("output.txt", data, {
  create: true,  // Create if doesn't exist (default: true)
  createNew: false,  // Error if exists (default: false)
  truncate: true,  // Truncate before writing (default: false)
  append: false,  // Append to file (default: false)
  mode: 0o666,  // File permissions
});
```

### Opening Files

```typescript
// Open file for reading
const file = await Deno.open("file.txt", { read: true });
const data = new Uint8Array(1024);
await file.read(data);
await file.close();

// Open file for writing
const writer = await Deno.open("output.txt", {
  write: true,
  create: true,
  truncate: true
});
await writer.write(new Uint8Array([1, 2, 3]));
await writer.close();

// Using ReadableStream
for await (const bytes of file.readable) {
  console.log(bytes);
}
```

### File Information

```typescript
// Get file stats
const info = await Deno.stat("file.txt");
console.log(info.isFile);  // true
console.log(info.isDirectory);  // false
console.log(info.isSymlink);  // false
console.log(info.size);  // 1234
console.log(info.mtime);  // Date object

// Synchronous version
const infoSync = Deno.statSync("file.txt");

// Lstat (doesn't follow symlinks)
const lstat = await Deno.lstat("link.txt");
```

### Directory Operations

```typescript
// Create directory
await Deno.mkdir("/new/dir", { recursive: true });
Deno.mkdirSync("/new/dir", { recursive: true });

// List directory entries
for await (const entry of Deno.readDir("/path")) {
  console.log(entry.name, entry.isFile, entry.isDirectory);
}

// Synchronous version
for (const entry of Deno.readDirSync("/path")) {
  console.log(entry.name);
}

// Remove directory (must be empty)
await Deno.remove("/path/to/dir");

// Remove directory recursively
await Deno.remove("/path/to/dir", { recursive: true });
```

### File Watching

```typescript
const watcher = Deno.watchFs("/path/to/watch", {
  recursive: true,
  include: [".ts", ".js"],  // Optional filter
  exclude: ["node_modules"]  // Optional exclusion
});

for await (const event of watcher) {
  console.log(`Change: ${event.path}`);
  console.log(`Kind: ${event.kind}`); // "create", "update", or "remove"
}

// Stop watching
watcher.close();
```

### Symlinks

```typescript
// Create symlink
await Deno.symlink("/target/path", "/link/path");

// Read symlink target
const target = await Deno.readLink("/link/path");
console.log(target);  // "/target/path"

// Synchronous versions
Deno.symlinkSync("/target/path", "/link/path");
const targetSync = Deno.readLinkSync("/link/path");
```

### Copy and Move

```typescript
// Copy file
await Deno.copyFile("source.txt", "dest.txt");

// Move/rename file
await Deno.rename("old.txt", "new.txt");

// Synchronous versions
Deno.copyFileSync("source.txt", "dest.txt");
Deno.renameSync("old.txt", "new.txt");
```

### File Permissions

```typescript
// Change file permissions
await Deno.chmod("file.txt", 0o644);
Deno.chmodSync("file.txt", 0o600);

// Change ownership (Unix only)
await Deno.chown("file.txt", uid, gid);
Deno.chownSync("file.txt", uid, gid);
```

## Network APIs

### TCP Connections

```typescript
// Connect to TCP server
const conn = await Deno.connect({
  transport: "tcp",
  hostname: "example.com",
  port: 80
});

// Send data
await conn.write(new TextEncoder().encode("GET / HTTP/1.1\r\n\r\n"));

// Receive data
const buffer = new Uint8Array(4096);
const bytesRead = await conn.read(buffer);
console.log(new TextDecoder().decode(buffer.subarray(0, bytesRead)));

// Close connection
await conn.close();

// Listen on TCP port
const listener = Deno.listen({
  transport: "tcp",
  hostname: "0.0.0.0",
  port: 8000
});

for await (const conn of listener) {
  handleConnection(conn);
}
```

### UDP Connections

```typescript
// Create UDP socket
const udp = await Deno.connect({
  transport: "udp",
  hostname: "example.com",
  port: 53
});

// Send UDP packet
await udp.write(dnsQuery);

// Receive UDP packet
const buffer = new Uint8Array(512);
const bytesRead = await udp.read(buffer);
```

### Unix Domain Sockets

```typescript
// Connect to Unix socket
const conn = await Deno.connect({
  transport: "unix",
  path: "/tmp/socket.sock"
});

// Listen on Unix socket
const listener = Deno.listen({
  transport: "unix",
  path: "/tmp/server.sock"
});
```

### TLS Connections

```typescript
// Connect with TLS
const conn = await Deno.connectTls({
  hostname: "example.com",
  port: 443,
  // caCerts: [cert],  // Optional: custom CA certificates
  // cert: cert,  // For client authentication
  // key: key,
  // alpnProtocols: ["h2", "http/1.1"]
});

// Create TLS listener
const listener = await Deno.listenTls({
  port: 8443,
  cert: await Deno.readTextFile("cert.pem"),
  key: await Deno.readTextFile("key.pem")
});
```

## HTTP Server APIs

### Using Deno.serve (Recommended)

```typescript
// Basic server
Deno.serve({ port: 8000 }, (req) => {
  return new Response("Hello, World!");
});

// With handler function
async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);
  
  if (url.pathname === "/") {
    return new Response("Home");
  }
  
  return new Response("Not Found", { status: 404 });
}

Deno.serve(handler);

// Server with options
const listener = await Deno.serve({
  hostname: "0.0.0.0",
  port: 8000,
  async onListen({ hostname, port }) {
    console.log(`Server running at http://${hostname}:${port}/`);
  }
}, handler);

// Graceful shutdown
await listener.finished;
```

### HTTP/2 Support

```typescript
Deno.serve({
  port: 8443,
  cert: await Deno.readTextFile("cert.pem"),
  key: await Deno.readTextFile("key.pem"),
  alpnProtocols: ["h2", "http/1.1"]  // Enable HTTP/2
}, handler);
```

### WebSocket Upgrade

```typescript
import { upgradeWebSocket } from "@std/http";

Deno.serve(async (req) => {
  const ws = await upgradeWebSocket(req);
  
  ws.addEventListener("message", (event) => {
    ws.send(`Received: ${event.data}`);
  });
  
  ws.addEventListener("close", () => {
    console.log("Client disconnected");
  });
});
```

## Subprocess APIs

### Running Commands

```typescript
// Using Deno.Command (recommended)
const command = new Deno.Command(Deno.execPath(), {
  args: ["--version"],
  stdout: "piped",
  stderr: "piped"
});

const output = await command.output();

if (output.success) {
  console.log(new TextDecoder().decode(output.stdout));
} else {
  console.error(new TextDecoder().decode(output.stderr));
}

// Synchronous version
const outputSync = command.outputSync();
```

### Streaming Output

```typescript
const command = new Deno.Command("ls", {
  args: ["-la"],
  stdout: "piped",
  stderr: "piped"
});

const process = command.spawn();

// Stream stdout
for await (const line of process.stdout.getLines()) {
  console.log("STDOUT:", line);
}

// Stream stderr
for await (const line of process.stderr.getLines()) {
  console.error("STDERR:", line);
}

const status = await process.status;
console.log(`Exit code: ${status.code}`);
```

### Interactive Process

```typescript
const command = new Deno.Command("vim", {
  stdin: "inherit",
  stdout: "inherit",
  stderr: "inherit"
});

const process = command.spawn();
await process.status;
```

### Passing Input

```typescript
const command = new Deno.Command("cat", {
  stdin: "piped",
  stdout: "piped"
});

const process = command.spawn();

// Write to stdin
process.stdin.write(new TextEncoder().encode("Hello, World!\n"));
await process.stdin.close();

// Read from stdout
const output = await process.output;
console.log(new TextDecoder().decode(output.stdout));
```

### Environment Variables

```typescript
const command = new Deno.Command("echo", {
  args: ["$HOME"],
  env: {
    HOME: "/custom/home",
    PATH: Deno.env.get("PATH") || ""
  }
});

const output = await command.output();
```

### Working Directory

```typescript
const command = new Deno.Command("ls", {
  args: ["-la"],
  cwd: "/specific/path"
});

const output = await command.output();
```

## Process Information

### Environment Variables

```typescript
// Get environment variable
const home = Deno.env.get("HOME");
const path = Deno.env.get("PATH");

// Check if variable exists
if (Deno.env.has("DATABASE_URL")) {
  const dbUrl = Deno.env.get("DATABASE_URL")!;
}

// Set environment variable
Deno.env.set("MY_VAR", "value");

// Delete environment variable
Deno.env.delete("MY_VAR");

// Get all environment variables
for (const [key, value] of Deno.env) {
  console.log(key, "=", value);
}
```

### Process ID and Arguments

```typescript
// Current process ID
console.log(Deno.pid);

// Parent process ID
console.log(Deno.ppid);

// Command line arguments
console.log(Deno.args);

// Main module path
console.log(import.meta.main);
console.log(import.meta.filename);
console.log(import.meta.dirname);
```

### Process Exit

```typescript
// Exit with code
Deno.exit(0);  // Success
Deno.exit(1);  // Error

// Exit from async context (use return)
async function main() {
  if (error) {
    Deno.exit(1);
  }
}
```

### Signal Handling

```typescript
// Handle SIGINT (Ctrl+C)
Deno.addSignalListener("SIGINT", () => {
  console.log("Received SIGINT, cleaning up...");
  cleanup();
  Deno.exit(0);
});

// Handle SIGTERM
Deno.addSignalListener("SIGTERM", () => {
  console.log("Received SIGTERM");
});

// Handle SIGHUP
Deno.addSignalListener("SIGHUP", () => {
  console.log("Received SIGHUP, reloading config...");
});

// Remove signal listener
const handler = () => console.log("Signal received");
Deno.addSignalListener("SIGINT", handler);
Deno.removeSignalListener("SIGINT", handler);
```

## FFI (Foreign Function Interface)

### Loading Dynamic Libraries

```typescript
// Load dynamic library
const lib = await Deno.dlopen("./lib/native.so", {
  add: {
    parameters: ["number", "number"],
    result: "number"
  },
  greet: {
    parameters: ["cstring"],
    result: "void"
  }
});

// Call functions
const sum = lib.symbols.add(2, 3);
console.log(sum);  // 5

lib.symbols.greet("World");
```

### Supported Types

FFI supports these types:

| Type | Description |
|------|-------------|
| `void` | No value |
| `number` | 64-bit float |
| `i8`, `u8` | 8-bit signed/unsigned int |
| `i16`, `u16` | 16-bit signed/unsigned int |
| `i32`, `u32` | 32-bit signed/unsigned int |
| `i64`, `u64` | 64-bit signed/unsigned int |
| `cstring` | Null-terminated string |
| `buffer` | Raw bytes |
| `pointer` | Raw pointer |

### Callbacks to Rust

```typescript
const lib = await Deno.dlopen("./lib/native.so", {
  process: {
    parameters: ["number", "callback"],
    result: "void"
  }
});

// Define callback
function myCallback(x: number, y: number): number {
  return x + y;
}

// Pass callback to native code
lib.symbols.process(42, myCallback);
```

## System Information

### Build Information

```typescript
console.log(Deno.build);
// {
//   os: "linux",
//   arch: "x86_64",
//   cpuCount: 8,
//   env: "production",
//   family: "linux"
// }
```

### System Information API

```typescript
// Get OS release (requires --allow-sys)
const osRelease = await Deno.sys.osRelease();
console.log(osRelease);

// Get hostname
const hostname = await Deno.sys.hostname();
console.log(hostname);

// Get load average
const loadAvg = await Deno.sys.loadAverage();
console.log(loadAvg); // [1-min, 5-min, 15-min]

// Get CPU usage
const cpuUsage = await Deno.sys.cpuUsage();
console.log(cpuUsage);

// Get memory usage
const memUsage = await Deno.sys.memoryUsage();
console.log(memUsage);

// Get network interfaces
const interfaces = await Deno.sys.networkInterfaces();
console.log(interfaces);
```

## High-Resolution Time

```typescript
// Get high-resolution timestamp (requires --allow-hrtime)
const start = Deno.hrtime.bigint();

// Do some work
await someOperation();

const end = Deno.hrtime.bigint();
const duration = Number(end - start) / 1e6; // Convert to milliseconds
console.log(`Duration: ${duration}ms`);
```

## Errors

### Error Classes

Deno provides specific error classes:

```typescript
try {
  await Deno.open("nonexistent.txt");
} catch (error) {
  if (error instanceof Deno.errors.NotFound) {
    console.log("File not found");
  } else if (error instanceof Deno.errors.PermissionDenied) {
    console.log("Permission denied");
  } else if (error instanceof Deno.errors.AlreadyExists) {
    console.log("File already exists");
  } else {
    throw error;
  }
}
```

Available error classes:
- `Deno.errors.NotFound`
- `Deno.errors.PermissionDenied`
- `Deno.errors.ConnectionRefused`
- `Deno.errors.AddrInUse`
- `Deno.errors.AddrNotAvailable`
- `Deno.errors.BrokenPipe`
- `Deno.errors.AlreadyExists`
- `Deno.errors.InvalidData`
- `Deno.errors_TIMED_OUT`
- `Deno.errors.Interrupted`
- `Deno.errors.InvalidInput`
- `Deno.errors.NotSupported`
- And more...

## Import Meta

### Module Information

```typescript
// Current module URL
console.log(import.meta.url);
// "file:///path/to/module.ts"

// Is this the main module?
console.log(import.meta.main);
// true if run directly, false if imported

// File path (not URL)
console.log(import.meta.filename);
// "/path/to/module.ts"

// Directory path
console.log(import.meta.dirname);
// "/path/to"
```

### Module Resolution

```typescript
// Resolve module specifier
const resolved = await import.meta.resolve("./mod.ts");
console.log(resolved);  // Full URL

// Resolve with import map
const lodash = await import.meta.resolve("lodash");
console.log(lodash);  // Resolved from import map
```

## Related Topics

- [Permissions and Security](01-permissions.md) - Required permissions for APIs
- [Building Web Servers](02-web-servers.md) - HTTP server patterns
- [NPM Integration](07-npm-integration.md) - Using npm packages with Deno APIs
