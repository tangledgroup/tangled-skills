---
name: esbuild-0-28
description: Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API access for bundling, minification, transformation, and development workflows with support for TypeScript, JSX, CSS modules, tree shaking, source maps, watch mode, and local development server without requiring npm installation via npx execution.
version: "0.28.0"
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
required_environment_variables: []

external_references:
  - https://esbuild.github.io/
  - https://github.com/evanw/esbuild
---
## Overview
Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API access for bundling, minification, transformation, and development workflows with support for TypeScript, JSX, CSS modules, tree shaking, source maps, watch mode, and local development server without requiring npm installation via npx execution.

An extremely fast JavaScript bundler written in Go that bundles, minifies, and transforms JavaScript, TypeScript, JSX, and CSS files 10-100x faster than alternative tools like webpack, rollup, or parcel. Esbuild requires no cache for its speed and supports both ECMAScript modules (ESM) and CommonJS formats with built-in tree shaking, source maps, watch mode, and a local development server.

## When to Use
- Bundling JavaScript/TypeScript applications for browser or Node.js deployment
- Transforming TypeScript to JavaScript without type checking
- Minifying code for production builds
- Converting modern JavaScript syntax to older versions for browser compatibility
- Developing with hot reload using watch mode and local server
- Processing CSS modules and bundling CSS files
- Using as a build tool via `npx` without npm installation
- Creating bundles from stdin or in-memory strings
- Integrating into CI/CD pipelines with the Go API

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### Using npx (No Installation Required)

Esbuild can be used immediately without installing anything:

```bash
# Transform TypeScript to JavaScript
echo 'let x: number = 1' | npx esbuild@0.28.0 --loader=ts

# Bundle a file for the browser
npx esbuild@0.28.0 app.tsx --bundle --outfile=dist/bundle.js

# Bundle with minification and source maps
npx esbuild@0.28.0 app.tsx --bundle --minify --sourcemap --target=es2015
```

### Using npm (Recommended for Development)

```bash
npm install --save-dev esbuild

# Run via node_modules
./node_modules/.bin/esbuild app.tsx --bundle --outfile=dist/bundle.js

# Or add to package.json scripts
{
  "scripts": {
    "build": "esbuild app.tsx --bundle --minify --outdir=dist"
  }
}
```

See [Installation Methods](reference/01-installation.md) for all installation options including direct binary download, WASM version, and building from source.

## Common Operations
### Bundle for Browser

```bash
npx esbuild@0.28.0 src/index.tsx --bundle --outdir=dist --sourcemap
```

See [Bundling Guide](reference/02-bundling.md) for entry points, output formats, splitting, and advanced bundling options.

### Bundle for Node.js

```bash
npx esbuild@0.28.0 src/index.ts --bundle --platform=node --target=node18 --outfile=dist/index.js
```

See [Platform Configuration](reference/03-platforms.md) for browser vs Node.js differences and platform-specific settings.

### Transform Single File

```bash
echo 'const x: string = "hello"' | npx esbuild@0.28.0 --loader=ts
```

See [Transform API](reference/04-transform-api.md) for in-memory transformation without file system access.

### Watch Mode with Live Reload

```bash
npx esbuild@0.28.0 src/index.tsx --bundle --outdir=dist --watch
```

See [Development Workflows](reference/05-development.md) for watch mode, serve mode, and live reload setup.

### Minify Code

```bash
npx esbuild@0.28.0 src/app.js --minify --outfile=dist/app.min.js
```

See [Optimization Options](reference/06-optimization.md) for minification, tree shaking, dead code elimination, and code splitting.

### Use JavaScript API

```javascript
import * as esbuild from 'esbuild'

await esbuild.build({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outfile: 'dist/bundle.js',
  minify: true,
  sourcemap: true,
})
```

See [API Reference](reference/07-api-reference.md) for complete CLI, JavaScript API, and Go API documentation.

## Supported Content Types
Esbuild handles these file types out of the box:

- **JavaScript** (`.js`, `.cjs`, `.mjs`) - All modern ES2024 syntax
- **TypeScript** (`.ts`, `.tsx`, `.mts`, `.cts`) - Type stripping without type checking
- **JSX** (`.jsx`, `.tsx`) - React JSX and custom factories
- **JSON** (`.json`) - Imported as JavaScript objects
- **CSS** (`.css`) - Bundling with CSS modules support
- **Text/Binary** - Base64 encoding, data URLs, external files

See [Content Types](reference/08-content-types.md) for loader configuration and file type handling.

## Plugin System
Esbuild supports plugins for custom resolution, loading, and build hooks:

```javascript
import * as esbuild from 'esbuild'

await esbuild.build({
  entryPoints: ['src/index.ts'],
  plugins: [{
    name: 'example',
    setup(build) {
      build.onResolve({ filter: /^\.\/.*\.custom$/ }, args => ({
        path: args.path.replace('.custom', '.js'),
      }))
    },
  }],
})
```

See [Plugin Development](reference/09-plugins.md) for on-resolve, on-load, on-start, and on-end callbacks.

## Advanced Topics
## Advanced Topics

- [Installation](reference/01-installation.md)
- [Bundling](reference/02-bundling.md)
- [Platforms](reference/03-platforms.md)
- [Transform Api](reference/04-transform-api.md)
- [Development](reference/05-development.md)
- [Optimization](reference/06-optimization.md)
- [Api Reference](reference/07-api-reference.md)
- [Content Types](reference/08-content-types.md)
- [Plugins](reference/09-plugins.md)
- [Faq Troubleshooting](reference/10-faq-troubleshooting.md)

## Troubleshooting
### Anti-virus Software False Positives

Esbuild downloads platform-specific binaries during installation. Some anti-virus software may flag these as suspicious. Add `node_modules` to your anti-virus exclusion list or use the `--ignore-scripts` npm flag.

See [FAQ and Troubleshooting](reference/10-faq-troubleshooting.md) for common issues including outdated Go versions, minification problems, and name collision avoidance.

### Cross-Platform Compatibility

Esbuild installs platform-specific binaries. When moving between platforms (Windows/Linux/macOS) or architectures (x64/arm64), reinstall esbuild on the target platform. For Docker or CI environments, run `npm install` inside the container.

See [Installation Methods](reference/01-installation.md) for simultaneous platform support using Yarn and handling ARM/x64 transitions.

### Performance Issues

Esbuild is designed to be extremely fast without caching. If experiencing slow builds:
- Avoid using `esbuild-wasm` (10x slower than native binaries)
- Ensure you're not copying `node_modules` between platforms
- Use the async JavaScript API instead of sync for parallelization
- Check anti-virus software isn't scanning esbuild binaries

See [FAQ and Troubleshooting](reference/10-faq-troubleshooting.md) for benchmark details and performance optimization tips.

**Note:** All paths in this skill are relative to the skill's base directory (`.agents/skills/esbuild-0-28/`). The `{baseDir}` variable refers to this location when used in agent contexts.

