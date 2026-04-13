# Esbuild Optimization Options

## Minification

Minify code to reduce bundle size:

```bash
esbuild app.js --minify --outfile=app.min.js
```

### Minification Components

```bash
# Full minification (default)
esbuild app.js --minify --outfile=app.min.js

# Whitespace only
esbuild app.js \
  --minify-whitespace \
  --minify-identifiers=false \
  --minify-syntax=false \
  --outfile=app.min.js

# Identifiers only (rename variables)
esbuild app.js \
  --minify-whitespace=false \
  --minify-identifiers \
  --minify-syntax=false \
  --outfile=app.min.js

# Syntax only (optimize syntax)
esbuild app.js \
  --minify-whitespace=false \
  --minify-identifiers=false \
  --minify-syntax \
  --outfile=app.min.js
```

### Minification Examples

**Before:**
```javascript
function add(a, b) {
  return a + b
}

const result = add(1, 2)
console.log('Result:', result)
```

**After minification:**
```javascript
function add(n,r){return n+r}console.log("Result:",add(1,2))
```

## Tree Shaking

Automatic removal of unused code:

### How It Works

```javascript
// lib.js
export function used() { return 1 }
export function unused() { return 2 }

// app.js
import { used } from './lib.js'
used()  // 'unused' is removed from bundle
```

**Requirements:**
- Must use `--bundle`
- Works best with ESM imports/exports
- Limited CommonJS support

### Disable Tree Shaking

```bash
esbuild app.js --bundle --tree-shaking=false --outfile=bundle.js
```

Use when code relies on side effects from unused imports.

## Define: Variable Replacement

Replace variables at build time:

### Basic Usage

```bash
# Replace process.env.NODE_ENV
esbuild app.js --bundle \
  --define:process.env.NODE_ENV="'production'" \
  --outfile=dist/app.js
```

**Important:** String values must be double-quoted inside single quotes.

### Multiple Definitions

```bash
esbuild app.js --bundle \
  --define:process.env.NODE_ENV="'production'" \
  --define:__VERSION__="'1.0.0'" \
  --define:__API_URL__="'https://api.example.com'" \
  --outfile=dist/app.js
```

### Code Example

```javascript
// app.js
if (process.env.NODE_ENV === 'development') {
  console.log('Debug mode')
  debugFunction()
}

console.log('Version:', __VERSION__)
fetch(__API_URL__ + '/data')
```

In production build, the entire development if-block is removed.

### Replace Functions

```bash
esbuild app.js --bundle \
  --define:Math.random="'() => 0.5'" \
  --outfile=dist/app.js
```

Replaces `Math.random()` with deterministic value for testing.

### TypeScript Compatibility

```bash
esbuild app.ts --bundle \
  --define:'globalThis.CONFIG={apiUrl:"https://api.example.com"}' \
  --outfile=dist/app.js
```

## Inject: Automatic Imports

Automatically inject code into every module:

### Polyfill Injection

```bash
# Inject polyfills into all modules
esbuild app.js --bundle \
  --inject:./polyfills.js \
  --outfile=dist/app.js
```

**polyfills.js:**
```javascript
export const fetch = require('node-fetch')
export const TextEncoder = require('text-encoding').TextEncoder
```

Every module now has access to these globals.

### Environment Injection

```bash
esbuild app.js --bundle \
  --inject:./env.js \
  --outfile=dist/app.js
```

**env.js:**
```javascript
export const env = {
  NODE_ENV: 'production',
  API_URL: 'https://api.example.com',
}
```

### Multiple Inject Files

```bash
esbuild app.js --bundle \
  --inject:./polyfills.js \
  --inject:./env.js \
  --outfile=dist/app.js
```

## Drop: Remove Code

Remove specific types of code:

### Drop Console Statements

```bash
esbuild app.js --bundle --drop:console --outfile=dist/app.js
```

Removes:
- `console.log()`
- `console.error()`
- `console.warn()`
- All `console.*` calls

### Drop Debugger Statements

```bash
esbuild app.js --bundle --drop:debugger --outfile=dist/app.js
```

Removes `debugger;` statements.

### Drop Labels

```bash
esbuild app.js --bundle --drop-labels:myLabel --outfile=dist/app.js
```

Removes code with specific labels:
```javascript
myLabel: {
  // This code is removed if --drop-labels:myLabel is used
  console.log('labeled code')
}
```

### Multiple Drop Options

```bash
esbuild app.js --bundle \
  --drop:console \
  --drop:debugger \
  --outfile=dist/app.js
```

## Pure: Mark Functions as Side-Effect-Free

Mark functions as pure for tree shaking:

### Using Comments

```javascript
// Pure function - can be removed if unused
const result = /* #__PURE__ */ expensiveComputation()

// Or @__PURE__
const result = /* @__PURE__ */ anotherPureFunction()
```

Esbuild removes the call if `result` is unused.

### Babel-Compatible Annotations

```javascript
// babel-plugin-prune
const x = /* #__NO_SIDE_EFFECTS__ */ function() {}
```

## Keep Names: Preserve Function Names

Preserve function and class names during minification:

```bash
esbuild app.js --bundle --minify --keep-names --outfile=dist/app.js
```

**Without keep-names:**
```javascript
function MyClass() {}  // Becomes: function a() {}
```

**With keep-names:**
```javascript
function MyClass() {}  // Stays: function MyClass() {}
```

Useful for libraries where names are part of the public API.

## Line Limit: Code Splitting by Size

Split output into chunks based on line count:

```bash
esbuild app.js --bundle \
  --line-limit=100000 \
  --outfile=dist/app.js
```

Creates multiple files if single file exceeds limit.

## Charset: Character Encoding Control

Control which characters are escaped in output:

```bash
# ASCII only (escape all non-ASCII)
esbuild app.js --bundle --charset=ascii --outfile=dist/app.js

# Allow UTF-8 (default)
esbuild app.js --bundle --charset=utf8 --outfile=dist/app.js
```

Use `--charset=ascii` for environments that don't support UTF-8.

## Legal Comments: License Handling

Move license comments to separate file:

```bash
# Move legal comments to end of file
esbuild app.js --bundle --legal-comments=eof --outfile=dist/app.js

# Extract to separate file
esbuild app.js --bundle \
  --legal-comments=license.txt \
  --outfile=dist/app.js

# Keep inline (default)
esbuild app.js --bundle --legal-comments=inline --outfile=dist/app.js

# Remove all legal comments
esbuild app.js --bundle --legal-comments=none --outfile=dist/app.js
```

## Ignore Annotations: Override Tree Shaking

Force keep or remove code regardless of usage:

### Keep Used Code

```javascript
// Force keep this import even if unused
import './side-effect-module' /* #__KEEP__ */
```

### Mark as Unused

```javascript
// Force remove this call
const x = /* #__NO_SIDE_EFFECTS__ */ fn()
```

## Optimization Pipeline Example

Complete production build with all optimizations:

```bash
esbuild src/index.tsx --bundle \
  --minify \
  --tree-shaking=true \
  --define:process.env.NODE_ENV="'production'" \
  --drop:console \
  --drop:debugger \
  --keep-names \
  --legal-comments=license.txt \
  --sourcemap=external \
  --outfile=dist/app.js
```

## Performance vs Size Trade-offs

### Maximum Minification

```bash
esbuild app.js --bundle \
  --minify \
  --drop:console \
  --drop:debugger \
  --legal-comments=none \
  --charset=ascii \
  --outfile=dist/app.min.js
```

Smallest bundle, hardest to debug.

### Balanced Production Build

```bash
esbuild app.js --bundle \
  --minify \
  --sourcemap=external \
  --legal-comments=eof \
  --outfile=dist/app.js
```

Good compression with debug capability via source maps.

### Development Build (No Optimization)

```bash
esbuild app.js --bundle \
  --minify=false \
  --sourcemap=inline \
  --outfile=dist/app.dev.js
```

Fast builds, easy debugging, larger bundle.

## Measuring Optimization Impact

Generate metadata to analyze bundle:

```bash
esbuild app.js --bundle --metafile=meta.json --outfile=dist/app.js
```

Analyze with esbuild:
```javascript
import { analyzeMetafile } from 'esbuild'
const meta = require('./meta.json')
console.log(analyzeMetafile(meta))
```

Or use third-party tools:
```bash
npm install -g esbuild-analyzer
esbuild-analyzer meta.json
```

## Common Optimization Patterns

### Environment-Specific Builds

```json
{
  "scripts": {
    "build:dev": "esbuild src/index.tsx --bundle --sourcemap=inline --outfile=dist/app.dev.js",
    "build:prod": "esbuild src/index.tsx --bundle --minify --drop:console --outfile=dist/app.js"
  }
}
```

### Library Build (Keep Names)

```bash
esbuild src/lib.ts --bundle \
  --format=umd \
  --global-name=MyLib \
  --minify \
  --keep-names \
  --outfile=dist/lib.umd.js
```

### Worker/Service Worker Build

```bash
esbuild src/worker.ts --bundle \
  --format=esm \
  --minify \
  --target=es2020 \
  --outfile=dist/worker.js
```
