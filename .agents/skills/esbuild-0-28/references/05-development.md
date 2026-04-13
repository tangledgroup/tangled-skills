# Esbuild Development Workflows

## Watch Mode

Automatically rebuild when files change:

```bash
esbuild src/index.tsx --bundle --outdir=dist --watch
```

Output:
```
[watch] build finished, watching for changes...
[watch] 10ms (1 event)
[watch] 8ms (2 events)
```

### Watch Mode Options

```bash
# Watch with specific options
esbuild src/index.tsx --bundle --outdir=dist \
  --watch="*"  # Watch all files (default)

# With log level
esbuild src/index.tsx --bundle --outdir=dist \
  --watch \
  --log-level=warning  # Only show warnings and errors
```

Log levels: `info`, `warning`, `error`, `silent`

### JavaScript API Watch Mode

```javascript
import * as esbuild from 'esbuild'

const ctx = await esbuild.context({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outdir: 'dist',
})

await ctx.watch()

// Keep process running
console.log('Watching for changes...')
```

### Stop Watch Mode

```javascript
// Dispose context to stop watching
await ctx.dispose()
```

## Serve Mode

Start a local development server:

```bash
esbuild src/index.tsx --bundle --serve --servedir=dist
```

Output:
```
 > Local:   http://127.0.0.1:8000/
 > Network: http://192.168.1.100:8000/
```

### Serve Mode Options

```bash
# Custom port and host
esbuild src/index.tsx --bundle \
  --serve=8080 \
  --host=0.0.0.0 \
  --servedir=dist

# With certificate (HTTPS)
esbuild src/index.tsx --bundle \
  --serve \
  --cert=cert.pem \
  --key=key.pem \
  --servedir=dist
```

### JavaScript API Serve Mode

```javascript
import * as esbuild from 'esbuild'

const ctx = await esbuild.context({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outdir: 'dist',
})

const { hosts, port } = await ctx.serve({
  servedir: 'dist',
  port: 8080,
  host: '0.0.0.0',
})

console.log(`Server running at http://${hosts[0]}:${port}/`)
```

### Serve with Watch Mode

Combine watch and serve for auto-rebuilding server:

```bash
esbuild src/index.tsx --bundle \
  --watch \
  --serve \
  --servedir=dist
```

Server serves latest build after each change.

## Live Reload

Automatically reload browser page when code changes:

### Setup

1. Enable watch and serve mode:

```bash
esbuild src/index.tsx --bundle --watch --serve --servedir=dist
```

2. Add live reload script to your HTML (development only):

```html
<script>
  new EventSource('/esbuild').addEventListener('change', () => location.reload())
</script>
```

3. Load your app in the browser at `http://localhost:8000/`

### Advanced Live Reload

Hot reload CSS without page refresh:

```javascript
new EventSource('/esbuild').addEventListener('change', e => {
  const { added, removed, updated } = JSON.parse(e.data)

  // Only reload CSS files in place
  if (!added.length && !removed.length && updated.length === 1) {
    for (const link of document.getElementsByTagName("link")) {
      const url = new URL(link.href)

      if (url.host === location.host && url.pathname === updated[0]) {
        const next = link.cloneNode()
        next.href = updated[0] + '?' + Math.random().toString(36).slice(2)
        next.onload = () => link.remove()
        link.parentNode.insertBefore(next, link.nextSibling)
        return
      }
    }
  }

  // Fallback: full page reload
  location.reload()
})
```

### Production Build Without Live Reload

Exclude live reload code in production:

```javascript
if (!window.IS_PRODUCTION) {
  new EventSource('/esbuild').addEventListener('change', () => location.reload())
}
```

Build with define:

```bash
# Development (live reload enabled)
esbuild src/index.tsx --bundle --watch --serve

# Production (live reload disabled)
esbuild src/index.tsx --bundle \
  --define:window.IS_PRODUCTION=true \
  --minify \
  --outfile=dist/app.js
```

## Rebuild API (Manual Incremental Builds)

Manually trigger rebuilds:

```javascript
import * as esbuild from 'esbuild'

const ctx = await esbuild.context({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outdir: 'dist',
})

// Trigger rebuild manually
const result1 = await ctx.rebuild()
const result2 = await ctx.rebuild()

// Cleanup
await ctx.dispose()
```

### Cancel Ongoing Build

```javascript
import * as esbuild from 'esbuild'
import process from 'node:process'

const ctx = await esbuild.context({
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outdir: 'dist',
  logLevel: 'info',
})

// Cancel current build and start new one on stdin input
process.stdin.on('data', async () => {
  try {
    await ctx.cancel()  // Cancel ongoing build
    console.log('build:', await ctx.rebuild())
  } catch (err) {
    console.error(err)
  }
})
```

## Development Server Configuration

### Custom Host and Port

```bash
# Listen on all interfaces, port 3000
esbuild src/index.tsx --bundle --serve=3000 --host=0.0.0.0
```

### HTTPS Server

```bash
# Generate self-signed certificate
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem

# Start HTTPS server
esbuild src/index.tsx --bundle \
  --serve \
  --cert=cert.pem \
  --key=key.pem \
  --servedir=dist
```

### Serve Static Files Only

```bash
# Serve existing files without building
esbuild --serve --servedir=dist
```

Useful for serving production builds.

## Build Context Options

All context options are shared across rebuilds:

```javascript
const ctx = await esbuild.context({
  // Input
  entryPoints: ['src/index.tsx'],
  stdin: { contents: 'console.log("hello")', resolveDir: '.' },

  // Output
  bundle: true,
  outfile: 'dist/app.js',
  outdir: 'dist',
  format: 'iife',
  globalName: 'MyApp',

  // Optimization
  minify: false,  // Don't minify in development
  treeShaking: true,

  // Source maps
  sourcemap: 'inline',

  // Platform
  platform: 'browser',
  target: ['chrome91', 'firefox89', 'safari14'],

  // Logging
  logLevel: 'info',

  // Plugins
  plugins: [/* ... */],
})
```

## Package.json Scripts

Add development commands to package.json:

```json
{
  "scripts": {
    "dev": "esbuild src/index.tsx --bundle --sourcemap --watch --serve --servedir=dist",
    "build": "esbuild src/index.tsx --bundle --minify --outfile=dist/app.js",
    "build:dev": "esbuild src/index.tsx --bundle --sourcemap --outfile=dist/app.js"
  }
}
```

Run with:
```bash
npm run dev     # Development with watch and serve
npm run build   # Production build
npm run build:dev  # Development build (no watch)
```

## Multiple Entry Points in Development

```bash
# Watch multiple entry points
esbuild src/index.tsx src/admin.tsx \
  --bundle \
  --outdir=dist \
  --watch \
  --serve \
  --servedir=dist
```

Each entry point gets its own output file and rebuilds independently.

## Development vs Production Builds

### Development Build

```bash
esbuild src/index.tsx --bundle \
  --sourcemap=inline \
  --define:process.env.NODE_ENV="'development'" \
  --outfile=dist/app.dev.js
```

- Source maps enabled
- No minification
- Debug code included
- Faster builds

### Production Build

```bash
esbuild src/index.tsx --bundle \
  --minify \
  --sourcemap=external \
  --define:process.env.NODE_ENV="'production'" \
  --drop:console \
  --drop:debugger \
  --outfile=dist/app.js
```

- Minified code
- External source maps (for debugging)
- Console/debugger removed
- Smaller bundle size

## Hot Module Replacement (HMR) Limitations

Esbuild's live reload does full page refresh. For true HMR (preserving state):

1. Use a framework with built-in HMR (Next.js, Vite, etc.)
2. Implement custom HMR logic using `/esbuild` event stream
3. Use esbuild as bundler in tools that support HMR

Esbuild provides the build speed and watch/serve infrastructure, but HMR implementation is application-specific.

## Performance Tips for Development

### Fast Rebuilds

- Use `--watch` instead of manual rebuilds
- Keep entry points minimal (fewer files to scan)
- Exclude unnecessary directories with external packages

### Parallel Builds

```javascript
// Build multiple projects in parallel
const [ctx1, ctx2] = await Promise.all([
  esbuild.context({ entryPoints: ['project-a/src/index.ts'], bundle: true }),
  esbuild.context({ entryPoints: ['project-b/src/index.ts'], bundle: true }),
])

await Promise.all([ctx1.rebuild(), ctx2.rebuild()])
```

### Clean Output Before Build

```json
{
  "scripts": {
    "clean": "rm -rf dist",
    "build": "npm run clean && esbuild src/index.tsx --bundle --minify --outdir=dist"
  }
}
```
