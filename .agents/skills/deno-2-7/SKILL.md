---
name: deno-2-7
description: A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, covering installation, permissions, built-in APIs, development tools (task runner, test runner, lint, fmt), TypeScript support, npm integration, workspaces, and deployment patterns. Use when building applications with Deno, managing Deno projects, working with Deno's standard library (@std on JSR), configuring permissions, or deploying to Deno Deploy.
version: "0.2.0"
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
required_environment_variables: []

external_references:
  - https://docs.deno.com/
  - https://github.com/denoland/deno
---
## Overview
A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, covering installation, permissions, built-in APIs, development tools (task runner, test runner, lint, fmt), TypeScript support, npm integration, workspaces, and deployment patterns. Use when building applications with Deno, managing Deno projects, working with Deno's standard library (@std on JSR), configuring permissions, or deploying to Deno Deploy.

A comprehensive toolkit for using Deno, the modern JavaScript and TypeScript runtime with secure defaults. Deno is built on V8, Rust, and Tokio, providing a secure, fast, and developer-friendly environment for building web servers, CLI tools, and full-stack applications.

## When to Use
- Building JavaScript/TypeScript applications with secure defaults
- Creating HTTP servers, APIs, or web services
- Developing CLI tools and scripts
- Working with npm packages in TypeScript projects
- Using the Deno Standard Library (@std on JSR)
- Deploying applications to Deno Deploy
- Managing multi-package workspaces
- Running tests with built-in test runner
- Configuring project-specific tasks with `deno task`

## Installation / Setup
### Installation

Install Deno using one of these methods:

**Shell (Mac, Linux):**
```bash
curl -fsSL https://deno.land/install.sh | sh
```

**PowerShell (Windows):**
```powershell
irm https://deno.land/install.ps1 | iex
```

**Homebrew (Mac):**
```bash
brew install deno
```

**Verify installation:**
```bash
deno --version
# deno 2.7.x
```

### Your First Program

Create `hello.ts`:
```typescript
console.log("Hello, world!");
```

Run it:
```bash
deno run hello.ts
```

No build step, no configuration needed—TypeScript works out of the box.

### Building a Web Server

Create `server.ts`:
```typescript
Deno.serve((_req: Request) => {
  return new Response("Hello, world!");
});
```

Run with network permission:
```bash
deno run --allow-net server.ts
```

Visit http://localhost:8000.

See [Building Web Servers](reference/02-web-servers.md) for advanced patterns.

## Core Concepts
### Permissions Model

Deno requires explicit permissions for filesystem, network, and environment access:

```bash
# Allow reading from specific directory
deno run --allow-read=./data script.ts

# Allow writing to specific path
deno run --allow-write=./output script.ts

# Allow network access
deno run --allow-net script.ts

# Allow environment variables
deno run --allow-env script.ts

# Allow running subprocesses
deno run --allow-run=git script.ts

# Allow all permissions (use with caution)
deno run -A script.ts
```

See [Permissions and Security](reference/01-permissions.md) for detailed guidance.

### TypeScript First-Class Support

Deno runs TypeScript without compilation or configuration:

```bash
# Run TypeScript directly
deno run app.ts

# Type-check before running
deno run --check app.ts

# Type-check without running
deno check app.ts

# Type-check all modules including dependencies
deno check --all app.ts
```

Deno uses strict mode by default. See [TypeScript Configuration](reference/03-typescript.md) for advanced setup.

### Module System

Deno uses URL-based imports:

```typescript
// Import from local file
import { serve } from "./mod.ts";

// Import from remote URL
import { join } from "https://deno.land/std@0.224.0/path/mod.ts";

// Import from npm
import express from "npm:express@4.18.2";

// Import from JSR (recommended for std)
import { join } from "@std/path/join";
```

See [Module Resolution](reference/03-typescript.md#module-resolution) for import maps and workspaces.

## Development Tools
### Task Runner (`deno task`)

Define reusable commands in `deno.json`:

```json
{
  "tasks": {
    "start": "deno run --allow-net server.ts",
    "test": "deno test --allow-read --allow-env",
    "build": "deno bundle src/mod.ts dist/bundle.js",
    "dev": "deno run -A --watch=src/ server.ts"
  }
}
```

Run tasks:
```bash
deno task start
deno task test
```

See [Task Runner Guide](reference/04-task-runner.md) for dependencies, wildcards, and advanced syntax.

### Test Runner (`deno test`)

Write tests in `.test.ts` files:

```typescript
// math.test.ts
import { assertEquals } from "@std/assert";

Deno.test("addition works", () => {
  const result = 1 + 1;
  assertEquals(result, 2);
});

Deno.test("async test", async () => {
  const data = await fetch("https://api.example.com/data");
  assertEquals(data.status, 200);
});
```

Run tests:
```bash
# Run all tests
deno test

# Run with permissions
deno test --allow-net --allow-read

# Run specific test file
deno test math.test.ts

# Run tests matching pattern
deno test --filter "addition"

# Show test coverage
deno test --coverage

# Watch mode (re-run on changes)
deno test --watch
```

See [Testing Guide](reference/05-testing.md) for mocks, fixtures, and coverage.

### Linter (`deno lint`)

Check code quality:
```bash
# Lint all files
deno lint

# Lint specific files
deno lint src/mod.ts

# Auto-fix fixable issues
deno lint --fix

# Ignore specific rules
deno lint --rules-exclude no-explicit-any
```

Configure in `deno.json`:
```json
{
  "lint": {
    "rules": {
      "tags": ["recommended"],
      "include": ["no-console"],
      "exclude": ["no-explicit-any"]
    }
  }
}
```

### Code Formatter (`deno fmt`)

Format code automatically:
```bash
# Format all files
deno fmt

# Format specific files
deno fmt src/mod.ts

# Check if files are formatted (CI mode)
deno fmt --check

# Format with custom options
deno fmt --line-length 100 --indent-width 2
```

Configure in `deno.json`:
```json
{
  "fmt": {
    "lineLength": 100,
    "indentWidth": 2,
    "singleQuote": false,
    "semiColons": true
  }
}
```

### Documentation Generator (`deno doc`)

Generate documentation:
```bash
# Generate docs for current directory
deno doc

# Generate docs for specific module
deno doc mod.ts

# Output to file
deno doc --json > docs.json

# View in browser
deno doc | deno run -A jsr:@deno/doc-viewer
```

## Configuration
Create `deno.json` in project root:

```json
{
  "name": "@myorg/myapp",
  "version": "1.0.0",
  "tasks": {
    "start": "deno run -A server.ts"
  },
  "imports": {
    "@std/path": "jsr:@std/path@1",
    "lodash": "npm:lodash@^4.17.21"
  },
  "lint": {
    "rules": { "tags": ["recommended"] }
  },
  "fmt": {
    "lineLength": 100
  },
  "compilerOptions": {
    "lib": ["deno.ns", "dom"],
    "checkJs": true
  },
  "test": {
    "include": ["tests/**"],
    "exclude": ["tests/fixtures/**"]
  }
}
```

## Standard Library (@std)
Deno's standard library is hosted on JSR:

```typescript
// HTTP utilities
import { serve } from "@std/http";

// Path manipulation
import { join, extname } from "@std/path";

// Async utilities
import { delay } from "@std/async";

// JSON handling
import { parse } from "@std/jsonc";

// Testing assertions
import { assertEquals } from "@std/assert";

// YAML support
import { parse } from "@std/yaml";

// Database (SQL)
import { Client } from "@std/sql";
```

Browse all modules: https://jsr.io/@std

## Advanced Topics
## Advanced Topics

- [Permissions](reference/01-permissions.md)
- [Web Servers](reference/02-web-servers.md)
- [Typescript](reference/03-typescript.md)
- [Task Runner](reference/04-task-runner.md)
- [Testing](reference/05-testing.md)
- [Api Reference](reference/06-api-reference.md)
- [Npm Integration](reference/07-npm-integration.md)
- [Workspaces](reference/08-workspaces.md)

## Troubleshooting
### Permission Denied Errors

Always grant required permissions:
```bash
deno run --allow-read --allow-write --allow-net script.ts
```

### Module Not Found

Check import paths and ensure modules are accessible:
```bash
# Use full URLs for remote modules
import { join } from "https://deno.land/std@0.224.0/path/mod.ts";

# Or use import maps in deno.json
{
  "imports": {
    "@std/path": "jsr:@std/path@1"
  }
}
```

### Type Checking Errors

Deno uses strict mode by default. Fix errors or configure:
```json
{
  "compilerOptions": {
    "strict": false
  }
}
```

### Slow First Run

Deno caches remote modules. Subsequent runs are faster. Clear cache if needed:
```bash
deno cache --reload script.ts
```

## Additional Resources
- [Official Documentation](https://docs.deno.com)
- [Deno Standard Library](https://jsr.io/@std)
- [JSR Package Registry](https://jsr.io)
- [Deno Deploy](https://deno.com/deploy)
- [GitHub Repository](https://github.com/denoland/deno)
- [Deno Playground](https://play.deno.dev)

