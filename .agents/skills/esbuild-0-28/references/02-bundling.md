# Esbuild Bundling Guide

## Basic Bundling

Bundling combines multiple files into one or more output files, inlining all imports:

```bash
# Simple bundle
esbuild app.ts --bundle --outfile=bundle.js

# Multiple entry points (creates separate bundles)
esbuild src/a.ts src/b.ts --bundle --outdir=dist

# With minification and source maps
esbuild app.tsx --bundle --minify --sourcemap --outfile=dist/app.js
```

**Key points:**
- Bundling must be explicitly enabled with `--bundle`
- Multiple entry points create separate output files (not concatenated)
- Imports are recursively inlined (dependencies of dependencies included)

## Entry Points

### Single Entry Point

```bash
esbuild src/index.tsx --bundle --outfile=dist/bundle.js
```

### Multiple Entry Points

```bash
# CLI: Multiple input files
esbuild src/a.tsx src/b.tsx --bundle --outdir=dist

# Creates: dist/a.js, dist/b.js

# JavaScript API
await esbuild.build({
  entryPoints: ['src/a.tsx', 'src/b.tsx'],
  bundle: true,
  outdir: 'dist',
})
```

### Entry Point Naming

Customize output filenames:

```bash
# Pattern with <name> placeholder
esbuild src/pages/home.tsx src/pages/about.tsx \
  --bundle \
  --entry-names=js/[name].[hash].js \
  --outdir=dist

# Creates files like: dist/js/home.a1b2c3.js
```

Patterns supported:
- `<name>` - Entry point basename
- `<ext>` - File extension
- `<hash>` - Content hash (6 characters)

## Output Formats

### IIFE (Browser Default)

```bash
esbuild app.ts --bundle --outfile=bundle.js
# Output format: Immediately Invoked Function Expression
```

Wrap in global variable:

```bash
esbuild app.ts --bundle --global-name=MyApp --outfile=bundle.js
```

Generates:
```javascript
var MyApp = (function() {
  // Your code here
})();
```

### Universal Module Definition

```bash
esbuild app.ts --bundle --format=iife --outfile=bundle.js
```

Works in browsers, Node.js, and AMD loaders.

### CommonJS

```bash
esbuild app.ts --bundle --format=cjs --outfile=bundle.js
```

Generates `module.exports` for Node.js compatibility.

### ECMAScript Modules

```bash
esbuild app.ts --bundle --format=esm --outfile=bundle.js
```

Preserves `import`/`export` syntax. Required for top-level await support.

## Code Splitting

Automatic chunk splitting for shared dependencies:

```bash
esbuild src/a.tsx src/b.tsx \
  --bundle \
  --splitting \
  --outdir=dist
```

Creates separate chunks for:
- Shared imports between entry points
- Dynamically imported modules (`import()`)

### Dynamic Imports

```javascript
// Lazy load module
const module = await import('./heavy-module.js')

// esbuild creates separate chunk automatically with --splitting
```

### Chunk Naming

```bash
esbuild app.ts --bundle --splitting \
  --chunk-names=chunks/[name].[hash].js \
  --asset-names=assets/[name].[hash] \
  --outdir=dist
```

## Glob-Style Imports

Import all matching files at runtime:

```javascript
// Import all JSON files in locale directory
const locale = require(`./locales/${lang}.json`)

// Esbuild transforms to:
const globRequire = __glob({
  './locales/en.json': () => import('./locales/en.json'),
  './locales/fr.json': () => import('./locales/fr.json'),
})
const locale = globRequire(`./locales/${lang}.json`)
```

**Requirements:**
- Pattern must start with `./` or `../`
- Works with `require()` and `import()`
- Does NOT work with static `import` statements

**Limit the search:**
```javascript
// Search only in subdirectory (faster)
const file = require(`./data/${type}/${id}.json`)

// Search only top-level (no subdirectories)
const file = require(`./data-${type}.json`)
```

## External Dependencies

Mark modules as external (not bundled):

```bash
# Single external
esbuild app.ts --bundle --external:lodash --outfile=bundle.js

# Multiple externals
esbuild app.ts --bundle \
  --external:lodash \
  --external:react \
  --external:react-dom \
  --outfile=bundle.js

# All node_modules
esbuild app.ts --bundle --external:*/node_modules/* --outfile=bundle.js
```

External modules must be available at runtime.

### Node-Specific Externals

When bundling for Node.js, built-in modules are automatically external:

```bash
esbuild app.ts --bundle --platform=node --outfile=dist/app.js
# fs, path, http, etc. are automatically external
```

## Path Resolution

### Aliases

```bash
# Map @/ to src/
esbuild app.ts --bundle --alias:@=/src/ --outfile=bundle.js

# Multiple aliases
esbuild app.ts --bundle \
  --alias:~/components=/src/components \
  --alias:@/utils=/src/utils \
  --outfile=bundle.js
```

### Resolve Extensions

```bash
# Try .ts before .js
esbuild app.js --bundle --resolve-extensions:.js,.ts,.tsx --outfile=bundle.js
```

### Node Paths

```bash
# Add to module resolution paths
esbuild app.ts --bundle --node-paths:/shared/modules --outfile=bundle.js
```

## Conditional Loading

Different code for different environments:

```bash
# Set process.env.NODE_ENV
esbuild app.ts --bundle \
  --define:process.env.NODE_ENV="'production'" \
  --minify \
  --outfile=dist/app.js
```

Code example:
```javascript
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info')
}
```

In production, the entire if-block is removed.

## Advanced Bundle Options

### Banner and Footer

Inject code at start/end of bundle:

```bash
esbuild app.ts --bundle \
  --banner:js="'use strict';" \
  --footer:js="// Built with esbuild" \
  --outfile=bundle.js
```

Per-format banners:
```bash
esbuild app.ts --bundle \
  --banner:js="'use strict';" \
  --banner:css="/* Production CSS */" \
  --outfile=bundle.js
```

### Legal Comments

Move license comments to separate file:

```bash
esbuild app.ts --bundle \
  --legal-comments=license.txt \
  --outfile=bundle.js
```

Options: `inline` (default), `external`, `none`, `eof`

### Public Path

Prefix asset URLs:

```bash
esbuild app.ts --bundle \
  --public-path=https://cdn.example.com/assets \
  --outdir=dist
```

Or dynamic public path:
```bash
esbuild app.ts --bundle --public-path=/ --outfile=bundle.js
# Generated code uses relative paths
```

## Bundle Metadata

Generate build metadata:

```bash
esbuild app.ts --bundle --metafile=meta.json --outfile=bundle.js
```

Output includes:
- Input files and dependencies
- Output files and sizes
- Timing information

Use with bundle analyzer:
```javascript
import { analyzeMetafile } from 'esbuild'

const meta = require('./meta.json')
analyzeMetafile(meta) // Returns analysis string
```

## Non-Analyzable Imports

Esbuild cannot bundle these patterns:

```javascript
// ❌ Dynamic imports with variables
import(`pkg/${variable}`)
require(`pkg/${variable}`)

// ❌ Indirect require
['pkg'].map(require)

// ✅ These work (static strings)
import('pkg')
require('pkg')
import('./locale-' + lang + '.json')  // Glob pattern
```

**Solution:** Mark problematic packages as external:

```bash
esbuild app.js --bundle --external:problematic-pkg --outfile=bundle.js
```

## Tree Shaking

Esbuild automatically removes unused code when bundling:

```javascript
// lib.js
export function used() { return 1 }
export function unused() { return 2 }

// app.js
import { used } from './lib.js'
used()  // 'unused' function is removed from bundle
```

**Requirements:**
- Must use `--bundle`
- Works with ESM imports/exports
- Limited support for CommonJS

Disable tree shaking:
```bash
esbuild app.ts --bundle --tree-shaking=false --outfile=bundle.js
```
