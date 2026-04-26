# JavaScript API

## Async API (recommended)

The async API is faster, supports plugins, and spreads work across all CPU cores. Use `.mjs` extension in Node.js for `import` and top-level `await`.

```js
import * as esbuild from 'esbuild'

// Build
let result = await esbuild.build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  outdir: 'dist',
})

// Transform
let result = await esbuild.transform('let x: number = 1', {
  loader: 'ts',
})
console.log(result.code) // "let x = 1;\n"
```

## Sync API (Node.js only)

Synchronous API blocks the current thread, does not support plugins, and prevents parallelization. Use only when async is not possible (e.g., within `require.extensions`).

```js
const esbuild = require('esbuild')

let result1 = esbuild.buildSync({
  entryPoints: ['app.jsx'],
  bundle: true,
  outfile: 'out.js',
})

let result2 = esbuild.transformSync('let x: number = 1', {
  loader: 'ts',
})
```

## Build Context (incremental builds)

Create a long-running context for watch, serve, or manual rebuild. All builds share the same options and reuse work from previous builds.

```js
import * as esbuild from 'esbuild'

let ctx = await esbuild.context({
  entryPoints: ['app.ts'],
  bundle: true,
  outdir: 'dist',
})

// Watch mode
await ctx.watch()

// Serve mode
let { hosts, port } = await ctx.serve({
  servedir: 'dist',
})
console.log(`Serving at http://127.0.0.1:${port}/`)

// Manual rebuild
let result = await ctx.rebuild()

// Cancel current build
await ctx.cancel()

// Clean up
await ctx.dispose()
```

## Live Reload via SSE

Combine watch + serve for automatic browser reload:

```js
let ctx = await esbuild.context({
  entryPoints: ['app.ts'],
  bundle: true,
  outdir: 'www',
})
await ctx.watch()
let { hosts, port } = await ctx.serve({ servedir: 'www' })
```

Add to your JavaScript (development only):

```js
new EventSource('/esbuild').addEventListener('change', () => location.reload())
```

The `change` event data contains `{ added: string[], removed: string[], updated: string[] }` for advanced hot-reload:

```js
// CSS hot-reload example
new EventSource('/esbuild').addEventListener('change', e => {
  const { added, removed, updated } = JSON.parse(e.data)
  if (!added.length && !removed.length && updated.length === 1) {
    for (const link of document.getElementsByTagName('link')) {
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
  location.reload()
})
```

## Browser API (WASM)

Install `esbuild-wasm` instead of `esbuild`. Call `initialize()` before use. Sync API is not available in the browser.

```js
import * as esbuild from 'esbuild-wasm'

await esbuild.initialize({
  wasmURL: './node_modules/esbuild-wasm/esbuild.wasm',
})

let result = await esbuild.transform(code, options)
let result2 = await esbuild.build(options)
```

Without a bundler, use a script tag:

```html
<script src="./node_modules/esbuild-wasm/lib/browser.min.js"></script>
<script>
  esbuild.initialize({
    wasmURL: './node_modules/esbuild-wasm/esbuild.wasm',
  }).then(() => {
    // use esbuild API
  })
</script>
```

For ES modules in the browser:

```html
<script type="module">
  import * as esbuild from './node_modules/esbuild-wasm/esm/browser.min.js'
  await esbuild.initialize({
    wasmURL: './node_modules/esbuild-wasm/esbuild.wasm',
  })
</script>
```

If running from a worker and you don't want `initialize` to create another worker:

```js
await esbuild.initialize({
  wasmURL: new URL('esbuild.wasm', import.meta.url),
  worker: false,
})
```

## Build Result

The build API returns an object with:

- `errors` — array of error messages (empty on success)
- `warnings` — array of warning messages
- Each message has `text`, `location` (with `file`, `line`, `column`, `length`, `lineText`), and optionally `detail`

## Transform Result

The transform API returns an object with:

- `code` — the transformed source code as a string
- `map` — the source map as a string (if sourcemap is enabled)
- `warnings` — array of warning messages
