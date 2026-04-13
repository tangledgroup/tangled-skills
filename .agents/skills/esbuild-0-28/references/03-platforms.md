# Esbuild Platform Configuration

## Browser Platform (Default)

Esbuild targets browsers by default:

```bash
esbuild app.tsx --bundle --outfile=bundle.js
```

**Default browser settings:**
- Global variables like `window`, `document` are preserved
- CSS is inlined into JavaScript
- No automatic external dependencies
- IIFE format for global scope isolation

### Target Browser Versions

Specify minimum browser versions:

```bash
# Target specific browsers
esbuild app.tsx --bundle \
  --target=chrome58,firefox57,safari11,edge16 \
  --outfile=bundle.js

# Or use ES version (transforms syntax)
esbuild app.tsx --bundle --target=es2015 --outfile=bundle.js
```

**Supported targets:**
- Browsers: `chrome`, `firefox`, `safari`, `edge`, `ios`, `android`
- ES versions: `es5`, `es6`, `es2015`, `es2016`, ..., `es2023`, `esnext`

### Browser-Specific Transformations

Esbuild transforms modern syntax for older browsers:

| Syntax | Transformed below target | Example |
|--------|--------------------------|---------|
| Exponentiation | es2016 | `a ** b` → `Math.pow(a, b)` |
| Async/await | es2017 | `async () => {}` |
| Object spread | es2018 | `{...obj}` |
| Optional chaining | es2020 | `a?.b` |
| Nullish coalescing | es2020 | `a ?? b` |
| Class fields | es2022 | `class { x = 1 }` |
| Private methods | es2022 | `class { #x() {} }` |

## Node.js Platform

Bundle code for Node.js runtime:

```bash
esbuild app.ts --bundle --platform=node --outfile=dist/app.js
```

**Node platform changes:**
- Built-in modules (`fs`, `path`, `http`) marked as external
- CommonJS format by default
- `__dirname` and `__filename` preserved
- `import.meta.url` transformed to `fileURLToPath(import.meta.url)`
- Browser field in package.json ignored

### Node.js Target Version

```bash
# Target specific Node version
esbuild app.ts --bundle \
  --platform=node \
  --target=node18 \
  --outfile=dist/app.js

# Or node16, node14, etc.
```

### External Dependencies for Node

Exclude node_modules from bundle:

```bash
# All packages external
esbuild app.ts --bundle \
  --platform=node \
  --packages=external \
  --outfile=dist/app.js

# Specific packages external
esbuild app.ts --bundle \
  --platform=node \
  --external:lodash \
  --external:express \
  --outfile=dist/app.js
```

**Important:** External packages must be installed at runtime.

### Node-Specific Limitations

Esbuild doesn't support these in bundles:
- `__dirname` and `__filename` in ESM format
- `import.meta.url` without transformation
- Native `.node` binary modules
- `fs.readFileSync` for loading modules

**Workaround:** Use CommonJS format or mark as external.

## Simultaneous Platforms

Esbuild cannot bundle for multiple platforms in one build. Create separate builds:

```bash
# Browser bundle
esbuild app.tsx --bundle --platform=browser --outfile=dist/browser.js

# Node bundle
esbuild app.ts --bundle --platform=node --outfile=dist/node.js
```

Or use output format to control platform behavior:

```bash
# Universal module (works in browser and Node)
esbuild app.ts --bundle --format=iife --outfile=dist/universal.js
```

## Platform Detection in Code

Use define to inject platform-specific values:

```bash
esbuild app.ts --bundle \
  --define:PLATFORM="'browser'" \
  --outfile=dist/browser.js

esbuild app.ts --bundle \
  --define:PLATFORM="'node'" \
  --platform=node \
  --outfile=dist/node.js
```

Code example:
```javascript
if (PLATFORM === 'browser') {
  // Browser-specific code
} else {
  // Node-specific code
}
```

Tree shaking removes unused branch.

## CSS Handling by Platform

### Browser (default)

CSS is inlined into JavaScript as style tags:

```bash
esbuild app.tsx --bundle --outfile=bundle.js
# CSS from imported .css files injected via <style> tags
```

### Node.js

CSS is discarded by default:

```bash
esbuild app.ts --bundle --platform=node --outfile=dist/app.js
# CSS imports removed (Node doesn't execute CSS)
```

Preserve CSS for Node:
```bash
esbuild app.ts --bundle \
  --platform=node \
  --loader:.css=copy \
  --outfile=dist/app.js
```

## Environment Variables by Platform

### Browser

```bash
esbuild app.tsx --bundle \
  --define:process.env.NODE_ENV="'production'" \
  --define:process.env.API_URL="'https://api.example.com'" \
  --outfile=bundle.js
```

### Node.js

```bash
esbuild app.ts --bundle \
  --platform=node \
  --define:process.env.NODE_ENV="'production'" \
  --outfile=dist/app.js
```

Note: `process.env.VAR` in Node bundles refers to runtime environment, not build-time.

## Web Workers

Bundle web worker code separately:

```javascript
// Main thread
const worker = new Worker('/worker.js')

// Bundle worker
esbuild src/worker.ts --bundle --format=esm --outfile=dist/worker.js
```

**Important:** Don't use `toString()` on functions for worker code. Build worker as separate entry point.

## Service Workers

Similar to web workers:

```bash
esbuild src/service-worker.ts --bundle --format=esm --outfile=dist/sw.js
```

Service worker code runs in isolated context - no access to main thread variables.

## Deno Platform

Deno requires explicit platform configuration:

```bash
# Deno uses browser-like environment
esbuild app.ts --bundle --platform=browser --target=deno189 --outfile=dist/app.js
```

**Note:** Deno has its own esbuild integration at deno.land/x/esbuild.

## SSR (Server-Side Rendering)

Bundle separately for server and client:

```bash
# Client bundle (browser)
esbuild src/client.tsx --bundle \
  --target=es2015 \
  --outfile=dist/client.js

# Server bundle (Node)
esbuild src/server.tsx --bundle \
  --platform=node \
  --target=node18 \
  --outfile=dist/server.js
```

Share code between platforms:
```javascript
// shared/utils.ts
export function formatDate(d) { return d.toISOString() }

// Import in both client and server bundles
import { formatDate } from '../shared/utils'
```

## Edge Functions / Serverless

Bundle for edge runtimes (Cloudflare Workers, Vercel Edge):

```bash
esbuild src/edge.ts --bundle \
  --platform=browser \
  --target=es2020 \
  --format=esm \
  --outfile=dist/edge.js
```

**Common edge runtime settings:**
- Platform: `browser` (most edge runtimes use Web APIs)
- Target: Modern ES version (`es2020`+)
- Format: `esm`
- External: Runtime-specific packages

### Cloudflare Workers

```bash
esbuild src/index.ts --bundle \
  --platform=browser \
  --target=es2020 \
  --format=esm \
  --outfile=dist/worker.js
```

### Vercel Edge Functions

```bash
esbuild src/api/route.ts --bundle \
  --platform=browser \
  --target=es2022 \
  --format=esm \
  --outfile=dist/edge.js
```

## Platform-Specific Entry Points

Different entry points per platform:

```json
{
  "scripts": {
    "build:browser": "esbuild src/browser.tsx --bundle --outfile=dist/browser.js",
    "build:node": "esbuild src/node.ts --bundle --platform=node --outfile=dist/node.js",
    "build:all": "npm run build:browser && npm run build:node"
  }
}
```

## Testing Across Platforms

Test bundles in target environments:

```bash
# Test Node bundle
node dist/node.js

# Test browser bundle (serve with esbuild)
esbuild src/browser.tsx --bundle --serve --host=0.0.0.0

# Or use any HTTP server
npx serve dist/
```
