---
name: bun-1-3-12
description: Complete toolkit for Bun 1.3.12 JavaScript runtime, package manager, bundler, and test runner. Use when building high-performance Node.js-compatible applications, migrating from npm/yarn/pnpm workflows, bundling JavaScript/TypeScript projects, running Jest-compatible tests, or developing full-stack applications with native HTTP servers, SQLite, Redis, and WebAssembly support.
version: "0.2.0"
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
## Overview
Complete toolkit for Bun 1.3.12 JavaScript runtime, package manager, bundler, and test runner. Use when building high-performance Node.js-compatible applications, migrating from npm/yarn/pnpm workflows, bundling JavaScript/TypeScript projects, running Jest-compatible tests, or developing full-stack applications with native HTTP servers, SQLite, Redis, and WebAssembly support.

## When to Use
- Building high-performance JavaScript/TypeScript applications
- Replacing Node.js with faster alternative (10-30x faster startup)
- Migrating from npm/yarn/pnpm to integrated package management
- Bundling frontend/backend code without complex tooling
- Running Jest-compatible tests with native speed
- Developing full-stack apps with built-in HTTP server, SQLite, Redis
- Creating single-file executables from JavaScript/TypeScript
- Working with TypeScript/JSX without transpilation steps

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

Complete toolkit for Bun 1.3.12 JavaScript runtime, package manager, bundler, and test runner. Use when building high-performance Node.js-compatible applications, migrating from npm/yarn/pnpm workflows, bundling JavaScript/TypeScript projects, running Jest-compatible tests, or developing full-stack applications with native HTTP servers, SQLite, Redis, and WebAssembly support.

Bun is a fast, all-in-one JavaScript/TypeScript toolkit replacing Node.js, npm/yarn/pnpm, Webpack/esbuild, and Jest. It provides a runtime, package manager, bundler, and test runner in a single binary with native support for TypeScript, JSX, CSS, Wasm, and more.

## Installation / Setup
### Installation

```bash
# macOS & Linux
curl -fsSL https://bun.com/install | bash

# Windows PowerShell
powershell -c "irm bun.sh/install.ps1|iex"

# npm (last npm command you'll ever need)
npm install -g bun

# Homebrew
brew install oven-sh/bun/bun

# Docker
docker pull oven/bun
```

Verify installation:
```bash
bun --version  # Output: 1.3.12
bun --revision # Output: 1.3.12+<commit-hash>
```

### Basic Usage Patterns

See detailed guides in reference files below.

**Runtime**: [reference/01-runtime-basics.md](reference/01-runtime-basics.md) - Running TypeScript/JavaScript directly

**Package Manager**: [reference/02-package-manager.md](reference/02-package-manager.md) - `bun add`, `bun install`, workspaces

**Bundler**: [reference/03-bundler.md](reference/03-bundler.md) - Building bundles, hot-reloading, single-file executables

**Test Runner**: [reference/04-test-runner.md](reference/04-test-runner.md) - Jest-compatible testing with lifecycle hooks, mocking, snapshots

## Core Features
### Runtime
- Native TypeScript & JSX support (no transpilation needed)
- 10-30x faster than Node.js for many workloads
- Web APIs: `fetch`, `WebSocket`, `ReadableStream`, `Blob`, `File`
- Node.js compatibility: Most npm packages work without modification
- Built-in SQLite, Redis, S3 clients
- HTTP server with routing, cookies, TLS support
- Workers for parallel execution
- FFI for calling C/C++ libraries

### Package Manager
- 30x faster than npm, 10x faster than yarn
- Deterministic installs (lockfile-based)
- Workspaces and monorepo support
- Built-in package runner (`bunx`)
- Catalogs for deduping dependencies
- Patch system for local dependency modifications

### Bundler
- esbuild-compatible with additional features
- Hot module replacement (HMR)
- CSS, CSS modules, PostCSS support
- Single-file executable generation
- Bytecode compilation for faster startup
- Tree shaking and minification

### Test Runner
- Jest-compatible API (`test`, `expect`, `describe`)
- Snapshot testing
- Mocking and spies
- Watch mode with instant feedback
- Code coverage reporting
- Concurrent test execution
- DOM/JSX testing support

## Configuration
Bun uses `bunfig.toml` for configuration (optional - works without config):

```toml title="bunfig.toml"
[install]
# Package manager options

[test]
# Test runner options

[build]
# Bundler options

[env]
# Environment variables
```

See [reference/05-configuration.md](reference/05-configuration.md) for complete configuration reference.

## Advanced Topics
## Advanced Topics

- [Runtime Basics](reference/01-runtime-basics.md)
- [Package Manager](reference/02-package-manager.md)
- [Bundler](reference/03-bundler.md)
- [Test Runner](reference/04-test-runner.md)
- [Configuration](reference/05-configuration.md)
- [Http Server](reference/06-http-server.md)
- [Data Storage](reference/07-data-storage.md)
- [Nodejs Compat](reference/08-nodejs-compat.md)
- [Migration Guides](reference/09-migration-guides.md)
- [Ci Cd Deployment](reference/10-ci-cd-deployment.md)
- [Built In Apis](reference/11-built-in-apis.md)
- [Process System](reference/12-process-system.md)

## Troubleshooting
### Common Issues

**Module resolution errors**: Bun uses Node.js-style resolution. Use `bun --bun` flag or configure in `bunfig.toml`.

**Node.js compatibility issues**: Some native modules may not work. Check [compatibility docs](reference/08-nodejs-compat.md).

**TypeScript errors**: Ensure `tsconfig.json` is compatible. Bun uses its own compiler for runtime but respects your config.

**Package install failures**: Try `bun install --frozen` to use exact lockfile versions, or `bun install --no-cache` to bypass cache.

### Getting Help

- [Bun Discord](https://bun.com/discord) - Active community support
- [GitHub Issues](https://github.com/oven-sh/bun/issues) - Bug reports and feature requests
- [Bun Documentation](https://bun.sh/docs) - Full official documentation

## Performance Tips
1. Use `bun build --minify` for production bundles
2. Enable bytecode compilation: `--bytecode` flag
3. Use workspaces for monorepos to dedupe dependencies
4. Run tests concurrently: `bun test --concurrent`
5. Use built-in SQLite instead of external database clients when possible

## Version Management
```bash
# Check current version
bun --version

# Upgrade to latest stable
bun upgrade

# Upgrade to canary (bleeding edge)
bun upgrade --canary

# Downgrade to specific version
bun install -g bun@1.2.0

# Switch back to stable from canary
bun upgrade --stable
```

## Environment Setup
After installation, add Bun to PATH if needed:

**macOS/Linux**: Add to `~/.bashrc` or `~/.zshrc`:
```bash
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

**Windows PowerShell**:
```powershell
[System.Environment]::SetEnvironmentVariable(
  "Path",
  [System.Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\.bun\bin",
  [System.EnvironmentVariableTarget]::User
)
```

## Related Skills
Consider also using:
- `typescript` - For TypeScript configuration and patterns
- `jest` - For Jest-specific features not yet in Bun test runner
- `docker` - For containerized deployments
- `github-actions` - For CI/CD integration

