---
name: bun-1-3-13
description: Complete toolkit for Bun 1.3.13 JavaScript runtime, package manager, bundler, and test runner. Use when building high-performance Node.js-compatible applications, migrating from npm/yarn/pnpm workflows, bundling JS/TS projects, running Jest-compatible tests, or developing full-stack applications with native HTTP servers, SQLite, Redis, and WebAssembly.
version: "0.1.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
- javascript
- typescript
- runtime
- package-manager
- bundler
- test-runner
- nodejs-alternative
- web-development
category: development
external_references:
- https://bun.sh/docs
- https://github.com/oven-sh/bun
---

# Bun 1.3.13

## Overview

Bun is an all-in-one toolkit for JavaScript and TypeScript applications. It ships as a single, dependency-free executable called `bun` and includes four integrated tools:

- **Runtime** — A fast JavaScript runtime designed as a drop-in replacement for Node.js. Written in Zig and powered by Apple's JavaScriptCore engine, Bun starts up ~4x faster than Node.js with lower memory usage.
- **Package Manager** — A Node.js-compatible package manager up to 25x faster than `npm install`, with global caching, workspaces, overrides, and lockfile support.
- **Test Runner** — A Jest-compatible, TypeScript-first test runner with snapshots, DOM testing, watch mode, and concurrent execution.
- **Bundler** — A native bundler for JavaScript/TypeScript/JSX/CSS with code splitting, plugins, HTML imports, and hot reloading.

Bun supports TypeScript (`.ts`), TSX (`.tsx`), JSX (`.jsx`), and JavaScript (`.js`) out of the box with zero configuration. Every file is transpiled on the fly by Bun's fast native transpiler before execution.

### What's New in 1.3.13

- **`bun test --parallel`** — Run tests across multiple threads for faster CI/CD
- **`bun test --isolate`** — Isolate each test file into its own process to prevent state leakage
- **`bun test --shard`** — Split test execution across shards (e.g., `--shard=1/4`) for distributed CI
- **`bun test --changed`** — Run only tests affected by recent git changes
- **`bun install` memory improvement** — Streams tarballs directly to disk, using 17x less memory
- **Source maps** — Use 8x less memory with optimized internal representation
- **gzip performance** — 5.5x faster via zlib-ng integration
- **Range request support** in `Bun.serve()` — Partial content responses for file downloads and streaming
- **SHA3 hashing** — Available in both `node:crypto` (`crypto.createHash('sha3-256')`) and WebCrypto (`subtle.digest('SHA-3', data)`)
- **`ws+unix://` WebSocket client** — Connect to Unix domain socket servers via WebSocket protocol

## When to Use

- Building high-performance JavaScript/TypeScript applications that need faster startup and runtime than Node.js
- Migrating from npm/yarn/pnpm to a faster package manager
- Bundling JavaScript/TypeScript projects for browser or server deployment without webpack or esbuild
- Running Jest-compatible tests with native TypeScript support
- Developing full-stack applications with `Bun.serve` HTTP server
- Using built-in SQLite, Redis, WebSockets, TCP/UDP, DNS, and FFI APIs
- Working with native file I/O, streams, binary data, and WebAssembly
- Running CLI tools via `bunx` (equivalent to `npx`, ~100x faster)

## Core Concepts

**Single Binary**: Bun ships as one executable — no separate installs for runtime, package manager, bundler, or test runner. The same `bun` command handles everything.

**JavaScriptCore Engine**: Unlike Node.js (V8), Bun uses Apple's JavaScriptCore, the engine behind Safari. This provides faster startup times and lower memory usage while maintaining Web-standard API compatibility.

**Zero-Config TypeScript**: `.ts`, `.tsx`, `.jsx` files execute directly — no `tsc`, Babel, or build step needed. Bun transpiles on the fly. For type checking, install `@types/bun` as a dev dependency.

**Node.js Compatibility**: Bun implements Node.js globals (`process`, `Buffer`, `__dirname`) and built-in modules (`fs`, `http`, `path`, `stream`, `zlib`, etc.) for drop-in compatibility with existing npm packages. Full compatibility is an ongoing effort.

**Web Standard APIs**: Bun natively implements `fetch`, `WebSocket`, `ReadableStream`, `Headers`, `URL`, `Crypto`, and other Web APIs — no polyfills needed.

**ESM-First with CommonJS Support**: Bun recommends ES modules but fully supports CommonJS for backward compatibility with the npm ecosystem.

## Installation / Setup

Install via script (recommended), package manager, or Docker:

```bash
# macOS & Linux
curl -fsSL https://bun.com/install | bash

# Windows
powershell -c "irm bun.sh/install.ps1|iex"

# npm
npm install -g bun

# Homebrew
brew install oven-sh/bun/bun

# Docker
docker pull oven/bun
docker run --rm --init --ulimit memlock=-1:-1 oven/bun
```

Verify installation:

```bash
bun --version      # e.g. 1.3.13
bun --revision     # exact git commit
```

If `command not found`, add `~/.bun/bin` to your PATH:

```bash
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

Upgrade Bun:

```bash
bun upgrade          # latest stable
bun upgrade --canary # latest untested build
bun upgrade --stable # switch back to stable
```

## Usage Examples

**Run a file** (TypeScript, JSX, TSX supported natively):

```bash
bun run index.tsx
bun index.ts         # "naked" form, omit `run`
bun --watch run index.tsx  # watch mode
```

**Run package.json scripts**:

```json
{
  "scripts": {
    "dev": "bun server.ts",
    "build": "bun build ./src/index.tsx --outdir ./dist"
  }
}
```

```bash
bun run dev
bun dev              # shorthand (fails if name conflicts with built-in command)
```

**Install packages**:

```bash
bun install                    # install all dependencies
bun install express            # add a package
bun install -d typescript      # add dev dependency
bun install --production       # skip devDependencies
bun install --frozen-lockfile  # CI mode, exact lockfile
```

**HTTP server with `Bun.serve`**:

```ts
const server = Bun.serve({
  port: 3000,
  routes: {
    "/": () => new Response("Hello!"),
    "/api/:id": req => new Response(`User ${req.params.id}`),
    "/api/posts": {
      GET: () => new Response("List posts"),
      POST: async req => Response.json({ created: true, ...(await req.json()) }),
    },
  },
});

console.log(`Listening on ${server.url}`);
```

**Bundle for browser**:

```bash
bun build ./src/index.tsx --outdir ./dist --target browser --minify
```

**Run tests**:

```bash
bun test                    # all tests
bun test math               # filter by name
bun test ./math.test.ts     # specific file
bun test --watch            # watch mode
bun test --concurrent       # parallel execution
bun test --parallel         # multi-threaded parallel execution
bun test --isolate          # isolate each file into its own process
bun test --shard=1/4        # shard 1 of 4 for distributed CI
bun test --changed          # only tests affected by git changes
```

## Advanced Topics

**Runtime & Core**: File execution, watch mode, bunfig.toml configuration, REPL, debugger → [Runtime & Core](reference/01-runtime-core.md)

**HTTP Server & Networking**: `Bun.serve` routing, WebSockets, TLS, TCP/UDP sockets, DNS resolution → [HTTP & Networking](reference/02-http-networking.md)

**Package Manager**: Install, add, remove, update, bunx, workspaces, catalogs, overrides, lockfiles, publishing → [Package Manager](reference/03-package-manager.md)

**Bundler**: `bun build` CLI and JS API, entrypoints, targets, formats, plugins, loaders, full-stack HTML imports → [Bundler](reference/04-bundler.md)

**Test Runner**: Jest-compatible API, lifecycle hooks, snapshots, mocking, coverage, CI/CD integration → [Test Runner](reference/05-test-runner.md)

**Data & Storage**: SQLite (`bun:sqlite`), Redis client, file I/O (`Bun.file`, `Bun.write`), streams, binary data, S3 → [Data & Storage](reference/06-data-storage.md)

**Process & System**: Shell scripting (`$` template literal), child processes (`Bun.spawn`), workers, environment variables, cron → [Process & System](reference/07-process-system.md)

**Interop & Utilities**: FFI (`bun:ffi`), Node-API modules, C compiler, transpiler API, hashing, glob, semver, TOML/YAML/JSON5 → [Interop & Utilities](reference/08-interop-utilities.md)

**Node.js Compatibility**: Built-in module support status, globals, migration guidance → [Node.js Compatibility](reference/09-nodejs-compat.md)
