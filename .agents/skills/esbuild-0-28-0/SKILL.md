---
name: esbuild-0-28-0
description: Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API access for bundling, minification, transformation, and development workflows with support for TypeScript, JSX, CSS modules, tree shaking, source maps, watch mode, and local development server without requiring npm installation via npx execution.
version: 0.28.0
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
- javascript
- bundler
- typescript
- jsx
- css
- minification
- tree-shaking
- source-maps
- watch-mode
- development-server
- npx
- esm
- commonjs
category: tooling
external_references:
- https://esbuild.github.io/
- https://github.com/evanw/esbuild
---

# esbuild v0.28

## Overview

esbuild is an extremely fast JavaScript bundler written in Go that compiles to native code. It bundles ESM and CommonJS modules, transforms TypeScript and JSX to JavaScript, minifies output, generates source maps, and supports CSS bundling including CSS modules. It provides three APIs: CLI, JavaScript (Node.js), and Go — all sharing the same concepts and parameters.

esbuild is 10-100x faster than other bundlers (webpack, rollup, parcel) because it uses parallelism across all CPU cores, writes everything from scratch without third-party dependencies, and touches the AST only three times during compilation. It does not perform type checking — run `tsc --noEmit` separately for that.

## When to Use

- Bundling JavaScript/TypeScript/JSX projects for browser or Node.js
- Transforming TypeScript to JavaScript without type-checking overhead
- Minifying production bundles with source map generation
- Setting up fast development workflows with watch mode and local serve
- Building CLI tools or libraries that need programmatic bundling via JS or Go API
- Converting modern JavaScript syntax for older browser targets
- Bundling CSS including `@import` resolution and CSS modules

## Installation / Setup

### Via npm (recommended)

```bash
npm install --save-exact --save-dev esbuild
```

Run from `node_modules/.bin`:

```bash
./node_modules/.bin/esbuild --version
```

### Via npx (no install needed)

```bash
npx esbuild@0.28.0 --version
```

### Direct binary download (Unix)

```bash
curl -fsSL https://esbuild.github.io/dl/v0.28.0 | sh
```

Or download directly from npm registry without npm installed:

```bash
curl -O https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-0.28.0.tgz
tar xzf ./linux-x64-0.28.0.tgz
./package/bin/esbuild
```

### Build from source

Requires Go compiler:

```bash
git clone --depth 1 --branch v0.28.0 https://github.com/evanw/esbuild.git
cd esbuild
go build ./cmd/esbuild
```

Cross-compile for other platforms:

```bash
GOOS=linux GOARCH=386 go build ./cmd/esbuild
```

### Deno support

```js
import * as esbuild from 'https://deno.land/x/esbuild@v0.28.0/mod.js'
let result = await esbuild.transform('let x: number = 1', { loader: 'ts' })
console.log(result)
await esbuild.stop()
```

### WebAssembly version (unsupported platforms / browser)

```bash
npm install --save-exact esbuild-wasm
```

Note: WASM is ~10x slower than native. Use only when native binary is not available.

## Usage Examples

### Basic bundling

```bash
npx esbuild app.ts --bundle --outfile=dist/bundle.js
```

### Production build with minification and source maps

```bash
npx esbuild app.jsx --bundle --minify --sourcemap --target=chrome58,firefox57,safari11,edge16 --outfile=dist/bundle.js
```

### Bundling for Node.js

```bash
npx esbuild app.js --bundle --platform=node --target=node18 --outfile=dist/bundle.js
```

### Watch mode

```bash
npx esbuild app.ts --bundle --outdir=dist --watch
```

### Local development server

```bash
npx esbuild app.ts --bundle --outdir=dist --serve
# Serves at http://127.0.0.1:8000/
```

### JavaScript API

```js
import * as esbuild from 'esbuild'

await esbuild.build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  minify: true,
  sourcemap: true,
  target: ['chrome90', 'firefox90'],
  outdir: 'dist',
})
```

### Transform API (single file, no bundling)

```js
import * as esbuild from 'esbuild'

let result = await esbuild.transform('let x: number = 1', {
  loader: 'ts',
})
console.log(result.code) // "let x = 1;\n"
```

### CSS bundling

```bash
npx esbuild --bundle app.css --outfile=dist/bundle.css
```

## Advanced Topics

**CLI Reference**: Flags, forms, and command-line usage patterns → [CLI Reference](reference/01-cli-reference.md)

**JavaScript API**: Async/sync APIs, build context, watch/serve/rebuild modes → [JavaScript API](reference/02-javascript-api.md)

**Go API**: Package structure, BuildOptions, TransformOptions, and incremental builds → [Go API](reference/03-go-api.md)

**Build Options Reference**: Complete documentation of all build and transform options organized by category → [Build Options](reference/04-build-options.md)

**Content Types and Loaders**: JavaScript, TypeScript, JSX, JSON, CSS, text, binary, base64, data URL, external file, empty file → [Content Types](reference/05-content-types.md)

**Plugin System**: onResolve, onLoad, onStart, onEnd, onDispose callbacks with namespaces and filters → [Plugin System](reference/06-plugin-system.md)

**Incremental Builds and Live Reload**: Watch mode, serve mode, rebuild API, live reload via SSE, CSS hot-reload → [Incremental Builds](reference/07-incremental-builds.md)
