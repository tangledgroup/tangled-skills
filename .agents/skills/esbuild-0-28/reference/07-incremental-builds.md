# Incremental Builds and Live Reload

esbuild provides three incremental build APIs through the context object. All share the same build options and reuse work from previous builds for performance.

## Watch Mode

Automatically rebuilds when source files change.

```bash
esbuild app.ts --bundle --outdir=dist --watch
```

```js
let ctx = await esbuild.context({
  entryPoints: ['app.ts'],
  bundle: true,
  outdir: 'dist',
})
await ctx.watch()
```

## Serve Mode

Starts a local development server that serves the latest build results. Incoming requests trigger builds automatically.

```bash
esbuild app.ts --bundle --outdir=dist --serve
# Local:   http://127.0.0.1:8000/
# Network: http://192.168.0.1:8000/
```

```js
let ctx = await esbuild.context({
  entryPoints: ['app.ts'],
  bundle: true,
  outdir: 'dist',
})
let { hosts, port } = await ctx.serve()
```

Serve options include `port`, `host`, `servedir` (directory to serve static files from), and `fqPort`.

## Rebuild Mode

Manually invoke builds. Useful when integrating with custom file watchers or development servers. Not available from CLI.

```js
let ctx = await esbuild.context({
  entryPoints: ['app.ts'],
  bundle: true,
  outdir: 'dist',
})

for (let i = 0; i < 5; i++) {
  let result = await ctx.rebuild()
}
```

## Cancel API

Cancel a currently-running build before starting a new one. Not available from CLI.

```js
let ctx = await esbuild.context({
  entryPoints: ['app.ts'],
  bundle: true,
  outdir: 'www',
  logLevel: 'info',
})

process.stdin.on('data', async () => {
  try {
    await ctx.cancel()       // Wait for cancel to complete
    console.log('build:', await ctx.rebuild())
  } catch (err) {
    console.error(err)
  }
})
```

## Live Reload

Combine watch + serve for automatic browser page reload on file changes.

```bash
esbuild app.ts --bundle --outdir=www --watch --servedir=www
```

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

Guard with an environment flag for production removal:

```js
if (!window.IS_PRODUCTION) {
  new EventSource('/esbuild').addEventListener('change', () => location.reload())
}
```

Then use `define` in production: `{ 'window.IS_PRODUCTION': 'true' }`.

## CSS Hot-Reload

The `change` event data contains `{ added: string[], removed: string[], updated: string[] }` for advanced use cases:

```js
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

## Caveats

**Events only trigger on build output changes** — Changes to files unrelated to the watched build do not trigger events.

**Firefox EventSource reconnection bug** — Firefox may fail to reconnect if the server is temporarily unreachable. Workaround: use another browser, manually reload, or implement manual EventSource recreation.

**HTTP/2 requires TLS** — Without HTTPS, each `/esbuild` event source uses one of 6 simultaneous per-domain HTTP/1.1 connections. Opening more than 6 tabs breaks live reload in some tabs. Enable HTTPS to avoid this.

**JavaScript hot-reload is not supported** — esbuild does not implement HMR for JavaScript because JS is stateful. Use live-reload with `sessionStorage` to persist state across page reloads instead.

## Context Cleanup

When done with a context, call `dispose()` to wait for existing builds, stop watch/serve, and free resources:

```js
await ctx.dispose()
```
