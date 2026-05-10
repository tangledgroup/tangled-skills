---
name: nodejs-24-14-0
description: Complete Node.js 24.14 runtime toolkit covering core modules, async programming, HTTP servers, file system operations, streams, cryptography, process management, and modern ES modules. Use when building server-side JavaScript applications, CLI tools, microservices, or any Node.js-based project requiring access to built-in APIs for networking, I/O, encryption, child processes, and system interactions.
version: "0.1.0"
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
external_references:
  - https://nodejs.org/api/
  - https://github.com/nodejs/node
---

# Node.js 24.14

## Overview

Node.js is a JavaScript runtime built on Chrome's V8 engine that enables server-side JavaScript execution. Version 24 (current as of mid-2025) provides a comprehensive standard library with 60+ built-in modules covering file I/O, networking, cryptography, process management, streams, testing, and more. It supports both CommonJS and ECMAScript module systems, native TypeScript, built-in test runner, fetch API, Web Streams, SQLite, and worker threads.

Key capabilities:
- Event-driven, non-blocking I/O model
- Single-threaded event loop with libuv for async operations
- Built-in HTTP/HTTPS/HTTP2 servers and clients
- Native stream processing (Readable, Writable, Duplex, Transform)
- Child process spawning and IPC
- Worker threads for CPU-intensive tasks
- Cluster module for multi-process load balancing
- Built-in test runner with mocking, snapshots, and coverage
- Native TypeScript support (`node --experimental-strip-types`)
- SQLite via `node:sqlite` (built-in since v22)
- Web APIs: `fetch`, `AbortController`, `EventSource`, `WebCrypto`, `Web Streams`

## When to Use

- Building server-side JavaScript applications and APIs
- Creating CLI tools and scripts with built-in modules only
- Implementing HTTP/HTTPS servers without external frameworks
- Processing files, streams, or binary data at scale
- Running background tasks with child processes or worker threads
- Performing cryptographic operations (hashing, signing, TLS)
- Building microservices with inter-process communication
- Writing tests with the built-in test runner
- Any Node.js project requiring deep understanding of core APIs

## Core Concepts

**Event Loop**: Node.js uses a single-threaded event loop powered by libuv. Operations like file I/O, network requests, and timers are offloaded to system threads or the kernel, and callbacks fire when results are ready. Phases: timers → pending callbacks → idle/prepare → poll → check → close.

**Async Patterns**: Three styles coexist in Node.js:
- Callbacks (original pattern, error-first: `err, result`)
- Promises (thenable chains, `util.promisify` for conversion)
- Async/await (modern preferred style, built on Promises)

**Streams**: Node.js streams handle data piece-by-piece rather than loading everything into memory. Four types: Readable, Writable, Duplex, and Transform. Pipelining (`source.pipe(dest)`) chains streams together. Modern streams support async iteration (`for await`).

**Modules**: Two systems — CommonJS (`require`/`module.exports`) and ES Modules (`import`/`export`). Use `"type": "module"` in package.json or `.mjs` extension for ESM. Built-in modules use `node:` prefix (e.g., `node:fs`, `node:http`).

**Global Objects**: Available without import — `process`, `console`, `Buffer`, `setTimeout`, `setInterval`, `clearTimeout`, `clearInterval`, `setImmediate`, `queueMicrotask`, `fetch`, `TextEncoder`, `TextDecoder`.

## Usage Examples

### HTTP Server (ESM)

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello World\n');
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### File System (Promises API)

```javascript
import fs from 'node:fs/promises';
import path from 'node:path';

const filePath = path.join(process.cwd(), 'output.txt');
await fs.writeFile(filePath, 'Hello, Node.js!');
const content = await fs.readFile(filePath, 'utf-8');
console.log(content);
```

### Child Process

```javascript
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);
const { stdout, stderr } = await execFileAsync('ls', ['-la'], { encoding: 'utf-8' });
console.log(stdout);
```

### Worker Threads

```javascript
import { Worker, isMainThread, parentPort, workerData } from 'node:worker_threads';

if (isMainThread) {
  const worker = new Worker(import.meta.url, { workerData: { n: 1000000 } });
  worker.on('message', (result) => console.log('Result:', result));
  worker.on('error', (err) => console.error('Worker error:', err));
} else {
  const { n } = workerData;
  let sum = 0;
  for (let i = 0; i < n; i++) sum += i;
  parentPort.postMessage(sum);
}
```

## Advanced Topics

**Core Modules Reference**: Complete API reference for fs, http, https, net, tls, dns, dgram, os, path, url, util, crypto, buffer, stream, events, process, child_process, worker_threads, cluster, timers, console, readline, zlib, assert, v8, perf_hooks, test, sqlite, webcrypto, webstreams → [Core Modules API Reference](reference/01-core-modules-api.md)

**Async Programming Patterns**: Callbacks, Promises, async/await, EventEmitter, async iterators, AbortController integration, process.nextTick vs setImmediate, util.promisify/callbackify, microtask queue → [Async Programming Patterns](reference/02-async-programming.md)

**Streams and I/O**: Readable/Writable/Duplex/Transform streams, piping, backpressure, async iteration, object mode, web streams interop, zlib compression streams, readline, string_decoder → [Streams and I/O](reference/03-streams-and-io.md)

**Networking and HTTP**: http/http2/https servers and clients, net TCP sockets, dgram UDP, tls TLS/SSL, dns resolution, URL parsing, fetch API, EventSource (SSE), headers, keep-alive, proxy support → [Networking and HTTP](reference/04-networking-and-http.md)

**Modules and Project Structure**: CommonJS vs ESM, package.json fields, node_modules resolution, node: prefix, built-in module list, TypeScript support, import attributes, JSON modules, Wasm modules, top-level await, loaders → [Modules and Project Structure](reference/05-modules-and-structure.md)

**Testing and Debugging**: Built-in test runner (node:test), describe/test/suite APIs, mocking, snapshots, coverage, reporters, watch mode, assert module, inspector protocol, console, diagnostics_channel, trace events, v8 heap snapshots → [Testing and Debugging](reference/06-testing-and-debugging.md)

**Process and System APIs**: process object, signals, environment variables, child_process (spawn/fork/exec/execFile), cluster for multi-process, worker_threads for parallelism, os information, tty, permissions, hrtime, memory usage, CPU profiling → [Process and System APIs](reference/07-process-and-system.md)

**Cryptography and Security**: node:crypto (hashing, HMAC, cipher/decipher, sign/verify, key generation, Diffie-Hellman, ECDH, X.509), webcrypto (Web Crypto API), tls configuration, OpenSSL security levels, permission model → [Cryptography and Security](reference/08-crypto-and-security.md)

## Command-Line Options

Key `node` flags:
- `--version` / `-v` — print Node.js version
- `--watch` — restart on file changes (supports glob patterns)
- `--watch-path <dir>` — watch specific directory
- `--experimental-strip-types` — load and strip TypeScript types
- `--import <module>` — pre-load ES module (like require hook)
- `--require <module>` — pre-load CommonJS module
- `--experimental-test-module-mocks` — enable test mocking
- `--experimental-vm-modules` — VM with ES module support
- `--max-old-space-size=<mb>` — set heap size limit
- `--trace-deprecation` — show stack traces on deprecation warnings
- `--enable-source-maps` — enable source map support
- `--conditions <cond>` — add export condition

Run tests: `node --test [files...]`
Coverage: `node --test --experimental-test-coverage [files...]`
Watch mode: `node --test --watch [files...]`
