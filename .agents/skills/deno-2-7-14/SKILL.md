---
name: deno-2-7-14
description: A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime,
  covering installation, permissions, built-in APIs, development tools (task runner,
  test runner, lint, fmt), TypeScript support, npm integration, workspaces, and deployment
  patterns. Use when building applications with Deno, managing Deno projects, working
  with Deno's standard library (@std on JSR), configuring permissions, or deploying
  to Deno Deploy.
version: "0.1.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
- javascript
- typescript
- runtime
- web-server
- cli-tools
- npm
- jsr
- testing
category: development
external_references:
- https://docs.deno.com/
- https://github.com/denoland/deno
---

# Deno 2.7.14

## Overview

Deno (pronounced *dee-no*) is an open-source JavaScript, TypeScript, and WebAssembly runtime built on V8, Rust, and Tokio. It provides secure defaults, first-class TypeScript support, a robust built-in toolchain, and full Node.js/npm compatibility. Deno 2.x represents the current major version with enhanced performance, improved npm integration, and workspace support.

Key features:
- **TypeScript-ready out of the box** — zero config needed
- **Secure by default** — no filesystem, network, or environment access without explicit permission
- **Built-in toolchain** — test runner, linter, formatter, bundle, compile
- **Node.js and npm compatible** — import npm packages with `npm:` specifiers
- **JSR integration** — first-party package registry at jsr.io
- **Standard library** — modular `@std` packages published on JSR

### Notable Changes in 2.7.14 (since 2.7.0)

- **Delta updates** via bsdiff patches for faster `deno upgrade`
- **Alpha and beta release channels** supported
- **node:repl module** implemented
- **llhttp-based node:http rewrite** with native TCPWrap
- **Native TLSWrap** (Rust core) and **native uv_pipe_t** implementation
- **V8 updated to 146.8.0** with foreground task ownership
- **Function coverage** added to test summary and HTML reports
- **OpenTelemetry console exporter** and array attribute support
- **P-521 elliptic curve** sign, verify, and ECDH derive in ext/crypto
- **node:http rewritten** using llhttp parser with native C++ bindings
- **fs.Utf8Stream** added to ext/node
- **CacheStorage.keys()** and **Cache.keys()** methods implemented
- **deno doc** now supports npm packages
- **--cpu-prof flags** for CPU profiling
- **Auto-detect CJS vs ESM** in `deno eval`
- **Compile config** gains `include` and `exclude` fields

## When to Use

- Building JavaScript/TypeScript applications with a modern, secure runtime
- Migrating Node.js projects to Deno (full npm compatibility)
- Writing CLI tools, HTTP servers, or scripts with built-in tooling
- Working with TypeScript without separate compilation steps
- Deploying serverless applications to Deno Deploy
- Managing monorepo projects with workspace support
- Needing a batteries-included runtime with no external dependencies

## Core Concepts

**Permissions model**: Deno denies all I/O by default. Use `--allow-read`, `--allow-write`, `--allow-net`, `--allow-env`, and `--allow-run` flags to grant access. Permissions can also be configured in `deno.json`.

**Module specifiers**: Deno supports multiple import sources:
- Local files: `import { x } from "./module.ts"`
- URLs: `import { x } from "https://esm.sh/..."`
- JSR packages: `import { x } from "jsr:@std/assert@^1.0.0"`
- npm packages: `import { x } from "npm:chalk@5"`
- Node built-ins: `import fs from "node:fs"`

**Configuration**: The `deno.json` (or `deno.jsonc`) file configures imports, tasks, linting, formatting, permissions, and TypeScript compiler options. Deno also supports `package.json` for Node.js compatibility.

**Standard library**: Published as modular `@std` packages on JSR. Key packages include `@std/assert`, `@std/fs`, `@std/http`, `@std/path`, `@std/async`, and many more.

## Installation / Setup

Install Deno using the official install script:

```bash
# macOS and Linux
curl -fsSL https://deno.land/install.sh | sh

# Windows (PowerShell)
irm https://deno.land/install.ps1 | iex
```

Verify installation:

```bash
deno --version
```

Additional installation options include package managers (Homebrew, Chocolatey, npm), binary downloads from GitHub releases, and APT/YUM repositories → [Installation](reference/01-installation.md) for details.

## Usage Examples

**Hello World server:**

```typescript
Deno.serve((_req) => {
  return new Response("Hello, World!");
});
```

Run with: `deno run --allow-net server.ts`

**Import an npm package:**

```typescript
import chalk from "npm:chalk@5";
console.log(chalk.green("Hello from npm in Deno"));
```

**Using the standard library:**

```typescript
import { assertEquals } from "jsr:@std/assert";
import { walk } from "jsr:@std/fs/walk";

// Walk a directory
for await (const entry of walk("./src")) {
  console.log(entry.path);
}
```

**Configuration with bare specifiers:**

```jsonc
// deno.json
{
  "imports": {
    "@std/assert": "jsr:@std/assert@^1.0.0",
    "chalk": "npm:chalk@5"
  },
  "tasks": {
    "start": "deno run --allow-net server.ts",
    "test": "deno test --allow-read",
    "lint": "deno lint"
  }
}
```

```typescript
// Now use bare specifiers
import { assertEquals } from "@std/assert";
import chalk from "chalk";
```

## Advanced Topics

**Permissions and Security**: Granular permission flags, deny rules, configuration file permissions → [Security](reference/02-security.md)

**Node.js and npm Compatibility**: Importing npm packages, CommonJS support, `node:` built-ins, `node_modules` management → [Node Compatibility](reference/03-node-compatibility.md)

**Configuration (deno.json)**: Tasks, imports, lint/fmt settings, lockfile, TypeScript options, publish config → [Configuration](reference/04-configuration.md)

**Testing and Benchmarking**: Built-in test runner, hooks, coverage, snapshot testing, BDD → [Testing](reference/05-testing.md)

**HTTP Server and Web Development**: `Deno.serve`, HTTP/2, HTTPS, WebSockets, file serving → [HTTP Server](reference/06-http-server.md)

**Workspaces and Monorepos**: Multi-package management, path patterns, publishing → [Workspaces](reference/07-workspaces.md)

**FFI (Foreign Function Interface)**: Calling native C/Rust libraries, type mapping, callbacks → [FFI](reference/08-ffi.md)

**CLI Reference**: Complete subcommand reference for `deno run`, `test`, `lint`, `fmt`, `compile`, `publish`, etc. → [CLI Reference](reference/09-cli-reference.md)

**Standard Library (@std)**: Overview of all `@std` packages on JSR → [Standard Library](reference/10-standard-library.md)

**Deployment**: Deno Deploy platform, `deno deploy` CLI, Deno KV database → [Deployment](reference/11-deployment.md)

**Debugging and Profiling**: Chrome DevTools integration, CPU profiling, inspect flags → [Debugging](reference/12-debugging.md)
