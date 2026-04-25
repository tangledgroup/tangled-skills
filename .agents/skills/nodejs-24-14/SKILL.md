---
name: nodejs-24-14
description: Complete Node.js 24.14 runtime toolkit covering core modules, async programming, HTTP servers, file system operations, streams, cryptography, process management, and modern ES modules. Use when building server-side JavaScript applications, CLI tools, microservices, or any Node.js-based project requiring access to built-in APIs for networking, I/O, encryption, child processes, and system interactions.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - nodejs
  - javascript
  - runtime
  - server-side
  - async
  - streams
  - http
  - cryptography
category: runtime
required_environment_variables: []
---

# Node.js 24.14

## Overview

Complete Node.js 24.14 runtime toolkit covering core modules, async programming, HTTP servers, file system operations, streams, cryptography, process management, and modern ES modules. Use when building server-side JavaScript applications, CLI tools, microservices, or any Node.js-based project requiring access to built-in APIs for networking, I/O, encryption, child processes, and system interactions.

Complete toolkit for the Node.js 24.14 JavaScript runtime environment, providing access to core modules for HTTP servers, file system operations, networking, cryptography, process management, streams, and modern ECMAScript modules with full TypeScript support.

## When to Use

- Building server-side JavaScript applications or REST APIs
- Creating CLI tools and command-line utilities
- Developing microservices with HTTP/HTTPS or HTTP/2 support
- Implementing file system operations and stream processing
- Working with TCP/UDP networking and WebSocket connections
- Performing cryptographic operations (hashing, signing, TLS)
- Managing child processes and system resources
- Using modern ES modules or CommonJS module systems
- Building single executable applications (SEA)
- Testing with the built-in test runner
- Debugging with the Node.js inspector

## Setup

### Installation

Download and install Node.js 24.14 from [nodejs.org](https://nodejs.org/):

```bash
# Using npm to install globally (if you have an older Node.js)
npm install -g node@24.14

# Or download binaries from https://nodejs.org/
```

### Verify Installation

```bash
node --version  # v24.14.x
npm --version   # Included package manager
```

### Running Node.js Programs

```bash
# Run a JavaScript file
node app.js

# Run with ES modules explicitly
node --input-type=module app.js

# Start REPL interactively
node

# Run inline script
node -e "console.log('Hello World')"

# Read script from stdin
echo "console.log('Hello')" | node
```

## Quick Start

### Creating an HTTP Server

See [HTTP Servers](references/02-http-networking.md) for detailed examples.

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello World\n');
});

server.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

### File System Operations

See [File System API](references/03-file-system-streams.md) for comprehensive examples.

```javascript
import fs from 'node:fs/promises';

// Read file asynchronously
const data = await fs.readFile('file.txt', 'utf8');
console.log(data);

// Write file asynchronously
await fs.writeFile('output.txt', 'Hello World', 'utf8');

// Check if file exists
const exists = await fs.access('file.txt').then(() => true).catch(() => false);
```

### Working with Streams

See [Stream Processing](references/03-file-system-streams.md) for stream patterns.

```javascript
import fs from 'node:fs';
import zlib from 'node:zlib';

// Pipe file through gzip compression
fs.createReadStream('file.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('file.txt.gz'));
```

### ES Modules vs CommonJS

See [Module Systems](references/01-modules-cli.md) for module system details.

```javascript
// ES Module (app.mjs or with "type": "module" in package.json)
import fs from 'node:fs';
export const greeting = 'Hello';

// CommonJS (app.cjs or default)
const fs = require('node:fs');
module.exports.greeting = 'Hello';
```

## Core Concepts by Category

### Module Systems and CLI
- **ECMAScript Modules**: Native `import`/`export` syntax with top-level await
- **CommonJS**: Traditional `require()`/`module.exports` system
- **CLI Options**: 100+ command-line flags for debugging, optimization, and configuration
- **Package.json**: Module resolution, exports field, type declaration

See [Module Systems and CLI](references/01-modules-cli.md) for:
- ES module syntax and interoperability
- CommonJS module patterns
- Package.json exports and imports fields
- CLI options and environment variables
- TypeScript integration

### HTTP and Networking
- **HTTP/1.1**: Client and server APIs with keep-alive, compression
- **HTTP/2**: Multiplexed streams, server push, headers compression
- **HTTPS**: TLS-encrypted connections with certificate management
- **TCP/Net**: Low-level socket programming
- **UDP/Dgram**: Datagram sockets for broadcast/multicast
- **DNS**: Resolution with promises and callbacks

See [HTTP and Networking](references/02-http-networking.md) for:
- HTTP server setup and request handling
- HTTP client requests with streaming
- HTTP/2 multiplexing and push
- TLS/SSL configuration
- TCP server and client patterns
- DNS resolution strategies

### File System and Streams
- **fs/promises**: Async/await file operations
- **fs/callbacks**: Traditional callback-based API
- **Streams**: Readable, Writable, Duplex, Transform
- **Path**: Cross-platform path manipulation
- **OS**: System information and utilities

See [File System and Streams](references/03-file-system-streams.md) for:
- File reading/writing patterns
- Directory operations and watching
- Stream piping and backpressure
- Transform streams for data processing
- Path resolution across platforms

### Cryptography and Security
- **Crypto**: Hashing, signing, encryption, random generation
- **TLS**: Secure TCP connections
- **Permissions**: Runtime permission model

See [Cryptography and Security](references/04-crypto-security.md) for:
- Hash functions (SHA-256, SHA-3, etc.)
- HMAC and message authentication
- Public/private key cryptography
- TLS server and client setup
- Permission model and sandboxing

### Process and System Management
- **Process**: Event loop, environment, signals, child processes
- **Child Process**: Spawn, exec, fork with IPC
- **Cluster**: Multi-process application scaling
- **V8**: Memory management, GC tuning, code optimization
- **OS**: Platform-specific information

See [Process and System](references/05-process-system.md) for:
- Process events and lifecycle
- Environment variable management
- Signal handling and graceful shutdown
- Child process communication
- Cluster module for CPU scaling
- V8 heap snapshots and optimization

### Async Programming Patterns
- **Events**: EventEmitter pattern for custom events
- **Timers**: setTimeout, setInterval, setImmediate
- **Async Hooks**: Track async operation lifecycle
- **Diagnostics Channel**: Low-overhead observability
- **Performance Hooks**: Measure operation timing

See [Async Programming](references/06-async-programming.md) for:
- EventEmitter patterns and best practices
- Timer management and cleanup
- Async context tracking
- Performance measurement techniques
- Domain-based error handling

### Testing and Debugging
- **Test Runner**: Built-in test framework with coverage
- **Assert**: Test assertions and validations
- **Inspector**: Chrome DevTools integration
- **Report**: Diagnostic reporting
- **Repl**: Interactive development

See [Testing and Debugging](references/07-testing-debugging.md) for:
- Test runner syntax and fixtures
- Assertion patterns
- Debugging with breakpoints
- Coverage report generation
- REPL workflows

### Advanced Features
- **VM**: Isolated code execution contexts
- **Addons**: Native C/C++ module development
- **SQLite**: Built-in SQL database (new in v24)
- **WASI**: WebAssembly System Interface
- **Single Executable Apps**: Bundle apps into one file

See [Advanced Features](references/08-advanced-features.md) for:
- VM contexts for sandboxing
- Native addon development with Node-API
- SQLite integration patterns
- WASI module usage
- SEA application creation

## Reference Files

- [`references/01-modules-cli.md`](references/01-modules-cli.md) - ES modules, CommonJS, package.json, CLI options, TypeScript support
- [`references/02-http-networking.md`](references/02-http-networking.md) - HTTP/1.1, HTTP/2, HTTPS, TCP, UDP, DNS APIs
- [`references/03-file-system-streams.md`](references/03-file-system-streams.md) - File system operations, streams, path utilities
- [`references/04-crypto-security.md`](references/04-crypto-security.md) - Cryptography, hashing, TLS, permissions
- [`references/05-process-system.md`](references/05-process-system.md) - Process management, child processes, clustering, V8 tuning
- [`references/06-async-programming.md`](references/06-async-programming.md) - Events, timers, async hooks, diagnostics
- [`references/07-testing-debugging.md`](references/07-testing-debugging.md) - Test runner, assertions, inspector, REPL
- [`references/08-advanced-features.md`](references/08-advanced-features.md) - VM, native addons, SQLite, WASI, single executable apps

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/nodejs-24-14/`). All paths are relative to this directory.

## Common Patterns

### Error Handling Patterns

```javascript
// Async/await with try-catch
try {
  const data = await fs.readFile('file.txt', 'utf8');
} catch (error) {
  console.error('Read error:', error.code, error.message);
}

// Stream error handling
readStream.on('error', (err) => {
  console.error('Stream error:', err);
});

// Process uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
  process.exit(1);
});
```

### Graceful Shutdown

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  res.end('Hello');
});

server.listen(3000);

process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
```

### Environment Configuration

```javascript
import process from 'node:process';

const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';
const API_KEY = process.env.API_KEY;

if (!API_KEY && NODE_ENV === 'production') {
  throw new Error('API_KEY required in production');
}
```

## Troubleshooting

### Common Issues

**Module resolution errors**: Ensure file extensions are included for relative ES module imports. Use `node:prefix` for built-in modules (e.g., `node:fs`).

**Permission denied errors**: Check file permissions and ensure the process has access. Use `--allow-fs-read` flag with permission model.

**Maximum call stack size exceeded**: Reduce recursion depth or increase stack with `--stack-size=N` CLI option.

**Memory leaks**: Use `--inspect` flag with Chrome DevTools to profile memory. Check for unclosed streams and event listener leaks.

**Async operation timing out**: Set appropriate timeouts on HTTP requests and database connections. Use AbortController for cancellation.

### Debugging Commands

```bash
# Start with inspector
node --inspect app.js

# Inspector with host/port
node --inspect=0.0.0.0:9229 app.js

# Debug in pause mode
node --inspect-brk app.js

# Generate heap snapshot on exit
node --heap-snapshot-exit app.js

# Track memory allocation
node --trace-gc app.js
```

### Performance Tips

- Use streams for large file/network operations to avoid loading everything into memory
- Enable HTTP keep-alive for repeated requests to same host
- Use clustering to utilize multi-core systems
- Profile with `--perf-basic-prof` and analyze with Perfetto
- Monitor event loop lag with `perf_hooks` module

## Version Compatibility

Node.js 24.14 follows [Semantic Versioning](https://semver.org/). Major version changes may include breaking changes. This skill covers Node.js 24.x LTS features including:

- Full ES module support (stable)
- Import attributes (stable, replaced import assertions)
- Built-in test runner (stable)
- Permission model (active development)
- SQLite module (new in v24)
- Single executable applications (stable)

For migration from older versions, see the [Node.js Migration Guide](https://nodejs.org/api/all.html#all).

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
