# Bundler

Bun's bundler is a fast, native alternative to webpack, esbuild, and vite. It handles JavaScript, TypeScript, JSX, CSS, JSON, TOML, YAML, HTML, and static assets out of the box.

## CLI Usage

```bash
bun build ./src/index.tsx --outdir ./dist
```

Options:

- `--outdir <dir>` — output directory (required)
- `--target browser|bun|node` — runtime target
- `--format esm|cjs|iife` — module format (esm default; cjs/iife experimental)
- `--minify` — minify output
- `--sourcemap` — generate source maps
- `--watch` — incremental rebuilds on file changes
- `--splitting` — code splitting into multiple chunks
- `--external <pattern>` — exclude from bundle
- `--no-tree-shaking` — disable tree shaking
- `--define foo=bar` — replace identifiers at build time
- `--entry-naming` — output file naming pattern
- `--asset-naming` — asset file naming pattern
- `--public-path` — base URL for assets

### Examples

```bash
# Browser bundle with minification and sourcemaps
bun build ./src/index.tsx --outdir ./dist --target browser --minify --sourcemap

# Bun server bundle
bun build ./src/server.ts --outdir ./dist --target bun

# Node.js bundle
bun build ./src/index.ts --outdir ./dist --target node --format cjs

# Development with watch mode
bun build ./src/index.tsx --outdir ./dist --watch

# External dependencies
bun build ./src/index.tsx --outdir ./dist --external react --external react-dom
```

## JavaScript API

```ts
const result = await Bun.build({
  entrypoints: ["./src/index.tsx", "./src/worker.ts"],
  outdir: "./dist",
  target: "browser",
  minify: true,
  sourcemap: "external",
  splitting: true,
  external: ["react", "react-dom"],
});

if (!result.success) {
  console.error(result.logs);
}
```

## Full-Stack Development Server

Bun's bundler supports full-stack applications with HTML imports and hot reloading:

```ts
// server.ts
import app from "./index.html";

Bun.serve({
  routes: {
    "/": app,
  },
});
```

Run with `bun --hot server.ts` for development with HMR.

## Content Types / Loaders

| Extensions | Behavior |
|---|---|
| `.js`, `.jsx`, `.cjs`, `.mjs`, `.mts`, `.cts`, `.ts`, `.tsx` | Transpiled to vanilla JS with tree shaking and dead code elimination |
| `.json` | Parsed and inlined as JavaScript object |
| `.jsonc` | JSON with comments, inlined as object |
| `.toml` | Parsed and inlined as object |
| `.yaml`, `.yml` | Parsed and inlined as object |
| `.txt` | Inlined as string |
| `.html` | Processed with referenced assets bundled |
| `.css` | Bundled into a single CSS file |
| `.node`, `.wasm` | Treated as binary assets (copied to output) |
| Unrecognized extensions | Copied as external files, import resolved to path |

### Custom Loaders

Configure via `bunfig.toml`:

```toml
[loader]
".custom" = "tsx"
".data" = "json"
```

Supported loaders: `jsx`, `js`, `ts`, `tsx`, `css`, `file`, `json`, `toml`, `wasm`, `napi`, `base64`, `dataurl`, `text`.

## Plugins

Bun's bundler supports plugins for custom transformations:

```ts
await Bun.build({
  entrypoints: ["./src/index.tsx"],
  outdir: "./dist",
  plugins: [
    {
      name: "my-plugin",
      async setup(build) {
        build.onLoad({ filter: /\.custom$/ }, async ({ path }) => {
          const contents = await Bun.file(path).text();
          return {
            contents,
            loader: "tsx",
          };
        });
      },
    },
  ],
});
```

Plugin hooks include `onLoad`, `onResolve`, and `onEnd`.

## Code Splitting

Enable with `--splitting` to split output into multiple chunks:

```bash
bun build ./src/index.tsx --outdir ./dist --splitting
```

Shared dependencies are extracted into separate chunks automatically.

## Hot Reloading

For development, use `bun --hot` to enable hot module replacement:

```bash
bun --hot run server.ts
```

This provides fast, iterative development without full page reloads when frontend code changes.
